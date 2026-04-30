---
doc_type: canon
version: "2.0.0"
last_reviewed: "2026-03-17"
status: active
---

# Documentação Canônica — HB Track

Este diretório contém os artefatos normativos soberanos do HB Track. Todo módulo, agente e implementação deriva daqui.

## Propósito

`docs/_canon/` é a camada normativa global do sistema. Enquanto a documentação de módulo (`docs/hbtrack/modulos/`) governa comportamento específico de cada módulo, os documentos aqui presentes estabelecem as regras, convenções e escopo que todos os módulos devem respeitar sem exceção.

Nenhuma implementação, contrato de módulo ou decisão técnica pode contradizer os artefatos deste diretório sem processo formal de revisão.

## Hierarquia Normativa

```
docs/_canon/AGENT_INSTRUCTIONS.md (boot permanente)
  ├── CONTRACT_SYSTEM_RULES.md        ← regras do sistema contract-driven
  ├── CONTRACT_SYSTEM_LAYOUT.md       ← layout de filesystem
  └── docs/_canon/                     ← nível global normativo (este diretório)
        └── docs/hbtrack/modulos/      ← nível de módulo
              └── implementação         ← código, migrations, testes
```

Regra: em caso de conflito entre níveis, o nível superior prevalece sempre.

**Nota importante (APIs)**: convenções, regras de validação e templates de **API HTTP/OpenAPI** têm SSOT em `.contract_driven/templates/api/api_rules.yaml` (conforme `.contract_driven/CONTRACT_SYSTEM_RULES.md`).

## Artefatos Canônicos Globais

| # | Arquivo | Responsabilidade |
|---|---------|-----------------|
| 1 | `README.md` | Este guia de navegação — estrutura, hierarquia, ordem de leitura |
| 2 | `OPERATIONS.md` | Referência operacional condensada: soberania, boundaries, precedência, naming, validação |
| 3 | `SYSTEM_SCOPE.md` | Missão do sistema, 5 atores canônicos, 9 macrodomínios, o que está fora do escopo |
| 4 | `ARCHITECTURE.md` | Stack canônica, 5 princípios arquiteturais, estrutura de camadas, ADRs registradas |
| 5 | `CODE_ARCHITECTURE.md` | Clean Architecture, organização de pastas backend, nomenclatura |
| 6 | `MODULE_MAP.md` | Taxonomia dos 17 módulos canônicos, responsabilidades, dependências entre módulos |
| 7 | `GLOBAL_INVARIANTS.md` | Invariantes globais (INV-*) — guardrails soberanos cross-módulo |
| 8 | `SECURITY_RULES.md` | Regras globais de segurança — autenticação/autorização, dados sensíveis, logging, hardening |
| 9 | `DATA_CONVENTIONS.md` | IDs, datas, enums, soft delete, naming de tabelas e campos |
| 10 | `CI_CONTRACT_GATES.md` | Gates de CI/qualidade para contratos (OpenAPI/AsyncAPI/JSON Schema/Arazzo) |
| 11 | `TEST_STRATEGY.md` | Estratégia de testes (unit/integration/contract/e2e) e evidências aceitas |
| 12 | `UI_CONTRACT_GUIDE.md` | Fundamentos de UI, tokens, componentes, estados (consolida UI_FOUNDATIONS + DESIGN_SYSTEM) |
| 13 | `C4_CONTEXT.md` | C4 — Contexto (atores/sistemas externos, limites) |
| 14 | `C4_CONTAINERS.md` | C4 — Containers (frontend, backend, workers, DB, integrações) |
| 15 | `CHANGE_POLICY.md` | Como propor, revisar e aprovar mudanças em artefatos canônicos e contratos de módulo |
| 16 | `DOMAIN_GLOSSARY.md` | Glossário de termos do domínio: handebol, sistema, governança contract-driven |
| 17 | `HANDBALL_RULES_DOMAIN.md` | Regras IHF documentadas (HBR-001..) — âncora normativa para módulos handball-sensíveis |
| 18 | `security/OWASP_API_CONTROL_MATRIX.yaml` | Matriz normativa (OWASP → declaração → evidência → gate) para controles de segurança de API |
| 19 | `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | Matriz normativa por módulo: fontes permitidas, artefatos obrigatórios e limites de inferência |
| 20 | `MODULE_REGISTRY.yaml` | Registro determinístico por módulo: status operacional, owner e superfícies esperadas |
| 21 | `TOOLCHAIN_HEALTH_POLICY.md` | Política canônica da toolchain: ferramentas obrigatórias, timeouts, degradação local e evidências |
| 22 | `CONTRACT_PIPELINE.md` | Estágios oficiais do pipeline contract-driven, com inputs, outputs e bloqueios permitidos |
| 23 | `DECISION_POLICY.md` | Regras DSS, quando Decision Discovery é obrigatório |
| 24 | `ARCHITECTURE_DECISION_BACKLOG.md` | Backlog de decisões arquiteturais abertas |
| 25 | `DATA_MIGRATION_POLICY.md` | Estratégia de migrations e evolução de dados (ADR-028) |
| 26 | `DEPLOY_PIPELINE.md` | Pipeline de deploy: estágios, aprovações, rollback (ADR-027) |
| 27 | `RUNTIME_CONTRACT_MONITORING_POLICY.md` | Política de monitoramento de contratos em runtime (ADR-029) |
| 28 | `FRONTEND_CONTRACT.md` | Contrato de frontend: componentes, eventos, integração com backend (ADR-030) |
| 29 | `UX_BRAND_CONTRACT.md` | Contrato visual canônico: marca, tipografia, tokens, dark mode e assets oficiais |
| 30 | `UX_SHELL_CONTRACT.md` | Contrato da shell autenticada: sidebar, drawer mobile, top bar, contexto operacional e user menu |
| 31 | `AUTH_EXPERIENCE_CONTRACT.md` | Contrato da experiência de autenticação: login, recuperação de senha, estados e redirects |
| 32 | `NAVIGATION_VISIBILITY_CONTRACT.md` | Contrato de navegação e visibilidade: agrupamento, rollout visual, roles e contexto |
| 33 | `FEATURE_REGISTRY.yaml` | Registro de features e sua maturidade |
| 34 | `IR_TO_SURFACE_MAPPING.yaml` | Mapeamento de IR (Intermediate Representation) para superfícies expostas |
| 35 | `AGENT_INSTRUCTIONS.md` | Instruções de boot permanente para agentes — carregado em toda sessão |
| 36 | `SCOPE_BOUNDARY_POLICY.md` | Política de fronteiras entre módulos — regras de referências permitidas/proibidas (ADR-034) |
| 37 | `SURVIVAL_SUITE_POLICY.md` | Política da suíte de sobrevivência — testes obrigatórios antes de mudança em gates/profiles/schemas |
| 38 | `C4_COMPONENTS_BACKEND.md` | C4 — Componentes do backend: detalhamento dos 17 módulos, camadas internas e dependências (current-state) |
| 39 | `RUNTIME_CURRENT_STATE.md` | Inventário factual do runtime atual: o que existe, o que é só contrato, o que é target-state (current-state) |
| 40 | `INTEGRATION_FLOWS.md` | Flows críticos de integração cross-módulo: auth, training→wellness→analytics, notifications, video/scout, ai_ingestion (governance) |
| 41 | `ADR_INDEX.md` | Índice unificado de todas as ADRs com status, supersession e tema — referência rápida sem ambiguidade |
| 42 | `SOURCE_AUTHORITY_GRAPH.yaml` | Grafo de autoridade de fontes — define hierarquia entre SSOT canônicas e derivadas |
| 43 | `SYNC_MANIFEST.yaml` | Manifesto de sincronização determinístico entre source graphs e artefatos derivados por módulo |
| 44 | `DOC_USAGE_MANIFEST.yaml` | Manifesto de uso de documentos — rastreia ownership e freshness das doc-rules por módulo |
| 45 | `AI_EXECUTION_ROLES_POLICY.md` | Política canônica de papéis de execução por agentes, evidências obrigatórias e limites de autoridade |
| 46 | `DECISION_MATERIALIZATION_POLICY.md` | Política de materialização de decisões: liga ADR + Decision IR a obrigações runtime, testes adversariais, gates e evidência fresca pós-main. |

### Subdiretórios Autorizados

- **`decisions/`** — ADRs aprovadas no padrão `ADR-NNN-<slug>.md`
- **`gates/`** — GATES_REGISTRY.yaml (registry de gates) e README.md
- **`security/`** — OWASP_API_CONTROL_MATRIX.yaml (matriz de controles)
- **`templates/`** — `SESSION_HANDOFF.template.md` (template de handoff); `DECISION_MATERIALIZATION_MATRIX.template.yaml` (template de matriz de materialização de decisões)
- **`graph/`** — Regras globais do source graph: global_rules.yaml, global_policies.yaml, lifecycle.yaml, source_map.yaml

> **Nota**: `BOOT_PROFILES.yaml` e `TASK_CATALOG.yaml` foram movidos para `.contract_driven/` — veja [docs/_canon/AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) §7 para referência atualizada.

## Ordem Recomendada de Leitura

Para novos colaboradores e agentes, leia nesta sequência:

1. **`docs/_canon/AGENT_INSTRUCTIONS.md`** (raiz do repo) — boot permanente, módulos, task_types, bloqueios, boot profiles
2. **`OPERATIONS.md`** — referência operacional rápida
3. **`SYSTEM_SCOPE.md`** — entenda o que o sistema é, quem são os atores, o que está dentro e fora do escopo
4. **`ARCHITECTURE.md`** — entenda a stack, os princípios e a estrutura de camadas
5. **`MODULE_MAP.md`** — entenda os 17 módulos, suas responsabilidades e dependências
6. **`GLOBAL_INVARIANTS.md`** — conheça guardrails globais (INV-*) antes de propor contratos ou invariantes de módulo
7. **`SECURITY_RULES.md`** — segurança global antes de qualquer contrato público
8. **`.contract_driven/templates/api/api_rules.yaml`** — SSOT de convenções/validações/templates de API HTTP
9. **`DATA_CONVENTIONS.md`** — convenções de dados antes de criar qualquer schema ou migration
10. **`CI_CONTRACT_GATES.md`** — entenda quais validações/gates tornam um contrato "pronto"
11. **`TOOLCHAIN_HEALTH_POLICY.md`** — valide a saúde da toolchain e o significado de `DEGRADED`
12. **`CONTRACT_PIPELINE.md`** — veja os estágios formais e a condição de avanço entre eles
13. **`TEST_STRATEGY.md`** — entenda evidências e níveis de teste esperados
14. **`HANDBALL_RULES_DOMAIN.md`** — leia se for trabalhar em módulos handball-sensíveis
15. **`DOMAIN_GLOSSARY.md`** — consulte sempre que encontrar um termo do domínio não claro
16. **`CHANGE_POLICY.md`** — leia antes de propor qualquer alteração em artefatos normativos

Após ler os canônicos globais, leia a documentação do módulo em que for trabalhar (`docs/hbtrack/modulos/<módulo>/`).

## Regra Cardinal

> **Nenhuma implementação sem contrato vigente.**

Isso significa:
- Nenhum endpoint HTTP sem contrato OpenAPI correspondente
- Nenhuma migration sem invariante documentada para constraints críticas
- Nenhuma regra de negócio derivada do handebol sem âncora em `HANDBALL_RULES_DOMAIN.md`
- Nenhum evento assíncrono sem contrato AsyncAPI
- Nenhum workflow multi-step sem definição Arazzo quando formalmente exigido

## Artefatos Relacionados

- **Boot permanente**: `docs/_canon/AGENT_INSTRUCTIONS.md`
- **Sistema de contratos**: `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- **Layout canônico**: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- **Templates**: `.contract_driven/GLOBAL_TEMPLATES.md`
- **Documentação de módulos**: `docs/hbtrack/modulos/`
- **Contract gates (validação)**: `python3 scripts/validate_contracts.py`

---

*Última revisão: 2026-03-17*
