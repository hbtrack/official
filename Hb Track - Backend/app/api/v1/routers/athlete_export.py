"""
Athlete Data Export Router - Step 24 (LGPD Compliance)

Endpoint para exportação de dados pessoais do atleta conforme LGPD Art. 18.

Rota: GET /athletes/me/export-data?format=json|csv

Features:
- Autenticação obrigatória (JWT)
- Validação de ownership (apenas próprios dados)
- Formatos JSON (direto) e CSV (ZIP download)
- Rate limiting futuro (opcional)
- Registra em audit_logs
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.athlete_data_export_service import AthleteDataExportService
from app.core.exceptions import BadRequestException

router = APIRouter(prefix="/athletes", tags=["athletes-export"])


@router.get(
    "/me/export-data",
    summary="Exportar Dados Pessoais (LGPD)",
    description="""
    Exporta todos os dados pessoais do atleta conforme LGPD Art. 18.
    
    **Formatos disponíveis:**
    - `json`: Retorna JSON direto no response
    - `csv`: Retorna ZIP com múltiplos CSVs (download)
    
    **Dados incluídos:**
    - Informações pessoais (nome, data nascimento, posição, etc)
    - Wellness pré-treino (todas entradas)
    - Wellness pós-treino (todas entradas)
    - Presenças em treinos
    - Histórico médico (casos registrados)
    - Badges conquistados
    
    **NÃO inclui:**
    - Logs de acesso (data_access_logs)
    - Dados de outros atletas
    - Informações de equipes/organizações
    
    **Segurança:**
    - Apenas o próprio atleta pode exportar seus dados
    - Registra exportação em audit_logs
    - Rate limiting futuro: 3 exports/dia
    
    **Compliance:**
    - LGPD Art. 18, II - Direito à portabilidade
    - Dados em formato estruturado (JSON/CSV)
    - Gerado em até 5 segundos
    """,
    responses={
        200: {
            "description": "Dados exportados com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "format": "json",
                        "data": {
                            "personal_info": {},
                            "wellness_pre_history": [],
                            "wellness_post_history": [],
                            "attendance_history": [],
                            "medical_cases": [],
                            "badges": []
                        },
                        "generated_at": "2026-01-17T23:45:00",
                        "total_records": 1234
                    }
                },
                "application/zip": {
                    "example": "Binary ZIP file with CSVs"
                }
            }
        },
        400: {"description": "Formato inválido ou usuário não é atleta"},
        401: {"description": "Não autenticado"},
        404: {"description": "Atleta não encontrado"}
    }
)
async def export_athlete_data(
    request: Request,
    format: str = Query(
        "json",
        description="Formato do export: 'json' ou 'csv'",
        pattern="^(json|csv)$"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Exporta dados pessoais do atleta logado
    
    LGPD Compliance:
    - Apenas próprios dados
    - NÃO inclui data_access_logs
    - Registra em audit_logs
    """
    
    # 1. Validar que usuário é atleta
    if not current_user.athlete_id:
        raise BadRequestException(
            "Usuário não é um atleta. Apenas atletas podem exportar dados pessoais."
        )
    
    # 2. Criar service
    export_service = AthleteDataExportService(db)
    
    # 3. Exportar dados
    result = await export_service.export_athlete_data(
        user_id=current_user.id,
        athlete_id=current_user.athlete_id,
        export_format=format,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # 4. Retornar no formato apropriado
    if format == "json":
        # JSON direto
        return JSONResponse(
            content={
                "format": result["format"],
                "data": result["data"],
                "file_name": result["file_name"],
                "generated_at": result["generated_at"],
                "total_records": result["total_records"]
            },
            headers={
                "X-Total-Records": str(result["total_records"]),
                "X-LGPD-Compliance": "Art.18-II"
            }
        )
    
    else:  # CSV (ZIP)
        # Download de arquivo
        return Response(
            content=result["file_content"],
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{result["file_name"]}"',
                "X-Total-Records": str(result["total_records"]),
                "X-LGPD-Compliance": "Art.18-II"
            }
        )
