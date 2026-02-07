<!-- STATUS: NEEDS_REVIEW -->

## Implementações de Estatísticas – HB Track (estado atual)

### Backend
- Endpoints consolidados em `app/api/v1/routers/reports_operational.py`
  - `GET /reports/operational-session`: snapshot operacional (roster ativo, attendance, wellness pós, baseline de carga 7d, status da sessão, pendências, alertas de carga/médico/compliance, lista operacional). Usa `TrainingSession`, `Attendance`, `WellnessPost`, `TeamRegistration`, valida escopo por `ExecutionContext`.
  - `GET /reports/athlete-self`: visão individual autenticada. Resolve atleta via `ctx.person_id`, retorna presença (streak, faltas recentes, últimas sessões), wellness tendência, zona de carga, alerts (attendance/compliance/medical/load) e insights.
  - Engajamento: `_engagement_status` calcula ativo/parcial/inativo; `inactive_engagement` contado no snapshot.
- Listagem de sessões usada pelo frontend: `GET /training-sessions` (paginação) em `training_sessions.py`; matches ainda não conectados ao snapshot.

### Frontend
- Rota `/statistics` (`src/app/(admin)/statistics/page.tsx` + `StatisticsContainer.tsx`):
  - Empty state obrigatório com modal bloqueante para selecionar sessão.
  - Carrega sessões reais via `/training-sessions`; status calculado (scheduled/ongoing/completed).
  - Chama `statisticsService.getOperationalSession`; exibe pendências, carga, lista operacional e alertas; erros exibem card de aviso (sem mocks).
  - Ordena atletas por severidade (critical > attention > ok).
- Rota `/statistics/me` (`src/app/(admin)/statistics/me/page.tsx` + `components/AthleteSelfView.tsx`):
  - Consome `statisticsService.getAthleteSelf`; sem seleção manual; estados de loading/erro; mostra presença, wellness, carga pessoal, alertas e insights sem mock.
- Client API (`src/lib/api/statistics.ts`):
  - Tipos `OperationalSessionSnapshot` e `AthleteSelfReport` alinhados aos endpoints.
  - Métodos `getOperationalSession(sessionId)` e `getAthleteSelf()` usando `apiClient`.

### Gaps conhecidos
- Seleção de sessão inclui apenas treinos; integração com jogos/matches ainda pendente.
- `/reports/operational-session` não agrega dados de match attendance/eventos; status do tipo sempre “training”.
- UX do modal segue copy de ESTATISTICAS.MD, mas precisa receber lista de jogos quando endpoint for exposto.
- `/reports/athlete-self` traz últimas 8 sessões; insights e alertas são básicos (falta integração com regras médicas/compliance avançadas se existirem).

### Arquivos principais tocados
- Backend: `app/api/v1/routers/reports_operational.py`, `app/api/v1/api.py`.
- Frontend: `src/app/(admin)/statistics/StatisticsContainer.tsx`, `src/app/(admin)/statistics/me/page.tsx`, `src/app/(admin)/statistics/components/AthleteSelfView.tsx`, `src/lib/api/statistics.ts`.
