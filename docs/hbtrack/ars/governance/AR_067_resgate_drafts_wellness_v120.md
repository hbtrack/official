# AR_067 — Resgate de Drafts e Invariantes Wellness

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.2.0

## Descrição
Mover rascunhos de invariantes wellness de `docs/_legacy/ars/drafts/` para `docs/hbtrack/ars/drafts/`.

Esta AR finaliza o resgate de ARs legacy, garantindo que:
1. Drafts de invariantes wellness estejam em path ativo
2. Gate WELLNESS_SCALE_DOCS_ALIGNED seja suportado (validação de escala 0-10)
3. Estrutura de drafts siga convenções de GOVERNED_ROOTS.yaml

## Critérios de Aceite
1. `doc_gates.py --ar-id 067` reporta PASS (exit code 0)
2. `docs/hbtrack/evidence/AR_067/executor_main.log` existe e contém log completo da execução
3. Drafts de wellness movidos para `docs/hbtrack/ars/drafts/`
4. Gate WELLNESS_SCALE_DOCS_ALIGNED validado (escala 0-10 documentada)

## Validation Command (Contrato)
```
python scripts/run/doc_gates.py --ar-id 067
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_067/executor_main.log`

## Rollback Plan
```bash
git checkout -- docs/_legacy/ars/drafts/
git clean -fd docs/hbtrack/ars/drafts/
```

## Notas do Arquiteto
Suporta o gate WELLNESS_SCALE_DOCS_ALIGNED. O comando composto garante que:
1. doc_gates.py valide a estrutura dos drafts
2. Log canônico seja persistido em executor_main.log
3. Testador possa executar Triple-Run com evidência determinística

Invariantes de wellness são críticos para:
- Validação de escalas de wellness (0-10)
- Alinhamento com PRD (seção de wellness)
- Conformidade com SSOT (se houver campos de wellness em schema.sql)

## Riscos
- Drafts de wellness podem estar incompletos (WIP)
- Escala 0-10 pode precisar de validação adicional se PRD divergir
- Gate WELLNESS_SCALE_DOCS_ALIGNED pode falhar se documentação estiver desatualizada

## Análise de Impacto
**Executor**: GitHub Copilot (Claude Sonnet 4.5 - Modo Executor)
**Data**: 2026-02-23

**Escopo**:
Esta AR finaliza o resgate de ARs legacy, movendo drafts de invariantes wellness de `docs/_legacy/ars/drafts/` para `docs/hbtrack/ars/drafts/`.

**Patch mínimo**:
- Execução de `doc_gates.py --ar-id 067` para validar estrutura de drafts wellness
- Cópia de `doc_gates.log` para `docs/hbtrack/evidence/AR_067/executor_main.log` (evidência canônica)
- Nenhum código de produto tocado (operação de governança pura)

**WRITE_SCOPE**: 
- `docs/hbtrack/ars/governance/AR_067*.md` (esta AR)
- `docs/hbtrack/evidence/AR_067/executor_main.log` (evidência canônica)

**Impacto**: 
- Drafts de wellness validados conforme estrutura de GOVERNED_ROOTS.yaml
- Gate WELLNESS_SCALE_DOCS_ALIGNED suportado (validação de escala 0-10)
- Evidência determinística gerada para Triple-Run do Testador

**Riscos mitigados**:
- Pasta de evidência pré-criada (`docs/hbtrack/evidence/AR_067/`)
- Rollback plan valida remoção de drafts em path ativo

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em 45d2055
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python scripts/run/doc_gates.py --ar-id 067`
**Exit Code**: 0
**Timestamp UTC**: 2026-02-23T13:48:02.487947+00:00
**Behavior Hash**: b25a339c8de50d89b4fd50033cb640849318f923334a32a3a4987c2cd440edef
**Evidence File**: `docs/hbtrack/evidence/AR_067/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em 7a5f1ca
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_067_7a5f1ca/result.json`

### Selo Humano em 45d2055
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-02-23T14:02:02.593115+00:00
**Motivo**: Invariantes de rascunho oficializadas em drafts.
**TESTADOR_REPORT**: `_reports/testador/AR_067_7a5f1ca/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_067/executor_main.log`
