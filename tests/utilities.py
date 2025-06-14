import sys
from logging import INFO, Formatter, Logger, StreamHandler, getLogger


def get_print_logger(name: str = "") -> Logger:
    """
    Retrieve or create a logger which prints to `sys.stdout`.
    """
    log: Logger = getLogger(*((name,) if name else ()))
    log.setLevel(INFO)
    if not log.handlers:
        handler = StreamHandler(sys.stdout)
        handler.setLevel(INFO)
        handler.setFormatter(
            Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        log.addHandler(handler)
    return log
