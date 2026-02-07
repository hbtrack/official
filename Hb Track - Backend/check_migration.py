from sqlalchemy import create_engine, text

engine = create_engine('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev')
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    version = result.fetchone()
    if version:
        print(f"Current migration: {version[0]}")
    else:
        print("No migrations applied")
