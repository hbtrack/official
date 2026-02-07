#!/usr/bin/env python3
"""
Script para testar endpoints de relatórios em staging.
Valida que as materialized views estão funcionando corretamente.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database staging
DATABASE_URL = 'postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-misty-pine-ad12ggz1-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

print("=" * 80)
print("TESTE DE RELATORIOS - STAGING")
print("=" * 80)
print()

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# ============================================================================
# TEST 1: R1 - Training Performance Report
# ============================================================================
print("1. R1: Training Performance Report (mv_training_performance)")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) as total_sessions
    FROM mv_training_performance
""")
result = cursor.fetchone()
print(f"   Total sessions in view: {result['total_sessions']}")

cursor.execute("""
    SELECT
        session_id,
        organization_id,
        season_id,
        team_id,
        session_at,
        total_athletes,
        presentes,
        attendance_rate,
        avg_rpe,
        avg_internal_load
    FROM mv_training_performance
    ORDER BY session_at DESC
    LIMIT 3
""")
results = cursor.fetchall()
if results:
    print(f"   Sample data (latest 3 sessions):")
    for i, row in enumerate(results, 1):
        print(f"     {i}. Session {str(row['session_id'])[:8]}... | Athletes: {row['total_athletes']} | Attendance: {row['attendance_rate']}%")
else:
    print("   [No data found - staging DB might be empty]")

print()

# ============================================================================
# TEST 2: R2 - Athlete Individual Report
# ============================================================================
print("2. R2: Athlete Individual Report (mv_athlete_training_summary)")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) as total_athletes
    FROM mv_athlete_training_summary
""")
result = cursor.fetchone()
print(f"   Total athletes in view: {result['total_athletes']}")

cursor.execute("""
    SELECT
        athlete_id,
        full_name,
        current_state,
        total_sessions,
        sessions_presente,
        attendance_rate,
        avg_internal_load,
        load_7d,
        load_28d,
        active_medical_cases
    FROM mv_athlete_training_summary
    ORDER BY total_sessions DESC
    LIMIT 3
""")
results = cursor.fetchall()
if results:
    print(f"   Sample data (top 3 by sessions):")
    for i, row in enumerate(results, 1):
        print(f"     {i}. {row['full_name']} | Sessions: {row['total_sessions']} | Attendance: {row['attendance_rate']}% | Load 7d: {row['load_7d']}")
else:
    print("   [No data found - staging DB might be empty]")

print()

# ============================================================================
# TEST 3: R3 - Wellness Summary Report
# ============================================================================
print("3. R3: Wellness Summary Report (mv_wellness_summary)")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) as total_periods
    FROM mv_wellness_summary
""")
result = cursor.fetchone()
print(f"   Total periods in view: {result['total_periods']}")

cursor.execute("""
    SELECT
        organization_id,
        season_id,
        team_id,
        period_start,
        period_type,
        athletes_count,
        sessions_count,
        avg_sleep_hours,
        avg_sleep_quality,
        avg_fatigue_pre,
        avg_stress
    FROM mv_wellness_summary
    WHERE period_type = 'weekly'
    ORDER BY period_start DESC
    LIMIT 3
""")
results = cursor.fetchall()
if results:
    print(f"   Sample data (latest 3 weekly periods):")
    for i, row in enumerate(results, 1):
        print(f"     {i}. Week {row['period_start']} | Athletes: {row['athletes_count']} | Avg Sleep: {row['avg_sleep_hours']}h | Stress: {row['avg_stress']}")
else:
    print("   [No data found - staging DB might be empty]")

print()

# ============================================================================
# TEST 4: R4 - Medical Cases Summary Report
# ============================================================================
print("4. R4: Medical Cases Summary Report (mv_medical_cases_summary)")
print("-" * 80)

cursor.execute("""
    SELECT COUNT(*) as view_exists
    FROM pg_matviews
    WHERE matviewname = 'mv_medical_cases_summary'
""")
result = cursor.fetchone()
if result['view_exists'] > 0:
    print(f"   View exists: YES")

    cursor.execute("""
        SELECT COUNT(*) as total_records
        FROM mv_medical_cases_summary
    """)
    result = cursor.fetchone()
    print(f"   Total records in view: {result['total_records']}")

    # Try to fetch sample data
    cursor.execute("""
        SELECT *
        FROM mv_medical_cases_summary
        LIMIT 3
    """)
    results = cursor.fetchall()
    if results:
        print(f"   Sample data (first 3 records):")
        for i, row in enumerate(results, 1):
            print(f"     {i}. {dict(row)}")
    else:
        print("   [No data found - staging DB might be empty]")
else:
    print("   [ERROR: View does not exist]")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)

cursor.execute("""
    SELECT matviewname, schemaname
    FROM pg_matviews
    WHERE matviewname LIKE 'mv_%'
    ORDER BY matviewname
""")
views = cursor.fetchall()

print(f"\nMaterialized Views Status:")
expected_views = [
    'mv_athlete_training_summary',
    'mv_medical_cases_summary',
    'mv_training_performance',
    'mv_wellness_summary'
]

for view_name in expected_views:
    exists = any(v['matviewname'] == view_name for v in views)
    status = "OK" if exists else "MISSING"
    print(f"  - {view_name}: {status}")

# Check if views have data
print(f"\nData Status:")
for view_name in expected_views:
    try:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {view_name}")
        count = cursor.fetchone()['cnt']
        status = f"{count} records" if count > 0 else "EMPTY (no data)"
        print(f"  - {view_name}: {status}")
    except Exception as e:
        print(f"  - {view_name}: ERROR ({str(e)})")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Recommendations
print("\nRECOMMENDATIONS:")
if all(any(v['matviewname'] == view for v in views) for view in expected_views):
    print("  OK - All 4 materialized views exist")
else:
    print("  ACTION REQUIRED - Some views are missing")

# Check for empty views
empty_count = 0
for view_name in expected_views:
    try:
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {view_name}")
        if cursor.fetchone()['cnt'] == 0:
            empty_count += 1
    except:
        pass

if empty_count > 0:
    print(f"  NOTE - {empty_count} views are empty (staging DB might not have test data)")
    print("  ACTION - Populate staging DB with test data before production deployment")
else:
    print("  OK - All views contain data")

print("\nNEXT STEPS:")
print("  1. If staging DB is empty, populate with test data")
print("  2. Test API endpoints via /api/v1/docs")
print("  3. Validate permissions and authentication")
print("  4. Deploy to production when ready")

conn.close()
