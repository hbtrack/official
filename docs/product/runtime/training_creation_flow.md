---
id: training_creation_flow
doc_mode: HOWTO
status: CANONICAL
source_of_truth:
  - kind: ssot_factual
    ref: docs/_canon/HB_TRACK_PROFILE.yaml
depends_on:
  - docs/product/ARCHITECTURE.md
  - docs/product/DOMAIN_MODEL.md
evidence_expected:
  - docs/_generated/_reports/tasks/training_creation_flow.log
---

# Runtime Scenario: Training Session Creation Flow

## Goal
Verify the full training session lifecycle: create (draft) → add exercises → schedule → complete → readonly.

## Preconditions
- Backend running with authenticated user (treinador or above)
- At least one team exists with the user's membership
- Exercise bank populated (at least 1 exercise)

## Steps

1. Create a training session (draft):
```bash
curl -s -X POST http://localhost:8000/api/v1/training-sessions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"team_id":"<team_uuid>","date":"2026-02-18","title":"Treino Tatico"}' \
  | python -m json.tool
```
Expected: 201 with session in `draft` status.

2. Add exercises to session:
```bash
curl -s -X POST http://localhost:8000/api/v1/training-sessions/<session_id>/exercises \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"exercise_id":"<exercise_uuid>","order":1,"duration_minutes":15}' \
  | python -m json.tool
```
Expected: 201 with session_exercise created.

3. Transition to scheduled:
```bash
curl -s -X PATCH http://localhost:8000/api/v1/training-sessions/<session_id>/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"scheduled"}' \
  | python -m json.tool
```
Expected: 200 with status changed to `scheduled`.

4. Verify edit window enforcement (attempt edit after >24h should fail for non-superior roles).

## Expected outcomes
- Session created in draft status
- Exercises attached with drag-drop ordering preserved
- Status transitions follow lifecycle: draft → scheduled → in_progress → pending_review → readonly
- Edit windows enforced (R40): author 10min, superior 24h, >24h readonly

## Failure modes
- **Missing team_id:** 422 validation error
- **Invalid status transition:** 400 (e.g., draft → readonly directly)
- **Edit window expired:** 403 with edit window violation message
- **Insufficient permissions:** 403 (atleta cannot create sessions)

## Rollback
Sessions in `draft` can be deleted. Scheduled+ sessions require soft delete by superior role.
