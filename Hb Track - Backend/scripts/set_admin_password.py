"""
Script para definir senha do admin
"""
from sqlalchemy import text
from app.core.db import engine
from app.core.security import hash_password

pwd = hash_password('12345678')
with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE users SET password_hash = :pwd WHERE email = 'admin@hbtracking.com'"),
        {'pwd': pwd}
    )
    conn.commit()
    print(f'Password updated for admin@hbtracking.com. Rows affected: {result.rowcount}')
