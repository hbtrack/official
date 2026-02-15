# HB_SCRIPT_KIND=OPS
# HB_SCRIPT_SCOPE=db
# HB_SCRIPT_SIDE_EFFECTS=DB_READ,DB_WRITE,FS_READ,FS_WRITE
# HB_SCRIPT_IDEMPOTENT=NO
# HB_SCRIPT_ENTRYPOINT=python scripts/ops/db/maintenance/check_migration.py
# HB_SCRIPT_OUTPUTS=stdout
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://hbtrack_dev:hbtrack_dev_pwd@localhost:5433/hb_track_dev')
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    version = result.fetchone()
    if version:
        print(f"Current migration: {version[0]}")
    else:
        print("No migrations applied")

