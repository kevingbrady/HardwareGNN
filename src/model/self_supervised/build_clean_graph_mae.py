import torch
from src.CleanGraphDataset import CleanGraphDataset
from src.model.self_supervised.MultiModalCircuitMAE import MultiModalCircuitMAE
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
from torch_geometric.loader import DataLoader, DynamicBatchSampler

import warnings
import os
import sys
import time
import logging
import gc

warnings.filterwarnings("ignore", category=UserWarning)

if __name__ == '__main__':

    if hasattr(sys, "_is_gil_enabled"):
        if not sys._is_gil_enabled():
            print('GIL is disabled (free-threaded)')

    else:
        print('GIL is enabled (not free-threaded)')

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    dataset = CleanGraphDataset(data_dir, build_dataset=False)
    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    epochs = 75

    # 1. Update your model instantiation to map the full 23-dimensional feature space
    model = MultiModalCircuitMAE(
        cell_embedding_dim=16,
        node_features_dim=7,
        hidden_dimension=256,
        mask_rate=0.5,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead')
    optimizer = torch.optim.AdamW(model.parameters(), lr=torch.tensor(5e-4), weight_decay=1e-4)
    scaler = torch.amp.GradScaler(device)

    dtype=torch.bfloat16
    total_time = time.time()

    train_workers = os.cpu_count()

    train_loader = DataLoader(
        dataset,
        prefetch_factor=2,
        persistent_workers=True,
        batch_sampler=DynamicBatchSampler(dataset, max_num=50000, shuffle=True, mode='node'),
        num_workers=train_workers,
        pin_memory=True
    )

    for epoch in range(epochs):

        epoch_start_time = time.time()
        graph_count = 0

        model.train()

        for batch_idx, batch in enumerate(train_loader):

            batch.to(device, non_blocking=True)
            batch_start_time = time.time()
            graph_count += batch.num_graphs
            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast(device_type='cuda', dtype=dtype):
                # 4. Your updated get_model_metrics handles masking & regression inside the model class
                (loss, node_errors, (node_reconstruction_loss, edge_src_port_loss, edge_dst_port_loss, edge_features_loss), node_features_mask) = model.get_model_metrics(batch)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()

            logging.info(
                f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [node_reconstruction_loss, edge_src_port_loss, edge_dst_port_loss, edge_features_loss]: [{node_reconstruction_loss:.3f}, {edge_src_port_loss:.3f}, {edge_dst_port_loss:.3f}, {edge_features_loss:.3f}] {logFormatter.purple}({graph_count}/{len(dataset)})')

        logging.info(
            f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

    del train_loader
    gc.collect()

    os.makedirs('final_model', exist_ok=True)
    torch.save(model._orig_mod.state_dict(), 'final_model/self_supervised/graph_mae_model.pth')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')