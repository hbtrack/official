"""
Router para Lookup de dados estáticos (tabelas de referência)

Endpoints para:
- Posições ofensivas
- Posições defensivas
- Categorias
- Níveis de escolaridade
- Organizações
- Equipes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.db import get_async_db
from app.core.auth import get_current_user, MockUser

router = APIRouter(tags=["lookup"])

# ============================================================================
# SCHEMAS
# ============================================================================

class PositionResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    max_age: Optional[int] = None
    min_age: Optional[int] = None
    gender: Optional[str] = None
    
    class Config:
        from_attributes = True

class SchoolingLevelResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class OrganizationResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True

class TeamResponse(BaseModel):
    id: str
    name: str
    category_id: Optional[int] = None
    gender: Optional[str] = None
    season_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class SeasonResponse(BaseModel):
    id: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: bool = False
    
    class Config:
        from_attributes = True

# ============================================================================
# ENDPOINTS - POSIÇÕES
# ============================================================================

@router.get("/positions/offensive", response_model=List[PositionResponse])
async def get_offensive_positions(
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista todas as posições ofensivas."""
    result = await db.execute(
        text("SELECT id, name, code FROM offensive_positions ORDER BY id")
    )
    rows = result.fetchall()
    return [
        PositionResponse(id=row[0], name=row[1], code=row[2] if len(row) > 2 else None)
        for row in rows
    ]

@router.get("/positions/defensive", response_model=List[PositionResponse])
async def get_defensive_positions(
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista todas as posições defensivas."""
    result = await db.execute(
        text("SELECT id, name, code FROM defensive_positions ORDER BY id")
    )
    rows = result.fetchall()
    return [
        PositionResponse(id=row[0], name=row[1], code=row[2] if len(row) > 2 else None)
        for row in rows
    ]

# ============================================================================
# ENDPOINTS - CATEGORIAS
# ============================================================================

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista todas as categorias."""
    result = await db.execute(
        text("SELECT id, name, max_age, min_age, gender FROM categories ORDER BY id")
    )
    rows = result.fetchall()
    return [
        CategoryResponse(
            id=row[0], 
            name=row[1], 
            max_age=row[2] if len(row) > 2 else None,
            min_age=row[3] if len(row) > 3 else None,
            gender=row[4] if len(row) > 4 else None,
        )
        for row in rows
    ]

# ============================================================================
# ENDPOINTS - ESCOLARIDADE
# ============================================================================

@router.get("/schooling-levels", response_model=List[SchoolingLevelResponse])
async def get_schooling_levels(
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista todos os níveis de escolaridade."""
    # Verifica se a tabela existe
    check = await db.execute(
        text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'schooling_levels'
            )
        """)
    )
    exists = check.scalar()
    
    if not exists:
        # Retorna dados estáticos se tabela não existir
        return [
            SchoolingLevelResponse(id=1, name="Ensino Fundamental Incompleto"),
            SchoolingLevelResponse(id=2, name="Ensino Fundamental Completo"),
            SchoolingLevelResponse(id=3, name="Ensino Médio Incompleto"),
            SchoolingLevelResponse(id=4, name="Ensino Médio Completo"),
            SchoolingLevelResponse(id=5, name="Ensino Superior Incompleto"),
            SchoolingLevelResponse(id=6, name="Ensino Superior Completo"),
        ]
    
    result = await db.execute(
        text("SELECT id, name FROM schooling_levels ORDER BY id")
    )
    rows = result.fetchall()
    return [
        SchoolingLevelResponse(id=row[0], name=row[1])
        for row in rows
    ]

# ============================================================================
# ENDPOINTS - ORGANIZAÇÕES
# ============================================================================

@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_organizations(
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """
    Lista organizações acessíveis pelo usuário.
    Super admin vê todas, outros vêem apenas suas organizações.
    """
    # Verifica se é super_admin
    is_super = await db.execute(
        text("""
            SELECT EXISTS (
                SELECT 1 FROM memberships m
                JOIN roles r ON m.role_id = r.id
                WHERE m.person_id = :person_id 
                AND r.code = 'superadmin'
                AND m.is_active = true
            )
        """),
        {"person_id": str(current_user.person_id)}
    )
    is_super_admin = is_super.scalar()
    
    if is_super_admin:
        # Super admin vê todas as organizações
        result = await db.execute(
            text("SELECT id, name FROM organizations WHERE deleted_at IS NULL ORDER BY name")
        )
    else:
        # Outros vêem apenas suas organizações
        result = await db.execute(
            text("""
                SELECT DISTINCT o.id, o.name 
                FROM organizations o
                JOIN memberships m ON m.organization_id = o.id
                WHERE m.person_id = :person_id 
                AND m.is_active = true
                AND o.deleted_at IS NULL
                ORDER BY o.name
            """),
            {"person_id": str(current_user.person_id)}
        )
    
    rows = result.fetchall()
    return [
        OrganizationResponse(id=str(row[0]), name=row[1])
        for row in rows
    ]

# ============================================================================
# ENDPOINTS - TEMPORADAS
# ============================================================================

@router.get("/seasons", response_model=List[SeasonResponse])
async def get_seasons(
    organization_id: Optional[str] = Query(None, description="Filtrar por organização"),
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista temporadas disponíveis."""
    if organization_id:
        result = await db.execute(
            text("""
                SELECT id, name, start_date, end_date, is_active 
                FROM seasons 
                WHERE organization_id = :org_id
                ORDER BY start_date DESC
            """),
            {"org_id": organization_id}
        )
    else:
        result = await db.execute(
            text("""
                SELECT id, name, start_date, end_date, is_active 
                FROM seasons 
                ORDER BY start_date DESC
                LIMIT 20
            """)
        )
    
    rows = result.fetchall()
    return [
        SeasonResponse(
            id=str(row[0]), 
            name=row[1],
            start_date=str(row[2]) if row[2] else None,
            end_date=str(row[3]) if row[3] else None,
            is_active=row[4] if len(row) > 4 else False,
        )
        for row in rows
    ]

# ============================================================================
# ENDPOINTS - EQUIPES
# ============================================================================

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    organization_id: Optional[str] = Query(None, description="Filtrar por organização"),
    season_id: Optional[str] = Query(None, description="Filtrar por temporada"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    db: AsyncSession = Depends(get_async_db),
    current_user: MockUser = Depends(get_current_user),
):
    """Lista equipes com filtros opcionais."""
    query = """
        SELECT t.id, t.name, t.category_id, t.gender, t.season_id 
        FROM teams t
        WHERE t.deleted_at IS NULL
    """
    params = {}
    
    if organization_id:
        query += " AND t.organization_id = :org_id"
        params["org_id"] = organization_id
    
    if season_id:
        query += " AND t.season_id = :season_id"
        params["season_id"] = season_id
        
    if category_id:
        query += " AND t.category_id = :category_id"
        params["category_id"] = category_id
    
    query += " ORDER BY t.name"
    
    result = await db.execute(text(query), params)
    rows = result.fetchall()
    
    return [
        TeamResponse(
            id=str(row[0]), 
            name=row[1],
            category_id=row[2],
            gender=row[3],
            season_id=str(row[4]) if row[4] else None,
        )
        for row in rows
    ]
