# HB_SCRIPT_KIND=CHECK
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ
# HB_SCRIPT_IDEMPOTENT=YES
# HB_SCRIPT_ENTRYPOINT=python scripts/checks/db/test_fixture_select_only.py
# HB_SCRIPT_OUTPUTS=stdout
"""
FIXTURE TEST: execute(text("SELECT...")) should be detected as DB_READ only.
Expected: HB006 violation should NOT trigger (no DB_WRITE detected).
"""
import asyncio
from app.core.db import get_async_db
from sqlalchemy import text


async def test_select_only():
    """This should be detected as DB_READ, not DB_WRITE."""
    async for session in get_async_db():
        result = await session.execute(text("""
            SELECT user_id, role_id FROM org_memberships
            WHERE deleted_at IS NULL
            ORDER BY user_id
            LIMIT 100
        """))
        
        print("Results:")
        for row in result:
            print(f"  User {row.user_id}: Role {row.role_id}")
        break


asyncio.run(test_select_only())
