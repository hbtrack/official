# SYSTEM_DESIGN — Arquitetura e Padroes do HB Track Backend

> Referencia arquitetural unificada. Para fontes de verdade e workflow, ver [CANON.md](CANON.md), [ROUTER.md](ROUTER.md) e [CHECKS.md](CHECKS.md).

---

## 1. Visao Geral da Arquitetura

### 1.1 Stack

| Camada | Tecnologia | Versao |
|--------|-----------|--------|
| Framework | FastAPI | 0.100+ |
| ORM | SQLAlchemy 2.0 (Mapped) | 2.0+ |
| DB | PostgreSQL 17 (Neon cloud) | 17 |
| Migrations | Alembic | 1.12+ |
| Auth | JWT (python-jose) + bcrypt (passlib) | HS256 |
| Async Tasks | Celery + Redis | 5.3+ |
| Schemas | Pydantic v2 | 2.0+ |
| Integracoes | Gemini API, Cloudinary, Resend | - |
| Testes | pytest | 8.0+ |
| **Frontend** | Next.js + TypeScript + Tailwind CSS | 14+ / 5.0+ / 3.4+ |
| State Mgmt | React Query + React Hook Form | 5.0+ / 7.0+ |
| Hosting | Render (backend) + Vercel (frontend) + Neon (DB) | - |

### 1.2 Estrutura de Diretorios

```
app/
  main.py                         # FastAPI app + middleware + exception handlers
  api/v1/
    api.py                        # Agregacao de routers
    deps/auth.py                  # permission_dep()
    deps/pagination.py            # Paginacao padrao
    routers/                      # ~60 routers (1 por recurso)
  models/
    base.py                       # DeclarativeBase
    *.py                          # 1 model por tabela
  schemas/
    error.py                      # ErrorResponse, ErrorCode, ErrorDetail
    *.py                          # {Entity}Create, {Entity}Update, {Entity}Response
  services/
    *.py                          # 1 service por dominio
    alerts/                       # Subsistema de alertas
    reports/                      # Subsistema de relatorios
  core/
    config.py                     # Settings (BaseSettings)
    context.py                    # ExecutionContext + get_current_context
    deps.py                       # permission_dep (fabrica de dependencias)
    permissions_map.py            # Mapa canonico role -> permissoes
    permissions.py                # require_roles, require_membership, require_org_scope
    security.py                   # create_access_token, decode_access_token, hash_password
    exceptions.py                 # NotFoundError, BusinessError, ForbiddenError, etc.
    db.py                         # Engine sync/async, session factories, warmup
    celery_app.py                 # Celery config + beat schedule
    celery_tasks.py               # Tasks assincrona
    middleware.py                 # RequestIDMiddleware, SecurityHeadersMiddleware
    rate_limit.py                 # slowapi limiter
```

### 1.3 Pipeline de Middleware

```
Request → CORS → SecurityHeaders → RequestID → RateLimit → Auth (Depends) → Router → Service → DB
                                                                                                ↓
Response ← Exception Handler (se erro) ← JSON Response ←────────────────────────────────────────┘
```

Ordem no `main.py` (LIFO — ultimo adicionado executa primeiro):
1. `CORSMiddleware` (mais externo)
2. `SecurityHeadersMiddleware` (X-Content-Type-Options, X-Frame-Options, CSP, HSTS)
3. `RequestIDMiddleware` (gera/propaga `X-Request-ID`)
4. Rate limiting via `slowapi`

> Fonte: `app/main.py:46-84`

### 1.4 Modelo de Dominio (Relacoes Principais)

```
Organizations (tenant root)
  ├── OrgMemberships (staff: person + role)
  ├── Teams
  │   ├── TeamMemberships (coach/coordenador)
  │   ├── TeamRegistrations (atletas)
  │   ├── Seasons
  │   └── TrainingSessions
  │       ├── Attendance
  │       ├── WellnessPre / WellnessPost
  │       └── SessionExercises
  ├── TrainingCycles → TrainingMicrocycles
  ├── TrainingAnalyticsCache
  └── TrainingAlerts / TrainingSuggestions

Persons (identidade master)
  ├── Users (acesso ao sistema, 1:1)
  ├── Athletes (perfil esportivo, 1:1)
  ├── PersonAddresses / PersonContacts / PersonDocuments / PersonMedia

Competitions (cross-org)
  ├── CompetitionPhases → CompetitionMatches
  └── CompetitionStandings

Matches (analytics)
  ├── MatchEvents (lance a lance)
  ├── MatchRoster (sumula)
  └── MatchPossessions
```

### 1.5 Ambientes

| Ambiente | `ENV` | DB | Observacoes |
|----------|-------|-----|-------------|
| Local | `local` | Docker Compose / Neon dev | CORS permissivo |
| Test | `test` | DB isolado | pytest |
| Staging | `staging` | Neon staging | CORS restrito |
| Production | `production` | Neon prod | HSTS, CSP, CORS restrito |

### 1.6 Hierarquia de Roles (Perfis de Usuario)

| Role | Persona | Escopo de Acesso | Exemplo de uso |
|------|---------|-----------------|----------------|
| `superadmin` | Administrador tecnico da plataforma | Total — bypassa todas as validacoes (R3) | Criar organizacoes, gerenciar usuarios, acessar qualquer tenant |
| `dirigente` | Presidente/gestor do clube | Gestao completa da organizacao: memberships, equipes, financeiro | Criar equipes, vincular staff, ver relatorios globais |
| `coordenador` | Coordenador tecnico/esportivo | Equipes sob sua responsabilidade: treinos, atletas, jogos | Planejar temporada, analisar metricas de performance |
| `treinador` | Treinador/preparador fisico | Equipes vinculadas: treinos, presenca, wellness, exercicios | Criar sessoes de treino, registrar presenca, revisar wellness |
| `membro` | Staff administrativo/auxiliar | Somente leitura (R42: requer vinculo ativo) | Visualizar dados basicos sem permissao de escrita |
| `atleta` | Jogador vinculado a equipe | Dados proprios + wellness autopreenchimento | Preencher wellness pre/pos, ver historico pessoal |

**Regras criticas de acesso**:
- R3: Superadmin bypassa TODAS as verificacoes de vinculo, organizacao e permissao
- R42: Roles exceto superadmin DEVEM ter `org_membership` ativo para acessar o sistema
- R25: Cada endpoint define os roles permitidos via `require_role()` ou `permission_dep()`

> Fonte: `app/core/permissions_map.py`, `app/core/context.py:get_current_context()`

---

## 2. Regras Gerais

### 2.1 Nomenclatura Padronizada

| Elemento | Convencao | Exemplo |
|----------|-----------|---------|
| Tabela | `snake_case` plural | `team_registrations` |
| Model (classe) | `PascalCase` | `TeamRegistration` |
| Service | `{Entity}Service` ou `{Entity}ServiceV{X}_{Y}` | `TrainingSessionService`, `AthleteServiceV1_2` |
| Schema | `{Entity}{Proposito}` | `TrainingSessionCreate`, `TrainingSessionResponse` |
| Rota (URL) | kebab-case | `/training-sessions`, `/wellness-pre` |
| Constraint CHECK | `ck_{tabela}_{descricao}` | `ck_athletes_state` |
| Constraint FK | `fk_{tabela}_{coluna}` | `fk_athletes_person_id` |
| Constraint UNIQUE | `uq_{tabela}_{coluna}` | `uq_users_email` |
| Constraint EXCLUDE | `ex_{tabela}_{descricao}` | `ex_team_registrations_no_overlap` |
| Trigger | `trg_{tabela}_{acao}` | `trg_set_updated_at` |
| Funcao trigger | `fn_{descricao}()` | `fn_derive_phase_focus()` |
| Enum (DB) | valores `snake_case` | `ativa`, `dispensada`, `arquivada` |
| Arquivo router | `{entidade}.py` | `training_sessions.py` |
| Arquivo model | `{entidade}.py` | `training_session.py` |

### 2.2 HTTP Status Codes

| Codigo | Uso | Quando |
|--------|-----|--------|
| `200` | Sucesso | GET, PATCH, DELETE (soft) |
| `201` | Criado | POST que cria recurso |
| `400` | Bad Request | Parametro ausente/invalido no path/query |
| `401` | Unauthorized | Token ausente, expirado ou invalido |
| `403` | Forbidden | Papel nao autorizado (R25), sem vinculo ativo (R42) |
| `404` | Not Found | Recurso inexistente ou soft-deleted |
| `409` | Conflict | Violacao de unicidade, sobreposicao de periodo (RDB9/RDB10), edicao de jogo finalizado (RDB13) |
| `422` | Validation | Payload invalido (Pydantic), CHECK constraint, FK invalida |
| `500` | Internal Error | Erro nao tratado (detalhes ocultos em prod) |
| `503` | Service Unavailable | DB indisponivel (cold start Neon) |

### 2.3 Campos de Auditoria Obrigatorios

Toda tabela de dominio DEVE ter:

```python
# Timestamps (auto-gerenciados)
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    server_default=text("now()"),
    nullable=False,
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    server_default=text("now()"),
    nullable=False,
)
```

O trigger `trg_set_updated_at()` no PostgreSQL atualiza `updated_at` automaticamente em todo UPDATE.

Campos de rastreamento (quando aplicavel):
- `created_by_user_id` (UUID, FK → users) — quem criou
- `created_by_membership_id` (UUID, FK → org_memberships) — vinculo organizacional

> Fonte: `app/models/training_session.py:172-192`, `schema.sql` (trigger `trg_set_updated_at`)

### 2.4 Tratamento de Erros

**Hierarquia de excecoes** (`app/core/exceptions.py`):

| Excecao | HTTP | Quando usar |
|---------|------|-------------|
| `NotFoundError(message)` | 404 | Recurso nao encontrado |
| `ForbiddenError(message)` | 403 | Acesso negado (alias: `PermissionDeniedError`) |
| `ValidationError(message, field)` | 422 | Validacao de negocio no service |
| `ConflictError(message)` | 409 | Conflito de dados/estado |
| `BusinessError(error_key, message)` | 409/422 | Regra de negocio com mapeamento especifico |

**Mapeamento PostgreSQL → HTTP** (`POSTGRES_ERROR_MAP`):

| SQLSTATE | HTTP | Codigo | Regra |
|----------|------|--------|-------|
| `23P01` | 409 | `conflict_period_overlap` | RDB10 |
| `23505` | 409 | `conflict_unique_violation` | - |
| `23514` | 422 | `validation_check_constraint` | - |
| `23503` | 422 | `validation_foreign_key` | - |
| `23502` | 422 | `validation_required_field` | - |

**Mapeamento por constraint name** (prioridade sobre SQLSTATE):

| Constraint | HTTP | Regra |
|-----------|------|-------|
| `ex_team_registrations_no_overlap` | 409 | RDB10 |
| `ck_team_registrations_date_range_valid` | 422 | RDB10 |
| `trg_games_block_update_finalized` | 409 | RDB13 |

**Formato padrao de resposta de erro** (`app/schemas/error.py`):

```json
{
  "error_code": "MEMBERSHIP_OVERLAP",
  "message": "Vinculo sobrepoe periodo existente",
  "details": {
    "field": "start_date",
    "constraint": "RDB9",
    "existing_id": "uuid-aqui",
    "metadata": {}
  },
  "timestamp": "2026-01-15T10:30:00Z",
  "request_id": "550e8400-e29b-..."
}
```

**ErrorCode enum** — codigos disponiveis (`app/schemas/error.py:10-48`):
- DB: `MEMBERSHIP_OVERLAP`, `TEAM_REG_OVERLAP`, `SEASON_OVERLAP`, `SOFT_DELETE_REASON_REQUIRED`
- Negocio: `SUPERADMIN_IMMUTABLE`, `NO_ACTIVE_MEMBERSHIP`, `ATHLETE_DISPENSE_NO_UNDO`, `DUPLICATE_PERSON`, `DUPLICATE_USER`
- Dominio: `AGE_BELOW_CATEGORY`, `MATCH_ALREADY_FINALIZED`, `CORRECTION_NOTE_REQUIRED`
- Generico: `RESOURCE_NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`, `VALIDATION_ERROR`, `INTERNAL_SERVER_ERROR`

### 2.5 Soft Delete Obrigatorio

Toda tabela de dominio DEVE ter:

```python
# Soft delete (RDB4)
deleted_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
)
deleted_reason: Mapped[Optional[str]] = mapped_column(
    Text, nullable=True
)
```

**Constraint obrigatoria** — ambos NULL ou ambos preenchidos:
```sql
CONSTRAINT ck_{tabela}_deleted_reason CHECK (
    (deleted_at IS NULL AND deleted_reason IS NULL) OR
    (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
)
```

**Regras**:
- NUNCA fazer DELETE fisico — o trigger `trg_block_physical_delete()` impede
- Queries DEVEM filtrar `WHERE deleted_at IS NULL` (exceto quando explicitamente incluindo deletados)
- Para "excluir": `UPDATE SET deleted_at = now(), deleted_reason = 'motivo'`

### 2.6 Isolamento Multi-Tenant

- Tabelas de dominio possuem `organization_id` (UUID, FK → organizations)
- O `ExecutionContext` carrega `organization_id` resolvido do JWT
- Queries DEVEM filtrar: `Model.organization_id == ctx.organization_id`
- Superadmin (R3) pode operar em qualquer organizacao via header `X-Organization-ID`
- Regra R34: V1 suporta clube unico; estrutura pronta para multi-tenant

### 2.7 SLAs de Performance

Metas definidas no PRD (Secao 10.1) que o backend DEVE cumprir:

| Metrica | Target | Metodo |
|---------|--------|--------|
| Tempo de resposta API (P95) | < 200ms | Prometheus / New Relic |
| Carregamento de dashboard (P90) | < 3s | Inclui queries de analytics |
| Registro de presenca | < 100ms | Timing interno |
| Consultas complexas (relatorios) | < 2s | `EXPLAIN ANALYZE` PostgreSQL |
| Uptime | > 99.5% | Monitoramento Render (~3.6h downtime/mes) |
| Usuarios simultaneos | 500 (V1), 5000 (V2) | Load tests K6/Locust |

**Janela de manutencao**: Domingos 02:00-06:00 BRT.

> Fonte: `PRD_HB_TRACK.md` Secao 10.1-10.3

---

## 3. Camada de Dados

### 3.1 Padrao de Model

```python
# Fonte: app/models/training_session.py (exemplo representativo)

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    # PK — UUID gerado pelo PostgreSQL
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Tenant scope
    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )

    # Campos de dominio...

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(...)
    updated_at: Mapped[datetime] = mapped_column(...)
    created_by_user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(...)
    deleted_reason: Mapped[Optional[str]] = mapped_column(...)
```

Base class: `app/models/base.py` — `DeclarativeBase` puro (sem mixins).

### 3.2 Triggers PostgreSQL

| Trigger/Funcao | Tabela alvo | Evento | Logica |
|----------------|-------------|--------|--------|
| `trg_set_updated_at()` | Todas as tabelas de dominio | BEFORE UPDATE | `updated_at = NOW()` |
| `trg_set_athlete_age_at_registration()` | `athletes` | BEFORE INSERT/UPDATE | Calcula `age = EXTRACT(YEAR FROM AGE(registered_at, birth_date))` |
| `fn_derive_phase_focus()` | `training_sessions` | BEFORE INSERT/UPDATE | Deriva `phase_focus_*` booleans de percentuais (threshold >= 5%) |
| `fn_calculate_internal_load()` | `wellness_post` | BEFORE INSERT/UPDATE | `internal_load = minutes_effective * session_rpe` |
| `fn_update_wellness_response_timestamp()` | `wellness_reminders` | AFTER INSERT (wellness) | Atualiza `responded_at` quando atleta responde |
| `fn_invalidate_analytics_cache()` | `training_analytics_cache` | AFTER INS/UPD/DEL (training_sessions) | Marca `cache_dirty = TRUE` |
| `fn_audit_session_status()` | `audit_logs` | AFTER UPDATE (training_sessions) | Loga mudancas de status |
| `trg_block_finished_match_update()` | `matches` | BEFORE UPDATE | Bloqueia UPDATE em jogos finalizados (exceto reopen) |
| `trg_block_physical_delete()` | Tabelas com soft delete | BEFORE DELETE | Impede DELETE fisico |
| `trg_insert_default_session_templates()` | `session_templates` | AFTER INSERT (organizations) | Insere 4 templates default |

> Fonte: `schema.sql` (funcoes e triggers)

### 3.3 Constraints

**Padroes de constraint no sistema:**

- **CHECK (enum)**: Valida valores permitidos
  ```sql
  CONSTRAINT ck_athletes_state CHECK (state IN ('ativa','dispensada','arquivada'))
  ```

- **CHECK (range)**: Valida limites numericos
  ```sql
  CONSTRAINT ck_training_sessions_group_climate CHECK (group_climate BETWEEN 1 AND 5)
  CONSTRAINT ck_athletes_shirt_number CHECK (shirt_number BETWEEN 1 AND 99)
  ```

- **CHECK (soma de percentuais)**: Focus tatico <= 120%
  ```sql
  CHECK (COALESCE(focus_attack_positional_pct,0) + ... <= 120)
  ```

- **EXCLUDE (overlap)**: Impede sobreposicao de periodos
  ```sql
  CONSTRAINT ex_team_registrations_no_overlap EXCLUDE USING gist (...)
  ```

- **FK (ondelete)**: `RESTRICT` por padrao; `SET NULL` quando referencia e opcional

### 3.4 Conexao Neon

Configuracao otimizada para Neon Free Tier (`app/core/db.py`):

| Parametro | Valor | Razao |
|-----------|-------|-------|
| `pool_size` | 5 | Limite Neon free |
| `max_overflow` | 5 | Buffer |
| `pool_timeout` | 45s | Cold start Neon |
| `pool_recycle` | 1800s (30min) | Evitar conexoes mortas |
| `pool_pre_ping` | True (sync) | Detectar conexao morta |

**Warmup**: Na startup, `warmup_database()` executa query de aquecimento para evitar cold start no primeiro request.

**Retry**: Exponential backoff (0.5s, 1s, 2s) para conexoes transientes.

> Fonte: `app/core/db.py:1-80`

### 3.5 Migrations

Workflow Alembic — ver [CHECKS.md](CHECKS.md) secao 2.

Apos alterar models/migrations, regenerar artefatos canonicos:
```bash
python scripts/generate_docs.py --schema    # schema.sql
python scripts/generate_docs.py --alembic   # alembic_state.txt
```

### 3.6 Padroes de Relacionamento

**1:1 (Person → User)**:
```python
# Fonte: app/models/person.py:80-85
user: Mapped[Optional["User"]] = relationship(
    "User",
    back_populates="person",
    uselist=False,       # Garante retorno unico (nao lista)
    lazy="selectin",     # Carrega automaticamente
)
```

**1:N com cascade (Person → PersonContacts)**:
```python
# Fonte: app/models/person.py:88-93
contacts: Mapped[List["PersonContact"]] = relationship(
    "PersonContact",
    back_populates="person",
    cascade="all, delete-orphan",   # Propaga operacoes ao filho
    lazy="selectin"
)
```

**Estrategias de carregamento (lazy)**:

| Estrategia | Quando usar | Exemplo |
|-----------|-------------|---------|
| `selectin` | Padrao — relacoes sempre necessarias | Person → contacts, addresses |
| `noload` | Relacoes pesadas carregadas sob demanda | Evitar N+1 em listas grandes |
| `joined` | Raro — quando JOIN unico e suficiente | 1:1 em queries simples |

**FK — `ondelete` padrao**:
- `RESTRICT` (padrao) — impede exclusao do pai se filho existe
- `CASCADE` — apenas para tabelas "filhas" normalizadas (ex: `person_contacts`, `person_addresses`)
- `SET NULL` — quando referencia e opcional (ex: `season_id` em training_sessions)

### 3.7 Padroes de Index

**Simples (FK + campos de busca)**:
```python
# Fonte: app/models/training_session.py:55-83
organization_id: Mapped[UUID] = mapped_column(..., index=True)
team_id: Mapped[Optional[UUID]] = mapped_column(..., index=True)
session_at: Mapped[datetime] = mapped_column(..., index=True)
```

**Compostos (queries frequentes)**:
```python
# Fonte: app/models/training_session.py:382-389
Index("idx_sessions_team_date", "team_id", "session_at"),
Index("idx_training_sessions_org", "organization_id", "deleted_at"),
Index("ix_training_sessions_team_season_date", "team_id", "season_id", "session_at"),
```

**Parciais (filtro `WHERE` no indice)**:
```python
# Fonte: app/models/attendance.py:77
Index(
    'ix_attendance_athlete_session_active',
    'athlete_id', 'training_session_id',
    postgresql_where=sa.text('(deleted_at IS NULL)')   # So indexa registros ativos
)

# Fonte: app/models/wellness_reminder.py:29
Index(
    'idx_wellness_reminders_pending',
    'training_session_id', 'athlete_id',
    postgresql_where=sa.text('(responded_at IS NULL)')  # So indexa pendentes
)
```

**Regras**:
- Toda FK DEVE ter `index=True` (evitar seq scan em JOINs)
- Criar compostos para queries com filtro combinado (ex: team + date)
- Usar parciais para tabelas com soft delete (`deleted_at IS NULL`) ou status especifico

---

## 4. Camada de Servicos

### 4.1 Padrao de Service

```python
# Fonte: app/services/training_session_service.py

class TrainingSessionService:
    """Service de Sessoes de Treino. Ref: R18, R40, RDB3, RDB14"""

    def __init__(self, db: AsyncSession, context: ExecutionContext):
        self.db = db
        self.context = context

    async def get_all(self, *, team_id=None, page=1, size=20) -> tuple[list, int]:
        query = select(TrainingSession).where(
            TrainingSession.organization_id == self.context.organization_id,
            TrainingSession.deleted_at.is_(None),
        )
        # ... filtros, paginacao
        return items, total

    async def create(self, payload: TrainingSessionCreate) -> TrainingSession:
        # Validacao de negocio AQUI (nao no router)
        # ... criar instancia, db.add(), db.flush()
        return session

    async def update(self, session_id: UUID, payload: TrainingSessionUpdate):
        # R40: Validar janela de edicao
        # ... aplicar changes
        return session
```

**Regras do Service:**
- Constructor recebe `AsyncSession` + `ExecutionContext`
- Sem base class (composicao, nao heranca)
- Toda validacao de negocio fica no service
- Async-first: todos os metodos sao `async def`
- Retorna models (router converte para schema via `model_validate`)

### 4.2 Versionamento

Quando um service muda significativamente, versionar:
- `AthleteServiceV1_2` (nao `AthleteService` sobrescrito)
- Schema correspondente: `athletes_v2.py`
- Router pode coexistir: `athletes.py` + `athletes_v2.py` (se necessario)

### 4.3 Responsabilidades por Camada

| Camada | Responsabilidade | NAO faz |
|--------|-----------------|---------|
| **Router** | Receber request, injetar deps, chamar service, retornar response | Logica de negocio, queries diretas |
| **Service** | Validacao de negocio, orquestracao, queries | Parsing HTTP, serializacao de response |
| **Model** | Definicao de schema DB, relacionamentos | Logica de negocio, validacao de payload |
| **Schema** | Validacao de payload (Pydantic), serializacao | Queries, logica de negocio |

### 4.4 Paginacao

Padrao offset/limit com total count:

```python
# Service retorna (items, total)
items, total = await service.get_all(page=page, size=limit)
pages = (total + limit - 1) // limit if total > 0 else 0

return PaginatedResponse(items=items, total=total, page=page, limit=limit, pages=pages)
```

### 4.5 Padroes de Validacao no Service

O service e o unico local para logica de negocio. Padroes reais do sistema:

**Validacao de pertencimento (org scope)**:
```python
# Fonte: app/services/training_session_service.py:201-210
team = team_result.scalar_one_or_none()
if not team:
    raise NotFoundError(f"Team {data.team_id} not found")
if team.organization_id != self.context.organization_id:
    raise ForbiddenError("Team belongs to another organization")
```

**Validacao de janela temporal (R40)**:
```python
# Fonte: app/services/training_session_service.py:407-460
def _validate_edit_permission(self, session, data):
    now = datetime.now(timezone.utc)
    # Imutabilidade >60 dias
    if session_at < now - timedelta(days=self.IMMUTABILITY_DAYS):
        raise ForbiddenError("Training session is older than 60 days and is read-only.")
    # Treinador: ate 10min antes do inicio
    if session.status == "scheduled" and not is_superior:
        if now > session_at - timedelta(minutes=self.AUTHOR_EDIT_WINDOW_MINUTES):
            raise ForbiddenError("Prazo de edicao do autor expirado.")
```

**Validacao condicional por campo**:
```python
# Fonte: app/services/training_session_service.py:285-321
if outcome == "delayed":
    if not delay_minutes or delay_minutes <= 0:
        raise ValidationError("Informe o atraso em minutos")
elif outcome == "canceled":
    if not cancellation_reason or not cancellation_reason.strip():
        raise ValidationError("Informe o motivo do cancelamento")
```

**Efeitos colaterais nao-bloqueantes** (nao impede a operacao se falhar):
```python
# Fonte: app/services/training_session_service.py:949-1011
async def _check_and_generate_compensation_suggestion(self, session):
    try:
        total_focus = sum([session.focus_attack_positional_pct or 0, ...])
        if total_focus > 100:
            await suggestion_service.generate_compensation_suggestion(session_id=session.id)
    except Exception as e:
        logger.error(f"Error generating compensation suggestion: {e}")
        # NAO bloqueia operacao
```

---

## 5. Camada de API (Routers)

### 5.1 Padrao de Router

```python
# Fonte: app/api/v1/routers/training_sessions.py

router = APIRouter(tags=["training-sessions"])

# 1. Endpoints ESTATICOS primeiro (antes de /{id})
@router.get("/stats", response_model=StatsResponse)
async def get_stats(...): ...

# 2. Lista (GET sem path param)
@router.get("", response_model=PaginatedResponse)
async def list_items(...): ...

# 3. Criar (POST)
@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(...): ...

# 4. Detalhe (GET com path param)
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, ...): ...

# 5. Atualizar (PATCH)
@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: UUID, ...): ...

# 6. Deletar (DELETE — soft)
@router.delete("/{item_id}", response_model=ItemResponse)
async def delete_item(item_id: UUID, ...): ...
```

**REGRA CRITICA**: Endpoints estaticos (ex: `/stats`, `/available-today`) DEVEM vir ANTES de `/{id}` para evitar conflito de rota.

### 5.2 Uso de permission_dep()

```python
# Fonte: app/api/v1/deps/auth.py

# Padrao 1: Apenas validar papel
ctx: ExecutionContext = Depends(require_role(["dirigente", "coordenador", "treinador"]))

# Padrao 2: Validar papel + vinculo organizacional
ctx: ExecutionContext = Depends(permission_dep(
    roles=["coordenador", "treinador"],
    require_org=True,           # Exige membership ativo
))

# Padrao 3: Validar papel + escopo de equipe
ctx: ExecutionContext = Depends(permission_dep(
    roles=["coordenador", "treinador"],
    require_org=True,
    require_team=True,          # Exige team_id no path/query
))

# Padrao 4: Verificar permissao granular no service
context.requires("can_create_training")  # Levanta 403 se nao tiver
```

### 5.3 Response Models

Sempre especificar `response_model` e `responses` para documentacao OpenAPI:

```python
@router.post(
    "",
    response_model=TrainingSession,
    status_code=status.HTTP_201_CREATED,
    summary="Cria sessao de treino",
    responses={
        201: {"description": "Sessao criada com sucesso"},
        401: {"description": "Token invalido", "model": ErrorResponse},
        403: {"description": "Permissao insuficiente", "model": ErrorResponse},
    },
)
```

### 5.4 Registro no api.py

Todo novo router deve ser incluido em `app/api/v1/api.py`:

```python
from app.api.v1.routers import novo_recurso
api_router.include_router(novo_recurso.router, prefix="/novo-recurso")
```

---

## 6. Schemas (Request/Response)

### 6.1 Convencao de Nomes

| Sufixo | Uso | Exemplo |
|--------|-----|---------|
| `Create` | POST body | `TrainingSessionCreate` |
| `Update` | PATCH body | `TrainingSessionUpdate` |
| `Response` | GET response (item unico) | `TrainingSession` ou `TrainingSessionResponse` |
| `PaginatedResponse` | GET response (lista) | `TrainingSessionPaginatedResponse` |
| `StatsResponse` | Agregacao/metricas | `WellnessStatusResponse` |

### 6.2 Validacao Pydantic

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TrainingSessionCreate(BaseModel):
    team_id: UUID
    session_at: datetime
    session_type: str = Field(..., min_length=1, max_length=32)
    duration_planned_minutes: Optional[int] = Field(None, ge=1, le=600)
    group_climate: Optional[int] = Field(None, ge=1, le=5)
    intensity_target: Optional[int] = Field(None, ge=1, le=5)

    model_config = ConfigDict(from_attributes=True)
```

**Update — todos os campos Optional (PATCH parcial)**:
```python
# Fonte: app/schemas/training_sessions.py:241-329
class TrainingSessionUpdate(BaseModel):
    session_at: Optional[datetime] = Field(None, ...)
    session_type: Optional[SessionTypeEnum] = Field(None, ...)
    main_objective: Optional[str] = Field(None, ...)
    # Todos os campos sao Optional — PATCH envia somente os alterados
    # model_validator valida regras cross-field (ex: focus sum <= 120%)

    @model_validator(mode='after')
    def validate_focus_sum(self): ...

    model_config = ConfigDict(json_schema_extra={...})
```

**Response — `from_attributes=True` para converter ORM → JSON**:
```python
# Fonte: app/schemas/training_sessions.py:332-349
class TrainingSession(TrainingSessionBase):
    """Resposta completa de sessao de treino."""
    id: UUID = Field(...)
    status: str = Field(...)
    started_at: Optional[datetime] = Field(None, ...)
    ended_at: Optional[datetime] = Field(None, ...)
    execution_outcome: TrainingExecutionOutcome = Field(...)
    # Herda campos de TrainingSessionBase + adiciona campos de leitura

    model_config = ConfigDict(from_attributes=True)  # ORM → Pydantic
```

**Diferenca-chave entre schemas**:

| Aspecto | Create | Update | Response |
|---------|--------|--------|----------|
| Campos obrigatorios | Sim (sem default) | Nenhum (todos Optional) | Todos presentes |
| `@model_validator` | Validacao cross-field | Mesmo (foco sum) | Nao aplicavel |
| `from_attributes` | Nao necessario | Nao necessario | **Obrigatorio** (ORM → JSON) |
| Campos de sistema | Nao inclui (id, created_at) | Nao inclui | Inclui todos |
| Uso | `POST /endpoint` body | `PATCH /endpoint/{id}` body | Response body |

### 6.3 Schemas de Erro

Definidos em `app/schemas/error.py`:
- `ErrorCode` (Enum) — todos os codigos de erro do sistema
- `ErrorDetail` — detalhes opcionais (field, constraint, existing_id, metadata)
- `ErrorResponse` — schema padrao de resposta de erro

Factory functions disponiveis:
- `error_not_found()`, `error_unauthorized()`, `error_permission_denied()`
- `error_period_overlap()`, `error_season_locked()`, `error_age_category_violation()`

---

## 7. Autenticacao, Autorizacao e RBAC

### 7.1 Fluxo JWT

```
POST /auth/login (email + password)
  → bcrypt verify → create_access_token(payload) → JWT (HS256, 30min)
  → Set-Cookie: hb_access_token (HttpOnly) + response body

Request subsequente
  → Authorization: Bearer <token> OU Cookie hb_access_token
  → get_current_context() decodifica JWT
  → Busca User no DB, valida vinculo ativo (R42)
  → Resolve permissoes do mapa canonico
  → Retorna ExecutionContext
```

> Fonte: `app/core/context.py:112-382`, `app/core/security.py`

### 7.2 ExecutionContext

```python
# Fonte: app/core/context.py:46-106

@dataclass
class ExecutionContext:
    user_id: UUID
    email: str
    role_code: str                           # "superadmin" | "dirigente" | "coordenador" | "treinador" | "atleta" | "membro"
    person_id: Optional[UUID] = None
    is_superadmin: bool = False
    organization_id: Optional[UUID] = None
    membership_id: Optional[UUID] = None
    team_ids: List[UUID] = field(default_factory=list)
    permissions: Dict[str, bool] = field(default_factory=dict)

    def can(self, permission: str) -> bool: ...       # Verifica permissao
    def requires(self, permission: str) -> None: ...   # Levanta 403 se nao tiver
    def has_any(self, permissions: List[str]) -> bool: ...
    def has_all(self, permissions: List[str]) -> bool: ...
```

**Principios**:
- Estado puro (zero logica de negocio)
- Criado UMA VEZ por requisicao
- Permissoes ja resolvidas do mapa canonico

### 7.3 Mapa Canonico de Permissoes

Fonte UNICA: `app/core/permissions_map.py`

**6 roles** (hierarquia decrescente de privilegio):

| Role | Gestao Org | Gestao Users | Gestao Teams | CRUD Athletes | CRUD Training | CRUD Match | Live Scout | Reports |
|------|-----------|-------------|-------------|--------------|--------------|------------|-----------|---------|
| `superadmin` | Sim | Sim | Sim | Sim | Sim | Sim | Sim | Sim |
| `dirigente` | Sim | Sim | Sim | Sim | Sim | Sim | Nao | Sim |
| `coordenador` | Nao | Nao | Sim | Sim | Sim | Sim* | Sim | Sim |
| `treinador` | Nao | Nao | Sim | Sim | Sim | Parcial | Sim | Sim |
| `membro` | Nao | Nao | Nao | Nao | Nao | Nao | Nao | Nao |
| `atleta` | Nao | Nao | Nao | Nao | Nao | Nao | Nao | Sim** |

*Coordenador: nao pode deletar match. **Atleta: somente visualizacao.

> Para lista completa de 30+ permissoes, ver `app/core/permissions_map.py:13-317`

### 7.4 Hierarquia de Validacao

Quatro niveis progressivos de validacao de acesso:

```
1. require_roles(ctx, roles)           → 403 se papel nao autorizado
2. require_membership(ctx)             → 403 se sem vinculo ativo (R42)
3. require_org_scope(org_id, ctx)      → 403 se org diferente da do contexto
4. require_team_scope(team_id, ctx, db) → 403 se equipe fora da org do contexto
```

Superadmin (R3) bypassa TODOS os niveis.

> Fonte: `app/core/permissions.py`, `app/core/deps.py:30-92`

---

## 8. Tarefas Assincronas (Celery)

### 8.1 Configuracao

```python
# Fonte: app/core/celery_app.py
app = Celery("hbtrack_tasks", broker=REDIS_URL, backend=REDIS_URL)
```

| Parametro | Valor |
|-----------|-------|
| Broker | Redis (`redis://localhost:6379/0`) |
| Backend | Redis (`redis://localhost:6379/1`) |
| Timezone | `America/Sao_Paulo` |
| Serializer | JSON |
| Result expiry | 1 hora |

Queues: `alerts` (alertas/wellness) e `maintenance` (cleanup/status).

### 8.2 Jobs Agendados (Beat Schedule)

| Job | Cron | Queue | Descricao |
|-----|------|-------|-----------|
| `check_weekly_overload` | Dom 23:00 | alerts | Verifica sobrecarga semanal |
| `check_wellness_response_rates` | Diario 08:00 | alerts | Taxa de resposta wellness |
| `cleanup_old_alerts` | Dom 02:00 | maintenance | Remove alertas antigos |
| `cleanup_expired_exports` | Diario 03:00 | maintenance | Remove exports expirados |
| `update_training_session_statuses` | A cada 1min | maintenance | Transicoes automaticas de status |
| `anonymize_old_training_data` | Diario 04:00 | maintenance | LGPD: anonimizar dados >3 anos |
| `refresh_training_rankings` | Diario 05:00 | maintenance | Refresh cache de analytics |

> Fonte: `app/core/celery_app.py:67-162`

### 8.3 Padrao de Task

```python
@app.task(
    name="app.core.celery_tasks.check_weekly_overload_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def check_weekly_overload_task(self) -> Dict[str, Any]:
    # Tasks Celery sao SYNC — executar async via asyncio.run() ou loop
    ...
```

---

## 9. Exemplo Completo de Fluxo

**Cenario**: `POST /api/v1/training-sessions` — criar sessao de treino.

### Passo 1: Request chega

```
POST /api/v1/training-sessions
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  Content-Type: application/json
  X-Request-ID: 550e8400-e29b-...
Body:
  { "team_id": "uuid", "session_at": "2026-02-10T18:00:00Z", "session_type": "quadra", ... }
```

### Passo 2: Middleware processa

1. `RequestIDMiddleware` — gera/propaga `X-Request-ID`, loga entrada
2. `SecurityHeadersMiddleware` — adiciona headers de seguranca na response
3. `CORSMiddleware` — valida origin (preflight ja respondido antes)

### Passo 3: Autenticacao (Depends)

```python
# app/core/context.py:get_current_context()
1. Extrai token do header Authorization (ou cookie hb_access_token)
2. decode_access_token(token) → payload com {sub: user_id, ...}
3. SELECT user WHERE id = user_id AND deleted_at IS NULL
4. Se nao superadmin: valida vinculo ativo (R42)
5. Resolve permissoes: get_permissions_for_role(role_code)
6. Retorna ExecutionContext(user_id, email, role_code, org_id, permissions, ...)
```

### Passo 4: Autorizacao (Router)

```python
# app/api/v1/routers/training_sessions.py:199-202
@router.post("", response_model=TrainingSession, status_code=201)
async def create_training_session(
    payload: TrainingSessionCreate,                    # Pydantic valida body
    db: AsyncSession = Depends(get_async_db),          # Sessao DB
    context: ExecutionContext = Depends(
        require_role(["dirigente", "coordenador", "treinador"])  # Valida papel
    ),
):
    context.requires("can_create_training")  # Verifica permissao granular → 403 se nao
```

### Passo 5: Service (Logica de Negocio)

```python
# app/services/training_session_service.py
service = TrainingSessionService(db, context)
session = await service.create(payload)
# → Valida team_id pertence a org do contexto
# → Valida session_type in ('quadra','fisico','video','reuniao','teste')
# → Valida focus percentages sum <= 120%
# → db.add(TrainingSession(..., created_by_user_id=context.user_id))
# → db.flush()
```

### Passo 6: Triggers (DB)

```
INSERT INTO training_sessions →
  trg_set_updated_at()         → updated_at = NOW()
  fn_derive_phase_focus()      → phase_focus_attack = (attack_pct >= 5%), etc.
```

### Passo 7: Response

```python
await db.commit()
await db.refresh(session)
return TrainingSession.model_validate(session)  # → 201 Created
```

### Cenarios de Erro

| Cenario | Onde falha | HTTP | ErrorCode |
|---------|-----------|------|-----------|
| Token ausente | `get_current_context()` | 401 | `UNAUTHORIZED` |
| Papel "atleta" tenta criar | `require_role()` | 403 | `FORBIDDEN` |
| Sem vinculo ativo | `get_current_context()` (R42) | 403 | `NO_ACTIVE_MEMBERSHIP` |
| Sem permissao `can_create_training` | `context.requires()` | 403 | Permissao necessaria |
| Focus sum > 120% | CHECK constraint PostgreSQL | 422 | `validation_check_constraint` |
| team_id inexistente | FK constraint | 422 | `validation_foreign_key` |

---

## 10. Checklist por Feature

### 10.1 Checklist por Camada

**Model** (quando criar/alterar tabela):
- [ ] PK UUID com `gen_random_uuid()`
- [ ] `organization_id` FK (se tabela de dominio)
- [ ] `created_at`, `updated_at` com server_default
- [ ] `deleted_at`, `deleted_reason` com constraint `ck_*_deleted_reason`
- [ ] `created_by_user_id` FK
- [ ] CHECKs para enums, ranges, somas
- [ ] Indexes para FKs e campos de busca frequente
- [ ] Migration Alembic criada e testada

**Schema**:
- [ ] `{Entity}Create` com validacao Pydantic (Field, ge, le, min_length)
- [ ] `{Entity}Update` com todos os campos Optional
- [ ] `{Entity}Response` com `model_config = ConfigDict(from_attributes=True)`
- [ ] `{Entity}PaginatedResponse` com items, total, page, limit, pages

**Service**:
- [ ] Constructor: `__init__(self, db: AsyncSession, context: ExecutionContext)`
- [ ] Filtra por `organization_id == ctx.organization_id`
- [ ] Filtra por `deleted_at.is_(None)`
- [ ] Validacao de negocio no service (nao no router)
- [ ] Levanta excecoes do `app.core.exceptions` (nao HTTPException)
- [ ] Metodos async

**Router**:
- [ ] Endpoints estaticos ANTES de `/{id}`
- [ ] `permission_dep()` ou `require_role()` em endpoints protegidos
- [ ] `response_model` e `responses` especificados
- [ ] Status code correto (201 para POST, 200 para GET/PATCH/DELETE)
- [ ] Registrado em `api.py`
- [ ] Tags para agrupamento OpenAPI

**Testes**:
- [ ] Unit test para service (validacao de negocio)
- [ ] Integration test com `async_db` (para constraints DB)
- [ ] API test com `client`/`auth_client` (para auth/RBAC)

**Artefatos** (ver [CHECKS.md](CHECKS.md)):
- [ ] `python scripts/generate_docs.py --openapi` (se alterou rotas/schemas)
- [ ] `python scripts/generate_docs.py --schema` (se alterou models/migrations)
- [ ] `python scripts/generate_docs.py --alembic` (se criou migration)

### 10.2 Anti-Patterns

| Anti-Pattern | Correto |
|-------------|---------|
| Logica de negocio no router | Mover para service |
| `HTTPException` no service | Usar `NotFoundError`, `ValidationError`, etc. |
| Query sem filtro `deleted_at IS NULL` | Sempre filtrar soft deletes |
| Query sem filtro `organization_id` | Sempre filtrar pelo tenant do contexto |
| DELETE fisico (`db.delete()`) | Soft delete: `deleted_at = now(), deleted_reason = '...'` |
| Mock de DB em integration test | Usar `async_db` real (fixtures) |
| `/{id}` antes de endpoints estaticos | Estaticos primeiro, parametrizados depois |
| Criar base class para services | Composicao: constructor injection |
| Adicionar campo sem migration | Sempre criar migration Alembic |
| Inventar campo/constraint nao ancorado | Verificar `schema.sql` e `openapi.json` primeiro |

### 10.3 Boas Praticas

| Pratica | Detalhes |
|---------|---------|
| Async-first | Todos os endpoints e services sao `async def` |
| Soft delete universal | `deleted_at` + `deleted_reason` em toda tabela de dominio |
| Audit fields | `created_at`, `updated_at`, `created_by_user_id` |
| Tenant isolation | `organization_id` em queries, validado pelo contexto |
| Permission check duplo | `require_role()` no endpoint + `ctx.requires()` no service |
| Error mapping | PostgreSQL SQLSTATE → HTTP status code via `POSTGRES_ERROR_MAP` |
| Response validation | Sempre usar `response_model` para garantir contrato OpenAPI |
| Artefatos atualizados | Regenerar `schema.sql`/`openapi.json` apos mudancas |

---

## 11. Testes

### 11.1 Estrutura de Diretorios

```
tests/
  conftest.py                          # Fixtures globais: db, async_db, client, auth_client
  api/                                 # Testes de API (HTTP via TestClient)
    test_training.py                   # Exemplo: TestTrainingSessionsAPI, TestAttendanceAPI
  unit/                                # Testes unitarios (sem I/O)
    test_config.py, test_context.py    # Core logic, schemas, validacoes puras
  integration/                         # Testes de integracao (com DB real)
    conftest.py                        # Fixture de client para integracao
  training/invariants/                 # Testes de invariantes (INVARIANTS_TESTING_CANON.md)
    conftest.py                        # Fixtures async: person, user, org, team, season, athlete
    test_inv_train_XXX_*.py            # 1 arquivo por invariante
  athletes/                            # Testes de dominio atleta
    conftest.py                        # Fixtures sync: person, user, org, membership, athlete
    test_athlete_model.py, test_athlete_routes.py, test_athlete_service.py
  e2e/                                 # Testes end-to-end
  teams/, users/, organizations/       # Testes por dominio
  seasons/, memberships/, games/       # Testes por dominio
```

### 11.2 Fixtures de Isolamento (Savepoint)

O sistema usa **savepoint transacional** para isolamento total — cada teste roda dentro de uma transacao que e revertida ao final.

**Fixture sincrona (`db`)**:
```python
# Fonte: tests/conftest.py:51-88
@pytest.fixture(scope="function")
def db() -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    nested = connection.begin_nested()  # Savepoint

    # Recria savepoint apos commits internos
    @sa.event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    yield session
    session.close()
    transaction.rollback()   # Reverte TUDO
    connection.close()
```

**Fixture assincrona (`async_db`)**:
```python
# Fonte: tests/conftest.py:91-121
@pytest_asyncio.fixture(scope="function")
async def async_db() -> AsyncSession:
    async_engine = create_async_engine(async_db_url, poolclass=NullPool)
    async with async_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = async_sessionmaker(bind=connection, class_=AsyncSession)()
            async with connection.begin_nested():  # Savepoint
                yield session
                await session.close()
                await transaction.rollback()
    await async_engine.dispose()
```

### 11.3 Fixtures de Autenticacao

**TestClient com override de DB**:
```python
# Fonte: tests/conftest.py:124-142
@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: (yield db)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**AuthenticatedClient (wrapper com cookies)**:
```python
# Fonte: tests/conftest.py:204-230
@pytest.fixture
def auth_client(client, superadmin_cookies):
    class AuthenticatedClient:
        def __init__(self, test_client, cookies):
            self._client = test_client
            self._cookies = cookies
        def get(self, url, **kwargs):
            kwargs.setdefault("cookies", self._cookies)
            return self._client.get(url, **kwargs)
        # post, patch, delete identicos
    return AuthenticatedClient(client, superadmin_cookies)
```

**Cookies com cache de sessao** (evita rate limiting):
```python
# Fonte: tests/conftest.py:176-200
@pytest.fixture
def superadmin_cookies(client, superadmin_credentials):
    global _superadmin_cookies_cache
    if _superadmin_cookies_cache is not None:
        return _superadmin_cookies_cache
    response = client.post("/api/v1/auth/login", data={...})
    _superadmin_cookies_cache = dict(response.cookies)
    return _superadmin_cookies_cache
```

Fixtures de autenticacao disponiveis:

| Fixture | Role | Uso |
|---------|------|-----|
| `auth_client` | superadmin | Testes com acesso total |
| `treinador_auth_client` | treinador | Testes com escopo de equipe |
| `superadmin_cookies` | superadmin | Cookies para requests manuais |
| `treinador_cookies` | treinador | Cookies para requests manuais |
| `test_team_id` | - | ID de equipe ativa (via API) |
| `treinador_team_id` | - | ID de equipe do treinador (via API) |

### 11.4 Fixtures de Dominio (Async — para invariantes)

```python
# Fonte: tests/training/invariants/conftest.py
# Padroes: INSERT via text() SQL puro dentro de async_db

@pytest_asyncio.fixture
async def person_id(async_db):
    result = await async_db.execute(text("""
        INSERT INTO persons (full_name, first_name, last_name)
        VALUES ('Teste Pessoa', 'Teste', 'Pessoa') RETURNING id
    """))
    return result.scalar_one()

@pytest_asyncio.fixture
async def organization(async_db):
    result = await async_db.execute(text("""
        INSERT INTO organizations (name, slug) VALUES ('Org Teste', 'org-teste')
        RETURNING id, name, slug
    """))
    row = result.fetchone()
    return {"id": row.id, "name": row.name, "slug": row.slug}
```

**Cadeia tipica de fixtures para testes de invariante**:
```
async_db → person_id → user → organization → team → season_ativa → membership → athlete → training_session
```

### 11.5 Organizacao de Testes por Tipo

| Tipo | Diretorio | Fixture principal | O que testa | Exemplo |
|------|-----------|-------------------|-------------|---------|
| Unit | `tests/unit/` | Nenhuma (ou mocks) | Logica pura sem I/O | Validacao de schema, config |
| Integration | `tests/integration/` | `async_db` | Service + DB real | Constraints, queries, side effects |
| API | `tests/api/` | `client` / `auth_client` | HTTP status, auth, response shape | 401 sem token, 200 com auth |
| Invariante | `tests/training/invariants/` | `async_db` + fixtures de dominio | Regras de negocio canonicas | INV-TRAIN-001..N |
| E2E | `tests/e2e/` | `auth_client` | Fluxos completos multi-endpoint | Criar sessao → presenca → fechar |

### 11.6 Padroes de Teste

**Teste de API (classe + cenarios de erro/sucesso)**:
```python
# Fonte: tests/api/test_training.py
class TestTrainingSessionsAPI:
    """Testes de API para sessoes de treino."""

    def test_list_sessions_requires_auth(self, client):
        """401 sem autenticacao."""
        response = client.get("/api/v1/training-sessions")
        assert response.status_code == 401

    def test_list_sessions_success(self, auth_client):
        """200 com autenticacao."""
        response = auth_client.get("/api/v1/training-sessions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
```

**Teste de invariante (async + DB real)**:
```python
# Fonte: tests/training/invariants/test_inv_train_XXX_*.py
class TestInvTrainXXX:
    """INV-TRAIN-XXX: <enunciado da invariante>
    Evidencia: schema.sql — CONSTRAINT ck_... / Arquivo + Simbolo
    """

    @pytest.mark.asyncio
    async def test_caso_valido(self, async_db, training_session):
        # Inserir dado valido — deve passar sem erro
        ...

    @pytest.mark.asyncio
    async def test_violacao_minima(self, async_db, training_session):
        # Inserir dado que viola a invariante — deve falhar com SQLSTATE/constraint
        with pytest.raises(IntegrityError) as exc_info:
            await async_db.execute(text("INSERT INTO ..."))
            await async_db.flush()
        assert "constraint_name" in str(exc_info.value.orig)
```

> Para protocolo completo de testes de invariantes, ver `docs/02-modulos/training/INVARIANTS_TESTING_CANON.md`
