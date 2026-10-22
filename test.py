import torch
from src.TrojanGraphDataset import TrojanGraphDataset
from src.model.self_supervised.CircuitMAE import CircuitMAE
from src.model.supervised.CircuitGraphModel import TrojanGNN
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
from torch_geometric.loader import DataLoader, DynamicBatchSampler

import warnings
import os
import sys
import time
import logging
import gc
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

if __name__ == '__main__':

    if hasattr(sys, "_is_gil_enabled"):
        if not sys._is_gil_enabled():
            print('GIL is disabled (free-threaded)')

    else:
        print('GIL is enabled (not free-threaded)')

    print(Path.cwd())
    data_dir = '/data/TrustHub'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    trojan_dataset = TrojanGraphDataset(data_dir, build_dataset=False)
    logging.info(f'{logFormatter.gold}' + str(trojan_dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    dtype=torch.bfloat16
    total_time = time.time()
    best_run = []

    train_workers = os.cpu_count() - 4
    eval_workers = 2

    '''trojan_loader = DataLoader(
        trojan_dataset,
        prefetch_factor=2,
        persistent_workers=True,
        batch_sampler=DynamicBatchSampler(trojan_dataset, max_num=50000, shuffle=False, mode='node'),
        num_workers=train_workers,
        pin_memory=True
    )'''

    model = CircuitMAE(
        cell_embedding_dim=8,
        node_features_dim=21,
        hidden_dimension=128,
        node_mask_rate=0.75,
        edge_mask_rate=0.25,
        device=device
    )

    idx = 989
    loss_weights = torch.tensor([1.0, 0.1, 1.0, 1.0, 1.0, 1.0], device=device)

    checkpoint = torch.load('final_model/self_supervised/graph_mae_model.pth', weights_only=True)
    model.load_state_dict(checkpoint['state_dict'])

    graph = trojan_dataset[idx]
    node_scores = model.get_model_metrics(graph.to(device))
    instance_means = torch.mean(node_scores, dim=0, keepdim=True)
    instance_stds = torch.std(node_scores, dim=0, keepdim=True) + 1e-6
    normalized_scores = (node_scores - instance_means) / instance_stds

    weighted_scores = loss_weights * normalized_scores
    anomaly_scores = weighted_scores.sum(dim=-1)

    threshold = anomaly_scores.mean() + (3.0 * anomaly_scores.std())

    print(threshold)

    full_graph = trojan_dataset.get_full_graph(idx)

    for x, (name, cell) in enumerate(full_graph.netlist.items()):

        print(x, name, anomaly_scores[x])
        #if anomaly_scores[x] > threshold:
        #    print(x, name, anomaly_scores[x].item())

    '''idx = 992

    model = TrojanGNN(
        input_dimension=21,
        edge_dim=12,
        embedding_dim=8,
        hidden_dimension=256,
        output_dimension=1,
        threshold=0.5,
        device=device
    )

    model.load_state_dict(torch.load('final_model/supervised/trojan_detection_model.pth', weights_only=True))
    graph = trojan_dataset[idx]
    full_graph = trojan_dataset.get_full_graph(idx)

    predictions = model(graph.to(device))

    for x, (name, cell) in enumerate(full_graph.netlist.items()):
        #if predictions[x] > 0.5:
        print(x, name, predictions[x], cell.label)'''



