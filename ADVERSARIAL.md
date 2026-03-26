# Relatório Adversarial de Continuidade até o DONE

> ⚠️ **ARTEFATO DERIVADO — NON-SOVEREIGN**: Este arquivo é uma análise adversarial derivada. Não possui autoridade normativa. Não deve ser usado para redefinir schemas, gates, contratos ou políticas canônicas. Em caso de conflito, prevalecem: `scripts/hb` + `validate_contracts.py` > `contracts/schemas/` > `docs/_canon/` > `.contract_driven/CONTRACT_SYSTEM_RULES.md` > este arquivo.

## PARTE 1 — Veredito adversarial inicial
- A configuração atual passa ou reprova? **Reprova**
- O agente ainda pode alucinar ou se perder antes do DONE? **Sim**
- Qual é o nível de risco atual? **Crítico**

## PARTE 2 — Tabela de falhas encontradas
| ID | Falha encontrada | Tipo | Onde ocorre | Severidade | Como permite alucinação/perda de direção | Bloqueia DONE seguro? |
|----|------------------|------|-------------|------------|------------------------------------------|-----------------------|
| F-01 | Boot dito determinístico com caminhos inválidos em profiles de boot | instrução insuficiente | `.contract_driven/BOOT_PROFILES.yaml`, `scripts/hb`, `docs/_canon/AGENT_INSTRUCTIONS.md` | Crítica | O agente “obedece” o boot, mas não consegue abrir o que o profile manda ler e passa a improvisar contexto ausente | Sim |
| F-02 | Execuções parciais sobrescreviam `latest.json` e dashboards canônicos | rastreabilidade fraca | `scripts/contracts/validate/validate_contracts.py`, `_reports/contract_gates/latest.json`, `_reports/pipeline_health.json` | Crítica | Um PASS local plausível podia parecer PASS canônico; o próximo agente escolheria a ação seguinte com base falsa | Sim |
| F-03 | Handoff sem prova obrigatória suficiente e gate não bloqueante | lacuna de handoff | `SESSION_HANDOFF.md`, `contracts/schemas/shared/session_handoff.schema.json`, `docs/_canon/templates/SESSION_HANDOFF.template.md`, `docs/_canon/gates/GATES_REGISTRY.yaml` | Crítica | O agente podia declarar DONE e continuidade sem evidência verificável nem vínculo claro com boot/task/CI real | Sim |
| F-04 | Status de módulo podia subir sem superfícies mínimas ou evidência pré-contrato explícita | falta de evidência | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `docs/_canon/MODULE_REGISTRY.yaml` | Alta | O sistema aceitava progresso aparente em módulo “elevado” sem cobertura estrutural suficiente | Sim |
| F-05 | Autoridade do Decision IR fragmentada entre `.dev` e `.contract_driven/decisions` | conflito entre artefatos | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `docs/_canon/gates/README.md`, `docs/hbtrack/modulos/training/DECISION_IR_TRAINING.yaml` | Alta | Dois agentes poderiam seguir fontes diferentes e chegar a decisões divergentes obedecendo superficialmente o canon | Sim |
| F-06 | Referências canônicas/operacionais apontavam para documentos removidos ou fonte de IR antiga | conflito entre artefatos | `README.md`, `docs/_canon/ARCHITECTURE.md`, `docs/_canon/DATA_CONVENTIONS.md`, ADRs em `docs/_canon/decisions/`, `contracts/openapi/README.md` | Alta | O agente podia ser roteado para artefatos mortos e preencher a lacuna com inferência plausível | Sim |
| F-07 | Módulos legados sem continuidade pré-contrato explícita | falha de continuidade | `_reports/agent_execution/*.json`, `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `scripts/contracts/validate/validate_contracts.py` | Alta | A continuidade histórica ficava implícita; o agente podia assumir que “já foi feito” sem trilha formal | Sim |
| F-08 | Política de header de docs conflitava com docs reais do módulo | conflito entre artefatos | `.contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml`, docs de módulo | Média | O agente podia “corrigir” documento saudável para obedecer uma política incorreta ou falhar gate indevidamente | Sim |
| F-09 | Alterações soberanas podiam deixar derivados/manifests defasados até reteste explícito | rastreabilidade fraca | `generated/manifests/*.traceability.yaml`, `contracts/openapi/baseline/openapi_baseline.json`, `generated/contracts/openapi/**` | Alta | O sistema parecia consistente enquanto hashes e baselines já não correspondiam às fontes reais | Sim |
| F-10 | CLI da validação parcial anunciava `latest.json` mesmo quando escrevia relatório escopado | rastreabilidade fraca | `scripts/contracts/validate/validate_contracts.py` | Média | Um auditor humano ou uma sessão seguinte podia consumir o arquivo errado mesmo com a gravação correta em disco | Não |
| F-11 | Wrapper de execução de ferramenta produzia `FAIL` falso em gate bloqueante por timeout/interoperabilidade artificial | decisão sem regra | `scripts/contracts/validate/validate_contracts.py` | Alta | O agente podia perseguir uma breaking change inexistente ou parar sem saber o próximo passo por um falso negativo de infraestrutura | Sim |

## PARTE 3 — Cenários de quebra
| Cenário | Como o agente erra | Por que a configuração atual permite isso | Consequência |
|---------|--------------------|-------------------------------------------|-------------|
| S-01 Boot obediente, contexto inventado | Segue `roadmap_execution`, encontra path inexistente e completa o boot por inferência | O profile declarava ordem obrigatória, mas sem garantia de resolvibilidade | Contexto de sessão nasce incompleto e o agente inventa próximos passos |
| S-02 PASS local mascarado como PASS canônico | Roda validação parcial, vê PASS e trata como baseline global | O sistema sobrescrevia `latest.json`/dashboards com run parcial | Continuidade segue com falso sinal verde |
| S-03 DONE sem prova | Preenche handoff com texto plausível e marca `resultado: DONE` | Schema/template/gate não exigiam evidência mínima vinculada ao CI real | Sessão seguinte continua sem base verificável |
| S-04 Divergência de IR com obediência superficial | Um agente lê `.dev`, outro lê `.contract_driven/decisions` | As fontes concorrentes coexistiam como aparentemente válidas | Dois caminhos coerentes localmente, incompatíveis globalmente |
| S-05 Progresso aparente sem cobertura | Módulo sobe para `validated_contract`/`implementation_ready` sem superfícies mínimas | Gate de coerência não exigia evidência suficiente | DONE parcial é vendido como DONE real |
| S-06 Roteamento para documento morto | Agente segue README/ADR/README de OpenAPI e cai em `API_CONVENTIONS.md`/`ERROR_MODEL.md` inexistentes | Artefatos soberanos ainda apontavam para documentos removidos | Decisões plausíveis, mas desalinhadas do canon atual |
| S-07 Derivado parece saudável, mas não corresponde à fonte | Fonte soberana muda; baseline/manifests não são regenerados | Não havia reparo automático após cada correção | Auditoria ou CI seguinte entra em conflito com artefatos gerados |
| S-08 Gate bloqueante falha sem breaking change real | `oasdiff` existe e funciona, mas o wrapper força caminho com `nvm` e timeout | Regra genérica demais para ferramenta não-Node | Agente trava em falso bloqueio operacional |
| S-09 Continuidade aponta para evidência antiga | Handoff permanece preso a run anterior após novas correções | O handoff não era sincronizado com a evidência final da rodada | Sessão seguinte reconstrói estado desatualizado |

## PARTE 4 — Plano de correções finais
| ID da falha | Correção necessária | Prioridade | Arquivo(s) a corrigir | Critério de aceite |
|-------------|---------------------|------------|-----------------------|--------------------|
| F-01 | Corrigir paths dos boot profiles e bloquear boot com path/section irresolvível | P0 | `.contract_driven/BOOT_PROFILES.yaml`, `scripts/hb`, `docs/_canon/AGENT_INSTRUCTIONS.md` | `hb verify` falha se profile apontar para arquivo/section inexistente |
| F-02 | Separar persistência de relatório parcial e canônico; impedir overwrite de baseline global | P0 | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/CONTRACT_PIPELINE.md`, `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | Run parcial grava arquivo escopado e `latest.json` canônico permanece intacto |
| F-03 | Endurecer schema/template/gate do handoff e exigir evidência real | P0 | `SESSION_HANDOFF.md`, schema/template do handoff, `docs/_canon/gates/GATES_REGISTRY.yaml` | Handoff sem evidência ou sem coerência boot/task/CI falha gate |
| F-04 | Exigir superfícies mínimas e evidência pré-contrato para status elevado | P0 | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/gates/GATES_REGISTRY.yaml` | Módulo elevado sem superfícies/evidência resulta em FAIL |
| F-05 | Unificar autoridade do Decision IR em path canônico único | P0 | validator, gate registry, Decision IRs de módulo | Gate lê uma única fonte canônica e aceita formato explícito |
| F-06 | Remover ponteiros para documentos mortos/IR antigo em artefatos soberanos e operacionais | P1 | `README.md`, docs em `docs/_canon/**`, `contracts/openapi/README.md`, ADRs | Varredura por refs mortas retorna vazio nos artefatos-alvo |
| F-07 | Formalizar baseline backfill para módulos legados | P1 | `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `_reports/agent_execution/*.json`, validator | Evidência legada só conta se declarada como reconstrução explícita |
| F-08 | Alinhar política de header com a realidade dos docs de módulo | P2 | `.contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml` | Gate de crossref deixa de falhar por regra incorreta |
| F-09 | Regenerar derivados e manifests após ajustes soberanos | P0 | `generated/manifests/*.traceability.yaml`, baselines OpenAPI, derivados correlatos | `DERIVED_DRIFT_GATE` volta a PASS |
| F-10 | Fazer CLI anunciar o caminho real do relatório gerado | P2 | `scripts/contracts/validate/validate_contracts.py` | Run parcial imprime arquivo escopado, não `latest.json` |
| F-11 | Tornar `_try_tool` direto por padrão e remover timeout/interop artificial para não-Node | P0 | `scripts/contracts/validate/validate_contracts.py` | `CONTRACT_BREAKING_CHANGE_GATE` não falha quando `oasdiff` direto retorna `0` |

## PARTE 5 — Correções aplicadas
| ID | Arquivo alterado | Mudança aplicada | Falha corrigida | Justificativa |
|----|------------------|------------------|-----------------|---------------|
| F-01 | `.contract_driven/BOOT_PROFILES.yaml`, `scripts/hb`, `docs/_canon/AGENT_INSTRUCTIONS.md` | Paths corrigidos para repo-root, `path_resolution` explícito e validação estrutural de `load_sequence`/`required_sections` adicionada ao boot | F-01 | Sem resolvibilidade verificável, “boot determinístico” era só retórica |
| F-02 | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/CONTRACT_PIPELINE.md`, `docs/_canon/TOOLCHAIN_HEALTH_POLICY.md` | Execução parcial passou a gravar `stage-*.latest.json`; apenas `profile=ci` sem `--stage` atualiza `latest.json`, dashboards e scorecards canônicos | F-02 | Remove a rota de falso PASS global |
| F-03 | `contracts/schemas/shared/session_handoff.schema.json`, `docs/_canon/templates/SESSION_HANDOFF.template.md`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `SESSION_HANDOFF.md` | `modo_operacao`, `task_type`, `boot_profile_id`, `evidence_paths` e seção `## Evidências` tornados obrigatórios; gate virou bloqueante; handoff sincronizado com run final | F-03, F-09 | Continuidade sem prova deixou de passar silenciosamente |
| F-04 | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/gates/GATES_REGISTRY.yaml` | Gates de status/surface promotion passaram a falhar quando faltam superfícies esperadas ou evidência mínima | F-04 | Impede promoção de progresso sem cobertura |
| F-05 | `scripts/contracts/validate/validate_contracts.py`, `docs/_canon/gates/GATES_REGISTRY.yaml`, `docs/_canon/gates/README.md`, `.contract_driven/decisions/DECISION_IR_TRAINING.yaml`, `docs/hbtrack/modulos/training/DECISION_IR_TRAINING.yaml` | Authority unificada em `.contract_driven/decisions/DECISION_IR_<MODULE>.yaml`; mirror legado marcado como não soberano | F-05 | Fecha bifurcação entre duas fontes “válidas” |
| F-06 | `README.md`, `docs/_canon/ARCHITECTURE.md`, `docs/_canon/DATA_CONVENTIONS.md`, `docs/_canon/CHANGE_POLICY.md`, `docs/_canon/CI_CONTRACT_GATES.md`, ADRs e `contracts/openapi/README.md`, `generated/contracts/openapi/README.md` | Referências mortas e ponteiros para IR antigo removidos; README/baselines passaram a apontar para `OPERATIONS.md` e fonte canônica atual | F-06 | Roteamento deixou de depender de documento inexistente |
| F-07 | `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `_reports/agent_execution/2026-03-23_*_baseline_backfill.json`, `scripts/contracts/validate/validate_contracts.py` | Regra `baseline_backfill` criada; backfills explícitos gerados para módulos legados; validator exige `reconstructed_from` | F-07 | Continuidade histórica deixa de ser presumida |
| F-08 | `.contract_driven/templates/modulos/MODULE_DOC_HEADER_POLICY.yaml` | Campos opcionais alinhados ao uso real em docs de módulo | F-08 | Elimina correção errada induzida por política mais rígida que a realidade |
| F-09 | `scripts/generate/gen_openapi_baseline.py` executado, `contracts/openapi/baseline/openapi_baseline.json`, `generated/contracts/openapi/baseline/openapi_baseline.json`, `generated/manifests/*.traceability.yaml` | Baselines OpenAPI regenerados e manifests reparados com `scripts/repair_manifests.py` | F-09 | Fecha drift derivado introduzido pelas correções soberanas |
| F-10 | `scripts/contracts/validate/validate_contracts.py` | `report_artifacts.scoped_report_path` adicionado ao payload e CLI passou a imprimir o caminho real do relatório produzido | F-10 | Evita leitura humana incorreta do arquivo de evidência |
| F-11 | `scripts/contracts/validate/validate_contracts.py` | `_try_tool` passou a executar direto por padrão, com fallback `nvm` apenas para binários Node ausentes no PATH e timeout maior | F-11 | Remove falso FAIL operacional em `oasdiff` |

## PARTE 6 — Reteste adversarial
- Cenários eliminados:
  - `S-01`: `hb verify` passou a validar `boot_profile structure (paths + required_sections resolvíveis)`.
  - `S-02`: execução parcial agora grava `_reports/contract_gates/stage-session-start.local.latest.json`; `latest.json` permaneceu `PASS` com `canonical_scope=full_pipeline`.
  - `S-03`: `HANDOFF_COHERENCE_GATE` passou em stage-local e o handoff final carrega `modo_operacao`, `task_type`, `boot_profile_id` e `evidence_paths` válidos.
  - `S-04`: gate de Decision IR passou usando a fonte canônica única `.contract_driven/decisions/DECISION_IR_<MODULE>.yaml`.
  - `S-05`: `MODULE_STATUS_COHERENCE_GATE` passou após endurecimento das checagens de superfícies/evidências.
  - `S-06`: varredura final por `API_CONVENTIONS.md`, `ERROR_MODEL.md`, `MODULE_DECISION_IR.json` e `.dev/MODULE_DECISION_IR` em `docs/_canon`, `contracts/openapi`, `generated/contracts/openapi`, prompts relevantes e `README.md` retornou vazio.
  - `S-08`: `CONTRACT_BREAKING_CHANGE_GATE` voltou a `PASS` após correção do wrapper `_try_tool`.
  - `S-09`: `SESSION_HANDOFF.md` foi sincronizado para `_reports/runs/20260323T151553_055f66/{contract_gates.json,health.json}` e validado novamente via `hb verify`.
- Cenários que ainda restam:
  - Nenhum bloqueador material remanescente foi reproduzido após a rodada final.
- Cenários apenas reduzidos:
  - Drift de derivados ainda continua sendo risco operacional sempre que uma fonte soberana muda; porém agora ele é bloqueado por `DERIVED_DRIFT_GATE` e corrigível de forma determinística por regeneração + `scripts/repair_manifests.py`. Isso reduz o risco a residual não bloqueante, porque não permite PASS silencioso.
- Evidência objetiva do reteste:
  - `python3 -m py_compile scripts/contracts/validate/validate_contracts.py scripts/hb scripts/generate/gen_module_doc_templates.py` → PASS
  - `python3 scripts/generate/gen_openapi_baseline.py --input contracts/openapi/openapi.yaml --output contracts/openapi/baseline/openapi_baseline.json` → PASS
  - `python3 scripts/generate/gen_openapi_baseline.py --input generated/contracts/openapi/openapi.yaml --output generated/contracts/openapi/baseline/openapi_baseline.json` → PASS
  - `python3 scripts/repair_manifests.py` → PASS
  - `python3 scripts/contracts/validate/validate_contracts.py --profile ci` → PASS
  - `python3 scripts/hb verify --task-type execute_roadmap_phase --module training` → PASS
  - `_reports/contract_gates/latest.json` → `overall_status=PASS`, `canonical_scope=full_pipeline`, `run_dir=/home/davis/HB-TRACK/_reports/runs/20260323T151553_055f66`
  - `_reports/contract_gates/stage-session-start.local.latest.json` → `overall_status=PASS`, `canonical_scope=partial_validation`
- Se ainda existe qualquer bloqueador material:
  - **Não**

## PARTE 7 — Veredito final binário
- Após as correções finais, a configuração passa ou reprova? **Passa**
- Ainda é possível provar alucinação ou perda de direção antes do DONE? **Não**
- Ainda existem gaps, lacunas ou inconsistências materiais? **Não**
- O sistema agora está robusto o suficiente para que uma análise adversarial razoável não encontre bloqueadores materiais remanescentes? **Sim**
