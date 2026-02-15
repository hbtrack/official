# SPEC: Validação Local de Gates CI/CD (HB Track)

Metadados
Versão: 1.0.0
Data: 2026-02-15
Status: APPROVED
Autor: HB Track Team
Artefato-alvo: `scripts/checks/check_ci_gates_local.ps1` (orquestrador)
Objetivo: impedir falhas no CI/CD executando, localmente e antes de `git push`, o mesmo conjunto de gates executados no pipeline.

---

## 0. Linguagem normativa (BCP14)

As palavras-chave **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY** e **OPTIONAL** devem ser interpretadas conforme BCP14 (RFC 2119 + RFC 8174).

---

## 1. Escopo

1.1. Este SPEC define o contrato de execução local dos gates de conformidade e governança que equivalem aos gates do CI/CD.

1.2. Este SPEC cobre:

* Requisitos de execução (ambiente e paths).
* Interface do orquestrador local.
* Contrato de output (tabela determinística).
* Matriz determinística de gates (ordem, comandos, equivalência no CI).
* Semântica de exit codes (por gate e do orquestrador).
* Operação opcional via hook de pre-push.

1.3. Este SPEC **não** redefine as regras internas de cada gate (ex.: HB001–HB009); ele define como os gates são **orquestrados**, **executados** e **reportados** localmente.

---

## 2. Pré-requisitos e invariantes de ambiente

2.1. Execução no repo root
O usuário **MUST** executar os comandos a partir do root do repositório (ex.: `C:\HB TRACK`). O orquestrador **MUST** falhar com erro explícito se não conseguir resolver o root.

2.2. PowerShell
O orquestrador e scripts `.ps1` **MUST** ser executados em PowerShell (preferencialmente `pwsh`). Se o ambiente não suportar execução, o processo **MUST** retornar exit code de erro (seção 6).

2.3. Python (para gates que dependem de Python)
Quando `Language Protocol` e/ou `Path Constants` estiverem habilitados, o runtime Python **MUST** estar disponível e executável via `python`. Caso contrário, o gate correspondente **MUST** falhar (ou ser marcado como ERROR) e o orquestrador **MUST** propagar falha (seção 6).

2.4. Determinismo de execução

* O orquestrador **MUST** executar os gates sempre na mesma ordem definida na matriz determinística (seção 5).
* O orquestrador **MUST** produzir output com colunas e cabeçalho estáveis (seção 4).
* Flags `-Skip*` **MUST** resultar em status `SKIP` para o gate correspondente, sem execução do comando do gate.

---

## 3. Interface do orquestrador (check_ci_gates_local.ps1)

3.1. Comando canônico (default)

```powershell
.\scripts\checks\check_ci_gates_local.ps1
```

3.2. Opções (contrato)

* `-FailFast` (OPTIONAL)
  Se presente, o orquestrador **MUST** interromper a execução no primeiro gate com falha (FAIL/ERROR) e **MUST** retornar imediatamente com exit code não-zero.

* Flags de skip (OPTIONAL)
  Cada flag abaixo **MUST** desabilitar somente o gate indicado e marcar o gate como `SKIP` no relatório final:

  * `-SkipScriptsPolicy`
  * `-SkipLanguageLinter`
  * `-SkipManifest`
  * `-SkipDrift`
  * `-SkipPathConstants`

3.3. Defaults
Na ausência de flags `-Skip*`, o orquestrador **MUST** executar todos os gates definidos na matriz (seção 5).

---

## 4. Contrato de output (tabela determinística)

4.1. Formato mínimo REQUIRED
O orquestrador **MUST** imprimir um resumo tabular com as colunas, nesta ordem exata:

`Gate | Status | ExitCode`

4.2. Cabeçalho e separador REQUIRED
O output **MUST** conter, no mínimo, as duas linhas (ou equivalentes) que representam cabeçalho e separador:

```
Gate                Status   ExitCode
----                ------   --------
```

4.3. Status válidos
O orquestrador **MUST** usar somente estes status (case-sensitive):

* `PASS` (gate executou e passou)
* `FAIL` (gate executou e falhou por violação/drift/paridade/etc.)
* `ERROR` (gate executou, mas ocorreu erro operacional: exceção, arquivo não encontrado, runtime ausente, etc.)
* `SKIP` (gate não executou por flag de skip)

4.4. Linha de conclusão
Se (e somente se) todos os gates resultarem em `PASS` ou `SKIP`, o orquestrador **MUST** imprimir:

```
✅ ALL GATES PASS - Safe to push!
```

Caso contrário, o orquestrador **MUST NOT** imprimir essa linha.

4.5. Determinismo da ordem
A tabela **MUST** listar os gates exatamente na ordem definida em 5.1.

---

## 5. Matriz determinística de gates

### 5.1. Ordem e equivalência CI (REQUIRED)

| Ordem | Gate               | Descrição normativa                                                                                | Comando (local)                                   | Equivale a (CI)                                        |
| ----: | ------------------ | -------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------ |
|     1 | Scripts Policy     | Valida headers HB_SCRIPT, taxonomia, prefixos e side-effects (HB001–HB009).                        | `& 'scripts\_policy\check_scripts_policy.ps1'`    | `.github/workflows/scripts-policy.yml`                 |
|     2 | Language Protocol  | Valida linguagem promocional/conversacional em docs via linter.                                    | `python docs\scripts\_ia\ai_governance_linter.py` | `.github/workflows/governance-protocol-validation.yml` |
|     3 | Manifest Integrity | Verifica hashes SHA256 anti-tamper de policies.                                                    | `scripts\_policy\check_policy_manifest.ps1`       | `scripts-policy.yml` (Manifest check)                  |
|     4 | Policy MD Sync     | Verifica que `SCRIPTS_classification.md` é derivado e está sincronizado com `scripts.policy.yaml`. | `scripts\_policy\check_policy_md_is_derived.ps1`  | `scripts-policy.yml` (Drift check)                     |
|     5 | Path Constants     | Verifica consistência de constantes entre Python e PowerShell.                                     | `python scripts\_policy\check_path_constants.py`  | `scripts-policy.yml` (Consistency check)               |

### 5.2. Regras de execução por gate (REQUIRED)

* Cada gate **MUST** ser executado em processo isolado (invocação separada) para preservar semântica de exit code.
* A ausência de arquivos REQUIRED por um gate (ex.: script não encontrado) **MUST** resultar em `ERROR` para aquele gate.
* Um gate marcado como `SKIP` **MUST NOT** executar seu comando.

---

## 6. Semântica de exit codes

### 6.1. Exit codes por gate (normativo)

* Scripts Policy (`check_scripts_policy.ps1`)

  * `0` = PASS
  * `2` = FAIL (VIOLATION)
  * `3` = ERROR

* Governance Language Linter (`ai_governance_linter.py`)

  * `0` = PASS
  * `>0` = FAIL (WARNINGS/violations reportadas pelo linter)
    Observação normativa: o orquestrador **MUST** tratar `>0` como `FAIL` (não como `ERROR`).

* Policy Manifest (`check_policy_manifest.ps1`)

  * `0` = PASS
  * `2` = FAIL (DRIFT)
  * `3` = ERROR

* Policy Markdown Drift (`check_policy_md_is_derived.ps1`)

  * `0` = PASS
  * `2` = FAIL (DRIFT)
  * `3` = ERROR

* Path Constants (`check_path_constants.py`)

  * `0` = PASS (JSON válido)
  * `!=0` = ERROR/FAIL conforme implementação do script
    Regra do orquestrador: se o script retornar `!=0`, o orquestrador **MUST** marcar como `FAIL` quando houver violação de consistência e **MUST** marcar como `ERROR` quando houver falha operacional (ex.: crash). Se não houver como distinguir, **MUST** marcar como `ERROR`.

### 6.2. Exit code do orquestrador (REQUIRED)

* Se todos os gates executados resultarem em `PASS` e todos os pulados em `SKIP`, o orquestrador **MUST** retornar `0`.
* Caso exista ao menos um `FAIL` ou `ERROR`, o orquestrador **MUST** retornar um exit code não-zero.
* Se `-FailFast` estiver habilitado, o exit code do orquestrador **MUST** ser o exit code do primeiro gate que falhar.

---

## 7. Modos de operação (receitas normativas)

7.1. Validar tudo antes de push (RECOMMENDED)

```powershell
.\scripts\checks\check_ci_gates_local.ps1
```

7.2. Fail-fast (OPTIONAL; RECOMMENDED para ciclos rápidos)

```powershell
.\scripts\checks\check_ci_gates_local.ps1 -FailFast
```

7.3. Executar somente Scripts Policy (OPTIONAL; uso consciente)

```powershell
.\scripts\checks\check_ci_gates_local.ps1 `
  -SkipLanguageLinter `
  -SkipManifest `
  -SkipDrift `
  -SkipPathConstants
```

7.4. Executar somente Language Protocol (OPTIONAL; uso consciente)

```powershell
.\scripts\checks\check_ci_gates_local.ps1 `
  -SkipScriptsPolicy `
  -SkipManifest `
  -SkipDrift `
  -SkipPathConstants
```

---

## 8. Workflow operacional (RECOMMENDED)

8.1. Antes de commit

* O usuário **SHOULD** garantir working tree limpa (ou conscientemente suja) antes de validar.

```powershell
git status --porcelain
.\scripts\checks\check_ci_gates_local.ps1
git add .
git commit -m "feat: ..."
```

8.2. Antes de push (REQUIRED para compatibilidade CI)

```powershell
.\scripts\checks\check_ci_gates_local.ps1
git push origin <branch>
```

8.3. Pull Request
O CI **SHALL** executar gates equivalentes. Se o usuário executou o orquestrador local sem falhas, o CI **SHOULD** passar, salvo diferenças de ambiente.

---

## 9. Troubleshooting (contratos mínimos)

9.1. “Python não encontrado”
Se Python não estiver disponível:

* Gates Python **MUST** resultar em `ERROR` (ou `FAIL` quando aplicável, conforme seção 6).
* O usuário **SHOULD** ativar venv relevante ou instalar Python 3.11+.

9.2. “policy_lib.py not found” / arquivos de policy ausentes
O orquestrador **MUST** verificar se está no repo root. Se não estiver, **MUST** falhar com mensagem explícita orientando `Set-Location` para o root.

9.3. “Falhou mas não sei o motivo”
O usuário **SHOULD** executar o gate individual correspondente para obter output detalhado. Quando um script suportar `-Verbose`, o usuário **MAY** habilitá-lo.

---

## 10. Documentação relacionada (referências internas)

* `docs/_canon/_agent/SCRIPTS_classification.md` (Policy Governance)
* `docs/_canon/LANGUAGE_PROTOCOL.md` (Language Protocol)
* `docs/references/exit_codes.md` (Exit Codes)
* `.github/workflows/scripts-policy.yml`, `.github/workflows/governance-protocol-validation.yml` (CI/CD)

---

## Apêndice A (OPTIONAL): Hook de pre-push

A.1. Template (PowerShell)

```powershell
$HookContent = @'
#!/usr/bin/env pwsh
Set-Location (git rev-parse --show-toplevel)
.\scripts\checks\check_ci_gates_local.ps1 -FailFast
exit $LASTEXITCODE
'@

$HookPath = ".git\hooks\pre-push"
Set-Content -Path $HookPath -Value $HookContent -Encoding UTF8
```

A.2. Semântica

* `git push` **MUST** ser bloqueado se o hook retornar exit code `!= 0`.
* O bypass via `git push --no-verify` é **NOT RECOMMENDED** e **SHOULD NOT** ser usado exceto em incidentes controlados.


