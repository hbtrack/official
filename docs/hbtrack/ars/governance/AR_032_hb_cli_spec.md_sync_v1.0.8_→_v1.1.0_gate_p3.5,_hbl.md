# AR_032 — Hb cli Spec.md: sync v1.0.8 → v1.1.0 (GATE P3.5, HBLock, SHA-256, triple-run)

**Status**: ✅ SUCESSO
**Versão do Protocolo**: 1.1.0

## Descrição
ARQUIVO ALVO: docs/_canon/specs/Hb cli Spec.md

Divergências detectadas entre a Spec (v1.0.8) e o CLI real (v1.1.0). O Executor DEVE aplicar os patches abaixo em ordem, sem remover conteúdo existente salvo onde explicitamente indicado.

## PATCH S1 — Header e §1: Versão

Substituir TODAS as ocorrências de '1.0.8' por '1.1.0' no arquivo.
Substituir 'v1.0.6' por 'v1.1.0' na linha de saída do hb version (§1 item 1).

Resultado esperado em §1:
```
# SPEC_HB_CLI — scripts/run/hb_cli.py (HB CLI) — v1.1.0
...
hb_cli.py MUST ter:
- HB_PROTOCOL_VERSION = "1.1.0"
...
1) `python scripts/run/hb_cli.py version`
   Saída determinística:
   - "HB Track Protocol v1.1.0"
```

## PATCH S2 — §5 hb plan: GATE P3.5 (E_TRIVIAL_CMD)

ADICIONAR após o item 'P4) plan.version MUST == HB_PROTOCOL_VERSION' e ANTES do 'GATE 2) IDs únicos':

```
GATE P3.5) Anti-trivial: validation_command de cada task MUST ser não-trivial.
    Padrões triviais detectados e bloqueados:
    - Regex: `^\s*echo\s`, `^\s*true\s*$`, `^\s*exit\s+0\s*$`, `^\s*:\s*$`
    - Comprimento < 30 chars sem ASSERTION_KEYWORDS (assert, pytest, unittest, -c, verify, check, validate)
    Se trivial: FAIL E_TRIVIAL_CMD (exit 2)
```

## PATCH S3 — §5 hb plan: HBLock

ADICIONAR ao final do §5 (após 'Dependência: hb plan usa biblioteca jsonschema'):

```
Concorrência:
- hb plan usa HBLock (file-based lock em .hb_lock) para operações de escrita atômica.
- Se lock retido por outro processo: FAIL E_CLI_LOCKED (exit 3) após MAX_RETRIES=10 tentativas.
```

## PATCH S4 — §6 hb report: SHA-256 e workspace

ADICIONAR ao §6 após 'R3) executar comando e gravar:', ANTES de 'Exit codes do hb report':

```
Evidence Integrity (AR_029):
- Antes de gravar: captura governed_checksums (SHA-256 hex[:16] de arquivos em GOVERNED_ROOTS staged/modified via git diff HEAD).
- Captura workspace_status (git status --porcelain).
- Grava no evidence pack:
    Governed Checksums: {json}
    Workspace Status: clean|dirty_files=N
- hb report usa HBLock para escrita concorrente segura.
```

## PATCH S5 — §10 hb verify: TRIPLE_RUN + FLAKY_OUTPUT + workspace

Substituir 'V4) Re-executar validation_command (independente — não reutilizar output do Executor)' por:

```
V4) Re-executar validation_command TRIPLE_RUN_COUNT=3 vezes (independente).
    Para cada run: capturar exit code e sha256(stdout)[:16] como stdout_hash.
    - Se qualquer run exit != 0: triple_consistency = 'FAIL'
    - Se todos exit 0 MAS stdout_hash diferente entre runs: triple_consistency = 'FLAKY_OUTPUT'
    - Se todos exit 0 E stdout_hash idêntico: triple_consistency = 'OK'
    FLAKY_OUTPUT => REJEITADO (output não-determinístico).

Pre-check workspace (antes do triple-run):
    check_workspace_clean() via git status --porcelain.
    Se dirty: WARNING impresso (não bloqueia, mas registrado no TESTADOR_REPORT).

Post-check checksums (após o triple-run):
    compare governed_checksums pre vs post verify.
    Se pre != post: WARNING 'checksum_drift' no TESTADOR_REPORT.
```

## PATCH S6 — §8 Error codes: adicionar novos códigos de v1.1.0

ADICIONAR nova subseção APÓS 'Códigos adicionais (v1.0.6 — novos gates)':

```
Códigos adicionados (v1.1.0 — enterprise):
- E_TRIVIAL_CMD   (GATE P3.5: validation_command trivialmente passável)
- E_TRIPLE_FAIL   (hb verify: triple-run com exit != 0)
- E_CLI_LOCKED    (HBLock: lock file retido após MAX_RETRIES tentativas)
```

## PATCH S7 — Novo §13: HBLock (concorrência)

ADICIONAR nova seção ao FINAL do documento (após §12):

```
## 13. HBLock — Concorrência entre agentes (v1.1.0)

Implementação: AR_028.

O hb_cli.py usa um file-based lock (`.hb_lock`) para garantir atomicidade de escrita quando
múltiplos agentes (Arquiteto, Executor, Testador) operam em paralelo.

Comandos que usam HBLock:
- hb plan (materialização de ARs)
- hb report (gravação de evidence + carimbo na AR)
- hb verify (gravação de TESTADOR_REPORT + carimbo na AR)

Parâmetros:
- MAX_RETRIES = 10 (tentativas com backoff aleatório 100-500ms)
- Lock file: .hb_lock (deve estar no .gitignore)
- Em caso de lock órfão: remover manualmente o arquivo .hb_lock
- Em caso de exceder MAX_RETRIES: FAIL E_CLI_LOCKED (exit 3)
```

## PATCH S8 — Novo §14: Changelog

ADICIONAR nova seção ao FINAL do documento (após §13):

```
## 14. Changelog

| Versão | Data       | Descrição                                                              |
|--------|------------|------------------------------------------------------------------------|
| 1.0.5  | —          | Versão original (schema, plan, report, check)                          |
| 1.0.6  | —          | Novos gates: E_DUPLICATE_IDS, E_AR_COLLISION, E_ROLLBACK_MISSING/INVALID |
| 1.0.8  | —          | hb verify (Testador), novos status, C3 version-aware                   |
| 1.1.0  | 2026-02-21 | GATE P3.5, HBLock, SHA-256 evidence integrity, triple-run FLAKY_OUTPUT |
```

NÃO remover nenhuma seção existente (§1 a §12).
NÃO modificar scripts/run/hb_cli.py (FORBIDDEN pelo contrato).

## Critérios de Aceite
1) Título contém 'v1.1.0'. 2) §1 HB_PROTOCOL_VERSION = '1.1.0'. 3) §1 hb version output = 'v1.1.0'. 4) '1.0.6' NÃO aparece como string de versão de output. 5) GATE P3.5 documentado com E_TRIVIAL_CMD. 6) HBLock documentado em §5, §6 e §13. 7) SHA-256/governed_checksums documentado em §6. 8) TRIPLE_RUN_COUNT=3 e FLAKY_OUTPUT documentados em §10. 9) E_TRIVIAL_CMD, E_TRIPLE_FAIL, E_CLI_LOCKED em §8. 10) CLI real reporta v1.1.0 (gate comportamental).

## Validation Command (Contrato)
```
python -c "import pathlib,subprocess,sys; spec=pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8'); assert '1.1.0' in spec[:200],'FAIL: 1.1.0 not in header'; assert '1.0.8' not in spec[:200],'FAIL: old 1.0.8 still in header'; assert '1.0.6' not in spec[:500],'FAIL: old v1.0.6 output string still present'; kws=['E_TRIVIAL_CMD','TRIPLE_RUN_COUNT','FLAKY_OUTPUT','E_TRIPLE_FAIL','E_CLI_LOCKED','HBLock','SHA-256']; missing=[k for k in kws if k not in spec]; assert not missing,f'FAIL missing: {missing}'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.' in v.stdout,f'FAIL CLI version={v.stdout.strip()}'; print('PASS: Hb cli Spec v1.x sincronizado com CLI real')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_032_hb_cli_spec_v110_sync.log`

## Notas do Arquiteto
WRITE_SCOPE permitido: docs/_canon/specs/Hb cli Spec.md APENAS. FORBIDDEN: scripts/run/hb_cli.py e qualquer outro arquivo.

## Riscos
- §1 contém duas strings de versão: HB_PROTOCOL_VERSION e o output do hb version — ambas MUST ser atualizadas
- A linha 'HB Track Protocol v1.0.6' em §1 é a string de output — Executor MUST substituir por 'v1.1.0'
- Substituir '1.0.8' por '1.1.0' globalmente pode afetar referências históricas — verificar APENAS header e §1
- PATCH S5 substitui V4 existente — Executor MUST copiar texto original antes de substituir para não perder estrutura
- HBLock MUST ser mencionado em §5 (plan), §6 (report) e §10 (verify) além do novo §13
- Não tocar GOVERNED_ROOTS — valor ['backend/', 'Hb Track - Fronted/'] está correto

## Análise de Impacto
**Executor**: Roo (Executor HB Track)
**Data**: 2026-02-22

**Estado Atual - Hb cli Spec.md**:
- ✅ S1 (Header e §1): JÁ atualizado para v1.1.0 na AR-024
- ✅ S2 (GATE P3.5): JÁ adicionado na AR-024 (P3.5 com E_TRIVIAL_CMD)
- ❗ S3 (HBLock em §5): FALTA implementar
- ❗ S4 (SHA-256 em §6): FALTA implementar  
- ⚠️ S5 (V4 triple-run): PARCIAL na AR-024, precisa adicionar workspace checks
- ✅ S6 (Error codes): JÁ adicionado na AR-024 (E_TRIVIAL_CMD, E_TRIPLE_FAIL)
- ❗ S7 (§13 HBLock): FALTA implementar (nova seção)
- ❗ S8 (§14 Changelog): FALTA implementar (nova seção)

**Ações Necessárias**:
1. S3: Adicionar HBLock ao final do §5 hb plan
2. S4: Adicionar SHA-256 evidence integrity ao §6 hb report
3. S5: Expandir V4 em §10 com workspace pre/post checks
4. S6: Adicionar E_CLI_LOCKED aos error codes (S6 adicional)
5. S7: Criar nova seção §13 sobre HBLock
6. S8: Criar nova seção §14 Changelog

**Impacto**:
- Apenas Hb cli Spec.md será modificado (~6 adições)
- Nenhum código (hb_cli.py) será alterado
- Documentação ficará sincronizada com implementação v1.1.0

**Conclusão**: S1, S2 e parte de S6 já feitos na AR-024. Executar S3, S4, S5 (expansão), S6 (E_CLI_LOCKED), S7, S8.

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib,subprocess,sys; spec=pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8'); assert '1.1.0' in spec[:200],'FAIL: 1.1.0 not in header'; assert '1.0.8' not in spec[:200],'FAIL: old 1.0.8 still in header'; assert '1.0.6' not in spec[:500],'FAIL: old v1.0.6 output string still present'; kws=['E_TRIVIAL_CMD','TRIPLE_RUN_COUNT','FLAKY_OUTPUT','E_TRIPLE_FAIL','E_CLI_LOCKED','HBLock','SHA-256']; missing=[k for k in kws if k not in spec]; assert not missing,f'FAIL missing: {missing}'; v=subprocess.run([sys.executable,'scripts/run/hb_cli.py','version'],capture_output=True,text=True,encoding='utf-8'); assert 'v1.' in v.stdout,f'FAIL CLI version={v.stdout.strip()}'; print('PASS: Hb cli Spec v1.x sincronizado com CLI real')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_032_hb_cli_spec_v110_sync.log`
**Python Version**: 3.11.9

