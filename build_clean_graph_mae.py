import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)
warnings.filterwarnings(action="ignore", category=FutureWarning)

from src.CleanGraphDataset import CleanGraphDataset
from src.model.self_supervised.CircuitMAE import CircuitMAE
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
from torch_geometric.loader import DataLoader, DynamicBatchSampler
from torch.optim.lr_scheduler import CosineAnnealingLR

import os
import sys
import time
import logging
import gc
import torch

#torch._dynamo.config.capture_scalar_outputs = True
#torch._inductor.config.max_autotune = False
#torch._inductor.config.triton.cudagraphs = False

if __name__ == '__main__':

    if hasattr(sys, "_is_gil_enabled"):
        if not sys._is_gil_enabled():
            print('GIL is disabled (free-threaded)')

    else:
        print('GIL is enabled (not free-threaded)')

    data_dir = '/home/kgb/VerilogDatasets'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    dataset = CleanGraphDataset(data_dir, build_dataset=True)
    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    exit(0)
    epochs = 100
    training_reconstruction_metrics = []

    model = CircuitMAE(
        cell_embedding_dim=8,
        node_features_dim=21,
        hidden_dimension=128,
        node_mask_rate=0.25,
        edge_mask_rate=0.05,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead', dynamic=True)
    #model.get_model_metrics = torch.compile(model.get_model_metrics, mode='default', dynamic=True)
    optimizer = torch.optim.AdamW(model.get_model_parameters(weight_decay=1e-4), lr=1e-3)   #, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    scaler = torch.amp.GradScaler(device=device.type)

    loss_weights = torch.tensor([1.0, 0.2, 1.0, 1.0, 1.0, 1.0], device=device)

    dtype = torch.bfloat16
    total_time = time.time()

    train_workers = os.cpu_count() - 4

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

            batch = batch.to(device, non_blocking=True)
            batch_start_time = time.time()
            graph_count += batch.num_graphs
            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast(device_type='cuda', dtype=dtype):
                # 4. Your updated get_model_metrics handles masking & regression inside the model class
                per_node_losses = model.get_model_metrics(batch)
                weighted_loss = per_node_losses * loss_weights
                loss = weighted_loss.sum(dim=-1).mean()

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()

            detached_metrics = weighted_loss.mean(dim=0).detach().cpu().numpy()

            #if epoch > 30:
                #training_reconstruction_metrics.append(detached_metrics.tolist())
            logging.info(
                f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [node_loss, struct_loss, latent_rep_loss, src_port_loss, dst_port_loss, edge_loss]: [{detached_metrics[0]:.3f}, {detached_metrics[1]:.3f}, {detached_metrics[2]:.3f}, {detached_metrics[3]:.3f}, {detached_metrics[4]:.3f}, {detached_metrics[5]:.3f}] {logFormatter.purple}({graph_count}/{len(dataset)})')

        scheduler.step()
        logging.info(
            f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

    del train_loader
    gc.collect()

    checkpoint = {
        'state_dict': model._orig_mod.state_dict()
    }

    os.makedirs('final_model', exist_ok=True)
    torch.save(checkpoint, 'final_model/self_supervised/graph_mae_model.pth')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')