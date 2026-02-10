# ADR-MODELS-003 — Batch determinístico para varredura e correção de Models (SSOT → Requirements → Gate)

Status: **ACCEPTED**
Data: **2026-02-10**
Deciders: Davi (Tech Lead) + AI Assistant
Relacionado: ADR-MODELS-001 (Gate Model↔DB), ADR-MODELS-002 (se existir: observability/exit codes)

## Contexto

O projeto HB Track usa PostgreSQL como fonte estrutural real. Foi definido um gate binário (guard → parity → requirements) com SSOT canônico em `docs/_generated/schema.sql`.
Na prática, corrigir dezenas de tabelas “uma por uma” é lento e propenso a erro humano, além de gerar fricção com guard/baseline e artefatos gerados (`docs/_generated/*`).

A necessidade atual é: um **batch runner determinístico**, que:

* Faz **refresh SSOT 1x** (quando autorizado),
* Extrai automaticamente a lista de tabelas do SSOT,
* Roda **requirements** em lote para classificar (PASS / FAIL / SKIP_NO_MODEL),
* Executa o **gate apenas nas FAIL**, **uma por vez**, com **fail-fast** (parar no primeiro erro real),
* Mantém o repo limpo (ou documenta/restaura gerados corretamente),
* Gera logs e CSV auditáveis (e reproduzíveis).

## Decisão

Adotar o script `scripts/models_batch.ps1` como **orquestrador oficial** para varredura e correção de models, no padrão:

1. (Opcional) `inv.ps1 refresh` **uma vez** no início.
2. Extrair tabelas via regex do SSOT `docs/_generated/schema.sql`.
3. Rodar `model_requirements.py --profile <...>` para cada tabela.
4. Para tabelas com `exit=4` (requirements FAIL), executar `models_autogen_gate.ps1` (com perfil adequado, ex.: `fk` para ciclos).
5. Parar no primeiro erro (fail-fast) e exigir correção/commit/baseline conforme política.
6. Registrar execução em log e CSV.

## Tecnologia usada

* **PowerShell 5.1**: orquestração determinística no ambiente Windows.
* **SSOT via pg_dump**: `docs/_generated/schema.sql` gerado por `scripts/inv.ps1 refresh`.
* **Validação estrutural via análise estática**:

  * `scripts/model_requirements.py` (parser DDL + parser AST dos models Python).
* **Gate binário**:

  * Guard: `scripts/agent_guard.py` (baseline drift).
  * Parity: Alembic compare via `scripts/parity_gate.ps1` / `scripts/parity_scan.ps1`.
  * Requirements: `scripts/model_requirements.py`.

> Observação: este ADR trata do **batch runner** (orquestração). Ele não substitui o requirements; ele o padroniza no fluxo.

## Vantagem sobre o método antigo

### Antes (manual / ad-hoc)

* Execução por tabela (comandos soltos), sem padrão.
* Fácil “sujar” o repo com gerados e arquivos temporários.
* Guard/baseline frequentemente bloqueava por drift “invisível”.
* Difícil saber “o que falta” (não havia varredura completa com relatório).
* Alto custo de repetição: cada correção exigia recompor mentalmente o pipeline.

### Agora (models_batch.ps1)

* **Varredura completa** (visibilidade): PASS/FAIL/SKIP em CSV/log.
* **Determinismo**:

  * Refresh SSOT controlado 1x.
  * Gate aplicado somente em FAIL.
  * Fail-fast real no primeiro problema bloqueador.
* **Escopo controlado**:

  * Proíbe temporários no repo (via instruções) e trata `SKIP_NO_MODEL`.
* **Menos falso-positivo do guard**:

  * Repo limpo é pré-requisito.
  * Artefatos gerados têm rotina de restore (ou política documentada).
* **Auditoria/CI-ready**:

  * CSV + log dão trilha clara do que foi validado/corrigido.

> Comparação com “model_requirements.py anterior”: o ganho não é “trocar requirements”, e sim **evitar que o processo dependa de tentativa/erro humano**, criando um pipeline único, repetível e auditável.

## Padrão de implementação

### Padrões mandatórios no batch runner

* **CWD deve ser o backend root**.
* **Repo deve começar limpo** (`git status --porcelain` vazio).
* **Fail-fast ON por padrão** (parar no primeiro erro).
* **Não criar arquivos temporários no repo** (logs no `%TEMP%`).
* **Não depender de texto de erro para SKIP_NO_MODEL**: usar `Test-Path` do model esperado.
* **Capturar `$LASTEXITCODE` imediatamente** (sem pipelines que alterem o valor).
* **Não commitar automaticamente**. O batch executa validações/correções; commit é ato explícito.

### Exemplo de pattern correto (captura de exit code sem “pular”)

```powershell
$out = & ".\venv\Scripts\python.exe" scripts\model_requirements.py --table $t --profile $profile 2>&1
$ec = $LASTEXITCODE
$out | Add-Content -Path $logPath
return $ec
```

### Pattern correto para gate (sem Tee quebrar $LASTEXITCODE)

```powershell
$out = & ".\scripts\models_autogen_gate.ps1" -Table $t -Profile $profile -AllowCycleWarning 2>&1
$ec = $LASTEXITCODE
$out | Tee-Object -Append -FilePath $logPath | Out-Null
return $ec
```

### Handling canônico de “model não existe”

```powershell
$modelPath = Join-Path "app/models" "$t.py"
if (-not (Test-Path $modelPath)) {
  # registrar SKIP_NO_MODEL e continuar
}
```

## Semântica de exit codes

O batch deve respeitar a semântica canônica do gate:

* `0`: sucesso
* `1`: crash interno
* `2`: parity structural diffs
* `3`: guard violation (baseline drift)
* `4`: requirements violation

Para o batch runner, recomenda-se **código interno** para SKIP (ex.: `100`) para não conflitar com `2/3/4`.

## Cenários de teste

### A. Varredura (requirements-only)

1. **Tabela PASS**: model existe e requirements retorna `0`.
2. **Tabela FAIL**: requirements retorna `4` e vai para lista de correção.
3. **Tabela sem model**: não existe `app/models/<table>.py` → registrar `SKIP_NO_MODEL` e continuar.
4. **Crash do requirements**: requirements retorna `1` → batch deve abortar (fail-fast).

### B. Correção (gate)

5. **Gate passa após autogen**: tabela em FAIL vira PASS e segue para próxima.
6. **Gate falha em parity**: exit `2` deve abortar imediatamente.
7. **Gate falha em guard**: exit `3` deve abortar imediatamente (indica baseline desatualizada / drift).
8. **Gate falha em requirements**: exit `4` deve abortar imediatamente (autogen não resolveu ou model tem lógica extra).

### C. Tipos e estruturas (alvos do requirements)

9. Tipos complexos: `character varying(n)`, `numeric(p,s)`, `timestamp with/without time zone`, `uuid`, arrays (se houver).
10. Nullability explícita: `NOT NULL` ↔ `nullable=False`.
11. Defaults: literais vs funções, normalizações (best-effort).
12. FKs:

    * `ondelete`,
    * `use_alter=True` em ciclos (`teams`/`seasons` e quaisquer detectadas/documentadas).
13. Constraints:

    * CHECK,
    * UNIQUE,
    * INDEX (quando aplicável ao profile strict).

### D. Repo hygiene

14. Repo sujo no início: batch aborta com exit `3` e imprime `git status --porcelain`.
15. Batch não cria arquivos no repo: logs em `%TEMP%`, nenhum `??` no working tree.

## Consequências

### Positivas

* Reduz tempo de varredura e correção em massa.
* Torna o fluxo repetível, auditável e “fail-fast”.
* Minimiza regressões de guard por disciplina de baseline e repo limpo.

### Negativas / trade-offs

* Ainda existe fricção com artefatos gerados (`docs/_generated/*`) enquanto estiverem tracked.
* Não resolve automaticamente “tabelas sem model” (apenas classifica SKIP).
* Dependência do padrão de nome de arquivo (`<table>.py`) — se houver singular/plural irregular, precisa mapa de exceções.

## Plano de implementação

1. Consolidar `scripts/models_batch.ps1` com:

   * fail-fast correto (padrão ON),
   * SKIP_NO_MODEL via `Test-Path`,
   * código interno para SKIP (ex.: 100),
   * captura segura de exit code (sem pipeline),
   * logs e CSV em `%TEMP%`.
2. Atualizar `docs/_canon/05_MODELS_PIPELINE.md` para incluir:

   * quando usar batch,
   * como lidar com baseline/guard,
   * política de “não commitar gerados”.
3. (Opcional, PR separado) Definir política de versionamento para artefatos gerados para reduzir churn.

## Anexos

### Comandos canônicos

* Varredura rápida:

```powershell
.\scripts\models_batch.ps1 -SkipGate -SkipRefresh
```

* Execução completa (corrige FAIL uma por vez):

```powershell
.\scripts\models_batch.ps1 -SkipRefresh
```

### Critério de sucesso

* Batch consegue classificar todas as tabelas do SSOT.
* Para uma lista de FAILs conhecida, corrige progressivamente e para no primeiro erro real.
* Repo permanece limpo (exceto gerados, que são restaurados/ignorados conforme política).


