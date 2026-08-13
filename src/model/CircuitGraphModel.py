import torch
from torch.nn import Module, ReLU, LeakyReLU, Linear, Sequential, BatchNorm1d, Dropout
from torchmetrics.classification import Accuracy, Precision, Recall
from torch_geometric.nn import GCNConv, GATv2Conv

class TrojanGNN(Module):
    def __init__(self, input_dimension, hidden_dimension, output_dimension, device='cpu'):
        super(TrojanGNN, self).__init__()
        self.device = device

        self.conv1 = GATv2Conv(input_dimension, hidden_dimension, heads=4, concat=True)
        self.conv2 = GATv2Conv(hidden_dimension * 4, output_dimension, heads=1, concat=False)

        self.accuracy_fn = Accuracy(task='binary').to(device, non_blocking=True)
        self.precision_fn = Precision(task='binary').to(device, non_blocking=True)
        self.recall_fn = Recall(task='binary').to(device, non_blocking=True)

        self.to(self.device, non_blocking=True)

    def zero_gradients(self):
        for param in self.parameters():
            param.grad = None

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = ReLU()(x)
        x = Dropout(0.2)(x)

        x = self.conv2(x, edge_index)
        return x

    def get_model_metrics(self, batch, y_label, loss_function):
        batch.to(self.device, non_blocking=True)
        y_label.to(self.device, non_blocking=True)

        y_hat = self(batch)
        loss = loss_function(y_hat, y_label)

        accuracy = self.accuracy_fn(y_hat, y_label)
        precision = self.precision_fn(y_hat, y_label)
        recall = self.recall_fn(y_hat, y_label)

        return loss, accuracy, precision, recall









