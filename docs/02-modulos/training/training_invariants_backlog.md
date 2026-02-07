# Backlog de Invariantes (B) — Training

## BACKLOG-ATTENDANCE-SCOPED — Expor rota scoped de attendance no contrato
- Onde implementar: incluir `attendance_scoped.router` + `attendance_scoped.scoped_router` em `app/api/v1/api.py`.
- Como testar: ajustar teste para 401 sem auth (sugestao: `tests/api/test_training.py::TestAttendanceAPI::test_scoped_attendance_route_without_auth_returns_401`).
- Evidencia esperada: OpenAPI regenerado + TRD atualizado com rota exposta.
- Criterio de aceite (DoD): router incluído + OpenAPI atualizado + TRD/scripts ok + teste ajustado e passando.

## Resolvidas
- INV-TRAIN-004 — Janela de edição por autoria/hierarquia implementada e testada (validação por tempo em `_validate_edit_permission`).
- INV-TRAIN-019 (Legacy ID: INV-TRAIN-P002) — audit log em ações de sessão implementado e testado.
- INV-TRAIN-027 (Legacy ID: INV-TRAIN-P010) — cache refresh daily implementado via Celery beat + task.
