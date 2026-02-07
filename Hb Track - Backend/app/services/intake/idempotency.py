"""
Controle de idempotência para Ficha Única

FASE 3 - FICHA.MD Seção 3.3

Sistema para evitar processamento duplicado de requisições usando
header Idempotency-Key.

Fluxo:
1. Cliente envia header 'Idempotency-Key: <uuid>'
2. Backend verifica se já processou essa key + endpoint
3. Se sim: retorna response armazenado
4. Se não: processa, salva response, retorna

Regras:
- Mesma key + endpoint + payload diferente = 409 Conflict
- Mesma key + endpoint + mesmo payload = retorna response salvo
- Keys expiram após 24h (limpeza via scheduled job)
"""
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.idempotency_key import IdempotencyKey

logger = logging.getLogger("hb.idempotency")


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def compute_request_hash(payload: dict) -> str:
    """
    Gera hash SHA-256 do payload para comparação.
    
    Args:
        payload: Dicionário do payload da requisição
    
    Returns:
        Hash SHA-256 em hexadecimal (64 caracteres)
    """
    # Serializar com ordenação de chaves para consistência
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()


def serialize_response(response: Any) -> dict:
    """
    Serializa response para armazenamento em JSONB.
    
    Args:
        response: Response Pydantic ou dict
    
    Returns:
        Dicionário serializável
    """
    if hasattr(response, 'model_dump'):
        return response.model_dump(mode='json')
    elif hasattr(response, 'dict'):
        return response.dict()
    return dict(response) if response else {}


# =============================================================================
# VERIFICAÇÃO DE IDEMPOTÊNCIA
# =============================================================================

def check_idempotency(
    db: Session,
    key: str,
    endpoint: str,
    payload: dict
) -> Optional[Dict[str, Any]]:
    """
    Verifica se requisição já foi processada.
    
    Args:
        db: Sessão do banco
        key: Idempotency-Key do header
        endpoint: Endpoint da requisição (ex: "/api/v1/intake/ficha-unica")
        payload: Payload da requisição
    
    Returns:
        Dict com 'response' e 'status_code' se já processado, None caso contrário
    
    Raises:
        HTTPException 409: Se key existe com payload diferente
    """
    if not key:
        return None
    
    request_hash = compute_request_hash(payload)
    
    # Buscar registro existente
    existing = db.query(IdempotencyKey).filter(
        and_(
            IdempotencyKey.key == key,
            IdempotencyKey.endpoint == endpoint
        )
    ).first()
    
    if existing:
        # Verificar se payload é o mesmo
        if existing.request_hash != request_hash:
            logger.warning(
                "IDEMPOTENCY | Hash mismatch | key=%s endpoint=%s",
                key, endpoint
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "IDEMPOTENCY_CONFLICT",
                    "message": "Idempotency-Key já usada com payload diferente",
                    "details": {
                        "key": key,
                        "endpoint": endpoint
                    }
                }
            )
        
        # Payload idêntico: retornar response salvo
        logger.info(
            "IDEMPOTENCY | Cache hit | key=%s endpoint=%s status=%d",
            key, endpoint, existing.status_code or 200
        )
        
        return {
            "response": existing.response_json,
            "status_code": existing.status_code or 200
        }
    
    logger.debug("IDEMPOTENCY | Cache miss | key=%s endpoint=%s", key, endpoint)
    return None


def save_idempotency(
    db: Session,
    key: str,
    endpoint: str,
    payload: dict,
    response: Any,
    status_code: int
) -> None:
    """
    Salva resposta para idempotência futura.
    
    Args:
        db: Sessão do banco
        key: Idempotency-Key do header
        endpoint: Endpoint da requisição
        payload: Payload da requisição
        response: Response a armazenar
        status_code: HTTP status code
    """
    if not key:
        return
    
    request_hash = compute_request_hash(payload)
    response_json = serialize_response(response)
    
    idempotency_record = IdempotencyKey(
        key=key,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=response_json,
        status_code=status_code
    )
    
    db.add(idempotency_record)
    
    try:
        db.commit()
        logger.info(
            "IDEMPOTENCY | Saved | key=%s endpoint=%s status=%d",
            key, endpoint, status_code
        )
    except Exception as e:
        logger.error(
            "IDEMPOTENCY | Save failed | key=%s error=%s",
            key, str(e)
        )
        db.rollback()
        # Não propagar erro - idempotência é best-effort


# =============================================================================
# LIMPEZA DE REGISTROS ANTIGOS
# =============================================================================

def cleanup_expired_keys(
    db: Session,
    max_age_hours: int = 24
) -> int:
    """
    Remove registros de idempotência expirados.
    
    Args:
        db: Sessão do banco
        max_age_hours: Idade máxima em horas (default: 24h)
    
    Returns:
        Número de registros removidos
    """
    from datetime import timedelta
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    
    # Contar e deletar registros antigos
    deleted_count = db.query(IdempotencyKey).filter(
        IdempotencyKey.created_at < cutoff
    ).delete(synchronize_session=False)
    
    db.commit()
    
    if deleted_count > 0:
        logger.info(
            "IDEMPOTENCY | Cleanup | removed=%d cutoff=%s",
            deleted_count, cutoff.isoformat()
        )
    
    return deleted_count


# =============================================================================
# CONTEXT MANAGER (OPCIONAL)
# =============================================================================

class IdempotencyGuard:
    """
    Context manager para idempotência.
    
    Uso:
        async with IdempotencyGuard(db, key, endpoint, payload) as guard:
            if guard.cached_response:
                return guard.cached_response
            
            # Processar normalmente
            response = do_work()
            guard.save_response(response, 201)
            return response
    """
    
    def __init__(
        self,
        db: Session,
        key: Optional[str],
        endpoint: str,
        payload: dict
    ):
        self.db = db
        self.key = key
        self.endpoint = endpoint
        self.payload = payload
        self.cached_response: Optional[Dict[str, Any]] = None
    
    def __enter__(self) -> "IdempotencyGuard":
        if self.key:
            self.cached_response = check_idempotency(
                self.db, self.key, self.endpoint, self.payload
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        # Não suprime exceções
        return False
    
    def save_response(self, response: Any, status_code: int) -> None:
        """Salva response para idempotência."""
        if self.key and not self.cached_response:
            save_idempotency(
                self.db,
                self.key,
                self.endpoint,
                self.payload,
                response,
                status_code
            )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "compute_request_hash",
    "serialize_response",
    "check_idempotency",
    "save_idempotency",
    "cleanup_expired_keys",
    "IdempotencyGuard",
]
