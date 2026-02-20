---
id: async_job_execution
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: ssot_factual
    ref: docs/_canon/HB_TRACK_PROFILE.yaml
depends_on:
  - docs/product/ARCHITECTURE.md
evidence_expected:
  - _reports/tasks/async_job_execution.log
---

# Runtime Scenario: Async Job Execution (Celery)

## Goal
Verify that Celery workers process background tasks (training alerts, email queue, export jobs).

## Preconditions
- Redis running on port 6379 (`docker-compose up -d` in `infra/`)
- Backend running
- Celery worker started

## Steps

1. Start Celery worker:
```bash
cd "Hb Track - Backend"
celery -A app.celery_app worker --loglevel=info
```
Expected: Worker connects to Redis and reports ready.

2. Trigger an async task (e.g., training alert generation via API):
```bash
curl -s -X POST http://localhost:8000/api/v1/training-alerts/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"<team_uuid>"}' \
  | python -m json.tool
```
Expected: 202 Accepted with task_id.

3. Check task result in Celery logs or via Flower:
```bash
celery -A app.celery_app inspect active
```
Expected: Task appears in active/completed list.

4. Verify side effects in DB (e.g., TrainingAlert records created):
```sql
SELECT * FROM training_alert WHERE team_id = '<team_uuid>' ORDER BY created_at DESC LIMIT 5;
```

## Expected outcomes
- Celery worker connects to Redis broker
- Tasks are enqueued and processed
- Side effects (DB writes, emails sent) are observable
- Failed tasks are retried per Celery config

## Failure modes
- **Redis unreachable:** Worker fails to start; check Redis container
- **Task serialization error:** Check task parameter types match expected schema
- **DB connection from worker:** Worker needs own DB connection; check env vars in worker context
- **Stale results:** Analytics cache not refreshed; verify cache invalidation logic

## Rollback
Celery tasks are idempotent by design. If a task produces bad data, delete the affected rows and re-trigger.
