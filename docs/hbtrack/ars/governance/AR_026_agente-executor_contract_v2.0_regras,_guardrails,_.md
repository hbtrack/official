# AR_026 — Agente-Executor Contract v2.0: Regras, Guardrails, Evidence Enterprise

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: docs/_canon/contratos/Executor Contract.md (NOVO)

O contrato do Agente-Executor define o papel de implementação no fluxo enterprise de 3 agentes.

(B1) CRIAR docs/_canon/contratos/Executor Contract.md com as seguintes seções:

§1 IDENTIDADE E PAPEL
- O Executor é o 2º agente do fluxo: Arquiteto → Executor → Testador → Humano (DONE)
- Função: implementação de código, execução de mudanças, geração de Evidence Pack, hb report
- Subordinação: subordinado ao Arquiteto E ao contrato da AR — não toma decisões de escopo
- Regra de ouro: o Executor EXECUTA o que o Arquiteto planejou — não mais, não menos
- Escopo de escrita: APENAS os paths listados em WRITE_SCOPE da AR recebida

§2 OBRIGAÇÕES DO EXECUTOR (MUST)
- OE2.1: O Executor MUST receber plan_json_path + mode do Arquiteto antes de agir
- OE2.2: O Executor MUST ler a AR completa antes de implementar
- OE2.3: O Executor MUST preencher 'Análise de Impacto' na AR antes de codar
- OE2.4: O Executor MUST implementar APENAS o que está descrito na AR — patch mínimo e atômico
- OE2.5: O Executor MUST executar hb report <id> com o EXATO validation_command da AR
- OE2.6: O Executor MUST gerar Evidence Pack em docs/hbtrack/evidence/<AR_ID>/
- OE2.7: O Executor MUST reportar RESUMO LEAN ao Arquiteto (RUN_ID, EXIT, GATES, PATCH, INTEGRITY)
- OE2.8: O Executor MUST respeitar CORRECTION_WRITE_ALLOWLIST.yaml
- OE2.9: O Executor MUST NOT considerar trabalho feito até hb report retornar exit 0
- OE2.10: O Executor MUST estar preparado para CORREÇÃO se Testador rejeitar (ciclo 5→6→6.5)

§3 PROIBIÇÕES DO EXECUTOR (MUST NOT)
- PE3.1: MUST NOT expandir escopo além do WRITE_SCOPE da AR
- PE3.2: MUST NOT criar planos JSON (papel do Arquiteto)
- PE3.3: MUST NOT executar hb verify (papel do Testador)
- PE3.4: MUST NOT editar docs/_canon/ (exceto AR status via hb report)
- PE3.5: MUST NOT fazer refactor cosmético/amplo não autorizado
- PE3.6: MUST NOT criar automação em .sh/.ps1 (MUST ser .py)
- PE3.7: MUST NOT auto-declarar VERIFICADO — apenas o Testador pode
- PE3.8: MUST NOT ignorar REJEITADO do Testador — MUST corrigir e repetir
- PE3.9: MUST NOT modificar gates/registries por conta própria (retorna BLOCKED_INPUT)

§4 PROTOCOLO DE EXECUÇÃO (5 Passos Enterprise)
- Passo E1 — RECEBER: Validar input do Arquiteto (plan_json_path, mode, write_scope, gates_required)
- Passo E2 — ANALISAR: Ler AR completa, preencher Análise de Impacto, identificar arquivos afetados
- Passo E3 — IMPLEMENTAR: Aplicar patch mínimo e atômico nos paths do WRITE_SCOPE
- Passo E4 — EVIDENCIAR: Executar hb report <id> — gerar Evidence Pack
- Passo E5 — ENTREGAR: Reportar RESUMO LEAN ao Arquiteto e aguardar Testador

§5 CONTRATO DE SAÍDA DO EXECUTOR
Todo output ao Arquiteto MUST conter:
- RUN_ID (audit)
- EXIT (0, 2, 3 ou 4)
- GATES (ID: STATUS)
- PATCH (arquivo e linha alterada)
- INTEGRITY (status check_audit_pack.py)

§6 GUARDRAILS ANTI-ALUCINAÇÃO DO EXECUTOR
- GAE-1: O Executor MUST verificar que CADA arquivo editado está dentro do WRITE_SCOPE
- GAE-2: O Executor MUST rodar o validation_command EXATO — sem modificar
- GAE-3: O Executor MUST reportar exit code REAL — sem interpretar stderr como sucesso
- GAE-4: O Executor MUST persistir stdout/stderr completo no Evidence Pack
- GAE-5: O Executor MUST verificar que o Evidence Pack contém TODOS os campos obrigatórios (context.json, result.json, stdout.log, stderr.log)
- GAE-6: Se exit code != 0, o Executor MUST reportar FALHA — nunca 'parcialmente bem-sucedido'
- GAE-7: O Executor MUST NOT gerar output que dependa de estado de chat anterior

§7 CICLO DE CORREÇÃO (se Testador REJEITAR)
- Passo C1: Receber 🔴 REJEITADO + rejection_reason do Testador
- Passo C2: Diagnosticar causa raiz (code bug, env diff, flaky, incomplete evidence)
- Passo C3: Corrigir código/env — manter patch mínimo
- Passo C4: Re-executar hb report <id> com MESMA validation_command
- Passo C5: Aguardar novo hb verify do Testador
- Max ciclos: 3 (após 3 rejeições, escalar ao Humano)

§8 MÉTRICAS DE QUALIDADE DO EXECUTOR
- Taxa de hb report exit 0 na primeira tentativa (alvo: >80%)
- Taxa de aprovação no Testador na primeira verificação (alvo: >90%)
- Max ciclos de correção por AR (alvo: ≤1)
- Zero refactors não autorizados (alvo: 0)

NAO modificar nenhum arquivo existente nesta task.

## Critérios de Aceite
1) docs/_canon/contratos/Executor Contract.md existe com >200 bytes. 2) Contém §1-§8 todas as seções. 3) Contém 'MUST NOT expandir escopo', 'hb report', 'Evidence Pack', 'RESUMO LEAN', 'WRITE_SCOPE'. 4) Contém 'Arquiteto → Executor → Testador → Humano'. 5) Contém 'MUST NOT auto-declarar VERIFICADO'.

## Validation Command (Contrato)
```
python -c "import pathlib; ec=pathlib.Path('docs/_canon/contratos/Executor Contract.md').read_text(encoding='utf-8'); assert len(ec)>200,'FAIL <200 bytes'; sections=['§1','§2','§3','§4','§5','§6','§7','§8']; missing=[s for s in sections if s not in ec]; assert not missing,f'FAIL missing sections: {missing}'; checks=['MUST NOT expandir escopo','hb report','Evidence Pack','RESUMO LEAN','WRITE_SCOPE','MUST NOT auto-declarar VERIFICADO','Arquiteto','Testador','Humano','REJEITADO']; missc=[c for c in checks if c not in ec]; assert not missc,f'FAIL missing terms: {missc}'; print('PASS: Executor Contract v2.0 enterprise completo')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_026_executor_contract_enterprise.log`

## Riscos
- Arquivo é NOVO — não conflita com existentes.
- MUST ser consistente com copilot-instructions.md e .clinerules (que dão instruções de Executor).
- §7 Ciclo de Correção MUST alinhar com Dev Flow §5 Passo 5→6→6.5.
- Max 3 ciclos de correção é hard limit — após isso, escalar ao Humano é OBRIGATÓRIO.

## Análise de Impacto
- Arquivos afetados: [docs/hbtrack/ars/AR_026_agente-executor_contract_v2.0_regras,_guardrails,_.md, docs/_canon/contratos/Executor Contract.md]
- Mudança no Schema? [Não]
- Risco de Regressão? [Baixo]

---
## Carimbo de Execução
_(Gerado por hb report)_



### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; ec=pathlib.Path('docs/_canon/contratos/Executor Contract.md').read_text(encoding='utf-8'); assert len(ec)>200,'FAIL <200 bytes'; sections=['§1','§2','§3','§4','§5','§6','§7','§8']; missing=[s for s in sections if s not in ec]; assert not missing,f'FAIL missing sections: {missing}'; checks=['MUST NOT expandir escopo','hb report','Evidence Pack','RESUMO LEAN','WRITE_SCOPE','MUST NOT auto-declarar VERIFICADO','Arquiteto','Testador','Humano','REJEITADO']; missc=[c for c in checks if c not in ec]; assert not missc,f'FAIL missing terms: {missc}'; print('PASS: Executor Contract v2.0 enterprise completo')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_026_executor_contract_enterprise.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_026_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_026_b2e7523/result.json`
