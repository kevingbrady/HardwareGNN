import torch
from torch.nn import Module, ModuleList, Linear, GELU, Parameter, LayerNorm, EmbeddingBag, Dropout, Sequential, MSELoss, \
    BCEWithLogitsLoss
from torch_geometric.nn import GATv2Conv, GraphNorm, JumpingKnowledge
from torch_geometric.utils import scatter
from src.graph_builder.verilog_dataclasses import Cell, Port
from src.model.loss_functions.FocalLoss import FocalLoss


class CircuitMAE(Module):
    def __init__(self, hidden_dimension, node_mask_rate=0.25, edge_mask_rate=0.25, cell_embedding_dim=8,
                 node_features_dim=17, edge_dim=12,
                 num_conv_layers=3, device='cpu'):
        super(CircuitMAE, self).__init__()

        self.total_input_dim = cell_embedding_dim + node_features_dim
        self.device = device
        self.node_mask_rate = node_mask_rate
        self.edge_mask_rate = edge_mask_rate

        # Create EmbeddingBag Layer for cell type embeddings
        self.cell_embedding = EmbeddingBag(
            num_embeddings=Cell.get_total_cell_types() + 1,
            embedding_dim=cell_embedding_dim,
            mode='sum',
            padding_idx=0
        )

        heads = 8
        decoder_heads = 1
        self.num_port_classes = len(Port.classes) + 1  # Last one is the mask token

        self.node_feature_norm = LayerNorm(self.total_input_dim)
        self.edge_feature_norm = LayerNorm(edge_dim - 2)  # Dont normalize src_port and dst_port categorical features

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
        self.decoder_conv = GATv2Conv(hidden_dimension, hidden_dimension // decoder_heads, edge_dim=edge_dim,
                                      heads=decoder_heads, concat=True)
        self.decoder_norm = GraphNorm(hidden_dimension)

        # GraphMAE2 Multi-Task Reconstruction Heads
        self.edge_reconstruction_dim = hidden_dimension * 2 + (edge_dim - 2)
        self.reconstruct_node_features = Sequential(Linear(hidden_dimension, hidden_dimension), GELU(),
                                                    Linear(hidden_dimension, self.total_input_dim))

        # GraphMAE2 Edge Feature Reconstruction Head
        self.reconstruct_edge_features = Sequential(Linear(self.edge_reconstruction_dim, hidden_dimension), GELU(),
                                                    Linear(hidden_dimension, edge_dim - 2))

        self.reconstruct_src_port = Linear(self.edge_reconstruction_dim, self.num_port_classes)
        self.reconstruct_dst_port = Sequential(Linear(self.edge_reconstruction_dim, hidden_dimension), GELU(),
                                               Linear(hidden_dimension, self.num_port_classes))

        # Decoder B: Predicts structural validity from pairwise node representations
        self.structural_bilinear_vector = Parameter(torch.ones(1, hidden_dimension))
        self.structural_link_bias = Parameter(torch.zeros(1))

        # GraphMAE2 Latency Projector: Projects encoder embeddings to align with decoder space
        self.latent_target_projector = Sequential(
            Linear(hidden_dimension, hidden_dimension),
            GELU(),
            Linear(hidden_dimension, hidden_dimension)
        )

        # Loss Functions declared directly within the architecture
        self.mse_loss = MSELoss(reduction='none')
        self.bce_loss = BCEWithLogitsLoss(reduction='none')
        self.focal_loss = FocalLoss(alpha=0.8, gamma=3.0, reduction='none', device=self.device)

        # Mask tokens for both modalities
        self.latent_mask_token = Parameter(torch.randn(1, hidden_dimension))
        self.edge_mask_token = Parameter(torch.randn(1, edge_dim - 2))

        #self.reconstruction_std_vectors = None
        #self.training_data_mean = None
        #self.optimal_trojan_threshold = None

        self.to(self.device, non_blocking=True)

    def get_model_parameters(self, weight_decay=1e-4):

        decay = []
        no_decay = []

        for name, param in self.named_parameters():
            if not param.requires_grad:
                continue

                # Exclude loss scaling multipliers and standard 1D bias/normalization layers
            if "loss_multipliers" in name or any(nd in name for nd in ["bias", "LayerNorm.weight", "GraphNorm.weight"]):
                no_decay.append(param)
            else:
                decay.append(param)

        return {'params': decay, 'weight_decay': weight_decay}, {'params': no_decay, 'weight_decay': 0.0}

    def forward(self, batch, node_features_mask=None, edge_features_mask=None, structural_eval_edges=None):

        # Combine into single node features vector
        cell_embedding_vector = self.build_cell_embedding_vector(batch.type_indices, batch.type_lengths,
                                                                 batch.type_counts)
        x = torch.cat([batch.x, cell_embedding_vector], dim=1)
        x = self.node_feature_norm(x)
        x = self.proj_in(x)

        normalized_edge_features = self.edge_feature_norm(batch.edge_attr[:, 2:])

        if edge_features_mask is not None and edge_features_mask.numel() > 0:

            edge_token = self.edge_mask_token.to(device=self.device, dtype=normalized_edge_features.dtype)
            edge_features_mask = edge_features_mask.unsqueeze(-1)

            edge_attr = torch.cat([
                torch.where(edge_features_mask, self.num_port_classes - 1, batch.edge_attr[:, 0:1]),
                torch.where(edge_features_mask, self.num_port_classes - 1, batch.edge_attr[:, 1:2]),
                torch.where(edge_features_mask, edge_token, normalized_edge_features)
            ], dim=1)

        else:
            edge_attr = torch.cat([batch.edge_attr[:, 0:2], normalized_edge_features], dim=1)

        if node_features_mask is not None and node_features_mask.numel() > 0:
            node_token = self.latent_mask_token.to(device=self.device, dtype=x.dtype)
            x = torch.where(node_features_mask.unsqueeze(-1), node_token, x)

        edge_index = batch.edge_index
        conv_layer_outputs = []

        for idx, (conv_layer, conv_norm) in enumerate(zip(self.conv_layers, self.conv_norms)):
            x = conv_layer(x, edge_index, edge_attr=edge_attr)
            x = conv_norm(x, batch.batch)
            x = self.gelu(x)
            x = self.dropout(x)

            conv_layer_outputs.append(x)

        encoded_latent_unmasked = self.jumping_knowledge_layer(conv_layer_outputs)

        encoded_latent = encoded_latent_unmasked

        # GraphMAE2 Re-Masking & Projector Phase
        if node_features_mask is not None and node_features_mask.numel() > 0:
            node_token = self.latent_mask_token.to(device=self.device, dtype=x.dtype)
            encoded_latent = torch.where(node_features_mask.unsqueeze(-1), node_token, encoded_latent_unmasked)

        decoder = self.decoder_conv(encoded_latent, edge_index, edge_attr=edge_attr)
        decoder = self.decoder_norm(decoder, batch.batch)
        decoder = self.gelu(decoder)

        # Node Feature Generation
        prediction_node_features = self.reconstruct_node_features(decoder)

        # Reconstruct Edge Features by concatenating source and destination node representations
        row, col = edge_index

        src_latent = decoder[row]
        dst_latent = decoder[col]

        edge_latents = torch.cat([
            src_latent,
            dst_latent,
            normalized_edge_features
        ], dim=1)

        prediction_edge_features = self.reconstruct_edge_features(edge_latents)
        prediction_src_port = self.reconstruct_src_port(edge_latents)
        prediction_dst_port = self.reconstruct_dst_port(edge_latents)
        prediction_link_logits = None

        if structural_eval_edges is not None:
            q_row, q_col = structural_eval_edges
            struct_src = decoder[q_row]
            struct_dst = decoder[q_col]

            scaled_interaction = struct_src * self.structural_bilinear_vector

            prediction_link_logits = torch.sum(scaled_interaction * struct_dst, dim=-1) + self.structural_link_bias

        return prediction_node_features, prediction_link_logits, encoded_latent_unmasked, decoder, (prediction_src_port,
                                                                                                    prediction_dst_port,
                                                                                                    prediction_edge_features)

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

    def get_node_edge_masks(self, batch, create_node_mask=False, create_edge_mask=False, structural_mask_rate=0.0):

        node_features_mask = None
        edge_features_mask = None
        unmasked_structural_indices = None
        structural_eval_edges = None
        structural_targets = None

        edge_index = batch.edge_index

        if create_node_mask:
            # Build Node Features Mask
            mask_size = max(1, int(self.node_mask_rate * batch.num_nodes))
            shuffled_node_indices = torch.randperm(batch.num_nodes, device=self.device)
            node_features_mask = torch.zeros(batch.num_nodes, dtype=torch.bool, device=self.device)
            node_features_mask[shuffled_node_indices[:mask_size]] = True

        if create_edge_mask:
            # Build Edge Features Mask
            edge_mask_size = max(1, int(self.edge_mask_rate * edge_index.size(1)))
            shuffled_edge_indices = torch.randperm(batch.num_edges, device=self.device)
            edge_features_mask = torch.zeros(batch.num_edges, dtype=torch.bool, device=self.device)
            edge_features_mask[shuffled_edge_indices[:edge_mask_size]] = True

        if structural_mask_rate > 0.0:
            structural_mask_size = max(1, int(structural_mask_rate * edge_index.size(1)))
            shuffled_structural_indices = torch.randperm(batch.edge_index.size(1), device=self.device)
            masked_structural_indices = shuffled_structural_indices[:structural_mask_size]
            unmasked_structural_indices = shuffled_structural_indices[structural_mask_size:]

            # Positive items: Real hidden Driver -> Sink edges
            true_hidden_edges = edge_index[:, masked_structural_indices]

            neg_src = true_hidden_edges[0]
            random_shift = torch.randint(1, batch.num_nodes - 1, (1, ), device=self.device)
            neg_dst = (true_hidden_edges[1] + random_shift) % batch.num_nodes

            fake_random_edges = torch.stack([neg_src, neg_dst], dim=0)


            # Concatenate structural evaluations
            structural_eval_edges = torch.cat([true_hidden_edges, fake_random_edges], dim=1)

            # Ground Truth targets: 1.0 for feed-forward wiring, 0.0 for reverse feedback noise
            true_labels = torch.ones(true_hidden_edges.size(1), device=self.device)
            fake_labels = torch.zeros(fake_random_edges.size(1), device=self.device)
            structural_targets = torch.cat([true_labels, fake_labels], dim=0)

            if edge_features_mask is not None:
                edge_features_mask[masked_structural_indices] = True

        return node_features_mask, edge_features_mask, structural_eval_edges, structural_targets, unmasked_structural_indices

    def get_model_metrics(self, batch):
        # Computes self_supervised multi-modal reconstruction loss and tracks circuit anomaly metrics
        cell_type_embeddings = self.build_cell_embedding_vector(batch.type_indices, batch.type_lengths,
                                                                batch.type_counts)
        target_node = torch.cat([batch.x, cell_type_embeddings], dim=1)
        target_node = self.node_feature_norm(target_node)
        target_src_port = batch.edge_attr[:, 0].long()
        target_dst_port = batch.edge_attr[:, 1].long()
        target_edge_features = self.edge_feature_norm(batch.edge_attr[:, 2:])

        node_features_mask = None
        edge_features_mask = None
        structural_eval_edges = batch.edge_index
        structural_targets = batch.edge_index

        if self.training:

            (node_features_mask,
             edge_features_mask,
             structural_eval_edges,
             structural_targets,
             unmasked_structural_indices) = self.get_node_edge_masks(batch, create_node_mask=True, create_edge_mask=True, structural_mask_rate=0.2)

        predictions = self(
            batch,
            node_features_mask=node_features_mask,
            edge_features_mask=edge_features_mask,
            structural_eval_edges=structural_eval_edges
        )

        (prediction_nodes,
         prediction_link_logits,
         encoder_latent_unmasked,
         decoder,
         (prediction_src_port, prediction_dst_port, prediction_edge_features)) = predictions

        num_nodes = batch.num_nodes
        row, col = batch.edge_index
        struct_row, struct_col = structural_eval_edges
        reduce = 'mean'

        with (torch.amp.autocast(device_type='cuda', enabled=False)):
            # Isolate Node Loss to Masked Cells
            node_features_loss = torch.mean(self.mse_loss(prediction_nodes, target_node), dim=-1)

            # GraphMAE2 Edge Masking Context Optimization
            edge_src_port_loss = self.focal_loss(prediction_src_port, target_src_port)
            edge_dst_port_loss = self.focal_loss(prediction_dst_port, target_dst_port)
            edge_features_loss = torch.mean(self.mse_loss(prediction_edge_features, target_edge_features), dim=-1)

            latent_reg_loss = torch.mean(self.mse_loss(decoder, self.latent_target_projector(encoder_latent_unmasked)), dim=-1)
            structural_loss = self.bce_loss(prediction_link_logits, structural_targets)

            if self.training:

                reduce = 'sum'
                node_features_loss = node_features_loss * node_features_mask
                edge_src_port_loss = edge_src_port_loss * edge_features_mask
                edge_dst_port_loss = edge_dst_port_loss * edge_features_mask
                edge_features_loss = edge_features_loss * edge_features_mask

            src_pack = torch.stack([edge_src_port_loss, edge_features_loss], dim=-1)
            dst_pack = torch.stack([edge_dst_port_loss, edge_features_loss], dim=-1)

            scatter_src = scatter(src_pack, row, dim=0, dim_size=batch.num_nodes, reduce=reduce)
            scatter_dst = scatter(dst_pack, col, dim=0, dim_size=batch.num_nodes, reduce=reduce)

            struct_pack = torch.stack([structural_loss, torch.ones_like(structural_loss)], dim=-1)
            scatter_struct_src = scatter(struct_pack, struct_row, dim=0, dim_size=num_nodes, reduce='sum')
            scatter_struct_dst = scatter(struct_pack, struct_col, dim=0, dim_size=num_nodes, reduce='sum')

            if self.training:
                # Pull counts using the boolean mask array directly
                counts_src = scatter(edge_features_mask, row, dim=0, dim_size=num_nodes, reduce='sum').unsqueeze(
                    -1).clamp(min=1.0)
                counts_dst = scatter(edge_features_mask, col, dim=0, dim_size=num_nodes, reduce='sum').unsqueeze(
                    -1).clamp(min=1.0)

                src_metrics = scatter_src / counts_src
                dst_metrics = scatter_dst / counts_dst
            else:
                src_metrics = scatter_src
                dst_metrics = scatter_dst

                # Unified structural calculation resolves the inference sum breakdown cleanly
            node_structural_loss = 0.5 * (
                    (scatter_struct_src[:, 0] / scatter_struct_src[:, 1].clamp(min=1.0)) +
                    (scatter_struct_dst[:, 0] / scatter_struct_dst[:, 1].clamp(min=1.0))
            )

            # --- 5. Extract Outputs into Final Unified Matrix Matrix ---
            node_src_port_loss = src_metrics[:, 0]
            node_dst_port_loss = dst_metrics[:, 0]
            node_edge_feat_loss = 0.5 * (src_metrics[:, 1] + dst_metrics[:, 1])

        per_node_metrics_matrix = torch.stack([
            node_features_loss,
            node_structural_loss,
            latent_reg_loss,
            node_src_port_loss,
            node_dst_port_loss,
            node_edge_feat_loss
        ], dim=-1)

        return per_node_metrics_matrix


