"""
INV-TRAIN-056 — micro_contained_in_meso

SERVICE TEST (Classe C2) — Testa que mesociclos devem estar contidos no macrociclo pai.

Evidencia:
- app/services/training_cycle_service.py (MicrocycleOutsideMesoError L36-41)
- app/services/training_cycle_service.py (guard em create() L155-162)
- INV-055 comment L44-46

Mapping: "micro" = cycle de tipo meso (menor unidade relativa ao macro)
         "meso"  = cycle de tipo macro (o container pai)
O guard em TrainingCycleService.create() levanta MicrocycleOutsideMesoError
quando datas do meso sao incompativeis com o macro pai.
"""
import pytest
import pytest_asyncio
from datetime import date, datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ExecutionContext
from app.services.training_cycle_service import TrainingCycleService, MicrocycleOutsideMesoError
from app.schemas.training_cycles import TrainingCycleCreate


def _make_context_056(user_id: UUID, org_id: UUID) -> ExecutionContext:
    """Cria um ExecutionContext minimal para testes INV-056."""
    return ExecutionContext(
        user_id=user_id,
        email="inv056@hbtrack.com",
        role_code="treinador",
        request_id=str(uuid4()),
        organization_id=org_id,
    )


class TestInvTrain056:
    """
    INV-TRAIN-056: micro_contained_in_meso

    Prova que:
    1) Meso com datas dentro do macro -> valido (sem excecao)
    2) Meso com start_date antes de macro.start_date -> MicrocycleOutsideMesoError
    3) Meso com end_date apos macro.end_date -> MicrocycleOutsideMesoError

    Evidencia: training_cycle_service.py create() guard (L155-162) + MicrocycleOutsideMesoError (L36-41)
    """

    @pytest_asyncio.fixture
    async def inv056_setup(self, async_db: AsyncSession):
        """Cria org, team, user e um macrociclo pai para INV-056."""
        # Categoria
        cat_id = 9995
        await async_db.execute(text(
            "INSERT INTO categories (id, name, max_age, is_active) "
            "VALUES (:id, 'Cat INV-056', 19, true) ON CONFLICT (id) DO NOTHING"
        ), {"id": cat_id})

        # Organizacao
        org_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO organizations (id, name) VALUES (:id, 'Org INV-056')"
        ), {"id": str(org_id)})

        # Usuario
        pid = str(uuid4())
        uid = uuid4()
        await async_db.execute(text(
            "INSERT INTO persons (id, first_name, last_name, full_name, birth_date) "
            "VALUES (:id, 'Inv', '056', 'Inv 056', '1990-01-01')"
        ), {"id": pid})
        await async_db.execute(text(
            "INSERT INTO users (id, email, person_id, password_hash, status) "
            "VALUES (:id, :email, :person_id, 'hash', 'ativo')"
        ), {"id": str(uid), "email": f"inv056_{str(uid)[:8]}@hbtrack.com", "person_id": pid})

        # Time
        team_id = uuid4()
        await async_db.execute(text(
            "INSERT INTO teams (id, organization_id, category_id, name, gender, is_our_team) "
            "VALUES (:id, :org_id, :cat_id, 'Team INV-056', 'masculino', true)"
        ), {"id": str(team_id), "org_id": str(org_id), "cat_id": cat_id})

        # Macrociclo pai (2026-01-01 a 2026-12-31)
        macro_id = uuid4()
        await async_db.execute(text("""
            INSERT INTO training_cycles
                (id, organization_id, team_id, type, start_date, end_date, status, created_by_user_id)
            VALUES (:id, :org_id, :team_id, 'macro', :sd, :ed, 'active', :uid)
        """), {
            "id": str(macro_id), "org_id": str(org_id), "team_id": str(team_id),
            "sd": date(2026, 1, 1), "ed": date(2026, 12, 31), "uid": str(uid),
        })
        await async_db.flush()

        return {
            "org_id": org_id, "team_id": team_id,
            "user_id": uid, "macro_id": macro_id,
            "macro_start": date(2026, 1, 1), "macro_end": date(2026, 12, 31),
        }

    @pytest.mark.asyncio
    async def test_valid_meso_inside_macro(self, async_db: AsyncSession, inv056_setup):
        """
        INV-056 CASO POSITIVO: Meso com datas dentro do macro deve ser criado sem erro.

        Evidencia: training_cycle_service.py create() (L155-162)
        """
        d = inv056_setup
        context = _make_context_056(d["user_id"], d["org_id"])
        service = TrainingCycleService(async_db, context)

        # Meso dentro do macro: 2026-03-01 a 2026-05-31
        payload = TrainingCycleCreate(
            team_id=d["team_id"],
            type="meso",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 5, 31),
            parent_cycle_id=d["macro_id"],
        )

        meso = await service.create(payload)

        assert meso.id is not None
        assert meso.type == "meso"
        assert meso.parent_cycle_id == d["macro_id"]

    @pytest.mark.asyncio
    async def test_invalid_meso_start_before_macro(self, async_db: AsyncSession, inv056_setup):
        """
        INV-056 CASO NEGATIVO: Meso com start_date antes de macro.start_date
        deve levantar MicrocycleOutsideMesoError.

        Evidencia: training_cycle_service.py create() L158-162
        """
        d = inv056_setup
        context = _make_context_056(d["user_id"], d["org_id"])
        service = TrainingCycleService(async_db, context)

        # start_date ANTES do macro (macro inicia 2026-01-01)
        payload = TrainingCycleCreate(
            team_id=d["team_id"],
            type="meso",
            start_date=date(2025, 12, 1),  # antes do macro
            end_date=date(2026, 3, 31),
            parent_cycle_id=d["macro_id"],
        )

        with pytest.raises(MicrocycleOutsideMesoError):
            await service.create(payload)

    @pytest.mark.asyncio
    async def test_invalid_meso_end_after_macro(self, async_db: AsyncSession, inv056_setup):
        """
        INV-056 CASO NEGATIVO: Meso com end_date apos macro.end_date
        deve levantar MicrocycleOutsideMesoError.

        Evidencia: training_cycle_service.py create() L158-162
        """
        d = inv056_setup
        context = _make_context_056(d["user_id"], d["org_id"])
        service = TrainingCycleService(async_db, context)

        # end_date APOS do macro (macro termina 2026-12-31)
        payload = TrainingCycleCreate(
            team_id=d["team_id"],
            type="meso",
            start_date=date(2026, 10, 1),
            end_date=date(2027, 2, 28),  # apos o macro
            parent_cycle_id=d["macro_id"],
        )

        with pytest.raises(MicrocycleOutsideMesoError):
            await service.create(payload)
