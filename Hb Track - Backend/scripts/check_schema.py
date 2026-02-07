from app.core.db import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()
engine = db.get_bind()
inspector = inspect(engine)

cols = inspector.get_columns('teams')
print('\nteams columns:')
for c in cols:
    print(f"  {c['name']}: {c['type']}")

db.close()
