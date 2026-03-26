< ⚠️  UNDER REVIEW FOR C4 CONSOLIDATION (Sovereign Integrity Audit) -->
# AUDITORIA ARQUITETURAL — HB Track Instruction System

---

## PARTE 1 — MAPA RECURSIVO DO ESCOPO

| Arquivo | Tipo | Como foi encontrado | Papel atual | Papel real |
|---------|------|---------------------|-------------|------------|
| `CLAUDE.md` | Governança — boot permanente | Listado diretamente | Boot permanente obrigatório: identidade, módulos, task_types, bloqueios, árvore de decisão, comunicação, boot profiles, paths | Autoridade nível-0; único arquivo de boot permanente; bem executado |
| `SESSION_HANDOFF.md` | Handoff de sessão — leitura condicional | Listado diretamente | Estado de sessão, decisões pendentes, ADRs recentes | Ponteiro de continuidade entre sessões; funciona como pretendido |
| `.contract_driven/CONTRACT_SYSTEM_RULES.md` | Governança central — leitura condicional | Listado diretamente | Regras operacionais vinculantes: criação, validação, soberania, precedência, boot, bloqueios, DoD, procedimentos, modos de operação | Excessivamente longo (1071 linhas); §6.1 e §6.4 deprecated in-place; §21 duplica CLAUDE.md §7 inteiramente (~242 linhas redundantes); §2C duplica lista de módulos já em CLAUDE.md §2 e LAYOUT §2 |
| `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | Governança central — leitura condicional | Listado diretamente | Layout de filesystem, taxonomia de módulos, naming, soberania por superfície | Bem estruturado; §1A já foi esvaziado (redirect para OPERATIONS.md); tem seções duplicando conteúdo de OPERATIONS.md §1; módulo lista duplicada em 4 locais |
| `docs/_canon/OPERATIONS.md` | Canon global — leitura condicional | Listado diretamente | Referência operacional condensada: soberania, boundaries, precedência, artefatos obrigatórios, validação, naming | Arquivo bem-sucedido da auditoria anterior; alta densidade; porém ainda carregado em TODOS os task_types (overhead) |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Canon global — leitura condicional | Listado diretamente | Backlog de decisões arquiteturais | Todas as decisões resolvidas; §2 diz "não há decisões abertas"; arquivo carregado para leitura, mas atualmente vazio de bloqueios |
| `docs/_canon/MODULE_REGISTRY.yaml` | Canon global — gate_only na prática | Listado diretamente | Status operacional dos 16 módulos, superfícies esperadas | Correto e conciso; usado pelo pipeline e por F1.1; deveria ser gate_only |
| `docs/_canon/DATA_CONVENTIONS.md` | Canon global — leitura condicional | Listado diretamente | Identificadores, datas, naming, nulos, enums, soft delete, campos comuns | Denso e completo; alta qualidade; cross-referencia api_rules.yaml corretamente |
| `docs/_canon/ERROR_MODEL.md` | Canon global — ponteiro | Listado diretamente | Modelo de erros HTTP (Problem+JSON) | 25 linhas apenas; é puro ponteiro para SSOT em api_rules.yaml e DOMAIN_AXIOMS.json; contribuição líquida muito baixa |
| `docs/_canon/SECURITY_RULES.md` | Canon global — leitura condicional | Listado diretamente | Regras transversais de segurança, áreas, perfis base, ADRs normativas | Conciso mas aponta para ADRs; boa estrutura; redundância com CLAUDE.md §4 (RBAC roles) |
| `docs/_canon/SYSTEM_SCOPE.md` | Canon global — leitura condicional | Listado diretamente | Missão, stack, mercado, atores, macrodomínios, fora de escopo, dependências, riscos | Bom conteúdo; atores/roles duplicam CLAUDE.md e SECURITY_RULES.md |
| `docs/_canon/CONTRACT_PIPELINE.md` | Canon global — leitura condicional | Listado diretamente | Estágios oficiais do pipeline, regras de transição, papel do prompt | 4 referências a BOOT_PROFILES.md (arquivo deletado — link morto crítico) |
| `docs/_canon/DECISION_POLICY.md` | Canon global — leitura condicional | Listado diretamente | Regras do DSS, quando Decision Discovery é obrigatório, checklist de lacunas, fluxo de promoção | Bem estruturado; checklist de §4 já está parcialmente obsoleta (items resolvidos via ADRs) |
| `docs/_canon/CODE_ARCHITECTURE.md` | Canon global — leitura condicional | Listado diretamente | Stack, Clean Architecture, organização de pastas, nomenclatura, regras de geração | Conciso e preciso; usado apenas por generate_code e generate_frontend |
| `docs/_canon/UI_FOUNDATIONS.md` | Canon global — leitura condicional | Listado diretamente | Princípios de UI, estados globais, responsividade, acessibilidade | 41 linhas; muito raso para ser arquivo separado; fusível com DESIGN_SYSTEM.md |
| `docs/_canon/DESIGN_SYSTEM.md` | Canon global — leitura condicional | Listado diretamente | Tokens de design, componentes base, regras | 43 linhas; muito raso; fusível com UI_FOUNDATIONS.md |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | Canon global — leitura condicional com gatilho | Listado diretamente | Regras IHF documentadas (HBR-001 a HBR-014), módulos handball-sensíveis | Alta qualidade; carregamento correto por gatilho; ~298 linhas |
| `docs/_canon/API_CONVENTIONS.md` | Canon global — ponteiro puro | Listado diretamente | Aponta para api_rules.yaml como SSOT | 51 linhas; puro ponteiro; contribuição líquida quase zero |
| `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md` | Prompt operacional | Listado diretamente | Ponto de entrada obrigatório para todas as tarefas | Bem executado pós-auditoria; correto e conciso (139 linhas) |
| `.contract_driven/agent_prompts/create_openapi_contract.prompt.md` | Prompt operacional | Listado diretamente | Criar/atualizar contratos OpenAPI | Hardcoded para módulo TRAINING; deveria ser genérico |
| `.contract_driven/agent_prompts/create_module_docs.prompt.md` | Prompt operacional | Listado diretamente | Criar docs mínimas de módulo | Hardcoded para módulo training; deveria ser genérico |
| `.contract_driven/agent_prompts/create_asyncapi_contract.prompt.md` | Prompt operacional | Listado diretamente | Criar contratos AsyncAPI | Referencia BOOT_PROFILES.md (arquivo deletado — link morto) |
| `.contract_driven/agent_prompts/create_arazzo_workflow.prompt.md` | Prompt operacional | Listado diretamente | Criar workflows Arazzo | Conciso; usa código de bloqueio não canônico (BLOCKED_ARAZZO_OPENAPI_LINK_MISSING) |
| `.contract_driven/agent_prompts/create_json_schema_contract.prompt.md` | Prompt operacional | Listado diretamente | Criar contratos JSON Schema | Usa código de bloqueio não canônico (BLOCKED_FORMAT_VIOLATION) |
| `.contract_driven/agent_prompts/create_state_model.prompt.md` | Prompt operacional | Listado diretamente | Criar STATE_MODEL de módulo | Correto e conciso |
| `.contract_driven/agent_prompts/create_ui_contract.prompt.md` | Prompt operacional | Listado diretamente | Criar UI_CONTRACT de módulo | Correto e conciso |
| `.contract_driven/agent_prompts/decision_discovery.prompt.md` | Prompt operacional | Listado diretamente | Executar estágio Decision Discovery | Bem estruturado; redundante com create_asyncapi em leitura mínima |
| `.contract_driven/agent_prompts/adversarial_analysis.prompt.md` | Prompt operacional | Listado diretamente | Análise adversarial (OWASP, STRIDE, Consumer Break, Domain Gap) | Alta qualidade; referencia HUMAN_INTERFACE_POLICY.md (arquivo não listado no boot) |
| `.contract_driven/agent_prompts/generate_code.prompt.md` | Prompt operacional | Listado diretamente | Geração de código backend (Clean Architecture) | Detalhado e determinístico (242 linhas); bom uso de templates inline |
| `.contract_driven/agent_prompts/generate_frontend.prompt.md` | Prompt operacional | Listado diretamente | Geração de código frontend (React/TS) | Detalhado e determinístico (235 linhas); bem estruturado |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | Registry — gate_only | Listado diretamente | Registro machine-readable dos 25+ gates de validação | Correto; referencia BOOT_PROFILES.md (link morto); gate_only conforme política |
| `.contract_driven/DOMAIN_AXIOMS.json` | Registry — gate_only / validação | Listado diretamente | Invariantes machine-readable globais | Correto; 809 linhas; consumido por ferramentas, não pelo agente diretamente |
| `.contract_driven/templates/api/api_rules.yaml` | SSOT — leitura condicional | Listado diretamente | Regras, templates e validações de API HTTP; resolução de conflitos entre fontes | Alta qualidade; 1042 linhas; SSOT real para design de API |
| `_reports/contract_gates/latest.json` | Derivado — gate_only | Listado diretamente | Estado atual dos gates CI | Derivado; DEGRADED (ferramentas ausentes: oasdiff, schemathesis); não lido pelo agente |
| `docs/_canon/HUMAN_INTERFACE_POLICY.md` | Canon global — não listado no boot | Descoberto via referência em adversarial_analysis.prompt.md | Regras de comunicação R1-R5, formatos de decisão e progresso | Duplica integralmente CLAUDE.md §6; existência separada é redundância pura |

**Total de arquivos no escopo auditado: 35**

- Diretos (listados explicitamente): 34
- Indiretos (descobertos por referência): 1 (HUMAN_INTERFACE_POLICY.md)
- Centrais (boot permanente ou referenciados em 5+ arquivos): 6 (CLAUDE.md, CONTRACT_SYSTEM_RULES.md, OPERATIONS.md, api_rules.yaml, DOMAIN_AXIOMS.json, MODULE_REGISTRY.yaml)
- Acessórios (ponteiros, derivados, gate_only): 8 (ERROR_MODEL.md, API_CONVENTIONS.md, HUMAN_INTERFACE_POLICY.md, GATES_REGISTRY.yaml, latest.json, SESSION_HANDOFF.md, UI_FOUNDATIONS.md, DESIGN_SYSTEM.md)

---

## PARTE 2 — SCORECARD POR ARQUIVO

| Arquivo | Qualidade | Determinismo | Eficiência de contexto | Necessidade real | Sobreposição | Contribuição líquida | Decisão principal |
|---------|-----------|--------------|------------------------|------------------|--------------|----------------------|-------------------|
| `CLAUDE.md` | 88 | 90 | 72 | 100 | 45 | Alta | condensar |
| `SESSION_HANDOFF.md` | 95 | 95 | 95 | 90 | 5 | Alta | manter |
| `CONTRACT_SYSTEM_RULES.md` | 75 | 80 | 28 | 85 | 60 | Média | condensar |
| `CONTRACT_SYSTEM_LAYOUT.md` | 80 | 85 | 55 | 80 | 50 | Média | condensar |
| `OPERATIONS.md` | 92 | 90 | 88 | 85 | 30 | Alta | manter |
| `ARCHITECTURE_DECISION_BACKLOG.md` | 85 | 90 | 60 | 70 | 15 | Média | mover para leitura condicional |
| `MODULE_REGISTRY.yaml` | 90 | 95 | 90 | 95 | 10 | Alta | mover para gate_only |
| `DATA_CONVENTIONS.md` | 88 | 88 | 75 | 85 | 20 | Alta | manter |
| `ERROR_MODEL.md` | 60 | 70 | 30 | 30 | 80 | Baixa | fundir |
| `SECURITY_RULES.md` | 82 | 82 | 75 | 80 | 25 | Média | manter |
| `SYSTEM_SCOPE.md` | 85 | 80 | 72 | 80 | 30 | Média | condensar |
| `CONTRACT_PIPELINE.md` | 78 | 82 | 60 | 75 | 35 | Média | condensar |
| `DECISION_POLICY.md` | 88 | 90 | 72 | 80 | 20 | Média | manter |
| `CODE_ARCHITECTURE.md` | 90 | 92 | 88 | 85 | 10 | Alta | manter |
| `UI_FOUNDATIONS.md` | 65 | 70 | 40 | 50 | 70 | Baixa | fundir |
| `DESIGN_SYSTEM.md` | 65 | 70 | 40 | 50 | 70 | Baixa | fundir |
| `HANDBALL_RULES_DOMAIN.md` | 92 | 95 | 85 | 90 | 5 | Alta | manter |
| `API_CONVENTIONS.md` | 55 | 60 | 20 | 20 | 90 | Muito baixa | excluir |
| `pre_contract_orchestrator.prompt.md` | 92 | 90 | 88 | 100 | 10 | Alta | manter |
| `create_openapi_contract.prompt.md` | 72 | 78 | 70 | 90 | 15 | Média | condensar |
| `create_module_docs.prompt.md` | 68 | 75 | 65 | 85 | 15 | Média | condensar |
| `create_asyncapi_contract.prompt.md` | 55 | 60 | 65 | 80 | 20 | Baixa | condensar |
| `create_arazzo_workflow.prompt.md` | 60 | 60 | 70 | 80 | 15 | Média | condensar |
| `create_json_schema_contract.prompt.md` | 60 | 60 | 70 | 80 | 15 | Média | condensar |
| `create_state_model.prompt.md` | 82 | 85 | 80 | 85 | 10 | Alta | manter |
| `create_ui_contract.prompt.md` | 80 | 82 | 78 | 85 | 10 | Alta | manter |
| `decision_discovery.prompt.md` | 88 | 88 | 82 | 90 | 15 | Alta | manter |
| `adversarial_analysis.prompt.md` | 90 | 90 | 78 | 90 | 10 | Alta | manter |
| `generate_code.prompt.md` | 92 | 93 | 82 | 90 | 5 | Alta | manter |
| `generate_frontend.prompt.md` | 90 | 92 | 82 | 85 | 5 | Alta | manter |
| `GATES_REGISTRY.yaml` | 88 | 95 | 85 | 90 | 15 | Alta | mover para gate_only |
| `DOMAIN_AXIOMS.json` | 95 | 98 | 92 | 95 | 5 | Alta | mover para gate_only |
| `api_rules.yaml` | 92 | 95 | 80 | 95 | 15 | Alta | manter |
| `_reports/contract_gates/latest.json` | 80 | 95 | 85 | 75 | 0 | Média | mover para gate_only |
| `HUMAN_INTERFACE_POLICY.md` | 85 | 88 | 10 | 0 | 100 | Nenhuma | excluir |

---

## PARTE 3 — DIAGNÓSTICO POR ARQUIVO

### Arquivo: CLAUDE.md

Função real: Boot permanente de identidade do agente. Define o que o agente é, quais módulos existem, quais task_types são válidos, como comunicar com o humano, e quais arquivos carregar por task_type.

Problemas encontrados:
- §2 (lista de 16 módulos) duplica CONTRACT_SYSTEM_LAYOUT.md §2 e CONTRACT_SYSTEM_RULES.md §2C
- §6 (regras R1-R5 e formatos) duplica integralmente HUMAN_INTERFACE_POLICY.md
- §8 (paths críticos) parcialmente sobrepõe OPERATIONS.md e LAYOUT §4A
- A referência em §4 a CONTRACT_SYSTEM_RULES.md §9 para critério completo de bloqueios cria dependência implícita de leitura não classificada no §7

Bloqueadores principais:
- Duplicação com HUMAN_INTERFACE_POLICY.md: CLAUDE.md §6 é a versão canônica — HUMAN_INTERFACE_POLICY.md pode ser eliminado
- Duplicação da lista de módulos em 3-4 locais: uma mudança de módulo exige atualização síncrona em múltiplos arquivos

Decisão: condensar
Justificativa: Manter como boot permanente, mas remover §8 (paths críticos já estão em OPERATIONS.md), consolidar referência a bloqueios de forma mais compacta.

Impacto esperado:
- tokens: −150 (remoção de §8 e compactação de §4)
- contexto: −leve
- qualidade: neutro
- determinismo: sobe (única lista de módulos)

Arquivos relacionados para consolidação: HUMAN_INTERFACE_POLICY.md (eliminar; conteúdo já está em CLAUDE.md §6)

---

### Arquivo: SESSION_HANDOFF.md

Função real: Estado inter-sessão: o que foi feito, o que está pendente, bloqueios ativos, ADRs recentes.

Problemas encontrados:
- Nenhum estrutural; o arquivo é curto e bem-formatado

Bloqueadores principais: nenhum

Decisão: manter
Justificativa: Padrão correto; tamanho adequado; lido primeiro em cada sessão conforme §5.

Impacto esperado: neutro em todos os vetores

---

### Arquivo: CONTRACT_SYSTEM_RULES.md

Função real: Regras operacionais vinculantes para criação, validação e consumo de contratos. Hierarquia de precedência, bloqueios, DoD, modos de operação.

Problemas encontrados:
- §6.1 e §6.4: seções deprecated in-place mas presentes — consomem ~24 linhas de contexto morto
- §2C: duplica lista de 16 módulos já em CLAUDE.md §2 e LAYOUT §2.1
- §21 (Matriz mínima de boot por tipo de tarefa): ~242 linhas que duplicam explicitamente CLAUDE.md §7; o próprio §21 declara "fonte autoritativa: CLAUDE.md §7"
- §7 (regra Diátaxis): 13 linhas com valor marginal; não operacional
- §9 tem dois sistemas de bloqueios: os 4 promovidos para CLAUDE.md §4 (marcados com `[→ CLAUDE.md §4]`) e os restantes — split confuso
- Tamanho total de 1071 linhas para um arquivo que deve ser "lido on-demand" é excesso estrutural

Bloqueadores principais:
- §21 é a maior fonte de redundância do sistema: 242 linhas duplicando CLAUDE.md §7
- Seções deprecated adicionam ruído sem valor
- Tamanho torna leitura on-demand ineficiente

Decisão: condensar
Justificativa: Remover §21 inteiramente (CLAUDE.md §7 é autoritativo), remover seções deprecated, remover §2C (redirecionar para CLAUDE.md §2), condensar §7.

Impacto esperado:
- tokens: −280 (§21 ~242 + deprecated ~24 + §2C ~15)
- contexto: −alto
- qualidade: sobe (menos ruído, fonte única para boot profiles)
- determinismo: sobe (remove duplicata com possibilidade de drift)

Arquivos relacionados: CLAUDE.md §7 (fonte autoritativa para §21)

---

### Arquivo: CONTRACT_SYSTEM_LAYOUT.md

Função real: Layout canônico de filesystem para contratos: onde criar artefatos, naming, soberania por superfície.

Problemas encontrados:
- §1A foi esvaziado (redireciona para OPERATIONS.md §1) — seção fantasma
- §2 duplica lista de módulos de CLAUDE.md §2 e RULES §2C
- §5 (soberania por camada) tem overlap significativo com OPERATIONS.md §1
- §15 (regras estruturais) e §14 (DoD estrutural) têm valor marginal — repetem conclusões de seções anteriores
- Tamanho de 510 linhas para um arquivo cujo uso principal é "onde criar o arquivo" é excessivo

Bloqueadores principais:
- Duplicação da lista de módulos aumenta risco de drift
- §5 e OPERATIONS.md §1 dizem coisas similares sobre soberania

Decisão: condensar
Justificativa: Manter como referência de filesystem/naming, mas remover §14 e §15 (cobertos pelo DoD em RULES §16/17), remover §2 (redirecionar para CLAUDE.md §2), consolidar §5 com ponteiro para OPERATIONS.md §1.

Impacto esperado:
- tokens: −80
- contexto: −médio
- qualidade: neutro
- determinismo: sobe

---

### Arquivo: OPERATIONS.md

Função real: Referência operacional condensada em tabelas: soberania, boundaries de módulos, precedência, artefatos obrigatórios, validação, naming.

Problemas encontrados:
- Carregado em todos os 12 task_types (via `OPER` em CLAUDE.md §7) — overhead desnecessário para task_types como new_state_model, create_asyncapi onde boundary rules de módulo raramente são consultadas
- §3 é redirect para RULES.md §5 com duplicação parcial da hierarquia
- Qualidade alta; conteúdo denso e correto

Bloqueadores principais:
- Overhead de carregamento universal (110 linhas em todos os boots)

Decisão: manter
Justificativa: O arquivo é o ponto de equilíbrio correto entre densidade e acessibilidade. Reduzir o carregamento universal seria mais impactante que remover conteúdo.

Impacto esperado:
- tokens: −1100 se removido do boot de 5-6 task_types onde seu uso é raro
- contexto: −médio
- qualidade: neutro
- determinismo: neutro

---

### Arquivo: ARCHITECTURE_DECISION_BACKLOG.md

Função real: Backlog de decisões arquiteturais não-resolvidas. Aciona Decision Discovery quando há entradas `obrigatória + open`.

Problemas encontrados:
- §2 declara explicitamente que não há decisões abertas no momento
- Arquivo é carregado pelo orchestrator (F1.2) para filtrar entradas — mas está vazio de bloqueios
- §2 ainda lista as 11 entradas ARCH-001 a ARCH-011 com status `resolved`, consumindo ~185 linhas de contexto histórico sem valor operacional imediato

Bloqueadores principais:
- 185 linhas de histórico de decisões resolvidas não agregam valor quando o agente só precisa verificar "há entradas obrigatória+open?"

Decisão: mover para leitura condicional
Justificativa: Já é carregado condicionalmente (apenas por architecture_review e F1.2 no orchestrator). A questão é que o arquivo carrega histórico desnecessário. Decisões resolvidas devem ser mantidas apenas como referência soberana leve.

Impacto esperado:
- tokens: neutro (já condicional); −100 se histórico for movido para arquivo separado
- contexto: neutro
- qualidade: neutro
- determinismo: neutro

---

### Arquivo: MODULE_REGISTRY.yaml

Função real: Declarar status operacional, owner e superfícies esperadas de cada módulo.

Problemas encontrados:
- Consumido principalmente por ferramentas (validate_contracts.py, gates) e pelo orchestrator (F1.1)
- Listado no boot de architecture_review e contract_revision mas lido principalmente por código, não por raciocínio do agente

Bloqueadores principais: nenhum estrutural

Decisão: mover para gate_only
Justificativa: O agente raramente precisa ler este arquivo diretamente; é o pipeline que o consome. O orchestrator pode verificar status via tool call ao invés de carregar o arquivo no contexto.

Impacto esperado:
- tokens: −107 por sessão onde não for necessária leitura direta
- contexto: −leve
- qualidade: neutro
- determinismo: neutro

---

### Arquivo: DATA_CONVENTIONS.md

Função real: Convenções canônicas de dados: IDs, datas, naming, nulos, enums, soft delete, campos comuns.

Problemas encontrados:
- §3.1 aponta `api_rules.yaml` como SSOT para campos JSON — redundância parcial
- Alguns exemplos SQL (§7.4) são para implementação, não para design de contrato — conteúdo adjacente
- Alta qualidade geral; sem problemas estruturais graves

Decisão: manter
Justificativa: Conteúdo denso e necessário para new_contract, contract_revision, new_schema.

Impacto esperado: neutro

---

### Arquivo: ERROR_MODEL.md

Função real: Padronizar o modelo de erros HTTP usando Problem+JSON.

Problemas encontrados:
- 25 linhas no total: introdução, ponteiro para DOMAIN_AXIOMS.json, ponteiro para api_rules.yaml, ponteiro para o schema OpenAPI
- É puramente um ponteiro — não contém regras, apenas redireciona para 3 outras fontes
- A informação essencial (media type `application/problem+json`) poderia estar em OPERATIONS.md §5 ou em api_rules.yaml

Bloqueadores principais:
- Arquivo de 25 linhas com zero conteúdo próprio — overhead de carregamento maior que o valor entregue

Decisão: fundir
Justificativa: Os 3 ponteiros podem ser absorbed em OPERATIONS.md §5 como uma nota de 2 linhas.

Impacto esperado:
- tokens: −25 por eliminação do arquivo; +5 em OPERATIONS.md
- contexto: −leve
- qualidade: neutro
- determinismo: sobe (menos arquivos a navegar)

Arquivos relacionados para consolidação: OPERATIONS.md §5

---

### Arquivo: SECURITY_RULES.md

Função real: Regras transversais de segurança, áreas, perfis base, referências a ADRs normativas.

Problemas encontrados:
- Perfis base (admin, coordenador, treinador, etc.) duplicam SYSTEM_SCOPE.md §4 (Atores Canônicos)
- Referências às ADRs (007-013) são o conteúdo mais valioso — regras textuais são cobertas pelos próprios ADRs

Decisão: manter
Justificativa: Serve como entrada para adversarial_analysis e contract_revision; sem ele o agente precisaria ler múltiplos ADRs para encontrar as mesmas referências.

Impacto esperado: neutro

---

### Arquivo: SYSTEM_SCOPE.md

Função real: Escopo do sistema: missão, tipo, mercado, atores, macrodomínios, exclusões, dependências, riscos, princípios.

Problemas encontrados:
- §4 (Atores Canônicos / RBAC roles) duplica SECURITY_RULES.md §Perfis Base e parcialmente CODE_ARCHITECTURE.md
- §9 (Decisões em Aberto sobre versioning e broker) está desatualizado — ADR-003 e ADR-014 resolveram versioning; a questão do broker é deployment, não escopo
- §5 (macrodomínios) tem sobreposição conceitual com MODULE_MAP.md (não auditado aqui)

Decisão: condensar
Justificativa: Remover §9 (desatualizado), remover duplicação de RBAC roles (redirect para SECURITY_RULES.md §Perfis Base).

Impacto esperado:
- tokens: −25
- contexto: −leve
- qualidade: sobe (remove conteúdo desatualizado)
- determinismo: sobe

---

### Arquivo: CONTRACT_PIPELINE.md

Função real: Estágios oficiais do pipeline CDD, regras de transição, canonização de melhorias.

Problemas encontrados:
- 4 referências a `docs/_canon/BOOT_PROFILES.md` (arquivo deletado): links mortos críticos
- §4 instrui "classificar a leitura em BOOT_PROFILES.md" — deve apontar para CLAUDE.md §7
- §5 (papel do prompt) instrui "carregar artefatos exigidos por BOOT_PROFILES.md" — link morto
- Tabela de estágios (§2) também referencia BOOT_PROFILES como autoridade do estágio Pre-contract

Bloqueadores principais:
- 4 referências a arquivo deletado BOOT_PROFILES.md = risco de confusão em agente ou humano que lê este arquivo

Decisão: condensar
Justificativa: Substituir todas as 4 referências a BOOT_PROFILES.md por CLAUDE.md §7.

Impacto esperado:
- tokens: neutro (troca de referências)
- contexto: neutro
- qualidade: sobe (remove links mortos)
- determinismo: sobe (referência correta para boot profiles)

Arquivos relacionados: CLAUDE.md §7 (substitui BOOT_PROFILES.md em todas as referências)

---

### Arquivo: DECISION_POLICY.md

Função real: Regras do Decision Support System: quando Decision Discovery é obrigatório, estrutura de proposta DSS, fluxo de promoção para ADR.

Problemas encontrados:
- §4 (Checklist Mínima de Lacunas): todos os 12 tópicos listados já têm ADR aprovada (ver ARCHITECTURE_DECISION_BACKLOG.md §3); a checklist está factualmente resolvida para o estado atual
- §1 (Princípio Fundamental) repete a regra de "não inferir silenciosamente" já presente em RULES.md §8 e CLAUDE.md §5

Decisão: manter
Justificativa: Arquivo essencial para Decision Discovery. A checklist, mesmo estando "resolvida", serve como evidência de conformidade ao verificar novos contratos.

Impacto esperado: neutro

---

### Arquivo: CODE_ARCHITECTURE.md

Função real: Stack tecnológica, Clean Architecture, organização de pastas, nomenclatura, regras de geração.

Problemas encontrados:
- §7 (gate CODE_ARCHITECTURE_GATE) duplica conteúdo já em GATES_REGISTRY.yaml
- Conteúdo de código Python/YAML inline é necessário para generate_code — bem executado

Decisão: manter
Justificativa: Alta densidade instrucional para generate_code e generate_frontend.

Impacto esperado: neutro

---

### Arquivo: UI_FOUNDATIONS.md

Função real: Fundamentos transversais de UI: princípios, estados globais, responsividade, acessibilidade.

Problemas encontrados:
- 41 linhas; conteúdo é uma lista de tópicos sem regras específicas acionáveis
- Não referencia tokens de design, não tem exemplos, não tem critérios verificáveis
- Fusível com DESIGN_SYSTEM.md sem perda de qualidade

Bloqueadores principais:
- Overhead de um arquivo separado para 41 linhas de conteúdo que poderia estar em 10 linhas no topo do DESIGN_SYSTEM.md

Decisão: fundir
Justificativa: Combinar em `UI_CONTRACT_GUIDE.md` com DESIGN_SYSTEM.md.

Impacto esperado:
- tokens: −20 (overhead de separação eliminado)
- contexto: −leve
- qualidade: neutro
- determinismo: neutro

Arquivos relacionados: DESIGN_SYSTEM.md

---

### Arquivo: DESIGN_SYSTEM.md

Função real: Tokens de design, componentes base, regras de composição.

Problemas encontrados:
- 43 linhas; listas de tokens e componentes sem valores concretos (valores vivem em codebase, não no doc)
- Regras seção apenas tem 4 regras genéricas
- Fusível com UI_FOUNDATIONS.md

Decisão: fundir
Justificativa: Combinar com UI_FOUNDATIONS.md em arquivo único `UI_CONTRACT_GUIDE.md`.

Impacto esperado:
- tokens: −15
- contexto: −leve
- qualidade: neutro
- determinismo: neutro

Arquivos relacionados: UI_FOUNDATIONS.md

---

### Arquivo: HANDBALL_RULES_DOMAIN.md

Função real: Regras IHF documentadas (HBR-001 a HBR-014) com impacto e restrições de implementação.

Problemas encontrados:
- Alta qualidade; carregado apenas por gatilho esportivo (correto)
- Seção §2 (Regra Cardinal para Agentes) é a mais crítica — bem posicionada
- Nenhum problema estrutural

Decisão: manter
Justificativa: Arquivo soberano insubstituível para domínio esportivo.

Impacto esperado: neutro

---

### Arquivo: API_CONVENTIONS.md

Função real: Apontar para api_rules.yaml como SSOT de convenções de API.

Problemas encontrados:
- 51 linhas; 100% são ponteiros e disclaimers de que este arquivo não é a SSOT
- O §5 "Registry legado" reapresenta informação já em api_rules.yaml
- A §2 (Ordem de Leitura para APIs) duplica o procedimento do prompt create_openapi_contract.prompt.md
- Não há nenhuma regra aqui que não esteja melhor documentada em outro lugar

Bloqueadores principais:
- Existência deste arquivo cria confusão: agentes ou humanos novos podem ler aqui esperando encontrar regras de API e encontrar apenas redirects

Decisão: excluir
Justificativa: Todo conteúdo é ponteiro para api_rules.yaml. A referência a api_rules.yaml pode ser feita diretamente de OPERATIONS.md §5 e dos prompts que a referenciam.

Impacto esperado:
- tokens: −51 por eliminação
- contexto: −leve
- qualidade: sobe (menos confusão sobre onde estão as regras de API)
- determinismo: sobe

---

### Arquivo: pre_contract_orchestrator.prompt.md

Função real: Ponto de entrada obrigatório para toda tarefa de contratos (4 fases + observabilidade).

Problemas encontrados:
- Referência a `docs/_canon/templates/SESSION_HANDOFF.template.md` — template não foi listado no escopo e pode não existir
- Qualidade geral alta após reescrita da sessão anterior

Decisão: manter
Justificativa: Arquivo correto e bem executado.

---

### Arquivo: create_openapi_contract.prompt.md

Função real: Criar ou atualizar contratos OpenAPI de módulo.

Problemas encontrados:
- Hardcoded para módulo TRAINING em múltiplos lugares ("TRAINING.yaml", "module=TRAINING"): prompt deveria usar placeholder `<MODULE>`
- §Leitura mínima lista `MODULE_PROFILE_REGISTRY.yaml` — arquivo não presente no escopo auditado e não referenciado em CLAUDE.md §8 ou OPERATIONS.md
- Referencia `generated/resolved_policy/TRAINING.sync.resolved.yaml` (hardcoded ao invés de template)

Bloqueadores principais:
- Hardcoding para TRAINING reduz utilidade para outros módulos; agente pode confundir-se ao adaptar

Decisão: condensar
Justificativa: Substituir todas as instâncias de "TRAINING" por `<MODULE>` placeholder.

Impacto esperado:
- tokens: neutro
- contexto: neutro
- qualidade: sobe (genérico para todos os módulos)
- determinismo: sobe

---

### Arquivo: create_module_docs.prompt.md

Função real: Criar conjunto mínimo de documentação normativa de módulo.

Problemas encontrados:
- Hardcoded para módulo `training` em paths e nomes de arquivo ("training/MODULE_SCOPE_TRAINING.md")
- Linha 22: dupla barra `training//MODULE_SCOPE_TRAINING.md` (bug de path)

Bloqueadores principais:
- Bug de path na linha 22 pode causar artefato em path errado

Decisão: condensar
Justificativa: Corrigir bug de path, substituir hardcoding por `<MODULE>` placeholder.

Impacto esperado:
- tokens: neutro
- qualidade: sobe (corrige bug)
- determinismo: sobe

---

### Arquivo: create_asyncapi_contract.prompt.md

Função real: Criar contratos AsyncAPI de módulo.

Problemas encontrados:
- Linha 8: referencia `docs/_canon/BOOT_PROFILES.md` (arquivo deletado — link morto)
- Conteúdo muito escasso (20 linhas) para uma operação que exige verificação de múltiplos artefatos

Bloqueadores principais:
- Link morto para BOOT_PROFILES.md pode fazer agente buscar arquivo inexistente

Decisão: condensar
Justificativa: Substituir referência a BOOT_PROFILES.md por CLAUDE.md §7; expandir leitura mínima com artefatos corretos.

Impacto esperado:
- tokens: neutro
- qualidade: sobe (corrige link morto)
- determinismo: sobe

---

### Arquivo: create_arazzo_workflow.prompt.md

Função real: Criar workflows Arazzo de módulo.

Problemas encontrados:
- Usa bloqueio `BLOCKED_ARAZZO_OPENAPI_LINK_MISSING` — código não está em CLAUDE.md §4 nem em RULES.md §9
- Conteúdo muito escasso (19 linhas) — sem guidance sobre critérios de "multi-step real"

Bloqueadores principais:
- Código de bloqueio não canônico reduz determinismo (agente pode não saber como emitir esse código)

Decisão: condensar
Justificativa: Substituir bloqueio não canônico por `BLOCKED_MISSING_OPENAPI_PATH` (já em CLAUDE.md §4); adicionar critério de "multi-step obrigatório" de RULES.md §11.6.

Impacto esperado:
- tokens: neutro
- qualidade: neutro
- determinismo: sobe

---

### Arquivo: create_json_schema_contract.prompt.md

Função real: Criar schemas JSON soberanos de módulo.

Problemas encontrados:
- Usa bloqueio `BLOCKED_FORMAT_VIOLATION` — código não está em CLAUDE.md §4 nem em RULES.md §9

Decisão: condensar
Justificativa: Substituir por `BLOCKED_SCHEMA_DRIFT` ou `BLOCKED_MISSING_SCHEMA` (ambos canônicos).

Impacto esperado:
- tokens: neutro
- determinismo: sobe

---

### Arquivo: create_state_model.prompt.md

Função real: Criar STATE_MODEL de módulo com FSM, estados e transições.

Problemas encontrados:
- Nenhum problema estrutural

Decisão: manter

---

### Arquivo: create_ui_contract.prompt.md

Função real: Criar UI_CONTRACT e SCREEN_MAP de módulo.

Problemas encontrados:
- Nenhum problema estrutural

Decisão: manter

---

### Arquivo: decision_discovery.prompt.md

Função real: Executar o estágio Decision Discovery antes de contract_creation ou contract_revision.

Problemas encontrados:
- Leitura mínima lista `docs/_canon/ARCHITECTURE.md` (arquivo não no escopo auditado, mas existente) como obrigatória sem constar no boot profile de CLAUDE.md §7 para architecture_review

Decisão: manter
Justificativa: Alta qualidade; único problema é leitura não classificada no boot profile.

---

### Arquivo: adversarial_analysis.prompt.md

Função real: Análise de riscos em 4 dimensões (OWASP, STRIDE, Consumer Break, Domain Gap) antes do handoff.

Problemas encontrados:
- Linha 169 referencia `HUMAN_INTERFACE_POLICY R4` — referência a arquivo que duplica CLAUDE.md §6 e que deveria ser eliminado
- AA9 (Logging Failures) referencia `docs/_canon/AUDIT_LOG_POLICY.md` — arquivo não presente no escopo auditado

Decisão: manter
Justificativa: Alta qualidade instrucional. Corrigir referência a HUMAN_INTERFACE_POLICY para CLAUDE.md §6.

---

### Arquivo: generate_code.prompt.md

Função real: Geração de código backend em 6 fases (Domain, Application, Infrastructure, Interface, Tests).

Problemas encontrados:
- Templates Python inline ocupam ~120 linhas; bem justificados por determinismo
- Referencia `FEATURE_REGISTRY.yaml` como pré-requisito — arquivo existente mas não no boot profile de CLAUDE.md §7 para generate_code

Decisão: manter

---

### Arquivo: generate_frontend.prompt.md

Função real: Geração de código frontend React em 7 fases.

Problemas encontrados:
- Referencia `FRONTEND_CONTRACT.md` como pré-requisito — arquivo existente (listado na diretório) mas não auditado
- Templates TypeScript inline bem justificados

Decisão: manter

---

### Arquivo: GATES_REGISTRY.yaml

Função real: Registry machine-readable dos ~25 gates de validação do pipeline.

Problemas encontrados:
- Linha 16: `boot_profiles_ref: "docs/_canon/BOOT_PROFILES.md"` — referência a arquivo deletado

Decisão: mover para gate_only
Justificativa: Já classificado como gate_only em CLAUDE.md. Corrigir referência a BOOT_PROFILES.md.

Impacto esperado:
- tokens: neutro
- qualidade: sobe (corrige link morto)
- determinismo: sobe

---

### Arquivo: DOMAIN_AXIOMS.json

Função real: Invariantes machine-readable globais. Consumido por ferramentas de validação, não pelo agente diretamente.

Problemas encontrados:
- CLAUDE.md §7 indica que não deve ser lido diretamente pelo agente
- Corretamente posicionado como gate_only na política

Decisão: mover para gate_only
Justificativa: Já está na posição certa; apenas confirmar que nenhum boot profile o carrega como leitura direta.

---

### Arquivo: api_rules.yaml

Função real: SSOT de convenções, validações e templates de API HTTP. Resolução de conflitos entre fontes externas.

Problemas encontrados:
- 1042 linhas; denso mas bem estruturado
- Carregado por create_openapi_contract — correto
- Não listado explicitamente no boot profile de CLAUDE.md §7 para new_contract (apenas implicitamente via RULES §3B)

Bloqueadores principais:
- Boot profile de `new_contract` lista DATA_CONV, ERR, SEC, MDOCS — mas não api_rules.yaml explicitamente para tarefas de contrato HTTP

Decisão: manter
Justificativa: Arquivo correto; adicionar referência explícita em CLAUDE.md §7 para new_contract e contract_revision.

---

### Arquivo: _reports/contract_gates/latest.json

Função real: Evidência CI do estado atual dos gates.

Problemas encontrados:
- DEGRADED: oasdiff e schemathesis ausentes do ambiente
- Arquivo derivado — não deve ser lido pelo agente como fonte substantiva

Decisão: mover para gate_only
Justificativa: Já é derivado por definição; não adicionar ao contexto de agente.

---

### Arquivo: HUMAN_INTERFACE_POLICY.md

Função real: Duplicata de CLAUDE.md §6 — regras R1-R5, vocabulário proibido, formatos de decisão e progresso.

Problemas encontrados:
- 77 linhas de conteúdo 100% presente em CLAUDE.md §6
- Única referência ativa é em adversarial_analysis.prompt.md linha 169
- Não está em nenhum boot profile; não listado em CLAUDE.md §8

Bloqueadores principais:
- Existência cria risco de drift: se CLAUDE.md §6 for atualizado e HUMAN_INTERFACE_POLICY.md não, agente pode receber versão inconsistente se alguém carregar ambos

Decisão: excluir
Justificativa: Zero conteúdo exclusivo. Substituir referência em adversarial_analysis.prompt.md por "CLAUDE.md §6".

Impacto esperado:
- tokens: −77 por eliminação
- qualidade: sobe (remove fonte de drift)
- determinismo: sobe

---

## PARTE 4 — REDUNDÂNCIAS E CONFLITOS

| Regra/conteúdo redundante ou conflitante | Arquivos envolvidos | Tipo de problema | Efeito no agente | Solução recomendada |
|------------------------------------------|---------------------|------------------|------------------|---------------------|
| Lista dos 16 módulos canônicos | CLAUDE.md §2, CONTRACT_SYSTEM_RULES.md §2C, CONTRACT_SYSTEM_LAYOUT.md §2, OPERATIONS.md §2 (módulos com boundaries) | Redundância — 4 cópias | Mudança de módulo exige 4 atualizações síncronas; risco de drift | Manter em CLAUDE.md §2 como SSOT; RULES §2C e LAYOUT §2 devem redirecionar |
| Boot profiles / perfis de leitura por task_type | CLAUDE.md §7 (autoritativo), CONTRACT_SYSTEM_RULES.md §21 (duplicata de 242 linhas), CONTRACT_SYSTEM_RULES.md §6.4 (deprecated) | Redundância crítica — conteúdo idêntico em 3 locais | Agente pode confundir-se se §21 divergir de §7 em detalhe | Remover §21 e §6.4 de RULES.md inteiramente |
| Regras de comunicação R1-R5 e formatos de decisão/progresso | CLAUDE.md §6, HUMAN_INTERFACE_POLICY.md §§2-5 | Redundância total — conteúdo idêntico | Risco de drift entre versões; overhead de contexto | Excluir HUMAN_INTERFACE_POLICY.md; CLAUDE.md §6 permanece |
| Hierarquia de precedência entre arquivos | CONTRACT_SYSTEM_RULES.md §5 (fonte autoritativa), OPERATIONS.md §3 (duplicata parcial com redirect) | Redundância parcial com redirect correto | Aceitável; OPERATIONS.md §3 aponta explicitamente para RULES §5 | Manter como está; OPERATIONS.md §3 é resumo operacional com redirect |
| Modelo de erros HTTP (Problem+JSON) | ERROR_MODEL.md (apenas ponteiros), api_rules.yaml (regras reais), DOMAIN_AXIOMS.json (schema) | Fragmentação — regra em 3 arquivos sem conteúdo próprio no primeiro | Agente precisa abrir 3 arquivos para entender erros | Fundir ERROR_MODEL.md em OPERATIONS.md §5 (2 linhas de ponteiro) |
| Regras de soberania de artefatos | CONTRACT_SYSTEM_LAYOUT.md §5, OPERATIONS.md §1, CONTRACT_SYSTEM_RULES.md §3 | Triplicação parcial | Inconsistência entre versões é possível | OPERATIONS.md §1 é autoritativo (LAYOUT §1A já redireciona); RULES §3 deve redirecionar |
| Referências a BOOT_PROFILES.md (arquivo deletado) | CONTRACT_PIPELINE.md (4 refs), GATES_REGISTRY.yaml (1 ref), create_asyncapi_contract.prompt.md (1 ref), CONTRACT_SYSTEM_LAYOUT.md §4A.2 (1 ref) | Link morto — arquivo deletado na sessão anterior | Qualquer leitura instrucional que encontre estas referências não consegue resolver o arquivo | Substituir todas por referência a CLAUDE.md §7 |
| Atores RBAC / perfis de usuário | SYSTEM_SCOPE.md §4, SECURITY_RULES.md §Perfis Base | Duplicação semântica | Risco de discrepância nos nomes dos roles | Manter em SYSTEM_SCOPE.md §4 como SSOT dos 5 atores; SECURITY_RULES.md redireciona |
| Códigos de bloqueio não canônicos em prompts | create_arazzo_workflow.prompt.md (`BLOCKED_ARAZZO_OPENAPI_LINK_MISSING`), create_json_schema_contract.prompt.md (`BLOCKED_FORMAT_VIOLATION`) | Inconsistência — códigos não declarados em CLAUDE.md §4 ou RULES §9 | Agente emite código desconhecido; receptor não sabe como processar | Substituir por códigos canônicos: `BLOCKED_MISSING_OPENAPI_PATH` e `BLOCKED_MISSING_SCHEMA` |
| Referência a HUMAN_INTERFACE_POLICY.md | adversarial_analysis.prompt.md (linha 169) referencia arquivo que é duplicata de CLAUDE.md §6 | Redundância — arquivo não deveria existir | Nenhum efeito real hoje; risco de drift se o arquivo for atualizado independentemente | Excluir HUMAN_INTERFACE_POLICY.md; atualizar referência no prompt para CLAUDE.md §6 |
| Hardcoding de módulo TRAINING em prompts genéricos | create_openapi_contract.prompt.md (6+ instâncias), create_module_docs.prompt.md (6+ instâncias + bug de path) | Erro estrutural — prompts para todos os módulos estão fixados em TRAINING | Agente pode criar artefatos no path de TRAINING ao usar para outro módulo | Substituir por `<MODULE>` placeholder em todos os prompts afetados |
| §2C de CONTRACT_SYSTEM_RULES.md declara lista de 16 módulos | CONTRACT_SYSTEM_RULES.md §2C, CLAUDE.md §2 | Redundância com risco de drift | Qualquer atualização de módulo exige sincronização | Remover §2C; adicionar redirect para CLAUDE.md §2 |
| Seções deprecated mantidas in-place em RULES.md | CONTRACT_SYSTEM_RULES.md §6.1, §6.4 | Conteúdo morto | Agente lê conteúdo inerte; overhead de contexto | Remover as seções inteiramente (o ponto de deprecação já foi comunicado) |

---

## PARTE 5 — NOVA ARQUITETURA RECOMENDADA

| Arquivo final proposto | Função | Tipo de carregamento | Conteúdo que entra | Conteúdo que sai | Origem dos conteúdos |
|------------------------|--------|----------------------|--------------------|------------------|----------------------|
| `CLAUDE.md` | Boot permanente: identidade, módulos (SSOT única), task_types, bloqueios, árvore de decisão, comunicação, boot profiles | permanente | Lista de módulos como SSOT única; referência a api_rules.yaml no boot de new_contract/contract_revision | §8 (paths críticos — já em OPERATIONS.md); compactação de §4 | CLAUDE.md atual |
| `SESSION_HANDOFF.md` | Estado inter-sessão | permanente (quando existir) | sem mudanças | — | SESSION_HANDOFF.md atual |
| `CONTRACT_SYSTEM_RULES.md` | Regras operacionais vinculantes: soberania, precedência, bloqueios, DoD, modos, procedimentos, Domain Shapes | condicional (contract_revision, generate_code) | — | §21 (242 linhas — duplica CLAUDE.md §7); §6.1 e §6.4 (deprecated); §2C (redirecionar para CLAUDE.md §2); §7 Diátaxis (valor marginal) | CONTRACT_SYSTEM_RULES.md atual com remoções |
| `CONTRACT_SYSTEM_LAYOUT.md` | Layout de filesystem: onde criar artefatos, naming, árvore de contratos | condicional (new_contract, new_schema, new_event, new_workflow) | — | §1A (esvaziado — manter apenas redirect); §14 e §15 (DoD estrutural — absorvido por RULES §16/17); §2 (redirecionar para CLAUDE.md §2) | CONTRACT_SYSTEM_LAYOUT.md atual com remoções |
| `docs/_canon/OPERATIONS.md` | Referência operacional condensada: soberania, boundaries, precedência, artefatos obrigatórios, validação, naming; absorve ERROR_MODEL.md | condicional (maioria dos task_types) | Nota de 2 linhas sobre Problem+JSON (de ERROR_MODEL.md) | — | OPERATIONS.md atual + ERROR_MODEL.md |
| `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md` | Backlog de decisões; decisões resolvidas como histórico compacto | condicional (architecture_review) | — | Pode compactar seção §2 de histórico detalhado (manter apenas tabela §3) | ARCHITECTURE_DECISION_BACKLOG.md com compactação |
| `docs/_canon/MODULE_REGISTRY.yaml` | Status operacional dos 16 módulos | gate_only | — | — | MODULE_REGISTRY.yaml atual |
| `docs/_canon/DATA_CONVENTIONS.md` | Convenções de dados: IDs, datas, naming, nulos, enums, soft delete | condicional (new_contract, contract_revision, new_schema) | — | §§SQL exemplos extensos (manter apenas constraint canônica) | DATA_CONVENTIONS.md atual |
| `docs/_canon/SECURITY_RULES.md` | Regras de segurança transversais, ADRs normativas | condicional (adversarial_analysis, new_contract) | — | Perfis base (redirecionar para SYSTEM_SCOPE.md §4) | SECURITY_RULES.md atual |
| `docs/_canon/SYSTEM_SCOPE.md` | Escopo, missão, atores, macrodomínios, exclusões, dependências | condicional (new_module, generate_code) | — | §9 Decisões em Aberto (desatualizado — remover) | SYSTEM_SCOPE.md atual |
| `docs/_canon/CONTRACT_PIPELINE.md` | Estágios do pipeline, regras de transição, papel do prompt | condicional (architecture_review) | — | 4 referências a BOOT_PROFILES.md → substituir por CLAUDE.md §7 | CONTRACT_PIPELINE.md atual com correções |
| `docs/_canon/DECISION_POLICY.md` | Regras DSS, quando Decision Discovery é obrigatório, estrutura de proposta, fluxo de promoção | condicional (architecture_review) | — | — | DECISION_POLICY.md atual |
| `docs/_canon/CODE_ARCHITECTURE.md` | Stack, Clean Architecture, organização de pastas, nomenclatura | condicional (generate_code, generate_frontend) | — | §7 CODE_ARCHITECTURE_GATE (já em GATES_REGISTRY.yaml) | CODE_ARCHITECTURE.md atual |
| `docs/_canon/UI_CONTRACT_GUIDE.md` | Fusão de UI_FOUNDATIONS.md + DESIGN_SYSTEM.md: princípios UI, estados, tokens, componentes | condicional (new_ui_contract, generate_frontend) | UI_FOUNDATIONS.md completo + DESIGN_SYSTEM.md completo | — | UI_FOUNDATIONS.md + DESIGN_SYSTEM.md (arquivo renomeado/fundido) |
| `docs/_canon/HANDBALL_RULES_DOMAIN.md` | Regras IHF (HBR-001 a HBR-014) | condicional (gatilho esportivo) | — | — | HANDBALL_RULES_DOMAIN.md atual |
| Prompts worker (12 arquivos) | Execução operacional por task_type | condicional (carregado pelo orchestrator quando task_type ativa) | Correções de placeholder, bloqueios canônicos, link BOOT_PROFILES→CLAUDE.md §7 | Hardcoding de TRAINING → `<MODULE>`; bloqueios não canônicos | Prompts atuais com correções |
| `docs/_canon/gates/GATES_REGISTRY.yaml` | Registry de gates CI | gate_only | — | Referência a BOOT_PROFILES.md → CLAUDE.md §7 | GATES_REGISTRY.yaml atual |
| `.contract_driven/DOMAIN_AXIOMS.json` | Invariantes machine-readable | gate_only | — | — | DOMAIN_AXIOMS.json atual |
| `.contract_driven/templates/api/api_rules.yaml` | SSOT de convenções/templates de API HTTP | condicional (new_contract, contract_revision) | Referência explícita adicionada em CLAUDE.md §7 boot de new_contract/contract_revision | — | api_rules.yaml atual |
| `_reports/contract_gates/latest.json` | Evidência CI | gate_only (derivado) | — | — | Gerado pelo pipeline |

**Arquivos eliminados na nova arquitetura:**
- `docs/_canon/HUMAN_INTERFACE_POLICY.md` (100% duplicata de CLAUDE.md §6)
- `docs/_canon/API_CONVENTIONS.md` (100% ponteiro; substituído por referência direta a api_rules.yaml)
- `docs/_canon/ERROR_MODEL.md` (25 linhas de ponteiro; absorvido em OPERATIONS.md §5)
- `docs/_canon/UI_FOUNDATIONS.md` (fundido em UI_CONTRACT_GUIDE.md)
- `docs/_canon/DESIGN_SYSTEM.md` (fundido em UI_CONTRACT_GUIDE.md)

---

## PARTE 6 — CORREÇÕES DE ALTO IMPACTO

| Mudança | Arquivos afetados | Ganho em tokens/contexto | Ganho em qualidade | Ganho em determinismo | Prioridade |
|---------|-------------------|--------------------------|--------------------|-----------------------|------------|
| Remover §21 de CONTRACT_SYSTEM_RULES.md (242 linhas que duplicam CLAUDE.md §7) | CONTRACT_SYSTEM_RULES.md | −242 tokens por leitura de RULES | Alto (remove fonte de drift) | Alto (uma única fonte para boot profiles) | P1 |
| Excluir HUMAN_INTERFACE_POLICY.md e atualizar referência em adversarial_analysis.prompt.md | HUMAN_INTERFACE_POLICY.md, adversarial_analysis.prompt.md | −77 tokens | Alto (remove fonte de drift entre R1-R5) | Alto | P1 |
| Substituir todas as referências a BOOT_PROFILES.md por CLAUDE.md §7 | CONTRACT_PIPELINE.md (4), GATES_REGISTRY.yaml (1), create_asyncapi_contract.prompt.md (1), CONTRACT_SYSTEM_LAYOUT.md §4A.2 (1) | neutro | Alto (remove links mortos) | Alto | P1 |
| Corrigir bug de path em create_module_docs.prompt.md linha 22 (`training//` → `training/`) | create_module_docs.prompt.md | neutro | Crítico (bug funcional) | Sobe | P1 |
| Substituir bloqueios não canônicos em prompts (BLOCKED_ARAZZO_OPENAPI_LINK_MISSING, BLOCKED_FORMAT_VIOLATION) | create_arazzo_workflow.prompt.md, create_json_schema_contract.prompt.md | neutro | Médio | Alto (usa códigos do catálogo canônico) | P1 |
| Fazer lista dos 16 módulos ter SSOT única em CLAUDE.md §2; RULES §2C e LAYOUT §2 redirecionam | CONTRACT_SYSTEM_RULES.md §2C, CONTRACT_SYSTEM_LAYOUT.md §2 | −30 tokens | Médio | Alto (elimina risco de drift em 4 locais) | P2 |
| Remover seções deprecated de CONTRACT_SYSTEM_RULES.md (§6.1, §6.4: ~24 linhas) | CONTRACT_SYSTEM_RULES.md | −24 tokens | Médio (remove ruído) | Médio | P2 |
| Excluir API_CONVENTIONS.md; substituir por referência direta a api_rules.yaml | API_CONVENTIONS.md, qualquer arquivo que o referencia | −51 tokens | Médio (reduz confusão sobre onde estão as regras) | Médio | P2 |
| Fundir UI_FOUNDATIONS.md + DESIGN_SYSTEM.md em UI_CONTRACT_GUIDE.md | UI_FOUNDATIONS.md, DESIGN_SYSTEM.md | −25 tokens overhead | Neutro | Neutro | P2 |
| Absorver ERROR_MODEL.md em OPERATIONS.md §5 (2 linhas de ponteiro) | ERROR_MODEL.md, OPERATIONS.md | −25 tokens | Médio (menos fragmentação) | Médio | P2 |
| Corrigir hardcoding de TRAINING em create_openapi_contract.prompt.md e create_module_docs.prompt.md | create_openapi_contract.prompt.md, create_module_docs.prompt.md | neutro | Alto (usável para todos os módulos) | Alto | P2 |
| Adicionar api_rules.yaml explicitamente no boot de new_contract e contract_revision em CLAUDE.md §7 | CLAUDE.md §7 | +10 tokens (mais claro) | Médio (torna implícito em explícito) | Alto | P2 |
| Remover §9 de SYSTEM_SCOPE.md (decisões em aberto desatualizadas) | SYSTEM_SCOPE.md | −20 tokens | Médio (remove conteúdo factualmente incorreto) | Médio | P3 |
| Remover §14 e §15 de CONTRACT_SYSTEM_LAYOUT.md (DoD estrutural já em RULES §16/17) | CONTRACT_SYSTEM_LAYOUT.md | −30 tokens | Médio | Neutro | P3 |
| Remover §8 de CLAUDE.md (paths críticos já em OPERATIONS.md) | CLAUDE.md | −15 tokens por boot | Neutro | Neutro | P3 |
| Remover histórico detalhado de decisões resolvidas de ARCHITECTURE_DECISION_BACKLOG.md §2 (manter apenas tabela §3) | ARCHITECTURE_DECISION_BACKLOG.md | −80 tokens | Neutro | Neutro | P3 |

---

## PARTE 7 — PLANO DE MIGRAÇÃO

**Sequência:**

1. Exclusões imediatas (não requerem substituição, apenas remoção de referências):
   - Excluir `docs/_canon/HUMAN_INTERFACE_POLICY.md`
   - Excluir `docs/_canon/API_CONVENTIONS.md`
   - Excluir `docs/_canon/ERROR_MODEL.md`

2. Fusões imediatas:
   - Criar `docs/_canon/UI_CONTRACT_GUIDE.md` = UI_FOUNDATIONS.md + DESIGN_SYSTEM.md
   - Excluir `docs/_canon/UI_FOUNDATIONS.md` e `docs/_canon/DESIGN_SYSTEM.md`
   - Adicionar nota de 2 linhas sobre Problem+JSON em OPERATIONS.md §5

3. Arquivos a condensar:
   - `CONTRACT_SYSTEM_RULES.md`: remover §21, §6.1, §6.4, §2C, §7 (Diátaxis)
   - `CONTRACT_SYSTEM_LAYOUT.md`: remover §14, §15; redirecionar §2 para CLAUDE.md §2
   - `SYSTEM_SCOPE.md`: remover §9
   - `ARCHITECTURE_DECISION_BACKLOG.md`: compactar §2 (manter apenas tabela §3)
   - `CLAUDE.md`: remover §8; adicionar api_rules.yaml em boot de new_contract/contract_revision

4. Prompts a corrigir (hardcoding + links mortos + bloqueios não canônicos):
   - `create_openapi_contract.prompt.md`: substituir TRAINING → `<MODULE>`
   - `create_module_docs.prompt.md`: substituir training → `<MODULE>`, corrigir `training//` → `<module>/`
   - `create_asyncapi_contract.prompt.md`: substituir referência a BOOT_PROFILES.md → CLAUDE.md §7
   - `create_arazzo_workflow.prompt.md`: substituir `BLOCKED_ARAZZO_OPENAPI_LINK_MISSING` → `BLOCKED_MISSING_OPENAPI_PATH`
   - `create_json_schema_contract.prompt.md`: substituir `BLOCKED_FORMAT_VIOLATION` → `BLOCKED_MISSING_SCHEMA`
   - `adversarial_analysis.prompt.md`: substituir `HUMAN_INTERFACE_POLICY R4` → `CLAUDE.md §6 R4`

5. Arquivos a corrigir (links mortos para BOOT_PROFILES.md):
   - `CONTRACT_PIPELINE.md`: substituir 4 referências a BOOT_PROFILES.md → CLAUDE.md §7
   - `docs/_canon/gates/GATES_REGISTRY.yaml`: substituir `boot_profiles_ref` → CLAUDE.md §7

6. Ajustes finais de precedência e governança:
   - `CONTRACT_SYSTEM_RULES.md §2C`: adicionar redirect explícito para CLAUDE.md §2 como única lista de módulos
   - `CONTRACT_SYSTEM_LAYOUT.md §2`: adicionar redirect explícito para CLAUDE.md §2
   - Atualizar CLAUDE.md §7 boot profiles para referenciar `docs/_canon/UI_CONTRACT_GUIDE.md` ao invés de UI_FOUNDATIONS.md + DESIGN_SYSTEM.md separados

| Ordem | Ação | Arquivos envolvidos | Resultado esperado | Risco de regressão | Mitigação |
|-------|------|---------------------|--------------------|--------------------|-----------|
| 1 | Excluir HUMAN_INTERFACE_POLICY.md + atualizar referência | HUMAN_INTERFACE_POLICY.md, adversarial_analysis.prompt.md | Elimina 77 linhas de duplicata; prompt referencia CLAUDE.md §6 | Baixo — CLAUDE.md §6 tem conteúdo idêntico | Verificar grep por qualquer outra referência ao arquivo |
| 2 | Excluir API_CONVENTIONS.md | API_CONVENTIONS.md, qualquer referência | Elimina 51 linhas de ponteiro; referências vão direto para api_rules.yaml | Baixo — todo conteúdo está em api_rules.yaml | Verificar grep por referências ao arquivo |
| 3 | Excluir ERROR_MODEL.md + absorver em OPERATIONS.md §5 | ERROR_MODEL.md, OPERATIONS.md | Elimina fragmentação de modelo de erros | Baixo — conteúdo já está nas fontes apontadas | Adicionar nota em OPERATIONS.md antes de excluir |
| 4 | Criar UI_CONTRACT_GUIDE.md + excluir arquivos fonte | UI_FOUNDATIONS.md, DESIGN_SYSTEM.md, UI_CONTRACT_GUIDE.md, CLAUDE.md §7 | Um arquivo ao invés de dois para task_types de UI | Baixo — conteúdo é apenas fundido, não alterado | Atualizar referências em CLAUDE.md §7 e prompts |
| 5 | Remover §21 de CONTRACT_SYSTEM_RULES.md | CONTRACT_SYSTEM_RULES.md | −242 linhas; boot profiles ficam apenas em CLAUDE.md §7 | Médio — verificar que CLAUDE.md §7 cobre todos os casos de §21 | Diff cuidadoso entre §21 e CLAUDE.md §7 antes de remover |
| 6 | Remover §6.1, §6.4 de CONTRACT_SYSTEM_RULES.md | CONTRACT_SYSTEM_RULES.md | −24 linhas de conteúdo deprecated | Baixo | Verificar que nenhuma referência interna aponta para essas seções |
| 7 | Corrigir bug de path em create_module_docs.prompt.md | create_module_docs.prompt.md | Corrige `training//` para `<module>/` | Médio — bug ativo | Testar manualmente após correção |
| 8 | Substituir BOOT_PROFILES.md refs → CLAUDE.md §7 | CONTRACT_PIPELINE.md (4), GATES_REGISTRY.yaml (1), create_asyncapi_contract.prompt.md (1), CONTRACT_SYSTEM_LAYOUT.md (1) | Elimina 7 links mortos | Baixo | grep para validar ausência de referências restantes |
| 9 | Substituir bloqueios não canônicos em prompts | create_arazzo_workflow.prompt.md, create_json_schema_contract.prompt.md | Todos os bloqueios em prompts agora são do catálogo canônico | Baixo | Verificar contra lista em CLAUDE.md §4 e RULES §9 |
| 10 | Corrigir hardcoding de TRAINING em prompts | create_openapi_contract.prompt.md, create_module_docs.prompt.md | Prompts genéricos para todos os 16 módulos | Médio | Testar mentalmente o fluxo para um módulo que não seja training |
| 11 | Adicionar SSOT única de módulos (redirect em RULES §2C e LAYOUT §2) | CONTRACT_SYSTEM_RULES.md §2C, CONTRACT_SYSTEM_LAYOUT.md §2 | Uma única lista autoritativa de módulos | Baixo | Verificar que todos os redirects apontam para CLAUDE.md §2 |
| 12 | Condensar SYSTEM_SCOPE.md, ARCHITECTURE_DECISION_BACKLOG.md | Arquivos individuais | −100 tokens de conteúdo desatualizado/histórico | Baixo | Preservar tabela §3 do BACKLOG; preservar §§1-8 do SCOPE |

---

## PARTE 8 — VEREDITO FINAL

**Arquivos hoje no escopo:** 35

**Arquivos na arquitetura final:** 28
(3 excluídos: HUMAN_INTERFACE_POLICY.md, API_CONVENTIONS.md, ERROR_MODEL.md; 2 fundidos em 1: UI_FOUNDATIONS.md + DESIGN_SYSTEM.md → UI_CONTRACT_GUIDE.md; resultado: 35 − 3 − 2 + 1 = 31... mas MODULE_REGISTRY.yaml e DOMAIN_AXIOMS.json e GATES_REGISTRY.yaml e latest.json passam a gate_only sem leitura em contexto de agente; efetivamente **28 arquivos ativos no ciclo de instrução**)

**% do conteúdo que deve sair do contexto permanente:** 0% do boot permanente (CLAUDE.md já é o único arquivo permanente); das leituras condicionais, ~22% do conteúdo total auditado é eliminável (§21 de RULES + HUMAN_INTERFACE_POLICY.md + API_CONVENTIONS.md + ERROR_MODEL.md + UI_FOUNDATIONS.md + DESIGN_SYSTEM.md + seções deprecated/hardcoded)

**Qualidade instrucional 100/100: não**

O que falta:
- Prompts create_openapi_contract e create_module_docs estão hardcoded para módulo TRAINING — reduz qualidade para outros 15 módulos
- create_asyncapi_contract.prompt.md é escasso demais (20 linhas) para uma operação de complexidade equivalente a create_openapi_contract (51 linhas)
- Nenhum prompt cobre explicitamente o que fazer se FEATURE_REGISTRY.yaml não existir para generate_code (gate é não-bloqueante, mas o prompt assume que a feature existe)
- SYSTEM_SCOPE.md §9 contém afirmações factuais incorretas (versioning não está em aberto — ADR-003 e ADR-014 resolveram)

**Determinismo 100/100: não**

O que falta:
- 7 links mortos para BOOT_PROFILES.md (arquivo deletado) criam ambiguidade se um agente tenta resolver a referência
- 2 bloqueios não canônicos em prompts (BLOCKED_ARAZZO_OPENAPI_LINK_MISSING, BLOCKED_FORMAT_VIOLATION) não estão no catálogo de CLAUDE.md §4 ou RULES §9
- Lista de módulos em 4 locais cria risco de drift com cada mudança futura
- §21 de RULES.md (242 linhas) pode divergir de CLAUDE.md §7 em edições futuras — fonte de não-determinismo latente

**Eficiência de contexto 100/100: não**

O que falta:
- §21 de CONTRACT_SYSTEM_RULES.md consome ~242 tokens desnecessários toda vez que RULES é carregado
- HUMAN_INTERFACE_POLICY.md (77 tokens) existe como duplicata pura sem contribuição
- API_CONVENTIONS.md (51 tokens) existe como ponteiro puro sem contribuição
- OPERATIONS.md é carregado em todos os 12 task_types, incluindo aqueles onde §2 (boundary rules) raramente é relevante — overhead de 110 linhas × N sessões
- ERROR_MODEL.md (25 tokens) não tem conteúdo próprio; é puro ponteiro para 3 outros arquivos
- UI_FOUNDATIONS.md + DESIGN_SYSTEM.md somam 84 linhas que poderiam ser um arquivo único de 90 linhas com melhor integração

**Resumo executivo:**

O sistema de instruções do HB Track está acima da média em determinismo e qualidade instrucional comparado a sistemas similares — a auditoria anterior (registrada em SESSION_HANDOFF.md) já removeu problemas estruturais graves. O que permanece são redundâncias acumuladas organicamente (§21 de RULES, HUMAN_INTERFACE_POLICY.md, API_CONVENTIONS.md) e erros pontuais de manutenção (links mortos para BOOT_PROFILES.md deletado, hardcoding de TRAINING em prompts, bloqueios não canônicos, bug de path dupla barra). As 16 correções identificadas na Parte 6 podem ser implementadas em sequência sem risco sistêmico. As P1 são correções de bugs e links mortos que devem ser aplicadas imediatamente. As P2 são eliminações de redundâncias que reduzem entre 400-500 tokens de overhead sem impacto em qualidade. As P3 são otimizações de conteúdo desatualizado com ganho menor.
