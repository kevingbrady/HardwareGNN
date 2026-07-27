import contextlib
import os
import sys

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


