# INVARIANTS_TRAINING.md — Invariantes do Módulo Training

> Gerado por AR_075 (2026-02-24). Formato: SPEC YAML v1.0.

---

## INV-TRAIN-001

```yaml
id: INV-TRAIN-001
class: B
name: fn_invalidate_analytics_cache
rule: >
  Trigger tr_invalidate_analytics_cache dispara AFTER INSERT OR DELETE OR UPDATE em training_sessions,
  chamando fn_invalidate_analytics_cache() para invalidar cache de analytics.
table: training_sessions
trigger: tr_invalidate_analytics_cache
evidence: "Hb Track - Backend/docs/_generated/schema.sql:5314 — CREATE TRIGGER tr_invalidate_analytics_cache"
status: IMPLEMENTADO
rationale: >
  Cache de analytics (tabela analytics_cache) deve ser invalidado sempre que training_sessions é modificado.
  Trigger garante que agregações (participação, frequência, wellness médio) são recalculadas
  ao invés de usar dados stale.
  Integração com sistema de cache de métricas de treino.
```

---

## INV-TRAIN-002

```yaml
id: INV-TRAIN-002
class: C1
name: team_registrations_multiple_active_bonds_v12
rule: >
  A partir da V1.2, múltiplos vínculos ativos simultâneos são PERMITIDOS em team_registrations.
  Regra de não-sobreposição RDB10 foi REVOGADA.
  Serviço NÃO deve bloquear inserção de novo vínculo ativo.
table: team_registrations
evidence: "Hb Track - Backend/docs/_generated/schema.sql COMMENT ON TABLE team_registrations (V1.2: múltiplos vínculos ativos simultâneos permitidos)"
status: IMPLEMENTADO
note: >
  V1.2 revogou RDB10 (bloqueio de sobreposição de vínculos ativos).
  Atleta pode ter vínculo ativo em múltiplas equipes simultaneamente.
  Serviço deve permitir essa flexibilidade sem validação restritiva.
rationale: >
  Mudança de regra de negócio para permitir atletas multi-filiados (e.g., time titular + time reserva).
  Antes: RDB10 bloqueava sobreposição de vínculos.
  Agora: Sobreposição permitida — sistema suporta múltiplos vínculos ativos.
```

---

## INV-TRAIN-003

```yaml
id: INV-TRAIN-003
class: A
name: ux_wellness_unique_per_athlete_session
rule: >
  ux_wellness_pre_session_athlete e ux_wellness_post_session_athlete garantem
  no máximo 1 registro wellness PRE e 1 POST por atleta por sessão de treino.
  (soft-delete aware: WHERE deleted_at IS NULL)
table: wellness_records
constraints:
  - ux_wellness_pre_session_athlete (UNIQUE INDEX em player_id, training_session_id WHERE measurement_type='pre' AND deleted_at IS NULL)
  - ux_wellness_post_session_athlete (UNIQUE INDEX em player_id, training_session_id WHERE measurement_type='post' AND deleted_at IS NULL)
evidence: >
  Hb Track - Backend/docs/_generated/schema.sql:5286 — ux_wellness_post_session_athlete;
  schema.sql:5293 — ux_wellness_pre_session_athlete
status: IMPLEMENTADO
rationale: >
  Wellness é medido antes (PRE) e depois (POST) de cada sessão de treino.
  Duplicatas comprometem integridade de métricas de recuperação e fadiga.
  Soft-delete aware: unique index ignora registros deleted_at IS NOT NULL.
  Garante 1 wellness PRE + 1 wellness POST por atleta por treino no máximo.
```
