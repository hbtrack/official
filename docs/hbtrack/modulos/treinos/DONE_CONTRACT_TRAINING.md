# DONE_CONTRACT_TRAINING.md

Status: ATIVO
Versão: v1.1.0
Tipo de Documento: SSOT Normativo — Done Contract
Módulo: TRAINING
Autoridade: NORMATIVO_TECNICO
Última revisão: 2026-03-08

> Objetivo
> Separar formalmente:
> 1. convergência técnica,
> 2. validade semântica do fluxo real,
> 3. conclusão de produto no escopo aprovado.
>
> Este contrato existe para impedir a falsa equivalência entre:
> - backend validado,
> - contrato sincronizado,
> - cliente FE gerado,
> - e módulo concluído como produto.

---

## 1. Dependências normativas

Leitura obrigatória em conjunto com:
- `_INDEX.md`
- `INVARIANTS_TRAINING.md`
- `TRAINING_FRONT_BACK_CONTRACT.md`
- `TRAINING_USER_FLOWS.md`
- `TRAINING_SCREENS_SPEC.md`
- `TEST_MATRIX_TRAINING.md`
- `AR_BACKLOG_TRAINING.md`

Artefatos obrigatórios complementares desta versão:
- `TRAINING_SCOPE_REGISTRY.yaml`
- `TRAINING_STATE_MACHINE.yaml`
- `TRAINING_PERF_LIMITS.json`
- `traceability_training_core.csv`

---

## 2. Authority Matrix

| Aspecto | Regra |
|---|---|
| Fonte de verdade | DB constraints + Backend services + OpenAPI materializado + Test Matrix + Done Contract |
| Escrita normativa | **Arquiteto** — criar, alterar, remover gates e critérios de DONE |
| Escrita operacional | **Executor** e **Testador** — somente produzir evidência verificável |
| Proposta de alteração | Qualquer papel → via GAP/DESVIO ao Arquiteto |
| Somente leitura | Designer UX, Executor, Testador |
| Precedência em conflito | DB > Services > OpenAPI > FE Generated > FE Manual/Adapter > Flows/Screens > Backlog histórico |
| Regra de evidência | Texto narrativo não constitui prova; apenas comando executado + artefato gerado + resultado verificável constituem evidência válida |
| Regra de rastreabilidade | Nenhum teste, artefato ou PASS é válido sem vínculo com IDs normativos (`INV-*`, `FLOW-*`, `SCREEN-*`, `CONTRACT-*`, `DEC-*`, quando aplicável) |

---

## 3. Princípios

### 3.1 Separação obrigatória de DONE

Neste módulo, `DONE` é proibido como marcador único e não qualificado.

Só existem três gates válidos:
- `DONE_TECNICO`
- `DONE_SEMANTICO`
- `DONE_PRODUTO`

### 3.2 Regra de ouro

`DONE_TECNICO = TRUE` **não** autoriza linguagem de módulo concluído.  
`DONE_SEMANTICO = TRUE` **não** autoriza linguagem de escopo completo.  
A expressão “módulo concluído” só é válida quando `DONE_PRODUTO = TRUE`.

### 3.3 Regra de prova

Nenhum gate pode ser satisfeito por:
- texto declarativo,
- changelog,
- handoff narrativo,
- inferência do Executor,
- confirmação textual do Testador,
- ou simples existência de arquivo.

Todo gate exige:
1. comando canônico,
2. artefato verificável,
3. resultado determinístico,
4. vínculo com IDs normativos,
5. identidade de ambiente,
6. identidade de estado do banco,
7. reprodutibilidade pelo Testador.

### 3.4 Regra de identidade da evidência

Toda evidência deve ser capaz de responder, de forma verificável:
- em qual commit foi produzida;
- em qual ambiente foi executada;
- com qual fingerprint técnico;
- com qual estado inicial do banco;
- com qual estado final do banco;
- contra quais artefatos normativos foi validada.

### 3.5 Regra de seed determinístico

O seed de banco de dados usado na TRUTH SUITE:
- DEVE ser estático;
- NÃO pode usar `random()`, `uuid4()` não fixado, `datetime.now()`, `timezone.now()` ou equivalente sem valor determinístico controlado;
- DEVE produzir sempre o mesmo `DB_STATE_HASH` canônico para a mesma versão de seed.

Se o seed não for determinístico:
- toda a cadeia de evidência é inválida.

---

## 4. Taxonomia de escopo

### 4.1 Scope Registry obrigatório

Todo item do módulo TRAINING deve ser classificado em exatamente um dos grupos:

- `CORE`
- `EXTENDED`
- `EXPERIMENTAL`

### 4.2 Regras de escopo

#### CORE
Capacidades sem as quais o módulo não pode ser declarado concluído como produto.

Exemplos esperados no TRAINING:
- agenda
- sessões (criar/editar/publicar/fechar)
- attendance core
- wellness pre
- wellness post
- exercises core
- templates core
- analytics core mínimo
- export core mínimo

#### EXTENDED
Capacidades relevantes, mas não necessárias para `DONE_PRODUTO` do core.

Exemplos:
- pending queue
- rankings
- top performers
- alertas centralizados
- athlete pre-training view

#### EXPERIMENTAL
Capacidades futuras, opcionais ou com incerteza de produto.

Exemplos:
- AI coach chat
- AI draft assistant
- sugestões avançadas fora do OpenAPI canônico atual

### 4.3 Regra de bloqueio

Nenhum item classificado como `CORE` pode permanecer com:
- `GAP`
- `PARCIAL`
- `HIPOTESE`
- `BLOQUEADO`

quando `DONE_PRODUTO = TRUE`.

---

## 5. Artefatos obrigatórios desta política

### 5.1 TRAINING_SCOPE_REGISTRY.yaml
Arquivo canônico de classificação de escopo dos itens do módulo.

### 5.2 TRAINING_STATE_MACHINE.yaml
Arquivo canônico e legível por máquina que define:
- entidades stateful,
- estados válidos,
- transições válidas,
- transições proibidas,
- precondições,
- roles permitidos,
- invariantes relacionadas.

Sem este arquivo:
- `DONE_SEMANTICO = FALSE` para qualquer entidade stateful `CORE`;
- `DONE_PRODUTO = FALSE`.

### 5.3 TRAINING_PERF_LIMITS.json
Arquivo canônico de limites quantitativos e SLOs mínimos.

Sem este arquivo:
- item `CORE` com dependência de desempenho não é elegível para `DONE_PRODUTO`.

### 5.4 traceability_training_core.csv
Artefato canônico de rastreabilidade entre teste, fluxo, tela, contrato, invariante, seletor e baseline visual.

Sem este arquivo:
- `DONE_SEMANTICO = FALSE`.

---

## 6. DONE_TECNICO

### 6.1 Definição

`DONE_TECNICO` prova convergência estrutural do módulo com o SSOT técnico.

Ele valida:
- persistência,
- regras de backend,
- contrato materializado,
- cliente FE gerado,
- sincronização FE↔BE,
- runtime contract real,
- ausência de desvios técnicos proibidos.

Ele **não** prova:
- correção da UX final,
- executabilidade real do fluxo do usuário,
- legibilidade visual,
- comportamento correto da superfície do produto.

### 6.2 Critérios obrigatórios

`DONE_TECNICO = TRUE` somente se todos os itens abaixo forem verdadeiros:

1. `schema.sql` compatível com o backend real.
2. Models, services, routers e schemas Pydantic convergentes.
3. `openapi.json` regenerado a partir do backend real.
4. OpenAPI lint = PASS.
5. Contract diff classificado e aceito.
6. Generated client regenerado.
7. Nenhuma edição manual dentro de `src/api/generated/*`.
8. Adapter manual não redefine shape canônico.
9. `TRUTH_BE = PASS`.
10. `NO_MOCKS_GLOBAL = PASS`.
11. Runtime contract validation = PASS.
12. Tipos canônicos críticos convergentes:
   - `uuid`
   - `datetime`
   - `date`
   - enums canônicos
13. Cross-check de migração vs contrato executado.
14. Property-based checks mínimos para tipos críticos e invariantes de serialização.
15. Nenhum endpoint consumido pelo FE fora do OpenAPI normativo do módulo.
16. `ENV_FINGERPRINT` válido e persistido.
17. `DB_STATE_HASH` pré-execução compatível com seed canônico.
18. `DB_STATE_HASH` pós-reset compatível com baseline canônico da suíte.
19. `manifest.json` contém hashes de todos os artefatos obrigatórios do gate.

### 6.3 Proibições

`DONE_TECNICO = FALSE` automaticamente se houver qualquer um dos itens abaixo:

- endpoint fora do OpenAPI normativo
- generated client desatualizado
- adapter reescrevendo request/response shape
- spec válida, porém divergente do comportamento real
- timezone drift não testado em campos `datetime`
- enum documentado mas não materializado
- serialização assimétrica FE↔BE
- mudança de contrato sem diff classificado
- uso de mocks proibidos
- uso de dados residuais não determinísticos
- fingerprint de ambiente ausente
- `DB_STATE_HASH` incompatível com seed canônico
- seed não determinístico
- state machine do código permitindo transição que não existe no `TRAINING_STATE_MACHINE.yaml` para entidade `CORE`

### 6.4 Evidence Protocol — DONE_TECNICO

#### EVID-TEC-001 — Reset determinístico do ambiente
Comando:
```bash
python scripts/db/reset_hb_track_test.py
```

Artefatos esperados:
- `stdout.log`
- `stderr.log` (se houver)
- `exit_code.txt`
- `db_state_post_reset.json`
- `env_fingerprint.json`

Conteúdo mínimo de `db_state_post_reset.json`:
```json
{
  "database_name": "hb_track_test",
  "seed_version": "",
  "alembic_head": "",
  "db_state_hash": "",
  "table_row_counts": {},
  "critical_tables_digest": {}
}
```

Condição de aprovação:
- reset executado sem erro
- ambiente não aponta para banco de produção
- `db_state_hash` igual ao hash canônico esperado para a versão de seed

#### EVID-TEC-002 — TRUTH_BE
Comando:
```bash
cd "Hb Track - Backend" && pytest -q tests/training/
```

Artefatos esperados:
- stdout completo do pytest
- contagem final `X passed, 0 failed`
- `result.json`
- `db_state_pre_truth_be.json`
- `db_state_post_truth_be.json`

Condição de aprovação:
- suite verde em Postgres real
- sem mocks proibidos
- após reset+migrations+seed
- `db_state_pre_hash` compatível com seed canônico
- `db_state_post_hash` compatível com mutações esperadas da suíte, quando aplicável

#### EVID-TEC-003 — NO_MOCKS_GLOBAL
Comando:
```bash
rg -n "unittest\.mock|MagicMock|monkeypatch|patch\(" "Hb Track - Backend/tests/training" "Hb Track - Backend/app"
```

Artefatos esperados:
- `stdout.log`
- `exit_code.txt`

Condição de aprovação:
- nenhum uso proibido em escopo onde a política veda mocks

#### EVID-TEC-004 — OpenAPI lint
Comando:
```bash
npx @redocly/cli@latest lint "Hb Track - Backend/docs/ssot/openapi.json"
```

Artefatos esperados:
- `stdout.log`
- `exit_code.txt`
- `openapi_sha256.txt`

Condição de aprovação:
- sem erro bloqueante
- ruleset HB Track aplicado quando existir
- nenhum tipo proibido pelo strict mode definido pelo projeto

#### EVID-TEC-005 — Contract diff gate
Comando:
```bash
oasdiff breaking "contracts/openapi/baseline/openapi_baseline.json" "Hb Track - Backend/docs/ssot/openapi.json"
```

Artefatos esperados:
- relatório textual do diff
- `exit_code.txt`

Condição de aprovação:
- nenhuma breaking change silenciosa
- ou breaking change explicitamente classificada e aprovada via DEC/AR

#### EVID-TEC-006 — Generated client sync
Comando:
```bash
npm run api:sync
```

Artefatos esperados:
- stdout da geração
- diff do client gerado
- checksum dos arquivos regenerados
- `generated_client_sha256.txt`

Condição de aprovação:
- client alinhado à spec atual
- sem edição manual subsequente

#### EVID-TEC-007 — Runtime contract validation
Comando exemplo:
```bash
schemathesis run "Hb Track - Backend/docs/ssot/openapi.json" --base-url=http://localhost:8000
```

Artefatos esperados:
- `stdout.log`
- `stderr.log` (se houver)
- `exit_code.txt`
- relatório da execução

Condição de aprovação:
- request/response/status code compatíveis com a spec materializada

#### EVID-TEC-008 — Property-based contract checks
Comando exemplo:
```bash
cd "Hb Track - Backend" && pytest -q tests/training/property_based/
```

Artefatos esperados:
- stdout do pytest
- casos gerados automaticamente
- relatório de serialização e invariantes de tipo

Condição de aprovação:
- campos críticos (`uuid`, `datetime`, enums, limites numéricos) preservam invariantes entre domínio, API e persistência

#### EVID-TEC-009 — Environment fingerprint
Artefato obrigatório:
- `env_fingerprint.json`

Conteúdo mínimo:
```json
{
  "environment": "deterministic-test",
  "commit_sha": "",
  "python_version": "",
  "node_version": "",
  "postgres_version": "",
  "os_fingerprint": "",
  "openapi_sha256": "",
  "generated_client_sha256": "",
  "schema_sql_sha256": "",
  "seed_fixture_sha256": "",
  "test_matrix_sha256": "",
  "state_machine_sha256": "",
  "perf_limits_sha256": "",
  "scope_registry_sha256": ""
}
```

Condição de aprovação:
- todos os campos obrigatórios presentes
- fingerprint compatível com o ambiente aceito da suíte

### 6.5 Resultado técnico

Se todos os critérios acima passarem:
- `DONE_TECNICO = TRUE`

Mensagem permitida:
- “O módulo TRAINING está tecnicamente convergente.”

Mensagem proibida:
- “O módulo TRAINING está concluído.”

---

## 7. DONE_SEMANTICO

### 7.1 Definição

`DONE_SEMANTICO` prova que o comportamento real do módulo está correto na superfície do produto para o escopo `CORE`.

Ele valida:
- fluxo real executável,
- estados de tela,
- bloqueios de ação,
- regras de UX obrigatória,
- comportamento visível no browser,
- integração FE↔BE em uso real,
- persistência coerente com o que a UI afirmou.

Ele **não** é satisfeito por:
- documentação,
- spec de tela,
- manual guiado isolado,
- screenshot solto,
- ou narrativa do Testador.

### 7.2 Critérios obrigatórios

`DONE_SEMANTICO = TRUE` somente se todos os itens abaixo forem verdadeiros:

1. Todos os `FLOW-*` classificados como `P0` e pertencentes ao `CORE` são executáveis no browser.
2. Todas as `SCREEN-*` `CORE` estão materializadas.
3. Não existe `GAP`, `PARCIAL`, `HIPOTESE` ou `BLOQUEADO` em item `CORE`.
4. `TRUTH_FE_CORE = PASS`.
5. Há cobertura dos estados mínimos por tela `CORE`:
   - `loading`
   - `empty`
   - `error`
   - `success/data`
   - `readonly` quando aplicável
6. Regras operacionais críticas estão visíveis e efetivas na UI.
7. Assertions E2E estão ligadas a IDs normativos estáveis.
8. Seletores de teste usam `data-test-id` estável.
9. Não há dependência de mock para fluxos `P0`.
10. Há baseline visual aprovado para telas `CORE` críticas.
11. Há validação de matriz de transição de estados para fluxos centrais.
12. Há verificação de side-effect por canal independente da UI para cada fluxo `P0/CORE`.
13. O side-effect observado corresponde exatamente ao efeito esperado no contrato e na state machine.
14. `TRAINING_STATE_MACHINE.yaml` existe e cobre todas as entidades stateful `CORE`.
15. `traceability_training_core.csv` cobre 100% dos `FLOW-* P0/CORE`.

### 7.3 Regras semânticas mínimas obrigatórias

O `DONE_SEMANTICO` deve provar, no mínimo, quando aplicável ao item `CORE`:

- revisão obrigatória antes de aplicar draft de IA
- páginas athlete self-only realmente sem seleção de terceiro
- action blocking em estado inválido
- ACL visível e eficaz
- erro de backend corretamente refletido na UI
- estados degradados explicitamente tratados
- navegação do fluxo sem dead-end
- ausência de placeholder em tela classificada como `CORE`
- persistência compatível com o que a UI mostrou
- não existência de “sucesso visual” sem mutação real de estado

### 7.4 Traceability Matrix obrigatória

Toda assertion de E2E deve apontar para uma linha rastreável:

| test_id | flow_id | screen_id | contract_id | invariant_id | selector_id | visual_baseline_id | side_effect_check_id | state_transition_id |
|---|---|---|---|---|---|---|---|---|

Regras:
- um teste sem `flow_id` é inválido
- um `flow_id` P0 sem teste associado é inválido
- um seletor sem `data-test-id` estável é inválido
- baseline visual sem aprovação humana explícita é inválido
- teste `P0/CORE` sem `side_effect_check_id` é inválido
- teste stateful sem `state_transition_id` é inválido

### 7.5 Side-Effect Validation obrigatória

Para cada teste `P0/CORE`, o contrato exige:

1. ação na UI
2. asserção visual mínima
3. verificação do efeito colateral por canal independente

Canais permitidos:
- leitura direta no banco em ambiente de teste
- endpoint de inspeção de teste explicitamente isolado e proibido em produção
- API de suporte a teste gerada para inspeção
- snapshot before/after controlado

Regras:
- o canal de side-effect não pode depender do mesmo componente de UI testado
- “toast de sucesso” nunca é evidência suficiente
- a persistência observada deve refletir exatamente a expectativa do contrato

### 7.6 Evidence Protocol — DONE_SEMANTICO

#### EVID-SEM-001 — TRUTH_FE_CORE
Comando canônico:
```bash
cd "Hb Track - Frontend" && npm run test:e2e:training-core
```

Artefatos esperados:
- stdout completo
- relatório Playwright
- traces
- screenshots/videos quando habilitados
- `db_state_pre_truth_fe.json`
- `db_state_post_truth_fe.json`

Condição de aprovação:
- todos os flows `P0/CORE` passam
- execução contra backend real compatível
- sem mocks para fluxos `P0`
- `db_state_pre_hash` compatível com seed canônico

#### EVID-SEM-002 — Traceability matrix
Artefato obrigatório:
- `docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv`

Condição de aprovação:
- 100% dos flows `P0/CORE` cobertos
- 100% das screens `CORE` cobertas
- vínculo explícito test→flow→screen→contract→invariant→selector→side-effect→state transition

#### EVID-SEM-003 — Visual regression
Comando canônico:
```bash
cd "Hb Track - Frontend" && npm run test:visual:training-core
```

Artefatos esperados:
- diffs visuais
- baseline aprovado
- relatório de aprovação/rejeição

Condição de aprovação:
- nenhuma regressão visual não aprovada nas telas `CORE`

#### EVID-SEM-004 — State machine validation
Comando canônico:
```bash
cd "Hb Track - Backend" && pytest -q tests/training/state_machine/
```

Artefatos esperados:
- stdout do pytest
- relatório de transições válidas
- relatório de transições proibidas
- `state_machine_sha256.txt`

Condição de aprovação:
- estados impossíveis rejeitados
- transições normativas confirmadas
- testes derivados do `TRAINING_STATE_MACHINE.yaml`
- qualquer transição permitida no código, mas ausente no YAML, derruba o gate

#### EVID-SEM-005 — Performance mínima do CORE
Comando exemplo:
```bash
cd "Hb Track - Frontend" && npm run test:perf:training-core
```

Artefatos esperados:
- métricas por item core
- relatório comparável
- `perf_limits_sha256.txt`

Condição de aprovação:
- SLOs mínimos definidos em `TRAINING_PERF_LIMITS.json` atendidos

#### EVID-SEM-006 — Side-effect verification
Comando canônico:
```bash
cd "Hb Track - Backend" && pytest -q tests/training/side_effects/
```

Artefatos esperados:
- stdout do pytest
- matriz de before/after
- consultas ou inspeções persistidas por teste
- digest dos registros críticos afetados

Condição de aprovação:
- cada fluxo `P0/CORE` possui verificação de efeito colateral independente
- o estado persistido coincide com a UI e com o contrato

### 7.7 Resultado semântico

Se todos os critérios acima passarem:
- `DONE_SEMANTICO = TRUE`

Mensagem permitida:
- “O core do módulo TRAINING está semanticamente validado na superfície do produto.”

Mensagem proibida:
- “O módulo TRAINING completo está concluído.”

---

## 8. DONE_PRODUTO

### 8.1 Definição

`DONE_PRODUTO` prova que o módulo pode ser declarado concluído como produto no escopo formalmente aprovado.

### 8.2 Critérios obrigatórios

`DONE_PRODUTO = TRUE` somente se:

1. `DONE_TECNICO = TRUE`
2. `DONE_SEMANTICO = TRUE`
3. O escopo `CORE` estiver congelado e documentado
4. Todos os itens `CORE` estiverem implementados
5. Todos os itens `CORE` estiverem testados
6. Não houver `GAP/PARCIAL/HIPOTESE/BLOQUEADO` no `CORE`
7. Itens residuais estiverem apenas em `EXTENDED` ou `EXPERIMENTAL`
8. O backlog residual não reclassifique déficit de `CORE` como “pós-DONE”
9. A decisão de release estiver registrada
10. A linguagem do release reflita o escopo real concluído
11. Todo item `CORE` possuir limite quantitativo definido em `TRAINING_PERF_LIMITS.json`
12. Toda entidade stateful `CORE` possuir cobertura no `TRAINING_STATE_MACHINE.yaml`

### 8.3 Proibições

É proibido declarar `DONE_PRODUTO = TRUE` quando:

- `TRUTH_FE_CORE` não existe
- há tela `CORE` placeholder
- há flow `CORE` sem prova executável
- há item `CORE` coberto só por `MANUAL_GUIADO`
- há item `CORE` com estado `GAP/PARCIAL/HIPOTESE`
- há endpoint `CORE` consumido fora do OpenAPI normativo
- há “pós-DONE” mascarando déficit de `CORE`
- não existe `TRAINING_SCOPE_REGISTRY.yaml`
- não existe `TRAINING_STATE_MACHINE.yaml`
- não existe `TRAINING_PERF_LIMITS.json`

### 8.4 Evidence Protocol — DONE_PRODUTO

#### EVID-PROD-001 — Scope registry
Artefato obrigatório:
- `docs/hbtrack/modulos/treinos/TRAINING_SCOPE_REGISTRY.yaml`

Condição de aprovação:
- todos os itens do módulo classificados como `CORE`, `EXTENDED` ou `EXPERIMENTAL`

#### EVID-PROD-002 — Release decision record
Artefato obrigatório:
- `docs/hbtrack/modulos/treinos/_reports/TRAINING_RELEASE_DECISION.md`

Conteúdo mínimo:
- versão
- escopo liberado
- gates satisfeitos
- riscos residuais fora do core
- referência para suítes executadas

#### EVID-PROD-003 — Gate summary
Artefato obrigatório:
- `docs/hbtrack/modulos/treinos/_reports/DONE_GATE_SUMMARY.json`

Campos mínimos:
```json
{
  "module": "TRAINING",
  "done_tecnico": true,
  "done_semantico": true,
  "done_produto": true,
  "core_items_total": 0,
  "core_items_green": 0,
  "residual_gaps_core": 0,
  "residual_gaps_extended": 0,
  "residual_gaps_experimental": 0,
  "truth_be": "PASS",
  "truth_fe_core": "PASS",
  "env_fingerprint_sha256": "",
  "db_state_pre_hash": "",
  "db_state_post_hash": "",
  "state_machine_sha256": "",
  "perf_limits_sha256": ""
}
```

### 8.5 Resultado de produto

Se todos os critérios acima passarem:
- `DONE_PRODUTO = TRUE`

Mensagem permitida:
- “O módulo TRAINING está concluído como produto no escopo CORE aprovado.”

Mensagem proibida:
- “Todo o universo TRAINING está concluído” sem qualificação de escopo.

---

## 9. Critérios quantitativos mínimos

### 9.1 Regra geral

Nenhum item `CORE` pode ser considerado pronto apenas por “funcionar”.

Todo item `CORE` deve possuir, no mínimo:
- limite funcional
- limite de payload
- expectativa de desempenho
- comportamento sob erro

### 9.2 Fonte canônica dos limites

Os limites quantitativos **não** devem ser mantidos em prosa neste documento.  
A fonte de verdade é exclusivamente:

- `TRAINING_PERF_LIMITS.json`

### 9.3 Regra de ausência de número

Se um item `CORE` não tiver métrica mínima definida em `TRAINING_PERF_LIMITS.json`:
- esse item não está elegível para `DONE_PRODUTO`

---

## 10. RULES

### RULE-DONE-001
É proibido usar apenas `DONE` sem qualificativo.

### RULE-DONE-002
`DONE_TECNICO` nunca autoriza linguagem de módulo concluído.

### RULE-DONE-003
`DONE_SEMANTICO` é obrigatório para qualquer declaração de conclusão do `CORE`.

### RULE-DONE-004
Nenhum item `CORE` pode estar `GAP`, `PARCIAL`, `HIPOTESE` ou `BLOQUEADO` quando `DONE_PRODUTO = TRUE`.

### RULE-DONE-005
`MANUAL_GUIADO` pode complementar evidência, mas nunca substituir `TRUTH_FE_CORE` para itens `CORE`.

### RULE-DONE-006
Toda evidência válida deve ser reexecutável por comando.

### RULE-DONE-007
Nome de arquivo não é evidência; saída de comando + artefato gerado + resultado verificável é evidência.

### RULE-DONE-008
Todo teste E2E `CORE` deve usar `data-test-id` estável.

### RULE-DONE-009
Toda assertion de fluxo deve ser rastreável a `FLOW-*`.

### RULE-DONE-010
Toda tela `CORE` deve possuir baseline visual aprovado.

### RULE-DONE-011
Fluxos `P0` são proibidos de depender de mock.

### RULE-DONE-012
Toda transição de estado crítica do módulo deve possuir prova de state-machine validation.

### RULE-DONE-013
Mudança em contrato canônico exige reexecução do `DONE_TECNICO`.

### RULE-DONE-014
Mudança em UI/UX de item `CORE` exige reexecução do `DONE_SEMANTICO`.

### RULE-DONE-015
Reclassificar déficit de `CORE` como “pós-DONE” é inválido.

### RULE-DONE-016
Artefato histórico não substitui evidência executada no contexto atual.

### RULE-DONE-017
Não é permitido concluir `DONE_PRODUTO` sem `TRAINING_SCOPE_REGISTRY.yaml`.

### RULE-DONE-018
State machine inválida derruba `DONE_SEMANTICO` e `DONE_PRODUTO`, ainda que `DONE_TECNICO` permaneça verde.

### RULE-DONE-019
Divergência entre migration, modelo, OpenAPI e generated client derruba `DONE_TECNICO`.

### RULE-DONE-020
Qualquer PASS fora do ambiente determinístico definido é inválido como evidência.

### RULE-DONE-021
Toda execução de gate deve registrar `ENV_FINGERPRINT` e `DB_STATE_HASH` pré e pós execução.

### RULE-DONE-022
`DB_STATE_HASH` divergente do seed canônico invalida toda evidência subsequente.

### RULE-DONE-023
Todo teste `P0/CORE` deve comprovar efeito colateral por canal independente da UI.

### RULE-DONE-024
State machine validation só é válida se derivada de `TRAINING_STATE_MACHINE.yaml`.

### RULE-DONE-025
Entidade stateful `CORE` sem mapa formal de estados torna `DONE_SEMANTICO` inválido.

### RULE-DONE-026
SLO textual em prosa não constitui limite operacional válido; apenas `TRAINING_PERF_LIMITS.json`.

### RULE-DONE-027
Log isolado não é evidência suficiente sem hash de ambiente e hash de estado.

### RULE-DONE-028
Testador não pode validar evidência produzida fora do ambiente determinístico fingerprintado.

### RULE-DONE-029
Assertion visual sem side-effect validation não fecha fluxo `P0/CORE`.

### RULE-DONE-030
Seletores de teste estáveis são necessários, mas nunca suficientes, para validação semântica.

---

## 11. Coleta determinística de evidência

### 11.1 Estrutura mínima de saída

Toda execução de gate deve gerar:

- `stdout.log`
- `stderr.log` (se houver)
- `exit_code.txt`
- artefato principal (`result.json`, relatório Playwright, diff visual, etc.)
- carimbo temporal
- commit SHA
- AR_ID ou referência operacional
- `env_fingerprint.json`
- `db_state_pre.json`
- `db_state_post.json`

### 11.2 Diretório padrão

```text
docs/hbtrack/modulos/treinos/_evidence/
  done_tecnico/
  done_semantico/
  done_produto/
```

### 11.3 Manifesto de execução

Toda coleta de evidência deve gerar:

`docs/hbtrack/modulos/treinos/_evidence/manifest.json`

Campos mínimos:
```json
{
  "module": "TRAINING",
  "commit_sha": "",
  "executed_at": "",
  "environment": "deterministic-test",
  "env_fingerprint_sha256": "",
  "db_state_pre_hash": "",
  "db_state_post_hash": "",
  "seed_expected_hash": "",
  "openapi_sha256": "",
  "generated_client_sha256": "",
  "schema_sql_sha256": "",
  "scope_registry_sha256": "",
  "state_machine_sha256": "",
  "perf_limits_sha256": "",
  "test_matrix_sha256": "",
  "gates": {
    "done_tecnico": {
      "executed": true,
      "result": "PASS",
      "commands": []
    },
    "done_semantico": {
      "executed": true,
      "result": "PASS",
      "commands": []
    },
    "done_produto": {
      "executed": true,
      "result": "PASS",
      "commands": []
    }
  }
}
```

### 11.4 Regra de reprodutibilidade

Se a evidência não puder ser reproduzida pelo Testador a partir:
- do commit,
- do comando,
- do ambiente,
- do manifesto,
- do fingerprint,
- e do hash de estado,

então a evidência é inválida.

### 11.5 Regra de cadeia de custódia

Toda evidência deve preservar a seguinte cadeia:

`commit_sha`
→ `env_fingerprint`
→ `db_state_pre_hash`
→ `comando executado`
→ `artefatos gerados`
→ `db_state_post_hash`
→ `resultado`

Se qualquer elo faltar:
- o gate correspondente falha.

---

## 12. Condições de FAIL imediato

Qualquer um dos itens abaixo gera FAIL imediato do gate correspondente:

- falta de comando executável
- ausência de artefato gerado
- evidência apenas textual
- selector instável em teste `CORE`
- visual baseline ausente em tela `CORE`
- flow `P0` sem cobertura E2E
- item `CORE` com status documental não verde
- runtime contract FAIL
- property-based FAIL
- state-machine FAIL
- side-effect validation ausente para `P0/CORE`
- `DB_STATE_HASH` divergente do esperado
- `ENV_FINGERPRINT` ausente
- seed não determinístico
- presença de endpoint FE fora do OpenAPI normativo
- consumo manual mascarando divergência de shape
- uso de mock proibido
- ambiente não determinístico

---

## 13. Linguagem permitida de status

### Permitido
- “DONE_TECNICO = TRUE”
- “DONE_SEMANTICO = TRUE para o escopo CORE”
- “DONE_PRODUTO = TRUE para o escopo CORE aprovado”

### Proibido
- “módulo concluído” sem qualificativo
- “frontend validado” sem `TRUTH_FE_CORE`
- “produto pronto” sem `DONE_PRODUTO`
- “sem pendências” se existir resíduo no `CORE`

---

## 14. Compatibilidade com documentos vigentes

Este contrato não substitui:
- `INVARIANTS_TRAINING.md`
- `TRAINING_FRONT_BACK_CONTRACT.md`
- `TRAINING_USER_FLOWS.md`
- `TRAINING_SCREENS_SPEC.md`
- `TEST_MATRIX_TRAINING.md`

Ele atua como camada superior de decisão de encerramento.

Em conflito:
1. DB / Services / OpenAPI governam estrutura e contrato.
2. Test Matrix governa validade operacional da evidência.
3. Done Contract governa a legitimidade da declaração de conclusão.

---

## 15. Migração do modelo anterior

### 15.1 Regra de transição

O marcador histórico `DONE_TRAINING_ATINGIDO` deve ser reinterpretado como:

- equivalente aproximado a `DONE_TECNICO` + fechamento parcial de evidência histórica,
- mas insuficiente, por si só, para `DONE_PRODUTO`.

### 15.2 Regra de compatibilidade

Até a materialização de `TRUTH_FE_CORE`, o módulo pode no máximo declarar:
- convergência técnica,
- ou conclusão parcial condicionada,
- nunca conclusão plena de produto no `CORE`.

---

## 16. Definição final

Resumo decisório:

- `DONE_TECNICO` = prova que a arquitetura está convergente
- `DONE_SEMANTICO` = prova que o core funciona no produto real
- `DONE_PRODUTO` = prova que o módulo pode ser declarado concluído no escopo aprovado
```
