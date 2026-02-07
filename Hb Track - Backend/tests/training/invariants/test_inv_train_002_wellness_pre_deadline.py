"""
INV-TRAIN-002: Deadline Wellness Pré (até 2h antes da sessão)

Regra: wellness_pre é bloqueado se NOW > session_at - 2h.

Evidência:
- wellness_pre_service.py:93-102 (_check_edit_window)
- wellness_pre_service.py:231-232 (uso com ValidationError)

Obrigação A: Analisei o schema.sql (linhas 2870-2888). Para criar o payload mínimo, identifico:
  1. FK Obrigatória: organization_id (Âncora: wellness_pre.organization_id FK). Usarei fixture organization.
  2. FK Obrigatória: training_session_id (Âncora: wellness_pre.training_session_id FK). Usarei fixture training_session.
  3. FK Obrigatória: athlete_id (Âncora: wellness_pre.athlete_id FK). Usarei fixture athlete.
  4. FK Obrigatória: created_by_user_id (Âncora: wellness_pre.created_by_user_id FK). Usarei fixture user.
  5. NOT NULL: sleep_hours (Âncora: wellness_pre.sleep_hours NOT NULL). Usarei 8.0.
  6. NOT NULL: sleep_quality (Âncora: wellness_pre.sleep_quality NOT NULL). Usarei 3.
  7. NOT NULL: fatigue_pre (Âncora: wellness_pre.fatigue_pre NOT NULL). Usarei 3.
  8. NOT NULL: stress_level (Âncora: wellness_pre.stress_level NOT NULL). Usarei 3.
  9. NOT NULL: muscle_soreness (Âncora: wellness_pre.muscle_soreness NOT NULL). Usarei 3.
  O resto será omitido.

Obrigação B: Invariante alvo: validação de janela temporal (Service C2).
  * Exception Esperada: ValidationError (app.core.exceptions).
  * SQLSTATE: N/A (Classe C2 = Service validation, não DB constraint).
  * Mensagem: "Fora da janela de edição".
  * Fonte: wellness_pre_service.py:232
  * Estratégia: Integration test com async_db, pytest.raises(ValidationError).
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.models.training_session import TrainingSession
from app.services.wellness_pre_service import WellnessPreService


class TestInvTrain002WellnessPreDeadline:
    """
    Classe: C2 (Service com DB)
    Prova primária: Integration Test com ValidationError
    """

    @pytest.mark.asyncio
    async def test_valid_case__within_edit_window(
        self,
        async_db: AsyncSession,
        organization,
        team,
        user,
        athlete,
        team_membership,
    ):
        """Criação de wellness_pre dentro da janela (>2h antes) deve ser aceita."""
        # Criar sessão 3 horas no futuro (dentro da janela)
        session = TrainingSession(
            id=uuid4(),
            organization_id=UUID(str(organization.id)),
            team_id=UUID(str(team.id)),
            session_at=datetime.now(timezone.utc) + timedelta(hours=3),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste INV-002 válido",
            location="Ginásio",
            status="draft",
            created_by_user_id=UUID(str(user.id)),
        )
        async_db.add(session)
        await async_db.flush()

        # Criar wellness_pre via service (deve passar)
        service = WellnessPreService(async_db)
        
        wellness_data = {
            "sleep_hours": 8.0,
            "sleep_quality": 3,
            "fatigue_pre": 3,
            "stress_level": 3,
            "muscle_soreness": 3,
        }
        
        wellness = await service.submit_wellness_pre(
            session_id=session.id,
            athlete_id=UUID(str(athlete.id)),
            data=wellness_data,
            user_id=UUID(str(user.id)),
            user_role="coach",
        )
        
        # Se chegou aqui sem exceção, passou
        assert wellness.id is not None

    @pytest.mark.asyncio
    async def test_invalid_case_1__outside_edit_window(
        self,
        async_db: AsyncSession,
        organization,
        team,
        user,
        athlete,
        team_membership,
    ):
        """Criação de wellness_pre fora da janela (<2h antes) deve ser rejeitada."""
        # Criar sessão 1 hora no futuro (fora da janela - menos de 2h)
        session = TrainingSession(
            id=uuid4(),
            organization_id=UUID(str(organization.id)),
            team_id=UUID(str(team.id)),
            session_at=datetime.now(timezone.utc) + timedelta(hours=1),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste INV-002 inválido",
            location="Ginásio",
            status="draft",
            created_by_user_id=UUID(str(user.id)),
        )
        async_db.add(session)
        await async_db.flush()

        # Tentar criar wellness_pre via service (deve falhar)
        service = WellnessPreService(async_db)
        
        wellness_data = {
            "sleep_hours": 8.0,
            "sleep_quality": 3,
            "fatigue_pre": 3,
            "stress_level": 3,
            "muscle_soreness": 3,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await service.submit_wellness_pre(
                session_id=session.id,
                athlete_id=UUID(str(athlete.id)),
                data=wellness_data,
                user_id=UUID(str(user.id)),
                user_role="coach",
            )
        
        # Validar mensagem da exception (classe C2 não tem SQLSTATE)
        assert "Fora da janela de edição" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_case_2__session_already_past(
        self,
        async_db: AsyncSession,
        organization,
        team,
        user,
        athlete,
        team_membership,
    ):
        """Criação de wellness_pre para sessão já passada deve ser rejeitada."""
        # Criar sessão 1 hora no passado
        session = TrainingSession(
            id=uuid4(),
            organization_id=UUID(str(organization.id)),
            team_id=UUID(str(team.id)),
            session_at=datetime.now(timezone.utc) - timedelta(hours=1),
            duration_planned_minutes=90,
            session_type="quadra",
            main_objective="Teste INV-002 passado",
            location="Ginásio",
            status="readonly",
            created_by_user_id=UUID(str(user.id)),
        )
        async_db.add(session)
        await async_db.flush()

        # Tentar criar wellness_pre via service (deve falhar)
        service = WellnessPreService(async_db)
        
        wellness_data = {
            "sleep_hours": 8.0,
            "sleep_quality": 3,
            "fatigue_pre": 3,
            "stress_level": 3,
            "muscle_soreness": 3,
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await service.submit_wellness_pre(
                session_id=session.id,
                athlete_id=UUID(str(athlete.id)),
                data=wellness_data,
                user_id=UUID(str(user.id)),
                user_role="coach",
            )
        
        # Validar mensagem da exception (classe C2 não tem SQLSTATE)
        assert "Fora da janela de edição" in str(exc_info.value)
