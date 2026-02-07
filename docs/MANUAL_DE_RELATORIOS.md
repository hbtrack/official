<!-- STATUS: NEEDS_REVIEW -->

# MANUAL CANÔNICO DE RELATÓRIOS - HB TRACKING

**Versão:** 1.0
**Projeto:** HB Tracking - Sistema de Gestão de Handebol
**RAG:** [REGRAS_SISTEMAS.md](REGRAS_SISTEMAS.md)
**Data:** 2025-12-24

---

## 📚 SUMÁRIO

- [Introdução](#introdução)
- [Análise de Viabilidade](#análise-de-viabilidade)
- [Arquitetura de Relatórios](#arquitetura-de-relatórios)
- [GRUPO 1 - Relatórios Implementáveis Imediatamente](#grupo-1---relatórios-implementáveis-imediatamente)
  - [R1: Relatório de Performance em Treinos](#r1-relatório-de-performance-em-treinos)
  - [R2: Relatório Individual de Atleta (Treinos)](#r2-relatório-individual-de-atleta-treinos)
  - [R3: Relatório de Prontidão e Bem-Estar](#r3-relatório-de-prontidão-e-bem-estar)
  - [R4: Relatório de Gerenciamento de Lesões](#r4-relatório-de-gerenciamento-de-lesões)
- [GRUPO 2 - Relatórios Parcialmente Implementáveis](#grupo-2---relatórios-parcialmente-implementáveis)
  - [R5: Relatório de Performance em Partidas (Básico)](#r5-relatório-de-performance-em-partidas-básico)
  - [R6: Relatórios Personalizados de Grupo/Equipe](#r6-relatórios-personalizados-de-grupoequipe)
- [GRUPO 3 - Extensões Necessárias](#grupo-3---extensões-necessárias)
- [Implementação Técnica](#implementação-técnica)
- [Queries SQL de Referência](#queries-sql-de-referência)
- [Apêndices](#apêndices)

---

## 🎯 INTRODUÇÃO

### Objetivo do Manual

Este manual define **como implementar relatórios analíticos** para o HB Tracking **SEM CRIAR NOVAS TABELAS**, utilizando exclusivamente o schema existente consolidado na migration `4af09f9d46a0_initial_schema_consolidated`.

### Princípios de Implementação

1. **Zero Novas Tabelas**: Todos os relatórios devem usar tabelas existentes
2. **Views Materializadas**: Para agregações pesadas, usar `MATERIALIZED VIEW`
3. **Conformidade RAG**: Toda métrica deve referenciar regras específicas (R, RF, RD, RP)
4. **Performance First**: Queries otimizadas com índices adequados
5. **Auditabilidade**: Todos os cálculos devem ser rastreáveis

### Tabelas Disponíveis (26 tabelas)

**核心 (Core):**
- `persons`, `users`, `organizations`, `roles`, `permissions`, `role_permissions`, `membership`

**Temporada e Categorias:**
- `seasons`, `categories`

**Atletas e Equipes:**
- `athletes`, `athlete_states`, `teams`, `team_registrations`

**Treinos e Wellness:**
- `training_sessions`, `attendance`, `wellness_pre`, `wellness_post`

**Competições e Jogos:**
- `competitions`, `competition_seasons`, `matches`, `match_teams`, `match_roster`, `match_events`

**Médico:**
- `medical_cases`

**Views Existentes:**
- `v_session_athlete_dashboard` (treino + atleta + wellness)
- `v_training_session_summary` (agregados por treino)
- `v_seasons_with_status` (estados derivados de temporada)

---

## 🔍 ANÁLISE DE VIABILIDADE

### ✅ GRUPO 1 - Implementáveis Imediatamente (SEM modificações)

| Relatório | Tabelas Usadas | Complexidade | RAG |
|-----------|----------------|--------------|-----|
| **Performance em Treinos** | `training_sessions`, `attendance`, `wellness_post` | Baixa | R18, R22, RP5, RP6 |
| **Individual de Atleta (Treinos)** | `athletes`, `attendance`, `wellness_pre`, `wellness_post`, `medical_cases` | Média | R12, R13, RP4, RP5 |
| **Prontidão e Bem-Estar** | `wellness_pre`, `wellness_post`, `attendance` | Baixa | RP6, RP7, RP8 |
| **Gerenciamento de Lesões** | `medical_cases`, `athlete_states`, `attendance` | Média | R13, R14, RP7 |

### ⚠️ GRUPO 2 - Parcialmente Implementáveis (limitações)

| Relatório | Tabelas Usadas | Limitação | Solução |
|-----------|----------------|-----------|---------|
| **Performance em Partidas** | `matches`, `match_events`, `match_roster` | Eventos básicos (gols, faltas) sem detalhamento tático | Expandir `match_events.event_type` |
| **Personalizados de Grupo** | `athletes`, `teams`, `team_registrations` + qualquer tabela | Sem motor de templates | Criar endpoints parametrizáveis |

### ❌ GRUPO 3 - NÃO Implementáveis (requerem novas tabelas)

| Relatório | Dado Faltante | Tabela Necessária | Justificativa |
|-----------|---------------|-------------------|---------------|
| **Resultados de Testes Físicos** | Testes GPS, força, endurance | `physical_tests`, `test_results` | Dados externos (Catapult API) |
| **Análise de Vídeo** | Tags de vídeo, timestamps | `video_analysis`, `video_tags` | Integração com ferramentas de vídeo |

---

## 🏗️ ARQUITETURA DE RELATÓRIOS

### Camadas de Implementação

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 1: VIEWS MATERIALIZADAS (DB)                   │
│  └─ Agregações pesadas pré-calculadas                  │
│     Ex: mv_athlete_training_summary                     │
└─────────────────────────────────────────────────────────┘
              ↓ alimenta ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 2: SERVICES (Backend)                           │
│  └─ Lógica de negócio, filtros, validações RAG         │
│     Ex: TrainingReportService                           │
└─────────────────────────────────────────────────────────┘
              ↓ expõe via ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 3: ROUTERS (FastAPI)                            │
│  └─ Endpoints REST, paginação, permissões              │
│     Ex: GET /api/v1/reports/training-performance        │
└─────────────────────────────────────────────────────────┘
```

### Padrão de Nomenclatura

**Materialized Views:**
- Prefixo: `mv_`
- Formato: `mv_{dominio}_{metrica}_summary`
- Exemplo: `mv_athlete_training_summary`

**Services:**
- Sufixo: `ReportService`
- Localização: `backend/app/services/reports/`
- Exemplo: `training_report_service.py`

**Routers:**
- Prefixo: `/reports/`
- Agrupamento por domínio
- Exemplo: `/api/v1/reports/training-performance`

**Schemas:**
- Sufixo: `Report` ou `ReportResponse`
- Localização: `backend/app/schemas/reports/`
- Exemplo: `TrainingPerformanceReport`

---

## 📊 GRUPO 1 - RELATÓRIOS IMPLEMENTÁVEIS IMEDIATAMENTE

---

## R1: Relatório de Performance em Treinos

**Descrição:** Rastreia métricas de desempenho em treinos, incluindo carga, presença, PSE e clima de grupo.

**Regras RAG:**
- **R18**: Treinos são eventos operacionais editáveis
- **R22**: Dados de treino são métricas operacionais (carga, PSE, assiduidade)
- **RP5**: Ausência em treino gera carga = 0
- **RP6**: Toda participação gera métricas obrigatórias

### 1.1 - Dados Disponíveis

**Tabelas:**
```sql
training_sessions (
  id, organization_id, season_id, team_id,
  session_at, main_objective,
  planned_load, actual_load_avg, group_climate,
  highlight, next_corrections
)

attendance (
  id, session_id, athlete_id,
  status ('presente','ausente','medico','lesionada')
)

wellness_post (
  id, session_id, athlete_id,
  minutes, rpe, internal_load,
  fatigue_after, mood_after
)
```

**View Existente:**
```sql
v_training_session_summary (
  session_id, session_at, main_objective,
  total_registros, presentes, ausentes, dm, lesionadas,
  avg_minutes, avg_rpe, avg_internal_load,
  load_ok_count
)
```

### 1.2 - Materialized View (Performance)

**Arquivo:** `backend/db/migrations/create_mv_training_performance.sql`

```sql
-- ============================================================================
-- MATERIALIZED VIEW: Agregados de Performance de Treinos
-- Referências: R18, R22, RP5, RP6
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_training_performance AS
SELECT
  ts.id AS session_id,
  ts.organization_id,
  ts.season_id,
  ts.team_id,
  ts.session_at,
  ts.main_objective,
  ts.planned_load,
  ts.group_climate,

  -- Métricas de Presença (RP5)
  COUNT(DISTINCT att.athlete_id) AS total_athletes,
  COUNT(*) FILTER (WHERE att.status = 'presente') AS presentes,
  COUNT(*) FILTER (WHERE att.status = 'ausente') AS ausentes,
  COUNT(*) FILTER (WHERE att.status = 'medico') AS dm,
  COUNT(*) FILTER (WHERE att.status = 'lesionada') AS lesionadas,

  -- Taxa de presença (%)
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE att.status = 'presente') /
    NULLIF(COUNT(DISTINCT att.athlete_id), 0),
    2
  ) AS attendance_rate,

  -- Métricas de Carga (R22, RP6)
  ROUND(AVG(wp.minutes) FILTER (WHERE att.status = 'presente'), 1) AS avg_minutes,
  ROUND(AVG(wp.rpe) FILTER (WHERE att.status = 'presente'), 1) AS avg_rpe,
  ROUND(AVG(wp.internal_load) FILTER (WHERE att.status = 'presente'), 0) AS avg_internal_load,

  -- Desvio padrão de carga (identifica variação individual)
  ROUND(STDDEV(wp.internal_load) FILTER (WHERE att.status = 'presente'), 0) AS stddev_internal_load,

  -- Atletas com carga registrada
  COUNT(*) FILTER (
    WHERE att.status = 'presente'
      AND wp.minutes IS NOT NULL
      AND wp.rpe IS NOT NULL
  ) AS load_ok_count,

  -- % de dados completos
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE att.status = 'presente' AND wp.minutes IS NOT NULL AND wp.rpe IS NOT NULL) /
    NULLIF(COUNT(*) FILTER (WHERE att.status = 'presente'), 0),
    2
  ) AS data_completeness_pct,

  -- Fadiga e Humor Médios (wellness post)
  ROUND(AVG(wp.fatigue_after) FILTER (WHERE att.status = 'presente'), 1) AS avg_fatigue_after,
  ROUND(AVG(wp.mood_after) FILTER (WHERE att.status = 'presente'), 1) AS avg_mood_after,

  -- Timestamps
  ts.created_at,
  ts.updated_at

FROM training_sessions ts
LEFT JOIN attendance att ON att.session_id = ts.id
LEFT JOIN wellness_post wp ON wp.session_id = ts.id AND wp.athlete_id = att.athlete_id
WHERE ts.deleted_at IS NULL  -- Soft delete (RDB4)
GROUP BY ts.id, ts.organization_id, ts.season_id, ts.team_id, ts.session_at,
         ts.main_objective, ts.planned_load, ts.group_climate, ts.created_at, ts.updated_at;

-- Índices para performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_training_performance_session
  ON mv_training_performance(session_id);
CREATE INDEX IF NOT EXISTS idx_mv_training_performance_org_season
  ON mv_training_performance(organization_id, season_id);
CREATE INDEX IF NOT EXISTS idx_mv_training_performance_team
  ON mv_training_performance(team_id);
CREATE INDEX IF NOT EXISTS idx_mv_training_performance_date
  ON mv_training_performance(session_at DESC);

-- COMMENT (documentação)
COMMENT ON MATERIALIZED VIEW mv_training_performance IS
'Agregados de performance de treinos (R18, R22, RP5, RP6).
Atualizar via REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance.';
```

**Refresh Policy:**
```sql
-- Refresh automático (via cronjob ou trigger)
-- Opção 1: Trigger após INSERT/UPDATE em training_sessions
-- Opção 2: Cronjob diário às 02:00 UTC
-- Opção 3: Refresh manual via endpoint /api/v1/reports/refresh

-- Refresh concorrente (não bloqueia leituras)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance;
```

### 1.3 - Schema Pydantic

**Arquivo:** `backend/app/schemas/reports/training.py`

```python
"""
Schemas para relatórios de treino

Referências RAG:
- R18: Treinos são eventos operacionais
- R22: Dados de treino são métricas operacionais
- RP5: Ausência gera carga = 0
- RP6: Participação gera métricas obrigatórias
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class TrainingPerformanceMetrics(BaseModel):
    """Métricas agregadas de um treino (R22, RP6)"""

    # Presença (RP5)
    total_athletes: int = Field(..., description="Total de atletas registrados")
    presentes: int = Field(..., description="Atletas presentes")
    ausentes: int = Field(..., description="Atletas ausentes (RP5: carga = 0)")
    dm: int = Field(..., description="Atletas em DM (dispensados médico)")
    lesionadas: int = Field(..., description="Atletas lesionadas (R13)")
    attendance_rate: float = Field(..., description="Taxa de presença (%)")

    # Carga (R22, RP6)
    avg_minutes: Optional[float] = Field(None, description="Média de minutos (presentes)")
    avg_rpe: Optional[float] = Field(None, description="Média de RPE (presentes)")
    avg_internal_load: Optional[float] = Field(None, description="Média de carga interna (presentes)")
    stddev_internal_load: Optional[float] = Field(None, description="Desvio padrão de carga")

    # Completude de dados
    load_ok_count: int = Field(..., description="Atletas com carga registrada")
    data_completeness_pct: float = Field(..., description="% de dados completos")

    # Wellness pós-treino
    avg_fatigue_after: Optional[float] = Field(None, description="Fadiga média pós-treino (0-10)")
    avg_mood_after: Optional[float] = Field(None, description="Humor médio pós-treino (0-10)")


class TrainingPerformanceReport(BaseModel):
    """Relatório completo de performance de treino (R18, R22)"""

    # Identificação
    session_id: UUID
    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None

    # Dados do treino
    session_at: datetime
    main_objective: Optional[str] = None
    planned_load: Optional[int] = Field(None, ge=0, le=10, description="Carga planejada (0-10)")
    group_climate: Optional[int] = Field(None, ge=1, le=5, description="Clima do grupo (1-5)")

    # Métricas agregadas
    metrics: TrainingPerformanceMetrics

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingPerformanceFilters(BaseModel):
    """Filtros para relatório de performance de treinos"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    start_date: Optional[date] = Field(None, description="Data inicial (inclusiva)")
    end_date: Optional[date] = Field(None, description="Data final (inclusiva)")
    min_attendance_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa mínima de presença (%)")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)


class TrainingPerformanceTrend(BaseModel):
    """Tendências de performance ao longo do tempo"""

    period: str = Field(..., description="Período (week, month)")
    period_start: date
    period_end: date
    sessions_count: int
    avg_attendance_rate: float
    avg_internal_load: Optional[float] = None
    avg_fatigue: Optional[float] = None
    avg_mood: Optional[float] = None
```

### 1.4 - Service Layer

**Arquivo:** `backend/app/services/reports/training_report_service.py`

```python
"""
Service para relatórios de treino

Referências RAG:
- R18: Treinos editáveis dentro dos limites
- R22: Métricas operacionais
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias
"""
from sqlalchemy import select, func, text, and_, or_
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.schemas.reports.training import (
    TrainingPerformanceReport,
    TrainingPerformanceMetrics,
    TrainingPerformanceFilters,
    TrainingPerformanceTrend
)


class TrainingReportService:
    """Service para relatórios de performance de treino"""

    @staticmethod
    def get_training_performance(
        db: Session,
        filters: TrainingPerformanceFilters
    ) -> list[TrainingPerformanceReport]:
        """
        Lista relatórios de performance de treinos com filtros

        Referências:
        - R18: Treinos como eventos operacionais
        - R22: Métricas de carga, PSE, assiduidade

        Args:
            db: Sessão do banco
            filters: Filtros de busca

        Returns:
            Lista de TrainingPerformanceReport
        """
        # Query na materialized view
        query = text("""
            SELECT
                session_id,
                organization_id,
                season_id,
                team_id,
                session_at,
                main_objective,
                planned_load,
                group_climate,
                total_athletes,
                presentes,
                ausentes,
                dm,
                lesionadas,
                attendance_rate,
                avg_minutes,
                avg_rpe,
                avg_internal_load,
                stddev_internal_load,
                load_ok_count,
                data_completeness_pct,
                avg_fatigue_after,
                avg_mood_after,
                created_at,
                updated_at
            FROM mv_training_performance
            WHERE organization_id = :org_id
              AND (:season_id IS NULL OR season_id = :season_id)
              AND (:team_id IS NULL OR team_id = :team_id)
              AND (:start_date IS NULL OR session_at >= :start_date)
              AND (:end_date IS NULL OR session_at <= :end_date)
              AND (:min_attendance IS NULL OR attendance_rate >= :min_attendance)
            ORDER BY session_at DESC
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "start_date": filters.start_date,
            "end_date": filters.end_date,
            "min_attendance": filters.min_attendance_rate,
            "skip": filters.skip,
            "limit": filters.limit
        })

        reports = []
        for row in result:
            metrics = TrainingPerformanceMetrics(
                total_athletes=row.total_athletes,
                presentes=row.presentes,
                ausentes=row.ausentes,
                dm=row.dm,
                lesionadas=row.lesionadas,
                attendance_rate=row.attendance_rate,
                avg_minutes=row.avg_minutes,
                avg_rpe=row.avg_rpe,
                avg_internal_load=row.avg_internal_load,
                stddev_internal_load=row.stddev_internal_load,
                load_ok_count=row.load_ok_count,
                data_completeness_pct=row.data_completeness_pct,
                avg_fatigue_after=row.avg_fatigue_after,
                avg_mood_after=row.avg_mood_after
            )

            report = TrainingPerformanceReport(
                session_id=row.session_id,
                organization_id=row.organization_id,
                season_id=row.season_id,
                team_id=row.team_id,
                session_at=row.session_at,
                main_objective=row.main_objective,
                planned_load=row.planned_load,
                group_climate=row.group_climate,
                metrics=metrics,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            reports.append(report)

        return reports

    @staticmethod
    def get_training_trends(
        db: Session,
        organization_id: UUID,
        season_id: Optional[UUID],
        team_id: Optional[UUID],
        period: str = "week"  # 'week' ou 'month'
    ) -> list[TrainingPerformanceTrend]:
        """
        Calcula tendências de performance ao longo do tempo

        Referências:
        - R21: Estatísticas agregadas são derivadas
        - R22: Métricas de treino

        Args:
            db: Sessão
            organization_id: ID da organização
            season_id: ID da temporada (opcional)
            team_id: ID da equipe (opcional)
            period: Período de agregação ('week' ou 'month')

        Returns:
            Lista de tendências por período
        """
        # Determinar função de agregação temporal
        date_trunc = "week" if period == "week" else "month"

        query = text(f"""
            WITH periods AS (
                SELECT
                    date_trunc('{date_trunc}', session_at) AS period_start,
                    date_trunc('{date_trunc}', session_at) +
                        interval '1 {date_trunc}' - interval '1 day' AS period_end,
                    COUNT(*) AS sessions_count,
                    ROUND(AVG(attendance_rate), 2) AS avg_attendance_rate,
                    ROUND(AVG(avg_internal_load), 1) AS avg_internal_load,
                    ROUND(AVG(avg_fatigue_after), 1) AS avg_fatigue,
                    ROUND(AVG(avg_mood_after), 1) AS avg_mood
                FROM mv_training_performance
                WHERE organization_id = :org_id
                  AND (:season_id IS NULL OR season_id = :season_id)
                  AND (:team_id IS NULL OR team_id = :team_id)
                GROUP BY date_trunc('{date_trunc}', session_at)
                ORDER BY period_start DESC
                LIMIT 12  -- Últimas 12 semanas/meses
            )
            SELECT * FROM periods
        """)

        result = db.execute(query, {
            "org_id": str(organization_id),
            "season_id": str(season_id) if season_id else None,
            "team_id": str(team_id) if team_id else None
        })

        trends = []
        for row in result:
            trend = TrainingPerformanceTrend(
                period=period,
                period_start=row.period_start.date(),
                period_end=row.period_end.date(),
                sessions_count=row.sessions_count,
                avg_attendance_rate=row.avg_attendance_rate,
                avg_internal_load=row.avg_internal_load,
                avg_fatigue=row.avg_fatigue,
                avg_mood=row.avg_mood
            )
            trends.append(trend)

        return trends

    @staticmethod
    def refresh_materialized_view(db: Session) -> dict:
        """
        Atualiza materialized view de performance de treinos

        Referências:
        - R21: Estatísticas agregadas recalculáveis

        Returns:
            Status da atualização
        """
        try:
            db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_training_performance"))
            db.commit()
            return {
                "status": "success",
                "view": "mv_training_performance",
                "refreshed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "view": "mv_training_performance",
                "error": str(e)
            }
```

### 1.5 - Router (FastAPI)

**Arquivo:** `backend/app/api/v1/routers/reports.py`

```python
"""
Routers para relatórios

Referências RAG:
- R26: Permissões por papel (coordenador, treinador)
- R42: Modo somente leitura sem vínculo
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from uuid import UUID

from app.core.database import get_db
from app.core.context import ExecutionContext
from app.api.v1.deps.auth import get_current_context, require_role
from app.schemas.reports.training import (
    TrainingPerformanceReport,
    TrainingPerformanceFilters,
    TrainingPerformanceTrend
)
from app.services.reports.training_report_service import TrainingReportService


router = APIRouter(tags=["Reports"])


@router.get(
    "/training-performance",
    response_model=list[TrainingPerformanceReport],
    summary="Relatório de Performance em Treinos",
    description="""
    Retorna métricas agregadas de performance de treinos.

    **Referências RAG:**
    - R18: Treinos como eventos operacionais
    - R22: Métricas de carga, PSE, assiduidade
    - RP5: Ausência gera carga = 0
    - RP6: Participação gera métricas obrigatórias

    **Permissões:**
    - Coordenador: acesso total
    - Treinador: acesso às suas equipes (R26)
    """
)
async def get_training_performance_report(
    season_id: Optional[UUID] = Query(None, description="Filtrar por temporada"),
    team_id: Optional[UUID] = Query(None, description="Filtrar por equipe"),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    min_attendance_rate: Optional[float] = Query(None, ge=0, le=100, description="Taxa mínima de presença (%)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Lista relatórios de performance de treinos
    """
    filters = TrainingPerformanceFilters(
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
        min_attendance_rate=min_attendance_rate,
        skip=skip,
        limit=limit
    )

    return TrainingReportService.get_training_performance(db, filters)


@router.get(
    "/training-trends",
    response_model=list[TrainingPerformanceTrend],
    summary="Tendências de Performance em Treinos",
    description="""
    Retorna tendências agregadas por período (semana ou mês).

    **Referências RAG:**
    - R21: Estatísticas agregadas derivadas
    - R22: Métricas de treino
    """
)
async def get_training_trends(
    season_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    period: str = Query("week", regex="^(week|month)$"),
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador", "treinador"]))
):
    """
    Calcula tendências de performance ao longo do tempo
    """
    return TrainingReportService.get_training_trends(
        db=db,
        organization_id=ctx.organization_id,
        season_id=season_id,
        team_id=team_id,
        period=period
    )


@router.post(
    "/refresh-training-performance",
    status_code=status.HTTP_200_OK,
    summary="Atualizar Materialized View de Treinos",
    description="""
    Atualiza a materialized view de performance de treinos.

    **Referências RAG:**
    - R21: Estatísticas agregadas recalculáveis

    **Permissões:**
    - Apenas Coordenador
    """
)
async def refresh_training_performance(
    db: Session = Depends(get_db),
    ctx: ExecutionContext = Depends(require_role(["coordenador"]))
):
    """
    Força atualização da materialized view
    """
    return TrainingReportService.refresh_materialized_view(db)
```

### 1.6 - Checklist de Implementação R1

- [ ] Criar migration para `mv_training_performance`
- [ ] Aplicar migration: `alembic upgrade head`
- [ ] Validar view: `SELECT count(*) FROM mv_training_performance`
- [ ] Implementar `TrainingPerformanceMetrics` schema
- [ ] Implementar `TrainingPerformanceReport` schema
- [ ] Implementar `TrainingReportService.get_training_performance()`
- [ ] Implementar `TrainingReportService.get_training_trends()`
- [ ] Implementar router `GET /reports/training-performance`
- [ ] Implementar router `GET /reports/training-trends`
- [ ] Implementar router `POST /reports/refresh-training-performance`
- [ ] Criar testes de integração
- [ ] Documentar em OpenAPI: `/api/v1/docs`
- [ ] Validar permissões (R26: coordenador, treinador)

---

## R2: Relatório Individual de Atleta (Treinos)

**Descrição:** Relatório personalizado com métricas de prontidão, carga, presença e avaliações por atleta.

**Regras RAG:**
- **R12**: Atleta é papel permanente no histórico
- **R13/R14**: Estados (ativa, lesionada, dispensada) e impactos
- **RP4**: Escopo da participação (jogos, treinos, atividades extras)
- **RP5**: Ausência gera carga = 0
- **RP6**: Participação gera métricas obrigatórias

### 2.1 - Dados Disponíveis

**Tabelas:**
```sql
athletes (id, person_id, full_name, nickname, birth_date, position, state)
athlete_states (id, athlete_id, state, reason, started_at, ended_at)
attendance (id, session_id, athlete_id, status)
wellness_pre (id, session_id, athlete_id, sleep_hours, sleep_quality, fatigue, stress, muscle_soreness, pain, pain_level)
wellness_post (id, session_id, athlete_id, minutes, rpe, internal_load, fatigue_after, mood_after)
medical_cases (id, athlete_id, status, reason, started_at, ended_at)
team_registrations (id, athlete_id, season_id, category_id, team_id)
```

### 2.2 - Materialized View (Atleta Individual)

**Arquivo:** `backend/db/migrations/create_mv_athlete_training_summary.sql`

```python
"""create_mv_athlete_training_summary

Revision ID: a001b002c003
Revises: 4af09f9d46a0
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Cria materialized view para resumo individual de atleta em treinos"""

    op.execute(sa.text("""
    -- ============================================================================
    -- MATERIALIZED VIEW: Resumo Individual de Atleta em Treinos
    -- Referências: R12, R13, R14, RP4, RP5, RP6
    -- ============================================================================

    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_athlete_training_summary AS
    WITH athlete_sessions AS (
        -- Listar todas as participações da atleta em treinos
        SELECT
            a.id AS athlete_id,
            a.person_id,
            a.full_name,
            a.nickname,
            a.birth_date,
            a.position,
            a.state AS current_state,
            a.organization_id,

            ts.id AS session_id,
            ts.season_id,
            ts.team_id,
            ts.session_at,

            att.status AS attendance_status,

            -- Wellness pré-treino
            wpre.sleep_hours,
            wpre.sleep_quality,
            wpre.fatigue AS fatigue_pre,
            wpre.stress,
            wpre.muscle_soreness,
            wpre.pain,
            wpre.pain_level,

            -- Wellness pós-treino
            wpst.minutes,
            wpst.rpe,
            wpst.internal_load,
            wpst.fatigue_after,
            wpst.mood_after

        FROM athletes a
        LEFT JOIN attendance att ON att.athlete_id = a.id
        LEFT JOIN training_sessions ts ON ts.id = att.session_id
        LEFT JOIN wellness_pre wpre ON wpre.session_id = ts.id AND wpre.athlete_id = a.id
        LEFT JOIN wellness_post wpst ON wpst.session_id = ts.id AND wpst.athlete_id = a.id
        WHERE a.deleted_at IS NULL  -- Soft delete (RDB4)
          AND ts.deleted_at IS NULL
    ),
    athlete_aggregates AS (
        -- Agregar métricas por atleta
        SELECT
            athlete_id,
            person_id,
            full_name,
            nickname,
            birth_date,
            position,
            current_state,
            organization_id,

            -- Última temporada/equipe
            (
                SELECT tr.season_id
                FROM team_registrations tr
                WHERE tr.athlete_id = asess.athlete_id
                ORDER BY tr.created_at DESC
                LIMIT 1
            ) AS current_season_id,
            (
                SELECT tr.team_id
                FROM team_registrations tr
                WHERE tr.athlete_id = asess.athlete_id
                ORDER BY tr.created_at DESC
                LIMIT 1
            ) AS current_team_id,

            -- Contadores de presença (RP5)
            COUNT(DISTINCT session_id) AS total_sessions,
            COUNT(*) FILTER (WHERE attendance_status = 'presente') AS sessions_presente,
            COUNT(*) FILTER (WHERE attendance_status = 'ausente') AS sessions_ausente,
            COUNT(*) FILTER (WHERE attendance_status = 'medico') AS sessions_dm,
            COUNT(*) FILTER (WHERE attendance_status = 'lesionada') AS sessions_lesionada,

            -- Taxa de assiduidade (%)
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE attendance_status = 'presente') /
                NULLIF(COUNT(DISTINCT session_id), 0),
                2
            ) AS attendance_rate,

            -- Carga média (RP6)
            ROUND(AVG(internal_load) FILTER (WHERE attendance_status = 'presente'), 0) AS avg_internal_load,
            ROUND(AVG(rpe) FILTER (WHERE attendance_status = 'presente'), 1) AS avg_rpe,
            ROUND(AVG(minutes) FILTER (WHERE attendance_status = 'presente'), 1) AS avg_minutes,

            -- Carga acumulada (últimos 7 dias)
            ROUND(
                SUM(internal_load) FILTER (
                    WHERE attendance_status = 'presente'
                      AND session_at >= current_date - interval '7 days'
                ),
                0
            ) AS load_7d,

            -- Carga acumulada (últimos 28 dias)
            ROUND(
                SUM(internal_load) FILTER (
                    WHERE attendance_status = 'presente'
                      AND session_at >= current_date - interval '28 days'
                ),
                0
            ) AS load_28d,

            -- Wellness médio (pré-treino)
            ROUND(AVG(sleep_hours), 1) AS avg_sleep_hours,
            ROUND(AVG(sleep_quality), 1) AS avg_sleep_quality,
            ROUND(AVG(fatigue_pre), 1) AS avg_fatigue_pre,
            ROUND(AVG(stress), 1) AS avg_stress,
            ROUND(AVG(muscle_soreness), 1) AS avg_muscle_soreness,

            -- Wellness médio (pós-treino)
            ROUND(AVG(fatigue_after), 1) AS avg_fatigue_after,
            ROUND(AVG(mood_after), 1) AS avg_mood_after,

            -- Últimos registros (para detecção de anomalias)
            (
                SELECT sleep_hours
                FROM athlete_sessions last_sess
                WHERE last_sess.athlete_id = asess.athlete_id
                  AND last_sess.sleep_hours IS NOT NULL
                ORDER BY last_sess.session_at DESC
                LIMIT 1
            ) AS last_sleep_hours,
            (
                SELECT fatigue_pre
                FROM athlete_sessions last_sess
                WHERE last_sess.athlete_id = asess.athlete_id
                  AND last_sess.fatigue_pre IS NOT NULL
                ORDER BY last_sess.session_at DESC
                LIMIT 1
            ) AS last_fatigue,
            (
                SELECT internal_load
                FROM athlete_sessions last_sess
                WHERE last_sess.athlete_id = asess.athlete_id
                  AND last_sess.internal_load IS NOT NULL
                ORDER BY last_sess.session_at DESC
                LIMIT 1
            ) AS last_internal_load,

            -- Data do último treino
            MAX(session_at) AS last_session_at

        FROM athlete_sessions asess
        GROUP BY athlete_id, person_id, full_name, nickname, birth_date, position, current_state, organization_id
    )
    SELECT
        aa.*,

        -- Estado médico ativo (R13, R14)
        (
            SELECT COUNT(*)
            FROM medical_cases mc
            WHERE mc.athlete_id = aa.athlete_id
              AND mc.status = 'ativo'
        ) AS active_medical_cases,

        -- Idade esportiva atual (RD1)
        DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int AS current_age,

        -- Categoria esperada (calculada, RD2)
        (
            SELECT c.code
            FROM categories c
            WHERE DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int >= c.min_age
              AND (c.max_age IS NULL OR DATE_PART('year', AGE(CURRENT_DATE, aa.birth_date))::int <= c.max_age)
            ORDER BY c.min_age DESC
            LIMIT 1
        ) AS expected_category_code

    FROM athlete_aggregates aa;

    -- Índices para performance
    CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_athlete
        ON mv_athlete_training_summary(athlete_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_org
        ON mv_athlete_training_summary(organization_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_season
        ON mv_athlete_training_summary(current_season_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_team
        ON mv_athlete_training_summary(current_team_id);
    CREATE INDEX IF NOT EXISTS idx_mv_athlete_training_summary_state
        ON mv_athlete_training_summary(current_state);

    -- Documentação
    COMMENT ON MATERIALIZED VIEW mv_athlete_training_summary IS
    'Resumo individual de atleta em treinos (R12, R13, R14, RP4, RP5, RP6).
    Atualizar via REFRESH MATERIALIZED VIEW CONCURRENTLY mv_athlete_training_summary.';
    """))


def downgrade() -> None:
    """Remove materialized view"""
    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS mv_athlete_training_summary CASCADE"))
```

### 2.3 - Schema Pydantic (Atleta Individual)

**Arquivo:** `backend/app/schemas/reports/athlete.py`

```python
"""
Schemas para relatórios individuais de atleta

Referências RAG:
- R12: Atleta permanente no histórico
- R13/R14: Estados e impactos
- RP4: Escopo de participação
- RP5: Ausência = carga 0
- RP6: Participação = métricas obrigatórias
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class AthleteReadinessMetrics(BaseModel):
    """Métricas de prontidão (wellness pré-treino)"""

    avg_sleep_hours: Optional[float] = Field(None, description="Média de horas de sono")
    avg_sleep_quality: Optional[float] = Field(None, ge=1, le=5, description="Qualidade média de sono (1-5)")
    avg_fatigue_pre: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pré-treino (0-10)")
    avg_stress: Optional[float] = Field(None, ge=0, le=10, description="Estresse médio (0-10)")
    avg_muscle_soreness: Optional[float] = Field(None, ge=0, le=10, description="Dor muscular média (0-10)")

    last_sleep_hours: Optional[float] = None
    last_fatigue: Optional[float] = None


class AthleteTrainingLoadMetrics(BaseModel):
    """Métricas de carga de treino (RP6)"""

    avg_internal_load: Optional[float] = Field(None, description="Carga interna média (RPE × minutos)")
    avg_rpe: Optional[float] = Field(None, ge=0, le=10, description="RPE médio (0-10)")
    avg_minutes: Optional[float] = Field(None, description="Minutos médios por treino")

    load_7d: Optional[float] = Field(None, description="Carga acumulada (7 dias)")
    load_28d: Optional[float] = Field(None, description="Carga acumulada (28 dias)")

    last_internal_load: Optional[float] = None


class AthleteAttendanceMetrics(BaseModel):
    """Métricas de presença (RP5)"""

    total_sessions: int = Field(..., description="Total de treinos")
    sessions_presente: int = Field(..., description="Treinos presentes")
    sessions_ausente: int = Field(..., description="Treinos ausentes (RP5: carga = 0)")
    sessions_dm: int = Field(..., description="Treinos em DM")
    sessions_lesionada: int = Field(..., description="Treinos lesionada (R13)")
    attendance_rate: float = Field(..., description="Taxa de assiduidade (%)")


class AthleteWellnessMetrics(BaseModel):
    """Métricas de bem-estar pós-treino"""

    avg_fatigue_after: Optional[float] = Field(None, ge=0, le=10, description="Fadiga média pós-treino")
    avg_mood_after: Optional[float] = Field(None, ge=0, le=10, description="Humor médio pós-treino")


class AthleteIndividualReport(BaseModel):
    """Relatório individual completo de atleta (R12, R13, R14)"""

    # Identificação
    athlete_id: UUID
    person_id: UUID
    full_name: str
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    position: Optional[str] = None
    current_age: Optional[int] = None
    expected_category_code: Optional[str] = None

    # Contexto atual
    current_state: str = Field(..., description="Estado atual (R13: ativa, lesionada, dispensada)")
    current_season_id: Optional[UUID] = None
    current_team_id: Optional[UUID] = None
    organization_id: UUID

    # Métricas
    readiness: AthleteReadinessMetrics
    training_load: AthleteTrainingLoadMetrics
    attendance: AthleteAttendanceMetrics
    wellness: AthleteWellnessMetrics

    # Médico
    active_medical_cases: int = Field(..., description="Casos médicos ativos (R13)")

    # Última atividade
    last_session_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AthleteIndividualFilters(BaseModel):
    """Filtros para busca de relatórios individuais"""

    organization_id: UUID
    season_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    state: Optional[str] = Field(None, regex="^(ativa|lesionada|dispensada)$")
    min_attendance_rate: Optional[float] = Field(None, ge=0, le=100)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)
```

### 2.4 - Service Layer (Atleta Individual)

**Arquivo:** `backend/app/services/reports/athlete_report_service.py`

```python
"""
Service para relatórios individuais de atleta

Referências RAG:
- R12: Atleta permanente
- R13/R14: Estados e impactos
- RP4: Escopo de participação
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.schemas.reports.athlete import (
    AthleteIndividualReport,
    AthleteReadinessMetrics,
    AthleteTrainingLoadMetrics,
    AthleteAttendanceMetrics,
    AthleteWellnessMetrics,
    AthleteIndividualFilters
)


class AthleteReportService:
    """Service para relatórios individuais de atleta"""

    @staticmethod
    def get_athlete_report(
        db: Session,
        athlete_id: UUID
    ) -> Optional[AthleteIndividualReport]:
        """
        Retorna relatório individual de uma atleta

        Referências:
        - R12: Atleta permanente no histórico
        - R13/R14: Estados e seus impactos
        - RP4: Escopo da participação

        Args:
            db: Sessão do banco
            athlete_id: ID da atleta

        Returns:
            AthleteIndividualReport ou None
        """
        query = text("""
            SELECT * FROM mv_athlete_training_summary
            WHERE athlete_id = :athlete_id
        """)

        result = db.execute(query, {"athlete_id": str(athlete_id)}).fetchone()

        if not result:
            return None

        # Construir métricas
        readiness = AthleteReadinessMetrics(
            avg_sleep_hours=result.avg_sleep_hours,
            avg_sleep_quality=result.avg_sleep_quality,
            avg_fatigue_pre=result.avg_fatigue_pre,
            avg_stress=result.avg_stress,
            avg_muscle_soreness=result.avg_muscle_soreness,
            last_sleep_hours=result.last_sleep_hours,
            last_fatigue=result.last_fatigue
        )

        training_load = AthleteTrainingLoadMetrics(
            avg_internal_load=result.avg_internal_load,
            avg_rpe=result.avg_rpe,
            avg_minutes=result.avg_minutes,
            load_7d=result.load_7d,
            load_28d=result.load_28d,
            last_internal_load=result.last_internal_load
        )

        attendance = AthleteAttendanceMetrics(
            total_sessions=result.total_sessions,
            sessions_presente=result.sessions_presente,
            sessions_ausente=result.sessions_ausente,
            sessions_dm=result.sessions_dm,
            sessions_lesionada=result.sessions_lesionada,
            attendance_rate=result.attendance_rate
        )

        wellness = AthleteWellnessMetrics(
            avg_fatigue_after=result.avg_fatigue_after,
            avg_mood_after=result.avg_mood_after
        )

        # Construir relatório
        report = AthleteIndividualReport(
            athlete_id=result.athlete_id,
            person_id=result.person_id,
            full_name=result.full_name,
            nickname=result.nickname,
            birth_date=result.birth_date,
            position=result.position,
            current_age=result.current_age,
            expected_category_code=result.expected_category_code,
            current_state=result.current_state,
            current_season_id=result.current_season_id,
            current_team_id=result.current_team_id,
            organization_id=result.organization_id,
            readiness=readiness,
            training_load=training_load,
            attendance=attendance,
            wellness=wellness,
            active_medical_cases=result.active_medical_cases,
            last_session_at=result.last_session_at
        )

        return report

    @staticmethod
    def list_athlete_reports(
        db: Session,
        filters: AthleteIndividualFilters
    ) -> list[AthleteIndividualReport]:
        """
        Lista relatórios individuais de atletas com filtros

        Args:
            db: Sessão
            filters: Filtros de busca

        Returns:
            Lista de AthleteIndividualReport
        """
        query = text("""
            SELECT * FROM mv_athlete_training_summary
            WHERE organization_id = :org_id
              AND (:season_id IS NULL OR current_season_id = :season_id)
              AND (:team_id IS NULL OR current_team_id = :team_id)
              AND (:state IS NULL OR current_state = :state)
              AND (:min_attendance IS NULL OR attendance_rate >= :min_attendance)
            ORDER BY full_name
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(query, {
            "org_id": str(filters.organization_id),
            "season_id": str(filters.season_id) if filters.season_id else None,
            "team_id": str(filters.team_id) if filters.team_id else None,
            "state": filters.state,
            "min_attendance": filters.min_attendance_rate,
            "skip": filters.skip,
            "limit": filters.limit
        })

        reports = []
        for row in result:
            # Reutilizar lógica de get_athlete_report
            readiness = AthleteReadinessMetrics(
                avg_sleep_hours=row.avg_sleep_hours,
                avg_sleep_quality=row.avg_sleep_quality,
                avg_fatigue_pre=row.avg_fatigue_pre,
                avg_stress=row.avg_stress,
                avg_muscle_soreness=row.avg_muscle_soreness,
                last_sleep_hours=row.last_sleep_hours,
                last_fatigue=row.last_fatigue
            )

            training_load = AthleteTrainingLoadMetrics(
                avg_internal_load=row.avg_internal_load,
                avg_rpe=row.avg_rpe,
                avg_minutes=row.avg_minutes,
                load_7d=row.load_7d,
                load_28d=row.load_28d,
                last_internal_load=row.last_internal_load
            )

            attendance = AthleteAttendanceMetrics(
                total_sessions=row.total_sessions,
                sessions_presente=row.sessions_presente,
                sessions_ausente=row.sessions_ausente,
                sessions_dm=row.sessions_dm,
                sessions_lesionada=row.sessions_lesionada,
                attendance_rate=row.attendance_rate
            )

            wellness = AthleteWellnessMetrics(
                avg_fatigue_after=row.avg_fatigue_after,
                avg_mood_after=row.avg_mood_after
            )

            report = AthleteIndividualReport(
                athlete_id=row.athlete_id,
                person_id=row.person_id,
                full_name=row.full_name,
                nickname=row.nickname,
                birth_date=row.birth_date,
                position=row.position,
                current_age=row.current_age,
                expected_category_code=row.expected_category_code,
                current_state=row.current_state,
                current_season_id=row.current_season_id,
                current_team_id=row.current_team_id,
                organization_id=row.organization_id,
                readiness=readiness,
                training_load=training_load,
                attendance=attendance,
                wellness=wellness,
                active_medical_cases=row.active_medical_cases,
                last_session_at=row.last_session_at
            )
            reports.append(report)

        return reports
```

---

## 📄 APÊNDICES

### A. Checklist Geral de Implementação

**Para cada relatório:**

1. **Database Layer:**
   - [ ] Criar migration para materialized view
   - [ ] Validar índices de performance
   - [ ] Documentar com `COMMENT ON`
   - [ ] Testar query de agregação

2. **Backend Layer:**
   - [ ] Implementar schemas Pydantic
   - [ ] Implementar service layer
   - [ ] Implementar router FastAPI
   - [ ] Validar permissões (R26)
   - [ ] Implementar endpoint de refresh

3. **Testes:**
   - [ ] Teste unitário de schemas
   - [ ] Teste unitário de service
   - [ ] Teste de integração de endpoint
   - [ ] Teste de permissões

4. **Documentação:**
   - [ ] OpenAPI atualizado
   - [ ] Exemplos de request/response
   - [ ] Referências RAG nos comentários

### B. Performance Guidelines

**Materialized Views:**
- Refresh diário via cronjob (02:00 UTC)
- Refresh on-demand via endpoint (apenas coordenador)
- Usar `CONCURRENTLY` para não bloquear leituras
- Monitorar tamanho da view (alertar se > 1GB)

**Queries:**
- Sempre usar `WHERE deleted_at IS NULL` (soft delete)
- Limitar resultados com `LIMIT` obrigatório
- Usar `EXPLAIN ANALYZE` para validar plano de execução
- Índices devem cobrir 90%+ das queries

### C. Estrutura de Diretórios Final

```
backend/
├── app/
│   ├── schemas/
│   │   └── reports/
│   │       ├── __init__.py
│   │       ├── training.py       # R1
│   │       ├── athlete.py        # R2
│   │       ├── wellness.py       # R3
│   │       ├── medical.py        # R4
│   │       ├── match.py          # R5
│   │       └── team.py           # R6
│   ├── services/
│   │   └── reports/
│   │       ├── __init__.py
│   │       ├── training_report_service.py
│   │       ├── athlete_report_service.py
│   │       ├── wellness_report_service.py
│   │       ├── medical_report_service.py
│   │       ├── match_report_service.py
│   │       └── team_report_service.py
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           └── reports.py    # Todos os endpoints
│   └── tests/
│       └── integration/
│           └── reports/
│               ├── test_training_reports.py
│               ├── test_athlete_reports.py
│               └── ...
└── db/
    └── migrations/
        └── reports/
            ├── create_mv_training_performance.py
            ├── create_mv_athlete_training_summary.py
            └── ...
```

---

**FIM DO MANUAL DE RELATÓRIOS - PARTE 1**

**Próximos passos:**
1. Implementar R1 (Relatório de Performance em Treinos)
2. Implementar R2 (Relatório Individual de Atleta)
3. Implementar R3 (Prontidão e Bem-Estar)
4. Implementar R4 (Gerenciamento de Lesões)
5. Documentar limitações de R5 e R6
6. Especificar extensões necessárias para GRUPO 3
