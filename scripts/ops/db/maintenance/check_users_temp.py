# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ,DB_WRITE,FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=NO
# HB_SCRIPT_ENTRYPOINT=python scripts/ops/db/maintenance/check_users_temp.py
# HB_SCRIPT_OUTPUTS=stdout
import asyncio
from app.core.db import get_async_db
from sqlalchemy import text

async def check_users():
    async for session in get_async_db():
        result = await session.execute(text("""
            SELECT u.email, u.is_superadmin, p.full_name, r.name as role_name
            FROM users u
            LEFT JOIN org_memberships om ON om.user_id = u.id AND om.deleted_at IS NULL
            LEFT JOIN roles r ON r.id = om.role_id
            LEFT JOIN persons p ON p.id = u.person_id
            WHERE u.deleted_at IS NULL
            ORDER BY u.is_superadmin DESC, u.email
            LIMIT 10
        """))
        print("\n📋 Usuários no banco:\n")
        for row in result:
            superadmin = "SUPERADMIN" if row.is_superadmin else f"Role: {row.role_name or 'N/A'}"
            print(f"  Email: {row.email}")
            print(f"  Nome: {row.full_name or 'N/A'}")
            print(f"  {superadmin}\n")
        break

asyncio.run(check_users())

