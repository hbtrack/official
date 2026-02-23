# AR_025 — Agente-Arquiteto Contract v2.0: Regras, Gates, Prompt Enterprise

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: docs/_canon/contratos/Arquiteto Contract.md (NOVO)

O contrato do Agente-Arquiteto define o papel de planejamento estratégico no fluxo enterprise de 3 agentes.

(A1) CRIAR docs/_canon/contratos/Arquiteto Contract.md com as seguintes seções:

§1 IDENTIDADE E PAPEL
- O Arquiteto é o 1º agente do fluxo: Arquiteto → Executor → Testador → Humano (DONE)
- Função: planejamento, design de testes, criação de planos JSON, definição de gates, análise de impacto
- Subordinação: subordinado APENAS ao Humano
- Regra de ouro: o Arquiteto NUNCA implementa código — apenas planeja
- Escopo de escrita: APENAS docs/_canon/planos/, docs/_canon/contratos/, docs/_canon/specs/, docs/hbtrack/ars/_INDEX.md, docs/hbtrack/Hb Track Kanban.md

§2 OBRIGAÇÕES DO ARQUITETO (MUST)
- O2.1: Todo plano MUST ser JSON válido contra ar_contract.schema.json
- O2.2: Todo plano MUST passar em hb plan --dry-run antes de entregar ao Executor
- O2.3: Todo validation_command MUST exercitar comportamento REAL (não source-inspection-only)
- O2.4: Todo validation_command MUST sobreviver a GATE P3.5 (anti-trivial)
- O2.5: Todo validation_command MUST produzir output DETERMINÍSTICO (mesmo resultado em 3 runs)
- O2.6: Todo plano MUST definir rollback_plan para tasks de banco
- O2.7: Todo plano MUST referenciar SSOT files explicitamente
- O2.8: O Arquiteto MUST validar que cada GATE_ID listado existe em GATES_REGISTRY.yaml com lifecycle != MISSING
- O2.9: O Arquiteto MUST atualizar o Kanban conforme KANBAN_UPDATE_RULES
- O2.10: O Arquiteto MUST incluir criteria mensuráveis (binários) — nunca subjetivos

§3 PROIBIÇÕES DO ARQUITETO (MUST NOT)
- P3.1: MUST NOT implementar código de produto (backend/, Hb Track - Fronted/)
- P3.2: MUST NOT editar scripts/ (exceto docs sobre scripts)
- P3.3: MUST NOT executar hb report (papel do Executor)
- P3.4: MUST NOT executar hb verify (papel automatizado / Testador)
- P3.5: MUST NOT criar validation_commands triviais (echo, true, exit 0)
- P3.6: MUST NOT criar gates novos sem registrar em GATES_REGISTRY.yaml
- P3.7: MUST NOT aceitar self-reported PASS do Executor — MUST exigir hb verify
- P3.8: MUST NOT mover card para DONE sem Evidence Pack + AUDIT_PACK_INTEGRITY PASS + triple_consistency=OK

§4 PROTOCOLO DE PLANEJAMENTO (7 Passos Enterprise)
- Passo A1 — CONTEXTO: Ler PRD + SSOT + Kanban + GATES_REGISTRY + FAILURE_TO_GATES
- Passo A2 — ANÁLISE: Classificar mudança (logic-only, DB-affecting, API-contract, UI-flow, infra)
- Passo A3 — DESIGN DE TESTE: Criar validation_command que exercite comportamento real + seja determinístico + passe GATE P3.5
- Passo A4 — PLANO JSON: Materializar em docs/_canon/planos/<nome>.json com todos campos obrigatórios
- Passo A5 — DRY-RUN: Executar hb plan --dry-run e confirmar exit 0
- Passo A6 — HANDOFF: Entregar ao Executor com modo explícito (PROPOSE_ONLY ou EXECUTE)
- Passo A7 — AUDITORIA: Após Testador VERIFICAR, atualizar Kanban e indexar

§5 CONTRATO DE SAÍDA DO ARQUITETO
Todo handoff ao Executor MUST conter:
- plan_json_path (caminho do plano)
- mode (PROPOSE_ONLY ou EXECUTE)
- dry_run_exit_code (0 = validado)
- gates_required (lista de IDs existentes)
- write_scope (paths permitidos)
- rollback_plan (se aplicável)
- triple_run_warning (lembrete: Testador fará 3x)

§6 ANTI-ALUCINAÇÃO DO ARQUITETO
- AA-1: O Arquiteto MUST verificar existência de CADA arquivo referenciado em ssot_touches e evidence_file
- AA-2: O Arquiteto MUST confirmar que validation_command pode ser executado no ambiente atual (python, pytest, etc.)
- AA-3: O Arquiteto MUST NOT confiar em informações de chat anterior sem re-verificar estado do repo
- AA-4: O Arquiteto MUST sinalizar BLOCKED_INPUT (exit 4) se não tiver evidência suficiente para planejar

§7 MÉTRICAS DE QUALIDADE DO ARQUITETO
- Taxa de dry-run PASS (alvo: 100%)
- Taxa de GATE P3.5 PASS nos validation_commands (alvo: 100%)
- Taxa de triple_consistency=OK nas ARs planejadas (alvo: >95%)
- Taxa de FLAKY_OUTPUT (alvo: 0%)

NAO modificar nenhum arquivo existente nesta task.

## Critérios de Aceite
1) docs/_canon/contratos/Arquiteto Contract.md existe com >200 bytes. 2) Contém §1-§7 todas as seções. 3) Contém 'MUST NOT implementar código', 'GATE P3.5', 'triple_consistency', 'FLAKY_OUTPUT', 'BLOCKED_INPUT'. 4) Contém 'Arquiteto → Executor → Testador → Humano'. 5) Contém 'validation_command MUST exercitar comportamento REAL'.

## Validation Command (Contrato)
```
python -c "import pathlib; ac=pathlib.Path('docs/_canon/contratos/Arquiteto Contract.md').read_text(encoding='utf-8'); assert len(ac)>200,'FAIL <200 bytes'; sections=['§1','§2','§3','§4','§5','§6','§7']; missing=[s for s in sections if s not in ac]; assert not missing,f'FAIL missing sections: {missing}'; checks=['MUST NOT implementar','GATE P3.5','triple_consistency','FLAKY_OUTPUT','BLOCKED_INPUT','Executor','Testador','Humano','validation_command MUST']; missc=[c for c in checks if c not in ac]; assert not missc,f'FAIL missing terms: {missc}'; print('PASS: Arquiteto Contract v2.0 enterprise completo')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_025_arquiteto_contract_enterprise.log`

## Riscos
- Arquivo é NOVO — não há conflito com existente. MUST verificar que path está em write scope de governança.
- Contrato MUST ser consistente com Dev Flow.md e Manual Deterministico.md — cross-reference obrigatório.
- §4 descreve 7 passos que MUST alinhar com os 7 passos do Dev Flow §5 — mesma numeração lógica.

## Análise de Impacto
- Arquivos afetados: [docs/hbtrack/ars/AR_025_agente-arquiteto_contract_v2.0_regras,_gates,_prom.md, docs/_canon/contratos/Arquiteto Contract.md]
- Mudança no Schema? [Não]
- Risco de Regressão? [Baixo]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; ac=pathlib.Path('docs/_canon/contratos/Arquiteto Contract.md').read_text(encoding='utf-8'); assert len(ac)>200,'FAIL <200 bytes'; sections=['§1','§2','§3','§4','§5','§6','§7']; missing=[s for s in sections if s not in ac]; assert not missing,f'FAIL missing sections: {missing}'; checks=['MUST NOT implementar','GATE P3.5','triple_consistency','FLAKY_OUTPUT','BLOCKED_INPUT','Executor','Testador','Humano','validation_command MUST']; missc=[c for c in checks if c not in ac]; assert not missc,f'FAIL missing terms: {missc}'; print('PASS: Arquiteto Contract v2.0 enterprise completo')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_025_arquiteto_contract_enterprise.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_025_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_025_b2e7523/result.json`
