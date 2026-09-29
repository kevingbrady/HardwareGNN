import torch
from torch.nn import Module, ModuleList, GELU, Linear, Dropout, EmbeddingBag, LayerNorm
from torchmetrics.classification import Accuracy, Precision, Recall, BinaryPrecisionRecallCurve
from torch_geometric.nn import GATv2Conv, JumpingKnowledge, GraphNorm
from torch_geometric.loader import DataLoader, DynamicBatchSampler
from src.model.supervised.FCOutputLayer import FCOutputLayer
from src.graph_builder.verilog_dataclasses import Cell

class TrojanGNN(Module):
    def __init__(self, input_dimension, hidden_dimension, output_dimension, num_conv_layers=3, embedding_dim=16, edge_dim=12, threshold=0.5, device='cpu'):
        super(TrojanGNN, self).__init__()
        self.device = device
        self.threshold = threshold

        self.cell_embedding = EmbeddingBag(
            num_embeddings=Cell.get_total_cell_types() + 1,
            embedding_dim=embedding_dim,
            mode='sum',
            padding_idx=0
        )

        total_input_dim = input_dimension + embedding_dim
        heads = 8

        self.node_feature_norm = LayerNorm(total_input_dim)
        self.edge_feature_norm = LayerNorm(edge_dim)

        self.proj_in = Linear(total_input_dim, hidden_dimension)
        self.conv_layers = ModuleList()
        self.conv_norms = ModuleList()

        for _ in range(num_conv_layers):
            self.conv_layers.append(
                   GATv2Conv(hidden_dimension, hidden_dimension // heads, edge_dim=edge_dim, heads=heads, concat=True)
            )

            self.conv_norms.append(
                GraphNorm(hidden_dimension)
            )

        self.jumping_knowledge_layer = JumpingKnowledge(mode='max')
        self.output_layer = FCOutputLayer(hidden_dimension, hidden_dimension * (heads // 2), output_dimension)

        self.gelu = GELU()
        self.dropout = Dropout(0.2)

        self.accuracy_fn = Accuracy(task='binary').to(device, non_blocking=True)
        self.precision_fn = Precision(task='binary').to(device, non_blocking=True)
        self.recall_fn = Recall(task='binary').to(device, non_blocking=True)

        # Dedicated full-split Precision-Recall curve tool
        self.pr_curve_fn = BinaryPrecisionRecallCurve().to(device)

        self.to(self.device, non_blocking=True)

    def forward(self, batch):

        cell_embedding_vector = self.build_cell_embedding_vector(batch.type_indices, batch.type_lengths, batch.type_counts)
        x = torch.cat([torch.log1p(batch.x), cell_embedding_vector], dim=1)

        x =  self.node_feature_norm(x)
        edge_attr = self.edge_feature_norm(batch.edge_attr)

        edge_index = batch.edge_index

        x = self.proj_in(x)
        conv_layer_outputs = []

        for idx, (conv_layer, conv_norm) in enumerate(zip(self.conv_layers, self.conv_norms)):

            if idx == len(self.conv_layers):
                edge_index = edge_index.T

            residual = x
            x = conv_layer(x, edge_index, edge_attr=edge_attr)
            x = conv_norm(x, batch.batch)
            x = self.gelu(x)
            x = self.dropout(x)
            x = x + residual

            conv_layer_outputs.append(x)

        x = self.jumping_knowledge_layer(conv_layer_outputs)

        return self.output_layer(x)

    def build_cell_embedding_vector(self, type_indices, type_lengths, type_counts):

        zero_padding = torch.zeros(1, dtype=torch.long, device=self.device)
        offsets = torch.cumsum(
            torch.cat([zero_padding, type_lengths]), dim=0
        )[:-1]

        cell_type_embeddings = self.cell_embedding(
            input=type_indices,
            offsets=offsets,
            per_sample_weights=type_counts
        )

        return cell_type_embeddings

    def get_model_metrics(self, batch, loss_function):

        y_hat = self(batch).squeeze(-1)
        target = batch.y.squeeze(-1).float()

        loss = loss_function(y_hat, target)

        probabilities = torch.sigmoid(y_hat)
        predictions = (probabilities > self.threshold).long()

        with torch.no_grad():
            accuracy = self.accuracy_fn(predictions, batch.y)
            precision = self.precision_fn(predictions, batch.y)
            recall = self.recall_fn(predictions, batch.y)

        return loss, accuracy, precision, recall

    def calculate_optimal_threshold(self, validation_dataset, dtype=torch.float32, tolerance = 0.0005, logger=None):
        """
        Gathers raw predictions across the complete validation split, maps out
        the global Precision-Recall curve, and computes the optimal decision threshold.
        """
        if logger:
            logger.info("Gathering full validation split predictions for PR Curve calculation...")
        else:
            print("Gathering full validation split predictions for PR Curve calculation...")

        # Setup a clean, single-threaded loader to circumvent worker deadlocks during analysis
        tune_loader = DataLoader(
            validation_dataset,
            batch_sampler=DynamicBatchSampler(validation_dataset, max_num=50000, shuffle=False, mode='node'),
            num_workers=0,
            pin_memory=True
        )

        self.eval()
        all_probs = []
        all_targets = []

        with torch.no_grad():
            for tune_batch in tune_loader:
                tune_batch = tune_batch.to(self.device, non_blocking=True)

                with torch.amp.autocast(device_type='cuda', dtype=dtype):
                    logits = self(tune_batch)
                    if logits.shape[-1] == 1:
                        logits = logits.squeeze(-1)
                    probs = torch.sigmoid(logits)

                all_probs.append(probs)
                all_targets.append(tune_batch.y)

        # Merge isolated batch chunks into contiguous arrays
        all_probs = torch.cat(all_probs)
        all_targets = torch.cat(all_targets).long()

        # Compute precision, recall boundaries and float threshold arrays
        precisions, recalls, thresholds = self.pr_curve_fn(all_probs, all_targets)

        # Pull values to CPU space for standard python float parsing
        precisions = precisions.cpu()
        recalls = recalls.cpu()
        thresholds = thresholds.cpu()

        # Strategy: Find the point maximizing the overall validation F1-Score boundary
        f1_scores = (2 * (precisions * recalls)) / (precisions + recalls + 1e-8)

        f1_scores_thresh = f1_scores[:-1]
        max_f1 = torch.max(f1_scores_thresh)
        plateau_indices = torch.where(f1_scores_thresh >= (max_f1 - tolerance))[0]
        #best_idx = torch.argmax(f1_scores[:-1])  # Exclude trailing element placeholder
        #opt_threshold = thresholds[best_idx].item()

        min_thresh = thresholds[plateau_indices[0]]
        max_thresh = thresholds[plateau_indices[-1]]

        opt_threshold = torch.median(thresholds[plateau_indices])

        # Log out metrics summary safely
        msg = ( f"--- Threshold Optimization ---\n"
                f"Max Validation F1: {max_f1:.4f}\n"
                f"Perfect Separation Plateau: [{min_thresh:.4f} to {max_thresh:.4f}]\n"
                f"Locked Stable Threshold:   {opt_threshold:.4f}\n"
        )

        if logger:
            # Assumes logFormatter format styling strings are imported globally or passed
            logger.info(msg)
        else:
            print(msg)

        # Update the active classification decision boundary threshold vector directly
        self.threshold = opt_threshold
        return opt_threshold









