# AR_210 — Fix compute_behavior_hash: normalizar timings pytest no stdout_norm

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Modificar scripts/run/hb_cli.py para normalizar tempos de execucao do pytest antes do calculo do behavior_hash. O problema: pytest inclui linhas como '3 passed in 0.43s' ou '0.12s call' no stdout, valores que variam entre runs e causam FLAKY_OUTPUT no triple-run do hb verify, mesmo com os testes passando. Acao exata: (1) Adicionar import re no topo se nao existir (ja existe na linha 35). (2) Em compute_behavior_hash, apos montar o payload via _norm_newlines, aplicar normalizacao do timing antes do sha256: substituir re.sub(r'\b\d+\.\d+s\b', 'X.Xs', payload) antes de sha256. OU: adicionar funcao auxiliar _norm_timing(s) que aplica esta substituicao e chamar em compute_behavior_hash. Na funcao compute_behavior_hash, o payload normalizado deve ser: payload_norm = re.sub(r'\b\d+\.\d+s\b', 'X.Xs', f'{exit_code}\n{_norm_newlines(stdout)}\n---STDERR---\n{_norm_newlines(stderr)}'). Persistir o hash do payload_norm.

## Critérios de Aceite
1) scripts/run/hb_cli.py contem regex de normalizacao de timing (padrao \b\d+\.\d+s\b ou equivalente) em compute_behavior_hash ou em funcao auxiliar chamada por ela. 2) compute_behavior_hash(0,'1 passed in 0.01s','') == compute_behavior_hash(0,'1 passed in 0.99s',''). 3) Validacao inline Python retorna 'OK: timing-agnostic'. 4) Regressao: compute_behavior_hash(0,'OK','') ainda produz string hexadecimal nao-vazia.

## Write Scope
- scripts/run/hb_cli.py

## Validation Command (Contrato)
```
python -c "import importlib.util,sys;sys.path.insert(0,'.');spec=importlib.util.spec_from_file_location('hb_cli','scripts/run/hb_cli.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);h1=m.compute_behavior_hash(0,'1 passed in 0.01s','');h2=m.compute_behavior_hash(0,'1 passed in 0.99s','');assert h1==h2,'FAIL: timing not normalized: '+h1+' != '+h2;h3=m.compute_behavior_hash(1,'1 passed in 0.01s','');assert h1!=h3,'FAIL: exit_code diff lost';print('OK: timing-agnostic + exit_code still discriminates')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_210/executor_main.log`

## Riscos
- Se o regex for muito amplo (ex: \d+s sem ponto decimal), pode normalizar inteiros com 's' em outro contexto
- Testar que compute_behavior_hash(0,'PASSED','') ainda difere de compute_behavior_hash(1,'PASSED','') apos o fix

## Análise de Impacto

**Arquivo modificado:** `scripts/run/hb_cli.py`

**Função afetada:** `compute_behavior_hash` (linha 314) — chamada pelo triple-run de `hb verify` para gerar o hash de cada run e comparar consistência entre os 3.

**Causa raiz confirmada:** A função usa `_norm_newlines` que normaliza apenas CRLF→LF. O pytest emite timings flutuantes (`N passed in X.XXs`) no stdout que variam mesmo com testes passando, resultando em `payload` diferente a cada run e hashes SHA-256 distintos → `FLAKY_OUTPUT`.

**Impacto do patch:**
- Adiciona `re.sub(r'\b\d+\.\d+s\b', 'X.Xs', payload)` após montar o `payload` e antes do `hashlib.sha256`.
- `import re` já existe na linha 36 — sem novo import necessário.
- Assinatura pública de `compute_behavior_hash(exit_code, stdout, stderr)` inalterada.
- Hash resultante muda (normalização adicional), mas deterministicamente — todos os invocadores existentes são internos ao `hb_cli.py` (triple-run).
- Nenhum outro arquivo é alterado.
- Risco de regressão: mitigado — `exit_code` e conteúdo não-timing do stdout/stderr continuam discriminando.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import importlib.util,sys;sys.path.insert(0,'.');spec=importlib.util.spec_from_file_location('hb_cli','scripts/run/hb_cli.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);h1=m.compute_behavior_hash(0,'1 passed in 0.01s','');h2=m.compute_behavior_hash(0,'1 passed in 0.99s','');assert h1==h2,'FAIL: timing not normalized: '+h1+' != '+h2;h3=m.compute_behavior_hash(1,'1 passed in 0.01s','');assert h1!=h3,'FAIL: exit_code diff lost';print('OK: timing-agnostic + exit_code still discriminates')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-03T04:06:38.628549+00:00
**Behavior Hash**: d51c1fe3a50f943bfac361e303d29a7b1fd0a9bd64b5fcedacb04271c58830aa
**Evidence File**: `docs/hbtrack/evidence/AR_210/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_210_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-03T04:14:55.588788+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_210_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_210/executor_main.log`
