---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# CI_CONTRACT_GATES.md

## 0. Objetivo

Este documento define a especificação normativa dos gates de validação contratual do HB Track.

Ele não é um resumo de ferramentas.
Ele é o contrato operacional do pipeline de validação.

Seu papel é:

- definir a ordem obrigatória dos gates
- definir entradas, saídas e critérios binários de PASS/FAIL
- definir pré-condições determinísticas
- definir evidências obrigatórias
- definir códigos de bloqueio canônicos
- impedir split-brain entre fontes soberanas, artefatos derivados e implementações
- impedir que um contrato "passe no lint" mas falhe na integração real

Este documento deve ser lido junto com:

- `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- `docs/_canon/API_CONVENTIONS.md`
- `docs/_canon/DATA_CONVENTIONS.md`
- `docs/_canon/ERROR_MODEL.md`
- `docs/_canon/CHANGE_POLICY.md`
- `docs/_canon/TEST_STRATEGY.md`
- `.contract_driven/DOMAIN_AXIOMS.json` (axiomas globais machine-readable)
- `.contract_driven/templates/API_RULES/API_RULES.yaml` quando aplicável à superfície HTTP

---

## 1. Princípios Normativos

### 1.1 Gate binário
Cada gate termina em exatamente um destes estados:

- `PASS`
- `FAIL`
- `SKIP_NOT_APPLICABLE`

Não existe "quase passou", "aceitável por enquanto", "warn que libera" ou equivalente para gates classificados como bloqueantes.

### 1.2 Ordem obrigatória
A ordem dos gates é vinculante.
Um gate não pode assumir sucesso implícito de gate anterior.

### 1.3 Falha rápida
Se um gate bloqueante falhar, o pipeline deve interromper a execução dos gates dependentes.
Gates independentes podem continuar apenas quando explicitamente marcados como paralelizáveis neste documento.

### 1.4 Determinismo operacional
Nenhum gate pode depender de estado implícito, aleatoriedade não controlada, baseline ambíguo, ou interpretação humana livre como condição de aprovação.

### 1.5 Hermeticidade
Nenhuma fonte fora das raízes soberanas pode participar do grafo de validação sem referência explícita permitida por política canônica.

### 1.6 Semântica cross-artifact
Não basta validar arquivos isolados.
O pipeline deve validar coerência entre OpenAPI, JSON Schema, AsyncAPI, Arazzo, documentação modular e artefatos derivados quando estes coexistirem.

### 1.7 Evidência obrigatória
Todo gate deve produzir evidência estruturada e legível por máquina.

### 1.8 Sem bypass textual
Nenhum gate pode ser burlado por texto explicativo em documento livre.
Exceções exigem artefato machine-readable no formato definido neste documento.

---

## 2. Escopo

Este documento governa a validação de:

- `contracts/openapi/openapi.yaml`
- `contracts/openapi/paths/**/*.yaml`
- `contracts/openapi/components/**`
- `contracts/schemas/**/*.schema.json`
- `contracts/workflows/**/*.arazzo.yaml`
- `contracts/asyncapi/**/*.yaml`
- `docs/hbtrack/modulos/<module>/**/*.md`
- `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json` quando aplicável
- `.contract_driven/DOMAIN_AXIOMS.json`
- `generated/**` quando houver artefatos derivados
- arquivos de waiver machine-readable
- evidências produzidas por `scripts/validate_contracts.py`

Este documento não redefine:

- layout de paths canônicos
- taxonomia de módulos
- regras de naming
- templates de contratos
- regras de API HTTP da superfície OpenAPI

Esses itens continuam sendo governados por `LAYOUT`, `RULES`, `GLOBAL_TEMPLATES` e `API_RULES.yaml`.

---

## 3. Stack Oficial de Validação

A stack oficial é fixa até alteração explícita do manual:

- `Redocly CLI` para lint/validate OpenAPI estrutural
- `Spectral` para rulesets customizados OpenAPI
- `oasdiff` para detecção de breaking change HTTP
- `Schemathesis` para testes contract/runtime HTTP
- `JSON Schema validator in pipeline`
- `AsyncAPI parser/validator`
- `Arazzo validator/linter defined in pipeline`
- `Storybook build` quando houver UI documentada

Substituição de ferramenta sem alteração prévia de `.contract_driven/CONTRACT_SYSTEM_RULES.md` é inválida.

---

## 4. Contrato do Pipeline

O pipeline canônico deve ser executado por um agregador único.

Comando canônico recomendado:

```bash
python scripts/validate_contracts.py
```
O agregador deve:
	•	executar gates na ordem definida neste documento
	•	produzir saída legível por humanos no stdout
	•	produzir saída machine-readable em JSON
	•	retornar exit code determinístico
	•	nunca depender de interação manual
	•	nunca pedir confirmação em tempo de execução

4.1 Arquivo de saída machine-readable obrigatório

O pipeline deve gerar:
`_reports/contract_gates/latest.json`

4.2 Schema lógico da saída do pipeline

Formato obrigatório:

```json
{
  "pipeline_id": "string",
  "timestamp_utc": "ISO-8601 string",
  "target": {
    "scope": "system|module",
    "module": "string|null",
    "openapi_root": "string|null",
    "asyncapi_root": "string|null",
    "workflow_scope": "string|null"
  },
  "environment": {
    "git_commit": "string|null",
    "python_version": "string|null",
    "tool_versions": {
      "redocly": "string|null",
      "spectral": "string|null",
      "oasdiff": "string|null",
      "schemathesis": "string|null",
      "json_schema_validator": "string|null",
      "asyncapi_validator": "string|null",
      "arazzo_validator": "string|null",
      "storybook": "string|null"
    }
  },
  "overall_status": "PASS|FAIL",
  "exit_code": 0,
  "gates": [
    {
      "gate_id": "string",
      "status": "PASS|FAIL|SKIP_NOT_APPLICABLE",
      "blocking": true,
      "exit_code": 0,
      "blocking_code": "string|null",
      "summary": "string",
      "inputs": ["string"],
      "artifacts_checked": ["string"],
      "evidence_files": ["string"],
      "metrics": {
        "errors": 0,
        "warnings": 0,
        "violations": 0,
        "duration_ms": 0
      }
    }
  ]
}
```

4.3 Exit codes do agregador
	•	0 = pipeline PASS
	•	2 = pipeline FAIL_ACTIONABLE
	•	3 = pipeline ERROR_INFRA
	•	4 = pipeline BLOCKED_INPUT
	•	5 = pipeline FAIL_POLICY
	•	6 = pipeline FAIL_RUNTIME_MISMATCH

Nenhum outro exit code é canônico sem atualização deste documento.

⸻

5. Ordem Obrigatória dos Gates

A ordem canônica é:
		0.	AXIOM_INTEGRITY_GATE
		1.	PATH_CANONICALITY_GATE
		2.	REQUIRED_ARTIFACT_PRESENCE_GATE
		2A.	MODULE_DOC_CROSSREF_GATE
		2B.	API_NORMATIVE_DUPLICATION_GATE (não-bloqueante)
		3.	PLACEHOLDER_RESIDUE_GATE
		4.	REF_HERMETICITY_GATE
		5.	OPENAPI_ROOT_STRUCTURE_GATE
		6.	OPENAPI_POLICY_RULESET_GATE
		7.	JSON_SCHEMA_VALIDATION_GATE
		8.	CROSS_SPEC_ALIGNMENT_GATE
	9.	CONTRACT_BREAKING_CHANGE_GATE
	10.	TRANSFORMATION_FEASIBILITY_GATE
	11.	HTTP_RUNTIME_CONTRACT_GATE
	12.	ASYNCAPI_VALIDATION_GATE
	13.	ARAZZO_VALIDATION_GATE
	14.	UI_DOC_VALIDATION_GATE
	15.	DERIVED_DRIFT_GATE
	16.	READINESS_SUMMARY_GATE

5.1 Gates paralelizáveis

Os seguintes gates podem executar em paralelo somente após sucesso de todos os seus pré-requisitos:
	•	ASYNCAPI_VALIDATION_GATE
	•	ARAZZO_VALIDATION_GATE
	•	UI_DOC_VALIDATION_GATE

5.2 Gates não paralelizáveis

Todos os demais gates são sequenciais; gates explicitamente marcados como não-bloqueantes não devem derrubar a readiness quando falham.

6. Política de Severidade

6.1 Severidade canônica

Cada regra interna de ferramenta deve ser mapeada para uma destas severidades do pipeline:
	•	blocking_error
	•	non_blocking_warning
	•	info

6.2 Regra de promoção

Se uma ferramenta externa classificar algo como warning, o pipeline pode promovê-lo a erro bloqueante se este documento assim definir.

6.3 Regras minimamente bloqueantes

Os seguintes problemas são sempre bloqueantes:
	•	path não canônico
	•	artefato obrigatório ausente
	•	placeholder residual em artefato pronto
	•	$ref fora do grafo permitido
	•	OpenAPI estruturalmente inválido
	•	regra policy OpenAPI marcada como error
	•	JSON Schema inválido
	•	divergência cross-spec crítica
	•	breaking change sem waiver machine-readable válido
	•	runtime mismatch crítico
	•	AsyncAPI inválido quando aplicável
	•	Arazzo inválido quando aplicável
	•	drift entre soberano e derivado
	•	ausência de evidência obrigatória do próprio pipeline


7. Política de Waiver Machine-Readable

7.1 Proibição de waiver textual

Nenhum gate pode ser liberado apenas porque um ADR, comentário ou texto em Markdown afirmou uma exceção.

7.2 Artefato canônico de waiver

Waivers devem viver em:
	•	contracts/_waivers/

Formato de nome:
	•	contracts/_waivers/<gate_id>/<waiver_name>.json

7.3 Schema lógico mínimo do waiver

```json
{
  "waiver_id": "string",
  "gate_id": "string",
  "scope": "system|module",
  "module": "string|null",
  "target_artifact": "string",
  "justification": "string",
  "approved_by": "string",
  "approved_at_utc": "ISO-8601 string",
  "expires_at_utc": "ISO-8601 string|null",
  "fingerprint": {
    "type": "sha256",
    "value": "string"
  }
}

7.4 Regras de validade do waiver

Um waiver só é válido se:
	•	o gate_id existir neste documento
	•	o target_artifact existir
	•	o fingerprint corresponder ao artefato ou diff alvo
	•	o waiver não estiver expirado
	•	o scope for compatível com o gate
	•	o waiver não contradizer CHANGE_POLICY.md

7.5 Waiver para breaking change

Breaking change só pode ser liberado por waiver machine-readable que referencie explicitamente o fingerprint do diff detectado.

⸻

8. Política de Determinismo para Gates com Exploração de Estado

8.1 Regra geral

Qualquer gate baseado em geração de casos, fuzzing, property-based testing, busca de estados ou exploração probabilística só é considerado determinístico se suas pré-condições de execução forem fixadas.

8.2 Requisitos obrigatórios para Schemathesis

HTTP_RUNTIME_CONTRACT_GATE só pode retornar PASS quando todos os seguintes requisitos forem verdadeiros:
	•	seed explícita fixada
	•	base URL explícita fixada
	•	ambiente alvo identificado
	•	banco ou estado externo resetado antes da execução
	•	fixture de autenticação conhecida
	•	timeouts explícitos
	•	número de exemplos/casos explicitamente fixado
	•	logs e falhas serializados em evidência

8.3 Proibição

Executar Schemathesis sem seed fixa e sem reset de estado invalida o resultado do gate.
Nesse caso, o gate deve falhar com ERROR_INFRA ou BLOCKED_INPUT, nunca retornar PASS.

⸻

9. Especificação dos Gates

9.0 AXIOM_INTEGRITY_GATE

Objetivo

Provar que a própria “física do sistema” é válida antes de validar contratos: `.contract_driven/DOMAIN_AXIOMS.json` deve ser estruturalmente e semanticamente consistente.

Aplica quando

Sempre. Este é o primeiro gate do pipeline.

Entradas
	•	`.contract_driven/DOMAIN_AXIOMS.json`
	•	`contracts/schemas/shared/domain_axioms.schema.json`

Executor

Script Python do pipeline.

### Verificações obrigatórias (ordem fixa)
- JSON parse do arquivo de axiomas (sintaxe/encoding)
- validação contra `domain_axioms.schema.json`
- compilação de todos os `global_formats.*.pattern` (regex válida no Python)
- resolução de referências internas (`format_ref`, `*_enum_ref`, `*_machine_ref`) para chaves existentes
- integridade de enums (UPPER_SNAKE_CASE, closed/open set policy)
- integridade de máquinas de estado (grafo bem-formado, sem órfãos, sem dead-ends não terminais, forbidden não pode aparecer em allowed)
- integridade da progressão disciplinar (ordem e precondições)
- integridade do modelo de erro (Problem + required fields canônicos)
- integridade cross-surface (refs e invariantes canônicas)
- integridade da normalization policy (regex compila + flags canônicas)
- integridade do contrato do validador (checks obrigatórios presentes)

PASS
	•	todas as verificações verdadeiras

FAIL
	•	qualquer verificação falhar

### Blocking codes (violations)
- `BLOCKED_AXIOM_FILE_NOT_FOUND`
- `BLOCKED_INVALID_AXIOM_JSON`
- `BLOCKED_AXIOM_SCHEMA_INVALID`
- `BLOCKED_AXIOM_INVALID_REGEX`
- `BLOCKED_AXIOM_BROKEN_INTERNAL_REFERENCE`
- `BLOCKED_AXIOM_INVALID_ENUM_DEFINITION`
- `BLOCKED_AXIOM_ILLEGAL_OPEN_SET_POLICY`
- `BLOCKED_AXIOM_ILLEGAL_CLOSED_SET_EXTENSION_POLICY`
- `BLOCKED_AXIOM_INVALID_STATE_MACHINE`
- `BLOCKED_AXIOM_ORPHAN_STATE`
- `BLOCKED_AXIOM_DEAD_END_STATE`
- `BLOCKED_AXIOM_FORBIDDEN_TRANSITION_CONFLICT`
- `BLOCKED_AXIOM_TERMINAL_STATE_WITH_OUTGOING_EDGE`
- `BLOCKED_AXIOM_INVALID_DISCIPLINARY_PROGRESSION`
- `BLOCKED_AXIOM_DISCIPLINARY_PRECONDITION_MISSING`
- `BLOCKED_AXIOM_DISCIPLINARY_ORDER_CONFLICT`
- `BLOCKED_AXIOM_INVALID_ERROR_MODEL`
- `BLOCKED_AXIOM_MISSING_REQUIRED_ERROR_FIELD`
- `BLOCKED_AXIOM_INVALID_CROSS_SURFACE_CONSTRAINT`
- `BLOCKED_AXIOM_INVALID_NORMALIZATION_POLICY`
- `BLOCKED_AXIOM_INVALID_NORMALIZATION_REGEX`
- `BLOCKED_AXIOM_INVALID_VALIDATOR_CONTRACT`
- `BLOCKED_AXIOM_INTEGRITY`

Evidência
	•	resultado estruturado em `_reports/contract_gates/latest.json` (campo `axiom_integrity` quando FAIL)

Dependências
	•	nenhuma

⸻

9.1 PATH_CANONICALITY_GATE

Objetivo

Garantir que artefatos normativos e técnicos existam apenas em paths canônicos e que não haja split-brain por duplicata soberana.

Aplica quando

Sempre.

Entradas
	•	árvore do repositório
	•	.contract_driven/CONTRACT_SYSTEM_LAYOUT.md
	•	.contract_driven/CONTRACT_SYSTEM_RULES.md

Executor

Script Python do pipeline.

Verificações obrigatórias
	•	nenhum contrato técnico fora de contracts/
	•	nenhum artefato global canônico fora de docs/_canon/
	•	nenhum artefato de governança fora de .contract_driven/
	•	nenhum artefato derivado tratado como soberano
	•	nenhum arquivo de módulo fora da taxonomia canônica
	•	nenhum arquivo normativo duplicado concorrente para a mesma superfície

PASS

Todas as verificações acima verdadeiras.

FAIL

Qualquer violação.

Blocking codes
	•	BLOCKED_NON_CANONICAL_PATH
	•	BLOCKED_DUPLICATE_SOVEREIGN_SOURCE
	•	BLOCKED_MISSING_MODULE

Evidência
	•	inventário de paths inspecionados
	•	lista de violações
	•	lista de duplicatas, se houver

Dependências

Nenhuma.

⸻

9.2 REQUIRED_ARTIFACT_PRESENCE_GATE

Objetivo

Garantir presença dos artefatos mínimos obrigatórios para sistema e módulo.

Aplica quando

Sempre.

Entradas
	•	árvore do repositório
	•	.contract_driven/CONTRACT_SYSTEM_RULES.md
	•	.contract_driven/CONTRACT_SYSTEM_LAYOUT.md

Executor

Script Python do pipeline.

Verificações obrigatórias

No escopo global:
	•	presença dos artefatos canônicos globais definidos no layout

No escopo de módulo:
	•	README.md
	•	MODULE_SCOPE_<MODULE>.md
	•	DOMAIN_RULES_<MODULE>.md
	•	INVARIANTS_<MODULE>.md
	•	TEST_MATRIX_<MODULE>.md
	•	contracts/openapi/paths/<module>.yaml
	•	contracts/schemas/<module>/

Artefatos condicionais:
	•	devem existir se o módulo declarar aplicabilidade real para state, permissions, errors, UI, screen map, workflows ou eventos

PASS

Nenhuma ausência.

FAIL

Qualquer artefato obrigatório ausente.

Blocking codes
	•	BLOCKED_MISSING_REQUIRED_ARTIFACT
	•	BLOCKED_MISSING_OPENAPI_PATH
	•	BLOCKED_MISSING_SCHEMA
	•	BLOCKED_MISSING_DOMAIN_RULE
	•	BLOCKED_MISSING_INVARIANT
	•	BLOCKED_MISSING_TEST_MATRIX
	•	BLOCKED_MISSING_STATE_MODEL
	•	BLOCKED_MISSING_PERMISSION_MODEL
	•	BLOCKED_MISSING_UI_CONTRACT
	•	BLOCKED_MISSING_HANDBALL_REFERENCE

Evidência
	•	inventário por módulo
	•	lista de faltas por categoria

Dependências

PATH_CANONICALITY_GATE

⸻

9.2A MODULE_DOC_CROSSREF_GATE

Objetivo

Garantir que os docs mínimos de módulo tenham o header YAML canônico e que seus cross-references apontem para os paths soberanos corretos (SYSTEM_SCOPE, handball rules quando aplicável, OpenAPI path file e pasta de schemas).

Aplica quando

Sempre que existirem docs de módulo sob `docs/hbtrack/modulos/<module>/`.

Entradas
	•	docs/hbtrack/modulos/<module>/*
	•	docs/_canon/SYSTEM_SCOPE.md
	•	docs/_canon/HANDBALL_RULES_DOMAIN.md
	•	contracts/openapi/paths/<module>.yaml
	•	contracts/schemas/<module>/

PASS

Headers presentes e todos os refs resolvem para os artefatos canônicos.

FAIL

Header ausente/inválido ou cross-reference apontando para path incorreto/inexistente.

Blocking codes
	•	BLOCKED_INVALID_MODULE_DOC_HEADER

⸻

9.2B API_NORMATIVE_DUPLICATION_GATE

Objetivo

Detectar risco de duplicação normativa de convenções/shape HTTP no canon humano (`docs/_canon/`) sem apontar a SSOT `.contract_driven/templates/API_RULES/API_RULES.yaml`.

Severidade

Não-bloqueante por padrão (warning forte). Pode ser promovido a bloqueante quando o canon estiver estabilizado.

PASS

Nenhum doc do canon menciona convenções/shape HTTP sem apontar a SSOT.

FAIL

Qualquer doc do canon menciona convenções/shape HTTP e não aponta a SSOT.

Blocking code
	•	WARN_API_NORMATIVE_OUTSIDE_SSOT

⸻

9.3 PLACEHOLDER_RESIDUE_GATE

Objetivo

Bloquear contratos e documentação prontos com placeholders residuais.

Aplica quando

Sempre.

Entradas
	•	todos os artefatos no escopo do pipeline

Executor

Script Python do pipeline.

Lista mínima bloqueante
	•	TODO
	•	TBD
	•	A definir
	•	{{...}}
	•	<MODULE_NAME>
	•	<MODULE>
	•	<ENTITY>
	•	qualquer placeholder declarado pelo próprio sistema como não resolvido

PASS

Nenhum placeholder residual em artefato avaliado como pronto.

FAIL

Qualquer placeholder residual.

Blocking code
	•	BLOCKED_PLACEHOLDER_RESIDUE

Evidência
	•	arquivo
	•	linha
	•	token encontrado

Dependências

REQUIRED_ARTIFACT_PRESENCE_GATE

⸻

9.4 REF_HERMETICITY_GATE

Objetivo

Garantir que o grafo de referências não escape das raízes soberanas permitidas.

Aplica quando

Sempre que houver OpenAPI, AsyncAPI, Arazzo, JSON Schema ou refs documentais validados pelo pipeline.

Entradas
	•	contracts/**
	•	docs/**
	•	.contract_driven/**

Executor

Script Python do pipeline, com resolução de grafo de refs e links.

Regras obrigatórias
	•	nenhum $ref pode apontar para fora das raízes soberanas permitidas
	•	nenhum link documental obrigatório pode apontar para arquivo inexistente
	•	nenhum contrato pode depender de artefato gerado como se fosse fonte soberana
	•	refs externos só são permitidos se explicitamente aprovados por política canônica

PASS

Todos os refs resolvem dentro do grafo permitido.

FAIL

Qualquer ref fora da raiz permitida, quebrado ou apontando para derivado proibido.

Blocking codes
	•	BLOCKED_REF_OUTSIDE_SOVEREIGN_ROOT
	•	BLOCKED_BROKEN_REFERENCE
	•	BLOCKED_DERIVED_COMPETING_WITH_SOURCE

Evidência
	•	grafo resolvido de refs
	•	lista de violações
	•	origem e destino de cada violação

Dependências

PLACEHOLDER_RESIDUE_GATE

⸻

9.5 OPENAPI_ROOT_STRUCTURE_GATE

Objetivo

Validar a estrutura do root OpenAPI e de todos os refs estruturais alcançáveis a partir dele.

Aplica quando

Sempre que contracts/openapi/openapi.yaml existir.

Entradas
	•	contracts/openapi/openapi.yaml

Ferramenta

Redocly CLI

Comando de referência

redocly lint contracts/openapi/openapi.yaml

PASS
	•	exit code 0 da ferramenta
	•	sem refs quebrados
	•	sem erro estrutural
	•	root válido
	•	paths resolvidos
	•	components resolvidos

FAIL

Qualquer erro estrutural da ferramenta.

Blocking code
	•	BLOCKED_OPENAPI_INVALID_STRUCTURE

Evidência
	•	stdout/stderr da ferramenta
	•	exit code
	•	arquivo de log

Dependências

REF_HERMETICITY_GATE

⸻

9.6 OPENAPI_POLICY_RULESET_GATE

Objetivo

Aplicar as regras normativas do HB Track sobre a superfície OpenAPI.

Aplica quando

Sempre que contracts/openapi/openapi.yaml existir.

Entradas
	•	contracts/openapi/openapi.yaml
	•	.spectral.yaml
	•	.contract_driven/templates/API_RULES/API_RULES.yaml quando aplicável

Ferramenta

Spectral

Comando de referência

spectral lint contracts/openapi/openapi.yaml --ruleset .spectral.yaml

Regras mínimas esperadas no ruleset
	•	OpenAPI 3.1.x
	•	proibição de versionamento por URI
	•	operationId obrigatório
	•	tags com descrição
	•	paginação obrigatória para coleções quando a convenção exigir
	•	Problem Details para respostas de erro quando definido
	•	segurança declarada quando aplicável
	•	naming conforme convenções canônicas
	•	proibição de exposição silenciosa de outro módulo pelo path file errado

PASS

Nenhuma violação classificada como error.

FAIL

Qualquer violação classificada como error.

Blocking code
	•	BLOCKED_OPENAPI_POLICY_VIOLATION

Evidência
	•	stdout/stderr da ferramenta
	•	exit code
	•	violations por regra

Dependências

OPENAPI_ROOT_STRUCTURE_GATE

⸻

9.7 JSON_SCHEMA_VALIDATION_GATE

Objetivo

Validar sintaxe, refs e naming dos JSON Schemas de domínio.

Aplica quando

Sempre que houver arquivos *.schema.json.

Entradas
	•	contracts/schemas/**/*.schema.json

Ferramenta

Validador JSON Schema definido no pipeline.

Comando de referência

ajv validate -s contracts/schemas/<module>/*.schema.json

PASS
	•	todos os schemas válidos
	•	refs resolvidos
	•	filenames obedecem <entity>.schema.json

FAIL
	•	schema inválido
	•	ref inválido
	•	arquivo fora do naming canônico

Blocking code
	•	BLOCKED_INVALID_JSON_SCHEMA

Evidência
	•	lista de arquivos validados
	•	erros por arquivo
	•	exit code

Dependências

REF_HERMETICITY_GATE

⸻

9.8 CROSS_SPEC_ALIGNMENT_GATE

Objetivo

Validar coerência semântica cross-artifact entre superfícies que representam o mesmo conceito.

Aplica quando

Sempre que coexistirem duas ou mais superfícies representando conceitos semanticamente relacionados.

Entradas
	•	OpenAPI
	•	JSON Schema
	•	AsyncAPI
	•	Arazzo
	•	docs modulares
	•	domain axioms: `.contract_driven/DOMAIN_AXIOMS.json`
	•	axiomas modulares: `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json` (quando existir e permitido por política)
	•	ERROR_MODEL.md
	•	API_CONVENTIONS.md
	•	DATA_CONVENTIONS.md

Executor

Script Python do pipeline.

### Verificações mínimas obrigatórias
- erro HTTP em OpenAPI alinha com `domain_axioms.error_axioms`
- enums usados em OpenAPI, AsyncAPI, JSON Schema e STATE_MODEL devem pertencer ao conjunto permitido em `domain_axioms.domain_enums`
- se `closed_set` for `true`, qualquer valor fora do conjunto canônico deve falhar
- se `module_extension_policy.allow_module_extensions` for `true`, extensões só são válidas quando declaradas em `docs/hbtrack/modulos/<module>/DOMAIN_AXIOMS_<MODULE>.json`
- formatos de data, timestamp, ids públicos, `trace_id` e `request_id` devem obedecer a `domain_axioms.global_formats`
- máquinas de estado modulares devem ser subconjunto de `domain_axioms.state_axioms`
- transições presentes em `forbidden_transitions` devem falhar sempre
- Arazzo deve referenciar `operationId` existente no OpenAPI
- docs modulares não podem contradizer enums, formatos ou estados definidos em `DOMAIN_AXIOMS.json`

PASS

Nenhuma divergência crítica.

FAIL

Qualquer divergência crítica entre superfícies.

### Blocking codes
- `BLOCKED_CROSS_SPEC_DIVERGENCE`
- `BLOCKED_ENUM_OUTSIDE_AXIOMS`
- `BLOCKED_FORMAT_VIOLATION`
- `BLOCKED_STATE_MACHINE_VIOLATION`
- `BLOCKED_FORBIDDEN_TRANSITION`
- `BLOCKED_ARAZZO_OPENAPI_LINK_MISSING`
- `BLOCKED_ERROR_MODEL_MISMATCH`

Evidência
	•	matriz de alinhamento
	•	divergências por conceito
	•	origem e destino de cada conflito

Dependências
	•	OPENAPI_POLICY_RULESET_GATE
	•	JSON_SCHEMA_VALIDATION_GATE

⸻

9.9 CONTRACT_BREAKING_CHANGE_GATE

Objetivo

Bloquear breaking changes HTTP sem waiver machine-readable válido.

Aplica quando

Em revisão de contrato, comparação de baseline e candidate.

Entradas
	•	baseline OpenAPI
	•	candidate OpenAPI
	•	CHANGE_POLICY.md
	•	waivers em contracts/_waivers/CONTRACT_BREAKING_CHANGE_GATE/

Ferramenta

oasdiff

Comando de referência

oasdiff breaking contracts/openapi/baseline.yaml contracts/openapi/openapi.yaml

PASS
	•	nenhum breaking change detectado
ou
	•	todo breaking change detectado coberto por waiver válido

FAIL
	•	breaking change detectado sem waiver válido
	•	waiver expirado
	•	waiver com fingerprint incompatível

Blocking code
	•	BLOCKED_BREAKING_CHANGE

Evidência
	•	diff
	•	fingerprint do diff
	•	waiver associado, se houver

Dependências

CROSS_SPEC_ALIGNMENT_GATE

⸻

9.10 TRANSFORMATION_FEASIBILITY_GATE

Objetivo

Validar que o contrato é implementável na stack técnica e transformável de forma idempotente para os artefatos derivados esperados.

Aplica quando

Sempre que houver geração de tipos, cliente, docs ou outros derivados.

Entradas
	•	OpenAPI
	•	JSON Schema
	•	domain axioms: `.contract_driven/DOMAIN_AXIOMS.json` (normalization_policy)
	•	geradores configurados
	•	pasta generated/

Executor

Script Python do pipeline + geradores da stack.

### Verificações mínimas obrigatórias
- contrato pode ser processado pelas ferramentas de geração configuradas
- geração repetida do mesmo input produz saída equivalente após aplicação de `domain_axioms.normalization_policy`
- comparação de drift deve ocorrer somente após strip de linhas voláteis, normalização de line endings, trim de trailing whitespace e garantia de final newline
- nenhum gerado precisa de edição manual para permanecer funcional

PASS

Todas as verificações verdadeiras.

FAIL

Qualquer inviabilidade de transformação ou não idempotência.

Blocking codes
	•	BLOCKED_TRANSFORMATION_NOT_FEASIBLE
	•	BLOCKED_NON_IDEMPOTENT_GENERATION

Evidência
	•	logs de geração
	•	diff de duas gerações consecutivas
	•	lista de incompatibilidades

Dependências
	•	CONTRACT_BREAKING_CHANGE_GATE
	•	CROSS_SPEC_ALIGNMENT_GATE

⸻

9.11 HTTP_RUNTIME_CONTRACT_GATE

Objetivo

Validar aderência runtime da implementação HTTP ao contrato OpenAPI.

Aplica quando

Existe ambiente executável explicitamente provisionado para teste runtime.

Entradas
	•	OpenAPI root
	•	base URL
	•	credenciais/fixtures controladas
	•	seed fixa
	•	estratégia de reset de estado

Ferramenta

Schemathesis

Comando de referência

schemathesis run contracts/openapi/openapi.yaml --base-url=<API_BASE_URL> --seed=<FIXED_SEED>

Pré-condições obrigatórias
	•	ambiente alvo identificado
	•	seed fixa
	•	reset de estado antes da execução
	•	autenticação de teste conhecida
	•	timeout configurado
	•	número máximo de casos configurado
	•	side effects perigosos isolados ou proibidos no ambiente de teste

PASS
	•	ferramenta retorna sucesso
	•	nenhuma divergência crítica de schema/status/content-type
	•	todas as pré-condições determinísticas satisfeitas

FAIL
	•	mismatch crítico entre runtime e contrato
	•	ambiente sem reset
	•	seed ausente
	•	configuração indeterminística

Blocking codes
	•	BLOCKED_RUNTIME_CONTRACT_MISMATCH
	•	BLOCKED_NONDETERMINISTIC_RUNTIME_GATE
	•	BLOCKED_RUNTIME_ENV_NOT_RESET

Evidência
	•	seed usada
	•	base URL
	•	snapshot do estado inicial
	•	stdout/stderr
	•	falhas serializadas
	•	exit code

Dependências
	•	TRANSFORMATION_FEASIBILITY_GATE

⸻

9.12 ASYNCAPI_VALIDATION_GATE

Objetivo

Validar contratos de eventos quando eles existirem por realidade de evento.

Aplica quando

Existe AsyncAPI real no escopo.

Entradas
	•	contracts/asyncapi/asyncapi.yaml
	•	splits relacionados

Ferramenta

AsyncAPI parser/validator

PASS
	•	documento válido
	•	refs válidos
	•	sem placeholder
	•	contrato existe porque há evento real documentado

FAIL
	•	documento inválido
	•	contrato placeholder sem realidade de evento

Blocking codes
	•	BLOCKED_INVALID_ASYNCAPI
	•	BLOCKED_ASYNCAPI_WITHOUT_EVENT_REALITY

Evidência
	•	log do validador
	•	inventário de canais/operações/mensagens
	•	exit code

Dependências
	•	REF_HERMETICITY_GATE
	•	CROSS_SPEC_ALIGNMENT_GATE

⸻

9.13 ARAZZO_VALIDATION_GATE

Objetivo

Validar workflows multi-step quando eles existirem por realidade de orquestração.

Aplica quando

Existe Arazzo real no escopo.

Entradas
	•	contracts/workflows/**/*.arazzo.yaml
	•	OpenAPI root

Ferramenta

Validador/linter Arazzo definido no pipeline.

Verificações obrigatórias
	•	documento válido
	•	refs válidos
	•	operationId referenciado existe no OpenAPI
	•	workflow existe porque há realidade multi-step documentada

PASS

Todas as verificações verdadeiras.

FAIL

Qualquer violação.

Blocking codes
	•	BLOCKED_INVALID_ARAZZO
	•	BLOCKED_ARAZZO_WITHOUT_WORKFLOW_REALITY
	•	BLOCKED_ARAZZO_OPENAPI_LINK_MISSING

Evidência
	•	log do validador
	•	lista de operationIds referenciados
	•	resolução dessas referências no OpenAPI

Dependências
	•	OPENAPI_ROOT_STRUCTURE_GATE
	•	CROSS_SPEC_ALIGNMENT_GATE

⸻

9.14 UI_DOC_VALIDATION_GATE

Objetivo

Validar documentação de UI quando houver superfície UI documentada.

Aplica quando

Existe UI_CONTRACT_<MODULE>.md, Storybook ou documentação equivalente.

Entradas
	•	docs de UI
	•	Storybook, quando adotado

Ferramenta

Storybook build quando aplicável

PASS
	•	build bem-sucedido
	•	componentes documentados não contradizem contrato UI soberano

FAIL
	•	build falhou
	•	divergência crítica entre documentação e contrato UI

Blocking code
	•	BLOCKED_UI_DOC_INVALID

Evidência
	•	logs de build
	•	componentes validados
	•	divergências encontradas

Dependências
	•	REQUIRED_ARTIFACT_PRESENCE_GATE

⸻

9.15 DERIVED_DRIFT_GATE

Objetivo

Garantir que artefatos derivados permanecem derivados, regeneráveis e não concorram com a fonte soberana.

Aplica quando

Existem artefatos em generated/.

Entradas
	•	generated/**
	•	contratos soberanos correspondentes
	•	compiler determinístico: `scripts/contracts/validate/api/compile_api_policy.py`
	•	domain axioms: `.contract_driven/DOMAIN_AXIOMS.json` (normalization_policy.derived_artifacts)

Executor

Script Python do pipeline.

### Verificações obrigatórias
- `generated/` existe e não está vazia
- o compiler recompila o **esperado** em memória (policy resolvida + cópias derivadas + manifestos)
- comparação é feita de forma determinística (byte-a-byte) entre o esperado e o que está em `generated/`
- qualquer drift exige reexecução do compiler (ex.: `python3 scripts/contracts/validate/api/compile_api_policy.py --all`)

PASS

Todas as verificações verdadeiras.

FAIL

Qualquer violação.

Blocking codes
	•	BLOCKED_DERIVED_DRIFT
	•	BLOCKED_DERIVED_COMPETING_WITH_SOURCE
	•	BLOCKED_NON_IDEMPOTENT_GENERATION
	•	BLOCKED_NON_NORMALIZED_DERIVED_DIFF_CHECK

Evidência
	•	inventário de derivados
	•	logs de regeneração
	•	diffs detectados

Dependências

TRANSFORMATION_FEASIBILITY_GATE

⸻

9.16 READINESS_SUMMARY_GATE

Objetivo

Consolidar o resultado binário de prontidão do contrato e do módulo.

Aplica quando

Sempre.

Entradas

Todos os resultados anteriores.

Executor

Script Python do pipeline.

PASS
	•	todos os gates bloqueantes aplicáveis passaram
	•	nenhuma lacuna crítica remanescente
	•	critérios de Contract Ready for Implementation atendidos
	•	critérios de Module Ready for Implementation atendidos quando o escopo for módulo

FAIL

Qualquer gate bloqueante aplicável falhou ou foi indevidamente omitido.

Blocking codes
	•	BLOCKED_CONTRACT_NOT_READY
	•	BLOCKED_MODULE_NOT_READY

Evidência
	•	resumo consolidado
	•	lista de gates aplicáveis
	•	lista de gates falhos
	•	decisão final

Dependências

Todos os gates aplicáveis.

⸻

10. Matriz de Aplicabilidade

10.1 Gates sempre aplicáveis
	•	PATH_CANONICALITY_GATE
	•	REQUIRED_ARTIFACT_PRESENCE_GATE
	•	PLACEHOLDER_RESIDUE_GATE
	•	REF_HERMETICITY_GATE
	•	READINESS_SUMMARY_GATE

10.2 Gates aplicáveis quando houver OpenAPI
	•	OPENAPI_ROOT_STRUCTURE_GATE
	•	OPENAPI_POLICY_RULESET_GATE
	•	CONTRACT_BREAKING_CHANGE_GATE em revisão comparativa
	•	HTTP_RUNTIME_CONTRACT_GATE quando existir ambiente de teste
	•	TRANSFORMATION_FEASIBILITY_GATE quando houver geração

10.3 Gates aplicáveis quando houver JSON Schema
	•	JSON_SCHEMA_VALIDATION_GATE

10.4 Gates aplicáveis quando houver superfícies múltiplas relacionadas
	•	CROSS_SPEC_ALIGNMENT_GATE

10.5 Gates aplicáveis quando houver AsyncAPI
	•	ASYNCAPI_VALIDATION_GATE

10.6 Gates aplicáveis quando houver Arazzo
	•	ARAZZO_VALIDATION_GATE

10.7 Gates aplicáveis quando houver UI documentada
	•	UI_DOC_VALIDATION_GATE

10.8 Gates aplicáveis quando houver derivados
	•	DERIVED_DRIFT_GATE

⸻

11. Política de Evidência

Cada gate deve produzir:
	•	comando executado
	•	inputs considerados
	•	artifacts_checked
	•	exit code
	•	status
	•	blocking_code quando houver
	•	logs brutos
	•	resumo textual
	•	timestamp UTC
	•	duração em milissegundos

A ausência de evidência torna o gate inválido mesmo que a ferramenta tenha sido executada.

Blocking code:
	•	BLOCKED_MISSING_GATE_EVIDENCE

⸻

12. Política de Baseline

12.1 Baseline canônico para diffs HTTP

A fonte baseline do CONTRACT_BREAKING_CHANGE_GATE deve ser explícita.
Não é permitido comparar contra “o que estava localmente” sem identificação.

12.2 Requisitos do baseline

O baseline deve informar:
	•	path do arquivo baseline
	•	commit ou tag de origem
	•	fingerprint do baseline

12.3 Falha por baseline ambíguo

Se o baseline não puder ser identificado de forma inequívoca, o gate deve falhar.

Blocking code:
	•	BLOCKED_AMBIGUOUS_BASELINE

⸻

13. Política de Integridade Semântica

13.1 Regra

Toda superfície adicional aumenta a obrigação de alinhamento semântico.

13.2 Casos mínimos de alinhamento obrigatório
	•	identificadores críticos
	•	enums críticos
	•	formas públicas de erro
	•	operationIds usados em workflow
	•	tópicos/eventos correlacionados com APIs públicas
	•	docs de UI versus contratos de payload/erro/estado

13.3 Proibição

Não é permitido aprovar contratos isoladamente quando o sistema já possui superfícies relacionadas conflitantes.

⸻

14. Política de Side Effects e Ambientes

14.1 Ambientes de validação runtime

Todo gate que toca implementação real deve declarar:
	•	ambiente alvo
	•	credenciais de teste
	•	política de reset
	•	política de limpeza
	•	política para side effects destrutivos

14.2 Operações destrutivas

Operações destrutivas só podem ser exercitadas em ambiente controlado e resetável.

14.3 Falha por ausência de isolamento

Se não houver isolamento suficiente, o gate runtime não pode retornar PASS.

Blocking code:
	•	BLOCKED_RUNTIME_ENV_UNSAFE

⸻

15. Lista Canônica de Blocking Codes
	•	BLOCKED_NON_CANONICAL_PATH
	•	BLOCKED_DUPLICATE_SOVEREIGN_SOURCE
	•	BLOCKED_MISSING_MODULE
	•	BLOCKED_MISSING_REQUIRED_ARTIFACT
	•	BLOCKED_MISSING_OPENAPI_PATH
	•	BLOCKED_MISSING_SCHEMA
	•	BLOCKED_MISSING_DOMAIN_RULE
	•	BLOCKED_MISSING_INVARIANT
	•	BLOCKED_MISSING_TEST_MATRIX
	•	BLOCKED_MISSING_STATE_MODEL
	•	BLOCKED_MISSING_PERMISSION_MODEL
	•	BLOCKED_MISSING_UI_CONTRACT
	•	BLOCKED_MISSING_HANDBALL_REFERENCE
	•	BLOCKED_PLACEHOLDER_RESIDUE
	•	BLOCKED_REF_OUTSIDE_SOVEREIGN_ROOT
	•	BLOCKED_BROKEN_REFERENCE
	•	BLOCKED_OPENAPI_INVALID_STRUCTURE
	•	BLOCKED_OPENAPI_POLICY_VIOLATION
	•	BLOCKED_INVALID_JSON_SCHEMA
	•	BLOCKED_CROSS_SPEC_DIVERGENCE
	•	BLOCKED_ARAZZO_OPENAPI_LINK_MISSING
	•	BLOCKED_ERROR_MODEL_MISMATCH
	•	BLOCKED_BREAKING_CHANGE
	•	BLOCKED_AMBIGUOUS_BASELINE
	•	BLOCKED_TRANSFORMATION_NOT_FEASIBLE
	•	BLOCKED_NON_IDEMPOTENT_GENERATION
	•	BLOCKED_RUNTIME_CONTRACT_MISMATCH
	•	BLOCKED_NONDETERMINISTIC_RUNTIME_GATE
	•	BLOCKED_RUNTIME_ENV_NOT_RESET
	•	BLOCKED_RUNTIME_ENV_UNSAFE
	•	BLOCKED_INVALID_ASYNCAPI
	•	BLOCKED_ASYNCAPI_WITHOUT_EVENT_REALITY
	•	BLOCKED_INVALID_ARAZZO
	•	BLOCKED_ARAZZO_WITHOUT_WORKFLOW_REALITY
	•	BLOCKED_UI_DOC_INVALID
	•	BLOCKED_DERIVED_DRIFT
	•	BLOCKED_DERIVED_COMPETING_WITH_SOURCE
	•	BLOCKED_MISSING_GATE_EVIDENCE
	•	BLOCKED_CONTRACT_NOT_READY
	•	BLOCKED_MODULE_NOT_READY

⸻

16. Critério Final de PASS do Pipeline

O pipeline só pode retornar PASS se:
	•	todos os gates bloqueantes aplicáveis retornarem PASS
	•	nenhum gate aplicável estiver sem evidência
	•	nenhum waiver inválido tiver sido usado
	•	nenhuma divergência cross-spec crítica existir
	•	nenhum derivado competir com a fonte soberana
	•	o resultado final de prontidão for binário e positivo

Qualquer outra situação deve retornar FAIL.

⸻

17. Proibições Explícitas

É proibido:
	•	aprovar gate por interpretação humana de texto livre
	•	aprovar runtime gate sem seed fixa quando a ferramenta gerar casos
	•	aprovar gate com baseline ambíguo
	•	aprovar contrato com refs fora do grafo permitido
	•	tratar warning como irrelevante sem política explícita
	•	tratar artefato gerado como fonte soberana
	•	aprovar Arazzo sem verificar resolução de operationId
	•	aprovar AsyncAPI placeholder sem realidade de evento
	•	aprovar módulo por checklist manual sem evidência executável
	•	omitir gate aplicável sem registrar SKIP_NOT_APPLICABLE com justificativa objetiva

⸻

18. Comando Agregador Recomendado

O pipeline deve ser exposto por um comando único.

Exemplo canônico:

python scripts/validate_contracts.py

Esse comando deve:
	•	carregar este documento como política normativa
	•	executar os gates em ordem
	•	serializar a saída machine-readable obrigatória
	•	falhar com exit code canônico
	•	nunca depender de input interativo

⸻

19. DONE do Documento

Este documento está sendo usado corretamente somente quando:
	•	existe scripts/validate_contracts.py
	•	existe _reports/contract_gates/latest.json
	•	cada gate aplicável gera evidência
	•	o pipeline falha de forma determinística para os casos bloqueantes
	•	pelo menos um contrato já foi validado ponta a ponta com este pipeline
