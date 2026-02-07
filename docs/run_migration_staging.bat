@echo off
REM Script to apply migrations to staging database
REM FASE 1: Testing Phase 1 migration in staging

set DATABASE_URL=postgresql://neondb_owner:npg_fmT3ctPrD8pW@ep-misty-pine-ad12ggz1-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require^&channel_binding=require

echo ================================================================================
echo APPLYING MIGRATIONS TO STAGING
echo ================================================================================
echo Database: ep-misty-pine-ad12ggz1-pooler (staging)
echo ================================================================================

.venv\Scripts\alembic.exe -c backend\db\alembic.ini upgrade head

echo ================================================================================
echo MIGRATION COMPLETE
echo ================================================================================
