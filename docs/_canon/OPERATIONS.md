---
doc_type: canon
authority: operational-reference
version: "1.0.0"
status: active
---

# OPERATIONS.md — Referência Operacional Consolidada

> Carregado on-demand pelo orchestrator conforme §7 do docs/_canon/AGENT_INSTRUCTIONS.md.
> OPERATIONS.md §1 é fonte autoritativa de soberania (LAYOUT.md §1A redireciona para cá).
> RULES.md §5 é fonte autoritativa de hierarquia de precedência (OPERATIONS.md §3 redireciona para lá).

## §1 SOBERANIA DE ARTEFATOS

| Classe                        | Soberano | Path canônico                              | Derivados                              |
|-------------------------------|----------|--------------------------------------------|----------------------------------------|
| Governança do sistema         | Sim      | `.contract_driven/*`                       | `_reports/`, `generated/`              |
| Templates de scaffold         | Não      | `.contract_driven/templates/`              | N/A                                    |
| Prompts operacionais          | Não      | `.contract_driven/agent_prompts/`          | `_reports/agent_execution/`            |
| Canon global (docs)           | Sim      | `docs/_canon/*`                            | `_reports/`                            |
| Docs normativos de módulo     | Sim      | `docs/hbtrack/modulos/<module>/*`          | `_reports/`                            |
| Estudos e ideação humana      | Não      | `docs/guias/*`                             | N/A                                    |
| Contrato OpenAPI              | Sim      | `contracts/openapi/*`                      | `generated/resolved_policy/*`          |
| Schemas de domínio (JSON Schema)| Sim    | `contracts/schemas/*`                      | `generated/`, `generated/ui-types/`    |
| Workflows (Arazzo)            | Sim      | `contracts/workflows/*`                    | `generated/*`                          |
| Eventos (AsyncAPI)            | Sim      | `contracts/asyncapi/*`                     | `generated/contracts/asyncapi/*`       |
| DSS / apoio decisório         | Não      | `docs/hbtrack/decisoes/*`                  | N/A                                    |

Regras absolutas:
- `_reports/` e `generated/` são sempre derivados. Nunca sobrepõem fontes soberanas.
- `docs/guias/` é material humano de estudo/ideação. Nunca define SSOT, DONE, status operacional ou próxima ação permitida.
- Templates em `.contract_driven/templates/` são scaffold — agentes instanciam a partir deles.
- `docs/hbtrack/decisoes/` nunca tem linguagem de autoridade sem disclaimer explícito.
- `docs/guias/` nunca pode usar linguagem de SSOT/autoridade sem disclaimer explícito no topo.

## §2 BOUNDARY RULES CRÍTICOS DE MÓDULOS

| Módulo          | Domínio                                              | Fora do escopo deste módulo                           |
|-----------------|------------------------------------------------------|-------------------------------------------------------|
| users           | pessoa, perfil, dados biográficos                    | autenticação, autorização, credenciais, sessões, JWT  |
| identity_access | autenticação, autorização, RBAC, JWT, MFA, sessões   | dados de perfil de pessoa                             |
| seasons         | períodos competitivos, calendário da temporada        | resultados de partidas, métricas de atletas           |
| teams           | composição de elenco, staff, grupos                   | resultados de partidas, métricas individuais          |
| training        | planejamento e registro de treinos                   | regras de competição, métricas de wellness            |
| wellness        | bem-estar, recuperação, carga subjetiva              | dados médicos clínicos, prontuário                    |
| medical         | prontuário, lesões, liberações médicas               | planejamento de treino                                |
| competitions    | estrutura e calendário de campeonatos                 | resultado de partidas individuais, treinos            |
| matches         | registro de partidas, placar, eventos de jogo         | estrutura de campeonato, dados de treino              |
| scout           | análise tática e estatística de partidas              | gerenciamento de elenco, prescrição de treino         |
| exercises       | biblioteca de exercícios e variações                  | prescrição de treino (pertence a training)            |
| analytics       | agregação e análise cross-módulo                      | coleta primária de dados (pertence a cada módulo)     |
| reports         | geração e exportação de relatórios                    | lógica de negócio dos dados reportados                |
| ai_ingestion    | ingestão e processamento de dados por IA              | decisão sobre dados (pertence ao módulo de domínio)   |
| audit           | rastreabilidade de ações no sistema                  | lógica de negócio de qualquer módulo                  |
| notifications   | entrega de notificações                              | regras de negócio que geram as notificações           |
| video           | captura, ingestão, clipping e distribuição técnica interna de mídia | broadcast/OTT como domínio de produto autônomo        |

Regra: se um artefato sob módulo X tentar definir comportamento do domínio de módulo Y → BLOCKED_SCOPE_OVERFLOW.

## §3 HIERARQUIA DE PRECEDÊNCIA

Fonte autoritativa: `.contract_driven/CONTRACT_SYSTEM_RULES.md §5`. Em conflito entre esta seção e RULES.md §5, RULES.md §5 prevalece.

1. `DOMAIN_AXIOMS.json` — invariantes machine-readable, nunca sobrescritos
2. `.contract_driven/CONTRACT_SYSTEM_RULES.md` — regras operacionais vinculantes
   2a. `.contract_driven/templates/api/api_rules.yaml` — convenções de API HTTP
3. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` — layout canônico de filesystem
4. Contratos soberanos em `contracts/` (OpenAPI > JSON Schema > AsyncAPI > Arazzo)
   4a. `docs/_canon/HANDBALL_RULES_DOMAIN.md` — quando gatilho esportivo ativo
5. `.contract_driven/templates/api/api_rules.yaml`, `docs/_canon/{DATA_CONVENTIONS,SECURITY_RULES}.md`, `OPERATIONS.md §5` (modelo de erros)
6–11. `docs/hbtrack/modulos/<module>/` (DOMAIN_RULES > SPORT_SCIENCE > INVARIANTS > STATE_MODEL > PERMISSIONS > UI_CONTRACT)
12. Implementação
13. `generated/resolved_policy/` e `_reports/` — derivados, sem autoridade sobre 1–12

Conflito no mesmo nível → BLOCKED_CONTRACT_CONFLICT.
Conflito entre níveis → o nível mais alto (menor número) prevalece.

## §4 ARTEFATOS OBRIGATÓRIOS POR MÓDULO

| Artefato                              | Obrigatório | Condicional quando                          |
|---------------------------------------|-------------|---------------------------------------------|
| MODULE_SCOPE_<MODULE>.md              | sempre      | —                                           |
| DOMAIN_RULES_<MODULE>.md             | sempre      | —                                           |
| INVARIANTS_<MODULE>.md               | sempre      | —                                           |
| TEST_MATRIX_<MODULE>.md              | sempre      | —                                           |
| SPORT_SCIENCE_RULES_<MODULE>.md      | não         | módulo ∈ {training, wellness, medical}      |
| STATE_MODEL_<MODULE>.md              | não         | módulo tem máquina de estados               |
| PERMISSIONS_<MODULE>.md              | não         | módulo tem RBAC específico                  |
| ERRORS_<MODULE>.md                   | não         | módulo define error codes próprios          |
| UI_CONTRACT_<MODULE>.md              | não         | módulo tem superfície de UI                 |

Ausência de artefato obrigatório → BLOCKED_REQUIRED_ARTIFACT_MISSING. Parar.

## §5 REGRAS CORE DE VALIDAÇÃO

1. Enum fechado: rejeitar qualquer valor de enum não definido em DOMAIN_AXIOMS.json.
2. Formatos globais obrigatórios: UUID v4, date_only (YYYY-MM-DD), timestamp_utc (RFC3339Z).
3. Error shape: toda resposta de erro deve usar Problem+JSON (RFC 7807) — media type `application/problem+json` — com campos: type, title, status, traceId. SSOT: `.contract_driven/templates/api/api_rules.yaml` + `contracts/openapi/components/schemas/shared/problem.yaml`.
4. Drift: `generated/resolved_policy/<module>.sync.resolved.yaml` deve refletir os contratos soberanos. Se divergir → BLOCKED_SCHEMA_DRIFT.
5. Derivados: nunca comparar artefatos derivados sem normalizar (remover markers de geração) antes do diff.
6. Sem interpretação LLM para validação semântica: usar apenas validação de schema/regex.

## §6 NAMING CONVENTIONS ESSENCIAIS

| Contexto                     | Convenção       | Exemplo                              |
|------------------------------|-----------------|--------------------------------------|
| Módulos e paths              | snake_case      | `identity_access`, `ai_ingestion`    |
| Campos de schema JSON        | snake_case      | `session_id`, `started_at`           |
| Campos de response de API    | camelCase       | `sessionId`, `startedAt`             |
| Variáveis de código          | snake_case (py) | `training_session`, `player_id`      |
| IDs de recursos              | UUID v4         | `550e8400-e29b-41d4-a716-446655440000`|
| Branches de git              | kebab-case      | `feat/training-session-endpoint`     |

Violação de naming em path de contrato soberano → BLOCKED_PATH_VIOLATION.

---

## §7 DESENVOLVIMENTO LOCAL — RESET E RESEED DO BANCO

### Pré-requisitos

- PostgreSQL rodando em `localhost:5433` (ou `DB_HOST`/`DB_PORT` configurados)
- Virtualenv ativo: `.venv/bin/activate`

### Resetar banco de desenvolvimento

```bash
# 1. Dropar e recriar o banco de desenvolvimento
psql -h localhost -p 5433 -U hbtrack_dev -d postgres -c "DROP DATABASE IF EXISTS hb_track_dev;"
psql -h localhost -p 5433 -U hbtrack_dev -d postgres -c "CREATE DATABASE hb_track_dev;"

# 2. Aplicar todas as migrations
python manage.py migrate

# 3. Popular com dados demo
python manage.py seed_demo
```

### Resetar banco de testes (unittest)

O banco de testes (`hb_track_test`) é criado e destruído automaticamente pelo pytest.
Para forçar recriação:

```bash
python -m pytest --reuse-db=false src/ tests/
```

### Seed manual (sem reset)

Se o banco já existe e você só quer adicionar dados demo:

```bash
python manage.py seed_demo
```

O comando `seed_demo` é idempotente: não duplica registros se executado mais de uma vez (verifica por `username`/`name` antes de criar).

### Dados criados pelo seed_demo

| Recurso         | Valor demo                          |
|-----------------|-------------------------------------|
| Usuário admin   | `admin@hbtrack.dev` / senha: `admin123` |
| Usuário treinador | `coach@hbtrack.dev` / senha: `coach123` |
| Time demo       | `Handebol Demo FC`                  |
| Temporada demo  | `Temporada 2026`                    |
| Sessões treino  | 5 sessões de treino demo            |

