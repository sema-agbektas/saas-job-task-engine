import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
import os
import socket


task_id_var: ContextVar[str | None] = ContextVar("task_id", default=None)
worker_id_var: ContextVar[str | None] = ContextVar("worker_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "task_id": task_id_var.get(),
            "worker_id": worker_id_var.get(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)