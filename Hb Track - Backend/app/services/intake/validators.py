"""
Validadores para Ficha Única

FASE 3 - FICHA.MD Seção 3.1

Funções de normalização e verificação de duplicatas para:
- CPF
- Email
- Telefone
- Documentos

Regras implementadas:
- Normalização de dados antes de validação
- Verificação de duplicatas no banco
- Regra do goleiro (RD13)

FASE 4 - FICHA.MD Seção 4.1
Autorização e escopo para criação de Ficha Única
"""
import re
from typing import Optional
from sqlalchemy import and_, select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.person import Person, PersonContact, PersonDocument
from app.models.defensive_position import DefensivePosition
from app.models.organization import Organization
from app.models.membership import OrgMembership
from app.core.context import ExecutionContext
from app.core.permissions import require_org_scope, require_team_scope
from app.schemas.intake.ficha_unica import FichaUnicaRequest


# =============================================================================
# AUTORIZAÇÃO E ESCOPO (FASE 4)
# =============================================================================

def _validate_user_role_permission(ctx: ExecutionContext, role_id: int) -> None:
    """
    Valida se usuário autenticado pode criar usuário com o role_id solicitado.
    
    MATRIZ DE PERMISSÕES:
    - superadmin (bypass - já validado antes)
    - dirigente: pode criar coordenador(2), treinador(3), atleta(4) - NÃO pode criar dirigente(1)
    - coordenador: pode criar treinador(3), atleta(4) - NÃO pode criar dirigente(1) ou coordenador(2)
    - treinador: pode criar apenas atleta(4) - NÃO pode criar dirigente(1), coordenador(2), treinador(3)
    
    Args:
        ctx: Contexto de execução
        role_id: ID do papel que se deseja criar
    
    Raises:
        HTTPException 403: Se usuário não pode criar esse papel
    
    References:
        - R25: Papéis e permissões
        - Apenas superadmin pode criar dirigente
    """
    # Mapeamento de papéis permitidos por papel do usuário
    allowed_roles_by_user = {
        "dirigente": [2, 3, 4],  # coordenador, treinador, atleta
        "coordenador": [3, 4],   # treinador, atleta
        "treinador": [4]         # apenas atleta
    }
    
    allowed = allowed_roles_by_user.get(ctx.role_code, [])
    
    if role_id not in allowed:
        role_names = {1: "dirigente", 2: "coordenador", 3: "treinador", 4: "atleta"}
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "FORBIDDEN",
                "message": f"Papel '{ctx.role_code}' não pode criar usuário com papel '{role_names.get(role_id, 'desconhecido')}'. "
                          f"Apenas superadmin pode criar dirigente.",
                "constraint": "R25 - Apenas superadmin cria dirigente"
            }
        )


def _validate_dirigente_single_org(ctx: ExecutionContext, db: Session) -> None:
    """
    Valida que dirigente não criou outra organização anteriormente.
    
    Regra: Dirigente só pode criar 1 organização.
    
    Args:
        ctx: Contexto de execução
        db: Sessão do banco de dados
    
    Raises:
        HTTPException 403: Se dirigente já criou uma organização
    """
    # Buscar organizações criadas por este usuário como dirigente
    existing_orgs = db.query(Organization).join(
        OrgMembership,
        and_(
            OrgMembership.organization_id == Organization.id,
            OrgMembership.person_id == ctx.person_id,
            OrgMembership.role_id == 1,  # 1 = dirigente
            OrgMembership.deleted_at.is_(None)
        )
    ).filter(
        Organization.created_by_user_id == ctx.user_id,
        Organization.deleted_at.is_(None)
    ).count()
    
    if existing_orgs > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "FORBIDDEN",
                "message": f"Dirigente já criou uma organização. Apenas 1 organização permitida por dirigente.",
                "constraint": "Dirigente - Organização única"
            }
        )


def validate_ficha_scope(
    payload: FichaUnicaRequest,
    ctx: ExecutionContext,
    db: Session
) -> None:
    """
    Valida autorização para criação de Ficha Única baseado no papel do usuário.
    
    FASE 4 - FICHA.MD Seção 4.1
    
    Regras de autorização:
    - **superadmin**: Bypass completo, pode criar qualquer role_id
    - **dirigente**: Pode criar org (1x), criar equipe, criar coord/trei/atl, vincular atleta
    - **coordenador**: NÃO pode criar org, pode criar equipe, criar trei/atl, vincular atleta
    - **treinador**: NÃO pode criar org/equipe, criar apenas atl, vincular atleta
    
    Validações por modo:
    - organization.mode = "create": Requer papel dirigente/superadmin + dirigente só cria 1 org
    - organization.mode = "select": Valida escopo organizacional (require_org_scope)
    - team.mode = "create": Requer papel dirigente/coordenador ou superadmin
    - team.mode = "select": Valida escopo de equipe (require_team_scope)
    - create_user = true: Valida role_id permitido pelo papel do usuário
    
    Args:
        payload: Dados da ficha única (organization, team, athlete)
        ctx: Contexto de execução com user_id e papel
        db: Sessão do banco de dados
    
    Raises:
        HTTPException 403: Se usuário não autorizado para a operação
        HTTPException 400: Se dados inválidos (ex: team sem organization)
    
    References:
        - R25: Superadmin bypass
        - R34: Validação de escopo organizacional
        - Ficha única de cadastro.txt: Matriz de autorização
    """
    # Superadmin bypass completo
    if ctx.is_superadmin:
        return
    
    # =========================================================================
    # VALIDAÇÃO 0: CRIAÇÃO DE TEMPORADA (FASE 4.1)
    # =========================================================================
    if payload.season and payload.season.mode == "create":
        # Apenas dirigente pode criar temporada (superadmin já passou no bypass)
        if ctx.role_code not in ["dirigente"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": f"Papel '{ctx.role_code}' não pode criar temporada. Apenas 'dirigente' tem essa permissão.",
                    "constraint": "Ficha Única - Autorização de criação de temporada"
                }
            )
    
    # =========================================================================
    # VALIDAÇÃO 1: CRIAÇÃO DE USUÁRIO (role_id permitido)
    # =========================================================================
    if payload.create_user and payload.user and payload.user.role_id:
        _validate_user_role_permission(ctx, payload.user.role_id)
    
    # =========================================================================
    # VALIDAÇÃO 2: CRIAÇÃO DE ORGANIZAÇÃO
    # =========================================================================
    if payload.organization.mode == "create":
        # Apenas dirigente pode criar organização
        if ctx.role_code not in ["dirigente"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": f"Papel '{ctx.role_code}' não pode criar organização. Apenas 'dirigente' tem essa permissão.",
                    "constraint": "Ficha Única - Autorização de criação de organização"
                }
            )
        
        # Dirigente só pode criar 1 organização
        _validate_dirigente_single_org(ctx, db)
    elif payload.organization.mode == "select":
        # Valida que organização pertence ao escopo do usuário
        if payload.organization.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_DATA",
                    "message": "organization_id é obrigatório quando mode='select'"
                }
            )
        require_org_scope(payload.organization.organization_id, ctx)
    
    # Validação de equipe
    if payload.team.mode == "create":
        # Coordenador e dirigente podem criar equipes
        if ctx.role_code not in ["dirigente", "coordenador"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": f"Papel '{ctx.role_code}' não pode criar equipe. Apenas 'dirigente' ou 'coordenador' têm essa permissão.",
                    "constraint": "Ficha Única - Autorização de criação de equipe"
                }
            )
        
        # Se estiver criando equipe, deve ter organization_id (select) ou estar criando org
        if payload.organization.mode == "select":
            if payload.team.organization_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "INVALID_DATA",
                        "message": "team.organization_id é obrigatório quando team.mode='create' e organization.mode='select'"
                    }
                )
            # Valida escopo organizacional da equipe
            require_org_scope(payload.team.organization_id, ctx)
    
    elif payload.team.mode == "select":
        # Todos os papéis podem vincular em equipe existente
        if payload.team.team_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_DATA",
                    "message": "team_id é obrigatório quando mode='select'"
                }
            )
        # Valida escopo da equipe (retorna Team se válido)
        require_team_scope(payload.team.team_id, ctx, db)


# =============================================================================
# FUNÇÕES DE NORMALIZAÇÃO
# =============================================================================

def normalize_cpf(cpf: str) -> str:
    """
    Remove caracteres não numéricos do CPF.
    
    Args:
        cpf: CPF com ou sem formatação (ex: "123.456.789-09" ou "12345678909")
    
    Returns:
        CPF apenas com números (ex: "12345678909")
    """
    return re.sub(r'\D', '', cpf)


def normalize_phone(phone: str) -> str:
    """
    Remove caracteres não numéricos do telefone.
    
    Args:
        phone: Telefone com ou sem formatação (ex: "(11) 98765-4321")
    
    Returns:
        Telefone apenas com números (ex: "11987654321")
    """
    return re.sub(r'\D', '', phone)


def normalize_email(email: str) -> str:
    """
    Normaliza e-mail para lowercase e remove espaços.
    
    Args:
        email: Email com qualquer formatação
    
    Returns:
        Email em lowercase sem espaços
    """
    return email.strip().lower()


def validate_cpf_checksum(cpf: str) -> bool:
    """
    Valida dígitos verificadores do CPF.
    
    Args:
        cpf: CPF normalizado (apenas números)
    
    Returns:
        True se CPF válido, False caso contrário
    """
    cpf = normalize_cpf(cpf)
    
    if len(cpf) != 11:
        return False
    
    # CPFs inválidos conhecidos (todos dígitos iguais)
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2


# =============================================================================
# FUNÇÕES DE VERIFICAÇÃO DE DUPLICATAS
# =============================================================================

def check_duplicate_contact(
    db: Session,
    contact_value: str,
    contact_type: str
) -> Optional[Person]:
    """
    Verifica se contato já existe no banco.
    
    Args:
        db: Sessão do banco
        contact_value: Valor do contato
        contact_type: Tipo ("email", "telefone", "whatsapp")
    
    Returns:
        Person se encontrar duplicata, None caso contrário
    """
    # Normalizar valor baseado no tipo
    if contact_type == "email":
        normalized = normalize_email(contact_value)
    elif contact_type in ["telefone", "whatsapp"]:
        normalized = normalize_phone(contact_value)
    else:
        normalized = contact_value.strip()
    
    # Buscar contato existente
    contact = db.execute(
        select(PersonContact)
        .where(
            and_(
                PersonContact.contact_value == normalized,
                PersonContact.contact_type == contact_type,
                PersonContact.deleted_at.is_(None)
            )
        )
    ).scalar()
    
    if contact:
        # Retornar a pessoa associada
        return db.execute(
            select(Person)
            .where(
                and_(
                    Person.id == contact.person_id,
                    Person.deleted_at.is_(None)
                )
            )
        ).scalar()
    
    return None


def check_duplicate_document(
    db: Session,
    document_number: str,
    document_type: str
) -> Optional[Person]:
    """
    Verifica se documento já existe no banco.
    
    Args:
        db: Sessão do banco
        document_number: Número do documento
        document_type: Tipo ("cpf", "rg", "cnh", etc.)
    
    Returns:
        Person se encontrar duplicata, None caso contrário
    """
    # Normalizar CPF
    if document_type == "cpf":
        normalized = normalize_cpf(document_number)
    else:
        normalized = "".join(c for c in document_number if c.isalnum())
    
    # Buscar documento existente
    doc = db.execute(
        select(PersonDocument)
        .where(
            and_(
                PersonDocument.document_number == normalized,
                PersonDocument.document_type == document_type,
                PersonDocument.deleted_at.is_(None)
            )
        )
    ).scalar()
    
    if doc:
        # Retornar a pessoa associada
        return db.execute(
            select(Person)
            .where(
                and_(
                    Person.id == doc.person_id,
                    Person.deleted_at.is_(None)
                )
            )
        ).scalar()
    
    return None


def check_email_exists(db: Session, email: str) -> bool:
    """
    Verifica se email já está cadastrado como contato.
    
    Args:
        db: Sessão do banco
        email: Email a verificar
    
    Returns:
        True se existe, False caso contrário
    """
    normalized = normalize_email(email)
    result = db.execute(
        select(PersonContact.id)
        .where(
            and_(
                func.lower(PersonContact.contact_value) == normalized,
                PersonContact.contact_type == "email",
                PersonContact.deleted_at.is_(None)
            )
        )
        .limit(1)
    ).first()
    return result is not None


def check_cpf_exists(db: Session, cpf: str) -> bool:
    """
    Verifica se CPF já está cadastrado.
    
    Args:
        db: Sessão do banco
        cpf: CPF a verificar
    
    Returns:
        True se existe, False caso contrário
    """
    normalized = normalize_cpf(cpf)
    result = db.execute(
        select(PersonDocument.id)
        .where(
            and_(
                PersonDocument.document_number == normalized,
                PersonDocument.document_type == "cpf",
                PersonDocument.deleted_at.is_(None)
            )
        )
        .limit(1)
    ).first()
    return result is not None


def check_phone_exists(db: Session, phone: str) -> bool:
    """
    Verifica se telefone já está cadastrado.
    
    Args:
        db: Sessão do banco
        phone: Telefone a verificar
    
    Returns:
        True se existe, False caso contrário
    """
    normalized = normalize_phone(phone)
    result = db.execute(
        select(PersonContact.id)
        .where(
            and_(
                PersonContact.contact_value == normalized,
                PersonContact.contact_type.in_(["telefone", "whatsapp"]),
                PersonContact.deleted_at.is_(None)
            )
        )
        .limit(1)
    ).first()
    return result is not None


# =============================================================================
# VALIDAÇÃO DE REGRAS DE ATLETA
# =============================================================================

def is_goalkeeper_position(db: Session, position_id: Optional[int]) -> bool:
    """
    Verifica se a posição é de goleira.
    
    Args:
        db: Sessão do banco
        position_id: ID da posição defensiva
    
    Returns:
        True se é goleira, False caso contrário
    """
    if not position_id:
        return False
    
    result = db.execute(
        select(DefensivePosition.code)
        .where(DefensivePosition.id == position_id)
    ).scalar()
    
    return result in ("goleira", "goleiro", "goalkeeper", "GK")


def validate_goalkeeper_positions(
    db: Session,
    athlete_data: dict
) -> dict:
    """
    Aplica regra do goleiro (RD13): se posição defensiva = goleiro,
    limpa posições ofensivas.
    
    Args:
        db: Sessão do banco
        athlete_data: Dicionário com dados do atleta
    
    Returns:
        athlete_data modificado (posições ofensivas NULL se goleira)
    
    Raises:
        HTTPException 422 se não-goleiro sem posição ofensiva principal
    """
    main_defensive_id = athlete_data.get('main_defensive_position_id')
    
    if is_goalkeeper_position(db, main_defensive_id):
        # Goleira: limpar posições ofensivas
        athlete_data['main_offensive_position_id'] = None
        athlete_data['secondary_offensive_position_id'] = None
    else:
        # Não-goleira: posição ofensiva principal é obrigatória
        if not athlete_data.get('main_offensive_position_id'):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "INVALID_POSITION",
                    "message": "Posição ofensiva principal é obrigatória para não-goleiros",
                    "constraint": "RD13"
                }
            )
    
    return athlete_data


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Autorização (FASE 4)
    "validate_ficha_scope",
    # Normalização
    "normalize_cpf",
    "normalize_phone",
    "normalize_email",
    "validate_cpf_checksum",
    # Verificação de duplicatas
    "check_duplicate_contact",
    "check_duplicate_document",
    "check_email_exists",
    "check_cpf_exists",
    "check_phone_exists",
    # Validação de atleta
    "is_goalkeeper_position",
    "validate_goalkeeper_positions",
]
