import logging
import queue
import threading
import pathlib
from logging.handlers import RotatingFileHandler


def setup_logger(bot: str) -> logging.Logger:
    q = queue.Queue(-1)
    root = logging.getLogger(bot)
    root.setLevel(logging.INFO)

    root.handlers.clear()

    queue_handler = logging.handlers.QueueHandler(q)
    root.addHandler(queue_handler)

    logdir = pathlib.Path("/app/logs")
    logdir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        logdir / f"{bot}.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(formatter)

    def _listen():
        while True:
            try:
                record = q.get()
                if record is None:
                    break
                file_handler.emit(record)
            except Exception:
                pass

    listener_thread = threading.Thread(target=_listen, daemon=True)
    listener_thread.start()

    return root
