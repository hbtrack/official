"""
INV-TRAIN-055 — meso_overlap_allowed

POLICY TEST (Classe C1/B) — Testa que mesociclos de equipes diferentes
com datas sobrepostas NAO geram conflito (ausencia de constraint de non-overlap).

Anti-false-positive: inserir 2 mesos de orgs/teams diferentes com datas sobrepostas
e verificar que AMBOS existem no DB apos flush.

Evidencia:
- app/services/training_cycle_service.py (comentario INV-055 L44-46)
- schema.sql: training_cycles nao tem unique constraint em (team_id, date_range)
- INV-055: overlap entre mesociclos de EQUIPES DIFERENTES eh permitido por design
"""
import pytest
import pytest_asyncio
from datetime import date, datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training_cycle import TrainingCycle


class TestInvTrain055:
    """
    INV-TRAIN-055: meso_overlap_allowed

    Prova que:
    1) Dois mesociclos de equipes DIFERENTES com datas sobrepostas sao inseridos sem erro
    2) Ambos existem no DB apos flush (anti-false-positive: conta 2, nao apenas 1)

    Evidencia: training_cycle_service.py INV-055 comment (L44-46)
    """

    @pytest_asyncio.fixture
    async def inv055_orgs_teams(self, async_db: AsyncSession):
        """Cria 2 orgs e 2 teams para o teste de overlap."""
        cat_id = 9996
        await async_db.execute(text(
            "INSERT INTO categories (id, name, max_age, is_active) "
            "VALUES (:id, 'Cat INV-055', 19, true) ON CONFLICT (id) DO NOTHING"
        ), {"id": cat_id})

        org1_id = uuid4()
        org2_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO organizations (id, name) VALUES (:id, 'Org INV-055 A')"
        ), {"id": str(org1_id)})
        await async_db.execute(text(
            "INSERT INTO organizations (id, name) VALUES (:id, 'Org INV-055 B')"
        ), {"id": str(org2_id)})

        team1_id = uuid4()
        team2_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team) "
            "VALUES (:id, :org_id, :cat_id, 'Team INV-055 A', 'masculino', true)"
        ), {"id": str(team1_id), "org_id": str(org1_id), "cat_id": cat_id})
        await async_db.execute(text(
            "INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team) "
            "VALUES (:id, :org_id, :cat_id, 'Team INV-055 B', 'masculino', true)"
        ), {"id": str(team2_id), "org_id": str(org2_id), "cat_id": cat_id})

        pid = str(uuid4())
        uid = uuid4()
        await async_db.execute(text(
            "INSERT INTO persons (id, first_name, last_name, full_name, birth_date) "
            "VALUES (:id, 'Inv', '055', 'Inv 055', '1990-01-01')"
        ), {"id": pid})
        await async_db.execute(text(
            "INSERT INTO users (id, email, person_id, password_hash, status) "
            "VALUES (:id, :email, :person_id, 'hash', 'ativo')"
        ), {"id": str(uid), "email": f"inv055_{str(uid)[:8]}@hbtrack.com", "person_id": pid})
        await async_db.flush()

        return {
            "org1_id": org1_id, "org2_id": org2_id,
            "team1_id": team1_id, "team2_id": team2_id,
            "user_id": uid,
        }

    @pytest.mark.asyncio
    async def test_meso_overlap_different_teams_allowed(
        self, async_db: AsyncSession, inv055_orgs_teams
    ):
        """
        INV-055: Dois mesociclos de equipes DIFERENTES com datas sobrepostas
        devem ser inseridos sem erro e ambos existem no DB.

        Anti-false-positive: verifica COUNT == 2 apos insert de ambos.
        """
        d = inv055_orgs_teams
        meso1_id = uuid4()
        meso2_id = uuid4()

        # Datas sobrepostas: 2026-03-01 a 2026-05-31 para ambos os mesos
        start_date = date(2026, 3, 1)
        end_date = date(2026, 5, 31)

        # Insere meso 1 (Org A / Team A) diretamente via ORM
        meso1 = TrainingCycle(
            id=meso1_id,
            organization_id=d["org1_id"],
            team_id=d["team1_id"],
            type="meso",
            start_date=start_date,
            end_date=end_date,
            status="active",
            created_by_user_id=d["user_id"],
        )
        async_db.add(meso1)

        # Insere meso 2 (Org B / Team B) com MESMAS datas sobrepostas
        meso2 = TrainingCycle(
            id=meso2_id,
            organization_id=d["org2_id"],
            team_id=d["team2_id"],
            type="meso",
            start_date=start_date,
            end_date=end_date,
            status="active",
            created_by_user_id=d["user_id"],
        )
        async_db.add(meso2)

        # Flush deve ser bem-sucedido: ausencia de constraint de overlap
        await async_db.flush()

        # Anti-false-positive: AMBOS devem existir no DB
        result = await async_db.execute(
            select(TrainingCycle).where(
                TrainingCycle.id.in_([meso1_id, meso2_id])
            )
        )
        found = list(result.scalars().all())

        assert len(found) == 2, (
            f"Esperado 2 mesociclos sobrepostos, encontrado {len(found)}. "
            "INV-055: overlap entre equipes diferentes deve ser permitido."
        )

        found_ids = {str(c.id) for c in found}
        assert str(meso1_id) in found_ids
        assert str(meso2_id) in found_ids

    @pytest.mark.asyncio
    async def test_meso_overlap_same_date_range_two_orgs(
        self, async_db: AsyncSession, inv055_orgs_teams
    ):
        """
        INV-055: Overlap identico (mesmas datas exatas) de orgs diferentes — sem erro.

        Prova que NAO existe constraint UNIQUE em (date_range) para mesociclos.
        """
        d = inv055_orgs_teams
        id_a = uuid4()
        id_b = uuid4()

        # Datas identicas
        for cycle_id, org_id, team_id in [
            (id_a, d["org1_id"], d["team1_id"]),
            (id_b, d["org2_id"], d["team2_id"]),
        ]:
            cycle = TrainingCycle(
                id=cycle_id,
                organization_id=org_id,
                team_id=team_id,
                type="meso",
                start_date=date(2026, 6, 1),
                end_date=date(2026, 8, 31),
                status="active",
                created_by_user_id=d["user_id"],
            )
            async_db.add(cycle)

        # Sem excecao = sem constraint de non-overlap
        await async_db.flush()

        result = await async_db.execute(
            select(TrainingCycle).where(TrainingCycle.id.in_([id_a, id_b]))
        )
        assert len(list(result.scalars().all())) == 2
