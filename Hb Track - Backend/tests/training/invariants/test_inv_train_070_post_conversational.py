"""
INV-TRAIN-070: post_training_conversational
Classe B — Runtime Integration com async_db
Evidencia: docs/ssot/schema.sql — wellness_post.conversational_feedback (linha 3039),
           wellness_post.conversation_completed DEFAULT false (linha 3040)
           AR_157: adicionou campos conversational_feedback + conversation_completed
Tabelas: wellness_post (conversational_feedback text nullable, conversation_completed boolean)
Regra: Pós-treino aceita input conversacional (conversational_feedback) sem formulário
       rígido. Os campos numéricos (session_rpe, fatigue_after, mood_after) continuam
       sendo os únicos NOT NULL — todos os outros incluindo conversational_feedback
       são opcionais, viabilizando fluxo conversacional.
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestInvTrain070:
    """
    INV-TRAIN-070 — pós-treino conversacional sem formulário rígido.
    conversational_feedback é nullable e opcional, complementar ao RPE.
    Evidencia: docs/ssot/schema.sql — wellness_post.conversational_feedback,
               AR_157 (conversational_feedback adicionado).
    """

    @pytest.mark.asyncio
    async def test_wellness_post_with_conversational_feedback(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        organization,
        user,
    ):
        """
        wellness_post aceita conversational_feedback preenchido junto com
        os campos obrigatórios mínimos. Viabiliza o fluxo conversacional pós-treino.
        """
        wp_id = str(uuid4())
        feedback_text = (
            "Senti a perna pesada hoje, mas consegui completar os exercícios. "
            "O treino de quadra foi intenso. Preciso descansar mais."
        )
        await async_db.execute(text("""
            INSERT INTO wellness_post
              (id, organization_id, training_session_id, athlete_id,
               session_rpe, fatigue_after, mood_after,
               conversational_feedback, conversation_completed,
               created_by_user_id)
            VALUES
              (:id, :org_id, :session_id, :athlete_id,
               7, 6, 7,
               :feedback, false,
               :user_id)
        """), {
            "id": wp_id,
            "org_id": str(organization.id),
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
            "feedback": feedback_text,
            "user_id": str(user.id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT conversational_feedback, conversation_completed FROM wellness_post WHERE id = :id"),
            {"id": wp_id},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == feedback_text, (
            "INV-070: conversational_feedback deve ser armazenado sem modificação"
        )
        assert row[1] is False, (
            "INV-070: conversation_completed=false indica fluxo em andamento"
        )

    @pytest.mark.asyncio
    async def test_wellness_post_minimal_without_conversational_feedback(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        organization,
        user,
    ):
        """
        wellness_post aceita inserção sem conversational_feedback (NULL).
        O fluxo conversacional é opcional — os campos obrigatórios são apenas
        session_rpe, fatigue_after e mood_after.
        """
        wp_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO wellness_post
              (id, organization_id, training_session_id, athlete_id,
               session_rpe, fatigue_after, mood_after,
               created_by_user_id)
            VALUES
              (:id, :org_id, :session_id, :athlete_id, 5, 4, 8, :user_id)
        """), {
            "id": wp_id,
            "org_id": str(organization.id),
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT conversational_feedback, conversation_completed FROM wellness_post WHERE id = :id"),
            {"id": wp_id},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] is None, "INV-070: conversational_feedback é nullable (sem fluxo conversacional)"
        assert row[1] is False, "INV-070: conversation_completed default é false"

    @pytest.mark.asyncio
    async def test_conversation_completed_flag_updatable(
        self,
        async_db: AsyncSession,
        training_session,
        athlete,
        organization,
        user,
    ):
        """
        conversation_completed pode ser atualizado para True quando o fluxo
        conversacional é completado. Confirma que o campo é mutável.
        """
        wp_id = str(uuid4())
        await async_db.execute(text("""
            INSERT INTO wellness_post
              (id, organization_id, training_session_id, athlete_id,
               session_rpe, fatigue_after, mood_after,
               conversational_feedback, created_by_user_id)
            VALUES
              (:id, :org_id, :session_id, :athlete_id, 8, 7, 6,
               'Treino foi bom, senti evolução', :user_id)
        """), {
            "id": wp_id,
            "org_id": str(organization.id),
            "session_id": str(training_session.id),
            "athlete_id": str(athlete.person_id),
            "user_id": str(user.id),
        })
        await async_db.flush()

        # Marcar fluxo conversacional como completo
        await async_db.execute(text("""
            UPDATE wellness_post SET conversation_completed = true WHERE id = :id
        """), {"id": wp_id})
        await async_db.flush()

        result = await async_db.execute(
            text("SELECT conversation_completed FROM wellness_post WHERE id = :id"),
            {"id": wp_id},
        )
        row = result.fetchone()
        assert row[0] is True, "INV-070: conversation_completed pode ser marcado como true"
