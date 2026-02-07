<!-- STATUS: NEEDS_REVIEW -->

# Manual do Sistema HB Track - Backend

> **Versão:** 1.0  
> **Última atualização:** Janeiro 2026  
> **Status:** Produção-Ready

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura de Autorização e Escopo](#2-arquitetura-de-autorização-e-escopo)
3. [Rotas Canônicas da API](#3-rotas-canônicas-da-api)
4. [Módulos Implementados](#4-módulos-implementados)
5. [Sistema de Cache](#5-sistema-de-cache)
6. [Performance e Índices](#6-performance-e-índices)
7. [Relatórios e Alertas](#7-relatórios-e-alertas)
8. [Guia de Testes](#8-guia-de-testes)
9. [Roadmap e Próximos Passos](#9-roadmap-e-próximos-passos)

---

## 1. Visão Geral

O HB Track é um sistema de gerenciamento esportivo com foco em **handebol**, projetado para:

- Gerenciar organizações, equipes, temporadas e atletas
- Controlar treinos, partidas e presenças
- Monitorar carga de trabalho e bem-estar dos atletas
- Gerar relatórios consolidados e alertas automáticos

### 1.1 Princípios de Design

| Princípio | Descrição |
|-----------|-----------|
| **Escopo Organizacional** | Todo dado pertence a uma organização; usuários só acessam dados de suas organizações |
| **Autorização por Papel + Vínculo** | Acesso depende do papel (dirigente/coordenador/treinador) E do vínculo ativo |
| **Rotas Canônicas** | IDs explícitos no path, escopo derivado da hierarquia (team → organization) |
| **Soft Delete** | Registros são marcados como deletados, nunca removidos fisicamente |

### 1.2 Stack Tecnológico

- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy (síncrono)
- **Banco de Dados:** PostgreSQL 17.7 (Neon)
- **Migrations:** Alembic
- **Cache:** cachetools.TTLCache (in-memory)
- **Autenticação:** JWT + bcrypt

---

## 2. Arquitetura de Autorização e Escopo

### 2.1 Modelo de Autenticação

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE AUTENTICAÇÃO                    │
├─────────────────────────────────────────────────────────────┤
│  Request → Token JWT → get_current_context() → Validação    │
│                                                             │
│  Se token ausente/inválido → 401 Unauthorized               │
│  Se papel/vínculo inválido → 403 Forbidden                  │
│  Se recurso não encontrado → 404 Not Found                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Papéis do Sistema

| Papel | Código | Permissões |
|-------|--------|------------|
| **Superadmin** | `superadmin` | Acesso total, bypass de escopo organizacional |
| **Dirigente** | `dirigente` | CRUD completo na organização |
| **Coordenador** | `coordenador` | Gerenciamento de equipes e atletas |
| **Treinador** | `treinador` | Gestão de treinos e presenças |

### 2.3 Helpers de Autorização

Localizados em `app/core/permissions.py`:

| Helper | Função |
|--------|--------|
| `require_role(ctx, roles)` | Valida se usuário tem um dos papéis permitidos |
| `require_active_membership(ctx)` | Exige vínculo ativo com organização |
| `require_org_scope(ctx, org_id)` | Valida escopo organizacional |
| `require_team_scope(ctx, team_id, db)` | Valida escopo de equipe |
| `require_team_registration(ctx, team_id, athlete_id, db)` | Valida vínculo atleta-equipe |
| `require_team_registration_in_season(...)` | Valida vínculo com janela de temporada |

### 2.4 Dependency Injection

```python
# Uso padrão em rotas
from app.core.auth import permission_dep

@router.get("/teams/{team_id}/trainings")
async def list_trainings(
    team_id: UUID,
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["dirigente", "coordenador", "treinador"],
        require_team=True
    )),
    db: Session = Depends(get_db)
):
    ...
```

### 2.5 Endpoint de Contexto

```
GET /api/v1/auth/context
```

Retorna informações do usuário autenticado:
- Papel atual
- Organização vinculada
- Membership ativo
- Equipes com vínculo ativo

---

## 3. Rotas Canônicas da API

### 3.1 Padrão de URLs

```
/api/v1/teams/{team_id}/[recurso]
/api/v1/teams/{team_id}/matches/{match_id}/[sub-recurso]
/api/v1/teams/{team_id}/trainings/{training_id}/[sub-recurso]
```

### 3.2 Mapa de Rotas

#### Organizações e Equipes

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/organizations` | Lista organizações |
| POST | `/organizations` | Cria organização |
| GET | `/organizations/{id}` | Obtém organização |
| PATCH | `/organizations/{id}` | Atualiza organização |
| GET | `/teams` | Lista equipes |
| POST | `/teams` | Cria equipe |
| GET | `/teams/{id}` | Obtém equipe |
| PATCH | `/teams/{id}` | Atualiza equipe |

#### Temporadas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/seasons` | Lista temporadas |
| POST | `/seasons` | Cria temporada |
| GET | `/seasons/{id}` | Obtém temporada |
| PATCH | `/seasons/{id}` | Atualiza temporada |

#### Inscrições de Atletas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/registrations` | Lista inscrições |
| POST | `/teams/{team_id}/registrations/{athlete_id}` | Inscreve atleta |
| GET | `/teams/{team_id}/registrations/{id}` | Obtém inscrição |
| PATCH | `/teams/{team_id}/registrations/{id}` | Atualiza inscrição |

#### Treinos (Training Sessions)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/trainings` | Lista treinos |
| POST | `/teams/{team_id}/trainings` | Cria treino |
| GET | `/teams/{team_id}/trainings/{id}` | Obtém treino |
| PATCH | `/teams/{team_id}/trainings/{id}` | Atualiza treino |
| DELETE | `/teams/{team_id}/trainings/{id}` | Soft delete |
| POST | `/teams/{team_id}/trainings/{id}/restore` | Restaura treino |

#### Presença em Treinos

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/trainings/{training_id}/attendance` | Lista presenças |
| POST | `/teams/{team_id}/trainings/{training_id}/attendance` | Registra presença |
| PATCH | `/teams/{team_id}/trainings/{training_id}/attendance/{id}` | Atualiza presença |
| DELETE | `/teams/{team_id}/trainings/{training_id}/attendance/{id}` | Remove presença |

#### Partidas (Matches)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/matches` | Lista partidas |
| POST | `/teams/{team_id}/matches` | Cria partida |
| GET | `/teams/{team_id}/matches/{id}` | Obtém partida |
| PATCH | `/teams/{team_id}/matches/{id}` | Atualiza partida |
| DELETE | `/teams/{team_id}/matches/{id}` | Soft delete |
| POST | `/teams/{team_id}/matches/{id}/restore` | Restaura partida |

#### Eventos de Partida

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/matches/{match_id}/events` | Lista eventos |
| POST | `/teams/{team_id}/matches/{match_id}/events` | Cria evento |
| PATCH | `/teams/{team_id}/matches/{match_id}/events/{id}` | Atualiza evento |
| DELETE | `/teams/{team_id}/matches/{match_id}/events/{id}` | Remove evento |

#### Roster (Escalação)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/matches/{match_id}/roster` | Lista roster |
| POST | `/teams/{team_id}/matches/{match_id}/roster` | Adiciona atleta |
| PATCH | `/teams/{team_id}/matches/{match_id}/roster/{id}` | Atualiza entrada |
| DELETE | `/teams/{team_id}/matches/{match_id}/roster/{athlete_id}` | Remove atleta |

#### Equipes na Partida

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/matches/{match_id}/teams` | Lista equipes |
| POST | `/teams/{team_id}/matches/{match_id}/teams` | Adiciona equipe |
| PATCH | `/teams/{team_id}/matches/{match_id}/teams/{side}` | Atualiza (home/away) |

#### Presença em Partidas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/teams/{team_id}/matches/{match_id}/attendance` | Lista presenças |
| POST | `/teams/{team_id}/matches/{match_id}/attendance` | Registra presença |
| PATCH | `/teams/{team_id}/matches/{match_id}/attendance/{id}` | Atualiza presença |
| DELETE | `/teams/{team_id}/matches/{match_id}/attendance/{id}` | Remove presença |
| GET | `/teams/{team_id}/athletes/{athlete_id}/match-load` | Carga do atleta |

---

## 4. Módulos Implementados

### 4.1 Training Sessions (Treinos)

**Status:** ✅ CRUD Completo

**Funcionalidades:**
- Criação de treinos com tipo de sessão (técnico, tático, físico, etc.)
- Filtros por temporada, data inicial/final
- Paginação e soft delete
- Vinculação automática com organização via equipe

**Validações:**
- Escopo de equipe obrigatório
- Membership ativo para criar/editar
- Datas futuras permitidas

### 4.2 Match Roster (Escalação)

**Status:** ✅ CRUD Completo

**Funcionalidades:**
- Adicionar atletas à escalação
- Definir número da camisa e posição
- Marcar goleiros e disponibilidade

**Validações:**
- Atleta deve ter inscrição ativa na equipe
- Limite de 16 atletas por partida (RD18)
- Verificação de duplicatas

### 4.3 Match Attendance (Presença em Jogos)

**Status:** ✅ CRUD Completo

**Funcionalidades:**
- Registro de minutos jogados
- Marcação de titular vs reserva
- Cálculo de carga por partida

**Validações:**
- Atleta deve estar no roster
- Minutos máximo: 80 (60 + prorrogação)
- `played=false` não permite minutos > 0

### 4.4 Relatórios Consolidados

**Status:** ✅ Implementado

**Endpoints:**

| Endpoint | Descrição |
|----------|-----------|
| `GET /reports/attendance` | Taxa de assiduidade por atleta |
| `GET /reports/minutes` | Minutos jogados/treinados |
| `GET /reports/load` | Carga acumulada (RPE × minutos) |

### 4.5 Sistema de Alertas

**Status:** ✅ Implementado

**Endpoints:**

| Endpoint | Descrição |
|----------|-----------|
| `GET /alerts/load` | Alertas de excesso/déficit de carga (ACWR) |
| `GET /alerts/injury-return` | Atletas lesionadas ou retornando |

---

## 5. Sistema de Cache

### 5.1 Configuração

| Parâmetro | Valor |
|-----------|-------|
| **Backend** | `cachetools.TTLCache` |
| **TTL** | 120 segundos |
| **Max Entries** | 512 |
| **Escopo** | In-memory (por instância) |

### 5.2 Endpoints com Cache

| Endpoint | Prefixo de Cache |
|----------|------------------|
| `GET /reports/attendance` | `report_attendance` |
| `GET /reports/minutes` | `report_minutes` |
| `GET /reports/load` | `report_load` |
| `GET /alerts/load` | `alerts_load` |
| `GET /alerts/injury-return` | `alerts_injury` |

### 5.3 Invalidação Automática

O cache é invalidado automaticamente após operações de escrita em:

| Router | Endpoints |
|--------|-----------|
| `attendance_scoped` | POST, PATCH, DELETE |
| `match_attendance` | POST, PATCH, DELETE |
| `training_sessions` | POST, PATCH, DELETE, RESTORE |

### 5.4 Logs de Cache

Logger dedicado: `hb.cache`

```
DEBUG hb.cache CACHE MISS | key=report:attendance:{...}
DEBUG hb.cache CACHE SET  | key=report:attendance:{...}
DEBUG hb.cache CACHE HIT  | key=report:attendance:{...}
DEBUG hb.cache CACHE INVALIDATED | entries_cleared=5
```

**Controle de nível:**
- **Dev:** `logging.getLogger("hb.cache").setLevel(logging.DEBUG)`
- **Prod:** `logging.getLogger("hb.cache").setLevel(logging.INFO)`

---

## 6. Performance e Índices

### 6.1 Índices Criados (9 total)

| Tabela | Índice | Propósito |
|--------|--------|-----------|
| `athletes` | `ix_athletes_medical_flags` | Alertas de lesão |
| `attendance` | `ix_attendance_athlete_session_active` | Assiduidade por atleta |
| `match_attendance` | `ix_match_attendance_athlete_match_active` | Minutos jogados |
| `matches` | `ix_matches_season_date_active` | Jogos por temporada |
| `medical_cases` | `ix_medical_cases_athlete_status_active` | Retorno de lesão |
| `team_registrations` | `ix_team_registrations_team_athlete_active` | Vínculos ativos |
| `training_sessions` | `ix_training_sessions_team_date_active` | Treinos por equipe/data |
| `training_sessions` | `ix_training_sessions_team_season_date` | Treinos por temporada |
| `wellness_post` | `ix_wellness_post_athlete_session_active` | Carga (RPE) |

### 6.2 Características dos Índices

- **Tipo:** Índices parciais (`WHERE deleted_at IS NULL`)
- **Benefício:** Redução de storage e manutenção
- **Ativação:** PostgreSQL usa Index Scan automaticamente com >1000 rows

### 6.3 Paginação

**Parâmetros disponíveis:**

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `page` | int | 1 | Página (1-indexed) |
| `page_size` | int | 25 | Itens por página (máx 100) |
| `order_by` | string | - | Campo de ordenação (whitelist) |
| `order_dir` | string | desc | Direção (asc/desc) |

**Exemplo de resposta:**

```json
{
  "team_id": "...",
  "athletes": [...],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 143,
    "total_pages": 6
  }
}
```

### 6.4 Whitelists de Ordenação

| Endpoint | Campos Permitidos |
|----------|-------------------|
| `/reports/attendance` | `athlete_name`, `training_attendance_rate`, `match_participation_rate`, `combined_attendance_rate` |
| `/reports/minutes` | `athlete_name`, `total_minutes_played`, `total_training_minutes`, `total_activity_minutes` |
| `/reports/load` | `athlete_name`, `training_load_total`, `match_load_total`, `total_load`, `avg_daily_load` |

### 6.5 Métricas de Performance

Resultados do EXPLAIN ANALYZE (dataset pequeno):

| Query | Planning | Execution |
|-------|----------|-----------|
| Athletes + TeamReg | 0.15 ms | 0.04 ms |
| Training Sessions | 0.10 ms | 0.03 ms |
| Attendance/atleta | 0.30 ms | 0.90 ms |
| Match Attendance | 6.07 ms | 0.86 ms |
| Wellness/Load | 0.30 ms | 0.05 ms |

---

## 7. Relatórios e Alertas

### 7.1 Relatório de Assiduidade

```
GET /api/v1/reports/attendance?team_id={uuid}&days=30
```

**Retorna por atleta:**
- Taxa de presença em treinos
- Taxa de participação em jogos
- Taxa combinada de assiduidade

### 7.2 Relatório de Minutos

```
GET /api/v1/reports/minutes?team_id={uuid}&days=30
```

**Retorna por atleta:**
- Total de minutos jogados
- Total de minutos de treino
- Total de atividade

### 7.3 Relatório de Carga

```
GET /api/v1/reports/load?team_id={uuid}&days=30
```

**Retorna por atleta:**
- Carga de treino (RPE × minutos)
- Carga de jogos
- Carga total
- Média diária de carga

### 7.4 Alertas de Carga

```
GET /api/v1/alerts/load?team_id={uuid}
```

**Alertas baseados em:**
- **ACWR (Acute:Chronic Workload Ratio):** Razão entre carga aguda (7 dias) e crônica (28 dias)
- **Limites:** ACWR < 0.8 (déficit) ou ACWR > 1.5 (excesso)
- **Carga semanal absoluta:** Alertas para valores extremos

### 7.5 Alertas de Lesão

```
GET /api/v1/alerts/injury-return?team_id={uuid}
```

**Tipos de alerta:**
- Atletas com lesão ativa
- Atletas em recuperação
- Atletas retornando de lesão (últimos 14 dias)

---

## 8. Guia de Testes

### 8.1 Smoke Tests Disponíveis

| Arquivo | Cobertura |
|---------|-----------|
| `tests/smoke_reports_alerts.py` | Relatórios e alertas (6 testes) |
| `tests/smoke_match_attendance.py` | Presença em jogos (11 testes) |
| `tests/smoke_match_roster_teams.py` | Roster e equipes (9 testes) |
| `tests/test_training_crud_e2e.py` | CRUD de treinos (5 testes) |

### 8.2 Executando Testes

```bash
# Smoke test individual
cd "Hb Track - Backend"
python tests/smoke_reports_alerts.py

# Todos os smoke tests
python -m pytest tests/smoke_*.py -v

# Teste E2E de treinos
python -m pytest tests/test_training_crud_e2e.py -v
```

### 8.3 Validação de Cache

```python
# Forçar logs DEBUG do cache
import logging
logging.getLogger("hb.cache").setLevel(logging.DEBUG)

# Primeira request = MISS
# Segunda request (mesmos params) = HIT
```

---

## 9. Roadmap e Próximos Passos

### 9.1 Status Atual

| Item | Status |
|------|--------|
| Arquitetura de autorização | ✅ Completo |
| Rotas canônicas | ✅ Completo |
| CRUD Training Sessions | ✅ Completo |
| CRUD Match Roster | ✅ Completo |
| CRUD Match Attendance | ✅ Completo |
| Relatórios consolidados | ✅ Completo |
| Alertas automáticos | ✅ Completo |
| Cache com TTL | ✅ Completo |
| Índices de performance | ✅ Completo |
| Paginação e ordenação | ✅ Completo |

### 9.2 Próximos Passos - Curto Prazo

| Prioridade | Item | Descrição |
|------------|------|-----------|
| 🔴 Alta | **Seed de Volume** | Criar script para popular 50k-100k registros para teste de carga |
| 🔴 Alta | **Wellness Post CRUD** | Implementar endpoints de bem-estar pós-treino (atualmente 501) |
| 🟡 Média | **LIMIT por Período** | Aumentar default de 30 para 90 dias nos relatórios |
| 🟡 Média | **Testes de Carga** | Executar load testing com k6 ou Locust |

### 9.3 Próximos Passos - Médio Prazo

| Prioridade | Item | Descrição |
|------------|------|-----------|
| 🟡 Média | **Cursor Pagination** | Substituir OFFSET por `WHERE id > :last_id` para listas > 10k |
| 🟡 Média | **Rate Limiting** | Implementar throttling por usuário/IP |
| 🟡 Média | **Audit Log** | Registrar todas as operações de escrita |
| 🟡 Média | **Export CSV/PDF** | Exportação de relatórios |

### 9.4 Próximos Passos - Longo Prazo (Escalabilidade)

| Prioridade | Item | Descrição |
|------------|------|-----------|
| 🟢 Baixa | **Read Replica** | Separar leituras de escritas com réplica PostgreSQL |
| 🟢 Baixa | **Redis Cache** | Migrar de cachetools para Redis (distribuído) |
| 🟢 Baixa | **Background Jobs** | Celery/RQ para relatórios pesados |
| 🟢 Baixa | **WebSockets** | Atualizações em tempo real para jogos ao vivo |
| 🟢 Baixa | **CDN para Assets** | Mover fotos de atletas para S3/CloudFront |
| 🟢 Baixa | **Multi-tenancy Avançado** | Schema isolation por organização |

### 9.5 Melhorias de Segurança

| Item | Descrição |
|------|-----------|
| **API Keys** | Autenticação alternativa para integrações |
| **2FA** | Autenticação de dois fatores para dirigentes |
| **IP Whitelist** | Restrição por IP para organizações sensíveis |
| **Encryption at Rest** | Criptografia de dados sensíveis (médicos) |
| **GDPR Compliance** | Exportação e exclusão de dados pessoais |

### 9.6 Observabilidade

| Item | Descrição |
|------|-----------|
| **APM** | Integração com Datadog/New Relic |
| **Structured Logging** | Migrar para JSON logging (Loguru) |
| **Metrics** | Prometheus + Grafana para métricas |
| **Tracing** | OpenTelemetry para distributed tracing |
| **Health Checks** | Endpoints `/health` e `/ready` |

### 9.7 Script de Seed para Teste de Volume

```sql
-- Sugestão de volume para teste de performance
-- attendance: 50,000 rows
-- training_sessions: 5,000 rows
-- match_attendance: 20,000 rows
-- wellness_post: 30,000 rows
-- matches: 1,000 rows

-- Com esse volume, PostgreSQL usará Index Scan
-- automaticamente nos índices criados
```

---

## Anexo A: Correções Técnicas Aplicadas

### A.1 Compatibilidade bcrypt

Adicionado shim de compatibilidade em `security.py` para o passlib reconhecer bcrypt 4.3+:

```python
# Define bcrypt.__about__.__version__ quando ausente
```

### A.2 Season.organization_id

Corrigido para usar `column_property` com `correlate_except(Team)` para evitar autocorrelação em joins.

### A.3 Modelo Match

Alinhado com schema real:
- `our_team_id`, `home_team_id`, `away_team_id`
- Status: `scheduled`, `in_progress`, `finished`, `cancelled`
- `organization_id` derivado via JOIN com Team

### A.4 Modelo TrainingSession

Mapeado para colunas reais:
- `created_by_user_id` (não `created_by_membership_id`)
- `session_type` NOT NULL
- Colunas booleanas de fases de foco

---

## Anexo B: Estrutura de Arquivos

```
Hb Track - Backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── deps/
│   │       │   └── pagination.py      # Paginação e ordenação
│   │       └── routers/
│   │           ├── alerts.py          # Alertas
│   │           ├── attendance_scoped.py
│   │           ├── match_attendance.py
│   │           ├── match_events.py
│   │           ├── match_roster.py
│   │           ├── match_teams.py
│   │           ├── matches.py
│   │           ├── reports.py         # Relatórios
│   │           ├── training_sessions.py
│   │           └── ...
│   ├── core/
│   │   ├── auth.py                    # Autenticação
│   │   ├── cache.py                   # Sistema de cache
│   │   ├── permissions.py             # Helpers de autorização
│   │   └── ...
│   ├── models/
│   │   ├── match_attendance.py
│   │   ├── medical_case.py
│   │   ├── wellness_post.py
│   │   └── ...
│   ├── schemas/
│   │   ├── alerts.py
│   │   └── reports/
│   │       └── consolidated.py
│   └── services/
│       ├── alerts/
│       │   └── alert_service.py
│       └── reports/
│           └── consolidated_service.py
├── db/
│   └── alembic/
│       └── versions/
│           └── 2026_01_01_add_reports_alerts_indexes.py
└── tests/
    ├── smoke_match_attendance.py
    ├── smoke_match_roster_teams.py
    ├── smoke_reports_alerts.py
    └── test_training_crud_e2e.py
```

---

> **Documento gerado em:** Janeiro 2026  
> **Próxima revisão sugerida:** Após implementação do Wellness Post CRUD
