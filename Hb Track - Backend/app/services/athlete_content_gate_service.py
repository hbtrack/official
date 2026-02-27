"""
Service de gate de conteúdo para atletas baseado em wellness obrigatório.

Implementa as invariantes:
- INV-076: has_completed_daily_wellness — verificação de wellness diário
- INV-071: check_content_access — gate de conteúdo por wellness
- INV-078: check_progress_access — gate de telas de progresso/relatório

Regras:
- wellness_pre: verificada pelo campo filled_at (DATE = today) para a sessão do dia
- wellness_post: verificada pelo último treino concluído (training_sessions.closed_at IS NOT NULL)
- allows_minimum=True: atleta vê conteúdo mínimo (ex: horário do próximo treino)
  mesmo sem wellness completo, mas NÃO vê conteúdo completo.

Âncoras canônicas:
- docs/ssot/schema.sql — wellness_pre (linha 3080), wellness_post (linha 3016)
- docs/ssot/schema.sql — training_sessions.closed_at (linha 2820)
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.training_session import TrainingSession


# ---------------------------------------------------------------------------
# Tipos de retorno (INV-071, INV-078)
# ---------------------------------------------------------------------------

@dataclass
class AccessGranted:
    """Atleta completou wellness obrigatório — acesso total liberado."""
    reason: str = "wellness_complete"


@dataclass
class AccessGated:
    """
    Atleta NÃO completou wellness obrigatório.

    allows_minimum=True  → pode ver conteúdo mínimo (horário do próximo treino, etc.)
    allows_minimum=False → acesso completamente bloqueado (ex: telas de progresso)
    """
    reason: str = "wellness_missing"
    allows_minimum: bool = True
    missing_items: List[str] = field(default_factory=list)


# Tipo de retorno union
AccessResult = AccessGranted | AccessGated


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AthleteContentGateService:
    """
    Gate de conteúdo para atletas baseado em wellness diário obrigatório.

    INV-076: has_completed_daily_wellness
    INV-071: check_content_access
    INV-078: check_progress_access
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # -----------------------------------------------------------------------
    # INV-076: Verificação de wellness diário
    # -----------------------------------------------------------------------

    async def has_completed_daily_wellness(
        self,
        athlete_id: UUID,
        ref_date: Optional[date] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Verifica se o atleta completou o wellness diário obrigatório.

        Critérios:
        1. wellness_pre submetida para hoje (ref_date, default=hoje UTC)
        2. wellness_post submetida para o último treino concluído
           (training_sessions.closed_at IS NOT NULL mais recente)

        Retorna:
            (True, []) se tudo completo
            (False, list_of_missing) com os itens faltantes para exibição na UI

        Âncoras:
        - wellness_pre.filled_at (timestamp TZ) — DATE extraído via func.date()
        - wellness_post.training_session_id → training_sessions.closed_at IS NOT NULL
        """
        if ref_date is None:
            ref_date = datetime.now(timezone.utc).date()

        missing: List[str] = []

        # --- 1. wellness_pre de hoje ---
        pre_stmt = (
            select(func.count())
            .select_from(WellnessPre)
            .where(
                and_(
                    WellnessPre.athlete_id == athlete_id,
                    WellnessPre.deleted_at.is_(None),
                    func.date(WellnessPre.filled_at) == ref_date,
                )
            )
        )
        pre_result = await self.db.execute(pre_stmt)
        pre_count = pre_result.scalar() or 0

        if pre_count == 0:
            missing.append("wellness_pre_hoje")

        # --- 2. wellness_post do último treino concluído ---
        # Encontrar o training_session mais recente com closed_at IS NOT NULL
        # onde o atleta tem wellness_post vinculado
        last_closed_stmt = (
            select(TrainingSession.id)
            .where(
                and_(
                    TrainingSession.closed_at.is_not(None),
                    TrainingSession.deleted_at.is_(None)
                    if hasattr(TrainingSession, "deleted_at")
                    else True,
                )
            )
            .order_by(TrainingSession.closed_at.desc())
            .limit(1)
        )
        closed_result = await self.db.execute(last_closed_stmt)
        last_closed_session_id = closed_result.scalar()

        if last_closed_session_id is not None:
            post_stmt = (
                select(func.count())
                .select_from(WellnessPost)
                .where(
                    and_(
                        WellnessPost.athlete_id == athlete_id,
                        WellnessPost.training_session_id == last_closed_session_id,
                        WellnessPost.deleted_at.is_(None),
                    )
                )
            )
            post_result = await self.db.execute(post_stmt)
            post_count = post_result.scalar() or 0

            if post_count == 0:
                missing.append("wellness_post_ultimo_treino")

        completed = len(missing) == 0
        return completed, missing

    # -----------------------------------------------------------------------
    # INV-071: Gate de conteúdo geral
    # -----------------------------------------------------------------------

    async def check_content_access(
        self,
        athlete_id: UUID,
        resource_type: str = "default",
        ref_date: Optional[date] = None,
    ) -> AccessResult:
        """
        Verifica se o atleta pode acessar conteúdo completo.

        Se wellness NÃO está completo:
            → AccessGated(reason='wellness_missing', allows_minimum=True)
              'allows_minimum=True' = atleta vê conteúdo mínimo
              (ex: horário do próximo treino) mas NÃO conteúdo completo

        Se wellness está completo:
            → AccessGranted()

        Parâmetros:
            resource_type: tipo de recurso solicitado (para logging futuro)
            ref_date: data de referência (default: hoje UTC)

        Âncora: INV-071 — docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md
        """
        completed, missing = await self.has_completed_daily_wellness(
            athlete_id=athlete_id,
            ref_date=ref_date,
        )

        if completed:
            return AccessGranted()

        return AccessGated(
            reason="wellness_missing",
            allows_minimum=True,
            missing_items=missing,
        )

    # -----------------------------------------------------------------------
    # INV-078: Gate de telas de progresso/relatório
    # -----------------------------------------------------------------------

    async def check_progress_access(
        self,
        athlete_id: UUID,
        ref_date: Optional[date] = None,
    ) -> AccessResult:
        """
        Verifica se o atleta pode acessar telas de progresso e relatórios.

        Telas de progresso são mais restritas que conteúdo geral:
        se wellness não está em dia → AccessGated (sem allows_minimum relevante
        para progresso — UI decide como interpretar).

        Se wellness em dia → AccessGranted().

        Âncora: INV-078 — docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md
        """
        completed, missing = await self.has_completed_daily_wellness(
            athlete_id=athlete_id,
            ref_date=ref_date,
        )

        if completed:
            return AccessGranted()

        return AccessGated(
            reason="wellness_missing",
            allows_minimum=False,  # progresso: sem acesso mínimo — tela completamente bloqueada
            missing_items=missing,
        )
