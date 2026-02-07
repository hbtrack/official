# CHECKLIST CANÔNICA — Integridade Model↔DB (SSOT: `schema.sql`) 

**Objetivo:** Garantir que **todo model SQLAlchemy reflete o DB real**, sem alucinações, com validação determinística e gate binário (PASS/FAIL), **dentro dos limites conhecidos de parsing**.

**Princípio fundamental:** `docs/_generated/schema.sql` é a **única fonte da verdade**. Nenhuma decisão estrutural vem de suposição ou "parece certo".

---

## 📋 FASE 0 — Fundação (pré-requisitos)

### 0.1 Princípios não-negociáveis

- [x] **SSOT estabelecido**: `docs/_generated/schema.sql` é gerado via `pg_dump` após cada migration
- [x] **Zero inventividade**: Agente não cria FK/coluna/check/index/relationship por suposição
- [x] **Gate binário**: Mudança só passa se `exit=0` em todos os gates
- [x] **Fail-fast com contexto**: Exit codes específicos para cada tipo de falha (guard=3, parity=2, requirements=4, internal=1)
- [x] **Limites de parsing reconhecidos**: Validação cobre declarações estáticas; construções dinâmicas (loops, metaprogramming) exigem perfil `lenient` ou exceção documentada

### 0.2 Infraestrutura base

- [x] `scripts/agent_guard.py` implementado (baseline + snapshot + check)
- [x] `.hb_guard/baseline.json` existe e está atualizado
- [x] `scripts/parity_gate.ps1` implementado (guard + parity structural)
- [x] `scripts/parity_classify.py` implementado (classifica diffs estruturais vs não-estruturais)
- [x] `docs/_generated/schema.sql` sincronizado com DB após última migration

---

## 📋 FASE 1 — Guardrails Estruturais (anti-desvio)

### 1.1 Agent Guard (baseline + allowlist)

- [x] `agent_guard.py snapshot` executado após qualquer alteração aprovada
- [x] Exclusões configuradas: `venv`, `.venv`, `__pycache__`, `*.pyc`, `.pytest_cache`, `docs/_generated`, `.git`, `.hb_guard`
- [x] `agent_guard.py check` com flags obrigatórias:
  - [x] `--forbid-new` (bloqueia arquivos novos fora da allowlist)
  - [x] `--forbid-delete` (bloqueia deleções fora da allowlist)
  - [x] `--allow` especifica exatamente quais arquivos podem mudar
  - [x] `--assert-skip-model-only-empty` em `db/alembic/env.py` (protege configuração crítica)
- [x] Exit code: **3** quando viola baseline/allowlist

### 1.2 Parity Gate (validação estrutural)

- [x] `parity_gate.ps1` executa na ordem:
  1. [x] `agent_guard.py check` (verifica baseline)
  2. [x] `parity_scan.ps1 -FailOnStructuralDiffs` (verifica model↔DB)
  3. [x] Propaga exit code do step que falhou
- [x] `parity_classify.py` classifica diffs corretamente:
  - [x] `NOT NULL on column ...` → **structural** (crítico)
  - [x] `assuming SERIAL...` → **warning** (ruído, não bloqueia)
  - [x] `sa_warning` de ciclo FK → **warning** (não é structural, mas indica risco de tooling)
- [x] `summary.structural_count` é a métrica de decisão (deve ser 0)
- [x] Exit code: **2** quando há diffs estruturais, **3** quando guard falha

### 1.3 Tratamento de ciclos FK (política determinística escopada)

⚠️ **POLÍTICA CORRIGIDA**: SAWarning de ciclo **não é ignorado universalmente**

**Evidência da implementação atual:**
- [x] Ciclo FK conhecido documentado (`teams` ↔ `seasons`):
  - [x] `teams.season_id` → `seasons.id` (FK: `fk_teams_season_id`, ON DELETE RESTRICT)
  - [x] `seasons.team_id` → `teams.id` (FK: `fk_seasons_team_id`, ON DELETE RESTRICT)
  - [x] Ambos têm `use_alter=True` forçado no autogen
  - [x] Revalidação confirmou `gate_exit=0` após correções (SAWarning não apareceu nos scans finais)

**Política de gate determinística:**

- [ ] **Gate FAIL quando:**
  - [ ] `-Table teams` OU `-Table seasons` **E** SAWarning presente
    - [ ] **Exception:** `-AllowCycleWarning` presente (override explícito)
  - [ ] Scan global (sem `-TableFilter`) **E** SAWarning presente
    - [ ] **Exception:** `-AllowCycleWarning` presente (override global)
  - [ ] **Independentemente de `structural_count`** (warning persiste mesmo com count=0)

- [ ] **Gate WARN apenas (não bloqueia) quando:**
  - [ ] `-Table` fora do ciclo (não `teams` nem `seasons`) **E** SAWarning presente
  - [ ] Log: `[WARN] SAWarning detected but table outside known cycle - proceeding`

- [ ] **Override explícito (`-AllowCycleWarning`):**
  - [ ] Uso restrito a tabelas documentadas em ANEXO B.1
  - [ ] Requer justificativa em commit message: `"Cycle FK teams<->seasons (ANEXO B.1) - use_alter=True present"`
  - [ ] Requer aprovação em code review
  - [ ] Gate valida que `use_alter=True` está presente nas FKs relevantes

- [ ] **Tooling health risk mitigado:**
  - [ ] SAWarning indica que Alembic compare pode não detectar mudanças em FKs do ciclo
  - [ ] `model_requirements.py` (FASE 2) valida FKs independentemente (não depende de Alembic)
  - [ ] Testes de integração obrigatórios para `teams` e `seasons`

- [ ] **Tabelas especiais ignoradas:** `alembic_version`, stub tables em `SKIP_STUB_ONLY_TABLES`

---

## 📋 FASE 2 — Validação de Estrutura (detecção de alucinações)

### 2.1 `model_requirements.py` — Validação Canônica **OBRIGATÓRIA**

⚠️ **STATUS**: Fase em implementação — checklist atualizada para refletir estado real

**Objetivo:** Validar que model Python reflete exatamente o schema.sql, sem depender de Alembic compare.

#### 2.1.1 Parser completo de `schema.sql` (DDL → estrutura)

- [ ] `_parse_columns()` extrai:
  - [ ] Nome da coluna
  - [ ] Tipo PostgreSQL (ex: `character varying(100)`, `DATE`, `INTEGER`)
  - [ ] Nullable (`NOT NULL` presente ou ausente)
  - [ ] Default value (quando relevante)
  - [ ] Primary Key (identificado em `PRIMARY KEY (...)`)

- [ ] `_parse_fks()` extrai (já implementado):
  - [ ] Nome da FK
  - [ ] Colunas locais
  - [ ] Tabela/colunas referenciadas
  - [ ] `ON DELETE` action
  - [ ] `ON UPDATE` action (se presente)

- [ ] `_parse_checks()` extrai nomes de CHECK constraints

- [ ] `_parse_indexes()` extrai indexes explícitos (prefixos `idx_`, `ix_`)

- [ ] `_parse_unique_constraints()` extrai UNIQUE constraints separados de indexes

#### 2.1.2 Parser AST do model Python (arquivo → estrutura)

⚠️ **LIMITES DE PARSING DECLARADOS EXPLICITAMENTE**

- [ ] `_parse_model_columns()` extrai via AST:
  - [ ] **Padrões suportados:**
    ```python
    # Padrão 1: Mapped + mapped_column (moderno)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Padrão 2: Column direto (legacy)
    name = Column(String(200), nullable=False)
    
    # Padrão 3: sa.Column (import aliasado)
    name = sa.Column(sa.String(200), nullable=False)
    ```
  
  - [ ] **Padrões NÃO suportados (requerem `lenient`):**
    ```python
    # Metaprogramming dinâmico
    for col_name in dynamic_list:
        setattr(cls, col_name, Column(String))
    
    # Geração via __init_subclass__
    # Mixins que adicionam colunas via metaclass
    ```

- [ ] `_parse_model_constraints()` extrai via AST:
  - [ ] `__table_args__` estático (tupla/lista de constraints)
  - [ ] `ForeignKey(...)` dentro de `Column()` ou `mapped_column()`
  - [ ] `CheckConstraint(...)`, `Index(...)`, `UniqueConstraint(...)`

- [ ] **Limite explícito documentado:**
  - [ ] Validação cobre **declarações estáticas no arquivo `.py`**
  - [ ] Construções dinâmicas (loops, decorators que modificam classe, imports condicionais) **não são detectadas**
  - [ ] Models com metaprogramming devem:
    - [ ] Usar perfil `lenient` (aceita diferenças documentadas), OU
    - [ ] Adicionar exceção explícita em `.hb_guard/model_requirements_exceptions.json`

#### 2.1.3 Validações obrigatórias — Perfil `strict` (padrão)

**A. Colunas (crítico — GAP #1 eliminado)**

- [ ] `_validate_columns_exact_match()`:
  - [ ] Extrai **todas** as colunas do model via AST (parsing completo do arquivo)
  - [ ] Compara com **todas** as colunas do `schema.sql`
  - [ ] Detecta **colunas extras** no model:
    ```python
    # Violation: EXTRA_COLUMN: nickname (exists in model line 42, not in schema.sql)
    ```
  - [ ] Detecta **colunas faltantes** no model:
    ```python
    # Violation: MISSING_COLUMN: legacy_id (exists in schema.sql, missing in model)
    ```
  - [ ] **NÃO ignora** blocos `HB-AUTOGEN-COLUMNS` — valida resultado final do arquivo
  - [ ] Ignora colunas em seções marcadas `# LENIENT: dynamic columns` (perfil lenient)

**B. Tipos (crítico — GAP #2 eliminado)**

- [ ] `_validate_column_types()`:
  - [ ] Mapeamento correto PostgreSQL → SQLAlchemy (ver ANEXO A)
  - [ ] Detecta tipo incompatível:
    ```python
    # Violation: TYPE_MISMATCH: birth_date expected=Date (from DATE) got=DateTime (model line 45)
    ```
  - [ ] Aceita equivalências documentadas (ANEXO A: `ACCEPTABLE_EQUIVALENCES`)
  - [ ] Rejeita equivalências perigosas (ANEXO A: `REJECTED_EQUIVALENCES`)

**C. Nullable (crítico — GAP #2.1 eliminado)**

- [ ] `_validate_nullability()`:
  - [ ] DB `NOT NULL` → model deve ter `nullable=False` explícito
  - [ ] DB nullable → model deve ter `nullable=True` explícito
  - [ ] Primary Keys ignoradas (implicitamente NOT NULL)
  - [ ] Detecta mismatch:
    ```python
    # Violation: NULLABLE_MISMATCH: email expected=NOT NULL got=nullable=True (model line 48)
    # Violation: NULLABLE_MISMATCH: phone expected=nullable got=missing/implicit False (model line 51)
    ```

**D. Foreign Keys (já implementado)**

- [ ] `_fk_present()` valida:
  - [ ] Nome exato da FK (ex: `fk_teams_season_id`)
  - [ ] Referência correta (`ref_table.ref_column`)
  - [ ] `ondelete` correto (RESTRICT, CASCADE, SET NULL, etc.)
  - [ ] `use_alter=True` aceito (requerido para ciclos)
  - [ ] Detecta FKs extras:
    ```python
    # Violation: EXTRA_FK_NAME: fk_teams_season_id_invented (model line 55, not in schema.sql)
    ```

**E-H. CHECK constraints, Indexes, Unique Constraints, Server Defaults**

- [ ] Validações análogas às anteriores (já descritas na versão anterior)
- [ ] Exit code **4** quando qualquer violação detectada

#### 2.1.4 Perfis de validação

- [ ] **Perfil `fk`** (mínimo): apenas FKs
- [ ] **Perfil `strict`** (padrão): colunas + tipos + nullable + FKs + constraints
- [ ] **Perfil `lenient`** (opt-in): aceita diferenças documentadas em comments/config

#### 2.1.5 Integração com gate

- [ ] `model_requirements.py` é **step obrigatório** no `models_autogen_gate.ps1` STEP 4
- [ ] Exit code específico: **4** (requirements violations)
- [ ] Output estruturado com números de linha do model

---

## 📋 FASE 3 — Autogeração de Models (SSOT → código)

### 3.1 `autogen_model_from_db.py` — Gerador Canônico

*(Já implementado conforme evidências — mantém descrição anterior)*

- [x] Flag `--create`: cria skeleton com blocos `HB-AUTOGEN-*`
- [x] Gera colunas/tipos/nullable corretos
- [x] Corrige duplicação UniqueConstraint vs Index
- [x] `use_alter=True` forçado para ciclos FK (`fk_teams_season_id`, `fk_seasons_team_id`)
- [x] Tipos String/VARCHAR/CHAR sem fallback fixo (usa length refletido)
- [x] `ondelete` priorizado do SSOT por constraint_name

---

## 📋 FASE 4 — Gate Unificado (orquestração)

### 4.1 `models_autogen_gate.ps1` — Comando Oficial

#### 4.1.1 Flags e parâmetros

- [x] `-Table <nome>` (obrigatório)
- [x] `-Create` (opcional)
- [x] `-Allow <paths>` (opcional)
- [x] `-Profile <fk|strict>` (padrão: `strict`)
- [x] `-DbUrl <url>` (opcional)
- [ ] `-AllowCycleWarning` (opcional - a implementar)

#### 4.1.2 Fluxo de execução (ordem obrigatória)

**STEP 1: Pré-validação (apenas se NÃO `-Create`)**

- [x] Executa `parity_gate.ps1 -Table $Table -Allow $Allow`
- [x] **Se falha por guard (exit=3)**: ABORT imediatamente
- [x] **Se falha por parity estrutural (exit=2)**: WARN e continua
- [x] **Se `-Create`**: SKIP este step

**STEP 2: Autogeração**

- [x] Resolve `DATABASE_URL_SYNC`
- [x] Executa `autogen_model_from_db.py` (com/sem `--create`)
- [x] Se `exit!=0` → ABORT

**STEP 3: Validação estrutural pós-autogen (parity)**

- [x] Executa `parity_gate.ps1 -Table $Table -Allow $Allow`
- [ ] **Política de ciclo aplicada (A IMPLEMENTAR):**
  ```powershell
  $isCycleTable = $Table -in @("teams", "seasons")
  $hasSAWarning = # check parity_report.warnings
  
  if ($isCycleTable -and $hasSAWarning -and -not $AllowCycleWarning) {
      Write-Host "[FAIL] Cycle FK detected in $Table - use -AllowCycleWarning with justification" -ForegroundColor Red
      exit 2
  }
  
  if (-not $isCycleTable -and $hasSAWarning) {
      Write-Host "[WARN] SAWarning detected but table outside known cycle - proceeding" -ForegroundColor Yellow
  }
  ```
- [x] Propaga exit code do parity_gate

**STEP 4: Validação de requisitos (model_requirements.py)**

- [ ] **A IMPLEMENTAR:**
  ```powershell
  & $py scripts\model_requirements.py --table $Table --profile $Profile
  $requirementsExit = $LASTEXITCODE
  
  if ($requirementsExit -ne 0) {
      Write-Host "[FAIL] Model requirements validation failed (exit=$requirementsExit)" -ForegroundColor Red
      Write-Host "See violations listed above" -ForegroundColor Red
      exit $requirementsExit  # Propaga exit code 4
  }
  ```

**STEP 5: Atualização de baseline**

- [x] Condição: `$Create -and $LASTEXITCODE -eq 0`
- [x] Executa `agent_guard.py snapshot`

**STEP 6: Propagação de exit code (CRÍTICO)**

⚠️ **CORREÇÃO OBRIGATÓRIA**: Script atual "achata" exit codes para 1

- [ ] **Implementar propagação real:**
  ```powershell
  # Variável de tracking em cada step
  $exitCode = 0
  
  try {
      # STEP 1
      if (-not $Create) {
          & .\scripts\parity_gate.ps1 -Table $Table -Allow $Allow
          $exitCode = $LASTEXITCODE
          if ($exitCode -eq 3) { 
              throw "guard_failed" 
          } elseif ($exitCode -eq 2) {
              Write-Host "[WARN] Pre-check found structural diffs - attempting autogen fix" -ForegroundColor Yellow
              $exitCode = 0  # Reset para continuar
          }
      }
      
      # STEP 2
      $autogenArgs = @("scripts\autogen_model_from_db.py", "--table", $Table)
      if ($Create) { $autogenArgs += "--create" }
      & $py @autogenArgs
      $exitCode = $LASTEXITCODE
      if ($exitCode -ne 0) { throw "autogen_failed" }
      
      # STEP 3
      & .\scripts\parity_gate.ps1 -Table $Table -Allow $Allow
      $exitCode = $LASTEXITCODE
      
      # Aplicar política de ciclo (quando implementado)
      # ...
      
      if ($exitCode -ne 0) { throw "parity_failed" }
      
      # STEP 4 (quando implementado)
      & $py scripts\model_requirements.py --table $Table --profile $Profile
      $exitCode = $LASTEXITCODE
      if ($exitCode -ne 0) { throw "requirements_failed" }
      
      # STEP 5
      if ($Create -and $exitCode -eq 0) {
          & $py scripts\agent_guard.py snapshot # ...
      }
      
  } catch {
      # Preserve exit code específico, não achata para 1
      if ($exitCode -eq 0) { $exitCode = 1 }  # Apenas se erro inesperado
      
      $reason = switch ($exitCode) {
          2 { "parity structural diffs" }
          3 { "guard baseline/allowlist violation" }
          4 { "model requirements validation" }
          default { "internal error: $_" }
      }
      Write-Host "[FAIL] Gate failed due to: $reason (exit=$exitCode)" -ForegroundColor Red
      
  } finally {
      exit $exitCode  # CRÍTICO: propaga exit code real
  }
  ```

---

## 📋 FASE 5-8 — Workflows, Critérios, Anexos

*(Mantém conteúdo das versões anteriores, com ajustes nos comandos de debug)*

### Ajuste em FASE 8.2 — Debug quando gate falha

**Correção do filtro de parity_report.json:**

```powershell
# ❌ ERRADO (campo não existe):
Where-Object { $_.category -eq "structural" }

# ✅ CORRETO:
Where-Object { $_.is_structural -eq $true }

# Comando completo corrigido:
Get-Content "docs\_generated\parity_report.json" | ConvertFrom-Json | 
    Select-Object -ExpandProperty items | 
    Where-Object { $_.table -eq "<table>" -and $_.is_structural -eq $true }
```

---

## 📋 ANEXO A — Mapeamento Canônico PG → SQLAlchemy

*(Mantém mapeamento completo da versão anterior)*

**Adição: Política de tamanhos:**

```python
# String/VARCHAR sem tamanho no schema.sql
"character varying" (sem (N)) → String  # SEM fallback de 255

# String/VARCHAR com tamanho
"character varying(100)" → String(100)  # length refletido exato

# CHAR sempre com tamanho (não tem sem tamanho em PG)
"char(10)" → CHAR(10)
```

---

## 📋 ANEXO B — Casos Edge Documentados

### B.1 Ciclo FK (teams ↔ seasons)

**Estrutura real validada (estado atual):**

```sql
-- Schema.sql (SSOT)
ALTER TABLE ONLY public.teams 
    ADD CONSTRAINT fk_teams_season_id 
    FOREIGN KEY (season_id) 
    REFERENCES public.seasons(id) 
    ON DELETE RESTRICT;

ALTER TABLE ONLY public.seasons 
    ADD CONSTRAINT fk_seasons_team_id 
    FOREIGN KEY (team_id) 
    REFERENCES public.teams(id) 
    ON DELETE RESTRICT;
```

**Implementação validada nos models:**

```python
# app/models/team.py (estado atual)
class Team(Base):
    __tablename__ = "teams"
    
    # HB-AUTOGEN-COLUMNS-START
    season_id = Column(
        Integer, 
        ForeignKey("seasons.id", name="fk_teams_season_id", use_alter=True),
        nullable=True
    )
    # HB-AUTOGEN-COLUMNS-END

# app/models/season.py (estado atual)
class Season(Base):
    __tablename__ = "seasons"
    
    # HB-AUTOGEN-COLUMNS-START
    team_id = Column(
        Integer,
        ForeignKey("teams.id", name="fk_seasons_team_id", use_alter=True),
        nullable=True
    )
    # HB-AUTOGEN-COLUMNS-END
```

**Status de validação (evidência 2026-02-07):**

- [x] `use_alter=True` forçado no autogen para ambas as FKs
- [x] Gate validado: `teams_gate_exit=0`, `seasons_gate_exit=0`
- [x] `summary.structural_count=0` em ambos
- [x] `warnings_count=0` nos scans finais (SAWarning não apareceu)

**Política de gate quando implementar `-AllowCycleWarning`:**

```powershell
# Validar com override explícito (quando necessário)
.\scripts\models_autogen_gate.ps1 -Table "teams" -AllowCycleWarning
.\scripts\models_autogen_gate.ps1 -Table "seasons" -AllowCycleWarning

# Commit message obrigatório:
# "Cycle FK teams<->seasons (ANEXO B.1) - use_alter=True present"
```

---

## ✅ CONCLUSÃO

### Garantias Fornecidas (com limites declarados)

**Um model que passa Guard + Parity + Requirements (strict) é considerado estruturalmente conforme ao SSOT para:**

- ✅ **Colunas** (nome, existência) — dentro dos limites de parsing AST estático
- ✅ **Tipos** (mapeamento PG→SA) — conforme ANEXO A
- ✅ **Nullable** (NOT NULL vs nullable) — sempre explícito
- ✅ **FKs** (nome, ref, ondelete, use_alter) — validado independente de Alembic
- ✅ **Constraints** (CHECKs, Indexes, Unique) — nomes e estrutura
- ✅ **Server defaults** (literais) — exceto funções (now(), gen_random_uuid())

**Limites conhecidos e aceitos:**

- ⚠️ **Metaprogramming dinâmico** no model → requer perfil `lenient` ou exceção
- ⚠️ **Relationships** → manuais até FASE 7 (developer responsável)
- ⚠️ **Defaults de funções** → opcionais (não bloqueiam)
- ⚠️ **Ciclos FK** → requerem `-AllowCycleWarning` + documentação

### Próximos passos imediatos (implementação)

**FASE 2 — `model_requirements.py` (CRÍTICO):**

1. [ ] Implementar parser AST de models (colunas, tipos, nullable)
2. [ ] Implementar validações A-C (colunas exatas, tipos, nullable)
3. [ ] Testar em `attendance` (smoke test)
4. [ ] Exit code 4 para violations

**FASE 4 — Gate propagation (CRÍTICO):**

1. [ ] Corrigir `models_autogen_gate.ps1` para propagar exit codes reais (não achatar)
2. [ ] Implementar política de ciclo com `-AllowCycleWarning`
3. [ ] Integrar STEP 4 (model_requirements.py)

**Validação final:**

1. [ ] Smoke test: `.\scripts\models_autogen_gate.ps1 -Table "attendance"`
2. [ ] Validar exit codes: forçar falhas de guard (3), parity (2), requirements (4)
3. [ ] Validar ciclo: rodar `teams`/`seasons` com/sem `-AllowCycleWarning`

---


## Conclusão


Abaixo vai a versão **operacional (roteiro único)**, pensada pra você colar no canônico e executar **um comando por vez** (sem travar PowerShell). Tudo parte do princípio: **SSOT = `docs/_generated/schema.sql`** e **“pronto” = gate PASS (exit 0)**.

---

## Roteiro Operacional Único — Model↔DB (SSOT)

### BLOCO 0 — Entrar no root do backend (sempre)

```powershell
cd "C:\HB TRACK\Hb Track - Backend"
pwd
```

### BLOCO 1 — (Opcional) Backup local sem Git (antes de mexer em model)

Use quando você vai rodar `-Create` ou atualizar um model importante.

```powershell
New-Item -ItemType Directory -Force .hb_backups | Out-Null
Copy-Item "app\models\<TABLE>.py" ".hb_backups\<TABLE>_$(Get-Date -Format 'yyyyMMdd_HHmmss').py" -ErrorAction SilentlyContinue
```

---

# CENÁRIO A — Tabela já tem model: “atualizar/alinha e validar”

**Comando único oficial (gera/patch + valida):**

```powershell
.\scripts\models_autogen_gate.ps1 -Table "<TABLE>"
echo "gate_exit=$LASTEXITCODE"
```

**Pronto quando:**

* `gate_exit=0`

**Se falhar (gate_exit != 0), debug mínimo:**

```powershell
Get-Content "docs\_generated\parity_report.json" -Raw | Select-Object -First 80
```

(Se precisar filtrar só a tabela, rode direto o parity scan dela:)

```powershell
.\scripts\parity_scan.ps1 -TableFilter "<TABLE>" -FailOnStructuralDiffs
echo "parity_exit=$LASTEXITCODE"
```

---

# CENÁRIO B — Tabela existe no DB, mas NÃO tem model ainda: “criar model do zero”

**Comando único oficial (cria + valida + snapshot baseline ao final):**

```powershell
.\scripts\models_autogen_gate.ps1 -Table "<TABLE>" -Create
echo "gate_exit=$LASTEXITCODE"
```

**Pronto quando:**

* `gate_exit=0`
* e o arquivo aparece em `app\models\<TABLE>.py`

**Se falhar:** mesmo debug do Cenário A (`parity_report.json`).

---

# CENÁRIO C — Tabela nova (migração → DB → schema.sql → model)

**Comando único do workflow (orquestrador):**

```powershell
.\scripts\new_table_workflow.ps1 -Table "<TABLE>" -MigrationMessage "add <TABLE>"
echo "workflow_exit=$LASTEXITCODE"
```

**Pronto quando:**

* `workflow_exit=0`
* e `.\scripts\models_autogen_gate.ps1 -Table "<TABLE>"` também retorna `gate_exit=0` (sanity final)

---

## Evidência mínima pra você colar aqui (quando der FAIL)

Quando algum comando retornar exit != 0, cole sempre:

1. `pwd`
2. comando exato
3. output completo (stdout/stderr) + `gate_exit/parity_exit`
4. `docs/_generated/parity_report.json` (ou pelo menos `summary` + primeiros itens)

---

## Regras práticas (pra não reintroduzir problema)

* **Não editar estrutura manualmente** (coluna/tipo/nullable/FK/check/index) fora do autogen — se precisar, ajuste o autogen, rode o gate de novo.
* **Um comando por bloco** (como acima). Se travar: pare, rode só o próximo bloco após voltar o prompt.
* **“Model pronto” = gate 0**. Qualquer “parece certo” sem gate é hipótese.

---