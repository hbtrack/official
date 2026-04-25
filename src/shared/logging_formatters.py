"""
FlowIDFormatter — HB Track
Formatter JSON que inclui flow_id, module, level e timestamp em cada registro.
INV-LOG: todo log tem flow_id rastreável (FASE 1.7).
"""
from __future__ import annotations

import json
import logging

from shared.middleware import get_current_flow_id


class FlowIDFormatter(logging.Formatter):
    """Formatter JSON estruturado com flow_id propagado via ContextVar (seguro para ASGI/async)."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "time": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "module": record.name,
                "message": record.getMessage(),
                "flow_id": get_current_flow_id(),
            },
            ensure_ascii=False,
        )
