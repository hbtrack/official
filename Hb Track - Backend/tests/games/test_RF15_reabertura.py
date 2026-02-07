import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import text


def insert_match(db, competition_season_id, category_id):
    match_id = str(uuid4())
    db.execute(
        """
        INSERT INTO matches (id, competition_season_id, category_id, match_at, status)
        VALUES (:id, :csid, :catid, now(), 'scheduled')
        """,
        {"id": match_id, "csid": competition_season_id, "catid": category_id},
    )
    db.commit()
    return match_id


def get_one(db, query, params=None):
    res = db.execute(text(query), params or {})
    return res.fetchone()


@pytest.mark.parametrize("action", ["block_edit", "reopen_audit"])
def test_matches_block_and_reopen(db, action):
    # Obter ids necessários do seed
    cs = get_one(db, "SELECT id FROM competition_seasons LIMIT 1")
    cat = get_one(db, "SELECT id FROM categories LIMIT 1")
    assert cs is not None and cat is not None

    match_id = insert_match(db, cs.id, cat.id)

    # Fazer finalização do jogo (mudança de status requer admin_note conforme migrations)
    db.execute(
        """
        UPDATE matches
        SET status = 'finished', admin_note = 'finalizando teste', finalized_at = now()
        WHERE id = :id
        """,
        {"id": match_id},
    )
    db.commit()

    if action == "block_edit":
        # Tentar editar campo qualquer; espera-se erro vindo da trigger
        with pytest.raises(Exception) as exc:
            db.execute("UPDATE matches SET venue = 'Local X' WHERE id = :id", {"id": match_id})
            db.commit()

        msg = str(exc.value)
        assert 'trg_games_block_update_finalized' in msg or 'Jogo finalizado' in msg

    else:
        # Reabertura: precisa setar allow_reopen=true e admin_note e mudar status
        db.execute(
            """
            UPDATE matches
            SET allow_reopen = true, admin_note = 'reabertura teste', status = 'scheduled'
            WHERE id = :id
            """,
            {"id": match_id},
        )
        db.commit()

        # Verificar audit_logs por ação de reabertura
        row = get_one(
            db,
            "SELECT action, justification, context FROM audit_logs WHERE entity = 'match' AND entity_id = :id ORDER BY created_at DESC LIMIT 1",
            {"id": match_id},
        )
        assert row is not None
        assert row.action in ('game_reopen', 'status_reopen')
