# AR_054 — Fix Arquiteto Contract §1: INDEX path errado + DEV FLOW consistency

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
PROBLEMA RAIZ RECORRENTE: O Arquiteto Contract.md §1 declara o escopo de escrita do Arquiteto como incluindo 'docs/hbtrack/ars/_INDEX.md' — mas o índice CANÔNICO escrito por rebuild_ar_index() é 'docs/hbtrack/_INDEX.md'. Toda vez que um agente lê o contrato e acredita que ars/_INDEX.md é o SSOT, o caos se repete. Esta é a causa raiz da 5ª quebra do INDEX.

FIXES NECESSÁRIOS:

--- FIX 1: Arquiteto Contract.md §1 ---
Arquivo: docs/_canon/contratos/Arquiteto Contract.md
Localização: linha 14, §1 'Escopo de escrita'

ANTES:
  - Escopo de escrita: APENAS `docs/_canon/planos/`, `docs/_canon/contratos/`, `docs/_canon/specs/`, `docs/hbtrack/ars/_INDEX.md`, `docs/hbtrack/Hb Track Kanban.md`.

DEPOIS:
  - Escopo de escrita: APENAS `docs/_canon/planos/`, `docs/_canon/contratos/`, `docs/_canon/specs/`, `docs/hbtrack/_INDEX.md` (canônico — escrito por rebuild_ar_index()), `docs/hbtrack/Hb Track Kanban.md`.
  - LEGADO (read-only): `docs/hbtrack/ars/_INDEX.md` — arquivo histórico, NÃO é SSOT.

--- FIX 2: DEV FLOW.md §2.2 ---
Arquivo: docs/_canon/contratos/Dev Flow.md
Localização: §2.2 linha 'Índice'

Adicionarr nota explícita após a linha do Índice:
  > NOTA: `docs/hbtrack/ars/_INDEX.md` é arquivo LEGADO (formato pré-v1.1.0 com status DRAFT). NÃO é SSOT. O índice canônico é `docs/hbtrack/_INDEX.md`, gerado automaticamente por `hb plan`/`hb report` via `rebuild_ar_index()`.

--- FIX 3: hb_watch trigger DRAFT ---
O hb_watch.py:25 tem 'DRAFT' em EXECUTOR_TRIGGERS. Este trigger nunca dispara no índice canônico (que usa PENDENTE). Documentar no contrato infra_003_hb_watch.json que DRAFT é trigger legado/dead-code após AR_053.
  Arquivo: docs/_canon/planos/infra/infra_003_hb_watch.json
  Adicionar no campo 'notes' (se existir) ou 'description': nota sobre DRAFT trigger sendo dead-code após AR_053 Fix 2.

--- FIX 4: Arquiteto Contract.md §2 O2.9 ---
O2.9 diz 'O Arquiteto MUST atualizar Kanban conforme KANBAN_UPDATE_RULES'. Mas não existe documento KANBAN_UPDATE_RULES. Clarificar que o Arquiteto atualiza o Kanban MANUALMENTE enquanto AR_055 não for executada.
  Após O2.9 adicionar: '(manual até AR_055 — hb_cli.py não escreve automaticamente no Kanban.md)'

## Critérios de Aceite
1. grep 'docs/hbtrack/_INDEX.md' 'docs/_canon/contratos/Arquiteto Contract.md' retorna >= 1 match (path canônico presente).
2. grep 'ars/_INDEX.md' 'docs/_canon/contratos/Arquiteto Contract.md' | grep -v 'LEGADO\|histórico\|read-only' retorna 0 matches (referência errada removida ou marcada como legado).
3. grep 'LEGADO' 'docs/_canon/contratos/Dev Flow.md' retorna >= 1 match (nota adicionada).
4. python -c "content=open('docs/_canon/contratos/Arquiteto Contract.md',encoding='utf-8').read(); assert 'docs/hbtrack/_INDEX.md' in content; assert 'LEGADO' in content or 'canônico' in content; print('PASS')" exits 0.

## Validation Command (Contrato)
```
python -c "c=open('docs/_canon/contratos/Arquiteto Contract.md',encoding='utf-8').read(); assert 'docs/hbtrack/_INDEX.md' in c, 'FAIL: canonical path missing'; df=open('docs/_canon/contratos/Dev Flow.md',encoding='utf-8').read(); assert 'LEGADO' in df or 'canônico' in df, 'FAIL: DEV FLOW missing legacy note'; print('PASS: contracts updated correctly')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_054_contract_index_path_fix.log`

## Notas do Arquiteto
IMPORTANTE: DEV FLOW §1 diz que mudanças em docs/_canon/contratos/** MUST ser via AR de governança com bump de versão. Esta AR É a AR de governança. Após execução, o Executor DEVE:
1. Fazer bump de versão no cabeçalho de Arquiteto Contract.md (ex.: v2.0.0 → v2.1.0)
2. Fazer bump de versão no cabeçalho de Dev Flow.md (ex.: v1.1.0 → v1.1.1)
3. Atualizar hb_cli.py HB_PROTOCOL_VERSION se necessário

O Executor NÃO deve fazer mais nada além dos 4 fixes descritos acima. Mínimo cirúrgico.

## Riscos
- Arquiteto Contract.md está na linha 14 — verificar linha exata antes de editar.
- Dev Flow.md tem múltiplas seções — adicionar nota SOMENTE em §2.2, não em outro lugar.
- Version bump dos contratos: verificar header format antes de editar (pode ser '# ARQUITETO_CONTRACT — HB Track (Determinístico) — v2.0.0').

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: 4 fixes cirúrgicos em contratos:
1. `Arquiteto Contract.md §1`: path canônico `docs/hbtrack/_INDEX.md` + nota LEGADO
2. `Dev Flow.md §2.2`: nota LEGADO sobre `ars/_INDEX.md`
3. `infra_003_hb_watch.json`: nota DRAFT trigger dead-code (já feito em AR_053)
4. `Arquiteto Contract.md §2 O2.9`: clarificação Kanban manual até AR_055

**Version bumps**: Arquiteto Contract v2.0.0 → v2.1.0, Dev Flow v1.1.0 → v1.1.1

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "c=open('docs/_canon/contratos/Arquiteto Contract.md',encoding='utf-8').read(); assert 'docs/hbtrack/_INDEX.md' in c, 'FAIL: canonical path missing'; df=open('docs/_canon/contratos/Dev Flow.md',encoding='utf-8').read(); assert 'LEGADO' in df or 'canônico' in df, 'FAIL: DEV FLOW missing legacy note'; print('PASS: contracts updated correctly')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_054_contract_index_path_fix.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_054_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_054_b2e7523/result.json`
