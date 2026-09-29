import torch
from torch.nn import Module, ModuleList, Linear, GELU, Parameter, LayerNorm, EmbeddingBag, Dropout, Sequential, MSELoss
from torch_geometric.nn import GATv2Conv, GraphNorm, JumpingKnowledge, RGATConv
from src.graph_builder.verilog_dataclasses import Cell, Port
from src.model.loss_functions.FocalLoss import FocalLoss


class MultiModalCircuitMAE(Module):
    def __init__(self, hidden_dimension, mask_rate=0.25, cell_embedding_dim=16, node_features_dim=7, edge_dim=12,
                 num_conv_layers=3, device='cpu'):
        super(MultiModalCircuitMAE, self).__init__()
        self.total_input_dim = cell_embedding_dim + node_features_dim
        self.device = device
        self.mask_rate = mask_rate

        # Create EmbeddingBag Layer for cell type embeddings
        self.cell_embedding = EmbeddingBag(
            num_embeddings=Cell.get_total_cell_types() + 1,
            embedding_dim=cell_embedding_dim,
            mode='sum',
            padding_idx=0
        )

        heads = 8
        num_port_classes = len(Port.classes)

        self.node_feature_norm = LayerNorm(self.total_input_dim)
        self.edge_feature_norm = LayerNorm(edge_dim - 2)

        # Projection layer to higher-dimensional latent space
        self.proj_in = Linear(self.total_input_dim, hidden_dimension)
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

        self.gelu = GELU()
        self.dropout = Dropout(0.15)

        # GraphMAE2 Decoder Stage
        self.decoder_proj = Linear(hidden_dimension, hidden_dimension)
        self.decoder_conv = GATv2Conv(hidden_dimension, hidden_dimension // heads, edge_dim=edge_dim, heads=heads, concat=True)
        self.decoder_norm = GraphNorm(hidden_dimension)

        # GraphMAE2 Multi-Task Reconstruction Heads
        self.reconstruct_node_features = Sequential(Linear(hidden_dimension, hidden_dimension), GELU(), Linear(hidden_dimension, self.total_input_dim))

        # GraphMAE2 Edge Feature Reconstruction Head
        self.reconstruct_edge_features = Sequential(Linear(hidden_dimension * 2, hidden_dimension), GELU(), Linear(hidden_dimension, edge_dim - 2))
        self.reconstruct_src_port = Linear(hidden_dimension * 2, num_port_classes)
        self.reconstruct_dst_port = Sequential(Linear(hidden_dimension * 2, hidden_dimension), GELU(), Linear(hidden_dimension, num_port_classes))

        # Loss Functions declared directly within the architecture
        self.mse_loss = MSELoss(reduction='none')
        self.focal_loss = FocalLoss(alpha=0.8, gamma=2.0, reduction='none', device=self.device)

        # Mask tokens for both modalities
        self.latent_mask_token = Parameter(torch.randn(1, hidden_dimension))
        self.edge_multipliers = Parameter(torch.zeros(3, device=self.device))
        self.node_multipliers = Parameter(torch.zeros(1, device=self.device))

        self.to(self.device, non_blocking=True)

    def forward(self, batch, node_features_mask=None):

        # Combine into single node features vector
        cell_embedding_vector = self.build_cell_embedding_vector(batch.type_indices, batch.type_lengths,
                                                                 batch.type_counts)
        x = torch.cat([batch.x, cell_embedding_vector], dim=1)
        x = self.node_feature_norm(x)

        edge_attr = torch.cat([batch.edge_attr[:, 0:2], self.edge_feature_norm(batch.edge_attr[:, 2:])], dim=1)
        edge_index = batch.edge_index

        if node_features_mask is None:
            node_features_mask = torch.tensor([], dtype=torch.long, device=self.device)

        x = self.proj_in(x)
        if node_features_mask.numel() > 0:
            x[node_features_mask] = self.latent_mask_token.to(x.dtype)

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

        encoded_latent = self.jumping_knowledge_layer(conv_layer_outputs)

        # GraphMAE2 Re-Masking & Projector Phase
        if node_features_mask.numel() > 0:
            encoded_latent[node_features_mask] = self.latent_mask_token.to(encoded_latent.dtype)

        decoder_input = self.decoder_proj(encoded_latent)
        decoder = self.decoder_conv(decoder_input, edge_index, edge_attr=edge_attr)
        decoder = self.decoder_norm(decoder, batch.batch)
        decoder = self.gelu(decoder) + decoder_input

        # Node and Edge Feature Generation
        prediction_node_features = self.reconstruct_node_features(decoder)

        # Reconstruct Edge Features by concatenating source and destination node representations
        row, col = edge_index

        src_latent = decoder[row]
        dst_latent = decoder[col]

        edge_latents = torch.cat([
            src_latent,
            dst_latent
        ], dim=1)

        prediction_edge_features = self.reconstruct_edge_features(edge_latents)
        prediction_src_port = self.reconstruct_src_port(edge_latents)
        prediction_dst_port = self.reconstruct_dst_port(edge_latents)

        return prediction_node_features, (prediction_src_port, prediction_dst_port, prediction_edge_features)

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

    def get_model_metrics(self, batch):
        # Computes self_supervised multi-modal reconstruction loss and tracks circuit anomaly metrics

        with torch.no_grad():
            target_src_port = batch.edge_attr[:, 0].long()
            target_dst_port = batch.edge_attr[:, 1].long()
            target_edge_features = self.edge_feature_norm(batch.edge_attr[:, 2:])

        cell_type_embeddings = self.build_cell_embedding_vector(batch.type_indices, batch.type_lengths,
                                                                batch.type_counts)
        target_node = torch.cat([batch.x, cell_type_embeddings], dim=1)
        target_node = self.node_feature_norm(target_node)

        mask_size = max(1, int(self.mask_rate * batch.num_nodes))
        shuffled_indices = torch.randperm(batch.num_nodes, device=self.device)

        node_features_mask = torch.zeros(batch.num_nodes, dtype=torch.bool, device=self.device)
        node_features_mask[shuffled_indices[:mask_size]] = True

        # Forward pass call
        prediction_nodes, (prediction_src_port, prediction_dst_port, prediction_edge_features) = self(
            batch,
            node_features_mask=node_features_mask
        )

        with torch.amp.autocast(device_type='cuda', enabled=False):
            node_errors = self.mse_loss(prediction_nodes, target_node)

            edge_src_port_loss = self.focal_loss(prediction_src_port, target_src_port)
            edge_dst_port_loss = self.focal_loss(prediction_dst_port, target_dst_port)
            edge_features_loss = self.mse_loss(prediction_edge_features, target_edge_features).mean()

            # Softmax normalization bounds the loss constraints above zero
            # This generates a dynamic distribution weight for your 3 tasks
            edge_weights = torch.softmax(-self.edge_multipliers, dim=0) * 3.0

            # Derive precision multipliers (1 / sigma^2) smoothly from log-space values
            precision_node = torch.sigmoid(-self.node_multipliers) * 3.0 + 0.5
            precision_src = torch.exp(edge_weights[0])
            precision_dst = torch.exp(edge_weights[1])
            precision_edge = torch.exp(edge_weights[2])

            edge_errors = ((precision_src * edge_src_port_loss) +
                           (precision_dst * edge_dst_port_loss) +
                           (precision_edge * edge_features_loss)
                           )

            # Isolate Node Loss to Masked Cells
            loss_nodes = node_errors[node_features_mask].mean() if node_features_mask.numel() > 0 else torch.tensor(
                0.0, device=self.device)
            loss_nodes = precision_node * loss_nodes

            # GraphMAE2 Edge Masking Context Optimization
            row, col = batch.edge_index
            row, col, node_features_mask = row.long(), col.long(), node_features_mask.long()
            edge_mask = torch.isin(row, node_features_mask) | torch.isin(col, node_features_mask)
            loss_edges = edge_errors[edge_mask].mean() if edge_mask.any() else torch.tensor(0.0, device=self.device)

            # Balance loss by number of edges since dynamicbatchsampler will be set at 5000 max nodes
            density_ratio = max(1.0, batch.num_edges) / batch.num_nodes
            loss = loss_nodes + (loss_edges / density_ratio)

        metrics = (
            node_errors.mean().item(),
            edge_src_port_loss.mean().item(),
            edge_dst_port_loss.mean().item(),
            edge_features_loss.mean().item()
        )

        return loss, node_errors, metrics, node_features_mask
