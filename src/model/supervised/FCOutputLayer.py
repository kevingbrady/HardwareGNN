import torch
from torch.nn import Module, ModuleList, ReLU, LeakyReLU, Linear, Dropout, LayerNorm

class FCOutputLayer(Module):
    def __init__(self, hidden_one, hidden_two, output_dimension):
        super(FCOutputLayer, self).__init__()

        self.linear1 = Linear(hidden_one, hidden_one)
        self.linear2 = Linear(hidden_one, hidden_two)
        self.linear3 = Linear(hidden_two, hidden_two)

        self.output_layer = Linear(hidden_two, output_dimension)

        self.hidden_layers = [hidden_one, hidden_two]
        self.layer_norms = ModuleList([LayerNorm(x) for x in self.hidden_layers])

        self.activation_layers = ModuleList([ReLU(x) for x in self.hidden_layers])

    def forward(self, x):

        x = self.layer_norms[0](x)
        x = self.linear1(x)
        x = self.activation_layers[0](x)

        x = self.layer_norms[0](x)
        x = self.linear2(x)
        x = self.activation_layers[1](x)

        x = self.layer_norms[1](x)
        x = self.linear3(x)
        x = self.activation_layers[1](x)

        return self.output_layer(x)