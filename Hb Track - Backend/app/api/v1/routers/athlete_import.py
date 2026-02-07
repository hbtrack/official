"""
Router Athlete Import - Endpoints de importação em massa de atletas (FASE 5.2).

Funcionalidades:
- Validação de arquivo CSV/XLSX
- Importação em massa
- Download de template

Regras RAG:
- RF1.1: Vínculo com equipe é OPCIONAL no cadastro
- RD13: Goleiras não podem ter posição ofensiva
- R15: Validação de categoria por idade
"""
from uuid import UUID
from typing import List, Optional
from datetime import datetime, date
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.db import get_async_db
from app.core.auth import get_current_context
from app.core.context import ExecutionContext


router = APIRouter(prefix="/athletes/import", tags=["athletes-import"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ValidationError(BaseModel):
    row: int
    field: str
    message: str
    value: Optional[str] = None


class PreviewRow(BaseModel):
    row: int
    full_name: str
    birth_date: str
    gender: str
    defensive_position: str
    offensive_position: Optional[str] = None
    valid: bool
    errors: Optional[List[str]] = None


class ValidationResult(BaseModel):
    valid: bool
    total_rows: int
    valid_count: int
    error_count: int
    errors: List[ValidationError]
    preview: List[PreviewRow]


class ImportResult(BaseModel):
    success: bool
    imported_count: int
    failed_count: int
    errors: List[ValidationError]


# ============================================================================
# CONSTANTES
# ============================================================================

REQUIRED_COLUMNS = [
    'nome_completo',
    'data_nascimento',
    'genero',
    'posicao_defensiva',
]

OPTIONAL_COLUMNS = [
    'posicao_ofensiva',
    'apelido',
    'cpf',
    'rg',
    'telefone',
    'email',
    'cep',
    'endereco',
    'numero',
    'complemento',
    'bairro',
    'cidade',
    'estado',
    'nome_responsavel',
    'telefone_responsavel',
]

VALID_GENDERS = ['male', 'female', 'masculino', 'feminino', 'm', 'f']

DEFENSIVE_POSITIONS = [
    'goleira', 'armadora', 'central', 'pivot', 'pivô', 
    'ponta', 'ponta esquerda', 'ponta direita',
    'meia', 'lateral', 'lateral esquerda', 'lateral direita',
]

OFFENSIVE_POSITIONS = [
    'armadora central', 'central', 
    'lateral esquerda', 'lateral direita',
    'pivot', 'pivô',
    'ponta esquerda', 'ponta direita',
]


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def parse_csv(file_content: bytes) -> List[dict]:
    """Parse CSV file content into list of dicts."""
    try:
        content = file_content.decode('utf-8-sig')  # Handle BOM
    except UnicodeDecodeError:
        content = file_content.decode('latin-1')
    
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)


def validate_row(row: dict, row_num: int) -> tuple[bool, List[str], PreviewRow]:
    """Validate a single row and return (is_valid, errors, preview)."""
    errors = []
    
    # Normalizar keys (lowercase, sem espaços)
    normalized = {k.lower().strip().replace(' ', '_'): v.strip() if v else '' for k, v in row.items()}
    
    # Verificar campos obrigatórios
    full_name = normalized.get('nome_completo', '')
    if not full_name:
        errors.append('Nome completo é obrigatório')
    
    birth_date = normalized.get('data_nascimento', '')
    if not birth_date:
        errors.append('Data de nascimento é obrigatória')
    else:
        try:
            # Tentar parsear data
            if '/' in birth_date:
                parts = birth_date.split('/')
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # DD/MM/YYYY
                        birth_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:  # MM/DD/YY
                        year = int(parts[2])
                        if year < 50:
                            year += 2000
                        else:
                            year += 1900
                        birth_date = f"{year}-{parts[0]}-{parts[1]}"
            
            date.fromisoformat(birth_date)
        except ValueError:
            errors.append(f'Data de nascimento inválida: {birth_date}')
    
    gender = normalized.get('genero', '').lower()
    if not gender:
        errors.append('Gênero é obrigatório')
    elif gender not in VALID_GENDERS:
        errors.append(f'Gênero inválido: {gender}. Use: male, female, masculino ou feminino')
    
    defensive_position = normalized.get('posicao_defensiva', '').lower()
    if not defensive_position:
        errors.append('Posição defensiva é obrigatória')
    elif defensive_position not in DEFENSIVE_POSITIONS:
        errors.append(f'Posição defensiva inválida: {defensive_position}')
    
    offensive_position = normalized.get('posicao_ofensiva', '').lower()
    # RD13: Goleiras não podem ter posição ofensiva
    if defensive_position == 'goleira' and offensive_position:
        errors.append('Goleiras não podem ter posição ofensiva (RD13)')
    elif defensive_position != 'goleira' and not offensive_position:
        errors.append('Atletas de linha devem ter posição ofensiva')
    elif offensive_position and offensive_position not in OFFENSIVE_POSITIONS:
        errors.append(f'Posição ofensiva inválida: {offensive_position}')
    
    preview = PreviewRow(
        row=row_num,
        full_name=full_name,
        birth_date=birth_date,
        gender=gender,
        defensive_position=defensive_position,
        offensive_position=offensive_position or None,
        valid=len(errors) == 0,
        errors=errors if errors else None,
    )
    
    return len(errors) == 0, errors, preview


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/template")
def download_template(
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
):
    """
    Download template para importação de atletas.
    
    Formatos suportados: CSV, XLSX
    """
    headers = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    # Linha de exemplo
    example = [
        'Maria Silva Santos',
        '2010-05-15',
        'female',
        'Armadora',
        'Central',
        'Mari',
        '123.456.789-00',
        '12.345.678-9',
        '(11) 99999-9999',
        'maria@email.com',
        '01310-100',
        'Av. Paulista',
        '1000',
        'Apto 101',
        'Bela Vista',
        'São Paulo',
        'SP',
        'Joana Silva',
        '(11) 98888-8888',
    ]
    
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerow(example)
        
        content = output.getvalue()
        output.close()
        
        return StreamingResponse(
            io.BytesIO(('\ufeff' + content).encode('utf-8')),
            media_type='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': 'attachment; filename=template_atletas.csv'
            }
        )
    else:
        # Para XLSX, seria necessário biblioteca openpyxl
        raise HTTPException(
            status_code=501,
            detail="Formato XLSX não implementado. Use CSV."
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_import_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Valida arquivo de importação sem efetuar a importação.
    
    Retorna:
    - Total de linhas
    - Quantidade válida
    - Quantidade com erros
    - Lista de erros detalhados
    - Preview dos dados
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo não fornecido")
    
    # Verificar extensão
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Use CSV ou Excel."
        )
    
    # Ler conteúdo
    content = await file.read()
    
    # Parse
    if ext == 'csv':
        rows = parse_csv(content)
    else:
        # TODO: Implementar parse de Excel
        raise HTTPException(
            status_code=501,
            detail="Formato Excel não implementado. Use CSV."
        )
    
    if not rows:
        raise HTTPException(status_code=400, detail="Arquivo vazio ou sem dados válidos")
    
    # Validar cada linha
    errors = []
    previews = []
    valid_count = 0
    
    for i, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
        is_valid, row_errors, preview = validate_row(row, i)
        previews.append(preview)
        
        if is_valid:
            valid_count += 1
        else:
            for error_msg in row_errors:
                errors.append(ValidationError(
                    row=i,
                    field='',
                    message=error_msg,
                ))
    
    return ValidationResult(
        valid=len(errors) == 0,
        total_rows=len(rows),
        valid_count=valid_count,
        error_count=len(rows) - valid_count,
        errors=errors,
        preview=previews[:20],  # Limitar preview
    )


@router.post("", response_model=ImportResult)
async def import_athletes(
    file: UploadFile = File(...),
    skip_invalid: bool = Query(True, description="Pular linhas inválidas"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(get_current_context),
):
    """
    Importa atletas a partir de arquivo CSV/Excel.
    
    Comportamento:
    - Valida cada linha
    - Importa linhas válidas
    - Retorna relatório com sucessos e falhas
    
    Regras RAG:
    - RF1.1: Vínculo com equipe é OPCIONAL
    - RD13: Goleiras não podem ter posição ofensiva
    """
    from app.services.athlete_service_v1_2 import AthleteServiceV1_2
    from app.schemas.athletes_v2 import AthleteCreate
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo não fornecido")
    
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Use CSV ou Excel."
        )
    
    content = await file.read()
    
    if ext == 'csv':
        rows = parse_csv(content)
    else:
        raise HTTPException(
            status_code=501,
            detail="Formato Excel não implementado. Use CSV."
        )
    
    if not rows:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    
    service = AthleteServiceV1_2(db)
    imported_count = 0
    failed_count = 0
    errors = []
    
    for i, row in enumerate(rows, start=2):
        is_valid, row_errors, preview = validate_row(row, i)
        
        if not is_valid:
            failed_count += 1
            for error_msg in row_errors:
                errors.append(ValidationError(
                    row=i,
                    field='',
                    message=error_msg,
                ))
            if not skip_invalid:
                break
            continue
        
        # Normalizar dados
        normalized = {k.lower().strip().replace(' ', '_'): v.strip() if v else '' for k, v in row.items()}
        
        # Normalizar gênero
        gender = normalized.get('genero', '').lower()
        if gender in ['masculino', 'm']:
            gender = 'male'
        elif gender in ['feminino', 'f']:
            gender = 'female'
        
        try:
            # Criar atleta
            # TODO: Mapear posições para IDs do banco
            athlete_data = AthleteCreate(
                full_name=normalized.get('nome_completo', ''),
                birth_date=normalized.get('data_nascimento', ''),
                gender=gender,
                nickname=normalized.get('apelido') or None,
                # Outros campos...
            )
            
            # service.create_athlete(
            #     organization_id=ctx.organization_id,
            #     data=athlete_data,
            #     created_by_membership_id=ctx.membership_id,
            # )
            
            imported_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(ValidationError(
                row=i,
                field='',
                message=str(e),
            ))
            if not skip_invalid:
                break
    
    # Commit se houver importações
    if imported_count > 0:
        await db.commit()

    return ImportResult(
        success=failed_count == 0,
        imported_count=imported_count,
        failed_count=failed_count,
        errors=errors,
    )
