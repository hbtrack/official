#!/usr/bin/env python3
"""Verify staging database schema after migration."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-misty-pine-ad12ggz1-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("=" * 80)
print("STAGING DATABASE VERIFICATION")
print("=" * 80)

# Check columns in training_sessions
print("\n1. Check training_sessions columns:")
print("-" * 80)
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'training_sessions'
      AND column_name IN ('season_id', 'team_id')
    ORDER BY column_name
""")
for row in cursor.fetchall():
    print(f"  - {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")

# Check materialized views
print("\n2. Check materialized views:")
print("-" * 80)
cursor.execute("""
    SELECT schemaname, matviewname
    FROM pg_matviews
    WHERE matviewname LIKE 'mv_%'
    ORDER BY matviewname
""")
views = cursor.fetchall()
if views:
    for row in views:
        print(f"  - {row['matviewname']}")
else:
    print("  [No materialized views found]")

# Check FK constraints
print("\n3. Check foreign key constraints:")
print("-" * 80)
cursor.execute("""
    SELECT conname, confrelid::regclass AS referenced_table
    FROM pg_constraint
    WHERE conrelid = 'training_sessions'::regclass
      AND contype = 'f'
      AND conname LIKE 'fk_training_sessions_%'
    ORDER BY conname
""")
for row in cursor.fetchall():
    print(f"  - {row['conname']} -> {row['referenced_table']}")

# Check indexes
print("\n4. Check indexes:")
print("-" * 80)
cursor.execute("""
    SELECT indexname
    FROM pg_indexes
    WHERE tablename = 'training_sessions'
      AND indexname LIKE 'idx_training_sessions_%'
    ORDER BY indexname
""")
for row in cursor.fetchall():
    print(f"  - {row['indexname']}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

conn.close()
