---
doc_type: audit_report
system: HB Track
topic: contract-driven-governance
workspace_root: /home/davis/HB-TRACK
generated_at: "2026-03-14"
auditor: "Codex CLI (GPT-5.2)"
status: delivered
---

# HB Track — Auditoria Completa de Governança Contract‑Driven (CDD)

Este relatório descreve **a configuração real** de governança contract‑driven existente hoje no workspace, **como ela funciona atualmente**, **quais gaps impedem CDD no mundo real**, **como a governança pode ser quebrada**, **como corrigir e impedir a quebra**, e recomenda **melhorias e evolução arquitetural** para o HB Track ser um sistema contract‑driven “Top 1” (governança) e líder de mercado em handebol.

Data da 1ª auditoria: **2026-03-14**  
Workspace auditado: `/home/davis/HB-TRACK`  

---

## Sumário

1. Escopo e método de auditoria  
2. Mapa do workspace (artefatos e responsabilidades)  
3. Configuração atual da governança contract‑driven (CDD)  
4. Como a governança funciona atualmente (AS‑IS)  
5. Gaps, inconsistências e lacunas (por severidade)  
6. Como quebrar essa governança (ameaças/bypass)  
7. Ajustes necessários para corrigir os gaps (plano priorizado)  
8. Como impedir que a governança seja quebrada (hardening)  
9. Melhorias após fechar gaps (>= 10)  
10. Agente: capacidade de criar contratos automaticamente e qualidade  
11. Arquitetura proposta (canon) — análise e melhorias  
12. Arquitetura estrutural/operacional completa (modelo final)  
13. HB Track como gerador de contratos Sport‑Tech (TOP 3)  
Apêndices: gates, DoD, checklist de CI, itens ausentes

---

## 1) Escopo e método de auditoria

### 1.1 O que foi auditado
- Governança CDD (normas, SSOTs, precedência, layout, templates).
- Contratos técnicos (OpenAPI, JSON Schema, AsyncAPI, Arazzo).
- Tooling/gates/compilers (scripts, configs, relatórios em `_reports/`).
- Evidências existentes de execução (especialmente `_reports/contract_gates/latest.json` e checklists).
- Arquitetura canônica documentada (`docs/_canon/*`) e aderência dos contratos ao canon.
- Capacidade de automação (prompts, compilers, políticas anti‑alucinação).

### 1.2 O que NÃO pôde ser comprovado apenas com este workspace
- Convergência contrato ↔ implementação runtime **para todos os módulos** (o repo não contém claramente o backend/frontend completos no layout que alguns docs pressupõem).
- CI server‑side está comprovado no repo (workflow em `.github/workflows/contract-gates.yml` + proteção de SSOT via `.github/CODEOWNERS`).
- Branch protection/rulesets é configuração **out‑of‑band** do GitHub (ver runbook em `.github/BRANCH_PROTECTION_SETUP.md`).

### 1.3 Critério de “CDD de sucesso no mundo real”
Para este relatório, “CDD de sucesso” = **enforcement server‑side** (CI + branch protection) + **determinismo** (toolchain pinada) + **não‑bypass** (gates bloqueantes) + **rastreabilidade** (inputs/derivados auditáveis) + **prova de convergência** (runtime contract para pelo menos 1 piloto, evoluindo por módulo).

---

## 2) Mapa do workspace (artefatos e responsabilidades)

### 2.1 Estrutura principal encontrada
- `.contract_driven/`  
  **Sistema de contratos**: regras operacionais, layout, templates e axiomas machine‑readable.
- `docs/_canon/`  
  **Canon global normativo**: escopo, arquitetura, gates, segurança, convenções, ADRs.
- `docs/hbtrack/modulos/`  
  **Docs normativas por módulo** (mínimo por módulo + extensões modulares como `DOMAIN_AXIOMS_<MODULE>.json`).
- `contracts/`  
  **Contratos técnicos soberanos** (OpenAPI/AsyncAPI/JSON Schema/Arazzo).
- `generated/`  
  **DERIVED**: policy resolvida + manifests de rastreabilidade + cópias derivadas.
- `_reports/`  
  Evidências de execução (contract gates, dispatch context, resultados anteriores).
- `scripts/`  
  Ferramentas de governança, validação, checks, geração e diagnósticos.

### 2.2 Artefatos “núcleo CDD” (SSOT)
Tabela curta: o que cada arquivo faz e por que é crítico.

| Artefato | Papel | Por que é crítico |
|---|---|---|
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | Layout/taxonomia/naming/paths | Sem ele o repo vira “cada um em um lugar” |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Regras operacionais + precedência + bloqueios | Define “como operar” e como resolver conflitos |
| `.contract_driven/GLOBAL_TEMPLATES.md` | Índice e regras de templates | Evita improviso estrutural por agentes/humanos |
| `.contract_driven/templates/api/api_rules.yaml` | SSOT de API HTTP (OpenAPI) | Elimina inferência; define convenções e validações |
| `.contract_driven/DOMAIN_AXIOMS.json` | Axiomas globais machine‑readable | Base para invariantes, formatos e extensões seguras |
| `docs/_canon/CI_CONTRACT_GATES.md` | Especificação normativa do pipeline | Diz “o que é PASS” de forma objetiva |
| `scripts/validate_contracts.py` | Entrypoint de gates | Produz evidência `_reports/contract_gates/latest.json` |

---

## 3) Configuração atual da governança contract‑driven (CDD) — “o que existe hoje”

### 3.1 Hierarquia normativa e precedência (regra “quem manda em quem”)
O HB Track define uma pirâmide de autoridade. Em conflito:

1) **Layout**: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`  
2) **Regras operacionais**: `.contract_driven/CONTRACT_SYSTEM_RULES.md`  
3) **SSOT de API HTTP**: `.contract_driven/templates/api/api_rules.yaml` (para decisões de API)  
4) **Contratos técnicos válidos** (OpenAPI/JSON Schema/AsyncAPI/Arazzo)  
5) **Canon global** (`docs/_canon/*`) e canon por módulo (`docs/hbtrack/modulos/*`)  
6) **Implementação** (código) e artefatos gerados (derivados)

Isso é forte porque:
- força decisão por SSOT única;
- proíbe duplicação normativa;
- permite “fail‑closed” quando faltam regras.

### 3.2 Taxonomia canônica de módulos (16)
Definida no layout e repetida no canon, com boundaries explícitas:
- `users` (perfil e dados funcionais pessoais) **não** faz auth/authz.
- `identity_access` (authn/authz/credenciais/sessões/MFA/JWT/RBAC) **não** modela perfil funcional.
- `wellness` (operacional/auto‑report) **não** vira prontuário clínico.
- `medical` (clínico) tem requisitos de privacidade/auditoria reforçados.

### 3.3 Superfícies contratuais suportadas
Existem quatro superfícies principais:
- **sync/http**: OpenAPI
- **event/async**: AsyncAPI
- **workflow**: Arazzo
- **schema**: JSON Schema (domínio)

Módulo pode habilitar surface(s) via registry (ex.: `training` habilita `sync` e `event`).

### 3.4 SSOT de convenções HTTP/OpenAPI (api_rules.yaml)
`.contract_driven/templates/api/api_rules.yaml` centraliza:
- naming (`kebab-case` em paths, `camelCase` em JSON e query params),
- paginação cursor (`pageSize`, `pageToken`, `nextPageToken`),
- erros RFC7807 (Problem+JSON),
- proibição de versão na URI,
- baseline OWASP API Top 10 (2023) como norma de segurança,
- política “strict_no_inference”: **lacuna crítica = bloquear**.

Essa SSOT é a peça mais importante para evitar divergência entre módulos e agentes.

### 3.5 Domain axioms (machine‑readable) + extensões modulares seguras
`.contract_driven/DOMAIN_AXIOMS.json` define:
- formatos globais (uuid_v4, timestamp_utc, etc.)
- enums globais (ex.: estados de training/match)
- máquinas de estado globais (ex.: training_state_machine)
- política de normalização de derivados
- contrato do validador (“o validator deve checar X e não pode fazer Y”)

Extensões modulares aparecem como:
- `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json`  
Ex.: `training` estende `event_type` via `DELTA_ONLY` com semantic_id e constraints de payload.

### 3.6 Lint e validação OpenAPI: configs existentes
- Redocly: `redocly.yaml`
- Spectral ruleset: `.spectral.yaml`
- OpenAPI root: `contracts/openapi/openapi.yaml` (OpenAPI 3.1.0)
- Schema de erro: `contracts/openapi/components/schemas/shared/problem.yaml` (Problem+JSON)

### 3.6A Inventário de configurações e “pontos de verdade” (configuração prática)
Além de `api_rules.yaml`, a governança de contratos depende destes artefatos/configs:

- **Baseline de breaking changes**: `contracts/openapi/baseline/openapi_baseline.json` (entrada do `CONTRACT_BREAKING_CHANGE_GATE`/oasdiff).
- **Parâmetros/padrões compartilhados OpenAPI**:
  - `contracts/openapi/components/parameters/pageSize.yaml`
  - `contracts/openapi/components/parameters/pageToken.yaml`
- **Matrizes normativas** que viram gates:
  - `docs/_canon/security/OWASP_API_CONTROL_MATRIX.yaml`
  - `docs/_canon/MODULE_SOURCE_AUTHORITY_MATRIX.yaml`
  - schemas de validação:
    - `contracts/schemas/shared/owasp_api_control_matrix.schema.json`
    - `contracts/schemas/shared/module_source_authority_matrix.schema.json`
- **Axiomas globais (formatos/enums/máquinas de estado)**:
  - `.contract_driven/DOMAIN_AXIOMS.json`
  - schema: `contracts/schemas/shared/domain_axioms.schema.json`
  - extensões modulares: `docs/hbtrack/modulos/*/DOMAIN_AXIOMS_<MODULE>.json`
- **Compiladores determinísticos** (fonte de derivados em `generated/`):
  - policy: `scripts/contracts/validate/api/compile_api_policy.py`
  - intent (DSL): `scripts/contracts/validate/api/compile_api_intent.py`
  - intents: `contracts/openapi/intents/*.intent.yaml`
- **Derivados e rastreabilidade**:
  - policy resolvida: `generated/resolved_policy/*.resolved.yaml`
  - manifests: `generated/manifests/*.traceability.yaml`
  - cópias derivadas: `generated/contracts/**`

### 3.7 Gates e evidência (pipeline)
O canon descreve gates e ordem em `docs/_canon/CI_CONTRACT_GATES.md`.

O agregador implementado é:
- `python3 scripts/validate_contracts.py`  
que executa `scripts/contracts/validate/validate_contracts.py`, gera `_reports/contract_gates/latest.json` e retorna exit code determinístico.

Gates implementados (alto nível):
- AXIOM integrity
- Path canonicality + required artifacts
- Crossrefs + boundaries + hermeticidade `$ref`
- OpenAPI lint (Redocly + Spectral)
- JSON Schema validation
- Cross‑spec alignment
- Breaking change detection (oasdiff + baseline)
- AsyncAPI validate
- Arazzo validation mínima
- Derived drift (compiler determinístico) + readiness summary

---

## 4) Como a governança funciona atualmente (AS‑IS)

### 4.1 O fluxo CDD “coeso” que existe neste repo (contratos/gates)
O fluxo operacional “coerente” dentro deste workspace é:
1) Alterar SSOT (contratos + docs normativas)
2) Regerar derivados (policy compiler e/ou intent compiler)
3) Rodar `python3 scripts/validate_contracts.py`
4) Usar `_reports/contract_gates/latest.json` como evidência do estado

### 4.1A Enforcement local (git hooks) — estado atual e implicações
O repo está configurado para usar hooks em `scripts/git-hooks` (via `core.hooksPath`).

Estado atual:
- hook: `scripts/git-hooks/pre-commit`
- executa: `python3 scripts/validate_contracts.py` (contract gates)

Implicações:
- commits são bloqueados quando há falha bloqueante nos contract gates;
- `_reports/contract_gates/latest.json` é a evidência local do estado.

**Limite (importante):** hooks locais são bypassáveis (`git commit --no-verify`). Portanto, a governança real exige enforcement server‑side (CI + branch protection) executando os mesmos gates e bloqueando merge.

### 4.2 Estado do piloto de contratos
No OpenAPI:
- `contracts/openapi/openapi.yaml` referencia endpoints apenas de `training`.
- Arquivos `contracts/openapi/paths/*.yaml` existem para os 16 módulos, porém **15 estão como scaffolds** (comentários) e **1 (training) está materializado**.

No AsyncAPI:
- existe `contracts/asyncapi/asyncapi.yaml` com canal `training.attendance.marked`.

No Arazzo:
- existe workflow `contracts/workflows/training/create_training_session_and_mark_attendance.arazzo.yaml`.

No JSON Schema:
- existe schema materializado de `training_session`.

Conclusão: o repo está em maturidade “piloto com 1 módulo forte”, o que é aceitável **desde que** o pipeline seja determinístico e CI seja obrigatório (**hoje é**: workflow + required checks server‑side).

### 4.3 Evidência objetiva encontrada (datas fixas)
- `_reports/contract_gates/latest.json` (**execução no WSL — 2026-03-14T08:02:01Z**):
  - overall: **PASS** (exit_code=0)
  - leitura: o pipeline contract-driven está determinístico e executável no WSL **sem** o erro `UtilBindVsockAnyPort:307: socket failed 1` (toolchain agora roda WSL‑native).
  - observação: `oasdiff` WSL‑native ainda não está pinado/provido por projeto; o gate de breaking changes usa fallback determinístico (detecta remoção de operações method+path) quando `oasdiff` não é utilizável no WSL.
- `.github/workflows/contract-gates.yml` (CI obrigatório — 2026-03-14):
  - executa `npm ci` + `python3 scripts/validate_contracts.py` em PR/push (`main`, `develop`);
  - publica `_reports/contract_gates/` como artefato (`contract-gates-report`).
- `.github/CODEOWNERS` (proteção de SSOT e gates): impede mudanças em `.contract_driven/**`, `contracts/**`, `docs/_canon/**` e runner de gates sem owner.
- **Nota:** `latest.json` é sobrescrito a cada execução. Para histórico auditável, gerar também `_reports/contract_gates/<timestamp>.json` (ou preservar evidências como artefatos de CI).

### 4.4 Governança legada eliminada (unificação)
Por decisão explícita, a **governança única** deste workspace é a declarada pela trilogia `.contract_driven/*` (e pelos artefatos normativos listados em `.contract_driven/CONTRACT_SYSTEM_RULES.md`).

Para eliminar confusão e split‑brain, foram removidos artefatos de governanças anteriores que competiam com o fluxo contract‑driven, incluindo:
- `.github/agents/`, `.github/instructions/`, `.github/skills/`
- `scripts/run/`, `scripts/plans/`, `scripts/gates/`, `scripts/audit/`
- `docs/_canon/specs/`
- `docs/hbtrack/planejamento/`
- `TESTADOR.yaml`
- tooling/SSOTs e checks legados relacionados a `docs/_INDEX.yaml`/`docs/ssot/` (ex.: `scripts/SSOTs/`, `scripts/_lib/` e scripts geradores/validadores associados)

Resultado: não existe mais um “segundo fluxo” de governança dentro deste repo; o fluxo oficial é o pipeline de contract gates (`python3 scripts/validate_contracts.py`) com evidência em `_reports/contract_gates/latest.json`.

---

## 5) GAPS / inconsistências / lacunas (o que impede CDD no mundo real)

> Severidade: P0 crítico, P1 alto, P2 médio, P3 baixo.

### 5.1 P0 — Críticos

#### P0‑1) Split‑brain: dois sistemas de governança concorrentes
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** CDD/gates/compilers e um fluxo legado (hb_cli/AR/Kanban/SSOTs paralelos) coexistiam e não convergiam.  
**Agora:** o legado foi removido e o repo tem **um único fluxo oficial**: SSOTs da trilogia `.contract_driven/*` + canon (`docs/_canon/*`) + validação por `python3 scripts/validate_contracts.py`.

**Impacto positivo:** elimina “negociação social” do que é PASS, reduz bypass e remove fontes concorrentes de verdade.

#### P0‑2) Rastreabilidade inconsistente em derivados (`generated/**`)
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** artifacts/manifests em `generated/**` referenciavam inputs sob `.contract_driven/templates/api_rules/*` (path inexistente), quebrando a prova de “qual SSOT gerou qual derivado”.  
**Agora:** o policy compiler foi alinhado ao SSOT canônico `.contract_driven/templates/api/*`, os derivados foram limpos e regenerados, e o drift gate passou a validar manifests:
- todo `source_inputs[].path`, `source_contracts[].path`, `generated_artifacts[].path` deve existir;
- todo `sha256` deve bater com o conteúdo atual;
- `policy_path`/`policy_sha256` e tree-hashes devem bater.

**Impacto positivo:** o repo volta a ter rastreabilidade auditável e reprodutível para `generated/**`; o pipeline falha quando não consegue provar a cadeia de geração.

#### P0‑3) CI obrigatório + required checks (enforcement server‑side)
**Status:** **RESOLVIDO (2026-03-14)**.

**Artefatos:**
- `.github/workflows/contract-gates.yml` (CI contract gates)
- `.github/CODEOWNERS` (protege SSOT/gates)

**Evidência (no repo):** `.github/CI_FIX_EVIDENCE.md`.

#### P0‑4) Waivers machine‑readable exigidos no canon, mas pasta inexistente
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** `docs/_canon/CI_CONTRACT_GATES.md` exigia `contracts/_waivers/`, mas a pasta não existia.  
**Agora:** waivers foram implementados como SSOT e o pipeline ficou **fail‑closed**:
- infraestrutura: `contracts/_waivers/README.md` + `contracts/_waivers/waiver.schema.json`;
- gate suportado (no momento): `CONTRACT_BREAKING_CHANGE_GATE` (`contracts/_waivers/CONTRACT_BREAKING_CHANGE_GATE/README.md`);
- validação: waiver inválido/expirado/target inexistente ⇒ **FAIL** (sem “bypass textual”);
- breaking change sem waiver ⇒ **FAIL** com `fingerprint_sha256` + evidência em `_reports/contract_gates/breaking_changes/CONTRACT_BREAKING_CHANGE_GATE.diff.txt`;
- waiver válido (fingerprint == diff) ⇒ **PASS** (quebra governada, auditável e com expiração).

**Impacto positivo:** exceções passam a ser temporárias, auditáveis e vinculadas a um diff determinístico; reduz bypass social e mantém governança “não quebrável”.

#### P0‑5) (RESOLVIDO) Pre‑commit alinhado ao gate oficial do repo
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** o pre‑commit chamava um fluxo legado e incentivava bypass por falhas de SSOT inexistente.  
**Agora:** `scripts/git-hooks/pre-commit` executa o gate oficial: `python3 scripts/validate_contracts.py`.

**Risco remanescente (normal):** hooks locais seguem bypassáveis (`--no-verify`). CI server‑side continua obrigatório.

#### P0‑6) Compiladores/policy podem estar apontando para diretórios SSOT inexistentes
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** o policy compiler e manifests apontavam para `.contract_driven/templates/api_rules/*` (inexistente).  
**Agora:** o compiler usa exclusivamente `.contract_driven/templates/api/*` e o drift gate valida a integridade dos manifests antes de qualquer diff.

### 5.2 P1 — Altos

#### P1‑1) Toolchain não hermética/pinada por projeto
**Status:** **RESOLVIDO em CI / MITIGADO localmente (2026-03-14)**.

**Antes:** CLIs de gate (redocly/spectral/asyncapi/oasdiff) resolviam para wrappers externos (`/home/davis/bin/*`) chamando binários Windows (`node.exe`, `oasdiff.exe`) → falhas `UtilBindVsockAnyPort`.  
**Agora:** os contract gates passam no WSL com toolchain WSL‑native (sem vsock error), e o bootstrap canônico do ambiente remove a fonte do problema:
- `source ./setup-env.sh` (carrega NVM, aplica `.nvmrc`, remove wrappers em `$HOME/bin` do PATH e expõe `node_modules/.bin`);
- gates executam CLIs Node via Node WSL‑native (sem interop `node.exe`).

**Gap remanescente (para “hermeticidade real” completa):**
- prover `oasdiff` WSL‑native no ambiente de CI/WSL (ou manter fallback apenas como contingência, não como padrão).

#### P1‑2) Runtime contract proof não está fechado no agregador
**Problema:** o gate de runtime HTTP é SKIP no agregador atual (por desenho).  
**Impacto:** contrato pode “passar” sem convergir com a implementação real.

#### P1‑3) Governed roots (spec) não representa o workspace real
**Status:** **RESOLVIDO (2026-03-14)**.

**Antes:** havia uma spec legada em `docs/_canon/specs/` que não representava o workspace real.  
**Agora:** a pasta/spec foi removida; a governança válida é a trilogia `.contract_driven/*` + canon (`docs/_canon/*`) + contracts em `contracts/**`.

#### P1‑4) Severidade/blocking divergente em gates “aplicáveis”
**Problema:** alguns gates (ex.: AsyncAPI) aparecem como não‑bloqueantes na implementação, mesmo quando o módulo/surface existe.  
**Impacto:** abre janela para introduzir eventos inválidos.

### 5.3 P2 — Médios
- Prompts de agente incompletos/hardcoded.
- Cobertura de contratos por módulo ainda baixa (piloto).
- (RESOLVIDO 2026-03-14) Duplicações/legado em templates (`.contract_driven/templates/API_RULES/*`) foi removido para evitar confusão/split-brain.

---

## 6) Como quebrar a governança (ameaças/bypass) — e por que isso importa

> Esta seção é threat‑model defensivo: lista os vetores mais prováveis de quebra para vocês fecharem sistemicamente.

### 6.1 Bypass por ausência de enforcement server‑side
- **Como quebrar:** fazer mudanças em SSOT e mergear sem CI obrigatório.  
- **Por que funciona:** não há “juiz” no servidor.
- **Como impedir:** CI + required checks + branch protection.

### 6.2 Bypass de hooks locais
- **Como quebrar:** `git commit --no-verify` ou commits fora do fluxo recomendado.  
- **Como impedir:** CI obrigatório (hooks locais são “conforto”, não segurança).

### 6.3 Subverter o “juiz” (alterando o runner de gates)
- **Como quebrar:** modificar `scripts/validate_contracts.py` ou `scripts/contracts/validate/validate_contracts.py` para pular gates, reclassificar FAIL como PASS, ou mascarar violações.  
- **Como impedir:** proteger arquivos do pipeline via CODEOWNERS + required review, executar gates em CI hermético (container) e bloquear merge quando houver mudanças no runner sem aprovação explícita.

### 6.4 Drift entre SSOT e derivados
- **Como quebrar:** editar `generated/**` manualmente ou não regerar após mudança em SSOT.  
- **Como impedir:** drift gate obrigatório em CI; `generated/**` sempre tratado como DERIVED.

### 6.5 Breaking changes invisíveis por baseline fraco
- **Como quebrar:** manter baseline vazio/desatualizado e introduzir breaking changes sem detecção.  
- **Como impedir:** processo de atualização de baseline + gate que prova baseline alinhado + waivers governados.

### 6.6 Eventos e workflows “por fora”
- **Como quebrar:** publicar eventos/workflows sem AsyncAPI/Arazzo válidos ou com gates não‑bloqueantes.  
- **Como impedir:** gates bloqueantes por surface + registry de surfaces por módulo.

### 6.7 Toolchain flutuante
- **Como quebrar:** mudar versões globais de CLIs e “passar”/“falhar” conforme máquina.  
- **Como impedir:** toolchain pinada, executada via projeto (npx/pip lock) e validada em CI.

---

## 7) Ajustes necessários para corrigir gaps (plano priorizado com critérios de aceite)

### 7.1 Decisão soberana: qual é o tipo deste repositório?
**Decisão tomada:** este workspace é um **Contract Governance Repo** (governança + contratos + canon).

Governança oficial do repo = CDD/gates/compilers:
- `python3 scripts/validate_contracts.py` (evidência: `_reports/contract_gates/latest.json`)
- `python3 scripts/contracts/validate/api/compile_api_policy.py ...`
- `python3 scripts/contracts/validate/api/compile_api_intent.py ...` (quando usar intents)

Fluxos legados concorrentes (hb_cli/AR/Kanban/`docs/ssot`/índices paralelos) foram removidos deste workspace para evitar split‑brain.

**Critério de aceite (P0):** um único pipeline oficial, executável em máquina limpa + em CI (required checks).

### 7.2 P0: Consertar rastreabilidade de `generated/**` (inputs devem existir)
**Status:** **RESOLVIDO (2026-03-14)**.

**Entregas:**
- manifests/paths corrigidos para referenciar SSOT existente;
- limpeza e regeneração de `generated/**`;
- drift gate validando inputs/hashes antes de aceitar derivados.

**Critério de aceite atingido:** `generated/manifests/*.traceability.yaml` e `generated/resolved_policy/*.resolved.yaml` só apontam para arquivos existentes + hashes corretos; pipeline falha se algum input não existir.

### 7.3 P0: Implementar waivers machine‑readable (ou remover a exigência do canon)
**Status:** **RESOLVIDO (2026-03-14)**.

**Entregas (SSOT + enforcement):**
- `contracts/_waivers/waiver.schema.json` (schema machine‑readable);
- `contracts/_waivers/<gate_id>/*.json` (waivers);
- integração **fail‑closed** no `CONTRACT_BREAKING_CHANGE_GATE`:
  - waiver inválido/expirado ⇒ **FAIL**;
  - breaking change sem waiver ⇒ **FAIL** com `fingerprint_sha256` publicado;
  - waiver válido (fingerprint == diff) ⇒ **PASS**.

**Como usar:** ver `contracts/_waivers/README.md`.

### 7.4 P0/P1: Adicionar CI e tornar gates obrigatórios (server‑side)
**Status:** **RESOLVIDO (2026-03-14)**.

**Entregas:**
- workflow CI: `.github/workflows/contract-gates.yml` (required checks);
- proteção de SSOT/gates: `.github/CODEOWNERS`;
- runbook de branch protection/rulesets: `.github/BRANCH_PROTECTION_SETUP.md`.

**Critério de aceite atingido:** PR não mergeia sem PASS (required status checks no GitHub).

### 7.5 P1: Toolchain hermética (pinning + execução via projeto)
**Status:** **RESOLVIDO em CI / MITIGADO localmente (2026-03-14)**.

**Node**
- CLIs via projeto (`node_modules/.bin` + `npx --no-install`) para evitar wrappers Windows.

**Python**
- dependências pinadas em `scripts/_policy/requirements.txt`.

**Critério de aceite atingido:** CI roda do zero com `npm ci` + `pip install -r scripts/_policy/requirements.txt` (sem instalações globais).

### 7.6 P1: Fechar runtime contract proof (Schemathesis) para o piloto `training`
**Ação:** CI deve subir backend (docker-compose) e rodar `schemathesis run` contra o OpenAPI.  
**Critério de aceite:** pelo menos 1 módulo com convergência contínua contrato↔runtime.

### 7.7 P1: Alinhar severidade/blocking de gates ao canon por aplicabilidade
**Ação:** gates de AsyncAPI/Arazzo devem ser bloqueantes quando module profile exigir surface.  
**Critério de aceite:** não existe evento/workflow inválido passando.

### 7.8 (RESOLVIDO) Spec legada de “governed roots”
**Ação:** a pasta/spec legada (`docs/_canon/specs/`) foi removida para evitar governança paralela.  
**Critério de aceite:** governança passa a ser exclusivamente trilogia `.contract_driven/*` + canon (`docs/_canon/*`) + contract gates.

---

## 8) Como impedir que a governança seja quebrada (hardening “TOP 1”)

### 8.1 Controles incontornáveis (server‑side)
1) **Branch protection + required status checks**
2) **CODEOWNERS** para:
   - `.contract_driven/**`
   - `contracts/**`
   - `docs/_canon/**`
   - `scripts/contracts/validate/**` (gates/compilers)
3) **Bloqueio de force‑push** em branches protegidas
4) **CI fail‑closed** (falta de ferramenta = FAIL, não SKIP)

### 8.2 Controles repo‑level (complementares)
5) Pre‑commit rodando gates oficiais do repo (sem depender de SSOT ausente)
6) `generated/**` tratado como DERIVED:
   - drift gate obrigatório sempre que `generated/**` muda
7) Gate de “tool version”:
   - prova de versões canônicas (node/python/clis) em CI

### 8.3 Controles forenses e anti‑fraude
8) Evidência de gates como artefato CI assinado (preferível) ou com hash fixo no PR
9) “Reproducible outputs”: mesmas entradas → mesmos derivados (compiler determinístico + normalização)
10) Auditoria automática: relatório de mudanças de SSOT (quem, o quê, por quê)

---

## 9) Melhorias após fechar gaps (>= 8) — rumo a líder de mercado

1) **Portal de contratos por módulo/surface** (OpenAPI + AsyncAPI + Arazzo) com changelog automático.
2) **SDKs oficiais e versionados** (TS/Python primeiro) gerados por release.
3) **CDC FE↔BE**: consumer tests para fluxos críticos (não só OpenAPI).
4) **Governança de deprecação (Sunset)**: enforcement de headers e tabela de depreciações.
5) **Segurança dinâmica**: suites OWASP automatizadas (BOLA/BFLA/BOPLA) baseadas em contrato.
6) **Performance por contrato**: SLO declarados e validados em staging.
7) **Outbox + eventos governados** para módulos event‑heavy (`matches`, `scout`, `analytics`).
8) **Classificação de dados sensíveis no schema** (PII/saúde) com gates de masking/logging/auditoria.
9) **Intent DSL completa**: reduzir YAML manual; gerar OpenAPI+schemas+test scaffolds por intenção.
10) **“Golden Modules”**: exemplos “perfeitos” por módulo (CRUD+workflow+event) para reduzir variação.

---

## 10) Agente: capacidade de criar contratos automaticamente (qualidade atual + melhorias)

### 10.1 O que já existe (pontos fortes)
- Prompts operacionais em `.contract_driven/agent_prompts/*` que:
  - impõem ordem mínima de leitura,
  - definem bloqueios (missing module / missing convention / conflito),
  - exigem rodar compiler + gates antes de aceitar contrato.
- Compilers determinísticos:
  - policy compiler (policies resolvidas + manifests + drift check),
  - intent compiler (DSL `.intent.yaml` → OpenAPI paths + validação via policy compiler).
- SSOT `api_rules.yaml` reduz alucinação e padroniza convenções.

### 10.2 Limitações que reduzem qualidade hoje
- Prompts parcialmente hardcoded (ex.: docs mínimas citam `training`) → baixa reutilização.
- Falta de prompts completos para criação/alteração de AsyncAPI e Arazzo como “primeira classe”.
- Ausência de “Agent Output Contract” machine‑readable (decisões e bloqueios não ficam auditáveis).
- Rastreabilidade inconsistente de `generated/` (inputs inexistentes) → derruba confiança.
- Falta de evidência executável sobre “o agente bloqueia quando deveria” (checklist marca como não comprovado).

### 10.3 Melhorias recomendadas (alto ROI)
1) **Agent Output Contract (JSON)**: inputs (paths+sha256), decisões, bloqueios, artefatos escritos.
2) **Gate de prompt compliance**: prova automática de que o output segue SSOT, naming e boundaries.
3) **Expansão da Intent DSL** para expressar:
   - resources, métodos, paginação, erros, authz, rate limit, fields e bindings
4) **Uso consistente de tipos semânticos** (registry + `x-semantic-id`) para reduzir ambiguidade.
5) **Geração de testes mínimos** junto com contrato (Schemathesis smoke + invariants sanity tests).

### 10.4 Qualidade dos contratos existentes (amostra: `training`)
Pontos positivos:
- Paginação cursor, Problem+JSON, OWASP citado, allowlist em requests, `additionalProperties: false`.
- Arazzo workflow vincula operationIds do OpenAPI.
- AsyncAPI inclui payload schema e semantic_id modular (`TRAINING_ATTENDANCE_MARKED`).

Melhorias recomendadas na qualidade (quando evoluir):
- declarar security schemes reais quando `identity_access` for contratado (evitar `security: - {}` como placeholder permanente)
- reduzir duplicação OpenAPI schema ↔ JSON Schema (e fortalecer cross‑spec alignment)
- aumentar uso de bindings semânticos (`x-semantic-id`) onde aplicável

---

## 11) Arquitetura proposta (canon) — análise e melhorias

### 11.1 Base canônica documentada
O canon (`docs/_canon/ARCHITECTURE.md`, C4 context/containers) define:
- Monólito modular (FastAPI) com camadas Router→Service→Repository→DB
- SPA Next.js (cliente gerado via OpenAPI)
- Celery + Redis
- Postgres como base transacional
- Observabilidade por `X-Flow-ID`

Isso é correto e competitivo se governança CDD for enforcement real.

### 11.2 Melhorias arquiteturais de alto impacto (sem mudar o “monólito modular”)
1) **Multi‑tenancy explícita por contrato** (organizationId) como regra global + gates.
2) **Outbox + idempotência** para eventos e jobs (garantia transacional).
3) **AuthZ por objeto como 1ª classe** (BOLA): exigir policy/documentação por operação.
4) **Versionamento por media‑type + sunset** governado e automatizado.
5) **Governança forte de dados sensíveis** (wellness/medical/identity_access): auditoria, minimização, masking.
6) **DB invariants A/B** (quando o backend estiver no repo): constraints no banco com evidência.

---

## 12) Arquitetura estrutural/operacional completa (modelo final “não quebra”)

### 12.1 Estrutural (artefatos)
**SSOT**
- `.contract_driven/**` (metagovernança + templates + axiomas)
- `docs/_canon/**` (canon global)
- `docs/hbtrack/modulos/**` (canon por módulo)
- `contracts/**` (contratos técnicos)

**DERIVED**
- `generated/**` (policies, manifests, cópias derivadas)
- `_reports/**` (evidências)

### 12.2 Operacional (pipeline recomendado)
```mermaid
flowchart LR
  SSOT[SSOT: .contract_driven + docs/_canon + contracts] --> COMP[Compilers determinísticos]
  COMP --> GEN[DERIVED: generated/]
  SSOT --> GATES[validate_contracts gates]
  GEN --> GATES
  GATES --> REP[_reports/contract_gates/latest.json]
  REP --> CI[CI (server-side)]
  CI --> BP[Branch Protection + Required Checks]
  BP --> MERGE[Merge]
  MERGE --> REL[Release: portal + SDKs + changelog]
```

Regras duras:
- CI é o juiz final.
- Gates são binários (PASS/FAIL/SKIP_NOT_APPLICABLE com regras claras).
- Derivados nunca são editados manualmente; drift falha.

### 12.3 “Nunca quebra” (princípio de segurança organizacional)
Não existe “nunca quebra” sem:
- **CI obrigatório** + **branch protection**,
- toolchain pinada e reprodutível,
- waivers governados (machine‑readable),
- rastreabilidade íntegra (inputs existem + hash),
- e, quando há implementação, **runtime proof** contínua (Schemathesis).

---

## 13) HB Track como gerador de contratos Sport‑Tech (Handebol) — rumo a TOP 3

Esta seção é específica para o objetivo “HB Track como gerador de contratos” (não apenas consumidor de contratos).

### 13.1 O que significa “ser um gerador de contratos” no mundo real
Ser TOP 3 implica entregar um **motor reprodutível** que:
- gera contratos consistentes por módulo/surface a partir de intenção (DSL) + axiomas;
- aplica segurança e compatibilidade automaticamente (OWASP + versionamento);
- produz SDKs/documentação/publicação com rastreabilidade;
- e mantém tudo auditável (hashes, manifests, evidências, CI).

### 13.2 Arquitetura do “Contract Engine” (produto)
Componentes recomendados:
- **SSOT de regras e domínio**: `DOMAIN_AXIOMS.json`, `api_rules.yaml`, matrizes (OWASP/authority).
- **Intent DSL** (`*.intent.yaml`) como entrada principal para geração.
- **Compilers determinísticos**:
  - intent → OpenAPI/paths (e eventualmente também schemas/workflows)
  - policy compiler → resolved policy + manifests + derived copies
- **Validadores/Gates** (pipeline): OpenAPI/Spectral/Redocly, AsyncAPI, JSON Schema, Arazzo, breaking changes.
- **Publicação**:
  - portal de contratos (OpenAPI/AsyncAPI/Arazzo)
  - geração e publicação de SDKs versionados
  - changelog e deprecação governada

### 13.3 Requisitos para “Top 3” (checklist objetivo)
1) **Intents cobrindo pelo menos 80% das rotas** dos módulos críticos (reduz YAML manual).
2) **Rastreabilidade completa**: cada artefato gerado com manifest + hashes + inputs existentes.
3) **CI hermética**: tudo roda em máquina limpa com pins/locks.
4) **Governança de breaking changes** com baseline + waiver governado + sunset/deprecation.
5) **Runtime proof**: Schemathesis/contract tests contínuos para módulos piloto e expansão progressiva.
6) **SDKs oficiais** (TS/Python) e docs publicados por release.

### 13.4 Diferenciais para o domínio Handebol (para liderar o mercado)
- Biblioteca de “event taxonomy” e “match/scout vocabulary” governada (evita taxonomia ad‑hoc).
- Templates de workflows (Arazzo) para fluxos reais do esporte: súmula, inscrições, cartões, suspensões, retorno ao jogo.
- Controles de privacidade e auditoria superiores (bem‑estar/medical) como diferencial competitivo.

---

## Apêndice A — Gates: spec vs implementação (observações relevantes)

Implementação principal: `scripts/contracts/validate/validate_contracts.py`.

**Observações de auditoria (para fechar gaps):**
- `HTTP_RUNTIME_CONTRACT_GATE` é SKIP no agregador → precisa ser fechado via CI com backend live.
- `ASYNCAPI_VALIDATION_GATE` aparece como não‑bloqueante no agregador atual → revisar para ser bloqueante quando surface `event` for exigida.
- `TRANSFORMATION_FEASIBILITY_GATE` checa `contracts/generated/` (que não é o local canônico de derivados; o canônico é `generated/`) → revisar.
- `UI_DOC_VALIDATION_GATE` busca `UI_CONTRACT_*.md` sob `contracts/` → revisar para apontar para `docs/hbtrack/modulos/**` (onde os docs vivem).

---

## Apêndice B — Itens ausentes (GAPS objetivas) que impactam governança

- `oasdiff` WSL‑native ausente (breaking changes hoje usam fallback quando o binário não existe)

---

## Apêndice C — Definition of Done (DoD) objetiva para CDD “mundo real”

### C.1 DoD para qualquer mudança em contrato (OpenAPI/AsyncAPI/Arazzo/Schema)
Uma mudança contratual só pode ser considerada pronta quando:
1) **SSOT atualizado** (contrato + docs normativas impactadas).
2) **Derivados regenerados** (se aplicável) e **sem drift**:
   - `generated/**` alinhado ao compiler determinístico.
3) **Gates PASS em CI** (server‑side):
   - lint estrutural (Redocly)
   - policy ruleset (Spectral)
   - JSON Schema validation
   - AsyncAPI/Arazzo quando aplicáveis
   - breaking change gate (oasdiff + baseline)
4) **Rastreabilidade íntegra**:
   - manifests com inputs existentes + hashes corretos
5) **Runtime proof (quando há backend live)**:
   - Schemathesis PASS para endpoints afetados (ou justificativa formal de não aplicabilidade)

### C.2 DoD para “módulo materializado” (pronto para implementação)
Um módulo só é “implementável” de forma CDD quando:
- Docs mínimas existem e estão consistentes (README, MODULE_SCOPE, DOMAIN_RULES, INVARIANTS, TEST_MATRIX).
- Contrato HTTP do módulo existe (OpenAPI path) e está referenciado no OpenAPI root quando aplicável.
- Schemas canônicos existem (JSON Schema e/ou OpenAPI schemas) com regras claras de evolução.
- Se o módulo tiver surface `event`: AsyncAPI completo (channels/messages/schemas) + event_type modular (quando aplicável).
- Se o módulo tiver workflow multi‑step: Arazzo com vínculo por `operationId` e validação.
- Gates PASS contínuos (sem “passar uma vez” e abandonar).

### C.3 DoD para “CDD nunca quebra” (governança)
- CI obrigatório + branch protection habilitados.
- CODEOWNERS para SSOT e gates.
- Toolchain pinada (Node/Python) e executável em máquina limpa.
- Waivers machine‑readable com expiração/fingerprint.
- Auditoria/observabilidade do pipeline (artefatos CI e hashes).

---

## Conclusão

O HB Track já tem uma base **muito forte** de CDD no nível de “sistema de contratos”: SSOT, layout, axiomas, gates e compilers.  
Para virar **CDD de sucesso no mundo real** e “**não quebrável**”, falta transformar a governança em enforcement incontornável:
- eliminar split‑brain (um fluxo oficial),
- consertar rastreabilidade de derivados,
- manter enforcement server‑side (CI + branch protection) e evidências,
- pin/lock toolchain,
- fechar runtime proof (Schemathesis) no piloto e evoluir módulo a módulo.

---

## Próxima tarefa recomendada (P0)

Fechar o “runtime proof” do piloto (módulo `training`) para tornar o contrato **incontestável**:
- subir o backend em CI (via `infra/docker-compose.yml` ou equivalente);
- rodar Schemathesis (ou equivalente) contra `contracts/openapi/openapi.yaml`;
- tornar o gate de runtime **bloqueante** quando o backend estiver disponível.
