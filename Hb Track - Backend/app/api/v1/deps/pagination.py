"""
Dependency de paginação e ordenação.

Padrão de paginação:
- page: página atual (1-indexed)
- page_size: itens por página (máx 100)
- order_by: campo de ordenação (whitelist por endpoint)
- order_dir: direção (asc/desc)

Uso:
    @router.get("/items")
    def list_items(
        pagination: PaginationParams = Depends(pagination_params),
    ):
        page, page_size, order_by, order_dir = pagination
        ...
"""
from typing import NamedTuple, Optional, Dict, Any, TypeVar, Generic, List
from fastapi import Query
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query as SAQuery


class PaginationParams(NamedTuple):
    """Parâmetros de paginação extraídos da query."""
    page: int
    page_size: int
    order_by: Optional[str]
    order_dir: str


def pagination_params(
    page: int = Query(1, ge=1, description="Número da página (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Itens por página (máx 100)"),
    order_by: Optional[str] = Query(None, description="Campo de ordenação"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$", description="Direção: asc ou desc"),
) -> PaginationParams:
    """
    Dependency para extrair parâmetros de paginação.
    
    Exemplo:
        GET /reports/attendance?page=1&page_size=25&order_by=attendance_rate&order_dir=desc
    """
    return PaginationParams(
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_dir=order_dir,
    )


class PaginationMeta(BaseModel):
    """Metadados de paginação para resposta."""
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Itens por página")
    total: int = Field(..., description="Total de itens")
    total_pages: int = Field(..., description="Total de páginas")


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica."""
    items: List[T]
    pagination: PaginationMeta


def calculate_pagination(
    total: int,
    page: int,
    page_size: int,
) -> PaginationMeta:
    """Calcula metadados de paginação."""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def apply_sorting(
    query: SAQuery,
    order_by: Optional[str],
    order_dir: str,
    allowed_fields: Dict[str, Any],
    default_field: Optional[str] = None,
) -> SAQuery:
    """
    Aplica ordenação segura a uma query SQLAlchemy.
    
    Args:
        query: Query SQLAlchemy
        order_by: Campo solicitado pelo cliente
        order_dir: Direção (asc/desc)
        allowed_fields: Whitelist de campos permitidos {nome: coluna}
        default_field: Campo padrão se nenhum for especificado
    
    Returns:
        Query com ordenação aplicada
    
    Segurança:
        - Nunca interpola campos livres do usuário
        - Apenas campos na whitelist são aceitos
    """
    # Determinar campo efetivo
    effective_field = order_by if order_by in allowed_fields else default_field
    
    if effective_field and effective_field in allowed_fields:
        column = allowed_fields[effective_field]
        if order_dir == "asc":
            return query.order_by(asc(column))
        return query.order_by(desc(column))
    
    return query


def apply_pagination(
    query: SAQuery,
    page: int,
    page_size: int,
) -> SAQuery:
    """
    Aplica offset/limit à query.
    
    Args:
        query: Query SQLAlchemy
        page: Página atual (1-indexed)
        page_size: Itens por página
    
    Returns:
        Query com paginação aplicada
    """
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


# =============================================================================
# WHITELISTS DE ORDENAÇÃO POR ENDPOINT
# =============================================================================

# Campos permitidos para ordenação em /reports/attendance
ATTENDANCE_ORDER_FIELDS = {
    "athlete_name": "athlete_name",
    "training_attendance_rate": "training_attendance_rate",
    "match_participation_rate": "match_participation_rate", 
    "combined_attendance_rate": "combined_attendance_rate",
    "training_sessions_present": "training_sessions_present",
    "matches_played": "matches_played",
}

# Campos permitidos para ordenação em /reports/minutes
MINUTES_ORDER_FIELDS = {
    "athlete_name": "athlete_name",
    "total_minutes_played": "total_minutes_played",
    "total_training_minutes": "total_training_minutes",
    "total_activity_minutes": "total_activity_minutes",
    "matches_played": "matches_played",
    "avg_minutes_per_match": "avg_minutes_per_match",
}

# Campos permitidos para ordenação em /reports/load
LOAD_ORDER_FIELDS = {
    "athlete_name": "athlete_name",
    "training_load_total": "training_load_total",
    "match_load_total": "match_load_total",
    "total_load": "total_load",
    "avg_daily_load": "avg_daily_load",
    "is_overloaded": "is_overloaded",
}

# Campos permitidos para ordenação em /alerts/load
LOAD_ALERTS_ORDER_FIELDS = {
    "athlete_name": "athlete_name",
    "status": "status",
    "weekly_load": "weekly_load",
    "daily_avg_load": "daily_avg_load",
    "variance_percent": "variance_percent",
}

# Campos permitidos para ordenação em /alerts/injury-return
INJURY_ALERTS_ORDER_FIELDS = {
    "athlete_name": "athlete_name",
    "status": "status",
    "days_since_injury": "days_since_injury",
    "expected_return": "expected_return",
}
