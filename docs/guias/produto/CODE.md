# CODE.md — Análise de Governança da Implementação Backend

> **Tipo:** Análise arquitetural
> **Escopo:** Implementação backend no sistema Contract-Driven Development do HB Track
> **Versão:** 1.0.0 — 2026-03-21
> **Baseado em:** inspeção direta de todos os artefatos do repositório

---

## PARTE 1 — Veredito Geral

| Pergunta | Resposta |
|----------|----------|
| O backend é implementado apenas pelos contratos finais? | **NÃO** |
| O backend é implementado por contratos + arquivos de orientação/instrução? | **SIM** |
| Esses arquivos de orientação são centrais, relevantes ou apenas auxiliares? | **CENTRAIS** — sem eles, a geração não ocorre nem poderia ocorrer corretamente |
| A camada de orientação muda conteúdo, processo ou apenas aprovação? | **OS TRÊS** — conteúdo, processo e aprovação são todos governados por arquivos fora dos contratos |

**Conclusão direta:**

O backend do HB Track é governado por **duas camadas soberanas paralelas**:

1. **Contratos** — definem o *quê*: endpoints, shapes de request/response, domínio de dados, eventos.
2. **Camada de orientação** — define o *como*, *em que ordem*, *com quais regras*, *com quais restrições* e *quando a implementação pode ser aceita*.

A ausência de qualquer arquivo central da camada de orientação bloquearia ou deformaria a implementação — não seria apenas uma perda de contexto, mas uma falha estrutural no fluxo.

---

## PARTE 2 — Mapa dos Artefatos que Influenciam a Implementação

| Arquivo | Categoria | Papel real | Etapa do fluxo | Muda conteúdo do backend? | Muda processo? | Muda apenas aprovação? | Obrigatório / condicional / auxiliar | Nível de influência |
|---------|-----------|------------|----------------|---------------------------|----------------|------------------------|--------------------------------------|---------------------|
| `contracts/openapi/paths/<módulo>.yaml` | contrato gerador direto | Define endpoints, request/response shapes exatos; `api.py` implementa exatamente o que está aqui | GC1, GC5 | SIM — campos, paths, métodos, status codes | NÃO | NÃO | Obrigatório | crítico |
| `contracts/openapi/openapi.yaml` | contrato gerador direto | Root do OpenAPI; security schemes globais, component refs compartilhados | GC1, GC5 | SIM — schemas compartilhados, security | NÃO | NÃO | Obrigatório | crítico |
| `contracts/schemas/<módulo>/*.schema.json` | contrato gerador direto | Shapes de domínio; derivam diretamente os Pydantic schemas (`schemas.py`) e Django models (`models.py`) | GC1, GC3, GC4 | SIM — estrutura de dados do model e schema | NÃO | NÃO | Obrigatório | crítico |
| `contracts/asyncapi/` | contrato gerador direto | Event contracts; usados em geração de event handlers quando layer=all | GC1 (quando aplicável) | SIM — event payloads | NÃO | NÃO | Condicional (módulos com asyncapi) | alto |
| `.contract_driven/agent_prompts/generate_code.prompt.md` | instrução/orientação de implementação | **Cérebro da geração**: define fases GC1–GC6, regras R1–R5, estrutura de pastas exata, o que gerar em cada layer, como derivar Pydantic de JSON Schema, quando bloquear | GC1–GC6 (todas as fases de geração) | SIM — determina toda a estrutura e lógica | SIM — define as 6 fases sequenciais | NÃO | Obrigatório | crítico |
| `docs/_canon/CODE_ARCHITECTURE.md` | instrução/orientação de implementação | Especifica stack (Django 5.x, Ninja 1.x, Python 3.12, PostgreSQL 16), arquitetura limpa em 4 layers, organização exata de pastas, convenções de nomenclatura por tipo de artefato | GC1 (montagem de contexto) | SIM — stack, layer structure, nomes de entidades/use cases/routers | SIM — prerequisites obrigatórios (versão ≥ 1.1.0) | NÃO | Obrigatório (prerequisite explícito no generate_code.prompt.md) | crítico |
| `docs/_canon/FEATURE_REGISTRY.yaml` | instrução/orientação de implementação | Determina quais features existem por módulo; R3 do generate_code: "um use case por feature" — sem feature registrada, nenhum use case é gerado | GC1 (montagem de contexto), GC3 (use cases) | SIM — quantidade e nome de use cases em `application/use_cases.py` | NÃO | NÃO | Obrigatório | crítico |
| `docs/hbtrack/modulos/<módulo>/DOMAIN_RULES_<MOD>.md` | instrução/orientação de implementação | Regras de domínio; extraídas pelo agente e implementadas em `domain/rules.py`; definem validações, restrições e comportamentos do domínio | GC1 (montagem de contexto), GC2 (domain layer) | SIM — conteúdo de `domain/rules.py` | NÃO | NÃO | Obrigatório (sempre, per §4 OPERATIONS.md) | crítico |
| `docs/hbtrack/modulos/<módulo>/INVARIANTS_<MOD>.md` | instrução/orientação de implementação | Invariantes de entidade; determinam os métodos de validação implementados nas entidades (`domain/entities.py`) | GC1, GC2 | SIM — lógica de validação das entities | NÃO | NÃO | Obrigatório (sempre) | crítico |
| `docs/hbtrack/modulos/<módulo>/STATE_MODEL_<MOD>.md` | instrução/orientação de implementação | FSM (máquina de estados); quando presente, gera `domain/state_machine.py` com classes de estado e transições | GC1, GC2 | SIM — `domain/state_machine.py` inteiro | NÃO | NÃO | Condicional (módulos com FSM) | alto |
| `docs/hbtrack/modulos/<módulo>/PERMISSIONS_<MOD>.md` | instrução/orientação de implementação | Regras RBAC do módulo; afetam decorators e guards na interface layer (`interface/api.py`) | GC1, GC5 | SIM — lógica de autorização no router | NÃO | NÃO | Condicional (módulos com RBAC próprio) | alto |
| `docs/hbtrack/modulos/<módulo>/ERRORS_<MOD>.md` | instrução/orientação de implementação | Error codes e mensagens específicas do módulo; determinam os error responses implementados | GC1, GC5 | SIM — error handling no router e use cases | NÃO | NÃO | Condicional (módulos com error codes próprios) | médio |
| `.contract_driven/templates/api/api_rules.yaml` | instrução/orientação de implementação | SSOT das convenções HTTP: camelCase em campos de API, kebab-case em paths, Problem+JSON obrigatório em errors, formatos de ID/data, trailing slash proibida | GC1, GC5 | SIM — serializers, error shapes, naming em schemas.py e api.py | NÃO | NÃO | Obrigatório (referenciado explicitamente no generate_code.prompt.md e OPERATIONS.md §5) | alto |
| `docs/_canon/DATA_CONVENTIONS.md` | instrução/orientação de implementação | UUID v4, date_only (YYYY-MM-DD), timestamp_utc (RFC3339Z), snake_case no código vs camelCase em respostas de API | GC1 | SIM — formato de campos em models, schemas e respostas | NÃO | NÃO | Obrigatório | alto |
| `docs/_canon/SECURITY_RULES.md` | instrução/orientação de implementação | Regras de segurança: auth requirements, tratamento de dados sensíveis, secrets; afetam a interface layer | GC1 | SIM — decorators de auth, headers de segurança, validação de input | NÃO | NÃO | Obrigatório | alto |
| `docs/_canon/OPERATIONS.md §§2,5,6` | instrução/orientação de implementação | §2: módulos boundary (o que cada módulo pode/não pode implementar); §5: regras de validação (enum closure, drift, formatos); §6: convenções de nomenclatura (snake_case/camelCase) | GC1 | SIM — o que o módulo pode implementar (boundary), como nomear variáveis | NÃO | NÃO | Obrigatório | alto |
| `.contract_driven/DOMAIN_AXIOMS.json` | instrução/orientação de implementação | Enums fechados; qualquer valor de enum não presente aqui é rejeitado (enum closure rule) — define o universo de valores válidos para enums no código | GC1 | SIM — valores de enums nas entities e schemas | SIM — enum closure é gate bloqueante | NÃO | Obrigatório | alto |
| `docs/_canon/decisions/ADR-031-backend-framework.md` | instrução/orientação de implementação | Decisão arquitetural que estabelece Django Ninja como framework; prerequisite explícito do generate_code.prompt.md | GC1 (prerequisite check) | SIM — confirma o stack a usar | SIM — ausência bloqueia execução | NÃO | Obrigatório (prerequisite do generate_code) | alto |
| `docs/_canon/decisions/ADR-026` | instrução/orientação de implementação | ADR de arquitetura; prerequisite explícito do generate_code.prompt.md | GC1 (prerequisite check) | SIM — contexto arquitetural relevante | SIM — ausência bloqueia execução | NÃO | Obrigatório (prerequisite do generate_code) | alto |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | instrução/orientação de implementação | Regras IHF do handebol; influencia regras de domínio em módulos esportivos (training, wellness, medical) | GC1 (quando sport trigger ativo) | SIM — regras de negócio do domínio esportivo | NÃO | NÃO | Condicional (módulos esportivos) | médio |
| `docs/hbtrack/modulos/<módulo>/SPORT_SCIENCE_RULES_<MOD>.md` | instrução/orientação de implementação | Ciência do esporte aplicada ao módulo; influencia lógica de domínio em training, wellness, medical | GC1 | SIM — regras de cálculo/ciência no domínio | NÃO | NÃO | Condicional (training, wellness, medical) | médio |
| `docs/hbtrack/modulos/<módulo>/TEST_MATRIX_<MOD>.md` | instrução/orientação de implementação | Matriz de cenários de teste; orientam o que o agente gera em `tests/` | GC6 | SIM — cenários de teste em `tests/` | NÃO | NÃO | Obrigatório | médio |
| `.contract_driven/TASK_CATALOG.yaml` | governança/validação | Routing authority: mapeia generate_code → code_generator worker; define gates bloqueantes (AXIOM_INTEGRITY_GATE, OPENAPI_ROOT_STRUCTURE_GATE, ADVERSARIAL_ANALYSIS_GATE) e pré-requisitos | Fase 0 (boot/routing) | NÃO (não escreve código) | SIM — determina se e como a execução ocorre | SIM — gates bloqueantes | Obrigatório | alto |
| `.contract_driven/BOOT_PROFILES.yaml` | governança/validação | Define quais arquivos são carregados e em que ordem antes da execução; validações de session e task | Fase 0, Fase 1 | NÃO | SIM — sequência de carregamento do contexto | NÃO | Obrigatório | alto |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | governança/validação | ~23 seções de regras operacionais vinculantes; inclui hierarquia de precedência §5 (define qual artefato ganha em conflito), anti-patterns proibidos, enum closure, drift rules, naming | GC1 (contexto obrigatório no perfil contract_execution) | NÃO diretamente | SIM — define hierarquia de autoridade e blocos | SIM — anti-patterns são gates | Obrigatório | alto |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | governança/validação | Registry de todos os gates com critérios de PASS/FAIL; gates bloqueantes para generate_code: AXIOM_INTEGRITY_GATE, OPENAPI_ROOT_STRUCTURE_GATE, ADVERSARIAL_ANALYSIS_GATE | Fase de validação (pré e pós geração) | NÃO | SIM — define quais checks rodar | SIM — gates FAIL bloqueiam promoção | Obrigatório | alto |
| `docs/_canon/CI_CONTRACT_GATES.md` | governança/validação | Especificação detalhada dos gates: condições de PASS, evidências exigidas, regras de waiver | Fase de validação | NÃO | NÃO | SIM | Obrigatório | médio |
| `_reports/adversarial/<módulo>/ALL.adversarial.json` | governança/validação | Relatório do ADVERSARIAL_ANALYSIS_GATE; deve existir com `overall_status: PASS` para desbloquear generate_code | Fase 0 (eligibility check no `scripts/hb`) | NÃO | SIM — ausência ou FAIL bloqueia completamente | SIM | Obrigatório (prerequisite hard check no CLI) | alto |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | governança/validação | Backlog de decisões em aberto; decision IR aberta pode exigir decision_discovery antes de generate_code | Fase 0, Fase 1 | NÃO | SIM — pode obrigar execução prévia de decision_discovery | SIM — bloqueia se IR relevante aberta | Condicional | médio |
| `docs/_canon/CHANGE_POLICY.md` | governança/validação | Define quando mudanças exigem novo ADR; governa quando decision_discovery é obrigatório | Fase 0 | NÃO | SIM — pode obrigar etapas adicionais | SIM | Condicional | médio |
| `.contract_driven/waivers.json` | governança/validação | Rastreia waivers de gates aprovados; gate com waiver não bloqueia implementação | Fase de validação | NÃO | NÃO | SIM — gates waivered não bloqueiam | Condicional | baixo |
| `docs/_canon/AGENT_INSTRUCTIONS.md` | execução/orquestração | Protocolo master de boot (§0–§7): o que ler primeiro, como operar, 16 módulos canônicos, 9 task types, bloqueios, 8 regras core, SSoTs críticos | Fase 0 e 1 (boot completo) | NÃO diretamente | SIM — define o protocolo completo de execução | NÃO | Obrigatório | alto |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | execução/orquestração | Ponto de entrada do fluxo: determina task_type, valida no TASK_CATALOG, roteia para o worker correto | Fase 0 | NÃO | SIM — ponto de entrada obrigatório | NÃO | Obrigatório | alto |
| `scripts/hb` (CLI) | execução/orquestração | Orquestrador determinístico: `hb verify` (eligibility check), `hb check` (pre-authoring), `hb artifact` (per-artefact validation); implementa checks de elegibilidade de generate_code (module status, adversarial report, boot profile) | Todas as fases | NÃO | SIM — verifica pré-condições de execução | SIM — falha bloqueia | Obrigatório | alto |
| `docs/_canon/MODULE_REGISTRY.yaml` | execução/orquestração | SSOT dos 16 módulos canônicos com status; `scripts/hb` verifica que o módulo está em `implementation_ready` ou `validated_contract` antes de permitir generate_code | Fase 0 (eligibility check) | NÃO | SIM — status do módulo controla se geração pode ocorrer | SIM | Obrigatório | alto |
| `SESSION_HANDOFF.md` | estado/handoff | Estado da sessão atual: o que foi feito, o que está em aberto, próximos módulos, erros anteriores; orienta o agente sobre contexto operacional da sessão | Fase 0 (leitura obrigatória antes de qualquer coisa, §0 AGENT_INSTRUCTIONS) | PARCIAL — se handoff menciona módulo concluído, evita retrabalho | SIM — informa ordem e contexto de execução | NÃO | Condicional (quando existe) | médio |
| `_reports/session_start.json` | estado/handoff | Registro de sessão em curso: task_type, module, stage, boot_profile_id, artifacts criados; valida continuidade de sessão | Fase 0 (validação de boot profile e sessão ativa) | NÃO | SIM — valida continuidade e estado | NÃO | Obrigatório (quando sessão ativa) | médio |
| `docs/_canon/decisions/ADR-*.md` (outros) | contexto/referência | ADRs específicos: ADR-007 (auth), ADR-008 (authz), ADR-013 (logging), ADR-025 (CDCT/Pact), etc.; fornecem contexto de decisões anteriores | GC1 (quando relevantes ao módulo) | PARCIAL — ADRs de auth/logging influenciam interface layer | NÃO | NÃO | Condicional (quando módulo tem decision IR) | médio |
| `docs/_canon/GLOBAL_INVARIANTS.md` | contexto/referência | Invariantes globais do sistema (cross-module); podem afetar entities compartilhadas | GC1 | PARCIAL — quando invariante global se aplica ao módulo | NÃO | NÃO | Auxiliar | médio |
| `docs/_canon/CONTRACT_PIPELINE.md` | contexto/referência | Descrição dos 6 estágios do pipeline; contexto processual | Fase 1 (carregado no perfil contract_execution) | NÃO | NÃO | NÃO | Auxiliar | baixo |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | contexto/referência | Canonical filesystem: onde cada artefato mora, regras de naming; §15 explicitamente diz "usado apenas para determinar onde o artefato pertence" | GC1 | NÃO (determina paths, não conteúdo) | NÃO | NÃO | Auxiliar | baixo |
| `docs/_canon/DOMAIN_GLOSSARY.md` | contexto/referência | Glossário de termos; referência para nomenclatura consistente | GC1 | NÃO | NÃO | NÃO | Auxiliar | baixo |
| `docs/hbtrack/modulos/<módulo>/UI_CONTRACT_<MOD>.md` | contexto/referência | Contrato de UI; não é usado pelo backend generator | N/A para backend | NÃO | NÃO | NÃO | Auxiliar (frontend apenas) | nulo |
| `_reports/contract_gates/latest.json` | observabilidade | Snapshot do estado atual dos gates (derivado); lido para contexto, sem autoridade | Diagnóstico | NÃO | NÃO | NÃO | Auxiliar | nulo |
| `_reports/evidence/module_readiness_scorecard.json` | observabilidade | Scorecard de readiness (derivado); evidência de que módulo passou pelos gates de readiness | Diagnóstico | NÃO | NÃO | NÃO | Auxiliar | nulo |
| `_reports/READINESS_DASHBOARD.md` | observabilidade | Dashboard humano de readiness (derivado); legível por humano, sem autoridade normativa | Diagnóstico | NÃO | NÃO | NÃO | Auxiliar | nulo |
| `generated/resolved_policy/*.resolved.yaml` | observabilidade | Policy resolvida por módulo (derivado de contracts + api_rules); sem autoridade sobre fontes soberanas | Derivado | NÃO | NÃO | NÃO | Auxiliar | nulo |
| `generated/manifests/*.traceability.yaml` | observabilidade | Manifests de rastreabilidade (derivados); não influenciam geração | Derivado | NÃO | NÃO | NÃO | Auxiliar | nulo |

---

## PARTE 3 — Fluxo Real de Implementação do Backend

### Como começa

O humano inicia com `hb verify --task-type generate_code --module <módulo>`.

O CLI (`scripts/hb`) executa **3 checks de elegibilidade em sequência** antes de qualquer código ser discutido:
1. `module` existe em `MODULE_REGISTRY.yaml` com status `implementation_ready` ou `validated_contract`
2. Relatório adversarial existe em `_reports/adversarial/<módulo>/` com `overall_status: PASS`
3. `boot_profile_id` válido em `BOOT_PROFILES.yaml`

Qualquer falha → bloqueio completo. Não há execução parcial.

### Arquivos que entram ANTES do contrato

| Ordem | Arquivo | O que faz |
|-------|---------|-----------|
| 1 | `SESSION_HANDOFF.md` | Contexto obrigatório §0 — lido antes de qualquer operação |
| 2 | `docs/_canon/AGENT_INSTRUCTIONS.md` | Boot protocol — carregado pelo perfil `default` → `contract_execution` |
| 3 | `docs/_canon/OPERATIONS.md` | Referência operacional — carregado pelo perfil `contract_execution` |
| 4 | `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Regras operacionais vinculantes — carregado pelo perfil `contract_execution` |
| 5 | `docs/_canon/gates/GATES_REGISTRY.yaml` | Gates e critérios — carregado pelo perfil `contract_execution` |
| 6 | `.contract_driven/TASK_CATALOG.yaml` | Routing e gates bloqueantes — validado na Fase 0 |
| 7 | `.contract_driven/BOOT_PROFILES.yaml` | Perfil de boot e sequência — validado na Fase 0 |
| 8 | `docs/_canon/MODULE_REGISTRY.yaml` | Status do módulo — validado no CLI |
| 9 | `_reports/adversarial/<módulo>/ALL.adversarial.json` | Gate ADVERSARIAL PASS — verificado no CLI |

Apenas após todos esses checks passarem, o agente carrega o worker:

### Arquivo que entra JUNTO com o contrato (GC1 — Montagem de Contexto)

O `generate_code.prompt.md` instrui o agente a montar o contexto completo na fase GC1, carregando em paralelo:

- `contracts/openapi/paths/<módulo>.yaml` — **o contrato**
- `contracts/openapi/openapi.yaml` — root do OpenAPI
- `contracts/schemas/<módulo>/*.schema.json` — shapes de domínio
- `docs/_canon/FEATURE_REGISTRY.yaml` — features → use cases
- `docs/_canon/CODE_ARCHITECTURE.md` — stack e layers
- `docs/hbtrack/modulos/<módulo>/DOMAIN_RULES_<MOD>.md` — regras de domínio
- `docs/hbtrack/modulos/<módulo>/INVARIANTS_<MOD>.md` — invariantes
- `docs/hbtrack/modulos/<módulo>/STATE_MODEL_<MOD>.md` (se presente)
- `docs/hbtrack/modulos/<módulo>/PERMISSIONS_<MOD>.md` (se presente)
- `.contract_driven/DOMAIN_AXIOMS.json` — enums fechados
- `.contract_driven/templates/api/api_rules.yaml` — convenções HTTP
- `docs/_canon/DATA_CONVENTIONS.md` — formatos de dados
- `docs/_canon/SECURITY_RULES.md` — regras de segurança
- `docs/_canon/OPERATIONS.md §§2,5,6` — boundary e naming
- `docs/hbtrack/modulos/<módulo>/TEST_MATRIX_<MOD>.md` — cenários de teste

### Arquivos que entram DEPOIS (validação pós-geração)

| Fase | Arquivo | O que faz |
|------|---------|-----------|
| `hb artifact <path>` | `.contract_driven/TASK_CATALOG.yaml` (gates) | Valida cada artefato gerado contra gates bloqueantes |
| Pós-geração | `_reports/contract_gates/latest.json` | Atualizado com resultado dos gates (derivado, sem autoridade) |
| Pós-geração | `generated/manifests/*.traceability.yaml` | Manifest de rastreabilidade atualizado (derivado) |

### Arquivos que restringem a implementação

1. `DOMAIN_AXIOMS.json` — enum closure: enum fora daqui = BLOCKED
2. `DOMAIN_RULES_<MOD>.md` + `INVARIANTS_<MOD>.md` — o que as entities podem e não podem fazer
3. `OPERATIONS.md §2` — boundary: o que o módulo pode implementar (ex: `users` não pode tocar auth)
4. `TASK_CATALOG.yaml` — se `ADVERSARIAL_ANALYSIS_GATE` está em FAIL, nenhuma linha de código pode ser gerada
5. `MODULE_REGISTRY.yaml` — status do módulo controla elegibilidade

### Arquivos que orientam decisões do agente

1. `generate_code.prompt.md` — cada fase (GC1–GC6) com regras explícitas
2. `CODE_ARCHITECTURE.md` — como estruturar cada layer
3. `FEATURE_REGISTRY.yaml` — quantos e quais use cases gerar
4. `api_rules.yaml` — como serializar, nomear, formatar erros
5. `STATE_MODEL_<MOD>.md` — como implementar a FSM

### Arquivos que apenas verificam conformidade

- `scripts/hb artifact` — valida SHA-256, roda validador por artefato
- `GATES_REGISTRY.yaml` — critérios de PASS post-geração
- `CI_CONTRACT_GATES.md` — specs dos gates

---

## PARTE 4 — Arquivos Não-Contratuais que Realmente Orientam a Implementação

### 1. `.contract_driven/agent_prompts/generate_code.prompt.md`

**Decisão que influencia:** Toda a geração — fases, o que gerar em cada layer, regras R1–R5, condições de bloqueio.

**Afeta conteúdo ou processo:** **Conteúdo** (o que gerar, como gerar) e **processo** (sequência GC1–GC6, prerequisites).

**Efeito da ausência:** Geração impossível. Não há outro documento que descreva como transformar contratos em código. Sem este worker, o agente não tem instruções sobre como mapear OpenAPI → Django Ninja, JSON Schema → Pydantic, features → use cases.

**Efeito se alterado:** Todo o código gerado mudaria — estrutura de pastas, nomes, layers, quais testes são criados.

---

### 2. `docs/_canon/CODE_ARCHITECTURE.md`

**Decisão que influencia:** Stack técnico, organização em 4 layers, nomes exatos de arquivos, convenções de nomenclatura por tipo de objeto.

**Afeta conteúdo ou processo:** **Conteúdo** — especifica literalmente `backend/apps/<módulo>/domain/entities.py`, `application/use_cases.py`, etc.

**Efeito da ausência:** BLOQUEADO — é prerequisite explícito do `generate_code.prompt.md` (versão ≥ 1.1.0 exigida).

**Efeito se alterado:** Mudaria stack (ex: de Django Ninja para FastAPI), layers, estrutura de pastas, convenções de nomes.

---

### 3. `docs/_canon/FEATURE_REGISTRY.yaml`

**Decisão que influencia:** Quantos e quais use cases existem em `application/use_cases.py`.

**Afeta conteúdo ou processo:** **Conteúdo** — R3 do generate_code.prompt.md é "um use case por feature"; feature não registrada = use case não gerado; feature com status `implemented` já existente pode evitar regeação.

**Efeito da ausência:** BLOQUEADO — `BLOCKED_FEATURE_UNREGISTERED` se feature não existe.

**Efeito se alterado:** Adicionar feature → novo use case; remover feature → use case some; mudar endpoints de feature → endpoints da interface mudam.

---

### 4. `docs/hbtrack/modulos/<módulo>/DOMAIN_RULES_<MOD>.md`

**Decisão que influencia:** Conteúdo de `domain/rules.py` — quais regras de negócio são implementadas.

**Afeta conteúdo ou processo:** **Conteúdo direto** — este arquivo é a fonte das regras que viram código em `rules.py`.

**Efeito da ausência:** BLOQUEADO — prerequisite obrigatório (ausência = `BLOCKED_REQUIRED_ARTIFACT_MISSING`).

**Efeito se alterado:** Regra adicionada → nova validação em `rules.py`; regra removida → validação some; regra alterada → lógica de domínio muda.

---

### 5. `docs/hbtrack/modulos/<módulo>/INVARIANTS_<MOD>.md`

**Decisão que influencia:** Métodos de validação das entities em `domain/entities.py`.

**Afeta conteúdo ou processo:** **Conteúdo** — invariantes definem o que `entity.validate()` verifica.

**Efeito da ausência:** BLOQUEADO — prerequisite obrigatório.

**Efeito se alterado:** Invariante nova → nova validação na entity; invariante removida → validação some.

---

### 6. `docs/hbtrack/modulos/<módulo>/STATE_MODEL_<MOD>.md`

**Decisão que influencia:** Se `domain/state_machine.py` é gerado e com quais estados e transições.

**Afeta conteúdo ou processo:** **Conteúdo** — gera um arquivo inteiro que não existiria sem este documento.

**Efeito da ausência:** `domain/state_machine.py` não é criado; endpoints de transição de estado não são implementados.

**Efeito se alterado:** Estado ou transição nova → novo código de FSM; transição removida → endpoint de transição some.

---

### 7. `.contract_driven/DOMAIN_AXIOMS.json`

**Decisão que influencia:** Valores válidos de enums em entities, schemas e models.

**Afeta conteúdo ou processo:** **Conteúdo** — enum closure: todo enum no código deve ser subconjunto dos valores aqui definidos.

**Efeito da ausência:** Enum closure não pode ser verificado; risco de enum drift entre código e contratos.

**Efeito se alterado:** Valor adicionado → novo enum value permitido; valor removido → código com esse valor bloqueado; valor renomeado → refactor em todos os layers.

---

### 8. `.contract_driven/templates/api/api_rules.yaml`

**Decisão que influencia:** Formato de serialização (camelCase vs snake_case), formato de errors (Problem+JSON), trailing slash, convenções de paths.

**Afeta conteúdo ou processo:** **Conteúdo** — `schemas.py` usa camelCase porque api_rules manda; `api.py` usa Problem+JSON porque api_rules manda.

**Efeito da ausência:** Sem SSOT de convenções HTTP, o agente aplicaria convenções ad hoc; inconsistência entre módulos.

**Efeito se alterado:** Convenção de naming mudada → todos os response schemas mudam; formato de error mudado → todo error handling muda.

---

### 9. `docs/_canon/OPERATIONS.md §2 (Module Boundary Rules)`

**Decisão que influencia:** O que o módulo pode e não pode implementar; ex: `users` não pode tocar auth (pertence a `identity_access`).

**Afeta conteúdo ou processo:** **Conteúdo** — impede implementação de comportamento fora do escopo do módulo.

**Efeito da ausência:** Risco de scope overflow (módulo implementando comportamento de outro módulo).

**Efeito se alterado:** Boundary ampliado → módulo pode implementar mais; boundary restrito → uso case fora do escopo é bloqueado.

---

### 10. `docs/_canon/decisions/ADR-031-backend-framework.md` e `ADR-026`

**Decisão que influencia:** Confirma o stack tecnológico; prerequisite hard do generate_code.

**Afeta conteúdo ou processo:** **Processo** — ausência bloqueia execução (`BLOCKED_REQUIRED_ARTIFACT_MISSING`).

**Efeito da ausência:** BLOQUEADO — nenhuma geração ocorre.

**Efeito se alterado:** Se ADR-031 fosse alterado para outro framework, todo o código gerado usaria o novo framework.

---

### 11. `docs/_canon/MODULE_REGISTRY.yaml` (via `scripts/hb`)

**Decisão que influencia:** Se a geração pode ocorrer para o módulo.

**Afeta conteúdo ou processo:** **Processo** — status `implementation_ready` é gate de elegibilidade; status `scaffold` ou `draft_contract` bloqueia.

**Efeito da ausência:** CLI não consegue validar elegibilidade; geração seria não-governada.

**Efeito se alterado:** Status rebaixado → módulo não pode mais ser implementado; status promovido → módulo torna-se elegível.

---

### 12. `_reports/adversarial/<módulo>/ALL.adversarial.json`

**Decisão que influencia:** Pré-condição hard para generate_code.

**Afeta conteúdo ou processo:** **Processo** — sem relatório PASS, CLI bloqueia antes de qualquer geração.

**Efeito da ausência:** BLOQUEADO — CLI retorna erro.

**Efeito se alterado (para FAIL):** Bloqueio imediato; nenhuma geração ocorre.

---

## PARTE 5 — Hierarquia Real de Influência

| Camada | Artefatos principais | Tipo de autoridade | O que controla | Impacto na implementação do backend |
|--------|----------------------|--------------------|----------------|-------------------------------------|
| **1 — Invariantes de máquina** | `.contract_driven/DOMAIN_AXIOMS.json` | Normativa máxima — nunca sobrescrita | Valores válidos de enums; fechamento de vocabulário controlado | Crítico — enum fora daqui = bloqueio imediato |
| **2 — Regras operacionais** | `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Normativa vinculante | Hierarquia de precedência, anti-patterns proibidos, regras de drift, naming geral | Alto — define o espaço de legalidade de toda implementação |
| **2a — Convenções HTTP** | `.contract_driven/templates/api/api_rules.yaml` | Normativa vinculante (sub-camada de §2) | camelCase, kebab-case, Problem+JSON, formatos de ID/data | Alto — determina a forma de todo output da interface layer |
| **3 — Layout canônico** | `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | Normativa estrutural | Onde cada artefato mora, nomes de paths e arquivos | Médio — determina paths, não conteúdo de código |
| **4 — Contratos técnicos** | `contracts/openapi/paths/<módulo>.yaml`, `contracts/schemas/<módulo>/`, `contracts/asyncapi/`, `contracts/workflows/` | Normativa técnica soberana | Endpoints, request/response shapes, event payloads, domain shapes | Crítico — sem contrato, nenhum endpoint é implementado |
| **4a — Domínio esportivo** | `docs/_canon/HANDBALL_RULES_DOMAIN.md` | Normativa de domínio (quando sport trigger ativo) | Regras IHF aplicadas ao domínio | Médio — influencia regras de domínio em módulos esportivos |
| **5 — Convenções globais** | `docs/_canon/DATA_CONVENTIONS.md`, `docs/_canon/SECURITY_RULES.md`, `docs/_canon/OPERATIONS.md §§2,5,6` | Normativa global transversal | Formatos de dados, segurança, boundary de módulos, naming no código | Alto — aplica-se a todos os módulos sem exceção |
| **6–11 — Documentação normativa de módulo** | `DOMAIN_RULES_<MOD>.md`, `SPORT_SCIENCE_RULES_<MOD>.md`, `INVARIANTS_<MOD>.md`, `STATE_MODEL_<MOD>.md`, `PERMISSIONS_<MOD>.md`, `ERRORS_<MOD>.md` | Normativa de módulo | Regras de negócio, invariantes, FSM, RBAC, error codes do módulo | Alto — conteúdo diretamente transcrito para `domain/rules.py`, entities, state_machine |
| **Worker layer** | `.contract_driven/agent_prompts/generate_code.prompt.md` | Instrução de implementação | Como transformar contratos + docs normativas em código; fases GC1–GC6; regras R1–R5 | Crítico — ausência = geração impossível |
| **Arquitetura** | `docs/_canon/CODE_ARCHITECTURE.md` | Instrução de implementação | Stack, layers, estrutura de pastas, nomenclatura de código | Crítico — prerequisite obrigatório; define o framework |
| **Registry de features** | `docs/_canon/FEATURE_REGISTRY.yaml` | Instrução de implementação | Quais use cases existem | Crítico — R3: um use case por feature |
| **Orquestração** | `docs/_canon/AGENT_INSTRUCTIONS.md`, `.contract_driven/BOOT_PROFILES.yaml`, `.contract_driven/TASK_CATALOG.yaml`, `scripts/hb`, `agent_prompts/pre_contract_orchestrator.prompt.md` | Execução/orquestração | Sequência, routing, eligibility checks, session management | Alto — controla se e como a execução ocorre |
| **Gates** | `docs/_canon/gates/GATES_REGISTRY.yaml`, `docs/_canon/CI_CONTRACT_GATES.md`, `_reports/adversarial/<módulo>/ALL.adversarial.json` | Governança/aprovação | Critérios de PASS/FAIL; bloqueios pré e pós-geração | Alto — controla aprovação, não conteúdo |
| **Decisões arquiteturais** | `docs/_canon/decisions/ADR-031`, `ADR-026`, outros ADRs | Contexto + prerequisite | Framework, autenticação, logging, estratégias | Alto (ADR-031/026 = prerequisite); Médio/Baixo (outros = contexto) |
| **Estado de sessão** | `SESSION_HANDOFF.md`, `_reports/session_start.json` | Estado/handoff | Contexto operacional da sessão atual | Médio — informa contexto, pode evitar retrabalho |
| **Derivados** | `generated/resolved_policy/`, `generated/manifests/`, `_reports/contract_gates/latest.json`, `_reports/evidence/module_readiness_scorecard.json` | Observabilidade — sem autoridade | Snapshots e evidências derivadas | Nulo — nunca sobrescrevem fontes soberanas |

---

## PARTE 6 — Teste Contrafactual

| Grupo removido | O backend ainda poderia ser implementado? | O conteúdo mudaria? | O processo mudaria? | A aprovação mudaria? | Severidade da remoção |
|----------------|-------------------------------------------|---------------------|---------------------|----------------------|-----------------------|
| **Contratos finais** (`contracts/openapi/paths/`, `contracts/schemas/`) | NÃO — `BLOCKED_REQUIRED_ARTIFACT_MISSING` imediato | N/A — geração não ocorre | N/A | N/A | **Catastrófica** — é o SSOT do quê implementar |
| **`.contract_driven/**`** (tudo exceto agent_prompts) | Parcialmente — sem regras vinculantes, routing e boot profiles, o agente agiria sem governança; geração ad hoc e não-conformante | SIM — sem api_rules, naming, DOMAIN_AXIOMS, o código seria inconsistente | SIM — sem BOOT_PROFILES, TASK_CATALOG, a orquestração colapsa | SIM — sem gates e CONTRACT_SYSTEM_RULES, aprovação vira informal | **Catastrófica** |
| **`.contract_driven/agent_prompts/generate_code.prompt.md`** | NÃO — sem worker, o agente não tem instrução de como gerar | N/A | N/A | N/A | **Catastrófica** — é o único driver de geração |
| **`docs/_canon/**`** | Parcialmente — sem CODE_ARCHITECTURE.md (prerequisite), geração bloqueada; sem FEATURE_REGISTRY, nenhum use case; sem SECURITY_RULES/DATA_CONVENTIONS, código inconsistente | SIM massivamente — stack, layers, use cases, formatos todos perderiam definição canônica | SIM — MODULE_REGISTRY, CONTRACT_PIPELINE, AGENT_INSTRUCTIONS desaparecem | SIM — GATES_REGISTRY, CI_CONTRACT_GATES desaparecem | **Catastrófica** |
| **Docs canônicas de módulo** (`DOMAIN_RULES_<MOD>.md`, `INVARIANTS_<MOD>.md`) | NÃO — `BLOCKED_REQUIRED_ARTIFACT_MISSING` | N/A | N/A | N/A | **Catastrófica** — prerequisites obrigatórios |
| **Worker prompts** (todos os demais, ex: `adversarial_analysis.prompt.md`) | NÃO — sem adversarial analysis sendo executada, relatório PASS não existe; `scripts/hb` bloqueia generate_code | N/A | SIM — o fluxo de fases predecessoras (adversarial → generate_code) colapsa | SIM | **Alta** — quebra a sequência de prerequisite gates |
| **`docs/_canon/FEATURE_REGISTRY.yaml`** | NÃO — `BLOCKED_FEATURE_UNREGISTERED` em qualquer feature | N/A | N/A | N/A | **Catastrófica** — R3 do generate_code depende disto |
| **Handoff/session state** (`SESSION_HANDOFF.md`, `_reports/session_start.json`) | SIM — geração tecnicamente pode ocorrer sem contexto de sessão | PARCIAL — sem handoff, risco de retrabalho ou falta de contexto de módulos anteriores | PARCIAL — sem session_start.json, boot profile validation pode falhar | NÃO | **Média** — causa ineficiência e risco de inconsistência, não bloqueio hard em todos os casos |
| **Gates** (`GATES_REGISTRY.yaml`, `CI_CONTRACT_GATES.md`) | SIM — código seria gerado | NÃO | NÃO | SIM — sem critérios de gate, aprovação vira informal | **Média** — o código é gerado mas sem validação de conformidade |
| **Scorecards/readiness** (`_reports/evidence/module_readiness_scorecard.json`, `READINESS_DASHBOARD.md`) | SIM — são derivados sem autoridade normativa | NÃO | NÃO | NÃO — o que bloqueia é `MODULE_REGISTRY.yaml` (status), não o scorecard em si | **Baixa** — perda de observabilidade, não de governança |
| **`_reports/adversarial/<módulo>/ALL.adversarial.json`** | NÃO — CLI bloqueia (`generate_code` requer ADVERSARIAL_ANALYSIS_GATE PASS) | N/A | N/A | N/A | **Catastrófica** — prerequisite hard no CLI |

---

## PARTE 7 — Fato vs Inferência

| Afirmação | Classificação | Evidência | Confiança |
|-----------|---------------|-----------|-----------|
| O backend é gerado por `generate_code.prompt.md` em 6 fases (GC1–GC6) | fato confirmado | Leitura direta de `.contract_driven/agent_prompts/generate_code.prompt.md` + SESSION_HANDOFF.md confirmando execução de fases GC1–GC6 no módulo video | alta |
| `CODE_ARCHITECTURE.md` versão ≥ 1.1.0 é prerequisite obrigatório do generate_code | fato confirmado | Leitura direta de `generate_code.prompt.md` ("Prerequisites: 2. CODE_ARCHITECTURE.md exists (≥ v1.1.0)") | alta |
| FEATURE_REGISTRY.yaml determina quantos use cases são gerados (R3) | fato confirmado | Leitura direta de `generate_code.prompt.md` R3 + TASK_CATALOG.yaml input requirements | alta |
| `DOMAIN_RULES_<MOD>.md` e `INVARIANTS_<MOD>.md` são prerequisites obrigatórios | fato confirmado | OPERATIONS.md §4 "Mandatory: always" + TASK_CATALOG.yaml blocking condition | alta |
| `scripts/hb verify` verifica adversarial report com `overall_status: PASS` antes de permitir generate_code | fato confirmado | Leitura direta de `scripts/hb` linhas 136–203 (eligibility check) | alta |
| `STATE_MODEL_<MOD>.md` gera `domain/state_machine.py` quando presente | fato confirmado | `generate_code.prompt.md` fase GC2 descreve geração condicional de state_machine.py | alta |
| `api_rules.yaml` determina camelCase em responses de API | fato confirmado | `generate_code.prompt.md` GC5 + OPERATIONS.md §6 + leitura direta de api_rules.yaml | alta |
| `DOMAIN_AXIOMS.json` aplica enum closure no código gerado | fato confirmado | OPERATIONS.md §5.1 "Enum closure: reject any enum value not in DOMAIN_AXIOMS.json" + CONTRACT_SYSTEM_RULES.md | alta |
| ADR-031 e ADR-026 são prerequisites hard do generate_code | fato confirmado | `generate_code.prompt.md` Prerequisites §1 | alta |
| SESSION_HANDOFF.md pode influenciar o que é gerado (evitar retrabalho) | inferência plausível | AGENT_INSTRUCTIONS.md §0 instrui leitura obrigatória; handoff lista o que foi feito; agente razoavelmente evitaria regenerar módulo já concluído | média |
| `generated/resolved_policy/*.resolved.yaml` é lido durante GC1 | inferência plausível | `generate_code.prompt.md` descreve montagem de contexto com "domain rules, invariants, state model, permissions, features"; resolved_policy pode ser incluído para contexto de tipos canônicos | média |
| `docs/_canon/GLOBAL_INVARIANTS.md` afeta entities de múltiplos módulos | inferência plausível | OPERATIONS.md referencia invariantes globais como cross-module; generate_code.prompt.md diz "mount context" mas lista explícita não menciona GLOBAL_INVARIANTS.md | média |
| `waivers.json` pode desbloquear generate_code com gate waivered | inferência plausível | `scripts/hb verify` verifica gates bloqueantes; TASK_CATALOG.yaml menciona waivers; lógica inferida de que waiver desbloqueia gate sem alterar conteúdo | média |
| `UI_CONTRACT_<MOD>.md` não é usado na geração backend | fato confirmado | TASK_CATALOG.yaml `generate_frontend` é separado e FROZEN; `generate_code.prompt.md` não menciona UI_CONTRACT; scope de geração explicitamente é domain/application/infrastructure/interface (backend) | alta |
| `_reports/contract_gates/latest.json` tem autoridade normativa | não confirmado | Análise mostra que é derivado; OPERATIONS.md §1 "generated/ e _reports/ são sempre derivados. Nunca sobrescrevem fontes soberanas." | alta (confirmado como nulo) |
| `CONTRACT_SYSTEM_LAYOUT.md` influencia o conteúdo do código gerado | não confirmado | O próprio arquivo em §15 diz: "NOT used to invent business rules, states, permissions, event semantics" — apenas determina paths | alta (confirmado como estrutural apenas) |

---

## PARTE 8 — Veredito Final

### Arquivos que realmente moldam a implementação do backend

**Moldam o conteúdo (o que é gerado):**

1. `contracts/openapi/paths/<módulo>.yaml` — endpoints e shapes
2. `contracts/schemas/<módulo>/*.schema.json` — models e Pydantic schemas
3. `.contract_driven/agent_prompts/generate_code.prompt.md` — driver da geração completa
4. `docs/_canon/CODE_ARCHITECTURE.md` — stack e arquitetura
5. `docs/_canon/FEATURE_REGISTRY.yaml` — use cases
6. `docs/hbtrack/modulos/<módulo>/DOMAIN_RULES_<MOD>.md` — `domain/rules.py`
7. `docs/hbtrack/modulos/<módulo>/INVARIANTS_<MOD>.md` — validações em entities
8. `docs/hbtrack/modulos/<módulo>/STATE_MODEL_<MOD>.md` — `domain/state_machine.py`
9. `docs/hbtrack/modulos/<módulo>/PERMISSIONS_<MOD>.md` — RBAC na interface layer
10. `.contract_driven/DOMAIN_AXIOMS.json` — enums fechados
11. `.contract_driven/templates/api/api_rules.yaml` — camelCase, Problem+JSON, formatos
12. `docs/_canon/DATA_CONVENTIONS.md` — UUID v4, date formats, naming
13. `docs/_canon/SECURITY_RULES.md` — auth, segurança na interface layer
14. `docs/_canon/OPERATIONS.md §§2,5,6` — boundary de módulo, naming no código

**Moldam o processo (quando e como a geração ocorre):**

15. `docs/_canon/AGENT_INSTRUCTIONS.md` — protocolo master de boot
16. `.contract_driven/BOOT_PROFILES.yaml` — sequência de carregamento
17. `.contract_driven/TASK_CATALOG.yaml` — routing e gates bloqueantes
18. `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` — Fase 0
19. `scripts/hb` (CLI) — eligibility checks determinísticos
20. `docs/_canon/MODULE_REGISTRY.yaml` — status de elegibilidade do módulo
21. `_reports/adversarial/<módulo>/ALL.adversarial.json` — gate prerequisite hard
22. `docs/_canon/decisions/ADR-031`, `ADR-026` — prerequisites de framework

---

### Arquivos que cercam o fluxo sem mudar o código gerado

- `_reports/contract_gates/latest.json` — observabilidade (derivado)
- `_reports/evidence/module_readiness_scorecard.json` — observabilidade (derivado)
- `_reports/READINESS_DASHBOARD.md` — observabilidade (derivado)
- `generated/resolved_policy/*.resolved.yaml` — derivado, sem autoridade
- `generated/manifests/*.traceability.yaml` — derivado, sem autoridade
- `.contract_driven/CONTRACT_FILESYSTEM_REFERENCE.md` — referência informativa
- `.contract_driven/PLACEHOLDER_REGISTRY.md` — referência de scaffolds
- `docs/_canon/CONTRACT_PIPELINE.md` — descrição processual (contexto)
- `docs/_canon/SYSTEM_SCOPE.md` — contexto de escopo (não normativo para código)
- `docs/hbtrack/modulos/<módulo>/UI_CONTRACT_<MOD>.md` — apenas para frontend generator

---

### O backend é governado só por contratos ou por contratos + camada de orientação?

**Por contratos + camada de orientação.**

Os contratos são o SSOT do *quê* é implementado (endpoints, shapes, events). Mas a camada de orientação é igualmente soberana e determina:
- *como* é implementado (stack, layers, naming, formatos, error shapes)
- *o que mais* é implementado além do contrato puro (regras de domínio, invariantes, FSM, RBAC)
- *em que ordem* é implementado (fases GC1–GC6, sequência de prerequisites)
- *quando pode ser aceito* (gates, adversarial PASS, module status)

Sem a camada de orientação, os contratos seriam um conjunto de especificações sem mecanismo de tradução para código concreto.

---

### Menor lista de arquivos realmente normativos para a implementação do backend

Para gerar código backend conformante para um módulo qualquer, os seguintes arquivos são irredutíveis — remover qualquer um bloqueia ou deforma a implementação:

```
CONTRATOS (o quê)
├── contracts/openapi/paths/<módulo>.yaml
├── contracts/openapi/openapi.yaml
└── contracts/schemas/<módulo>/*.schema.json

WORKER (como gerar)
└── .contract_driven/agent_prompts/generate_code.prompt.md

ARQUITETURA E FEATURES (estrutura e use cases)
├── docs/_canon/CODE_ARCHITECTURE.md
└── docs/_canon/FEATURE_REGISTRY.yaml

DOMÍNIO DO MÓDULO (conteúdo de domain layer)
├── docs/hbtrack/modulos/<módulo>/DOMAIN_RULES_<MOD>.md
└── docs/hbtrack/modulos/<módulo>/INVARIANTS_<MOD>.md

VOCABULÁRIO E CONVENÇÕES (naming e formatos)
├── .contract_driven/DOMAIN_AXIOMS.json
├── .contract_driven/templates/api/api_rules.yaml
└── docs/_canon/DATA_CONVENTIONS.md

PREREQUISITE GATES (condições de elegibilidade)
├── docs/_canon/MODULE_REGISTRY.yaml          (status do módulo)
├── _reports/adversarial/<módulo>/ALL.adversarial.json  (PASS obrigatório)
├── docs/_canon/decisions/ADR-031             (framework decision)
└── docs/_canon/decisions/ADR-026             (architecture decision)
```

**Total: 15 arquivos mínimos obrigatórios** (mais arquivos condicionais conforme o módulo: STATE_MODEL, PERMISSIONS, ERRORS, SPORT_SCIENCE, HANDBALL_RULES_DOMAIN).

---

*Análise gerada por inspeção direta de `.contract_driven/**`, `docs/_canon/**`, `scripts/hb`, `SESSION_HANDOFF.md`, `_reports/**` e `generated/**`. Nenhuma inferência teórica sem evidência de arquivo real no repositório.*
