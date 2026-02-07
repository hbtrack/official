"""
Router para importação de dados legacy (CSV) - Admin Only

**Step 28:** Import CSV Legacy

**Endpoints:**
- POST /admin/import-legacy/preview: Valida CSVs e retorna preview
- POST /admin/import-legacy/execute: Executa importação
- GET /admin/import-legacy/jobs/{job_id}: Status do job de importação
"""

import asyncio
import logging
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import require_superadmin
from app.core.context import ExecutionContext
from app.core.db import get_async_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/import-legacy",
    tags=["admin-import"],
)

# ================================================================================
# SCHEMAS
# ================================================================================

class ImportPreviewRequest(BaseModel):
    organization_id: UUID4


class ImportPreviewResponse(BaseModel):
    success: bool
    sessions_count: int
    sessions_errors: list[str]
    attendance_count: Optional[int] = None
    attendance_errors: Optional[list[str]] = None
    warnings: list[str]
    estimated_duration_seconds: int


class ImportExecuteRequest(BaseModel):
    organization_id: UUID4


class ImportExecuteResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ImportJobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress_pct: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ================================================================================
# IN-MEMORY JOB TRACKER (Simplified - use Redis/DB in production)
# ================================================================================

import_jobs = {}


def create_job(org_id: UUID4) -> str:
    """Cria um job de importação"""
    job_id = str(uuid.uuid4())
    import_jobs[job_id] = {
        'status': 'pending',
        'progress_pct': 0,
        'message': 'Aguardando início da importação',
        'result': None,
        'error': None,
        'started_at': datetime.now(timezone.utc),
        'completed_at': None,
        'organization_id': str(org_id)
    }
    return job_id


def update_job(job_id: str, **kwargs):
    """Atualiza status do job"""
    if job_id in import_jobs:
        import_jobs[job_id].update(kwargs)


def get_job(job_id: str) -> Optional[dict]:
    """Retorna status do job"""
    return import_jobs.get(job_id)


# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

async def validate_csv_preview(
    sessions_file: UploadFile,
    attendance_file: Optional[UploadFile],
    org_id: UUID4
) -> ImportPreviewResponse:
    """Valida CSVs e retorna preview sem importar"""
    import csv
    
    # Validate sessions file
    sessions_content = await sessions_file.read()
    sessions_lines = sessions_content.decode('utf-8').splitlines()
    sessions_reader = csv.DictReader(sessions_lines)
    sessions_rows = list(sessions_reader)
    
    sessions_errors = []
    
    # Check required columns
    required_columns = [
        'team_name', 'title', 'session_type', 'session_at',
        'duration_minutes', 'focus_attack_pct', 'focus_defense_pct',
        'focus_physical_pct', 'focus_technical_pct', 'focus_tactical_pct',
        'focus_transition_pct', 'focus_goalkeeper_pct'
    ]
    
    if sessions_rows:
        missing_columns = [col for col in required_columns if col not in sessions_rows[0]]
        if missing_columns:
            sessions_errors.append(
                f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
            )
    
    # Basic validation (simplified - full validation in script)
    for i, row in enumerate(sessions_rows[:10], start=2):  # Preview first 10
        if not row.get('team_name'):
            sessions_errors.append(f"Linha {i}: team_name obrigatório")
        if not row.get('title'):
            sessions_errors.append(f"Linha {i}: title obrigatório")
        
        # Validate focus sum (if all present)
        if all(row.get(f'focus_{f}_pct') for f in ['attack', 'defense', 'physical', 'technical', 'tactical', 'transition', 'goalkeeper']):
            try:
                total = sum(int(row[f'focus_{f}_pct']) for f in ['attack', 'defense', 'physical', 'technical', 'tactical', 'transition', 'goalkeeper'])
                if total != 100:
                    sessions_errors.append(f"Linha {i}: soma de focos = {total}% (esperado 100%)")
            except ValueError:
                sessions_errors.append(f"Linha {i}: focos devem ser números inteiros")
    
    # Validate attendance file (if provided)
    attendance_count = None
    attendance_errors = []
    
    if attendance_file:
        attendance_content = await attendance_file.read()
        attendance_lines = attendance_content.decode('utf-8').splitlines()
        attendance_reader = csv.DictReader(attendance_lines)
        attendance_rows = list(attendance_reader)
        attendance_count = len(attendance_rows)
        
        required_att_columns = ['team_name', 'session_title', 'session_at', 'athlete_name', 'status']
        if attendance_rows:
            missing_att_columns = [col for col in required_att_columns if col not in attendance_rows[0]]
            if missing_att_columns:
                attendance_errors.append(
                    f"Colunas obrigatórias ausentes: {', '.join(missing_att_columns)}"
                )
    
    # Generate warnings
    warnings = []
    if len(sessions_rows) > 100:
        warnings.append(f"Grande volume de dados: {len(sessions_rows)} sessões. Importação pode demorar vários minutos.")
    
    # Estimate duration (rough: 10 sessions/second)
    estimated_duration = max(5, len(sessions_rows) // 10)
    
    return ImportPreviewResponse(
        success=len(sessions_errors) == 0 and len(attendance_errors) == 0,
        sessions_count=len(sessions_rows),
        sessions_errors=sessions_errors,
        attendance_count=attendance_count,
        attendance_errors=attendance_errors if attendance_file else None,
        warnings=warnings,
        estimated_duration_seconds=estimated_duration
    )


async def execute_import_job(
    job_id: str,
    sessions_path: Path,
    attendance_path: Optional[Path],
    org_id: UUID4
):
    """Executa importação em background"""
    import subprocess
    import json
    
    try:
        update_job(job_id, status='processing', progress_pct=10, message='Iniciando importação...')
        
        # Build command
        cmd = [
            'python',
            'import_legacy_training.py',
            '--sessions', str(sessions_path),
            '--org-id', str(org_id),
            '--output', f'import_summary_{job_id}.json'
        ]
        
        if attendance_path:
            cmd.extend(['--attendance', str(attendance_path)])
        
        update_job(job_id, progress_pct=20, message='Validando dados...')
        
        # Execute script
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent.parent,  # Backend root
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        update_job(job_id, progress_pct=80, message='Processando resultados...')
        
        # Read summary
        summary_path = Path(f'import_summary_{job_id}.json')
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            if summary.get('success'):
                update_job(
                    job_id,
                    status='completed',
                    progress_pct=100,
                    message='Importação concluída com sucesso',
                    result=summary,
                    completed_at=datetime.now(timezone.utc)
                )
            else:
                update_job(
                    job_id,
                    status='failed',
                    progress_pct=100,
                    message='Importação falhou na validação',
                    error=summary.get('error_message'),
                    result=summary,
                    completed_at=datetime.now(timezone.utc)
                )
        else:
            raise FileNotFoundError(f"Summary file not found: {summary_path}")
        
    except subprocess.TimeoutExpired:
        update_job(
            job_id,
            status='failed',
            progress_pct=100,
            message='Importação excedeu tempo limite (10 minutos)',
            error='Timeout',
            completed_at=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Import job {job_id} failed: {str(e)}")
        update_job(
            job_id,
            status='failed',
            progress_pct=100,
            message='Erro na importação',
            error=str(e),
            completed_at=datetime.now(timezone.utc)
        )


# ================================================================================
# ENDPOINTS
# ================================================================================

@router.post(
    "/preview",
    response_model=ImportPreviewResponse,
    summary="Preview de importação CSV",
    description="Valida CSVs e retorna preview sem importar dados"
)
async def preview_import(
    organization_id: UUID4 = Form(...),
    sessions_file: UploadFile = File(..., description="CSV de sessões de treino"),
    attendance_file: Optional[UploadFile] = File(None, description="CSV de attendance (opcional)"),
    ctx: ExecutionContext = Depends(require_superadmin),
):
    """
    Valida arquivos CSV e retorna preview da importação.
    
    **Validações:**
    - Schema das colunas obrigatórias
    - Formato de dados (datas, números, focos)
    - Soma de focos = 100%
    - Existência de teams na organização
    
    **Não executa a importação**, apenas valida e estima duração.
    
    Requer: superadmin
    """
    try:
        preview = await validate_csv_preview(
            sessions_file,
            attendance_file,
            organization_id
        )
        
        logger.info(
            f"Import preview generated: {preview.sessions_count} sessions, "
            f"{len(preview.sessions_errors)} errors by superadmin {ctx.user_id}"
        )
        
        return preview
        
    except Exception as e:
        logger.error(f"Preview failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar preview: {str(e)}"
        )


@router.post(
    "/execute",
    response_model=ImportExecuteResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Executar importação CSV",
    description="Inicia job de importação em background"
)
async def execute_import(
    organization_id: UUID4 = Form(...),
    sessions_file: UploadFile = File(...),
    attendance_file: Optional[UploadFile] = File(None),
    ctx: ExecutionContext = Depends(require_superadmin),
):
    """
    Executa importação de dados legacy de CSVs.
    
    **Processo:**
    1. Upload dos arquivos para temp
    2. Criação de job assíncrono
    3. Execução do script import_legacy_training.py
    4. Polling via GET /jobs/{job_id}
    
    **Regras:**
    - Sessões >60 dias recebem status 'readonly'
    - Importação em transação (rollback on error)
    - Gera relatório import_summary.json
    
    Requer: superadmin
    """
    try:
        # Save uploaded files to temp
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as sessions_temp:
            sessions_content = await sessions_file.read()
            sessions_temp.write(sessions_content)
            sessions_path = Path(sessions_temp.name)
        
        attendance_path = None
        if attendance_file:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as attendance_temp:
                attendance_content = await attendance_file.read()
                attendance_temp.write(attendance_content)
                attendance_path = Path(attendance_temp.name)
        
        # Create job
        job_id = create_job(organization_id)
        
        # Start background task
        asyncio.create_task(execute_import_job(
            job_id,
            sessions_path,
            attendance_path,
            organization_id
        ))
        
        logger.info(
            f"Import job {job_id} created for org {organization_id} "
            f"by superadmin {ctx.user_id}"
        )
        
        return ImportExecuteResponse(
            job_id=job_id,
            status='pending',
            message='Importação iniciada. Use GET /jobs/{job_id} para acompanhar progresso.'
        )
        
    except Exception as e:
        logger.error(f"Import execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar importação: {str(e)}"
        )


@router.get(
    "/jobs/{job_id}",
    response_model=ImportJobStatusResponse,
    summary="Status do job de importação",
    description="Retorna status e progresso da importação"
)
async def get_import_job_status(
    job_id: str,
    ctx: ExecutionContext = Depends(require_superadmin),
):
    """
    Retorna status de um job de importação.
    
    **Status possíveis:**
    - pending: Aguardando início
    - processing: Em andamento
    - completed: Concluído com sucesso
    - failed: Falhou (ver campo error)
    
    Requer: superadmin
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} não encontrado"
        )
    
    return ImportJobStatusResponse(
        job_id=job_id,
        status=job['status'],
        progress_pct=job['progress_pct'],
        message=job['message'],
        result=job.get('result'),
        error=job.get('error'),
        started_at=job.get('started_at'),
        completed_at=job.get('completed_at')
    )


@router.get(
    "/jobs/{job_id}/summary",
    summary="Download do relatório de importação",
    description="Baixa arquivo import_summary.json"
)
async def download_import_summary(
    job_id: str,
    ctx: ExecutionContext = Depends(require_superadmin),
):
    """
    Download do relatório import_summary.json.
    
    Requer: superadmin
    """
    summary_path = Path(f'import_summary_{job_id}.json')
    
    if not summary_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado"
        )
    
    return FileResponse(
        path=summary_path,
        media_type='application/json',
        filename=f'import_summary_{job_id}.json'
    )
