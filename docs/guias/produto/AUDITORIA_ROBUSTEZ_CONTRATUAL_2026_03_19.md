# AUDITORIA DE ROBUSTEZ CONTRATUAL — HB TRACK
**Data:** 2026-03-19
**Auditor:** Análise adversarial estrutural — mecanismos normativos e operacionais
**Escopo:** Sistema CDD completo — templates + regras + contratos gerados + pipeline de validação
**Postura:** Severa. Sem benefício da dúvida. Sem revisão benevolente.

---

## PARTE 1 — VEREDITO GERAL

### Classificação: **CONTRATO BONITO, MAS FRÁGIL**

O sistema de contratos do HB Track apresenta uma arquitetura aspiracional de alta sofisticação: 909 linhas de regras operacionais, 44 gates documentados, 19 tipos de tarefas catalogados, 16 módulos canônicos, hierarquia de 13 níveis de precedência, rastreabilidade SHA256 de artefatos, CANONICAL_TYPE_REGISTRY com field bindings, 24 seções de regras cobrindo naming, idioma, boot profiles, DoD por superfície e muito mais.

**A aparência de robustez é real. A robustez em si é ilusória.**

O problema central não está na redação dos contratos — está nos mecanismos de enforcement que sustentam a execução. Especificamente:

1. **37 dos 44 gates são permanentemente SKIP_NOT_APPLICABLE** — incluindo gates de natureza `blocking: true`, como `REQUIRED_ARTIFACT_PRESENCE_GATE`, `OWASP_API_CONTROL_MATRIX_GATE`, `MODULE_REGISTRY_GATE`, `BOUNDARY_*_GATE`. O pipeline retorna `overall_status = PASS` com exit_code 0 enquanto 84% de sua cobertura está desabilitada.

2. **A execução normativa real é delegada a agentes LLM interpretando arquivos Markdown** — os prompts operacionais (.prompt.md) são o mecanismo de execução principal. O próprio CONTRACT_SYSTEM_RULES.md §2A.2 declara que "prompts não são fonte substantiva" — mas todo o pipeline é implementado como prompts.

3. **A análise adversarial é declarada como não-bloqueante** na promoção para `implementation_ready`, enquanto o TASK_CATALOG exige `ADVERSARIAL_ANALYSIS_GATE = PASS` para `generate_code`. Há 15 módulos em `implementation_ready`, nenhum com evidência verificável de análise adversarial executada.

4. **O DERIVED_DRIFT_GATE** é exigido explicitamente em `readiness_promotion.prompt.md` como critério de promoção (P2), mas não existe no relatório de pipeline `latest.json`. Um gate obrigatório para promoção simplesmente não está no sistema de gates.

O sistema governa **aparência de conformidade**, não comportamento real.

---

## PARTE 2 — SCORE DE ROBUSTEZ

| Critério | Nota | Justificativa objetiva |
|---|---|---|
| **Clareza normativa** | 62 | CONTRACT_SYSTEM_RULES.md tem 909 linhas e 24 seções bem estruturadas. Mas as regras críticas vivem em cadeia de ponteiros (AGENT_INSTRUCTIONS → CONTRACT_SYSTEM_RULES → CONTRACT_PIPELINE → GATES_REGISTRY), o que distribui a normatividade de forma não-operacional. Vários trechos usam linguagem condicional ("quando aplicável", "recomenda-se") em pontos onde deveria haver imperativo. |
| **Acionabilidade** | 52 | Os 18 códigos de bloqueio (BLOCKED_*) são bem nomeados, mas a maior parte não tem caminho de resolução determinístico definido no contrato. O que fazer quando `BLOCKED_MISSING_ARCH_DECISION` é emitido? O contrato diz "ir para Decision Discovery" — mas não especifica prazo, critérios de conclusão nem quem é responsável. |
| **Determinismo** | 38 | O mecanismo de execução central é um LLM interpretando Markdown. Diferentes instâncias de agente, em diferentes sessões, com diferentes subconjuntos de contexto carregado (boot mínimo vs. boot condicional), produzem comportamentos diferentes sem violar qualquer regra explícita. SESSION_HANDOFF.md é opcional e sem schema. |
| **Cobertura de cenários** | 50 | Happy path (criar contrato → validar → promover → gerar código) está bem coberto. Ausentes: falha parcial em tarefas multi-fase, execução simultânea de agentes em módulos interdependentes, rebaixamento de gate após promoção, waivers expirados, módulo promovido mas com surface content mínimo que passa as checks de existência mas não de qualidade. |
| **Tratamento de exceções** | 42 | 18 BLOCKED_* codes definidos, mas a maioria não especifica: quem resolve, em quanto tempo, o que constitui resolução, o que acontece se não resolver. A exceção da análise adversarial (emitir aviso, não bloquear) cria um caminho de execução crítico desprotegido. Waivers existem em `_waivers/` sem data de expiração verificável. |
| **Ausência de ambiguidade** | 48 | "overall_status = PASS" significa coisas diferentes dependendo de quantos gates estão ativos. "Confirmação explícita do humano" (readiness_promotion Fase 3) não tem critério de validade — um "ok" de um leigo em desenvolvimento é tratado como confirmação suficiente para promover um módulo para `implementation_ready`. "artefatos presentes" = arquivo existe e não está vazio — conteúdo mínimo passa. |
| **Consistência interna** | 58 | Contradição §2A.2 vs. arquitetura geral: "prompts não são fonte substantiva" mas toda a execução normativa vive em .prompt.md. DERIVED_DRIFT_GATE exigido em readiness_promotion.prompt.md mas ausente no latest.json. Adversarial analysis: não-bloqueante em promoção (readiness_promotion S1) vs. bloqueante em generate_code (TASK_CATALOG). |
| **Precedência / hierarquia de regras** | 55 | §5 do CONTRACT_SYSTEM_RULES.md define 13 níveis de precedência. Nenhum gate verifica respeito a essa hierarquia. Os contratos gerados não referenciam a hierarquia diretamente. Conflito entre regra em CONTRACT_SYSTEM_RULES.md e instrução em um ADR não tem gate de detecção — depende de inferência do agente. |
| **Verificabilidade** | 35 | 37/44 gates SKIP_NOT_APPLICABLE, todos com blocking: true. ASYNCAPI_VALIDATION skipped — os contratos async não são validados. Adversarial analysis verificada via "menção em SESSION_HANDOFF.md" — evidência de texto não-estruturado em arquivo efêmero. Gap resolution (G-01 a G-06 no UI_CONTRACT_TRAINING) não tem gate de verificação. |
| **Robustez real vs qualidade aparente** | 30 | O delta entre aparência e realidade é a maior fragilidade do sistema. 909 linhas de regras → 7 gates ativos na prática. 44 gates documentados → 84% inativos. "pipeline verde" → apenas linting sintático (redocly) + JSON schema validation + placeholder check + path layout. O sistema produz artefatos que parecem prontos para implementação mas nunca foram submetidos a validação semântica, adversarial, de boundary ou de cross-module. |

### Nota final consolidada: **47/100**

**Por que não merece 100/100:**
O sistema não merece nem 60/100 porque falha no critério mais fundamental de um sistema de contratos: o mecanismo de enforcement real não corresponde ao mecanismo de enforcement declarado. A arquitetura normativa existe em texto; a execução normativa ocorre em LLM sessions com contexto variável, gates desativados e validação efetivamente restrita a checks sintáticos.

---

## PARTE 3 — SINAIS DE "CONTRATO BONITO"

| Trecho / Ponto | Por que parece bom | Por que é frágil na prática | Severidade | Tipo de falha | Impacto |
|---|---|---|---|---|---|
| **44 gates documentados** no `latest.json` com `blocking: true` | Aparenta cobertura de validação abrangente em múltiplas dimensões | 37/44 são SKIP_NOT_APPLICABLE. O campo `blocking: true` não significa "está bloqueando" — significa "se rodasse, bloquearia". O sistema nunca os roda. | Crítica | Falha de composição | Todos os módulos promovidos a `implementation_ready` sem que 84% dos gates tenham sido executados. |
| **overall_status = PASS, exit_code = 0** | Aparenta pipeline 100% verde, todo o sistema validado | PASS é atingido porque SKIP retorna exit_code 0, que é somado ao overall. A "aprovação" é uma identidade matemática: 7 PASS + 37 SKIP = PASS. | Crítica | Falha de regra | Qualquer consumidor do gate report que leia apenas `overall_status` será enganado sobre o estado real do sistema. |
| **18 códigos BLOCKED_*** definidos em CONTRACT_SYSTEM_RULES.md §9 | Aparenta sistema sofisticado de controle de falhas com categorias explícitas | A maioria não especifica resolução, prazo, escalação ou critério de conclusão. Um bloqueio emitido pode permanecer indefinidamente sem mecanismo de detecção de não-resolução. | Alta | Falha de template | Bloqueios viram burocracia — emitidos mas nunca verificados. |
| **909 linhas em CONTRACT_SYSTEM_RULES.md** com 24 seções detalhadas | Aparenta alto grau de cobertura normativa e maturidade do sistema | Volume não é cobertura. Seções inteiras são ponteiros para outros arquivos ("ver seção X de LAYOUT", "ver GATES_REGISTRY"). A densidade normativa real é bem menor que a aparente. | Média | Falha de template | Agentes que leem parcialmente o documento assumem cobertura que não existe naquele trecho. |
| **CANONICAL_TYPE_REGISTRY.yaml** com field bindings e semantic types | Aparenta tipos fortes rastreáveis até semantic contracts | O registry existe, mas não há gate que verifique que o contrato OpenAPI/AsyncAPI gerado usa os tipos canônicos. `style_veto` em `resolved_policy` documenta regras mas não executa verificação automaticamente. | Alta | Falha de regra | Contratos podem usar tipos ad hoc sem violar nenhuma gate. |
| **SHA256 traceability em `training.sync.traceability.yaml`** | Aparenta cadeia de custódia criptográfica rigorosa | Os SHAs verificam integridade de arquivo mas não de conformidade normativa. Um arquivo pode ter SHA correto e conteúdo conceitualmente incorreto. Não há gate que valide se os SHAs dos artefatos gerados batem com os manifestos. | Média | Falha de composição | Rastreabilidade de integridade sem rastreabilidade de conformidade = checksums sem semântica. |
| **readiness_promotion Fase 3: "AGUARDAR confirmação explícita"** | Aparenta controle humano sobre promoção crítica | Confirmação "sim" de "leigo em desenvolvimento" é tratada como válida. O relatório apresentado ao humano (Fase 3) descreve superfícies verificadas, não seu conteúdo ou qualidade. O humano não tem capacidade técnica para avaliar o que está confirmando. | Crítica | Falha de regra | Human-in-the-loop sem capacidade técnica de avaliação = rubber stamp institucionalizado. |
| **15 módulos em `implementation_ready`** | Aparenta sistema maduro com módulos prontos para desenvolvimento | `implementation_ready` é atingido via promoção cujo critério de pipeline é 7 gates sintáticos + 37 gates inativos. A promoção valida presença e não-vazio de artefatos, não qualidade ou correção normativa. | Alta | Falha de composição | O badge `implementation_ready` comunica maturidade que o sistema não verificou. |
| **Hierarquia de 13 níveis de precedência em §5** | Aparenta resolução determinística de conflitos normativos | Não há gate de detecção de conflito entre regras. O agente deve "inferir" precedência ao encontrar conflito. §5 define a hierarquia mas não provê mecanismo operacional para aplicá-la. | Alta | Falha de regra | Conflitos reais entre regras de níveis diferentes são resolvidos por inferência do LLM, não pelo sistema. |
| **Análise adversarial no TASK_CATALOG** como gate obrigatório para generate_code | Aparenta verificação de segurança antes de geração de código | Na readiness_promotion (caminho para `implementation_ready`), a adversarial analysis é não-bloqueante (S1 = aviso). Um módulo pode ser promovido sem analysis, e depois generate_code cria conflito: módulo está `implementation_ready` mas falta `ADVERSARIAL_ANALYSIS_GATE = PASS`. | Crítica | Falha de composição | Pipeline quebrado entre promoção e geração de código — os critérios não são coordenados. |

---

## PARTE 4 — FALHAS DE ROBUSTEZ REAL

| Falha | Tipo de falha | Severidade | Impacto prático | Cenário afetado | Correção necessária |
|---|---|---|---|---|---|
| **DERIVED_DRIFT_GATE referenciado em readiness_promotion mas ausente em latest.json** | Falha de composição | Crítica | Gate de promoção exige verificação de gate que não existe no pipeline. A promoção de módulos viola seu próprio critério P2 silenciosamente. | Todos os 15 módulos promovidos a `implementation_ready` | Criar o gate DERIVED_DRIFT_GATE no pipeline de validação OU remover a referência de P2 e documentar explicitamente que esse critério não é verificado. |
| **§2A.2 "prompts não são fonte substantiva" vs. sistema implementado como prompts** | Falha de regra | Crítica | Contradição sistêmica: a regra declara que prompts não criam obrigações, mas toda a execução normativa (readiness_promotion, generate_code, pre_contract_orchestrator) vive em .prompt.md files. O agente não pode aplicar §2A.2 sem suspender toda sua operação. | Todo o pipeline | Ou promover as regras dos prompts para artefatos canônicos (RULES/LAYOUT), ou revogar §2A.2, ou separar claramente "regras normativas" de "instruções de execução" com definições operacionais distintas. |
| **37/44 gates SKIP_NOT_APPLICABLE incluindo gates `blocking: true`** | Falha de regra | Crítica | O sistema de gates não impõe as verificações para as quais foi projetado. Gates como `OWASP_API_CONTROL_MATRIX_GATE`, `MODULE_REGISTRY_GATE`, `BOUNDARY_*_GATE` são sempre skip. Nunca há um estágio onde eles se tornam obrigatórios. | Todo o pipeline de validação | Definir explicitamente em qual estágio cada gate muda de SKIP para obrigatório. Criar regra de que nenhum módulo pode atingir `implementation_ready` com gates `blocking: true` em SKIP. |
| **Análise adversarial não-bloqueante em S1 de readiness_promotion** | Falha de regra | Crítica | 15 módulos em `implementation_ready` sem evidência verificável de análise adversarial. A geração de código fica em conflito: TASK_CATALOG exige `ADVERSARIAL_ANALYSIS_GATE = PASS` para `generate_code`, mas o caminho canônico para `implementation_ready` não impõe isso. | Todos os módulos, especialmente ao acionar generate_code | Tornar adversarial analysis bloqueante em readiness_promotion, não apenas aviso. |
| **SESSION_HANDOFF.md é opcional, efêmero e sem schema** | Falha de template | Alta | Agentes em novas sessões operam sem contexto das decisões tomadas em sessões anteriores. Não há schema que defina o que o arquivo DEVE conter. Conteúdo mínimo ("sessão anterior fez X") passa como SESSION_HANDOFF válido. | Toda tarefa multi-sessão | Criar schema JSON para SESSION_HANDOFF.md. Criar gate que verifica presença e conformidade ao schema em tarefas que dependem de contexto contínuo. |
| **"Confirmação explícita do humano" sem critério de validade** | Falha de regra | Alta | A confirmação que desbloqueia promoção de módulo pode ser qualquer string afirmativa. "ok", "sim", "pode", "vai" — todas equivalentes. O humano é explicitamente descrito como leigo em desenvolvimento. | readiness_promotion Fase 4 | Definir o que constitui confirmação válida. Pelo menos: o humano deve confirmar que leu e entendeu o relatório de superfícies, não apenas aprovar a promoção. Alternativamente, exigir segunda verificação de artefato após confirmação. |
| **Verificação de conteúdo de superfícies = existência + não-vazio** | Falha de template | Alta | Um arquivo de 10 bytes que não é vazio passa a verificação de readiness_promotion. Um UI_CONTRACT com seções incompletas mas sem a string "TODO" literal passa PLACEHOLDER_RESIDUE_GATE. Mínimos aceitáveis não são definidos por superfície. | Auditoria de superfícies na promoção | Definir limites mínimos por superfície: tamanho mínimo em bytes OU número mínimo de seções obrigatórias preenchidas. Criar gate que verifica schema de conteúdo, não apenas presença. |
| **Gap resolution (G-01 a G-06 em UI_CONTRACT_TRAINING) sem gate de verificação** | Falha do contrato final | Alta | O UI_CONTRACT_TRAINING documenta 6 gaps e afirma resolvê-los na seção correspondente. Não há gate que verifica se a resolução foi propagada para os contratos OpenAPI, AsyncAPI ou schemas afetados. | Módulo training (e possivelmente outros com gaps documentados) | Criar processo de rastreamento de gaps com gate de verificação: gap aberto não pode coexistir com status `implementation_ready`. |
| **SLAs declarados em GLOBAL_INVARIANTS sem gate de verificação de declaração** | Falha de regra | Alta | GI-007 exige que módulos live declarem SLA de latência. SLA-LIVE-001 (3s para live scouting) é declarado no documento global, mas não há gate que verifique se os módulos afetados declaram e respeitam esses SLAs em seus contratos individuais. | Módulos: training, scout, analytics, matches | Criar gate SLA_DECLARATION_GATE que verifica que cada módulo que afeta contexto live declara SLA compatível com GI. |
| **Ausência de controle de versão de waivers** | Falha de template | Média | `_waivers/` contém 3 arquivos mas não há schema de waiver com campo `expires_at`, `approved_by`, `gates_affected`. Um waiver arquivado permanece ativo indefinidamente. | Qualquer gate com waiver ativo | Criar schema de waiver com expiração obrigatória e gate que rejeita waivers vencidos. |
| **Precedência de 13 níveis sem mecanismo de detecção de conflito** | Falha de regra | Média | Quando uma regra em ADR contradiz uma regra em CONTRACT_SYSTEM_RULES.md, o agente deve inferir a precedência. Não há gate de detecção de conflito. O agente pode resolver o conflito de forma diferente em sessões distintas. | Toda tarefa que envolve regras de múltiplos artefatos normativos | Criar checklist de conflito explícito: ao criar ou atualizar ADR, verificar se contradiz regra em nível superior da hierarquia. Se sim, emitir BLOCKED_PRECEDENCE_CONFLICT. |
| **Arazzo workflows para apenas 13 dos 16 módulos** | Falha do contrato final | Média | O `READINESS_DASHBOARD.md` e o `latest.json` mostram módulos em `implementation_ready` mas sem cobertura completa de workflows Arazzo. `analytics`, `medical`, `reports` não têm workflows — ou os têm e não foram identificados. A ausência de cobertura não bloqueia promoção. | Módulos sem Arazzo workflows | Clarificar se Arazzo é superfície obrigatória para todos os módulos ou apenas os que declaram em `expected_surfaces`. Se obrigatório, fazer bloqueante. |
| **OpenAPI generated vs. source tem divergência: 5 módulos ausentes** | Falha do contrato final | Média | `generated/contracts/openapi/openapi.yaml` não tem `analytics`, `medical`, `reports`, `scout`, `video` enquanto `contracts/openapi/openapi.yaml` os tem. Não há gate que verifique completude de cobertura do generated vs. source. | Geração de código para os módulos ausentes | O DERIVED_DRIFT_GATE (que não existe no pipeline) deveria cobrir isso. Criar gate de verificação de completude. |

---

## PARTE 5 — ANÁLISE DA ORIGEM (TEMPLATE + REGRAS)

| Problema observado | Origem provável | Evidência | Efeito no contrato final | Correção na origem |
|---|---|---|---|---|
| **Gates bloqueantes permanentemente inativos** | Falha de regra + composição | latest.json: 37 gates com `blocking: true` e `status: SKIP_NOT_APPLICABLE`, `summary: "Pulado no estágio 'artifact'"`. Nenhum estágio tem gate de transição que ative-os. | O sistema nunca executa verificações que declarou como bloqueantes. Todo o pipeline de qualidade declarado não ocorre na prática. | Criar regra explícita em CONTRACT_SYSTEM_RULES.md e GATES_REGISTRY.yaml definindo em qual estágio cada gate passa de SKIP para obrigatório. O estágio `artifact` não pode ser um master-bypass implícito. |
| **Execução normativa em LLM (prompts como mecanismo)** | Falha estrutural de template | Todo worker vive em .prompt.md. CONTRACT_SYSTEM_RULES §2A.2 diz que prompts não são fonte substantiva — mas são o único mecanismo de execução. | Comportamento não-determinístico session-dependent. A mesma tarefa pode produzir resultados diferentes em sessões distintas sem violar nenhuma regra explícita. | Separar claramente: regras normativas em artefatos canônicos verificáveis por ferramentas; prompts apenas como instruções de execução já-validadas por gates anteriores. |
| **Adversarial analysis como aviso em readiness_promotion** | Falha de regra isolada | readiness_promotion.prompt.md §S1: "emitir aviso (não bloquear)". TASK_CATALOG: generate_code.blocking_gates inclui `ADVERSARIAL_ANALYSIS_GATE`. | Pipeline incoerente: módulo pode estar `implementation_ready` mas gerar bloqueio ao tentar usar generate_code. Os dois documentos não foram harmonizados. | Harmonizar: se generate_code requer ADVERSARIAL_ANALYSIS_GATE = PASS, então readiness_promotion deve exigir adversarial analysis executada antes de promover. |
| **DERIVED_DRIFT_GATE ausente em pipeline mas referenciado em regra** | Falha de composição | readiness_promotion.prompt.md P2 exige verificar DERIVED_DRIFT_GATE. latest.json não contém nenhuma entrada com esse gate_id. | Critério de promoção é verificado contra um gate que não existe. O verificador (agente LLM) não pode confirmar esse critério. | Implementar DERIVED_DRIFT_GATE no pipeline de validação (validate_contracts.py) OU remover a referência de P2 e substituir por verificação alternativa. |
| **Verificação de superfícies = presença + não-vazio** | Falha de template de módulo | readiness_promotion.prompt.md Fase 2: "Verificar que o artefato existe, não está vazio, sem placeholders". Não há critério de completude de conteúdo. | Superfícies mínimas passam. Um README.md com 5 linhas não é vazio e não contém "TODO" literal — passa. Um PERMISSIONS.md com uma tabela vazia passes. | Criar por template de superfície um critério mínimo de conteúdo: número de seções obrigatórias, palavras-chave esperadas, tamanho mínimo por tipo de artefato. |
| **Excesso de padronização na estrutura, baixa densidade normativa nas regras** | Falha de template | CONTRACT_SYSTEM_RULES.md §5 lista 13 níveis de precedência mas não define como detectar ou resolver conflito. §9 lista 18 BLOCKED codes mas não define resolução para 15 deles. | A estrutura organizacional cria aparência de completude sem preencher os requisitos operacionais que justificariam essa estrutura. | Para cada BLOCKED code: definir path de resolução, critério de conclusão, responsável. Para cada nível de precedência: criar detection rule aplicável por gate ou agente. |

---

## PARTE 6 — CASOS DE QUEBRA

| Cenário de quebra | Condição | Ponto de falha | Consequência | Severidade | Origem da falha | Correção |
|---|---|---|---|---|---|---|
| **Pipeline verde com contratos semanticamente incorretos** | Agente cria contrato OpenAPI que passa lint (redocly) mas viola regras de domínio (ex: endpoint de treino sem autenticação) | OPENAPI_ROOT_STRUCTURE_GATE verifica lint, não semântica. OWASP_API_CONTROL_MATRIX_GATE está SKIP. | Contrato implementado em código com vulnerabilidade de segurança. Pipeline nunca sinalizou o problema. | Crítica | Falha de regra (gate inativo) | Ativar OWASP_API_CONTROL_MATRIX_GATE no estágio de contrato, não apenas em deployment. |
| **Módulo promovido sem adversarial analysis, generate_code bloqueado** | Módulo X está em `validated_contract`. Readiness promotion executa sem adversarial analysis (S1 = aviso). Módulo promovido para `implementation_ready`. Agente tenta generate_code. | TASK_CATALOG: generate_code requer `ADVERSARIAL_ANALYSIS_GATE = PASS`. Gate não existe como check ativo. Agente LLM bloqueia ou ignora — comportamento inconsistente. | Ou generate_code é bloqueado (módulo promovido sem poder gerar código — contradição de `implementation_ready`), ou o requisito é ignorado (código gerado sem análise de segurança). | Crítica | Falha de composição | Harmonizar critérios: adversarial analysis deve ser pré-condição para `implementation_ready`, não pós-condição para `generate_code`. |
| **Agente novo em sessão sem SESSION_HANDOFF.md** | Sessão anterior terminou. SESSION_HANDOFF.md não foi criado. Nova sessão inicia tarefa de contrato. | AGENT_INSTRUCTIONS: "IF SESSION_HANDOFF.md exists → ler". Condição é opcional. Agente não sabe o que foi decidido antes. | Agente toma decisões que contradizem decisões de sessões anteriores. Conflitos de contrato não detectados por nenhum gate. | Alta | Falha de template | Tornar SESSION_HANDOFF.md criação obrigatória ao final de qualquer sessão com artefatos modificados. Criar gate PRE_CONTRACT_EVIDENCE_GATE (já listado mas SKIP) que verifica presença e schema do handoff. |
| **ASYNCAPI_VALIDATION nunca executada** | Sistema tem 47+ canais async documentados. AsyncAPI validator instalado (@asyncapi/cli/6.0.0). | ASYNCAPI_VALIDATION gate é SKIP. O validator nunca é invocado. | Contratos async podem ter erros de schema, referências quebradas, tipos incoerentes. Nunca detectado antes de implementação. | Alta | Falha de regra | Ativar ASYNCAPI_VALIDATION como gate bloqueante antes de qualquer promoção de módulo que declare superfície `asyncapi`. |
| **Gate downgrade após promoção** | Módulo Y é promovido para `implementation_ready` com contratos corretos. Módulo Z (dependente) tem contrato modificado que quebra $ref cross-module. `hb verify` no módulo Z passa (ou é rodado apenas no escopo de Z). | Nenhum gate reverifica módulos já promovidos quando suas dependências mudam. MODULE_Y permanece `implementation_ready` com contrato quebrado. | Código de implementação gerado a partir de contrato incoerente. Erro aparece em runtime, não em pipeline. | Alta | Falha de regra | Criar trigger de re-validação: ao modificar qualquer contrato, identificar módulos dependentes e re-validar gates de cross-module para todos. |
| **Human confirmation como rubber stamp** | Agente apresenta relatório de promoção de módulo com 13 superfícies verificadas. Humano (leigo) responde "sim" sem entender o relatório. | readiness_promotion Fase 4 executa imediatamente após "sim". Não há verificação de que o humano entendeu o que estava confirmando. | Módulo promovido com problemas reais que o humano teria rejeitado se compreendesse o relatório. | Alta | Falha de regra | Exigir que o humano responda a pelo menos 1 pergunta de verificação específica sobre o conteúdo antes de confirmar. Ou documentar explicitamente no relatório os riscos conhecidos em linguagem de produto. |
| **Waiver expirado silencioso** | `_waivers/` contém 3 arquivos criados em data não registrada. Gate X estava com waiver ativo. Versão nova do sistema é deployada. Gate X deveria ser PASS mas ainda está waivered. | Nenhum gate verifica se waivers estão vencidos. latest.json simplesmente não menciona gates com waiver ativo — eles aparecem como SKIP sem distinguir entre "SKIP por estágio" e "SKIP por waiver". | Gate que deveria bloquear deployment está permanentemente waivered sem ninguém perceber. | Média | Falha de template | Criar schema de waiver com `expires_at` obrigatório. Criar gate WAIVER_VALIDITY_GATE que rejeita waivers vencidos. |
| **Placeholder literal vs. conceitual** | PLACEHOLDER_RESIDUE_GATE verifica 315 arquivos e encontra 0 placeholders. Gate PASS. Contrato contém "Ver documentação da regra de handebol para definição completa" em seção de business rules. | A string não contém "TODO", "[PLACEHOLDER]", "TBD", "..." explícitos. Gate passa. Mas a seção é semanticamente incompleta. | Contrato promovido para `implementation_ready` com regras de domínio referenciando documentação externa em vez de definir a regra diretamente. Agente de geração de código não tem a regra completa. | Média | Falha de template | Expandir PLACEHOLDER_RESIDUE_GATE para incluir padrões de referência-sem-conteúdo: "Ver X", "Conforme X", "Definido em X". Ou criar gate de completude de business rules. |

---

## PARTE 7 — TESTE DE LOOPHOLES

| Loophole | Como o contrato permite isso | Impacto | Severidade | Correção |
|---|---|---|---|---|
| **Promover módulo para `implementation_ready` sem análise adversarial, satisfazendo todos os critérios formais** | readiness_promotion.prompt.md S1: adversarial analysis é "aviso, não bloqueia". P1 (status=validated_contract), P2 (overall_status=PASS), P3 (sem decisões abertas) — todos podem ser satisfeitos sem adversarial analysis. O relatório Fase 3 lista "⚠️ Avisos" que o humano leigo ignora. Confirmação "sim" recebida. Promoção executada. | 15 módulos em `implementation_ready` sem verificação de segurança executada. Código gerado a partir desses contratos pode ter vulnerabilidades não detectadas. | Crítica | Tornar adversarial analysis pre-condição bloqueante para `implementation_ready`. |
| **Criar contrato OpenAPI sintaticamente correto mas semanticamente inconsistente com as regras de domínio** | OPENAPI_ROOT_STRUCTURE_GATE verifica apenas lint estrutural (redocly). OWASP_API_CONTROL_MATRIX_GATE está SKIP. Não há gate que verifique se as operações declaradas são semanticamente coerentes com DOMAIN_RULES, GLOBAL_INVARIANTS ou HANDBALL_RULES_DOMAIN. Um contrato pode declarar `PATCH /training-sessions/{id}` sem restrição de janela de 10 minutos e passar todos os 7 gates ativos. | Implementação gerada viola regras de negócio que o contrato deveria ter codificado. Regra de janela de edição (core do domínio) inexistente no contrato sem detecção. | Crítica | Criar DOMAIN_RULES_COMPLIANCE_GATE que verifica presença de regras críticas de domínio nos endpoints afetados. |
| **Satisfazer verificação de superfícies com conteúdo mínimo não-vazio** | Fase 2 de readiness_promotion verifica: (1) arquivo existe, (2) arquivo não está vazio, (3) sem placeholders literais. Um `TEST_MATRIX_TRAINING.md` com uma tabela de 2 linhas sem casos de teste reais, mas com conteúdo não-vazio e sem "TODO" literal, passa a verificação. A superfície `test_matrix` fica marcada como verificada. | Módulo `implementation_ready` sem test matrix real. Generate_code é acionado sem matriz de testes que guie a geração. Testes gerados são superficiais. | Alta | Definir estrutura mínima por tipo de superfície. Para test_matrix: número mínimo de casos de teste por endpoint. Para permissions: número mínimo de roles cobertos. Para state_model: número mínimo de transições documentadas. |
| **Executar múltiplas sessões de agente em paralelo em módulos interdependentes sem detecção de conflito** | O sistema de contratos não tem mecanismo de lock ou detecção de concorrência. Dois agentes podem modificar contratos de módulos que referenciam um ao outro via $ref cross-module. Ambos executam `hb verify` nos seus contextos individuais. Ambos recebem PASS. | Contratos em conflito de $ref cross-module chegam ao estado `implementation_ready`. Conflito só detectado durante geração de código ou em runtime. | Alta | Criar mecanismo de lock de módulo durante tarefa ativa. Criar gate de validação cross-module que verifica integridade de $refs para todos os módulos quando qualquer contrato é modificado. |
| **Emitir BLOCKED_* e continuar a tarefa na mesma sessão se o humano não responder** | O sistema define bloqueios mas não especifica o que acontece se o bloqueio não for resolvido e o agente continuar. A maioria dos prompts usa "bloquear" como instrução para o agente, mas não como mecanismo técnico que interrompe execução. Um agente que recebe BLOCKED_REQUIRED_ARTIFACT_MISSING pode — dependendo do tom da conversa com o humano — continuar com inferências se o humano disser "pode continuar mesmo assim". | Regras de bloqueio são bypassed via conversação informal. O sistema normativo é contornado pela interface conversacional. | Alta | Definir BLOCKED_* como estados irrevogáveis sem resolução formal documentada no artefato canônico correspondente. Criar distinção entre "aviso" e "bloqueio técnico" — bloqueios técnicos não devem ser contornáveis por instrução conversacional. |
| **Usar `hb artifact` para registrar artefato não-conforme como canônico** | `hb artifact <path>` registra o artefato no pipeline. Não há documentação explícita do que o comando verifica além de gerar rastreabilidade. Se o comando apenas registra o path e gera SHA sem verificar conformidade normativa, um artefato com problemas pode ser "registrado como canônico" sem ser canônico. | Artefatos com problemas recebem SHA e são tratados como validados pelo sistema. | Média | Documentar explicitamente o que `hb artifact` verifica. Se é apenas registro, renomear para `hb register` para evitar a implicação de validação. |

---

## PARTE 8 — CORREÇÕES RECOMENDADAS

### Correções no template

1. **SESSION_HANDOFF.md schema obrigatório**: Criar `contracts/schemas/shared/session_handoff.schema.json` com campos obrigatórios: `session_id`, `timestamp`, `modules_modified[]`, `decisions_made[]`, `open_blockers[]`, `next_session_context`. Tornar criação obrigatória ao final de qualquer sessão que modifique artefatos canônicos.

2. **Critérios mínimos por superfície**: Para cada tipo de superfície em readiness_promotion (module_docs_minimum, openapi_sync, json_schema, asyncapi, etc.), definir: (a) tamanho mínimo em bytes, (b) seções obrigatórias que devem estar preenchidas, (c) padrões de completude específicos. Incluir em template de módulo.

3. **Schema de waiver**: Criar `contracts/schemas/shared/waiver.schema.json` com campos: `gate_id`, `approved_by`, `approved_at`, `expires_at`, `justification`, `risk_acknowledged`. Tornar `expires_at` obrigatório. Gate WAIVER_VALIDITY_GATE deve rejeitar waivers vencidos.

4. **Separar BLOCKED_* com e sem path de resolução**: Template de bloqueio deve ter: para cada código BLOCKED_, documentar (a) quem resolve, (b) como resolve, (c) critério de conclusão, (d) prazo máximo esperado. Atualizar §9 de CONTRACT_SYSTEM_RULES.md.

### Correções nas regras

5. **Tornar adversarial analysis bloqueante em readiness_promotion**: Alterar S1 de "emitir aviso" para "bloquear com BLOCKED_ADVERSARIAL_PENDING". Harmonizar com TASK_CATALOG que já declara esse gate como obrigatório para generate_code.

6. **Definir estágio de transição para cada gate**: Em GATES_REGISTRY.yaml, para cada gate atualmente SKIP_NOT_APPLICABLE em `artifact`, definir em qual estágio (pre_contract, contract_review, readiness_promotion, pre_generate_code, pre_deployment) o gate se torna obrigatório. Eliminar o uso de `artifact` como master-bypass implícito.

7. **Revogar ou reescrever §2A.2**: A regra "prompts não são fonte substantiva" é verdadeira em teoria mas falsa na prática. Ou (a) promover as regras dos prompts para artefatos canônicos e reduzir os prompts a referências de execução, ou (b) reconhecer que os prompts são fonte substantiva de segundo nível e criar regra que governa como prompts podem criar obrigações derivadas.

8. **Criar regra de re-validação cross-module**: Ao modificar contrato de qualquer módulo, identificar via SCOPE_BOUNDARY_GATE todos os módulos que referenciam esse contrato e re-executar seus gates de boundary. Documentar essa regra em CONTRACT_SYSTEM_RULES.md como invariante de pipeline.

### Correções na lógica de composição

9. **Criar DERIVED_DRIFT_GATE no pipeline**: Implementar o gate referenciado em readiness_promotion P2. O gate deve verificar que artefatos em `generated/` estão em sincronia com os artefatos em `contracts/`. SHAs dos manifestos em `generated/manifests/` devem bater com os SHAs atuais dos arquivos fonte.

10. **Ativar ASYNCAPI_VALIDATION antes de promoção de módulos async**: Qualquer módulo com superfície `asyncapi` declarada em `expected_surfaces` deve ter `ASYNCAPI_VALIDATION = PASS` (não SKIP) antes de `implementation_ready`.

11. **Resolver conflito adversarial: readiness_promotion vs. TASK_CATALOG**: Os dois documentos têm critérios diferentes para adversarial analysis. Criar regra explícita: adversarial analysis é pré-condição para `implementation_ready` (unificar os dois documentos).

12. **Distinguir `PASS via 0 gates ativo` de `PASS via gates verificados`**: O overall_status deve refletir explicitamente quantos gates foram ativamente verificados vs. skipped. Criar `active_pass_count` no relatório. Promoção deve exigir `active_pass_count >= X` (valor a definir), não apenas `overall_status = PASS`.

### Correções no contrato final

13. **Verificar e resolver os 6 gaps G-01 a G-06 do UI_CONTRACT_TRAINING com gate**: Cada gap declarado como "resolvido" no UI_CONTRACT_TRAINING.md deve ter evidência verificável de resolução: referência ao endpoint/schema/evento que implementa a resolução. Criar lista de gaps com ponteiros para artefatos.

14. **Verificar cobertura de OpenAPI generated vs. source**: 5 módulos (`analytics`, `medical`, `reports`, `scout`, `video`) ausentes no generated OpenAPI. Verificar se é intencional ou deriva não detectada. Se intencional, documentar explicitamente. Se deriva, criar gate de verificação de completude.

15. **Declarar SLAs nos contratos de módulo, não apenas em GLOBAL_INVARIANTS**: GI-007 exige que módulos live declarem SLA de latência. Criar campo `sla` nos schemas de módulo de training, scout, analytics, matches. O GLOBAL_INVARIANTS declara a invariante mas os contratos de módulo não implementam a declaração.

---

## PARTE 9 — VEREDITO FINAL

**Este contrato governa comportamento real ou só aparenta governar?**

Aparenta. A arquitetura normativa é sofisticada e bem-intencionada, mas o mecanismo de enforcement real é substancialmente mais fraco do que o declarado. O comportamento efetivo dos agentes é governado por 7 gates sintáticos + interpretação LLM de Markdown + confirmação informal de humano leigo. O restante da estrutura (909 linhas de regras, 44 gates, 13 níveis de precedência, hierarquia de soberania) existe como documentação aspiracional sem enforcement técnico correspondente.

**Ele resiste a uso real e casos limite?**

Não. Os cenários de quebra descritos na Parte 6 — módulo promovido sem adversarial analysis, contratos AsyncAPI nunca validados, SESSION_HANDOFF ausente, DERIVED_DRIFT_GATE inexistente, human confirmation como rubber stamp — não são cenários hipotéticos improváveis. São os cenários normais de uso cotidiano do sistema.

**Ele está em nível 100/100 de robustez?**

Não. Score atual: **47/100**. Abaixo do limiar de 60 que define "adequado para sustentar robustez contratual forte".

**O que falta para atingir esse nível?**

Em ordem de impacto:
1. Ativar os 37 gates inativos com critérios claros de estágio — especialmente ASYNCAPI_VALIDATION, OWASP_API_CONTROL_MATRIX_GATE, MODULE_REGISTRY_GATE, BOUNDARY_*_GATE.
2. Implementar DERIVED_DRIFT_GATE (gate referenciado mas inexistente).
3. Tornar adversarial analysis bloqueante antes de `implementation_ready`.
4. Criar e validar SESSION_HANDOFF schema.
5. Definir critérios mínimos de conteúdo por tipo de superfície.
6. Resolver a contradição §2A.2 vs. realidade de prompts como executores normativos.
7. Criar detecção de conflito cross-module com re-validação automática.
8. Substituir `overall_status = PASS` por métrica composta que exige gates ativos, não apenas gates definidos.

**A origem do problema está mais no template, nas regras, na composição ou no contrato final?**

**Nas regras e na composição**, em proporções aproximadamente iguais.

- **Regras**: Gates declarados como `blocking: true` nunca são executados porque a regra não define quando o estágio de bypass termina. A regra de adversarial analysis conflita entre dois documentos normativos. A regra de confirmação humana não define critério de validade.

- **Composição**: readiness_promotion e generate_code têm critérios desarmoniozados para adversarial analysis. DERIVED_DRIFT_GATE referenciado em promoção não existe no pipeline. O "PASS" do overall_status é composição matemática que mascara cobertura real.

- **Templates**: Verificação de superfícies por presença/não-vazio sem critério de completude é insuficiente mas não é o problema raiz — é sintoma de regras que não definem o que "suficiente" significa.

- **Contrato final**: Os contratos gerados (OpenAPI, AsyncAPI, schemas) são tecnicamente corretos no que cobrem. O problema não está no que o contrato diz, mas no que o sistema decide não verificar antes de declará-lo pronto.

---

*Auditoria conduzida com postura severa conforme instruções. Nenhuma fragilidade foi ocultada ou minimizada. O objetivo deste documento é expor onde o sistema falha em governar comportamento real, não avaliar qualidade editorial ou maturidade organizacional.*

**Score final: 47/100 — contrato bonito, mas frágil.**
