"""
Serviço Cloudinary - Upload de Fotos
FASE 3 - Integrações
"""
import logging
import os
import hashlib
import time
from typing import Dict, Any
from uuid import UUID

logger = logging.getLogger("hb.cloudinary")

# Configurações do Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "di5qmyhsx")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET", "hb_profile_photo")


def generate_signature(person_id: UUID) -> Dict[str, Any]:
    """
    Gera assinatura para upload direto ao Cloudinary.
    
    Args:
        person_id: ID da pessoa para organização de pastas
    
    Returns:
        Dict com signature, timestamp, public_id, folder
    """
    if not CLOUDINARY_API_SECRET:
        logger.error("CLOUDINARY_API_SECRET not configured")
        raise ValueError("Cloudinary API secret not configured")
    
    timestamp = int(time.time())
    folder = f"hbtrack/profiles/{person_id}"
    public_id = f"{person_id}_{timestamp}"
    
    # Parâmetros para assinar
    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
        "public_id": public_id,
        "upload_preset": CLOUDINARY_UPLOAD_PRESET
    }
    
    # Gera string para assinatura (ordem alfabética)
    params_string = "&".join([f"{k}={v}" for k, v in sorted(params_to_sign.items())])
    signature_string = f"{params_string}{CLOUDINARY_API_SECRET}"
    
    # Hash SHA-256
    signature = hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
    
    logger.info(f"Cloudinary signature generated | person_id={person_id} | timestamp={timestamp}")
    
    return {
        "signature": signature,
        "timestamp": timestamp,
        "public_id": public_id,
        "folder": folder,
        "cloud_name": CLOUDINARY_CLOUD_NAME,
        "api_key": CLOUDINARY_API_KEY,
        "upload_preset": CLOUDINARY_UPLOAD_PRESET
    }


def get_delivery_url(public_id: str, transformation: str = "t_profile_avatar") -> str:
    """
    Gera URL de entrega do Cloudinary com transformação.
    
    Args:
        public_id: Public ID do arquivo no Cloudinary
        transformation: Nome da transformação (t_profile_avatar)
    
    Returns:
        URL completa de entrega
    """
    base_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"
    return f"{base_url}/{transformation}/{public_id}"
