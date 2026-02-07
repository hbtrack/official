"""
Endpoints de teste E2E - APENAS HABILITADOS EM AMBIENTE DE TESTE

REGRAS DE SEGURANÇA:
1. Só funciona quando E2E=1 no ambiente
2. Requer autenticação de superadmin ou dirigente
3. Só aceita emails com prefixo e2e. ou e2e_ (domínio de teste)
4. Retorna 404 se E2E não estiver habilitado (não revela existência)

ENDPOINTS:
- GET /api/v1/test/welcome-token?email=... - Retorna token de welcome para testes E2E
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.core.auth import get_current_user, ExecutionContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test", tags=["Test Helpers (E2E)"])

# =============================================================================
# GUARDS
# =============================================================================

def is_e2e_enabled() -> bool:
    """Verifica se modo E2E está habilitado"""
    return os.getenv("E2E", "").lower() in ("1", "true", "yes")


def validate_e2e_email(email: str) -> bool:
    """Valida que email é de teste E2E (prefixo e2e. ou e2e_)"""
    email_lower = email.lower()
    return email_lower.startswith("e2e.") or email_lower.startswith("e2e_") or email_lower.startswith("e2e-")


# =============================================================================
# SCHEMAS
# =============================================================================

class WelcomeTokenResponse(BaseModel):
    """Resposta do endpoint de welcome token para testes"""
    token: str
    user_id: str
    email: str
    expires_at: str
    
    class Config:
        from_attributes = True


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get(
    "/welcome-token",
    response_model=WelcomeTokenResponse,
    summary="[E2E ONLY] Obter token de welcome para teste",
    description="""
    Endpoint exclusivo para testes E2E. Retorna o token de welcome mais recente
    para um email de teste.
    
    **REQUISITOS:**
    - Ambiente deve ter E2E=1
    - Usuário deve estar autenticado (qualquer role com org membership)
    - Email deve começar com e2e. ou e2e_ ou e2e-
    
    **RETORNA 404 se E2E não estiver habilitado (segurança)**
    """,
)
def get_welcome_token(
    email: str = Query(..., description="Email do convite (deve começar com e2e.)"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(get_current_user),
) -> WelcomeTokenResponse:
    """
    Retorna token de welcome para testes E2E.
    
    Só funciona quando E2E=1 está configurado no ambiente.
    """
    
    # Guard 1: E2E deve estar habilitado
    if not is_e2e_enabled():
        # Retornar 404 para não revelar existência do endpoint
        logger.warning(f"Tentativa de acesso a endpoint de teste sem E2E=1 | user={ctx.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    
    # Guard 2: Validar email é de teste
    if not validate_e2e_email(email):
        logger.warning(f"Email não é de teste E2E | email={email} | user={ctx.user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TEST_EMAIL",
                "message": "Email deve começar com e2e. ou e2e_ ou e2e- para uso em testes"
            }
        )
    
    # Buscar usuário pelo email
    target_user = db.query(User).filter(
        User.email.ilike(email),
        User.deleted_at.is_(None)
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": f"Usuário com email {email} não encontrado"
            }
        )
    
    # Buscar token de welcome mais recente válido/pendente
    password_reset = db.query(PasswordReset).filter(
        PasswordReset.user_id == target_user.id,
        PasswordReset.token_type == "welcome",
        PasswordReset.used == False,
        PasswordReset.deleted_at.is_(None),
    ).order_by(desc(PasswordReset.created_at)).first()
    
    if not password_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TOKEN_NOT_FOUND",
                "message": f"Nenhum token de welcome pendente para {email}"
            }
        )
    
    logger.info(f"[E2E] Welcome token recuperado | email={email} | requester={ctx.user_id}")
    
    return WelcomeTokenResponse(
        token=password_reset.token,
        user_id=str(target_user.id),
        email=target_user.email,
        expires_at=password_reset.expires_at.isoformat(),
    )


@router.get(
    "/health",
    summary="[E2E ONLY] Health check do módulo de teste",
    description="Verifica se o módulo de teste está habilitado",
)
def test_health():
    """Health check do módulo de testes E2E"""
    if not is_e2e_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    
    return {
        "status": "ok",
        "e2e_enabled": True,
        "message": "Test helpers module is active"
    }
