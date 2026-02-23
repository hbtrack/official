# INVARIANTS_SCOUT.md — Invariantes do Módulo Scout

> Gerado por AR_049 (2026-02-22). Formato: SPEC YAML v1.0.

---

## INV-SCOUT-001

```yaml
id: INV-SCOUT-001
class: A
name: ck_match_events_source
rule: "source IN ('live', 'video', 'post_game_correction')"
table: match_events
constraint: ck_match_events_source
evidence: "Hb Track - Backend/app/models/match_event.py:55"
rationale: >
  Rastreabilidade da origem do dado de scout.
  'post_game_correction' indica dado corrigido após o jogo — requer auditoria extra.
  Domínio fechado garante consistência analítica.
```

---

## INV-SCOUT-002

```yaml
id: INV-SCOUT-002
class: A
name: ck_match_events_period
rule: "period_number >= 1"
table: match_events
constraint: ck_match_events_period
evidence: "Hb Track - Backend/app/models/match_event.py:52"
rationale: >
  Períodos de handebol são numerados a partir de 1 (1=1º tempo, 2=2º tempo,
  3+=prorrogação). Período 0 ou negativo é fisicamente impossível no esporte.
```

---

## INV-SCOUT-003

```yaml
id: INV-SCOUT-003
class: A
name: ck_match_events_coords
rule: >
  (x_coord IS NULL OR x_coord BETWEEN 0 AND 100)
  AND
  (y_coord IS NULL OR y_coord BETWEEN 0 AND 100)
table: match_events
constraints:
  - ck_match_events_x_coord
  - ck_match_events_y_coord
evidence: "Hb Track - Backend/app/models/match_event.py:57-58"
rationale: >
  Coordenadas representam posição normalizada no campo (0-100% em cada eixo).
  NULL é permitido: evento sem posição (ex: substituição, intervalo).
  Valores fora de 0-100 indicam erro de captura.
```

---

## INV-SCOUT-004

```yaml
id: INV-SCOUT-004
class: C1
name: goalkeeper_save_requires_related_event
rule: "WHEN event_type = 'goalkeeper_save' THEN related_event_id IS NOT NULL"
layer: "Pydantic validator (app/schemas/match_events.py — ScoutEventCreate)"
evidence: "Hb Track - Backend/app/schemas/match_events.py (ScoutEventCreate)"
known_gap: >
  Esta invariante existe APENAS na camada Pydantic (validator de serviço).
  INSERT direto no banco (bypass da API) não é protegido por constraint de DB.
  Futura INV Classe B (trigger no DB) seria necessária para garantia end-to-end.
rationale: >
  Defesa de goleiro é sempre relacionada a um chute anterior (event_type='shot').
  Sem related_event_id, o evento goalkeeper_save fica órfão analiticamente —
  impossível calcular eficiência de goleiro corretamente.
```
