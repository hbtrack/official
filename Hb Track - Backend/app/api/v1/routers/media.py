"""
Media Router - Upload de Arquivos
=================================
Endpoints para upload de mídia via Cloudinary.

FASE 4 - FICHA.MD Section 4.4

FEATURES:
- Assinatura de upload para Cloudinary
- Validação de permissões
- Suporte a múltiplos tipos de mídia (foto, documento)

Baseado em: FICHA.MD seção 4.4
"""

import hashlib
import time
import logging
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.deps import permission_dep
from app.core.context import ExecutionContext
from app.core.config import settings

logger = logging.getLogger("hb.media")

router = APIRouter(prefix="/media", tags=["Media - Upload"])


# =============================================================================
# SCHEMAS
# =============================================================================

class CloudinarySignatureResponse(BaseModel):
    """Resposta com dados para upload direto ao Cloudinary."""
    
    cloud_name: str
    api_key: str
    timestamp: int
    signature: str
    upload_preset: Optional[str] = None
    folder: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "cloud_name": "hbtrack",
                "api_key": "123456789012345",
                "timestamp": 1699999999,
                "signature": "abc123def456...",
                "upload_preset": "hbtrack_unsigned",
                "folder": "athletes/photos"
            }
        }


# =============================================================================
# ENDPOINT: SIGN UPLOAD
# =============================================================================

@router.get(
    "/sign-upload",
    response_model=CloudinarySignatureResponse,
    summary="Obter assinatura para upload Cloudinary",
    description="""
    Gera assinatura para upload direto ao Cloudinary (client-side).
    
    ## Fluxo:
    1. Frontend chama este endpoint com o tipo de mídia
    2. Backend retorna cloud_name, api_key, timestamp, signature
    3. Frontend faz upload direto ao Cloudinary
    4. Frontend envia URL resultante no payload da Ficha Única
    
    ## Tipos de mídia:
    - **photo**: Fotos de perfil (folder: athletes/photos ou persons/photos)
    - **document**: Documentos (RG, certidões) (folder: documents)
    
    ## Segurança:
    - Assinatura expira em 1 hora
    - Requer autenticação
    """
)
async def sign_upload(
    media_type: Literal["photo", "document"] = Query(
        "photo",
        description="Tipo de mídia: photo ou document"
    ),
    entity_type: Optional[str] = Query(
        "person",
        description="Tipo de entidade: person, athlete, organization"
    ),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["dirigente", "coordenador", "treinador"],
        require_org=False
    ))
) -> CloudinarySignatureResponse:
    """
    Gera assinatura para upload Cloudinary.
    
    O upload acontece client-side diretamente para o Cloudinary.
    A assinatura garante que apenas uploads autorizados são aceitos.
    """
    # Verificar configuração
    if not settings.CLOUDINARY_API_SECRET:
        logger.error("MEDIA | Cloudinary not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "CLOUDINARY_NOT_CONFIGURED",
                "message": "Serviço de upload não configurado"
            }
        )
    
    # Determinar folder
    if media_type == "photo":
        folder = f"{entity_type}s/photos"
    else:
        folder = "documents"
    
    # Timestamp (unix epoch)
    timestamp = int(time.time())
    
    # Gerar assinatura
    # Cloudinary signature = SHA1(params_to_sign + api_secret)
    params_to_sign = f"folder={folder}&timestamp={timestamp}"
    
    if settings.CLOUDINARY_UPLOAD_PRESET:
        params_to_sign += f"&upload_preset={settings.CLOUDINARY_UPLOAD_PRESET}"
    
    signature_string = params_to_sign + settings.CLOUDINARY_API_SECRET
    signature = hashlib.sha1(signature_string.encode()).hexdigest()
    
    logger.info(
        f"MEDIA | Sign upload | "
        f"type={media_type} | "
        f"entity={entity_type} | "
        f"folder={folder} | "
        f"user_id={ctx.user_id if ctx else 'anonymous'}"
    )
    
    return CloudinarySignatureResponse(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        timestamp=timestamp,
        signature=signature,
        upload_preset=settings.CLOUDINARY_UPLOAD_PRESET,
        folder=folder
    )


# =============================================================================
# ENDPOINT: VALIDATE UPLOAD URL (OPCIONAL)
# =============================================================================

@router.get(
    "/validate-url",
    summary="Validar URL de upload Cloudinary",
    description="""
    Valida se uma URL de upload é do Cloudinary e está no formato esperado.
    
    Útil para validação server-side antes de salvar a URL no banco.
    """
)
async def validate_upload_url(
    url: str = Query(..., description="URL do arquivo no Cloudinary"),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["dirigente", "coordenador", "treinador"],
        require_org=False
    ))
):
    """Valida URL de arquivo Cloudinary."""
    # Verificar se é URL Cloudinary válida
    cloudinary_domains = [
        "res.cloudinary.com",
        "cloudinary.com"
    ]
    
    is_valid = any(domain in url for domain in cloudinary_domains)
    
    if not is_valid:
        # Também aceitar URLs de preview local (desenvolvimento)
        if url.startswith("blob:") or url.startswith("data:"):
            is_valid = True
    
    # Verificar cloud_name
    if is_valid and settings.CLOUDINARY_CLOUD_NAME:
        if settings.CLOUDINARY_CLOUD_NAME not in url:
            is_valid = False
    
    return {
        "valid": is_valid,
        "url": url,
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME if is_valid else None
    }
