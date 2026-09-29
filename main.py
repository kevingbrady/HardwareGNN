import os
import torch
from torch.utils.data import random_split
from src.TrojanGraphDataset import TrojanGraphDataset
from src.model.supervised.CircuitGraphModel import TrojanGNN
from src.model.loss_functions.FocalLoss import FocalLoss
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
from torch_geometric.loader import DataLoader, DynamicBatchSampler

import warnings
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

    dataset = TrojanGraphDataset(data_dir, build_dataset=True)

    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    hidden_dim = 256
    threshold = 0.5
    dtype = torch.bfloat16
    max_nodes = 50000

    model = TrojanGNN(
        input_dimension=7,
        hidden_dimension=hidden_dim,
        output_dimension=1,
        threshold=threshold,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead')

    optimizer = torch.optim.AdamW(model.parameters(), lr=torch.tensor(5e-4), weight_decay=1e-4)
    criterion = FocalLoss(alpha=0.85, gamma=3.0, device=device)
    scaler = torch.amp.GradScaler(device)

    epochs = 100
    early_stop = epochs
    total_time = time.time()
    best_run = []

    training, validation, test = random_split(dataset, [0.8, 0.1, 0.1])
    train_workers = os.cpu_count() - 4
    eval_workers = 2

    train_loader = DataLoader(
        training,
        batch_sampler=DynamicBatchSampler(training, max_num=max_nodes, shuffle=True, mode='node'),
        num_workers=train_workers,
        prefetch_factor=2,
        persistent_workers=True,
        pin_memory=True
    )

    val_loader = DataLoader(
        validation,
        batch_sampler=DynamicBatchSampler(validation, max_num=max_nodes, shuffle=False, mode='node'),
        shuffle=False,
        num_workers=eval_workers,
        persistent_workers=True,
        pin_memory=True
    )

    test_loader = DataLoader(
        test,
        batch_sampler=DynamicBatchSampler(test, max_num=max_nodes, shuffle=False, mode='node'),
        shuffle=False,
        num_workers=eval_workers,
        persistent_workers=True,
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

                (loss,
                 accuracy,
                 precision,
                 recall) = model.get_model_metrics(batch, criterion)

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

                    v_batch.to(device, non_blocking=True)

                    with torch.amp.autocast(device_type='cuda', dtype=dtype):
                        (v_loss,
                         v_accuracy,
                         v_precision,
                         v_recall) = model.get_model_metrics(v_batch, criterion)

                model.train()

            logging.info(
                f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [accuracy, precision, recall]: [{accuracy.item():.3f}, {precision.item():.3f}, {recall.item():.3f}] {logFormatter.orange}VALIDATION [{v_loss.item():.5f}] [{v_accuracy.item():.3f}, {v_precision.item():.3f}, {v_recall.item():.3f}] {logFormatter.purple}({graph_count}/{len(training)})')

        logging.info(
            f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

        model.eval()

        with torch.no_grad():
            avg_t_loss = 0.0
            avg_t_accuracy = 0.0
            avg_t_precision = 0.0
            avg_t_recall = 0.0
            num_test_batches = 0

            for t_batch in test_loader:

                t_batch.to(device, non_blocking=True)
                num_test_batches += 1

                with torch.amp.autocast(device_type='cuda', dtype=dtype):
                    (t_loss,
                     t_accuracy,
                     t_precision,
                     t_recall) = model.get_model_metrics(t_batch, criterion)

                    avg_t_loss += t_loss.item()
                    avg_t_accuracy += t_accuracy.item()
                    avg_t_precision += t_precision.item()
                    avg_t_recall += t_recall.item()

        avg_t_loss = avg_t_loss / num_test_batches
        avg_t_accuracy = avg_t_accuracy / num_test_batches
        avg_t_precision = avg_t_precision / num_test_batches
        avg_t_recall = avg_t_recall / num_test_batches

        model.train()

        logging.info(
            f'{logFormatter.blue}TEST [{avg_t_loss:.5f}] [accuracy, precision, recall]: [{avg_t_accuracy:.3f}, {avg_t_precision:.3f}, {avg_t_recall:.3f}]')

        if epoch > 40:
            f1 = (2 * (avg_t_precision + avg_t_recall)) / (avg_t_precision + avg_t_recall + 1e-8)
            if best_run == [] or (f1 > best_run[-1]):
                best_run = [epoch, avg_t_loss, avg_t_accuracy, avg_t_precision, avg_t_recall, f1]
                os.makedirs('final_model', exist_ok=True)
                torch.save(model._orig_mod.state_dict(), 'final_model/supervised/trojan_detection_model.pth')

    del val_cycle
    del train_loader
    del val_loader
    del test_loader

    gc.collect()

    logging.info(f'{logFormatter.blue}[[[BEST RUN]]] Epoch {best_run[0]} [{best_run[1]}] [accuracy, precision, recall, f1]: [{best_run[2]}, {best_run[3]}, {best_run[4]}, {best_run[5]}]')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')

    '''best_model = TrojanGNN(
        input_dimension=7,
        hidden_dimension=hidden_dim,
        output_dimension=1,
        threshold=threshold,
        device=device
    )
    best_model.load_state_dict(torch.load('final_model/trojan_detection_model.pth'))
    best_model = torch.compile(best_model, mode='reduce-overhead')
    best_model = best_model._orig_mod if hasattr(best_model, '_orig_mod') else best_model

    best_model.calculate_optimal_threshold(validation, dtype=dtype)'''
