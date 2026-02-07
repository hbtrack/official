"""
Script para definir senha do superadmin
"""
from sqlalchemy import text
from app.core.db import engine
from app.core.security import hash_password

pwd = hash_password('admin123')
with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE users SET password_hash = :pwd WHERE email = 'superadmin@seed.local'"),
        {'pwd': pwd}
    )
    conn.commit()
    print(f'Password updated for superadmin. Rows affected: {result.rowcount}')
