"""
Export Router - Step 23

REST API endpoints para exports PDF e LGPD data exports.

Endpoints:
- POST /analytics/export-pdf - Solicita export PDF analytics
- GET /analytics/exports/{id} - Consulta status de export job
- GET /analytics/exports - Lista exports do usuário
- GET /athletes/me/export-data - Export dados LGPD (Step 24)
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_db
from app.core.context import get_current_context as get_current_active_user
from app.core.context import ExecutionContext
from app.schemas.exports import (
    AnalyticsPDFExportRequest,
    ExportJobListResponse,
    ExportJobResponse,
    ExportRateLimitResponse,
)
from app.services.export_service import ExportService

router = APIRouter()


@router.post(
    "/analytics/export-pdf",
    response_model=ExportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicita export PDF analytics",
    description="""
    Cria job assíncrono para gerar PDF com analytics do team.
    
    **Rate Limit**: 5 exports/dia por usuário
    
    **Fluxo**:
    1. Valida rate limit (retorna 429 se excedido)
    2. Calcula hash dos params (cache)
    3. Verifica se export idêntico já existe e é válido
    4. Se cached: retorna job existente (não conta no rate limit)
    5. Se novo: cria job, incrementa contador, dispara Celery task
    
    **Polling**: Cliente deve fazer GET /analytics/exports/{id} a cada 2s
    para verificar status (pending → processing → completed/failed)
    
    **Cache**: Export idêntico é reutilizado se ainda válido (<7 dias)
    """,
)
async def request_analytics_pdf_export(
    request: AnalyticsPDFExportRequest,
    current_user: Annotated[ExecutionContext, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_async_db),
) -> ExportJobResponse:
    """
    Solicita export PDF analytics (assíncrono)
    """
    # DEC-TRAIN-004: estado degradado quando Celery worker não ativo (proibido polling fake)
    try:
        from app.core.celery_app import app as _celery_app
        inspector = _celery_app.control.inspect(timeout=1.0)
        active = inspector.active()
        if not active:  # None ou dict vazio = sem workers ativos
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unavailable",
                    "reason": "worker_not_active",
                    "message": "Export service is temporarily unavailable. Celery worker is not running.",
                },
            )
    except HTTPException:
        raise
    except Exception:
        # Falha na conexão com broker = worker não disponível
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unavailable",
                "reason": "worker_not_active",
                "message": "Export service is temporarily unavailable. Celery worker is not running.",
            },
        )

    try:
        service = ExportService(db)
        
        # Create export job
        job = await service.create_export_job(
            user_id=current_user.user_id,
            export_type='analytics_pdf',
            params={
                'team_id': str(request.team_id),
                'start_date': request.start_date.isoformat(),
                'end_date': request.end_date.isoformat(),
                'include_wellness': request.include_wellness,
                'include_badges': request.include_badges,
                'include_prevention': request.include_prevention,
            }
        )
        
        return ExportJobResponse.model_validate(job)
        
    except Exception as e:
        if "limit exceeded" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create export job: {str(e)}"
        )


@router.get(
    "/analytics/exports/{job_id}",
    response_model=ExportJobResponse,
    summary="Consulta status de export job",
    description="""
    Retorna status atual do job de export.
    
    **Status possíveis**:
    - `pending`: Na fila (Celery worker irá processar)
    - `processing`: Sendo gerado neste momento
    - `completed`: Pronto para download (file_url disponível)
    - `failed`: Erro durante geração (error_message disponível)
    
    **Polling**: Recomendado fazer GET a cada 2-3 segundos até status != pending
    
    **Expiração**: file_url é válido por 7 dias após completed_at
    """,
)
async def get_export_job_status(
    job_id: UUID,
    current_user: Annotated[ExecutionContext, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_async_db),
) -> ExportJobResponse:
    """
    Consulta status de export job (polling)
    """
    service = ExportService(db)
    
    try:
        job = await service.get_job_status(
            job_id=job_id,
            user_id=current_user.user_id
        )
        return ExportJobResponse.model_validate(job)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/analytics/exports",
    response_model=ExportJobListResponse,
    summary="Lista exports do usuário",
    description="""
    Lista histórico de exports do usuário (paginado).
    
    Útil para:
    - Dashboard "Meus Exports"
    - Redownload de PDFs anteriores (se ainda válidos)
    - Histórico de exports com status/data
    """,
)
async def list_user_exports(
    current_user: Annotated[ExecutionContext, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1, description="Página (1-indexed)"),
    per_page: int = Query(10, ge=1, le=50, description="Itens por página"),
) -> ExportJobListResponse:
    """
    Lista exports do usuário (histórico)
    """
    service = ExportService(db)
    
    jobs, total = await service.list_user_jobs(
        user_id=current_user.user_id,
        page=page,
        per_page=per_page
    )
    
    return ExportJobListResponse(
        jobs=[ExportJobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get(
    "/analytics/export-rate-limit",
    response_model=ExportRateLimitResponse,
    summary="Verifica rate limit atual",
    description="""
    Retorna informações sobre rate limit do usuário.
    
    Útil para:
    - Exibir no frontend: "Você pode exportar mais X vezes hoje"
    - Prevenir tentativas de export quando limite atingido
    - Mostrar quando limite reseta (meia-noite)
    """,
)
async def check_export_rate_limit(
    current_user: Annotated[ExecutionContext, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_async_db),
    export_type: str = Query("analytics_pdf", description="Tipo de export"),
) -> ExportRateLimitResponse:
    """
    Verifica rate limit atual do usuário
    """
    service = ExportService(db)
    
    try:
        return await service.check_rate_limit(
            user_id=current_user.user_id,
            export_type=export_type
        )
    except Exception as e:
        if "limit exceeded" in str(e).lower():
            # Retorna 200 com remaining=0 ao invés de 429
            from datetime import datetime, timedelta, date
            tomorrow = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
            return ExportRateLimitResponse(
                export_type=export_type,
                remaining_today=0,
                total_limit=5,
                resets_at=tomorrow
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
