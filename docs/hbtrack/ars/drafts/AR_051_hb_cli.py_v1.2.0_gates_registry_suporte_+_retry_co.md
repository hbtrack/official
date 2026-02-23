# AR_051 — hb_cli.py v1.2.0: GATES_REGISTRY suporte + retry_count schema + bump versão

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.1.0

## Descrição
CONTEXTO: GATES_REGISTRY.yaml v1.0 criado pelo Arquiteto em docs/_canon/specs/GATES_REGISTRY.yaml. O hb_cli.py deve ser atualizado para v1.2.0 para referenciar e validar contra o registry.

AÇÃO DO EXECUTOR em scripts/run/hb_cli.py:

1) BUMP DE VERSÃO:
   HB_PROTOCOL_VERSION = '1.2.0'
   Adicionar no docstring/changelog v1.2.0:
     Changelog v1.2.0:
       - AR_051: GATES_REGISTRY.yaml — path canônico GATES_REGISTRY_PATH
       - AR_051: cmd_gates_list() — lista gates ativos do registry
       - AR_051: cmd_gates_check(gate_id) — verifica gate específico
       - AR_051: retry_count gate em cmd_plan() — bloqueia ARs com retry >= MAX_RETRY_THRESHOLD

2) ADICIONAR CONSTANTE:
   GATES_REGISTRY_PATH = 'docs/_canon/specs/GATES_REGISTRY.yaml'
   (Logo após SCHEMA_PATH na seção CONFIGURAÇÃO)

3) IMPLEMENTAR cmd_gates_list():
   Ler GATES_REGISTRY.yaml, listar gates com id, name, lifecycle.
   Formato: '  [ACTIVE] GATE_ID — name'
   Se arquivo não existe: erro E_GATES_REGISTRY_MISSING.

4) IMPLEMENTAR cmd_gates_check(gate_id):
   Localizar gate por id no GATES_REGISTRY.yaml.
   Exibir required_proofs e lifecycle.
   Se gate não encontrado: erro E_GATE_NOT_FOUND.

5) ADICIONAR AO cmd_plan() — gate O2.8:
   Após a validação do schema JSON, verificar se os gates referenciados nas tasks existem no GATES_REGISTRY.yaml com lifecycle != MISSING.
   Se um gate não existir no registry: erro E_GATE_NOT_IN_REGISTRY.
   (Somente se GATES_REGISTRY.yaml existir — gate é soft quando arquivo ausente para não quebrar planos legados)

6) ATUALIZAR main() para rotear:
   'hb gates list' → cmd_gates_list()
   'hb gates check <id>' → cmd_gates_check(id)

NAO alterar lógica de hb plan/report/check/verify existente além do gate O2.8 em cmd_plan().
NAO alterar ar_contract.schema.json — retry_count já existe como campo no schema v1.1.1.

## Critérios de Aceite
1) python scripts/run/hb_cli.py version retorna 'HB Track Protocol v1.2.0'. 2) python scripts/run/hb_cli.py gates list retorna lista com pelo menos 5 gates ACTIVE. 3) python scripts/run/hb_cli.py gates check DB_MIGRATIONS_UPGRADE_HEAD retorna informações do gate. 4) hb_cli.py tem constante GATES_REGISTRY_PATH apontando para docs/_canon/specs/GATES_REGISTRY.yaml. 5) hb check --mode manual ainda sai com exit code 0 (sem regressão).

## Validation Command (Contrato)
```
python scripts/run/hb_cli.py version && python scripts/run/hb_cli.py gates list && python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert \"HB_PROTOCOL_VERSION = '1.2.0'\" in src or '\"1.2.0\"' in src, 'FAIL: version not 1.2.0'; assert 'GATES_REGISTRY_PATH' in src, 'FAIL: GATES_REGISTRY_PATH missing'; assert 'cmd_gates_list' in src, 'FAIL: cmd_gates_list missing'; print('PASS: hb_cli.py v1.2.0 structure verified')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_051_hb_cli_v120.log`

## Notas do Arquiteto
PyYAML já está disponível no venv (verificar com 'python -c import yaml'). Se não disponível, usar json.loads com um YAML subset parser simples ou pip install pyyaml. GATES_REGISTRY.yaml usa formato YAML 1.1 compatível com PyYAML 5+.

## Riscos
- Gate O2.8 deve ser SOFT (warning, não erro) quando GATES_REGISTRY.yaml não existe, para não quebrar planos legados que não têm campo gate.
- PyYAML pode não estar instalado — verificar antes de implementar. Alternativa: usar safe_load com fallback.

## Análise de Impacto
**Executor**: Claude Sonnet 4.6 (Modo Executor)
**Data**: 2026-02-22

**Escopo**: `scripts/run/hb_cli.py` — versão bumped v1.1.0 → v1.2.0; `GATES_REGISTRY_PATH` adicionado; `cmd_gates_list()` e `cmd_gates_check()` implementados; `main()` atualizado com routing `gates list | gates check <id>`. Gate O2.8 implementado como soft (PyYAML, non-blocking para planos legados).

**Impacto**: `hb gates list` agora exibe 14 ACTIVE gates. `hb gates check <id>` exibe proofs de triangulação por gate. Nenhuma regressão em hb plan/report/verify/check.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python scripts/run/hb_cli.py version && python scripts/run/hb_cli.py gates list && python -c "import re, pathlib; src=pathlib.Path('scripts/run/hb_cli.py').read_text(encoding='utf-8'); assert \"HB_PROTOCOL_VERSION = '1.2.0'\" in src or '\"1.2.0\"' in src, 'FAIL: version not 1.2.0'; assert 'GATES_REGISTRY_PATH' in src, 'FAIL: GATES_REGISTRY_PATH missing'; assert 'cmd_gates_list' in src, 'FAIL: cmd_gates_list missing'; print('PASS: hb_cli.py v1.2.0 structure verified')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_051_hb_cli_v120.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_051_b2e7523/result.json`

### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_051_b2e7523/result.json`
