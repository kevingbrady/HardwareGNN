from src.logFormatter import logFormatter
import contextlib
import os
import sys
import torch
import logging

def pretty_time_delta(seconds) -> str:
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd %dh %dm %ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh %dm %ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm %ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)

def setup_logger():
    log_colors_dict = {
        'DEBUG': 'grey',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    }

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logFormatter(log_colors_dict))

    logger.addHandler(ch)

def calculate_metrics(y_hat: torch.Tensor, y: torch.Tensor, threshold: float=0.5) -> tuple[float, float, float]:

    #optimal_threshold = otsu_threshold(y_hat)
    #print(optimal_threshold)
    #y_hat = torch.where(y_hat >= threshold, 1, 0)

    TP = torch.sum(y_hat == y)
    FP = torch.sum(y_hat == y)
    TN = torch.sum(y_hat == y)
    FN = torch.sum(y_hat == y)

    #print(f'true positive: {TP}, true negative {TN}, false positive: {FP}, false negative: {FN}')

    # Calculate metrics

    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    return accuracy, precision, recall

@contextlib.contextmanager
def output_manager(silent=False):
    # Mutes stdout if silent is True, otherwise output can pass through
    if not silent:
        yield
        return
    sys.stdout.flush()

    with contextlib.ExitStack() as stack:
        # 1. Open /dev/null and schedule its closure
        devnull = os.open(os.devnull, os.O_WRONLY)
        stack.callback(os.close, devnull)

        # 2. Back up the original stdout descriptor (1)
        old_stdout_fd = os.dup(1)

        # --- CRITICAL LIFO ORDER CORRECTION ---
        # We want os.close to happen LAST during cleanup, so we register it FIRST.
        stack.callback(os.close, old_stdout_fd)
        # We want os.dup2 to happen FIRST during cleanup, so we register it LAST.
        stack.callback(os.dup2, old_stdout_fd, 1)

        # 3. Force descriptor 1 to redirect to /dev/null
        os.dup2(devnull, 1)

        yield

        sys.stdout.flush()


def compact_dir(obj):
    return set(dir(obj)) - set(dir(object))


