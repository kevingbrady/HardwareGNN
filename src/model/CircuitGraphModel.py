import torch
from torch.nn import Module, ReLU, LeakyReLU, Linear, Sequential, BatchNorm1d, Dropout, EmbeddingBag, LayerNorm
from torchmetrics.classification import Accuracy, Precision, Recall
from torch_geometric.nn import GCNConv, GATv2Conv, global_mean_pool
from torch_geometric.utils import add_self_loops
from src.graph_builder.verilog_dataclasses import Cell

class TrojanGNN(Module):
    def __init__(self, input_dimension, hidden_dimension, output_dimension, embedding_dim=16, edge_dim=5, device='cpu'):
        super(TrojanGNN, self).__init__()
        self.device = device

        self.cell_embedding = EmbeddingBag(
            num_embeddings=Cell.get_total_cell_types() + 1,
            embedding_dim=embedding_dim,
            mode='sum',
            padding_idx=0
        )

        total_input_dim = input_dimension + embedding_dim
        #self.batch_norm1 = BatchNorm1d(total_input_dim)
        #self.batch_norm2 = BatchNorm1d(hidden_dimension * 4)

        self.batch_norm1 = LayerNorm(total_input_dim)
        self.batch_norm2 = LayerNorm(hidden_dimension * 4)

        self.conv1 = GATv2Conv(total_input_dim, hidden_dimension, edge_dim=edge_dim, heads=4, concat=True)
        self.conv2 = GATv2Conv(hidden_dimension * 4, hidden_dimension, edge_dim=edge_dim, heads=1, concat=False)
        self.linear = Linear(hidden_dimension, output_dimension)

        self.relu = ReLU()
        self.dropout = Dropout(0.25)

        self.accuracy_fn = Accuracy(task='binary').to(device, non_blocking=True)
        self.precision_fn = Precision(task='binary').to(device, non_blocking=True)
        self.recall_fn = Recall(task='binary').to(device, non_blocking=True)

        self.to(self.device, non_blocking=True)

    def zero_gradients(self):
        for param in self.parameters():
            param.grad = None

    def forward(self, batch):

        #edge_index, edge_attr = add_self_loops(batch.edge_index, edge_attr=batch.edge_attr, num_nodes=batch.num_nodes)

        zero_padding = torch.zeros(1, dtype=torch.long, device=self.device)
        offsets = torch.cumsum(
            torch.cat([zero_padding, batch.type_lengths]), dim=0
        )[:-1]

        # 3. Generate cell type embeddings safely
        cell_type_embeddings = self.cell_embedding(
            input=batch.type_indices,
            offsets=offsets,
            per_sample_weights=batch.type_counts
        )

        x = torch.cat([batch.x, cell_type_embeddings], dim=1)


        x = self.batch_norm1(x)
        x = self.conv1(x, batch.edge_index, edge_attr=batch.edge_attr)
        x = self.relu(x)
        x = self.dropout(x)

        x = self.batch_norm2(x)
        x = self.conv2(x, batch.edge_index, edge_attr=batch.edge_attr)
        x = self.relu(x)
        x = self.dropout(x)

        return self.linear(x)

    def get_model_metrics(self, batch, loss_function):
        batch.to(self.device, non_blocking=True)

        y_hat = self(batch).view(-1)
        target = batch.y.float().view(-1)
        loss = loss_function(y_hat, target)

        with torch.no_grad():
            accuracy = self.accuracy_fn(y_hat, batch.y)
            precision = self.precision_fn(y_hat, batch.y)
            recall = self.recall_fn(y_hat, batch.y)

        return loss, accuracy, precision, recall









