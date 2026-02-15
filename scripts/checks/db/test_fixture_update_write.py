# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/checks/db/test_fixture_update_write.py
# HB_SCRIPT_OUTPUTS=stdout
"""
FIXTURE TEST: execute(text("UPDATE...")) should be detected as DB_WRITE.
Expected: HB006 violation SHOULD trigger (DB_WRITE prohibited for checks/).
"""
import asyncio
from app.core.db import get_async_db
from sqlalchemy import text


async def test_update_write():
    """This SHOULD trigger HB006 (DB_WRITE prohibited for checks)."""
    async for session in get_async_db():
        # WARNING: This is a bad pattern for checks - should use DB_READ only
        await session.execute(text("""
            UPDATE org_memberships SET role_id = 2
            WHERE user_id = 999
        """))
        await session.commit()
        break


asyncio.run(test_update_write())
