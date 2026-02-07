# Endpoints do Módulo Training

Este arquivo lista todos os endpoints relacionados ao módulo de treinamento no HB Track, extraídos da especificação OpenAPI.

## Endpoints Disponíveis

### Training Sessions

#### 1. GET /api/v1/training-sessions
- **Summary**: Lista sessões de treino
- **Description**: Lista paginada de sessões de treino com filtros por team_id, season_id, datas, etc. Regras: R25/R26 (permissões por papel).
- **Parâmetros**: team_id (query, opcional), season_id (query, opcional), start_date (query, opcional), end_date (query, opcional), page (query, opcional, default=1), limit (query, opcional, default=50).
- **Respostas**: 200 (lista paginada), 401 (token inválido), 403 (permissão insuficiente), 422 (erro de validação).

#### 2. POST /api/v1/training-sessions
- **Summary**: Cria sessão de treino
- **Description**: Cria uma nova sessão de treino (evento operacional). Regras: R18 (eventos operacionais), R22 (métricas operacionais), R25/R26 (permissões), validação de can_create_training.
- **Request Body**: TrainingSessionCreate (JSON).
- **Respostas**: 201 (sessão criada), 401 (token inválido), 403 (permissão insuficiente), 404 (time não encontrado), 422 (erro de validação).

#### 3. GET /api/v1/training-sessions/{training_session_id}
- **Summary**: Obtém sessão de treino por ID
- **Description**: Retorna detalhes de uma sessão de treino específica. Regras: R25/R26 (permissões por papel e escopo).
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (detalhes da sessão), 401 (token inválido), 404 (sessão não encontrada), 422 (erro de validação).

#### 4. PATCH /api/v1/training-sessions/{training_session_id}
- **Summary**: Atualiza sessão de treino
- **Description**: Atualiza campos editáveis de uma sessão de treino. Regras de edição (R40): ≤10 min (livre), >10 min e ≤24h (perfil superior), >24h (admin_note obrigatório). Outras: R25/R26 (permissões).
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Request Body**: TrainingSessionUpdate (JSON).
- **Respostas**: 200 (sessão atualizada), 401 (token inválido), 403 (janela expirada), 404 (sessão não encontrada), 422 (erro de validação).

#### 5. DELETE /api/v1/training-sessions/{training_session_id}
- **Summary**: Exclui sessão de treino
- **Description**: Soft delete de sessão de treino. Regras: R29/R33 (sem DELETE físico, histórico), RDB3 (soft delete com deleted_at e deleted_reason).
- **Parâmetros**: training_session_id (path, obrigatório, UUID), reason (query, obrigatório, string min 5 chars).
- **Respostas**: 200 (sessão excluída), 401 (token inválido), 403 (permissão insuficiente), 404 (sessão não encontrada), 422 (erro de validação).

#### 6. POST /api/v1/training-sessions/{training_session_id}/restore
- **Summary**: Restaura sessão de treino
- **Description**: Restaura sessão de treino excluída. Regras: RDB3 (restore via nullify de deleted_at).
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (sessão restaurada), 401 (token inválido), 403 (permissão insuficiente), 404 (sessão não encontrada), 422 (erro de validação).

#### 7. POST /api/v1/training-sessions/{training_session_id}/publish
- **Summary**: Publica sessão de treino
- **Description**: Publica sessão de treino para atletas. Regras: permissões específicas.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (publicada), 401, 403, 404, 422.

#### 8. POST /api/v1/training-sessions/{training_session_id}/close
- **Summary**: Fecha sessão de treino
- **Description**: Fecha sessão de treino após conclusão. Regras: validações de estado.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (fechada), 401, 403, 404, 422.

#### 9. GET /api/v1/training-sessions/{training_session_id}/deviation
- **Summary**: Obtém desvio da sessão
- **Description**: Calcula desvio entre plano e execução da sessão.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (desvio), 401, 404, 422.

#### 10. POST /api/v1/training-sessions/{training_session_id}/duplicate
- **Summary**: Duplica sessão de treino
- **Description**: Cria cópia de sessão existente.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Request Body**: Parâmetros de duplicação.
- **Respostas**: 201 (duplicada), 401, 403, 404, 422.

#### 11. GET /api/v1/training-sessions/{training_session_id}/wellness-status
- **Summary**: Status de wellness da sessão
- **Description**: Retorna status de wellness pré/pós sessão.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (status), 401, 404, 422.

#### 12. POST /api/v1/training-sessions/copy-week
- **Summary**: Copia semana de treinos
- **Description**: Copia sessões de uma semana para outra.
- **Request Body**: Parâmetros de cópia.
- **Respostas**: 201 (copiada), 401, 403, 422.

#### 13. POST /api/v1/training-sessions/{training_session_id}/reopen
- **Summary**: Reabre sessão de treino
- **Description**: Reabre sessão de treino fechada.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (reabierta), 401, 403, 404, 422.

### Trainings (Escopo de Time)

#### 14. GET /api/v1/teams/{team_id}/trainings
- **Summary**: Lista treinos de um time
- **Description**: Lista paginada de treinos associados a um time específico com filtros por season_id, datas, athlete_id.
- **Parâmetros**: team_id (path, obrigatório, UUID), season_id (query, opcional), start_date (query, opcional), end_date (query, opcional), athlete_id (query, opcional), page (query, opcional), limit (query, opcional).
- **Respostas**: 200 (lista), 403, 422.

#### 15. POST /api/v1/teams/{team_id}/trainings
- **Summary**: Cria treino para um time
- **Description**: Cria nova sessão de treino no escopo de um time específico.
- **Parâmetros**: team_id (path, obrigatório, UUID), athlete_id (query, opcional).
- **Request Body**: ScopedTrainingSessionCreate (JSON).
- **Respostas**: 201 (criado), 403, 422.

#### 16. GET /api/v1/teams/{team_id}/trainings/{training_id}
- **Summary**: Detalhes de treino (escopo time)
- **Description**: Retorna detalhes de treino específico dentro do escopo do time.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), athlete_id (query, opcional).
- **Respostas**: 200 (detalhes), 403, 404, 422.

#### 17. PATCH /api/v1/teams/{team_id}/trainings/{training_id}
- **Summary**: Atualiza treino (escopo time)
- **Description**: Atualiza sessão de treino no escopo de um time.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), athlete_id (query, opcional).
- **Request Body**: TrainingSessionUpdate (JSON).
- **Respostas**: 200 (atualizado), 403, 404, 422.

#### 18. DELETE /api/v1/teams/{team_id}/trainings/{training_id}
- **Summary**: Exclui treino (escopo time)
- **Description**: Soft delete de treino no escopo de um time.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), reason (query, obrigatório, min 5 chars), athlete_id (query, opcional).
- **Respostas**: 200 (excluído), 403, 404, 422.

#### 19. POST /api/v1/teams/{team_id}/trainings/{training_id}/restore
- **Summary**: Restaura treino (escopo time)
- **Description**: Restaura treino excluído no escopo de um time.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), athlete_id (query, opcional).
- **Respostas**: 200 (restaurado), 403, 404, 422.

### Attendance (Presença)

#### 20. GET /api/v1/training_sessions/{training_session_id}/attendance
- **Summary**: Presença em sessão de treino
- **Description**: Lista presença de atletas em uma sessão de treino.
- **Parâmetros**: training_session_id (path, obrigatório, UUID).
- **Respostas**: 200 (presença), 401, 404, 422.

#### 21. GET /api/v1/teams/{team_id}/trainings/{training_id}/attendance
- **Summary**: Presença em treino (escopo time)
- **Description**: Lista presença de atletas em treino dentro do escopo do time.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID).
- **Respostas**: 200 (presença), 403, 404, 422.

#### 22. POST /api/v1/teams/{team_id}/trainings/{training_id}/attendance
- **Summary**: Registra presença
- **Description**: Registra presença de atleta em treino.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID).
- **Request Body**: Dados de presença.
- **Respostas**: 201 (registrado), 403, 404, 422.

#### 23. PATCH /api/v1/teams/{team_id}/trainings/{training_id}/attendance/{attendance_id}
- **Summary**: Atualiza presença
- **Description**: Atualiza registro de presença de atleta.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), attendance_id (path, obrigatório, UUID).
- **Request Body**: Dados atualizados de presença.
- **Respostas**: 200 (atualizado), 403, 404, 422.

#### 24. DELETE /api/v1/teams/{team_id}/trainings/{training_id}/attendance/{attendance_id}
- **Summary**: Remove presença
- **Description**: Remove registro de presença de atleta.
- **Parâmetros**: team_id (path, obrigatório, UUID), training_id (path, obrigatório, UUID), attendance_id (path, obrigatório, UUID).
- **Respostas**: 200 (removido), 403, 404, 422.

### Training Cycles

#### 13. GET /api/v1/training-cycles
- **Summary**: Lista ciclos de treino
- **Description**: Lista ciclos de treino paginados.
- **Parâmetros**: Filtros similares a sessões.
- **Respostas**: 200 (lista), 401, 403, 422.

#### 14. POST /api/v1/training-cycles
- **Summary**: Cria ciclo de treino
- **Description**: Cria novo ciclo de treino.
- **Request Body**: TrainingCycleCreate.
- **Respostas**: 201 (criado), 401, 403, 422.

#### 15. GET /api/v1/training-cycles/{cycle_id}
- **Summary**: Obtém ciclo por ID
- **Description**: Detalhes de ciclo específico.
- **Parâmetros**: cycle_id (path, obrigatório, UUID).
- **Respostas**: 200 (detalhes), 401, 404, 422.

#### 16. PATCH /api/v1/training-cycles/{cycle_id}
- **Summary**: Atualiza ciclo
- **Description**: Atualiza ciclo de treino.
- **Parâmetros**: cycle_id (path, obrigatório, UUID).
- **Request Body**: TrainingCycleUpdate.
- **Respostas**: 200 (atualizado), 401, 403, 404, 422.

#### 17. DELETE /api/v1/training-cycles/{cycle_id}
- **Summary**: Exclui ciclo
- **Description**: Soft delete de ciclo.
- **Parâmetros**: cycle_id (path, obrigatório, UUID), reason (query, obrigatório).
- **Respostas**: 200 (excluído), 401, 403, 404, 422.

#### 18. GET /api/v1/training-cycles/teams/{team_id}/active
- **Summary**: Ciclo ativo do time
- **Description**: Retorna ciclo ativo para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (ciclo), 401, 404, 422.

### Training Microcycles

#### 25. GET /api/v1/training-microcycles
- **Summary**: Lista microciclos
- **Description**: Lista microciclos paginados.
- **Parâmetros**: Filtros.
- **Respostas**: 200 (lista), 401, 403, 422.

#### 26. POST /api/v1/training-microcycles
- **Summary**: Cria microciclo
- **Description**: Cria novo microciclo.
- **Request Body**: TrainingMicrocycleCreate.
- **Respostas**: 201 (criado), 401, 403, 422.

#### 27. GET /api/v1/training-microcycles/teams/{team_id}/current
- **Summary**: Microciclo atual do time
- **Description**: Microciclo corrente para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (microciclo), 401, 404, 422.

#### 28. GET /api/v1/training-microcycles/{microcycle_id}
- **Summary**: Obtém microciclo por ID
- **Description**: Detalhes de microciclo específico.
- **Parâmetros**: microcycle_id (path, obrigatório, UUID).
- **Respostas**: 200 (detalhes), 401, 404, 422.

#### 29. PATCH /api/v1/training-microcycles/{microcycle_id}
- **Summary**: Atualiza microciclo
- **Description**: Atualiza microciclo.
- **Parâmetros**: microcycle_id (path, obrigatório, UUID).
- **Request Body**: TrainingMicrocycleUpdate.
- **Respostas**: 200 (atualizado), 401, 403, 404, 422.

#### 30. DELETE /api/v1/training-microcycles/{microcycle_id}
- **Summary**: Exclui microciclo
- **Description**: Soft delete de microciclo.
- **Parâmetros**: microcycle_id (path, obrigatório, UUID), reason (query, obrigatório).
- **Respostas**: 200 (excluído), 401, 403, 404, 422.

#### 31. GET /api/v1/training-microcycles/{microcycle_id}/summary
- **Summary**: Resumo do microciclo
- **Description**: Estatísticas e resumo de microciclo.
- **Parâmetros**: microcycle_id (path, obrigatório, UUID).
- **Respostas**: 200 (resumo), 401, 404, 422.

### Reports

#### 32. GET /api/v1/reports/training-performance
- **Summary**: Relatório de performance de treino
- **Description**: Análise de performance de treinos incluindo métricas, desvios e tendências.
- **Parâmetros**: Filtros por time, período, etc.
- **Respostas**: 200 (relatório), 401, 403, 422.

#### 33. GET /api/v1/reports/training-trends
- **Summary**: Tendências de treino
- **Description**: Análise de tendências de treino ao longo do tempo.
- **Parâmetros**: Filtros por time, período, etc.
- **Respostas**: 200 (tendências), 401, 403, 422.

#### 34. POST /api/v1/reports/refresh-training-performance
- **Summary**: Atualiza performance de treino
- **Description**: Força recalculação de métricas de performance de treino.
- **Request Body**: Parâmetros de refresh.
- **Respostas**: 200 (atualizado), 401, 403, 422.

#### 35. GET /api/v1/reports/team-training-game-correlation
- **Summary**: Correlação treino-jogo
- **Description**: Analisa correlação entre desempenho em treino e em jogo.
- **Parâmetros**: Filtros por time, período, etc.
- **Respostas**: 200 (correlação), 401, 403, 422.

### Alerts & Suggestions

#### 36. GET /api/v1/training/alerts-suggestions/alerts/team/{team_id}/active
- **Summary**: Alertas ativos do time
- **Description**: Lista alertas ativos para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (alertas), 401, 403, 422.

#### 37. GET /api/v1/training/alerts-suggestions/alerts/team/{team_id}/history
- **Summary**: Histórico de alertas
- **Description**: Histórico de alertas para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (histórico), 401, 403, 422.

#### 38. GET /api/v1/training/alerts-suggestions/alerts/team/{team_id}/stats
- **Summary**: Estatísticas de alertas
- **Description**: Estatísticas de alertas para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (stats), 401, 403, 422.

#### 39. POST /api/v1/training/alerts-suggestions/alerts/{alert_id}/dismiss
- **Summary**: Descarta alerta
- **Description**: Descarta um alerta específico.
- **Parâmetros**: alert_id (path, obrigatório, UUID).
- **Respostas**: 200 (descartado), 401, 403, 404, 422.

#### 40. GET /api/v1/training/alerts-suggestions/suggestions/team/{team_id}/pending
- **Summary**: Sugestões pendentes
- **Description**: Sugestões pendentes para um time.
- **Parâmetros**: team_id (path, obrigatório, UUID).
- **Respostas**: 200 (sugestões), 401, 403, 422.

## Notas Gerais
- Todos os endpoints requerem autenticação via HTTPBearer.
- Headers comuns: X-Request-ID (opcional), x-organization-id (opcional).
- Baseado na especificação OpenAPI gerada em `docs/_generated/openapi.json`.
- Última atualização: 2026-02-04.
- Total de endpoints: 40+ (análise completa com training scoped, attendance e reports adicionados).