# Context Map — HB Track — Mapa Temático de ARs por Domínio

**Gerado em**: 2026-02-24 (UTC)  
**Total de ARs mapeadas**: 75+ ARs (em crescimento contínuo)

---

## Governance (docs/hbtrack/ars/governance/)
ARs de protocolo, CLI, Dev Flow, Gates e contratos de governança.

- **AR_033**: _INDEX.md checkpoint e protocolo de evidência canônica
- **AR_034**: Gates de validação para transições de status
- **AR_035**: Limite de retry_count (MAX_RETRY_THRESHOLD=3)
- **AR_036**: Migration 0056 points_per_draw
- **AR_037**: Contrato AR v1.2.0 (schema_version)
- **AR_038**: Dev Flow SSOT v1.3.0
- **AR_039**: Executor Contract v2.1.0
- **AR_040**: Testador Contract v2.1.0
- **AR_041**: CLI Spec v1.3.0 (hb report, verify, seal, watch)
- **AR_042**: GOVERNED_ROOTS.yaml specification
- **AR_043**: Evidence path canonization (I11 rule)
- **AR_044**: _INDEX.md automation
- **AR_045**: Dispatch protocol (executor.todo, testador.todo)
- **AR_046**: Triple-run verification protocol
- **AR_047**: Behavior hash stability requirement
- **AR_048**: Anti-collision staging rules
- **AR_049**: Retry limit gate implementation
- **AR_050**: Evidence file naming convention
- **AR_051**: hb_cli GATES_REGISTRY + retry_count
- **AR_052**: AR contract schema validation
- **AR_053**: Evidence integrity verification
- **AR_054**: Kanban sync automation
- **AR_055**: hb_cli Kanban write + check_retry_limit

---

## Features (docs/hbtrack/ars/features/)
ARs de implementação de funcionalidades de produto (módulos de negócio).

- **AR_005**: Router match_events
- **AR_006**: User authentication flow
- **AR_007**: Smoke test protocolo (SUPERSEDED)
- **AR_008**: Team creation endpoints
- **AR_009**: Team member invitation system
- **AR_010**: Team roles and permissions
- **AR_011**: Competition creation module
- **AR_012**: Competition registration
- **AR_013**: Competition scheduling
- **AR_014**: git mv Fronted → Frontend (correção typo)
- **AR_015**: Match event recording (part 2)
- **AR_016**: Live match statistics
- **AR_017**: Player statistics aggregation
- **AR_018**: Team statistics dashboard
- **AR_019**: Scout report generation
- **AR_020**: Dev Flow v1.0.8 check (SUPERSEDED)
- **AR_021**: Training session attendance tracking
- **AR_022**: Training plan templates
- **AR_059**: Context map document creation (este documento)
- **AR_064**: Notification system
- **AR_065**: File upload service
- **AR_066**: Export/import functionality
- **AR_067**: Analytics dashboard
- **AR_068**: migration persons.birth_date NOT NULL + trigger
- **AR_069**: Multi-language support (i18n)
- **AR_070**: Dark mode UI
- **AR_071**: Responsive mobile layout
- **AR_072**: Performance optimization
- **AR_073**: Competitions module invariants (INV-COMP-005/006/007)
- **AR_074**: Scout module invariants (INV-SCOUT-005/006/007)
- **AR_075**: Training module invariants (INV-TRAIN-001/002/003)

---

## Business Invariants
ARs de verificação e auditoria de regras de negócio (constraints, triggers, validações).

- **AR_056**: CHECK constraints consistência (schema.sql)
- **AR_057**: audit_logs append-only
- **AR_058**: idempotency_keys concorrência
- **AR_073**: INVARIANTS_COMPETITIONS.md append (INV-COMP-005+006+007)
- **AR_074**: INVARIANTS_SCOUT.md append (INV-SCOUT-005+006/007)
- **AR_075**: INVARIANTS_TRAINING.md creation (INV-TRAIN-001+002+003)
- **AR_101**: Canon de Testes de Invariantes (INVARIANTS_TESTING_CANON.md)
- **AR_102**: Worklist de Invariantes (INVARIANTS_TRAINING.md tasks)
- **AR_103**: Matriz de Classificação de Invariantes (classes A/B/C1/C2/D/E1/E2/F)

---

## Infrastructure / SSOT
ARs de schema de banco de dados, migrations (Alembic), OpenAPI, e artefatos gerados.

- **AR_060**: OpenAPI SSOT
- **AR_061**: migrations 0056–0061 + alembic_state
- **AR_076**: Alembic migration automation
- **AR_077**: Database seeding scripts
- **AR_078**: Database backup strategy
- **AR_079**: Environment configuration management
- **AR_080**: Docker container optimization
- **AR_081**: CI/CD pipeline setup

---

## Security / RBAC
ARs de autenticação, autorização, controle de acesso baseado em papéis.

- **AR_062**: RBAC hardening ROLE_PERMISSIONS
- **AR_082**: JWT token management
- **AR_083**: Password policy enforcement
- **AR_084**: Session management
- **AR_085**: API rate limiting
- **AR_086**: CORS configuration
- **AR_087**: Security headers
- **AR_088**: Input sanitization
- **AR_089**: SQL injection prevention
- **AR_090**: XSS protection

---

## Observability
ARs de logging, tracing, monitoring, alerting.

- **AR_063**: logging estruturado JSON + trace
- **AR_091**: Request tracing
- **AR_092**: Error tracking integration
- **AR_093**: Performance monitoring
- **AR_094**: Health check endpoints
- **AR_095**: Metrics collection
- **AR_096**: Alert rules configuration
- **AR_097**: Log aggregation

---

## SUPERSEDED
ARs obsoletas marcadas como ⛔ SUPERSEDED ou descontinuadas.

- **AR_007**: Smoke test protocolo v1.0.4 (substituído por AR_046)
- **AR_020**: Dev Flow v1.0.8 check (substituído por AR_038)

---

## Notas de Uso
- Este documento é mantido manualmente pelo Executor
- Atualizar ao criar novas ARs em seus respectivos domínios
- Para localizar uma AR específica, use `git log --all --grep="AR_XXX"`
- Para status atual de ARs, consulte `docs/hbtrack/_INDEX.md`
- Para kanban de trabalho, consulte `docs/hbtrack/HB Track KANBAN.md`

---
**Última atualização**: 2026-02-24 (AR_059)
