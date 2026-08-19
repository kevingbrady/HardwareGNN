import torch

from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
from torch.utils.data import Subset, SubsetRandomSampler, random_split
from sentence_transformers import SentenceTransformer
from src.VerilogGraphDataset import VerilogGraphDataset
from src.model.CircuitGraphModel import TrojanGNN
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
# from torch.utils.data import DataLoader
from torch_geometric.loader import DataLoader

import warnings
import os
import sys
import time
import logging
import itertools

warnings.filterwarnings("ignore", category=UserWarning)

if __name__ == '__main__':

    if sys._is_gil_enabled():
        print('GIL is enabled (not free-threaded)')
    else:
        print('GIL is disabled (free-threaded)')

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    dataset = VerilogGraphDataset(data_dir)
    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    dataset.batch_size = 32

    model = TrojanGNN(
        input_dimension=7,
        hidden_dimension=32,
        output_dimension=1,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead')

    optimizer = torch.optim.AdamW(model.parameters(), lr=torch.tensor(5e-4), weight_decay=1e-4)  # , betas=(0.9, 0.999))
    model.zero_gradients()
    criterion = BCEWithLogitsLoss(pos_weight=torch.tensor([min(dataset.pos_weight, 50.0)])).to(model.device, non_blocking=True)

    epochs = 50
    early_stop = 40
    total_time = time.time()
    test_performance = []

    training, validation, test = random_split(dataset, [0.8, 0.1, 0.1])
    training_samples = len(training)
    train_workers = 4
    eval_workers = 2

    train_loader = DataLoader(
        training,
        batch_size=dataset.batch_size,
        shuffle=True,
        num_workers=train_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        validation,
        batch_size=dataset.batch_size,
        shuffle=False,
        num_workers=eval_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test,
        batch_size=dataset.batch_size,
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

            batch_start_time = time.time()
            graph_count += dataset.batch_size
            model.zero_gradients()

            with torch.amp.autocast(device_type='cuda', dtype=torch.float16):

                (loss,
                 accuracy,
                 precision,
                 recall) = model.get_model_metrics(batch, criterion)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            if batch_idx % 2 == 0:
                model.eval()
                with torch.no_grad():
                    try:
                        v_batch = next(val_cycle)
                    except StopIteration:
                        val_cycle = iter(val_loader)
                        v_batch = next(val_cycle)

                    with torch.amp.autocast(device_type='cuda', dtype=torch.float16):
                        (v_loss,
                         v_accuracy,
                         v_precision,
                         v_recall) = model.get_model_metrics(v_batch, criterion)
                    test_performance.append(v_accuracy)
                model.train()

            logging.info(
                f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [accuracy, precision, recall]: [{accuracy.item():.3f}, {precision.item():.3f}, {recall.item():.3f}] {logFormatter.orange}VALIDATION [{v_loss.item():.5f}] [{v_accuracy.item():.3f}, {v_precision.item():.3f}, {v_recall.item():.3f}] {logFormatter.purple}({graph_count}/{training_samples})')

        logging.info(
            f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

        model.eval()
        with torch.no_grad():
            for t_batch in test_loader:
                with torch.amp.autocast(device_type='cuda', dtype=torch.float16):
                    (t_loss,
                     t_accuracy,
                     t_precision,
                     t_recall) = model.get_model_metrics(t_batch, criterion)


        logging.info(
            f'{logFormatter.blue}TEST [{t_loss.item():.5f}] [accuracy, precision, recall]: [{t_accuracy.item():.3f}, {t_precision.item():.3f}, {t_recall.item():.3f}]')

        if epoch > early_stop:
            check_early_stop = test_performance[(-1 * early_stop):]
            if v_accuracy <= min(check_early_stop):
                break

    # os.makedirs('final_model', exist_ok=True)
    # torch.save(model.state_dict(), 'final_model/key_extractor_model.pth')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')
