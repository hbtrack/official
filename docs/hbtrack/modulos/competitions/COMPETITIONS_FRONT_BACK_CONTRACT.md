# COMPETITIONS_FRONT_BACK_CONTRACT.md

Status: DRAFT
Versão: v0.1.0
Tipo de Documento: Front-Back Contract (Normativo Operacional / SSOT)
Módulo: COMPETITIONS
Fase: FASE_0
Autoridade: NORMATIVO_OPERACIONAL
Owners:
- Arquitetura (Arquiteto): Agente Arquiteto
- Backend: Agente Executor
- Frontend: Agente Executor
- Auditoria: Agente Testador

Última revisão: 2026-02-25
Próxima revisão recomendada: 2026-03-15

Dependências:
- INVARIANTS_COMPETITIONS.md
- COMPETITIONS_USER_FLOWS.md
- COMPETITIONS_SCREENS_SPEC.md
- AR_BACKLOG_COMPETITIONS.md
- TEST_MATRIX_COMPETITIONS.md

Âncoras de evidência:
- openapi.json: `Hb Track - Backend/docs/ssot/openapi.json`
- Routers: `Hb Track - Backend/app/api/v1/routers/competitions.py` + `competitions_v2.py`

---

## 1. Objetivo (Normativo)

Especificar os contratos mínimos entre frontend e backend para o módulo Competitions. Cada CONTRACT-COMP-* define: operação, payload, resposta, erros obrigatórios e flags funcionais que o frontend DEVE interpretar.

---

## 2. Escopo

### 2.1 Dentro do escopo
- Contratos dos endpoints do módulo Competitions (v1 e v2)
- Campos obrigatórios de request e response
- Códigos de erro funcionais
- Flags de pendência não-bloqueante

### 2.2 Fora do escopo
- Autenticação/autorização
- Endpoints de outros módulos
- Paginação avançada
- Filtros opcionais não funcionalmente críticos

---

## 3. Convenções

- **Erro bloqueante**: HTTP 4xx que impede conclusão da ação
- **Aviso/pendência**: campo no response body com flag
- **Invariante bloqueante**: violação resulta em HTTP 422/409/400
- **Pendência não-bloqueante**: violação resulta em persistência + campo `warnings` no response

---

## 4. Contratos

---

### CONTRACT-COMP-001 — Listar Competições

**operationId**: `listCompetitions`
**Endpoint**: `GET /api/v1/competitions`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001
**Telas**: SCREEN-COMP-001

#### Request

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| status | query string | não | Filtrar por status |
| season | query string | não | Filtrar por temporada |
| organization_id | via auth token | sim | Inferido do JWT |

#### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "season": "string",
      "modality": "masculino|feminino|misto",
      "status": "draft|active|finished|cancelled",
      "points_per_win": 2,
      "points_per_draw": 1,
      "points_per_loss": 0,
      "match_count": 10,
      "created_at": "ISO8601"
    }
  ],
  "total": 0
}
```

#### Erros

| Código HTTP | Motivo |
|-------------|--------|
| 401 | Não autenticado |
| 403 | Sem permissão |

---

### CONTRACT-COMP-002 — Criar Competição

**operationId**: `createCompetitionV2`
**Endpoint**: `POST /api/v1/competitions/v2`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001
**Telas**: SCREEN-COMP-002
**Invariantes**: INV-COMP-001, INV-COMP-002, INV-COMP-007, INV-COMP-009

#### Request Body

```json
{
  "name": "string (required)",
  "season": "string (required)",
  "modality": "masculino|feminino|misto (required)",
  "points_per_win": "integer >= 1 (required, NOT NULL — INV-COMP-007)",
  "points_per_draw": "integer >= 0 (optional, default 1)",
  "points_per_loss": "integer >= 0 (optional, default 0)",
  "tiebreaker_rules": "object JSONB (optional)"
}
```

#### Response 201

```json
{
  "id": "uuid",
  "name": "string",
  "season": "string",
  "modality": "string",
  "status": "draft",
  "points_per_win": 2,
  "points_per_draw": 1,
  "points_per_loss": 0,
  "created_at": "ISO8601"
}
```

#### Erros bloqueantes

| Código HTTP | Código Negócio | Motivo | Invariante |
|-------------|----------------|--------|------------|
| 409 | COMPETITION_DUPLICATE | name+season já existe na org | INV-COMP-009 |
| 422 | VALIDATION_ERROR | modality fora do domínio | INV-COMP-002 |
| 422 | VALIDATION_ERROR | points_per_win ausente/null | INV-COMP-007 |

---

### CONTRACT-COMP-003 — Detalhe Completo de Competição

**operationId**: `getCompetitionFull`
**Endpoint**: `GET /api/v1/competitions/v2/{competition_id}/full`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-001..006
**Telas**: SCREEN-COMP-003

#### Response 200

```json
{
  "id": "uuid",
  "name": "string",
  "season": "string",
  "modality": "string",
  "status": "string",
  "points_per_win": 2,
  "points_per_draw": 1,
  "points_per_loss": 0,
  "phases": [],
  "opponent_teams": [],
  "match_count": 10,
  "pending_count": 3,
  "warnings": ["string"]
}
```

#### Campo `pending_count`
- Contagem de adversários ou atletas com pendência não resolvida
- Frontend DEVE exibir badge se `pending_count > 0`

---

### CONTRACT-COMP-004 — Gestão de Fases

**operationIds**: `listCompetitionPhases`, `createCompetitionPhase`, `updateCompetitionPhase`, `deleteCompetitionPhase`
**Endpoints**:
- `GET /api/v1/competitions/{competition_id}/phases`
- `POST /api/v1/competitions/{competition_id}/phases`
- `PATCH /api/v1/competitions/{competition_id}/phases/{phase_id}`
- `DELETE /api/v1/competitions/{competition_id}/phases/{phase_id}`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-003
**Telas**: SCREEN-COMP-004
**Invariantes**: INV-COMP-003, INV-COMP-019

#### POST Body

```json
{
  "name": "string (required)",
  "start_date": "date (required)",
  "end_date": "date (required)",
  "type": "string (optional)"
}
```

#### DELETE — Soft Delete
- Obrigatório incluir `deleted_reason: string` no body
- Retorna 422 se `deleted_reason` ausente (INV-COMP-003)

---

### CONTRACT-COMP-005 — Gestão de Equipes Adversárias

**operationIds**: `listOpponentTeams`, `createOpponentTeam`, `bulkCreateOpponentTeams`, `updateOpponentTeam`
**Endpoints**:
- `GET /api/v1/competitions/{competition_id}/opponent-teams`
- `POST /api/v1/competitions/{competition_id}/opponent-teams`
- `POST /api/v1/competitions/{competition_id}/opponent-teams/bulk`
- `PATCH /api/v1/competitions/{competition_id}/opponent-teams/{team_id}`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-004, FLOW-COMP-007
**Telas**: SCREEN-COMP-005
**Invariantes**: INV-COMP-011, INV-COMP-027

#### POST Body (single)

```json
{
  "name": "string (required)",
  "linked_team_id": "uuid (optional)"
}
```

#### Response 201 (single)

```json
{
  "id": "uuid",
  "name": "string",
  "canonical_name": "string (normalized)",
  "linked_team_id": "uuid|null",
  "is_pending": false
}
```

#### Campo `is_pending`
- `true` se canonical_name é ambíguo (parcialmente coincide com outro)
- Frontend DEVE exibir aviso visual

#### POST /bulk Response

```json
{
  "created": [],
  "skipped": [{"name": "...", "reason": "DUPLICATE_CANONICAL"}],
  "pending": [{"name": "...", "similar_to": "..."}]
}
```

#### Erros bloqueantes

| Código HTTP | Código Negócio | Motivo | Invariante |
|-------------|----------------|--------|------------|
| 409 | OPPONENT_TEAM_DUPLICATE | canonical_name já existe | INV-COMP-011 |

---

### CONTRACT-COMP-006 — Criar Partida

**operationId**: `createCompetitionMatch`
**Endpoint**: `POST /api/v1/competitions/{competition_id}/matches`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-005
**Telas**: SCREEN-COMP-006
**Invariantes**: INV-COMP-014, INV-COMP-016, INV-COMP-018, INV-COMP-019

#### Request Body

```json
{
  "phase_id": "uuid (required — INV-COMP-019)",
  "match_date": "datetime (required)",
  "home_team_id": "uuid (required)",
  "away_team_id": "uuid (required, diferente de home — INV-COMP-018)",
  "home_score": "integer >= 0 (optional, null = draft — INV-COMP-016)",
  "away_score": "integer >= 0 (optional, null = draft — INV-COMP-016)",
  "external_reference": "string (optional, unique por competition — INV-COMP-014)",
  "status": "draft|scheduled|in_progress|finished|cancelled (default: draft)"
}
```

#### Response 201

```json
{
  "id": "uuid",
  "phase_id": "uuid",
  "home_team_id": "uuid",
  "away_team_id": "uuid",
  "home_score": null,
  "away_score": null,
  "status": "draft",
  "counts_for_standings": false,
  "match_date": "ISO8601"
}
```

#### Campo `counts_for_standings`
- `false` para status=draft ou sem placar (INV-COMP-012)
- Frontend DEVE exibir indicador diferente para partidas que não contam

#### Erros bloqueantes

| Código HTTP | Código Negócio | Motivo | Invariante |
|-------------|----------------|--------|------------|
| 409 | MATCH_EXTERNAL_REF_DUPLICATE | external_reference duplicado | INV-COMP-014 |
| 422 | SAME_TEAM | home_team_id == away_team_id | INV-COMP-018 |
| 422 | INVALID_SCORE | score < 0 | INV-COMP-016 |
| 422 | PHASE_NOT_IN_COMPETITION | phase_id não pertence | INV-COMP-019 |

---

### CONTRACT-COMP-007 — Atualizar Resultado de Partida

**operationId**: `updateMatchResult`
**Endpoint**: `PATCH /api/v1/competitions/{competition_id}/matches/{match_id}/result`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-005
**Telas**: SCREEN-COMP-006
**Invariantes**: INV-COMP-016, INV-COMP-021

#### Request Body

```json
{
  "home_score": "integer >= 0 (required — INV-COMP-016)",
  "away_score": "integer >= 0 (required — INV-COMP-016)",
  "status": "finished|cancelled (required)"
}
```

#### Response 200

```json
{
  "id": "uuid",
  "home_score": 25,
  "away_score": 20,
  "status": "finished",
  "counts_for_standings": true,
  "standings_recalculated": true
}
```

#### Campo `standings_recalculated`
- `true` se recálculo de standings foi triggado
- Frontend PODE invalidar cache/refetch da tela de classificação

---

### CONTRACT-COMP-008 — Tabela de Classificação

**operationId**: `getCompetitionStandings`
**Endpoint**: `GET /api/v1/competitions/{competition_id}/standings`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-006
**Telas**: SCREEN-COMP-007
**Invariantes**: INV-COMP-008, INV-COMP-012, INV-COMP-015, INV-COMP-017, INV-COMP-019, INV-COMP-021, INV-COMP-024

#### Request

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|------------|
| phase_id | query uuid | não | Filtrar por fase |

#### Response 200

```json
{
  "competition_id": "uuid",
  "phase_id": "uuid|null",
  "scoring_rules": {
    "points_per_win": 2,
    "points_per_draw": 1,
    "points_per_loss": 0
  },
  "tiebreaker_rules": "object|null",
  "standings": [
    {
      "position": 1,
      "team_id": "uuid",
      "team_name": "string",
      "is_our_team": true,
      "points": 10,
      "played": 5,
      "wins": 5,
      "draws": 0,
      "losses": 0,
      "goals_for": 125,
      "goals_against": 98,
      "goal_difference": 27
    }
  ],
  "excluded_matches_count": 2,
  "warnings": ["2 partidas em rascunho não contabilizadas"]
}
```

#### Campos críticos para o frontend

| Campo | Obrigação do Frontend |
|-------|----------------------|
| `scoring_rules` | NUNCA hardcodar ppw/ppd/ppl — sempre usar do response (INV-COMP-008) |
| `is_our_team` | DEVE destacar esta linha visualmente (PRD §8.3) |
| `excluded_matches_count` | DEVE exibir aviso se > 0 |

---

### CONTRACT-COMP-009 — Importação via IA / PDF

**operationIds**: `parsePdfWithAI`, `importFromAI`
**Endpoints**:
- `POST /api/v1/competitions/v2/parse-pdf`
- `POST /api/v1/competitions/v2/{competition_id}/import-from-ai`
**Prioridade**: ALTA
**Flows**: FLOW-COMP-002, FLOW-COMP-007
**Telas**: SCREEN-COMP-008
**Invariantes**: INV-COMP-014, INV-COMP-023, INV-COMP-029

#### parsePdfWithAI — Request
- `Content-Type: multipart/form-data`
- Campo: `file` (PDF)

#### parsePdfWithAI — Response 200

```json
{
  "extraction_id": "uuid",
  "competition": {"name": "string", "season": "string", "modality": "string", "confidence": 0.95},
  "phases": [],
  "opponent_teams": [{"name": "string", "confidence": 0.9, "similar_existing": "uuid|null"}],
  "matches": [
    {
      "home_team": "string",
      "away_team": "string",
      "home_score": 25,
      "away_score": 20,
      "match_date": "ISO8601",
      "external_reference": "string",
      "confidence": 0.98
    }
  ],
  "warnings": ["Adversário 'CEPEA' 80% similar a 'CEPAEA' já existente"]
}
```

#### importFromAI — Request Body

```json
{
  "extraction_id": "uuid",
  "confirmed_mappings": {
    "opponent_teams": [{"extracted_name": "string", "map_to_id": "uuid|null", "create_new": true}]
  }
}
```

#### importFromAI — Response 200

```json
{
  "competition_id": "uuid",
  "phases_created": 2,
  "teams_created": 5,
  "matches_created": 10,
  "matches_skipped": 1,
  "pending_items": [{"type": "opponent_team", "name": "string", "reason": "AMBIGUOUS_ALIAS"}]
}
```

#### Campo `pending_items`
- Itens não resolvidos automaticamente (INV-COMP-023)
- Frontend DEVE redirecionar para resolução de pendências

---

## 5. Mapa de Rastreabilidade

| CONTRACT ID | operationId | Invariantes Alvo | Telas | Fase |
|-------------|-------------|-----------------|-------|------|
| CONTRACT-COMP-001 | listCompetitions | INV-001 | SCREEN-001 | FASE_0 |
| CONTRACT-COMP-002 | createCompetitionV2 | INV-001,002,007,009 | SCREEN-002 | FASE_0 |
| CONTRACT-COMP-003 | getCompetitionFull | todos | SCREEN-003 | FASE_0 |
| CONTRACT-COMP-004 | *CompetitionPhase | INV-003,019 | SCREEN-004 | FASE_0 |
| CONTRACT-COMP-005 | *OpponentTeam | INV-011,027 | SCREEN-005 | FASE_0 |
| CONTRACT-COMP-006 | createCompetitionMatch | INV-014,016,018,019 | SCREEN-006 | FASE_0 |
| CONTRACT-COMP-007 | updateMatchResult | INV-016,021 | SCREEN-006 | FASE_0 |
| CONTRACT-COMP-008 | getCompetitionStandings | INV-008,012,015,017,019,021,024 | SCREEN-007 | FASE_0 |
| CONTRACT-COMP-009 | parsePdfWithAI, importFromAI | INV-014,023,029 | SCREEN-008 | FASE_0 |

---

## 6. Itens Pendentes para Validação Humana

| # | Item | Status |
|---|------|--------|
| P-001 | Paginação: cursor ou offset? | PENDENTE |
| P-002 | standings_recalculated: síncrono ou async (Celery)? | PENDENTE |
| P-003 | Códigos de erro de negócio: strings ou numéricos? | PENDENTE |
| P-004 | Campo `warnings`: lista de strings ou objetos estruturados? | PENDENTE |
