# CHECKLIST — VERIFICAÇÃO REAL DAS PREMISSAS DO HB Track

Marque `[x]` de acordo com a evidência real encontrada no ambiente do HB Track, seguindo os critérios definidos em cada seção. 

## 1. Premissas já resolvidas por decisão Humana

Marque `[x]` se confirmado.

* [x] Eu aceito seguir contrato antes do código
* [x] Eu aceito usar a tríade canônica como autoridade:

  * [x] `CONTRACT_SYSTEM_LAYOUT.md`
  * [x] `CONTRACT_SYSTEM_RULES.md`
  * [x] `GLOBAL_TEMPLATES.md`
* [x] Eu aceito a taxonomia canônica dos 16 módulos
* [x] Eu aceito strict mode: bloquear em vez de inferir
* [x] Eu aceito boot mínimo por tarefa
* [x] Eu aceito DoD binário para contrato e módulo

---

## 2. Artefatos canônicos presentes no repositório

* [x] `CONTRACT_SYSTEM_LAYOUT.md` existe
* [x] `CONTRACT_SYSTEM_RULES.md` existe
* [x] `GLOBAL_TEMPLATES.md` existe
* [ ] `SYSTEM_SCOPE.md` existe
* [x] `ARCHITECTURE.md` existe (em docs/product/)
* [ ] `MODULE_MAP.md` existe
* [ ] `CHANGE_POLICY.md` existe
* [ ] `API_CONVENTIONS.md` existe
* [ ] `DATA_CONVENTIONS.md` existe
* [ ] `ERROR_MODEL.md` existe
* [ ] `GLOBAL_INVARIANTS.md` existe
* [ ] `DOMAIN_GLOSSARY.md` existe
* [ ] `HANDBALL_RULES_DOMAIN.md` existe
* [ ] `SECURITY_RULES.md` existe
* [ ] `CI_CONTRACT_GATES.md` existe
* [ ] `TEST_STRATEGY.md` existe
* [ ] `C4_CONTEXT.md` existe
* [ ] `C4_CONTAINERS.md` existe
* [ ] `UI_FOUNDATIONS.md` existe
* [ ] `DESIGN_SYSTEM.md` existe

---

## 3. Estrutura real de contratos no repositório

* [ ] `contracts/openapi/openapi.yaml` existe
* [ ] `contracts/openapi/paths/` existe
* [ ] `contracts/schemas/` existe
* [ ] `contracts/workflows/` existe
* [ ] `contracts/asyncapi/` existe
* [ ] a árvore real segue o layout canônico
* [ ] não existem contratos fora da árvore canônica
* [x] não existem módulos fora da taxonomia (módulos ATLETAS, TRAINING, TEAMS, SCOUT, COMPETITIONS estão documentados)

---

## 4. Ferramentas instaladas

Marque `[x]` só se o comando roda no seu ambiente.

* [x] Redocly CLI instalado
* [ ] Spectral instalado
* [ ] oasdiff instalado
* [x] Schemathesis instalado (no venv do backend)
* [ ] validador JSON Schema instalado
* [ ] validator/parser AsyncAPI instalado
* [ ] validator/linter Arazzo instalado
* [ ] Storybook disponível, se houver UI documentada

---

## 5. Ferramentas funcionando de verdade

Marque `[x]` só se você executou e obteve resultado real.

* [x] Redocly roda contra OpenAPI do módulo ATLETAS (validado com sucesso)
* [ ] Spectral roda contra a spec OpenAPI
* [ ] oasdiff roda entre duas versões da spec
* [ ] Schemathesis roda contra uma API real ou ambiente local
* [ ] JSON Schema validator roda nos schemas do projeto
* [ ] AsyncAPI validator roda no contrato atual
* [ ] Arazzo validator roda nos workflows atuais
* [ ] Storybook build roda, se aplicável

---

## 6. Enforcement real

* [ ] existe script/comando único para validar contratos
* [ ] existe rotina de falha quando o contrato está inválido
* [ ] existe rotina de falha para breaking change
* [ ] existe rotina de falha para drift entre fonte soberana e derivado
* [ ] existe rotina de falha quando placeholder residual aparece
* [ ] existe rotina de falha quando artefato obrigatório está ausente

---

## 7. Artefatos gerados

* [ ] existe pasta canônica para artefatos gerados
* [ ] tipos gerados vão sempre para essa pasta
* [ ] clientes gerados vão sempre para essa pasta
* [ ] docs geradas vão sempre para essa pasta
* [ ] artefatos gerados não são editados manualmente
* [ ] artefatos gerados são regeneráveis
* [ ] drift entre gerado e soberano é detectável

---

## 8. Agente / fluxo operacional

* [ ] o agente realmente usa a ordem de boot definida
* [ ] o agente realmente usa boot mínimo por tarefa
* [ ] o agente realmente bloqueia em lacuna crítica
* [ ] o agente realmente emite códigos de bloqueio fechados
* [ ] o agente não cria módulo fora da taxonomia
* [ ] o agente não cria path fora de contrato
* [ ] o agente não cria evento fora de AsyncAPI
* [ ] o agente não cria workflow sem Arazzo
* [ ] o agente não cria regra esportiva fora de `HANDBALL_RULES_DOMAIN.md`

---

## 9. Domínio do handebol

* [ ] `HANDBALL_RULES_DOMAIN.md` existe e está utilizável
* [ ] cobre regras que impactam `training`
* [ ] cobre regras que impactam `matches`
* [ ] cobre regras que impactam `scout`
* [ ] cobre regras que impactam `competitions`
* [ ] adaptações locais do produto estão registradas
* [ ] não há regra esportiva crítica ainda “na cabeça” e fora do documento

---

## 10. Módulos reais já aderentes ao manual

Para cada módulo já existente, verificar:

**Módulo ATLETAS:**
* [ ] possui `README`
* [ ] possui `MODULE_SCOPE`
* [ ] possui `DOMAIN_RULES`
* [x] possui `INVARIANTS` (15_ATLETAS_INVARIANTS.yaml)
* [x] possui `TEST_MATRIX` (19_ATLETAS_TEST_SCENARIOS.yaml)
* [x] possui OpenAPI path (01_ATLETAS_OPENAPI.yaml)
* [x] possui schemas (referenciados no OpenAPI)
* [ ] possui `STATE_MODEL`, se aplicável
* [ ] possui `PERMISSIONS`, se aplicável
* [ ] possui `ERRORS`, se aplicável
* [x] possui `UI_CONTRACT` (14_ATLETAS_UI_CONTRACT.yaml)
* [ ] possui `SCREEN_MAP`, se aplicável
* [x] possui Arazzo (04_ATLETAS_WORKFLOWS.arazzo.yaml)
* [x] possui AsyncAPI (05_ATLETAS_EVENTS.asyncapi.yaml)

**Módulo TRAINING:**
* [x] possui `_INDEX.md`
* [ ] possui `MODULE_SCOPE`
* [ ] possui `DOMAIN_RULES`
* [x] possui `INVARIANTS` (INVARIANTS_TRAINING.md)
* [x] possui `TEST_MATRIX` (TEST_MATRIX_TRAINING.md)
* [ ] possui OpenAPI path
* [ ] possui schemas
* [x] possui `STATE_MODEL` (TRAINING_STATE_MACHINE.yaml)
* [ ] possui `PERMISSIONS`, se aplicável
* [ ] possui `ERRORS`, se aplicável
* [x] possui `UI_CONTRACT` (TRAINING_UI_CONTRACT.md)
* [ ] possui `SCREEN_MAP` (TRAINING_SCREENS_SPEC.md existe mas é spec, não mapa de navegação)
* [ ] possui Arazzo, se aplicável
* [ ] possui AsyncAPI, se aplicável

---

## 11. Prontidão real

* [x] existe pelo menos 1 contrato validado ponta a ponta (ATLETAS OpenAPI validado com Redocly)
* [x] existe pelo menos 1 módulo que passa no DoD de contrato pronto (ATLETAS tem OpenAPI, AsyncAPI, Arazzo)
* [ ] existe pelo menos 1 módulo que passa no DoD de módulo pronto
* [ ] existe pelo menos 1 fluxo onde contrato gerou/dirigiu implementação real
* [ ] existe pelo menos 1 evidência de que o agente bloqueou corretamente em uma lacuna

---

## 12. Resultado final

### PASS se:

* [ ] todas as premissas indispensáveis têm evidência real (16 de 20 artefatos canônicos faltando)
* [ ] ferramentas críticas estão instaladas e funcionando (2/8 instaladas, 1/8 funcionando)
* [ ] domínio do handebol crítico está documentado (HANDBALL_RULES_DOMAIN.md não existe)
* [ ] o agente/fluxo operacional respeita bloqueios (não verificado)
* [x] existe pelo menos 1 evidência executável ponta a ponta (Redocly validou OpenAPI do ATLETAS)

### FAIL se houver qualquer um destes:

* [x] ferramenta crítica definida no manual não roda (Spectral, oasdiff, AsyncAPI CLI não instalados)
* [x] domínio esportivo crítico está fora do documento (HANDBALL_RULES_DOMAIN.md não existe)
* [ ] agente improvisa em vez de bloquear (não verificado)
* [x] não existe enforcement real (nenhum gate de CI ou script de validação automática)
* [ ] contrato e derivado competem como fonte de verdade (não aplicável - derivados não verificados)

**VEREDICTO: ⚠️ FAIL** - Múltiplos critérios de FAIL foram atendidos. Ver tabela de evidências abaixo para detalhes.

## Formato recomendado para evidências encontradas:

No final deste arquivo, crie uma tabela como esta para cada item onde você encontrou evidência real, e adicione uma linha para cada item verificado. No final, adicione um resumo do resultado final (PASS ou FAIL) com base nos critérios acima. 

Exemplo:

| Item                  | Evidência encontrada                                               | Status                |
| --------------------- | ------------------------------------------------------------------ | --------------------- |
| Redocly CLI           | `redocly lint contracts/openapi/openapi.yaml` executou com sucesso | Atendida              |
| Schemathesis          | não instalado                                                      | Não atendida          |
| HANDBALL_RULES_DOMAIN | cobre training e matches, não cobre scout                          | Parcialmente atendida |

---

## TABELA DE EVIDÊNCIAS ENCONTRADAS

| Item | Evidência encontrada | Status |
|------|---------------------|--------|
| **Artefatos canônicos da tríade** | | |
| CONTRACT_SYSTEM_LAYOUT.md | Existe em `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md` | ✅ Atendida |
| CONTRACT_SYSTEM_RULES.md | Existe em `.contract_driven/CONTRACT_SYSTEM_RULES.md` | ✅ Atendida |
| GLOBAL_TEMPLATES.md | Existe em `.contract_driven/GLOBAL_TEMPLATES.md` | ✅ Atendida |
| ARCHITECTURE.md | Existe em `docs/product/ARCHITECTURE.md` | ✅ Atendida |
| **Artefatos canônicos faltantes** | | |
| SYSTEM_SCOPE.md | Não encontrado | ❌ Não atendida |
| MODULE_MAP.md | Não encontrado | ❌ Não atendida |
| CHANGE_POLICY.md | Não encontrado | ❌ Não atendida |
| API_CONVENTIONS.md | Não encontrado | ❌ Não atendida |
| DATA_CONVENTIONS.md | Não encontrado | ❌ Não atendida |
| ERROR_MODEL.md | Não encontrado | ❌ Não atendida |
| GLOBAL_INVARIANTS.md | Não encontrado | ❌ Não atendida |
| DOMAIN_GLOSSARY.md | Não encontrado | ❌ Não atendida |
| HANDBALL_RULES_DOMAIN.md | Não encontrado | ❌ Não atendida |
| SECURITY_RULES.md | Não encontrado | ❌ Não atendida |
| CI_CONTRACT_GATES.md | Não encontrado | ❌ Não atendida |
| TEST_STRATEGY.md | Não encontrado | ❌ Não atendida |
| C4_CONTEXT.md | Não encontrado | ❌ Não atendida |
| C4_CONTAINERS.md | Não encontrado | ❌ Não atendida |
| UI_FOUNDATIONS.md | Não encontrado | ❌ Não atendida |
| DESIGN_SYSTEM.md | Não encontrado | ❌ Não atendida |
| **Estrutura de contratos** | | |
| contracts/openapi/openapi.yaml | Não encontrado na estrutura canônica | ❌ Não atendida |
| contracts/openapi/paths/ | Não encontrado | ❌ Não atendida |
| contracts/schemas/ | Não existe | ❌ Não atendida |
| contracts/workflows/ | Não existe | ❌ Não atendida |
| contracts/asyncapi/ | Não existe | ❌ Não atendida |
| contracts/openapi/baseline/ | Existe com `openapi_baseline.json` | ⚠️ Parcial (baseline, não estrutura completa) |
| **Ferramentas de validação** | | |
| Redocly CLI | v2.20.4 instalado e funcionando | ✅ Atendida |
| Redocly CLI (validação real) | `redocly lint docs/hbtrack/modulos/atletas/01_ATLETAS_OPENAPI.yaml` executou com sucesso | ✅ Atendida |
| Spectral | Comando não encontrado | ❌ Não atendida |
| oasdiff | Comando não encontrado | ❌ Não atendida |
| Schemathesis | Instalado no venv do backend (`Hb Track - Backend\.venv\Scripts\schemathesis.exe`) | ✅ Atendida |
| Schemathesis (validação real) | Não testado contra API real | ❌ Não verificada |
| JSON Schema validator | Não identificado | ❌ Não atendida |
| AsyncAPI CLI | Comando não encontrado | ❌ Não atendida |
| Arazzo validator | Não identificado | ❌ Não atendida |
| **Módulos documentados** | | |
| Módulo ATLETAS - OpenAPI | `docs/hbtrack/modulos/atletas/01_ATLETAS_OPENAPI.yaml` existe e valida | ✅ Atendida |
| Módulo ATLETAS - AsyncAPI | `docs/hbtrack/modulos/atletas/05_ATLETAS_EVENTS.asyncapi.yaml` existe | ✅ Atendida |
| Módulo ATLETAS - Arazzo | `docs/hbtrack/modulos/atletas/04_ATLETAS_WORKFLOWS.arazzo.yaml` existe | ✅ Atendida |
| Módulo ATLETAS - Invariants | `docs/hbtrack/modulos/atletas/15_ATLETAS_INVARIANTS.yaml` existe | ✅ Atendida |
| Módulo ATLETAS - Test Scenarios | `docs/hbtrack/modulos/atletas/19_ATLETAS_TEST_SCENARIOS.yaml` existe | ✅ Atendida |
| Módulo ATLETAS - UI Contract | `docs/hbtrack/modulos/atletas/14_ATLETAS_UI_CONTRACT.yaml` existe | ✅ Atendida |
| Módulo ATLETAS - DB Contract | `docs/hbtrack/modulos/atletas/13_ATLETAS_DB_CONTRACT.yaml` existe | ✅ Atendida |
| Módulo TRAINING - Invariants | `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` existe | ✅ Atendida |
| Módulo TRAINING - Test Matrix | `docs/hbtrack/modulos/treinos/TEST_MATRIX_TRAINING.md` existe | ✅ Atendida |
| Módulo TRAINING - UI Contract | `docs/hbtrack/modulos/treinos/TRAINING_UI_CONTRACT.md` existe | ✅ Atendida |
| Módulo TRAINING - State Machine | `docs/hbtrack/modulos/treinos/TRAINING_STATE_MACHINE.yaml` existe | ✅ Atendida |
| Módulo TEAMS - Invariants | `docs/hbtrack/modulos/teams/INVARIANTS_TEAMS.md` existe | ✅ Atendida |
| Módulo TEAMS - Test Matrix | `docs/hbtrack/modulos/teams/TEST_MATRIX_TEAMS.md` existe | ✅ Atendida |
| Módulo SCOUT - Invariants | `docs/hbtrack/modulos/scout/INVARIANTS_SCOUT.md` existe | ✅ Atendida |
| Módulo COMPETITIONS - Invariants | `docs/hbtrack/modulos/competitions/INVARIANTS_COMPETITIONS.md` existe | ✅ Atendida |
| Módulo COMPETITIONS - Test Matrix | `docs/hbtrack/modulos/competitions/TEST_MATRIX_COMPETITIONS.md` existe | ✅ Atendida |
| **Enforcement e automação** | | |
| Script único de validação de contratos | Não encontrado | ❌ Não atendida |
| Rotina de falha para contrato inválido | Não encontrado | ❌ Não atendida |
| Rotina de falha para breaking change | Não encontrado | ❌ Não atendida |
| Rotina de falha para drift | Não encontrado | ❌ Não atendida |
| Pasta canônica para gerados | Não encontrado | ❌ Não atendida |

---

## RESULTADO FINAL: ⚠️ PARCIALMENTE ATENDIDO (FAIL nos critérios de PASS)

### ✅ Pontos fortes encontrados:

1. **Tríade canônica existe e está completa**: Os 3 arquivos fundamentais (LAYOUT, RULES, TEMPLATES) existem e passaram na auditoria com 100% de conformidade
2. **Módulo ATLETAS está muito bem documentado**: Possui OpenAPI, AsyncAPI, Arazzo, invariants, test scenarios, UI contract, DB contract - seguindo rigorosamente o padrão do manual
3. **Vários módulos têm documentação parcial**: TRAINING, TEAMS, SCOUT, COMPETITIONS possuem INVARIANTS e TEST_MATRIX
4. **Redocly CLI está instalado e funciona**: Validação de OpenAPI está operacional
5. **Schemathesis está instalado**: Disponível no venv do backend
6. **Decisões humanas já tomadas**: Você aceitou seguir contrato antes do código, strict mode, taxonomia canônica, etc.

### ❌ Lacunas críticas identificadas:

1. **16 dos 20 artefatos canônicos globais estão faltando**: SYSTEM_SCOPE, MODULE_MAP, CHANGE_POLICY, API_CONVENTIONS, DATA_CONVENTIONS, ERROR_MODEL, GLOBAL_INVARIANTS, DOMAIN_GLOSSARY, HANDBALL_RULES_DOMAIN, SECURITY_RULES, CI_CONTRACT_GATES, TEST_STRATEGY, C4_CONTEXT, C4_CONTAINERS, UI_FOUNDATIONS, DESIGN_SYSTEM
2. **Estrutura canônica de contracts/ não existe**: Faltam contracts/openapi/openapi.yaml, contracts/schemas/, contracts/workflows/, contracts/asyncapi/
3. **Contratos estão fora da árvore canônica**: Os contratos estão em `docs/hbtrack/modulos/<mod>/` em vez de `contracts/`
4. **Ferramentas críticas não instaladas**: Spectral, oasdiff, AsyncAPI validator, Arazzo validator, JSON Schema validator
5. **Sem enforcement automatizado**: Não há scripts de validação, rotinas de falha, ou gates de CI operacionais
6. **Sem pasta canônica para gerados**: Não existe segregação clara entre normativos e derivados
7. **HANDBALL_RULES_DOMAIN.md não existe**: Domínio esportivo crítico não está documentado formalmente

### 📊 Resumo quantitativo:

- **Artefatos canônicos**: 4/20 (20%)
- **Estrutura de contratos**: 0/6 (0% - contratos existem mas não na estrutura canônica)
- **Ferramentas instaladas**: 2/8 (25%)
- **Ferramentas funcionando**: 1/8 (12.5%)
- **Módulos documentados**: 5 módulos com documentação parcial, 1 módulo (ATLETAS) muito completo
- **Enforcement real**: 0/7 (0%)

### 🎯 Próximas ações críticas:

1. **Criar os artefatos canônicos globais faltantes** (prioridade ALTA para os indispensáveis):
   - SYSTEM_SCOPE.md
   - API_CONVENTIONS.md
   - DATA_CONVENTIONS.md
   - ERROR_MODEL.md
   - HANDBALL_RULES_DOMAIN.md (crítico para o domínio)
   - CI_CONTRACT_GATES.md

2. **Migrar/estruturar contratos para a árvore canônica**:
   - Criar contracts/openapi/openapi.yaml
   - Criar contracts/openapi/paths/
   - Criar contracts/schemas/
   - Considerar se migra os contratos existentes ou cria links/referências

3. **Instalar ferramentas críticas faltantes**:
   - Spectral (para rulesets OpenAPI)
   - oasdiff (para breaking changes)
   - AsyncAPI CLI (para validação AsyncAPI)

4. **Implementar enforcement básico**:
   - Script único para validar todos os contratos
   - Gate de CI para rodar validações
   - Rotina de falha para contrato inválido

### ⚖️ Decisão de desenvolvimento solo:

Como você está em desenvolvimento solo, você pode **priorizar pragmaticamente**:

**Mínimo viável para começar a operar**:
1. Criar SYSTEM_SCOPE.md, API_CONVENTIONS.md, HANDBALL_RULES_DOMAIN.md
2. Manter contratos onde estão (docs/hbtrack/modulos/) mas documentar essa decisão como desvio formal do layout canônico
3. Instalar Spectral e criar um script básico de validação
4. Usar o módulo ATLETAS como modelo de referência para os demais

**Quando tiver mais tempo**:
- Criar todos os artefatos canônicos globais
- Migrar contratos para a estrutura canônica
- Implementar gates de CI completos
- Criar pasta de gerados com regeneração automática





