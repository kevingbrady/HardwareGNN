import torch

from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
from torch.utils.data import Subset, SubsetRandomSampler, random_split
from sentence_transformers import SentenceTransformer
from src.VerilogGraphDataset import VerilogGraphDataset
from src.model.CircuitGraphModel import TrojanGNN
from src.utils import pretty_time_delta, setup_logger
from src.logFormatter import logFormatter
from torch.utils.data import DataLoader

import warnings
import os
import sys
import time
import logging

warnings.filterwarnings("ignore", category=UserWarning)

if __name__ == '__main__':

    if sys._is_gil_enabled(): print('GIL is enabled (not free-threaded)')
    else: print('GIL is disabled (free-threaded)')

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed'
    setup_logger()
    device = (torch.device('cpu'), torch.device('cuda:0'))[torch.cuda.is_available()]

    dataset = VerilogGraphDataset(data_dir)
    logging.info(f'{logFormatter.gold}' + str(dataset))
    logging.info(f'{logFormatter.gold}' + str(device))

    dataset.batch_size = 1

    model = TrojanGNN(
        input_dimension=21,
        hidden_dimension=32,
        output_dimension=1,
        device=device
    )

    model = torch.compile(model, mode='reduce-overhead')

    optimizer = torch.optim.AdamW(model.parameters(), lr=torch.tensor(0.00001), betas=(0.9, 0.999))
    model.zero_gradients()
    criterion = BCEWithLogitsLoss(pos_weight=torch.tensor([dataset.pos_weight])).to(model.device, non_blocking=True)

    epochs = 5
    #training_samples = dataset.batch_size * 400
    early_stop = 3
    total_time = time.time()
    test_performance = []
    print(dataset[3])

    '''
    for epoch in range(epochs):

        epoch_start_time = time.time()
        graph_count = 0

        training, validation, test = random_split(dataset, [0.8, 0.1, 0.1])

        train_loader = DataLoader(
            training,
            batch_size=dataset.batch_size,
            #sampler=SubsetRandomSampler(torch.randint(0, len(training), (training_samples,))),
            num_workers=os.cpu_count(),
            pin_memory=True
        )

        val_loader = DataLoader(
            validation,
            batch_size=dataset.batch_size,
            sampler=SubsetRandomSampler(torch.randint(0, len(validation), (dataset.batch_size * 8,))),
            num_workers=int(os.cpu_count() / 6),
            pin_memory=True
        )

        test_loader = DataLoader(
            test,
            batch_size=dataset.batch_size,
            sampler=SubsetRandomSampler(torch.randint(0, len(test), (dataset.batch_size * 6,))),
            num_workers=int(os.cpu_count() / 6),
            pin_memory=True
        )

        model.train()

        for batch_idx, (batch, label) in enumerate(train_loader):

            with torch.amp.autocast(device_type='cuda', dtype=torch.float16):

                batch_start_time = time.time()
                graph_count += batch.size(0)

                (loss,
                 accuracy,
                 precision,
                 recall) = model.get_model_metrics(batch, label, criterion)

                loss.backward()
                optimizer.step()
                model.zero_gradients()

                if batch_idx % 5 == 0:
                    model.eval()
                    with torch.no_grad():
                        for v_batch, v_label in val_loader:
                            (v_loss,
                             v_accuracy,
                             v_precision,
                             v_recall) = model.get_model_metrics(v_batch, v_label, criterion)

                    model.train()

                logging.info(f'{logFormatter.gold}Epoch {epoch + 1}: [{pretty_time_delta(time.time() - epoch_start_time)}] {logFormatter.green}TRAIN [{loss.item():.5f}] [accuracy, precision, recall]: [{accuracy.item():.3f}, {precision.item():.3f}, {recall.item():.3f}] {logFormatter.orange}VALIDATION [{v_loss.item():.5f}] [{v_accuracy.item():.3f}, {v_precision.item():.3f}, {v_recall.item():.3f}] {logFormatter.purple}({graph_count}/{training_samples})')

        logging.info(f'{logFormatter.gold}Epoch {epoch + 1} completed in {pretty_time_delta(time.time() - epoch_start_time)}')

        model.eval()
        with torch.no_grad():
            for t_batch, t_label in test_loader:
                (t_loss,
                 t_accuracy,
                 t_precision,
                 t_recall) = model.get_model_metrics(t_batch, t_label, criterion)

        test_performance.append(t_accuracy)
        logging.info(f'{logFormatter.blue}TEST [{t_loss.item():.5f}] [accuracy, precision, recall]: [{t_accuracy.item():.3f}, {t_precision.item():.3f}, {t_recall.item():.3f}]')

        if epoch > early_stop:
            check_early_stop = test_performance[(-1 * early_stop):]
            if t_accuracy <= min(check_early_stop):
                break

    #os.makedirs('final_model', exist_ok=True)
    #torch.save(model.state_dict(), 'final_model/key_extractor_model.pth')
    logging.info(f'{logFormatter.gold}Total training time: {pretty_time_delta(time.time() - total_time)}')'''