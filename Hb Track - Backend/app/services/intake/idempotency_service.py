"""
Serviço de Idempotência para Ficha Única
FASE 3 - Service Layer
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.idempotency_key import IdempotencyKey

logger = logging.getLogger("hb.intake.idempotency")


def compute_request_hash(payload: Dict[str, Any]) -> str:
    """
    Gera hash SHA-256 do payload para validação de replay.
    
    Args:
        payload: Dicionário com dados da requisição
    
    Returns:
        Hash SHA-256 em hexadecimal
    """
    # Serializa payload de forma determinística
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    hash_obj = hashlib.sha256(payload_str.encode('utf-8'))
    return hash_obj.hexdigest()


def check_idempotency(
    db: Session,
    key: str,
    endpoint: str,
    payload: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Verifica se requisição já foi processada anteriormente.
    
    Args:
        db: Sessão do banco
        key: Chave de idempotência fornecida pelo cliente
        endpoint: Endpoint da requisição
        payload: Payload da requisição
    
    Returns:
        Response armazenado se encontrado, None caso contrário
    """
    request_hash = compute_request_hash(payload)
    
    # Busca registro existente
    existing = (
        db.query(IdempotencyKey)
        .filter(
            IdempotencyKey.key == key,
            IdempotencyKey.endpoint == endpoint
        )
        .first()
    )
    
    if not existing:
        logger.info(f"Idempotency check: NEW request | key={key} | endpoint={endpoint}")
        return None
    
    # Valida hash do payload
    if existing.request_hash != request_hash:
        logger.warning(
            f"Idempotency check: HASH MISMATCH | key={key} | "
            f"stored_hash={existing.request_hash[:8]}... | "
            f"current_hash={request_hash[:8]}..."
        )
        # Mesmo key, mas payload diferente = erro
        return {
            "error": "conflict",
            "detail": "Idempotency key reused with different payload",
            "status_code": 409
        }
    
    # Hash igual = replay legítimo, retorna response armazenado
    logger.info(
        f"Idempotency check: REPLAY detected | key={key} | "
        f"status={existing.status_code} | "
        f"created_at={existing.created_at.isoformat()}"
    )
    
    return {
        "response": existing.response_json,
        "status_code": existing.status_code,
        "replay": True
    }


def save_idempotency(
    db: Session,
    key: str,
    endpoint: str,
    payload: Dict[str, Any],
    response: Dict[str, Any],
    status_code: int
) -> None:
    """
    Salva resposta para idempotência futura.
    
    Args:
        db: Sessão do banco
        key: Chave de idempotência
        endpoint: Endpoint da requisição
        payload: Payload da requisição
        response: Response a ser armazenado
        status_code: HTTP status code
    """
    request_hash = compute_request_hash(payload)
    
    idempotency_record = IdempotencyKey(
        key=key,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=response,
        status_code=status_code,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(idempotency_record)
    db.commit()
    
    logger.info(
        f"Idempotency saved | key={key} | "
        f"endpoint={endpoint} | "
        f"status={status_code}"
    )
