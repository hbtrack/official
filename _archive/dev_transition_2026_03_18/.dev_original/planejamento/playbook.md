# Playbook HB Track — Uso de IA no pré-contrato e na descoberta de decisões arquiteturais

## 1. Objetivo

Usar IA como mecanismo de **Decision Discovery (DSS)** antes de `contract_creation_mode`, `contract_revision_mode`, `implementation_mode` ou `audit_mode`, para aumentar cobertura analítica, explicitar trade-offs e preparar promoção formal para ADR, sem transferir à IA a soberania decisória.

No HB Track:

* contrato e canon continuam sendo referência normativa;
* ADR continua sendo artefato de explicação;
* IA atua como apoio analítico e de estruturação;
* decisão obrigatória aberta impede prosseguimento do fluxo até resolução formal.  

## 2. Princípio operacional

A IA **não decide arquitetura sozinha**.

Ela pode:

* detectar lacunas arquiteturais;
* estruturar alternativas;
* articular trade-offs;
* redigir proposta DSS;
* preparar ADR candidato;
* montar Impact Map;
* testar riscos, reversibilidade e cenários adversariais.

Ela não pode:

* promover decisão sem aprovação humana;
* inventar restrições não documentadas;
* acionar worker de contrato sem fase pré-contrato concluída;
* tratar texto bem escrito como evidência normativa.   

## 3. Quando usar este playbook

Usar este playbook quando houver:

* decisão arquitetural relevante antes de criar ou revisar contrato;
* revisão de arquitetura (`task_type = architecture_review`);
* backlog com decisão `obrigatória` em aberto;
* lacuna de readiness arquitetural detectada na Fase 1 do orquestrador pré-contrato;
* temas como AUTH, AUTHZ, dados sensíveis, retenção, secrets, logging, timezone, depreciação, tenancy, fronteira de serviço, escolha de banco, estratégia síncrona/assíncrona, plataforma de execução, integração pública ou batch.  

## 4. Ponto de entrada obrigatório

Nenhuma tarefa contract-driven pode começar por “perguntar para a IA”.

A entrada correta é sempre:

`.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`

Se o fluxo pular essa etapa:

* parar imediatamente;
* emitir `BLOCKED_PRE_CONTRACT_SKIPPED`;
* reiniciar pelo orquestrador pré-contrato. 

## 5. Artefatos normativos envolvidos

Este playbook depende destes artefatos canônicos:

* `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
* `.contract_driven/CONTRACT_SYSTEM_RULES.md`
* `.contract_driven/GLOBAL_TEMPLATES.md`
* `.contract_driven/agent_prompts/pre_contract_orchestrator.prompt.md`
* `.contract_driven/agent_prompts/decision_discovery.prompt.md`
* `docs/_canon/DECISION_POLICY.md`
* `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
* `docs/_canon/decisions/ADR-*.md`
* docs do módulo afetado
* contratos do módulo afetado, quando aplicável.  

## 6. Fluxo canônico do playbook

### Fase 0 — Classificação e roteamento

Executar no `pre_contract_orchestrator`.

Entrada mínima:

* `module`
* `task_type`
* escopo da mudança
* recurso/entidade afetada, se houver

Regras:

* validar módulo na taxonomia do LAYOUT;
* validar `task_type`;
* identificar worker destino;
* se o worker não existir, emitir `BLOCKED_MISSING_AGENT_PROMPT`. 

### Fase 1 — Foundation Readiness

Executar no `pre_contract_orchestrator`.

Verificações:

1. presença de artefatos canônicos obrigatórios do módulo;
2. decisões arquiteturais bloqueantes no backlog;
3. checklist mínima de segurança de produção;
4. hermeticidade de derivados, quando aplicável. 

Se faltar artefato obrigatório:

* emitir `BLOCKED_REQUIRED_ARTIFACT_MISSING`.  

Se houver decisão `obrigatória` aberta:

* emitir `BLOCKED_MISSING_ARCH_DECISION`;
* acionar Fase 2.  

### Fase 2 — Decision Discovery (DSS)

Executar somente quando:

* Fase 1 detectar decisão bloqueante; ou
* `task_type = architecture_review`.  

Leitura mínima obrigatória:

1. `docs/_canon/DECISION_POLICY.md`
2. `docs/_canon/ARCHITECTURE_DECISION_BACKLOG.md`
3. ADRs relevantes
4. RULES
5. LAYOUT
6. `docs/_canon/ARCHITECTURE.md`
7. `docs/_canon/SECURITY_RULES.md`, se aplicável
8. `docs/_canon/DATA_CONVENTIONS.md`, se aplicável
9. `docs/_canon/HANDBALL_RULES_DOMAIN.md`, se gatilho esportivo ativo
10. `SPORT_SCIENCE_RULES_<MODULE>.md`, se aplicável
11. `MODULE_SCOPE_<MODULE>.md` 

### Fase 3 — Montagem paralela de contexto

Executar somente após PASS na Fase 1.

Carregar em paralelo, respeitando precedência:

* RULES
* LAYOUT
* `ARCHITECTURE.md`
* `SYSTEM_SCOPE.md`
* `DATA_CONVENTIONS.md`
* `ERROR_MODEL.md`, se contrato
* `SECURITY_RULES.md`, se contrato
* docs do módulo
* ADRs relevantes
* `HANDBALL_RULES_DOMAIN.md` e `SPORT_SCIENCE_RULES_<MODULE>.md`, quando o gatilho esportivo estiver ativo. 

### Fase 4 — Handoff ao worker

Somente com:

* Fase 1 = PASS
* Fase 3 concluída
* nenhuma decisão bloqueante em aberto

Saída obrigatória:

* módulo
* task
* worker destino
* artefatos lidos
* ADRs relevantes
* gatilho esportivo sim/não
* decisões pendentes remanescentes, se houver apenas avisos. 

## 7. Pacote de contexto obrigatório no HB Track

O “pacote de contexto” do playbook original deve ser convertido para o formato reconhecido pelo DSS do HB Track.

Ele não é um briefing solto. Ele deve ser ancorado em artefatos canônicos e conter, no mínimo:

* objetivo do módulo ou da mudança, conforme `MODULE_SCOPE_<MODULE>.md`
* regras de domínio, conforme `DOMAIN_RULES_<MODULE>.md`
* invariantes, conforme `INVARIANTS_<MODULE>.md`
* contratos e superfícies afetadas
* decisões já resolvidas por ADR
* decisões ainda abertas no backlog
* requisitos de segurança, dados e tempo, quando aplicáveis
* constraints de handebol e sport science, quando o gatilho esportivo estiver ativo
* classificação do sistema: produção vs. experimental/placeholder, quando relevante para bloqueio.  

Saída esperada:

* sumário estruturado de contexto
* lista de decisões abertas
* lista de artefatos normativos impactados

## 8. Exploração estruturada de alternativas

No HB Track, a IA nunca deve receber “qual a melhor arquitetura?”.

O pedido correto é:

“Com base nos artefatos canônicos lidos e nas decisões abertas identificadas, gere de 3 a 5 opções viáveis para o tópico `<decision_topic>`. Para cada opção, descreva: premissas, benefícios, trade-offs, custo de adoção, custo operacional, riscos principais, reversibilidade, condições em que a opção é inadequada, e pontos que exigem validação humana. Não promover decisão. Não criar contrato. Não assumir restrições não documentadas.”

Saída recomendada:

* tabela ou JSON estruturado conforme o template de proposta do `DECISION_POLICY.md` §5;
* sempre com `Impact Map` preliminar.  

## 9. Crítica adversarial obrigatória

No HB Track, a crítica adversarial deve existir antes de qualquer proposta de ADR aceita.

Pedido correto:

“Assuma que a opção preferida é `<X>`. Atue como arquiteto cético e identifique riscos não óbvios, overengineering, blast radius, custos ocultos, fragilidades operacionais, riscos de segurança, dificuldade de teste, impacto em observabilidade, incompatibilidade com o time atual e caminhos de rollback ou simplificação. Responda apenas com base no contexto canônico carregado e explicite as premissas.”

Essa etapa deve virar parte da proposta DSS ou do rationale do ADR candidato.

## 10. Teste de reversibilidade

A reversibilidade deve ser tratada como metadado da decisão, não só como reflexão informal.

Cada decisão analisada deve ser classificada em:

* reversibilidade baixa
* reversibilidade média
* reversibilidade alta

Heurística HB Track:

* alta irreversibilidade: banco, tenancy, fronteiras de serviço, modelo de dados, estratégia assíncrona, plataforma de execução, identidade e segurança;
* baixa irreversibilidade: nomes, organização interna, convenções, bibliotecas substituíveis.

Regra:

* quanto mais irreversível, maior a exigência de ADR explícita e revisão humana;
* nenhuma decisão de alta irreversibilidade deve prosseguir por “parece razoável”. Ela precisa de aprovação humana e promoção formal. 

## 11. Verificação de risco, compliance e operação

No HB Track, essa revisão deve ser orientada pelos artefatos normativos relevantes, especialmente:

* `SECURITY_RULES.md`
* `DATA_CONVENTIONS.md`
* `CHANGE_POLICY.md`
* `HANDBALL_RULES_DOMAIN.md`
* `SPORT_SCIENCE_RULES_<MODULE>.md`, quando aplicável. 

Pedido correto:

“Audite cada opção sob as lentes de segurança, compliance, custo total, operabilidade, observabilidade, escalabilidade realista e aderência ao domínio do HB Track. Identifique riscos concretos, controles compensatórios, lacunas canônicas e pontos que exigem validação externa.”

Se isso revelar lacuna obrigatória:

* registrar no backlog;
* emitir `BLOCKED_MISSING_ARCH_DECISION` se o item for obrigatório e estiver aberto. 

## 12. Rubrica de decisão

A rubrica pode existir, mas no HB Track ela é auxiliar e nunca soberana.

Critérios permitidos:

* aderência ao contexto canônico
* simplicidade
* custo inicial
* custo operacional
* segurança/compliance
* resiliência
* observabilidade
* velocidade de entrega
* adequação ao time
* reversibilidade

Regra:

* score ajuda comparação;
* score não substitui aprovação humana;
* score não autoriza promoção automática para ADR.

## 13. Saída correta do DSS

A saída do Decision Discovery deve conter:

1. decisões `obrigatória` em aberto, com bloqueio explícito;
2. decisões `importante` em aberto, com aviso;
3. proposta DSS estruturada para cada item relevante;
4. Impact Map:

   * quais artefatos canônicos precisam mudar;
   * quais ADRs precisam ser criadas;
   * quais gates devem ser executados;
5. instrução de aguardar aprovação humana.  

## 14. Geração do ADR candidato

Após análise madura e aprovação humana, a IA pode redigir um ADR candidato.

Estrutura mínima:

* título
* contexto
* problema
* restrições
* opções consideradas
* decisão proposta
* rationale
* riscos e mitigação
* consequências
* plano de revisão
* critérios de invalidação
* links para backlog e artefatos impactados

Regra:

* ADR é artefato de explicação;
* não substitui atualização dos artefatos normativos afetados;
* após ADR aceita, atualizar backlog para `resolved`, atualizar o canon impactado e rodar validação.  

## 15. Gate humano obrigatório

Nenhuma decisão sai do DSS diretamente para contrato ou implementação sem validação humana explícita.

Checklist mínimo:

* o contexto canônico está completo?
* os riscos operacionais foram entendidos?
* a opção é proporcional ao problema?
* o time atual consegue operar isso?
* existe caminho de rollback?
* existe complexidade sem evidência de necessidade?
* o Impact Map está completo?
* a decisão foi promovida para ADR aceita antes da execução? 

## 16. Anti-padrões proibidos no HB Track

Proibido:

* perguntar “qual a melhor arquitetura?” sem artefatos canônicos;
* usar a IA para legitimar decisão já tomada sem crítica adversarial;
* tratar score automático como aprovação;
* promover contrato sem fase pré-contrato concluída;
* promover decisão sem ADR aceita, quando ela for obrigatória;
* inventar restrições, módulos, endpoints, enums, estados, permissões ou integrações.  

## 17. Template curto HB Track

**Entrada**

* `module`
* `task_type`
* `decision_topic` (opcional)
* mudança pretendida
* artefatos já conhecidos
* dúvidas abertas

**Execução**

1. passar pelo `pre_contract_orchestrator`
2. se houver `BLOCKED_MISSING_ARCH_DECISION`, executar `decision_discovery`
3. gerar opções
4. rodar crítica adversarial
5. classificar reversibilidade
6. auditar risco/compliance/operação
7. gerar proposta DSS + Impact Map
8. aguardar aprovação humana
9. criar ADR
10. atualizar backlog
11. atualizar artefatos canônicos afetados
12. rodar validação
13. só então prosseguir para worker de contrato

## 18. Resultado esperado

Ao final, o HB Track produz:

* análise mais ampla e mais auditável;
* decisão arquitetural explicitada e rastreável;
* backlog atualizado;
* ADR aceita;
* canon reconciliado;
* contrato iniciado apenas depois de readiness arquitetural e aprovação humana.

Em uma frase: no HB Track, IA no pré-ADR não é um “consultor solto”; é um estágio formal de **Decision Discovery governado por canon, backlog, bloqueios e promoção para ADR**.
