#!/usr/bin/env python3
"""
Script to apply migrations to staging database.
Sets DATABASE_URL environment variable and runs alembic upgrade head.
"""

import os
import subprocess
import sys

# Set staging DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-misty-pine-ad12ggz1-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

print("=" * 80)
print("APPLYING MIGRATIONS TO STAGING")
print("=" * 80)
print(f"Database: ep-misty-pine-ad12ggz1-pooler (staging)")
print("=" * 80)
print()

# Run alembic upgrade head
try:
    alembic_path = os.path.join(os.getcwd(), '.venv', 'Scripts', 'alembic.exe')
    config_path = os.path.join(os.getcwd(), 'backend', 'db', 'alembic.ini')

    print(f"Alembic path: {alembic_path}")
    print(f"Config path: {config_path}")
    print()

    result = subprocess.run(
        [alembic_path, '-c', config_path, 'upgrade', 'head'],
        capture_output=False,
        text=True,
        check=True,
        env=os.environ
    )
    print()
    print("=" * 80)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print()
    print("=" * 80)
    print("❌ MIGRATION FAILED")
    print("=" * 80)
    print(f"Exit code: {e.returncode}")
    sys.exit(e.returncode)
