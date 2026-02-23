# AR_064 — Cleanup rogue: _agent/, agentes/, .github/cont + resolve GATES_REGISTRY conflict

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
LIMPEZA DE ESTRUTURAS ROGUES criadas pelo Executor sem AR:

--- ITEM 1: docs/_canon/_agent/ (dir rogue — DEV FLOW §2.2 não define este path) ---
Arquivos dentro:
  - GATES_REGISTRY.yaml (v2.0) — DIFERENTE de docs/_canon/specs/GATES_REGISTRY.yaml (v1.0). Renomear para CAPABILITY_GATES_REGISTRY.yaml antes de mover.
  - FAILURE_TO_GATES.yaml — relacionado ao CAPABILITY_GATES (v2.0). Mover junto.
  - CORRECTION_WRITE_ALLOWLIST.yaml — paths incorretos (lista app/, web/ que não existem). Deletar.
  - SCRIPTS_classification.md — marcado 'DERIVED FILE — DO NOT EDIT'. Verificar se scripts/_policy/scripts.policy.yaml existe. Se não existir, deletar também.

AÇÕES:
  a) Renomear docs/_canon/_agent/GATES_REGISTRY.yaml → docs/_canon/specs/CAPABILITY_GATES_REGISTRY.yaml
  b) Mover docs/_canon/_agent/FAILURE_TO_GATES.yaml → docs/_canon/specs/FAILURE_TO_GATES.yaml
  c) Deletar docs/_canon/_agent/CORRECTION_WRITE_ALLOWLIST.yaml (paths inválidos para este projeto)
  d) Verificar docs/_canon/_agent/SCRIPTS_classification.md: se scripts/_policy/scripts.policy.yaml NÃO existir, deletar; se existir, mover para docs/_canon/specs/
  e) Deletar diretório vazio docs/_canon/_agent/

--- ITEM 2: docs/_canon/agentes/ (dir rogue — artefato histórico) ---
Arquivos dentro:
  - BATCH_001_exec_assignments.yaml — plano histórico de execução dual do batch de 2026-02-20 (ARs 010-020). Já consumido.

AÇÃO:
  Mover para docs/hbtrack/ars/governance/BATCH_001_exec_assignments.yaml (artefato histórico de AR, não contrato ativo)
  Deletar diretório vazio docs/_canon/agentes/

--- ITEM 3: .github/cont (prompt do Testador no lugar errado) ---
Conteúdo: prompt do Agente Testador (equivalente ao .github/agents/executor.agent.md para o Executor)

AÇÃO:
  Renomear/mover .github/cont → .github/agents/testador.agent.md

--- ITEM 4: Duplicate plan governance/infra_004_cleanup_dead_files.json ---
AR_046 está declarada em DOIS planos JSON:
  - docs/_canon/planos/governance/governance/infra_004_cleanup_dead_files.json (AR id=046)
  - docs/_canon/planos/governance/AR_064_gov_auditoria.json (AR id=046)

AÇÃO:
  Verificar qual AR_046.md existe em docs/hbtrack/ars/. Adicionar campo 'status: SUPERSEDED' ao AR_046 dentro de AR_064_gov_auditoria.json (ou remover a task 046 de AR_064 e manter apenas no infra_004_cleanup). Não deletar nenhum plan JSON — apenas sincronizar.

## Critérios de Aceite
1. find docs/_canon/_agent -type f | wc -l retorna 0 (dir removido ou vazio).
2. python -c "import pathlib; assert not pathlib.Path('docs/_canon/_agent').exists() or not list(pathlib.Path('docs/_canon/_agent').iterdir()), 'FAIL: _agent dir not empty'; print('PASS')" exits 0.
3. find docs/_canon/agentes -type f | wc -l retorna 0 (dir removido).
4. python -c "import pathlib; p=pathlib.Path('.github/agents/testador.agent.md'); assert p.exists(), f'FAIL: {p} not found'; print('PASS: testador.agent.md present')" exits 0.
5. python -c "import pathlib; assert not pathlib.Path('.github/cont').exists(), 'FAIL: .github/cont still exists'; print('PASS')" exits 0.
6. python -c "import pathlib; p=pathlib.Path('docs/_canon/specs/CAPABILITY_GATES_REGISTRY.yaml'); assert p.exists(), f'FAIL: {p} missing'; print('PASS: capability gates moved')" exits 0.

## Validation Command (Contrato)
```
python -c "import pathlib; errors=[]; p1=pathlib.Path('docs/_canon/_agent'); errors.append('_agent dir still has files') if p1.exists() and list(p1.iterdir()) else None; p2=pathlib.Path('docs/_canon/agentes'); errors.append('agentes dir still has files') if p2.exists() and list(p2.iterdir()) else None; p3=pathlib.Path('.github/agents/testador.agent.md'); errors.append('testador.agent.md missing') if not p3.exists() else None; p4=pathlib.Path('.github/cont'); errors.append('.github/cont still exists') if p4.exists() else None; p5=pathlib.Path('docs/_canon/specs/CAPABILITY_GATES_REGISTRY.yaml'); errors.append('CAPABILITY_GATES_REGISTRY missing') if not p5.exists() else None; assert not errors, 'FAIL: ' + str(errors); print('PASS: all rogue artifacts cleaned')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_064_cleanup_rogue_dirs.log`

## Notas do Arquiteto
NOTA SOBRE GATES_REGISTRY CONFLICT:
  docs/_canon/specs/GATES_REGISTRY.yaml (v1.0) = gates de GOVERNANÇA (DB, schema, AR status, infra)
  docs/_canon/_agent/GATES_REGISTRY.yaml (v2.0) = gates de CAPABILITY (AUTH, RBAC, ATHLETES) para runner externo
  São documentos DISTINTOS com o mesmo nome — colisão de nomenclatura.
  Solução: renomear o v2.0 para CAPABILITY_GATES_REGISTRY.yaml (mais descritivo e sem colisão).

NOTA SOBRE CORRECTION_WRITE_ALLOWLIST.yaml:
  Paths listados (app/, web/, tests/) não existem no projeto HB Track.
  O projeto usa 'Hb Track - Backend/app/', 'Hb Track - Frontend/'.
  Este arquivo é inválido para este projeto — deletar é seguro.

## Riscos
- Antes de deletar SCRIPTS_classification.md, verificar existência de scripts/_policy/scripts.policy.yaml.
- BATCH_001_exec_assignments.yaml pode ser referenciado em algum script — grep antes de mover.
- .github/cont pode estar referenciado em .github/copilot-instructions.md ou outros — verificar antes de renomear.
- Ao mover CAPABILITY_GATES_REGISTRY.yaml, verificar se algum script o referencia pelo path antigo (_agent/).

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**:
1. ITEM 1 (`docs/_canon/_agent/`): GATES_REGISTRY.yaml → `docs/_canon/specs/CAPABILITY_GATES_REGISTRY.yaml`; FAILURE_TO_GATES.yaml → `docs/_canon/specs/`; CORRECTION_WRITE_ALLOWLIST.yaml deletado (paths inválidos: app/, web/, tests/ não existem no projeto); SCRIPTS_classification.md → `docs/_canon/specs/` (scripts.policy.yaml confirmado existente); diretório vazio removido.
2. ITEM 2 (`docs/_canon/agentes/`): BATCH_001_exec_assignments.yaml → `docs/hbtrack/ars/governance/` (artefato histórico); diretório vazio removido.
3. ITEM 3 (`.github/cont`): movido para `.github/agents/testador.agent.md` (convenção canônica para prompts de agente).
4. ITEM 4 (AR_046 duplicidade): AR_064_gov_auditoria.json NÃO contém AR_046 — nenhuma ação necessária.

**Impacto**: Estrutura de diretórios `docs/_canon/` agora segue DEV FLOW §2.2; conflito de nomenclatura GATES_REGISTRY resolvido via renomeação para CAPABILITY_GATES_REGISTRY; agente testador agora tem prompt canônico em `.github/agents/`.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; errors=[]; p1=pathlib.Path('docs/_canon/_agent'); errors.append('_agent dir still has files') if p1.exists() and list(p1.iterdir()) else None; p2=pathlib.Path('docs/_canon/agentes'); errors.append('agentes dir still has files') if p2.exists() and list(p2.iterdir()) else None; p3=pathlib.Path('.github/agents/testador.agent.md'); errors.append('testador.agent.md missing') if not p3.exists() else None; p4=pathlib.Path('.github/cont'); errors.append('.github/cont still exists') if p4.exists() else None; p5=pathlib.Path('docs/_canon/specs/CAPABILITY_GATES_REGISTRY.yaml'); errors.append('CAPABILITY_GATES_REGISTRY missing') if not p5.exists() else None; assert not errors, 'FAIL: ' + str(errors); print('PASS: all rogue artifacts cleaned')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_064_cleanup_rogue_dirs.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_064_b2e7523/result.json`
