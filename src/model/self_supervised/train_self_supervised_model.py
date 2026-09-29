import torch
from torch.utils.data import random_split
from src.TrojanGraphDataset import TrojanGraphDataset
from src.model.self_supervised.MultiModalCircuitMAE import MultiModalCircuitMAE
from src.model.loss_functions.ScaledCosineError import ScaledCosineError
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

    data_dir = '/data/decompressed'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    dataset = TrojanGraphDataset(data_dir)
    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    epochs = 45
    early_stop = epochs

    # 1. Update your model instantiation to map the full 23-dimensional feature space
    model = MultiModalCircuitMAE(
        cell_embedding_dim=16,
        node_features_dim=7,
        hidden_dimension=256,
        mask_rate=0.7,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead')
    #optimizer = torch.optim.AdamW(model.parameters(), lr=torch.tensor(5e-4), weight_decay=1e-4)
    optimizer = torch.optim.AdamW(model.get_optimizer_params(model, base_lr=1e-4, weight_decay=1e-3))
    scheduler = model.get_cooldown_with_warmup_scheduler(optimizer, warmup_epochs=35, total_epochs=epochs)
    scaler = torch.amp.GradScaler(device)

    criterion = ScaledCosineError()

    dtype=torch.bfloat16
    total_time = time.time()
    best_run = []

    training, validation, test = random_split(dataset, [0.8, 0.1, 0.1])
    train_workers = os.cpu_count() - 4
    eval_workers = 2

    train_loader = DataLoader(
        training,
        prefetch_factor=2,
        persistent_workers=True,
        batch_sampler=DynamicBatchSampler(training, max_num=50000, shuffle=True, mode='node'),
        num_workers=train_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        validation,
        batch_sampler=DynamicBatchSampler(validation, max_num=50000, shuffle=False, mode='node'),
        shuffle=False,
        num_workers=eval_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test,
        batch_sampler=DynamicBatchSampler(test, max_num=50000, shuffle=False, mode='node'),
        shuffle=False,
        num_workers=eval_workers,
        pin_memory=True
    )

    val_cycle = iter(val_loader)

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
                (loss, node_errors, node_features_mask) = model.get_model_metrics(batch, criterion)
                accuracy, precision, recall = model.get_predictions(batch, node_errors, node_features_mask)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()

            if batch_idx % 2 == 0:

                model.eval()

                with torch.no_grad():
                    try:
                        v_batch = next(val_cycle)
                    except StopIteration:
                        val_cycle = iter(val_loader)
                        v_batch = next(val_cycle)

                    v_batch = v_batch.to(device)

                    with torch.amp.autocast(device_type='cuda', dtype=dtype):
                        (v_loss, v_node_errors, v_node_features_mask) = model.get_model_metrics(v_batch, criterion)
                        v_accuracy, v_precision, v_recall = model.get_predictions(v_batch, v_node_errors, v_node_features_mask)

                model.train()

            logging.info(
                f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [accuracy, precision, recall]: [{accuracy:.3f}, {precision:.3f}, {recall:.3f}] {logFormatter.orange}VALIDATION [{v_loss.mean().item():.5f}] [{v_accuracy:.3f}, {v_precision:.3f}, {v_recall:.3f}] {logFormatter.purple}({graph_count}/{len(training)})')

        logging.info(
            f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

        # 5. Evaluate and output localized trojan nodes on the test set
        model.eval()

        t_loss_avg = 0.0
        t_accuracy_avg = 0.0
        t_precision_avg = 0.0
        t_recall_avg = 0.0
        t_batches = 0

        with torch.no_grad():
            for t_batch in test_loader:
                t_batch = t_batch.to(device)
                with torch.amp.autocast(device_type='cuda', dtype=dtype):
                    (t_loss, t_node_errors, t_node_features_mask) = model.get_model_metrics(t_batch, criterion)
                    t_accuracy, t_precision, t_recall = model.get_predictions(t_batch, t_node_errors, t_node_features_mask)

                    t_loss_avg += t_loss.mean().item()
                    t_accuracy_avg += t_accuracy
                    t_precision_avg += t_precision
                    t_recall_avg += t_recall
                    t_batches += 1

        t_loss_avg /= t_batches
        t_accuracy_avg /= t_batches
        t_precision_avg /= t_batches
        t_recall_avg /= t_batches

        scheduler.step()
        model.train()

        logging.info(
            f'{logFormatter.blue}TEST [{t_loss_avg:.5f}] [accuracy, precision, recall]: [{t_accuracy_avg:.3f}, {t_precision_avg:.3f}, {t_recall_avg:.3f}]')

        if epoch > 30:
            f1 = (2 * (t_precision_avg + t_recall_avg)) / (t_precision_avg + t_recall_avg + 1e-8)
            if best_run == [] or (f1 > best_run[-1]):
                best_run = [epoch, t_loss_avg, t_accuracy_avg, t_precision_avg, t_recall_avg, f1]

    del val_cycle
    del train_loader
    del val_loader
    del test_loader

    gc.collect()

    logging.info(f'{logFormatter.blue}[[[BEST RUN]]] Epoch {best_run[0]} [{best_run[1]}] [accuracy, precision, recall, f1]: [{best_run[2]}, {best_run[3]}, {best_run[4]}, {best_run[5]}]')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')