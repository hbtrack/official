╔════════════════════════════════════════════════════════════════════════════╗
║       AUDITORIA DE EFICIÊNCIA DE CONTEXTO — HB TRACK                      ║
╚════════════════════════════════════════════════════════════════════════════╝

Data: 2026-03-18T01:43:08.842147
Executor: audit_context_efficiency.py v1.0.0

SUB-TESTE A — MEDIÇÃO DE ORÇAMENTO
────────────────────────────────────────────────────────────────────────────────
Artefato                              │ Budget │ Real │ Status │ Delta
────────────────────────────────────────────────────────────────────────────────
AGENT_INSTRUCTIONS.md                │    450 │  378 │ ✓ PASS │   -72
CONTRACT_PIPELINE.md                 │    600 │  338 │ ✓ PASS │  -262
pre_contract_orchestrator.prompt.md  │    700 │  394 │ ✓ PASS │  -306

Total de palavras do boot: 1110
CE1 (Budget): ✓ PASS

SUB-TESTE B — ALCANÇABILIDADE DE REGRAS CRÍTICAS
────────────────────────────────────────────────────────────────────────────────
Regra Crítica                                │ Status     │ Detalhes
────────────────────────────────────────────────────────────────────────────────
Bloqueios canônicos (19 códigos)         │ ✓ PASS     │ Hop 1
Mapa task_type → worker                  │ ✓ PASS     │ Hop 1
Condição de bloqueio de fase pré-contrat │ ✓ PASS     │ Hop 1
Ordem de precedência de conflito         │ ✓ PASS     │ Hop 1

CE2 (Pointers):      ✓ PASS
CE3 (Orphans):       ✓ PASS
CE4 (Redundancy):    ✓ PASS
CE5 (Implicit):      ✓ PASS

════════════════════════════════════════════════════════════════════════════════
RESULTADO FINAL: ✓ PASS
════════════════════════════════════════════════════════════════════════════════
