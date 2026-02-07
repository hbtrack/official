"""
Ficha Única de Cadastro - Router
================================
Endpoint unificado para cadastro de Pessoa com opcionais.

FASE 4 - FICHA.MD

FEATURES:
- Transação atômica
- Dry-run com ?validate_only=true
- Idempotency-Key header para evitar duplicação
- Logs estruturados
- Autorização via permission_dep e validate_ficha_scope
- Autocomplete de organizações e equipes
- Rate limiting (10 cadastros/minuto por IP)
- Fila de emails assíncrona com retry

Baseado em: Ficha unica de cadastro.txt, REGRAS.md, REGRAS_GERENCIAMENTO_ATLETAS.md
"""

import logging
import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from app.core.deps import permission_dep
from app.core.context import ExecutionContext
from app.core.db import get_async_db
from app.core.permissions import require_org_scope
from app.core.rate_limit import limiter
from app.models.organization import Organization
from app.models.membership import OrgMembership
from app.models.team import Team
from app.schemas.intake.ficha_unica import (
    FichaUnicaRequest,
    FichaUnicaResponse,
    FichaUnicaDryRunResponse,
    ValidationResult,
    OrganizationAutocompleteResponse,
    OrganizationAutocompleteItem,
    TeamAutocompleteResponse,
    TeamAutocompleteItem,
)
from app.services.intake.ficha_unica_service import FichaUnicaService
from app.services.intake.idempotency import (
    check_idempotency,
    save_idempotency,
)
from app.services.intake.validators import validate_ficha_scope
from app.services.email_queue_service import enqueue_email

logger = logging.getLogger("hb.intake")

router = APIRouter(prefix="/intake", tags=["Intake - Ficha Única"])


# =============================================================================
# ENDPOINT PRINCIPAL: FICHA ÚNICA
# =============================================================================

@router.post(
    "/ficha-unica",
    response_model=FichaUnicaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro via Ficha Única",
    description="""
    Cadastro unificado de Pessoa com opcionais:
    
    - **Pessoa** (obrigatório): dados pessoais, contatos, documentos, endereço
    - **Usuário** (opcional): cria login e envia email de ativação
    - **Organização** (opcional): criar nova ou selecionar existente
    - **Equipe** (opcional): criar nova ou selecionar existente
    - **Atleta** (opcional): dados esportivos
    - **Vínculos** (opcional): org_membership, team_registration
    
    ## Features
    
    - **Dry-run**: `?validate_only=true` para validar sem gravar
    - **Idempotência**: Header `Idempotency-Key` evita duplicação em retry
    - **Transação atômica**: tudo ou nada
    - **Rate limiting**: 10 cadastros/minuto por IP
    - **Email assíncrono**: Não bloqueia resposta, retry automático
    
    ## Permissões
    
    - Superadmin: acesso total
    - Dirigente: todos os tipos de cadastro
    - Coordenador: todos exceto criar organização
    - Treinador: apenas atletas
    
    ## Validações (R15, RD13, etc)
    
    - CPF/RG únicos
    - Email único
    - Categoria vs idade (R15)
    - Gênero compatível com equipe
    - Goleira sem posição ofensiva (RD13)
    """
)
@limiter.limit("10/minute")
async def create_ficha_unica(
    request: Request,  # Para rate limiting
    payload: FichaUnicaRequest,
    validate_only: bool = Query(
        False,
        description="Se True, apenas valida sem gravar no banco"
    ),
    idempotency_key: Optional[str] = Header(
        None,
        alias="Idempotency-Key",
        description="Chave única para evitar duplicação em retry"
    ),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False  # Pode criar sem org (atleta em captação)
    )),
    db: AsyncSession = Depends(get_async_db)
) -> FichaUnicaResponse:
    """
    Processa cadastro via Ficha Única com suporte a idempotência.
    """
    start_time = time.time()
    endpoint = "/api/v1/intake/ficha-unica"
    
    # 1. Verificar idempotência (se key fornecida e não é dry-run)
    if idempotency_key and not validate_only:
        try:
            payload_dict = payload.model_dump(mode='json')
            cached = check_idempotency(db, idempotency_key, endpoint, payload_dict)
            if cached:
                logger.info(
                    f"INTAKE | Idempotency hit | key={idempotency_key[:16]}..."
                )
                # Reconstruir response do cache
                return FichaUnicaResponse(**cached["response"])
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"INTAKE | Idempotency check failed: {e}")
    
    # 2. Validar autorização e escopo (FASE 4)
    validate_ficha_scope(payload, ctx, db)
    
    # 3. Processar
    actor_id = ctx.user_id if ctx else None
    service = FichaUnicaService(db, actor_id=actor_id)
    
    response = service.process(payload, validate_only=validate_only)
    
    # 4. Log de observabilidade
    elapsed = (time.time() - start_time) * 1000
    logger.info(
        f"INTAKE | {'VALIDATE' if validate_only else 'PROCESS'} | "
        f"success={response.success} | "
        f"person_id={response.person_id} | "
        f"user_created={response.user_created} | "
        f"athlete_created={response.athlete_created} | "
        f"elapsed_ms={elapsed:.2f}"
    )
    
    # 5. Salvar idempotência (se sucesso e não dry-run)
    if idempotency_key and response.success and not validate_only:
        try:
            payload_dict = payload.model_dump(mode='json')
            save_idempotency(
                db,
                idempotency_key,
                endpoint,
                payload_dict,
                response,
                201
            )
        except Exception as e:
            logger.warning(f"INTAKE | Idempotency save failed: {e}")
    
    # 6. Enfileirar email de ativação (assíncrono, não bloqueia resposta)
    if response.success and not validate_only and payload.create_user and payload.user and response.user_id:
        import os
        import secrets
        import hashlib
        from datetime import timedelta
        from app.models.person import Person
        from app.models.organization import Organization
        from app.models.role import Role
        from app.models.password_reset import PasswordReset
        
        try:
            # Buscar dados da pessoa
            person = db.query(Person).filter(Person.id == response.person_id).first()
            if person:
                # Buscar nome da organização (se houver)
                organization_name = None
                if response.organization_id:
                    org = db.query(Organization).filter(
                        Organization.id == response.organization_id
                    ).first()
                    if org:
                        organization_name = org.name
                
                # Buscar nome do papel
                role_name = None
                role = db.query(Role).filter(Role.id == payload.user.role_id).first()
                if role:
                    role_name = role.name
                
                # Criar token seguro (single-use, 24h expiry)
                from datetime import datetime, timezone
                token = secrets.token_urlsafe(32)  # 32 bytes = 256 bits
                token_hash = hashlib.sha256(token.encode()).hexdigest()  # Hash SHA-256
                expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24h
                
                # Salvar registro de reset com hash
                reset_record = PasswordReset(
                    user_id=response.user_id,
                    token_hash=token_hash,  # ARMAZENADO COM HASH
                    token_type='welcome',
                    expires_at=expires_at,
                    used=False,  # Single-use
                    created_at=datetime.now(timezone.utc)
                )
                
                db.add(reset_record)
                await db.commit()
                
                logger.info(
                    f"Password reset token created | user_id={response.user_id} | "
                    f"expires_in=24h | type=welcome"
                )
                
                # ENFILEIRAR EMAIL (não bloqueia)
                app_url = os.getenv("APP_PUBLIC_URL", "https://app.hbtrack.app")
                await enqueue_email(
                    db=db,
                    template_type='invite',
                    to_email=payload.user.email,
                    template_data={
                        'person_name': person.full_name,
                        'organization_name': organization_name,
                        'role_name': role_name,
                        'token': token,  # Token em texto puro SÓ NO EMAIL
                        'app_url': app_url,
                        'activation_link': f"{app_url}/set-password?token={token}",
                        'cta_text': 'Criar senha',
                        'cta_link': f"{app_url}/set-password?token={token}",
                        'app_name': 'HB Track'
                    },
                    created_by_user_id=ctx.user_id if ctx else None
                )
                
                logger.info(
                    f"Invite email enqueued | to={payload.user.email} | "
                    f"person={person.full_name} | org={organization_name or 'N/A'} | "
                    f"role={role_name or 'N/A'}"
                )
        except Exception as e:
            # Não falhar o cadastro se email falhar
            logger.exception(f"Error enqueuing email: {str(e)}")
    
    # 7. HTTP status
    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": response.message,
                "errors": response.validation_errors
            }
        )
    
    return response


# =============================================================================
# ENDPOINT: VALIDAÇÃO (DRY-RUN)
# =============================================================================

@router.post(
    "/ficha-unica/validate",
    response_model=ValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validar Ficha Única (dry-run)",
    description="""
    Valida o payload da Ficha Única sem gravar no banco.
    
    Útil para validação em tempo real no frontend (UX).
    
    Retorna:
    - Erros de unicidade (CPF, RG, email)
    - Erros de regras de negócio (R15, RD13)
    - Warnings (avisos não bloqueantes)
    """
)
async def validate_ficha_unica(
    request: FichaUnicaRequest,
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: AsyncSession = Depends(get_async_db)
) -> ValidationResult:
    """Valida payload sem gravar."""
    actor_id = ctx.user_id if ctx else None
    service = FichaUnicaService(db, actor_id=actor_id)
    return service.validate(request)


@router.post(
    "/ficha-unica/dry-run",
    response_model=FichaUnicaDryRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview da Ficha Única (dry-run)",
    description="""
    Valida e retorna preview do que seria criado.
    
    Inclui:
    - Resultado da validação
    - Preview das entidades que seriam criadas
    - Warnings sobre regras de negócio
    """
)
async def dry_run_ficha_unica(
    request: FichaUnicaRequest,
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: AsyncSession = Depends(get_async_db)
) -> FichaUnicaDryRunResponse:
    """Valida e retorna preview."""
    actor_id = ctx.user_id if ctx else None
    service = FichaUnicaService(db, actor_id=actor_id)
    return service.dry_run(request)


# =============================================================================
# ENDPOINT: AUTOCOMPLETE ORGANIZAÇÕES
# =============================================================================

@router.get(
    "/organizations/autocomplete",
    response_model=OrganizationAutocompleteResponse,
    summary="Buscar Organizações (Autocomplete)",
    description="""
    Retorna organizações filtradas por escopo do usuário.
    
    - Superadmin: vê todas as organizações
    - Outros papéis: apenas organizações com membership ativo
    """
)
async def autocomplete_organizations(
    q: str = Query(..., min_length=2, description="Termo de busca (mínimo 2 caracteres)"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: AsyncSession = Depends(get_async_db)
) -> OrganizationAutocompleteResponse:
    """
    Autocomplete de organizações com filtro de escopo.
    """
    # Base query
    query = db.query(Organization).filter(
        and_(
            Organization.deleted_at.is_(None),
            Organization.name.ilike(f"%{q}%")
        )
    )
    
    # Superadmin vê todas
    if ctx and not ctx.is_superadmin:
        # Outros papéis: apenas organizações com membership ativo
        query = query.join(
            OrgMembership,
            and_(
                OrgMembership.organization_id == Organization.id,
                OrgMembership.person_id == ctx.person_id,
                OrgMembership.deleted_at.is_(None)
            )
        )
    
    orgs = query.limit(limit).all()
    
    items = [
        OrganizationAutocompleteItem(
            id=org.id,
            name=org.name,
            abbrev=None  # Organization model doesn't have abbrev field
        )
        for org in orgs
    ]
    
    return OrganizationAutocompleteResponse(
        items=items,
        total=len(items)
    )


# =============================================================================
# ENDPOINT: AUTOCOMPLETE TEMPORADAS (FASE 4.1)
# =============================================================================

@router.get(
    "/seasons/autocomplete",
    response_model=dict,
    summary="Buscar Temporadas (Autocomplete)",
    description="""
    Retorna temporadas disponíveis filtradas por escopo.
    
    FASE 4.1 - Season Management
    
    Parâmetros:
    - q: Termo de busca opcional (filtro por ano)
    - limit: Número máximo de resultados (default: 10)
    
    Autorização:
    - Superadmin: vê todas as temporadas
    - Dirigente/Coordenador/Treinador: vê temporadas da organização vinculada
    """
)
async def autocomplete_seasons(
    q: str = Query("", description="Termo de busca (ano ou nome)"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Autocomplete de temporadas com filtro de escopo.
    
    Retorna lista de temporadas ordenadas por ano DESC (mais recentes primeiro).
    """
    from app.models.season import Season
    
    # Base query: apenas temporadas ativas (não deletadas)
    query = db.query(Season).filter(Season.deleted_at.is_(None))
    
    # Filtrar por termo se fornecido (busca por ano)
    if q and q.isdigit():
        year = int(q)
        query = query.filter(Season.year == year)
    
    # Ordenar por ano DESC (mais recentes primeiro)
    query = query.order_by(Season.year.desc())
    
    seasons = query.limit(limit).all()
    
    items = [
        {
            "id": str(season.id),
            "year": season.year,
            "name": f"Temporada {season.year}",
            "start_date": season.start_date.isoformat(),
            "end_date": season.end_date.isoformat(),
            "is_active": season.is_active
        }
        for season in seasons
    ]
    
    return {
        "items": items,
        "total": len(items)
    }


# =============================================================================
# ENDPOINT: AUTOCOMPLETE EQUIPES
# =============================================================================

@router.get(
    "/teams/autocomplete",
    response_model=TeamAutocompleteResponse,
    summary="Buscar Equipes (Autocomplete)",
    description="""
    Retorna equipes da organização filtradas por escopo.
    
    Parâmetros:
    - organization_id: ID da organização (obrigatório)
    - q: Termo de busca (opcional)
    """
)
async def autocomplete_teams(
    organization_id: UUID = Query(..., description="ID da organização"),
    q: str = Query("", description="Termo de busca (opcional)"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["admin", "dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: AsyncSession = Depends(get_async_db)
) -> TeamAutocompleteResponse:
    """
    Autocomplete de equipes com filtro de escopo organizacional.
    """
    # Validar escopo organizacional (não superadmin)
    if ctx and not ctx.is_superadmin:
        require_org_scope(organization_id, ctx)
    
    # Base query
    query = db.query(Team).filter(
        and_(
            Team.organization_id == organization_id,
            Team.deleted_at.is_(None)
        )
    )
    
    # Filtrar por termo se fornecido
    if q:
        query = query.filter(Team.name.ilike(f"%{q}%"))
    
    teams = query.limit(limit).all()
    
    items = [
        TeamAutocompleteItem(
            id=team.id,
            name=team.name,
            category_code=team.category_id  # Ajustar se necessário
        )
        for team in teams
    ]
    
    return TeamAutocompleteResponse(
        items=items,
        total=len(items)
    )


# =============================================================================
# HELPERS
# =============================================================================



# =============================================================================
# CLOUDINARY - ASSINATURA E UPLOAD
# =============================================================================

@router.post(
    "/media/cloudinary/sign",
    summary="Gerar assinatura Cloudinary",
    description="Gera assinatura para upload direto ao Cloudinary (signed upload)"
)
async def sign_cloudinary_upload(
    person_id: UUID,
    ctx: ExecutionContext = Depends(permission_dep),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Gera assinatura para upload direto ao Cloudinary.
    
    O frontend usa esta assinatura para fazer upload direto,
    sem passar pelo backend.
    """
    from app.services.cloudinary_service import generate_signature
    from app.models.person import Person
    
    logger.info(f"Cloudinary signature request | person_id={person_id} | actor={ctx.user.id}")
    
    # Verifica se pessoa existe
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    try:
        signature_data = generate_signature(person_id)
        return signature_data
    except Exception as e:
        logger.error(f"Error generating Cloudinary signature: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao gerar assinatura Cloudinary"
        )


@router.post(
    "/persons/{person_id}/media",
    status_code=201,
    summary="Persistir mídia da pessoa",
    description="Salva referência da foto após upload no Cloudinary"
)
async def save_person_media(
    person_id: UUID,
    public_id: str = Query(..., description="Public ID retornado pelo Cloudinary"),
    db: AsyncSession = Depends(get_async_db),
    ctx: ExecutionContext = Depends(permission_dep)
):
    """
    Persiste referência da foto após upload no Cloudinary.
    
    Chamado pelo frontend após upload bem-sucedido.
    """
    from app.models.person import Person, PersonMedia
    from app.services.cloudinary_service import get_delivery_url
    from datetime import datetime, timezone
    
    logger.info(f"Saving person media | person_id={person_id} | public_id={public_id}")
    
    # Verifica se pessoa existe
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    # Desmarca primária anterior
    db.query(PersonMedia).filter(
        PersonMedia.person_id == person_id,
        PersonMedia.media_type == 'foto_perfil',
        PersonMedia.is_primary == True
    ).update({'is_primary': False})
    
    # Cria novo registro
    delivery_url = get_delivery_url(public_id)
    
    media = PersonMedia(
        person_id=person_id,
        media_type='foto_perfil',
        file_url=delivery_url,
        is_primary=True,
        created_by_user_id=ctx.user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(media)
    db.commit()
    
    logger.info(f"Person media saved | person_id={person_id} | url={delivery_url}")
    
    return {
        "person_id": str(person_id),
        "media_id": str(media.id),
        "file_url": delivery_url
    }

