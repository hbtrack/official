"""
Logging estruturado JSON

Para produção, usar logging em JSON para integração com:
- CloudWatch (AWS)
- Stackdriver (GCP)
- Application Insights (Azure)

Referências RAG:
- R31: Ações críticas auditáveis
- R32: Log obrigatório (quem, quando, o quê)
"""
import logging
import json
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter para logs em JSON"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Adicionar campos extras
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "person_id"):
            log_data["person_id"] = record.person_id

        if hasattr(record, "organization_id"):
            log_data["organization_id"] = record.organization_id

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "path"):
            log_data["path"] = record.path

        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(env: str, log_level: str) -> None:
    """
    Configura logging conforme ambiente

    Args:
        env: "local", "staging", "production"
        log_level: "DEBUG", "INFO", "WARNING", "ERROR"
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()

    if env == "production":
        # JSON em produção
        console_handler.setFormatter(JSONFormatter())
    else:
        # Human-readable em dev
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Reduzir verbosidade de bibliotecas terceiras
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
