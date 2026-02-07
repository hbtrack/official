"""
Validações Canônicas para Atletas

Implementação das regras de validação conforme decisões canônicas:
- Q3: Validação de categoria (R15) na criação de team_registration e convocação
- Q4: Validação de gênero (elegibilidade) bloqueante

CANÔNICO (31/12/2025): Gênero vem de persons.gender, NÃO athletes.gender

Data de canonização: 31/12/2025
"""

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.athlete import Athlete
from app.models.person import Person
from app.models.team import Team
from app.models.category import Category
from app.core.exceptions import ValidationError


def calculate_athlete_category(
    birth_date: date,
    season_year: int,
    db: Session
) -> Optional[Category]:
    """
    Calcula a categoria natural da atleta com base na idade na temporada.
    
    Regra R15: idade = ano_temporada - ano_nascimento
    categoria_natural = menor categoria onde idade <= max_age
    
    Args:
        birth_date: Data de nascimento da atleta
        season_year: Ano da temporada
        db: Sessão do banco de dados
        
    Returns:
        Category ou None se não houver categoria adequada
    """
    age = season_year - birth_date.year
    
    # Buscar categoria onde idade <= max_age, ordenar por max_age ASC
    stmt = (
        select(Category)
        .where(Category.max_age >= age)
        .order_by(Category.max_age.asc())
    )
    
    result = db.execute(stmt).scalar_one_or_none()
    return result


def validate_category_eligibility(
    athlete_id: UUID,
    team_id: UUID,
    season_year: int,
    db: Session
) -> None:
    """
    Valida se atleta pode jogar na categoria da equipe (R15).
    
    Regra canônica: Atleta pode jogar na sua categoria natural ou acima,
    NUNCA em categoria abaixo.
    
    Args:
        athlete_id: ID da atleta
        team_id: ID da equipe
        season_year: Ano da temporada
        db: Sessão do banco de dados
        
    Raises:
        ValidationError: Se atleta não pode jogar na categoria da equipe
    """
    # Buscar atleta
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise ValidationError("Atleta não encontrada")
    
    # Buscar equipe e categoria
    team = db.get(Team, team_id)
    if not team:
        raise ValidationError("Equipe não encontrada")
    
    if not team.category_id:
        raise ValidationError("Equipe não possui categoria definida")
    
    team_category = db.get(Category, team.category_id)
    if not team_category:
        raise ValidationError("Categoria da equipe não encontrada")
    
    # Calcular categoria natural da atleta
    athlete_category = calculate_athlete_category(
        athlete.birth_date,
        season_year,
        db
    )
    
    if not athlete_category:
        raise ValidationError("Não foi possível determinar categoria da atleta")
    
    # VALIDAÇÃO R15: categoria_natural <= categoria_equipe
    # (categorias com max_age menor são "inferiores")
    if athlete_category.max_age > team_category.max_age:
        raise ValidationError(
            f"Atleta não pode jogar em categoria inferior. "
            f"Categoria natural: {athlete_category.name} (idade máx: {athlete_category.max_age}), "
            f"Categoria da equipe: {team_category.name} (idade máx: {team_category.max_age})"
        )


def validate_gender_eligibility(
    athlete_id: UUID,
    team_id: UUID,
    db: Session
) -> None:
    """
    Valida compatibilidade de gênero entre atleta e equipe.
    
    CANÔNICO (31/12/2025): Gênero obtido de persons.gender (via athlete.person_id)
    
    Regra canônica (Q4-A): Sistema valida e BLOQUEIA incompatibilidade.
    
    Regras:
    - feminino pode jogar em feminino ou misto
    - masculino pode jogar em masculino ou misto
    - feminino NÃO pode jogar em masculino (bloqueado)
    - masculino NÃO pode jogar em feminino (bloqueado)
    
    Args:
        athlete_id: ID da atleta
        team_id: ID da equipe
        db: Sessão do banco de dados
        
    Raises:
        ValidationError: Se gênero incompatível ou não definido
    """
    # Buscar atleta
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise ValidationError("Atleta não encontrada")
    
    # CANÔNICO: Buscar pessoa para obter gênero
    person = db.get(Person, athlete.person_id)
    if not person:
        raise ValidationError("Pessoa da atleta não encontrada")
    
    # Buscar equipe
    team = db.get(Team, team_id)
    if not team:
        raise ValidationError("Equipe não encontrada")
    
    # CANÔNICO: Gênero da pessoa é OBRIGATÓRIO para elegibilidade
    if not person.gender:
        raise ValidationError(
            "Gênero da pessoa não está definido. "
            "É obrigatório definir persons.gender para validar elegibilidade."
        )
    
    # Se equipe não tem gênero definido, permitir (compatibilidade)
    if not team.gender:
        return
    
    person_gender = person.gender.lower().strip()
    team_gender = team.gender.lower().strip()
    
    # Equipes mistas aceitam qualquer gênero
    if team_gender == "misto":
        return
    
    # Regras de elegibilidade
    allowed_combinations = {
        ('feminino', 'feminino'),
        ('masculino', 'masculino'),
    }
    
    if (person_gender, team_gender) not in allowed_combinations:
        raise ValidationError(
            f"Atleta de gênero '{person_gender}' não pode jogar em equipe de gênero '{team_gender}'. "
            f"Regra de elegibilidade violada (R15)."
        )


def validate_team_registration_eligibility(
    athlete_id: UUID,
    team_id: UUID,
    season_year: int,
    db: Session
) -> None:
    """
    Valida TODAS as regras de elegibilidade para criação de team_registration.
    
    Esta é a PRIMEIRA linha de validação (Q3-C).
    
    Args:
        athlete_id: ID da atleta
        team_id: ID da equipe
        season_year: Ano da temporada
        db: Sessão do banco de dados
        
    Raises:
        ValidationError: Se qualquer validação falhar
    """
    # Validar categoria (R15)
    validate_category_eligibility(athlete_id, team_id, season_year, db)
    
    # Validar gênero
    validate_gender_eligibility(athlete_id, team_id, db)


def validate_match_convocation_eligibility(
    athlete_id: UUID,
    team_id: UUID,
    match_date: date,
    season_year: int,
    db: Session
) -> None:
    """
    Valida TODAS as regras de elegibilidade para convocação de partida.
    
    Esta é a SEGUNDA linha de validação (Q3-C - última linha de defesa).
    
    Validações redundantes intencionais:
    - R15 (categoria) - pode ter mudado se birth_date foi corrigida
    - Gênero - revalidar compatibilidade
    - Flags de restrição (injured, suspended_until) - bloqueio operacional
    - Vínculo ativo (team_registration) - deve existir vínculo ativo
    
    Args:
        athlete_id: ID da atleta
        team_id: ID da equipe
        match_date: Data da partida
        season_year: Ano da temporada
        db: Sessão do banco de dados
        
    Raises:
        ValidationError: Se qualquer validação falhar
    """
    # Buscar atleta
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise ValidationError("Atleta não encontrada")
    
    # 1. Revalidar categoria (R15)
    validate_category_eligibility(athlete_id, team_id, season_year, db)
    
    # 2. Revalidar gênero
    validate_gender_eligibility(athlete_id, team_id, db)
    
    # 3. Validar flags de restrição
    if athlete.injured:
        raise ValidationError("Atleta lesionada não pode ser convocada")
    
    if athlete.suspended_until and athlete.suspended_until >= match_date:
        raise ValidationError(
            f"Atleta suspensa até {athlete.suspended_until.isoformat()}. "
            f"Não pode participar de partida em {match_date.isoformat()}"
        )
    
    # 4. Validar vínculo ativo (team_registration)
    from app.models.team_registration import TeamRegistration
    
    stmt = (
        select(TeamRegistration)
        .where(
            TeamRegistration.athlete_id == athlete_id,
            TeamRegistration.team_id == team_id,
            TeamRegistration.end_at.is_(None)  # Vínculo ativo
        )
    )
    
    active_registration = db.execute(stmt).scalar_one_or_none()
    
    if not active_registration:
        raise ValidationError(
            "Atleta não possui vínculo ativo com esta equipe. "
            "É necessário team_registration ativo para convocação."
        )


def validate_athlete_state_change(
    athlete: Athlete,
    new_state: str,
    db: Session
) -> None:
    """
    Valida mudança de estado da atleta.
    
    Comportamento especial para 'dispensada':
    - Encerra automaticamente todos os team_registrations ativos
    - Atualiza organization_id para NULL
    
    Args:
        athlete: Objeto Athlete
        new_state: Novo estado ('ativa', 'dispensada', 'arquivada')
        db: Sessão do banco de dados
        
    Raises:
        ValidationError: Se mudança não permitida
    """
    valid_states = ['ativa', 'dispensada', 'arquivada']
    
    if new_state not in valid_states:
        raise ValidationError(
            f"Estado inválido: {new_state}. "
            f"Valores permitidos: {', '.join(valid_states)}"
        )
    
    # Se mudando para 'dispensada', será necessário encerrar vínculos
    # (implementado no service)
    if new_state == 'dispensada':
        # Apenas validação, ação será executada no service
        pass


def validate_birth_date_for_team(
    birth_date: date,
    team_id: UUID,
    season_year: int,
    db: Session,
    role_code: str
) -> None:
    """
    Valida se a data de nascimento é compatível com a categoria da equipe.
    
    Regra R15: Atleta só pode jogar na categoria natural ou superior, NUNCA inferior.
    Esta validação ocorre no fluxo de welcome_complete ANTES de criar registro em athletes.
    
    Args:
        birth_date: Data de nascimento do novo membro
        team_id: ID da equipe
        season_year: Ano da temporada ativa
        db: Sessão do banco de dados
        role_code: Código do papel (ex: "atleta", "treinador")
        
    Raises:
        ValidationError: Se data de nascimento incompatível com categoria da equipe
    """
    # Validar APENAS se for atleta
    if role_code != "atleta":
        return
    
    # Buscar equipe
    team = db.get(Team, team_id)
    if not team:
        raise ValidationError("Equipe não encontrada")
    
    # Verificar se equipe tem categoria definida
    if not team.category_id:
        raise ValidationError("Equipe não possui categoria definida")
    
    # Buscar categoria da equipe
    team_category = db.get(Category, team.category_id)
    if not team_category:
        raise ValidationError("Categoria da equipe não encontrada")
    
    # Calcular categoria natural do atleta
    athlete_category = calculate_athlete_category(
        birth_date,
        season_year,
        db
    )
    
    if not athlete_category:
        raise ValidationError("Não foi possível determinar categoria para esta data de nascimento")
    
    # Aplicar regra R15: categoria_natural <= categoria_equipe
    # Se max_age da categoria natural > max_age da categoria da equipe, significa que
    # o atleta é mais velho e está tentando jogar em categoria inferior (BLOQUEADO)
    if athlete_category.max_age > team_category.max_age:
        raise ValidationError(
            f"Não foi possível completar o cadastro! Sua idade não corresponde à "
            f"categoria {team_category.name} (até {team_category.max_age} anos). "
            f"Por favor, verifique com o administrador."
        )
