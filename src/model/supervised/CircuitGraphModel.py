import torch
from torch.nn import Module, ModuleList, GELU, Linear, Dropout, EmbeddingBag, LayerNorm
from torchmetrics.classification import Accuracy, Precision, Recall, BinaryPrecisionRecallCurve
from torch_geometric.nn import GATv2Conv, JumpingKnowledge, GraphNorm
from torch_geometric.loader import DataLoader, DynamicBatchSampler
from src.model.supervised.FCOutputLayer import FCOutputLayer
from src.graph_builder.verilog_dataclasses import Cell

class TrojanGNN(Module):
    def __init__(self, input_dimension, hidden_dimension, output_dimension, num_conv_layers=4, embedding_dim=8, edge_dim=8, threshold=0.5, device='cpu'):
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

            x = conv_layer(x, edge_index, edge_attr=edge_attr)
            x = conv_norm(x, batch.batch)
            x = self.gelu(x)
            x = self.dropout(x)

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

        # Define an uncompiled inner function to run metrics
        @torch.compiler.disable
        def _run_metrics_eager(preds, targets):
            accuracy = self.accuracy_fn(preds, targets)
            precision = self.precision_fn(preds, targets)
            recall = self.recall_fn(preds, targets)
            return accuracy, precision, recall

        # Step out of the compiler by passing detached variables
        with torch.no_grad():
            accuracy, precision, recall = _run_metrics_eager(
                predictions.detach(),
                batch.y.detach()
            )

        return loss, accuracy, precision, recall
