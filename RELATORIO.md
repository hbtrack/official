# RELATÓRIO DE ANÁLISE — SISTEMA CONTRACT-DRIVEN HB TRACK

**Perspectiva:** Arquiteto de Software e Engenheiro de Governança Sênior
**Data:** 2026-03-17
**Escopo de análise:** `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` · `.contract_driven/CONTRACT_SYSTEM_RULES.md` · `.contract_driven/GLOBAL_TEMPLATES.md`
**Tipo de auditoria:** Revisão metodológica de governança CDD (não operacional)
**Declaração de modo:** `PRE_CONTRACT_SKIPPED: audit-only, no normative contract artifact produced`

---

## SUMÁRIO EXECUTIVO

| Tópico | Score | Veredito |
|---|:---:|---|
| 1. Aderência às diretrizes CDD | 78/100 | Bom — falta CDCT |
| 2. Garantia de funcionamento do sistema | 71/100 | Médio-alto — dependente de `_canon/` |
| 3. Alinhamento com estado da arte | 73/100 | Bom — falta consumer contracts e versioning |
| 4. Prevenção de alucinação da IA | 82/100 | Alto — mecanismos defensivos sólidos |
| 5. Eficiência cognitiva do agente | 58/100 | Médio — carga alta, sem cheat sheet |
| **Score Geral** | **72/100** | **APTO COM RESSALVAS** |

**Prioridades críticas identificadas:** Consumer-Driven Contract Testing ausente · versionamento semântico de contratos não canonizado · carga cognitiva do boot sem estratégia de compressão · ausência de quick reference para o agente.

---

## TÓPICO 1 — Os arquivos seguem as diretrizes de contract driven?

**Score: 78/100**

### Conformidades identificadas

**1. Single Source of Truth bem definida**
`LAYOUT §5` define soberania por camada com clareza: OpenAPI para HTTP, JSON Schema para domain shapes, Arazzo para workflows, AsyncAPI para eventos. A regra "nenhuma superfície pode ter duas fontes primárias" (§5.5) é explícita e aplicável.

**2. API-First / Contract-First obrigatório**
`RULES §23` (Evolution Rule) proíbe explicitamente "implementation-first seguido de documentação depois". O fluxo de criação (RULES §15) exige que contratos existam antes da implementação — este é o núcleo do CDD.

**3. Schema-first para domain shapes**
`RULES §14A` define uma política completa para criação, promoção e uso de domain shapes em `contracts/schemas/`. Distingue corretamente entre domain shape (reutilizável) e HTTP DTO (exclusivo de OpenAPI components).

**4. Pipeline de validação de contratos**
`RULES §19` fixa a toolchain: Redocly CLI, Spectral, oasdiff, Schemathesis, JSON Schema validator, AsyncAPI parser, Arazzo validator. O DoD binário (§16) exige que todos esses gates passem.

**5. Breaking change detection**
oasdiff está na toolchain (§19) e `CONTRACT_BREAKING_CHANGE_GATE` consta no DoD (§16.1). O sistema reconhece breaking changes como evento de governança explícito.

**6. Definition of Done binária**
`RULES §16` e `§17` definem critérios pass/fail claros para readiness de contrato e módulo, eliminando ambiguidade subjetiva.

**7. Diátaxis como arquitetura documental**
`RULES §7` + `GLOBAL_TEMPLATES §4` aplicam Diátaxis (tutorial / how-to / reference / explanation). Contratos são artefatos de referência; ADRs são explicação. A separação é correta.

### Desvios identificados

**D-01 — Consumer-Driven Contract Testing (CDCT) ausente [CRÍTICO]**
O sistema é inteiramente provider-centric. Não há menção a Pact, Pact Broker, consumer contracts, ou verificação de compatibilidade do ponto de vista do consumidor. Em CDD moderno (2023-2025), CDCT é considerado essencial para garantir que mudanças no provider não quebrem silenciosamente os consumidores. Esta é a lacuna metodológica mais significativa.

**D-02 — Versionamento semântico de contratos não canonizado**
`GLOBAL_TEMPLATES §1.6` lista `{{VERSIONING_STRATEGY}}` como placeholder não resolvido. A estratégia concreta (URL path /v1/v2, header versioning, semver em `info.version`) não está canonizada em nenhum dos três arquivos. A IA não pode tomar decisões de versionamento sem risco de alucinação.

**D-03 — Contract Broker/Registry ausente**
Não há mecanismo de descoberta de contratos por consumidores. Em ecossistemas CDD maduros, um registry (Pact Broker, SwaggerHub, Backstage) é o ponto central de publicação e consumo de contratos.

**D-04 — Política de deprecação não canonizada**
`{{DEPRECATION_POLICY}}` em GLOBAL_TEMPLATES §1.6 é placeholder. Como deprecar um contrato de módulo, qual sunset period e qual comunicação aos consumidores não estão definidos.

---

## TÓPICO 2 — Os arquivos garantem o funcionamento do sistema desenvolvido por contract driven?

**Score: 71/100**

### O que os arquivos garantem

**1. Estrutura canônica de filesystem**
`LAYOUT §4` define a árvore completa de `contracts/`, `generated/`, `_reports/`. Qualquer desvio estrutural é detectável automaticamente por ferramentas de filesystem.

**2. Sequência obrigatória de criação de contratos**
`RULES §15` define 8 passos ordenados. O passo 2 inclui execução obrigatória do compiler determinístico (`compile_api_policy.py`). Nenhum passo pode ser pulado sem violação explícita de governança.

**3. Fase pré-contrato obrigatória**
`RULES §22` é um guardrail crítico: nenhum worker pode ser acionado sem evidência de execução da fase pré-contrato (Fases 0–3 do orquestrador). O código `BLOCKED_PRE_CONTRACT_SKIPPED` garante enforcement declarativo.

**4. Critérios binários de readiness**
`RULES §16/§17/§18` eliminam ambiguidade: ou o módulo passa todos os critérios ou não está pronto. Não há zona cinza.

**5. Taxonomia de 16 módulos fechada**
`LAYOUT §2` fecha a lista canônica. Nenhum módulo fantasma pode ser criado sem violar explicitamente a governança.

**6. Regra de canonização tripla**
`RULES §2A` exige que toda regra exista em 3 níveis: artefato normativo + registro operacional + enforcement técnico. Isso previne regras "fantasmas" que existem apenas em código ou apenas em prompts.

### O que os arquivos NÃO garantem (lacunas de funcionamento)

**L-01 — Docs `_canon/` não têm status verificado**
O boot protocol (`RULES §6.1`) carrega 18 artefatos em sequência. Desses 18, pelo menos 12 pertencem a `docs/_canon/` (SYSTEM_SCOPE, ARCHITECTURE, HANDBALL_RULES_DOMAIN, MODULE_SOURCE_AUTHORITY_MATRIX, etc.). Esses arquivos são intensamente referenciados pela trilogia, mas seu estado atual (existência, completude, ausência de placeholders) não é verificado pelos três arquivos analisados. Um boot com artefatos `_canon/` ausentes ou incompletos degrada o funcionamento sem alerta proativo além do blocking code que a IA deve emitir.

**L-02 — Ausência de mecanismo de rollback de contrato**
`RULES §23` define a ordem de evolução, mas não define como reverter um contrato com breaking change publicado. Em CDD operacional, rollback é um caminho crítico.

**L-03 — Enforcement de blocking codes é declarativo**
Os 19 blocking codes (`RULES §9`) dependem da IA auto-declarar o bloqueio. Não há mecanismo externo (hook de CI, middleware de prompt, validação pré-execução) que verifique se a IA realmente bloqueou antes de continuar.

**L-04 — Geração automática de artefatos derivados não explicitada na trilogia**
`_reports/` e `generated/` são definidos como destinos de artefatos derivados, e `compile_api_policy.py` é referenciado no §15. Mas o pipeline completo de geração (qual script gera o quê, em qual ordem, com qual frequência) não está explicitado nos três arquivos — depende de `docs/_canon/CONTRACT_PIPELINE.md`, que é um ponto de falha externo.

---

## TÓPICO 3 — Os arquivos estão de acordo com o que as fontes especializadas atuais ditam como sucesso para desenvolvimento por contract driven?

**Score: 73/100**

### Alinhamento com o estado da arte (2024-2025)

| Prática de referência | Status | Evidência nos arquivos |
|---|:---:|---|
| API-First / Contract-First | ✅ Total | RULES §23, §15 |
| OpenAPI como SSOT de interface HTTP | ✅ Total | LAYOUT §5.1 |
| JSON Schema para domain shapes | ✅ Total | RULES §14A |
| AsyncAPI para eventos | ✅ Total | LAYOUT §9, RULES §11.7 |
| Arazzo para workflows multi-step | ✅ Total | LAYOUT §8, RULES §11.6 |
| Spectral para linting de OpenAPI | ✅ Total | RULES §19 |
| oasdiff para breaking change detection | ✅ Total | RULES §19, §16.1 |
| Schemathesis para contract testing | ✅ Total | RULES §19 |
| Redocly CLI para validação | ✅ Total | RULES §19 |
| CI/CD gates de contratos | ✅ Total | RULES §16.1, LAYOUT §1A |
| Diátaxis como arquitetura documental | ✅ Total | RULES §7 |
| ADRs para decisões arquiteturais | ✅ Total | RULES §3.6 |
| Google AIP + Adidas API guidelines | ✅ Referenciado | `api_rules.yaml` (ref. §3B) |
| Taxonomia de módulos fechada | ✅ Boa prática | LAYOUT §2 |
| DoD binário de readiness | ✅ Boa prática | RULES §16-18 |

### Lacunas em relação ao estado da arte

| Prática Ausente | Impacto | Fonte de Referência |
|---|:---:|---|
| Consumer-Driven Contract Testing (Pact) | **Alto** | Pact Foundation, ThoughtWorks Radar 2023-2025 |
| Contract versioning semântico explícito | **Alto** | OpenAPI Best Practices, API Stylebook |
| Contract broker / registry centralizado | **Médio** | Pact Broker, Backstage API Catalog |
| Política de deprecação canônica | **Médio** | Google AIP-0191, Zalando API Guidelines |
| Automated mock generation (Prism/Mockoon) | **Médio** | OpenAPI Tooling Landscape 2024 |
| Runtime contract monitoring | **Médio** | ThoughtWorks Radar: Contract Testing in Production |
| Contract stability badges / maturity levels | **Baixo** | Pact Maturity Model |

**Nota sobre Consumer-Driven Contract Testing:** O ThoughtWorks Technology Radar (2022-2025) e o State of API Report (Postman, 2024) classificam CDCT como "Adopt" — prática consolidada para sistemas com múltiplos consumidores. A ausência de CDCT no sistema significa que mudanças em contratos provider-side não têm verificação de compatibilidade com consumidores reais, o que é o cenário exato que CDD se propõe a eliminar.

---

## TÓPICO 4 — Os arquivos garantem que a IA desenvolva o sistema sem alucinações?

**Score: 82/100**

Este é o ponto mais robusto do sistema. Os três arquivos implementam uma estratégia de defesa em profundidade contra alucinações.

### Mecanismos anti-alucinação: 6 camadas defensivas

**Camada 1 — Proibição explícita de inferência livre (RULES §8)**
O §8 lista 14 categorias explicitamente proibidas de serem inventadas sem contrato: módulos, endpoints, fields estáveis, enums, eventos, workflows, transições de estado, modelos de permissão, erros domain-specific, comportamento de UI, regras de handebol, integrações externas, operações assíncronas. A regra "Artefato ausente → bloquear" é direta e sem margem para interpretação.

**Camada 2 — Taxonomia fechada de 16 módulos (LAYOUT §2)**
A lista de módulos canônicos é fechada e enumera explicitamente todos os módulos válidos. Qualquer referência a módulo fora da lista emite `BLOCKED_MISSING_MODULE`. Esta camada elimina uma classe inteira de alucinações — criação de módulos fantasmas.

**Camada 3 — Sistema de 19 blocking codes (RULES §9)**
Os códigos cobrem todos os cenários de artefato ausente com especificidade. O comportamento padrão é parar, não inferir. A granularidade dos códigos (distinção entre `BLOCKED_MISSING_SCHEMA` e `BLOCKED_MISSING_DOMAIN_RULE`, por exemplo) força o agente a diagnosticar a ausência exata, não generalizar.

**Camada 4 — Fase pré-contrato obrigatória (RULES §22)**
Checkpoint obrigatório de verificação de contexto antes de qualquer trabalho normativo. A exceção (`PRE_CONTRACT_SKIPPED: audit-only, no artifact produced`) é explícita e declarativa.

**Camada 5 — Hierarquia de precedência determinística (RULES §5)**
14 níveis de precedência cobrem todos os cenários de conflito entre fontes. Não há ambiguidade sobre qual fonte prevalece. Conflito no mesmo nível emite `BLOCKED_CONTRACT_CONFLICT` em vez de resolução por inferência.

**Camada 6 — Regra de canonização tripla (RULES §2A)**
Uma regra só é válida se existir em: artefato normativo + registro operacional + enforcement técnico. Prompts sozinhos não canonizam comportamento (§2A.2). Esta regra evita que instruções ad-hoc em prompts sejam tratadas como autoritativas.

### Riscos residuais

**R-01 — Blocking codes são auto-declarados [CRÍTICO]**
O sistema depende que a IA auto-declare o bloqueio. Se a IA decidir continuar além de uma condição de bloqueio, não há mecanismo externo impeditivo. A garantia é comportamental, não mecânica.

**R-02 — Boot sequence de 18 itens pode exceder janela de contexto**
Em tarefas complexas multi-módulo, o boot completo (18 artefatos + docs de módulo + contratos) pode ocupar 40-60% da janela de contexto disponível. Se algum artefato do boot for omitido para "caber" no contexto, o agente opera com informação parcial sem declarar degradação.

**R-03 — Cross-references densas criam risco de rastreabilidade perdida**
Os três arquivos contêm ~55 referências cruzadas obrigatórias entre si. O agente precisa manter o mapa de referências ativo na memória de trabalho durante toda a tarefa. Uma navegação incorreta entre seções pode resultar em aplicação da regra errada.

**R-04 — Artefatos `_canon/` ausentes são detectados apenas durante o boot**
Se um doc obrigatório do boot não existir, a IA deve emitir `BLOCKED_MISSING_CANON_ARTIFACT`. Mas se o boot não incluiu o artefato que estava ausente (por perfil de leitura mínimo, por exemplo), a ausência passa despercebida.

---

## TÓPICO 5 — Os arquivos instruem o agente sem sobrecarregar capacidade cognitiva?

**Score: 58/100**

Este é o ponto de maior risco operacional do sistema atual. A estrutura é arquiteturalmente correta, mas a carga cognitiva para o agente é substancial e não tem estratégia explícita de mitigação.

### Métricas de carga cognitiva

**Volume da trilogia:**

| Arquivo | Linhas | Seções | Referências cruzadas saídas |
|---|:---:|:---:|:---:|
| `CONTRACT_SYSTEM_LAYOUT.md` | ~547 | 15 | ~12 para RULES, ~4 para api_rules |
| `CONTRACT_SYSTEM_RULES.md` | ~1.133 | 23 | ~15 para LAYOUT, ~8 para GLOBAL_TEMPLATES |
| `GLOBAL_TEMPLATES.md` | ~674 | 38+ | ~20 para RULES e LAYOUT |
| **Total** | **~2.354** | **76** | **~55 cross-refs** |

A trilogia + `api_rules.yaml` (não analisado aqui mas obrigatório no boot) representa um volume de governança que, em uma sessão típica de LLM (200k tokens), consome 15-25% da janela de contexto antes do início de qualquer trabalho real.

**Boot protocol:** `RULES §6.1` lista 18 artefatos em sequência obrigatória. Muitos desses artefatos são extensos (`HANDBALL_RULES_DOMAIN`, `MODULE_SOURCE_AUTHORITY_MATRIX`, `ARCHITECTURE`, etc.). Um boot completo teórico com todos os 18 artefatos pode ocupar 40-60% da janela de contexto.

### O que o sistema faz CERTO para reduzir carga

**C-01 — Perfis de leitura por tarefa (RULES §6.4)**
Boa ideia: cada task_type tem um conjunto mínimo de boot definido. Isso permite que o agente evite carregar artefatos irrelevantes.

**C-02 — Matriz de boot por task type (RULES §21)**
9 task types cobertos (§21.1 a §21.9) com boot obrigatório e condicional distintos. Reduz o escopo de leitura por tarefa específica.

**C-03 — BOOT_PROFILES.md como destino de detalhamento**
A trilogia delega o detalhamento de perfis para um doc especializado, evitando que a trilogia precise expandir ainda mais.

**C-04 — Separação em 3 arquivos com responsabilidades distintas**
LAYOUT (onde), RULES (como/quando), GLOBAL_TEMPLATES (scaffolds). Princípio de responsabilidade única respeitado.

### Problemas de carga cognitiva

**CC-01 — Ausência de "Quick Reference" para o agente [CRÍTICO]**
Não existe um arquivo `AGENT_CHEATSHEET.md` ou similar com: lista dos 16 módulos, 19 blocking codes, mapeamento task → boot mínimo, regras mais consultadas — em formato ultra-compacto (< 100 linhas). O agente sempre precisa navegar a trilogia para informações de alta frequência de consulta.

**CC-02 — GLOBAL_TEMPLATES.md é índice sem conteúdo**
Seções §3 a §35 dizem "Template movido para: `.contract_driven/templates/...`". Isso cria um hop de navegação desnecessário: o agente lê o índice → descobre que o conteúdo está em outro lugar → vai buscar. Em termos de contexto, o GLOBAL_TEMPLATES.md consome tokens de leitura sem entregar conteúdo diretamente utilizável.

**CC-03 — Cross-referencing denso e bidirecional**
~55 referências cruzadas nos três arquivos. Muitas são da forma "ver seção X do arquivo Y" sem reproduzir a informação relevante. O agente precisa manter um grafo de referências ativo enquanto raciocina sobre a tarefa.

**CC-04 — Condicionalidade aninhada**
§11 (Matriz de aplicabilidade) + §12 (Handball trigger) + §14A (Domain shapes policy) + §22 (Pre-contract) são todos condicionais e interagem entre si. A avaliação de "este artefato é obrigatório para esta tarefa?" requer navegação por 4 seções de RULES antes de uma resposta.

**CC-05 — Ausência de estratégia explícita de compressão de contexto**
Para tarefas multi-sessão ou multi-módulo, não há protocolo de "state handoff" que permita ao agente retomar o trabalho sem reler toda a trilogia. Cada sessão paga o custo total de boot.

---

## TÓPICO 6 — Parecer Final: Relação dos Arquivos × Desenvolvimento × Contract-Driven

**Score final: 72/100 — APTO COM RESSALVAS**

### Diagnóstico por dimensão

**Estrutura de governança (excelente):**
A trilogia define uma hierarquia de soberania clara (LAYOUT define onde, RULES define como, GLOBAL_TEMPLATES fornece scaffolds). A separação de responsabilidades é correta, as referências cruzadas são explícitas e vinculantes, e a regra de canonização tripla (§2A) é arquiteturalmente elegante. Este é o ativo mais valioso do sistema.

**Anti-alucinação para IA (bom):**
As 6 camadas defensivas (inferência proibida, taxonomia fechada, blocking codes, pré-contrato obrigatório, precedência determinística, canonização tripla) formam um sistema de contenção robusto. Com excepção dos blocking codes auto-declarados (sem enforcement externo), o sistema é sólido nesta dimensão.

**Completude metodológica (médio-alto):**
CDD provider-side está bem coberto. CDCT (Consumer-Driven) está inteiramente ausente. Versionamento e deprecação são placeholders. O sistema está completo para controlar a criação de contratos, mas incompleto para garantir a compatibilidade de consumo.

**Praticidade operacional para o agente (médio):**
O sistema é completo mas pesado. Um agente em produção real enfrenta: 18 artefatos de boot, 76 seções em 3 arquivos, 55 cross-references e nenhum cheat sheet. A probabilidade de o agente operar com contexto parcial (por limitação de janela) é real e não tem estratégia de mitigação explícita.

**Garantia de funcionamento (médio-alto):**
O sistema funciona bem quando todos os artefatos `_canon/` estão presentes e completos. A dependência não verificada desses artefatos é o principal risco de funcionamento. Se `_canon/` estiver incompleto, o sistema degrada sem alerta proativo eficaz.

### Veredito

Os três arquivos constituem **uma base de governança contract-driven madura e adequada para um sistema de gestão esportiva com IA como agente de desenvolvimento**. A arquitetura conceitual está correta, a toolchain é moderna, e os mecanismos anti-alucinação são os pontos mais fortes. As lacunas identificadas (CDCT, versionamento, carga cognitiva) não inviabilizam o sistema, mas representam riscos reais que devem ser endereçados antes de escalar o desenvolvimento assistido por IA para múltiplos módulos concorrentes.

---

## TÓPICO 7 — Pontos Detectados na Análise

### Críticos (prioridade imediata)

**P-01 — Consumer-Driven Contract Testing completamente ausente**
Nenhuma menção a Pact, consumer contracts, ou verificação de compatibilidade do ponto de vista do consumidor. O sistema verifica que o provider está correto, mas não verifica que os consumidores do provider continuam compatíveis após mudanças. Esta é a lacuna metodológica mais crítica em CDD moderno.

**P-02 — Versionamento semântico de contratos não canonizado**
`{{VERSIONING_STRATEGY}}` existe como placeholder não resolvido em GLOBAL_TEMPLATES §1.6. Sem definição explícita (URL path versioning, header versioning, semver), a IA não pode tomar decisões de versionamento sem risco de alucinação — violando diretamente o RULES §8.

**P-03 — Boot sequence de 18 itens sem estratégia de compressão**
O boot protocol pode consumir 40-60% da janela de contexto disponível antes de qualquer trabalho real. Não há protocolo de degradação graceful (qual é o mínimo absoluto se o contexto for limitado?), nem estratégia de state handoff entre sessões.

**P-04 — Blocking codes sem enforcement externo**
19 códigos de bloqueio são a principal defesa contra drift, mas todos são auto-declarados pela IA. Um hook de CI, um wrapper de prompt, ou uma validação pré-geração que inspecione o output do agente seria necessário para tornar o enforcement mecânico em vez de apenas comportamental.

### Médios (prioridade alta)

**P-05 — Estado dos artefatos `_canon/` desconhecido**
18 artefatos do boot residem em `docs/_canon/`. Seu estado (existência, completude, ausência de placeholders, alinhamento com a trilogia) não é verificado pelos três arquivos analisados. Se qualquer um estiver ausente ou incompleto, o sistema opera degradado.

**P-06 — GLOBAL_TEMPLATES.md é um índice/redirect, não um artefato auto-suficiente**
Todas as seções de template (§3 a §35) redirecionam para `.contract_driven/templates/`. O arquivo consome contexto de leitura sem entregar conteúdo diretamente utilizável. Para o agente, o custo de navegação é alto.

**P-07 — Ausência de Quick Reference para o agente**
Não existe um arquivo compacto com: módulos válidos, blocking codes, task-to-boot mapping, regras mais frequentemente consultadas. O agente precisa navegar a trilogia completa para qualquer consulta pontual.

**P-08 — Circularidade em §2A.4 (classificação de boot)**
Todo novo artefato deve ser classificado em BOOT_PROFILES.md. Mas BOOT_PROFILES.md é ele mesmo um artefato de boot. Se BOOT_PROFILES.md estiver desatualizado, o agente não saberá que novos artefatos foram promovidos ao boot — um blind spot estrutural.

**P-09 — Política de deprecação ausente**
`{{DEPRECATION_POLICY}}` é placeholder. Sem definição de sunset period, comunicação a consumidores e critérios de remoção de contrato, a evolução de longo prazo do sistema fica sem governança.

### Melhoria (baixa prioridade)

**P-10 — Regra de idioma referenciada em dois lugares**
LAYOUT §3 define idioma canônico. RULES §2B aponta para LAYOUT §3. A duplicação de referência adiciona um hop desnecessário.

**P-11 — Matriz de aplicabilidade (RULES §11) pode crescer indefinidamente**
9 artefatos condicionais cobertos. Sem critério explícito de encerramento, a seção pode acumular casos ad-hoc com o tempo.

**P-12 — `docs/hbtrack/decisoes/` tem status potencialmente ambíguo**
LAYOUT §4A.2A classifica como "não-soberana" e exige README local. A ausência do README é mencionada como gap de governança — se nunca for criado, a classificação fica implícita.

**P-13 — Ausência de mecanismo de lock de artefatos normativos**
Não há definição de como o sistema se comporta quando dois agentes ou dois desenvolvedores trabalham no mesmo módulo simultaneamente. Condição de corrida em artefatos normativos não tem política.

---

## TÓPICO 8 — O Que Você Deveria Perguntar (Mas Não Perguntou)

Estas são as perguntas que, se não respondidas, representam riscos reais ao sucesso do sistema.

---

### 8.1 "Os artefatos `_canon/` referenciados no boot realmente existem e estão completos?"

**Por que é vital:**
O sistema inteiro de anti-alucinação assume que o boot carrega contexto válido. A trilogia referencia ~20 artefatos em `docs/_canon/` como autoritativos e necessários para o boot. Se qualquer um desses artefatos estiver ausente, incompleto, ou cheio de placeholders não resolvidos, o agente opera em modo degradado sem saber. O resultado prático são contratos tecnicamente válidos para a governança mas semanticamente incorretos para o domínio — a alucinação mais perigosa porque passa pelos gates.

**Ação recomendada:**
Antes de qualquer ciclo de desenvolvimento com IA, executar um scorecard de completude de todos os 18 artefatos do boot. Isso deveria ser um gate obrigatório (`CANON_COMPLETENESS_GATE`) no pipeline.

---

### 8.2 "Qual é o procedimento de recovery quando um blocking code é emitido?"

**Por que é vital:**
`RULES §9` define 19 blocking codes, mas não define o procedimento de resolução de nenhum. O agente bloqueia, reporta o código — e então? Quem resolve? Como? Em quanto tempo? Sem um playbook de unblocking, os bloqueios se tornam gargalos operacionais: o trabalho para, mas não há caminho claro para retomada.

**Ação recomendada:**
Criar `docs/_canon/UNBLOCKING_PLAYBOOK.md` com, para cada código, o artefato a ser criado/corrigido, quem tem autoridade para fazê-lo, e os critérios de retomada.

---

### 8.3 "Como o sistema valida contratos contra o runtime em produção?"

**Por que é vital:**
A governance file faz um excelente trabalho de prevenir drift durante criação (pre-merge, CI). Mas depois que o sistema entra em produção, o runtime pode divergir gradualmente dos contratos. Schemathesis no CI resolve parte disso, mas sem schedule de validação contract-vs-runtime (contract testing against live API), drift de produção pode acumular silenciosamente por meses.

**Ação recomendada:**
Canonizar uma `RUNTIME_CONTRACT_MONITORING_POLICY.md` com: frequência mínima de validação, ferramenta (Schemathesis em modo produção, ou outro), critério de alerta, e responsável por triagem.

---

### 8.4 "Como o sistema lida com múltiplos agentes de IA trabalhando concorrentemente no mesmo módulo?"

**Por que é vital:**
O sistema foi desenhado implicitamente para um agente por sessão. Em cenários reais — múltiplos desenvolvedores usando agentes simultaneamente, ou um único desenvolvedor com múltiplas sessões paralelas — pode haver condição de corrida em artefatos normativos. Dois agentes podem produzir versões conflitantes do mesmo contrato, ambas passando nos gates individualmente. Sem política de locking ou de mesclagem de contratos, conflitos são silenciosos.

**Ação recomendada:**
Definir política de concorrência de agentes em RULES ou em `docs/_canon/GOVERNANCE_EVOLUTION_POLICY.md`, incluindo: uso de branches de contrato, processo de merge review, e critério de resolução de conflito.

---

### 8.5 "Os templates em `.contract_driven/templates/` têm versionamento próprio?"

**Por que é vital:**
GLOBAL_TEMPLATES.md migrou os corpos dos templates para `.contract_driven/templates/`. Se esses templates evoluírem (e evoluirão), artefatos instanciados a partir de versões anteriores ficam inconsistentes com o padrão atual. Sem versionamento de template, é impossível saber "de qual versão do template este artefato foi instanciado" — o que torna auditorias de conformidade imprecisas.

**Ação recomendada:**
Adicionar `template_version` ao header YAML dos artefatos de módulo. Manter `CHANGELOG.md` em `.contract_driven/templates/`. Incluir verificação de template_version no scorecard de readiness.

---

### 8.6 "Existe um caminho de onboarding progressivo para novos agentes/desenvolvedores?"

**Por que é vital:**
A trilogia tem ~2.354 linhas. O boot protocol tem 18 itens. Um desenvolvedor novo (humano ou IA) que nunca viu o sistema precisa processar tudo isso antes de contribuir. Sem um caminho progressivo — Tutorial (5 min) → How-to (por task type) → Reference (trilogia completa) — o risco de uso incorreto do sistema por pressa ou atalhos é alto. A trilogia atual é exclusivamente documentação de referência; não há tutorial nem how-to.

**Ação recomendada:**
Criar dois artefatos de Diátaxis que faltam:
- `docs/_canon/GETTING_STARTED.md` — tutorial de 1-2 páginas, caminho mínimo para a primeira contribuição
- `docs/_canon/HOW_TO_CREATE_CONTRACT.md` — checklist operacional para o caso de uso mais comum

---

### 8.7 "Como o sistema preserva estado de sessão entre conversas com a IA?"

**Por que é vital:**
A IA não tem memória persistente entre sessões por padrão. O boot protocol assume releitura completa a cada sessão — o que é correto para garantir consistência, mas é custoso. Para módulos complexos com muitos artefatos, o overhead de re-leitura pode consumir uma parte significativa de cada sessão. Pior: sem um artefato de "session state", informações de sessões anteriores (decisões tomadas, razão de escolhas, contexto de conflitos resolvidos) se perdem, e o agente pode repetir trabalho ou contradizer decisões anteriores.

**Ação recomendada:**
Canonizar um template `SESSION_STATE_HANDOFF.md` (em `docs/hbtrack/modulos/<module>/` ou `_reports/agent_execution/`) que capture: módulo em trabalho, fase atual, artefatos lidos, decisões tomadas, blockers pendentes. Este artefato acelera o boot de sessões subsequentes sem comprometer a integridade.

---

### 8.8 "Qual é o processo de evolução da própria governança (meta-governança)?"

**Por que é vital:**
`RULES §23` define como evoluir contratos de domínio. Mas não define como evoluir a própria trilogia de governança. Quem tem autoridade para modificar `CONTRACT_SYSTEM_RULES.md`? Qual processo de aprovação? Como as mudanças são comunicadas para agentes ativos? Como garantir que uma mudança na trilogia não invalida silenciosamente artefatos já criados? Sem meta-governança explícita, a trilogia pode derivar de forma não controlada.

**Ação recomendada:**
Criar `docs/_canon/GOVERNANCE_EVOLUTION_POLICY.md` com: autoridade de mudança, processo de revisão, comunicação de breaking change na governança, e critério de re-auditoria de artefatos existentes após mudança na trilogia.

---

## APÊNDICE — Consolidação de Lacunas por Prioridade

### Ação imediata (antes do próximo ciclo de desenvolvimento com IA)

1. Auditar completude dos ~18 artefatos `_canon/` do boot (→ P-05, tópico 8.1)
2. Criar `AGENT_CHEATSHEET.md` compacto com módulos, blocking codes, task-to-boot map (→ P-07)
3. Canonizar estratégia de versionamento de contratos em `API_CONVENTIONS.md` (→ P-02, D-02)
4. Definir playbook de unblocking por código de bloqueio (→ tópico 8.2)

### Ação de curto prazo (próximo sprint de governança)

5. Avaliar e canonizar Consumer-Driven Contract Testing — Pact ou alternativa (→ D-01, P-01)
6. Canonizar política de deprecação de contratos (→ D-04, P-09)
7. Criar `GETTING_STARTED.md` e `HOW_TO_CREATE_CONTRACT.md` (→ tópico 8.6)
8. Criar template `SESSION_STATE_HANDOFF.md` (→ tópico 8.7)

### Ação de médio prazo

9. Versionamento de templates + `template_version` no header de artefatos (→ tópico 8.5)
10. Política de meta-governança (evolução da trilogia) (→ tópico 8.8)
11. Estratégia de runtime contract monitoring (→ tópico 8.3)
12. Política de concorrência de agentes (→ tópico 8.4)

---

*Relatório produzido em modo audit-only. Nenhum artefato normativo foi criado ou modificado.*
*`PRE_CONTRACT_SKIPPED: audit-only, no normative contract artifact produced`*


