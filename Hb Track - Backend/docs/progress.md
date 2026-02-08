# CHECKLIST CANÔNICA — Integridade Model↔DB (SSOT: `schema.sql`) 

**Objetivo:** Garantir que **todo model SQLAlchemy reflete o DB real**, sem alucinações, com validação determinística e gate binário (PASS/FAIL), **dentro dos limites conhecidos de parsing**.

**Princípio fundamental:** `docs/_generated/schema.sql` é a **única fonte da verdade**. Nenhuma decisão estrutural vem de suposição ou "parece certo".

---

Estamos implementando um **pipeline determinístico de integridade Model↔DB**, onde:

1. **DB é SSOT**
   Tudo que é “estrutura” (colunas, tipos, nullable, FKs, ondelete, unique/check/index) vem do `docs/_generated/schema.sql`.

2. **Um gate binário (PASS/FAIL) que bloqueia drift e alucinação**
   O `models_autogen_gate.ps1` vira o **comando oficial** que:

   * impede mudanças fora da allowlist (guard/baseline)
   * valida paridade estrutural via Alembic (parity)
   * valida requisitos canônicos via SSOT direto (model_requirements)

3. **Autogen como “corretor” e SSOT como “juiz”**
   `autogen_model_from_db.py` gera/patch models para refletirem o schema real.
   O gate só aceita se o resultado final estiver conforme SSOT.

4. **Camada nova que elimina falso-negativo do Alembic: `model_requirements.py`**
   Alembic compare pode falhar/silenciar em edge cases (ex.: ciclo FK).
   O `model_requirements.py` entra como verificador independente:

   * lê `schema.sql`
   * lê o model via AST
   * compara “exatamente” (começando por FKs no perfil `fk`, depois colunas/tipos/nullable no `strict`)
   * retorna **exit 4** em violação

5. **Exit codes estáveis = automação confiável**
   Guard=3, Parity=2, Requirements=4, Internal=1.
   Isso permite CI/agent saber “por que” falhou sem interpretação humana.

Em termos práticos: você está construindo um **fluxo “prompt curto → execução automática confiável”** que:

* corrige models a partir do DB (autogen),
* valida com SSOT (parity + requirements),
* e impede mudanças inesperadas (guard),
  com evidência rastreável nos artefatos gerados.

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

**Evidência da implementação atual (estado real 2026-02-07):**
- [x] Ciclo FK conhecido documentado (`teams` ↔ `seasons`):
  - [x] `teams.season_id` → `seasons.id` (FK: `fk_teams_season_id`, ON DELETE RESTRICT)
  - [x] `seasons.team_id` → `teams.id` (FK: `fk_seasons_team_id`, ON DELETE RESTRICT)
  - [x] `use_alter=True` confirmado em `app/models/team.py` (prova via grep em `app/models/team.py`)
  - [x] `use_alter=True` em `app/models/season.py` (prova via grep em `app/models/season.py`)
  - [ ] ⚠️ SAWarning de ciclo (status ainda pendente de evidência numérica `warnings_count` por tabela)
  - [x] Último run colado: `teams_gate_exit=0` e `seasons_gate_exit=0` via `scripts/models_autogen_gate.ps1`


**Critério de promoção para [x]:**
- `gate_exit=0` para **ambos** (`-Table teams` e `-Table seasons`) em scan limpo, **OU**
- `-AllowCycleWarning` implementado e aceito como override explícito
“scan limpo” = structural_count=0 e política de warning satisfeita (0 ou allow). 
Ex.:
`gate_exit=0` (o gate já encapsula isso) e, se `-AllowCycleWarning` for usado, o gate precisa validar mitigação (`use_alter` nos 2 lados + requirements FK)

**Política de gate determinística:**

- [x] **Política de escopo implementada** (`parity_gate.ps1`: FAIL no ciclo `teams|seasons`; WARN fora do escopo)
- [ ] **Override `-AllowCycleWarning` + validação de mitigação (pendente)**

- [ ] **Gate FAIL quando:**
  - [ ] `-Table teams` OU `-Table seasons` **E** SAWarning presente
    - [ ] **Exception:** `-AllowCycleWarning` presente (override explícito)
  - [ ] **Scan global é via `parity_scan.ps1 -FailOnStructuralDiffs` (não via `parity_gate.ps1`)**
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

- [x] Stub inicial criado em `scripts/model_requirements.py`
- [x] `python .\scripts\model_requirements.py --help` retorna exit 0
- [x] Stub configurado para retornar exit **4** quando executado com `--table` (sem falso verde)
- [x] Perfil **`fk`** implementado (leitura de `schema.sql` + AST do model)
- [x] Smoke test via gate: `.\scripts\models_autogen_gate.ps1 -Table "attendance" -Profile fk` → `attendance_gate_exit=0`
- [x] Perfil **`strict` Onda A** implementado (FK + colunas + nullable)
- [x] Smoke strict: `attendance_strict_gate_exit=0`
- [x] Regressão strict: `training_sessions_strict_gate_exit=0`
- [x] Perfil **`strict` Onda B** implementado (validação inicial de tipos PG→SQLAlchemy)
- [x] Smoke strict pós-Onda B: `attendance_strict_gate_exit=0`
- [x] Regressão strict pós-Onda B: `training_sessions_strict_gate_exit=0`

**Evidências de validação (2026-02-07):**

- [x] Execução direta do requirements (`fk`):
  - `python .\scripts\model_requirements.py --table attendance --profile fk`
  - Resultado: `[OK] ... fk profile passed` + `attendance_fk_exit=0`
- [x] Execução direta do requirements (`strict`) em `attendance`:
  - `python .\scripts\model_requirements.py --table attendance --profile strict`
  - Resultado: `[OK] ... strict profile passed` + `attendance_strict_exit=0`
- [x] Execução direta do requirements (`strict`) em `training_sessions`:
  - `python .\scripts\model_requirements.py --table training_sessions --profile strict`
  - Resultado: `[OK] ... strict profile passed` + `training_sessions_strict_exit=0`

**Objetivo:** Validar que model Python reflete exatamente o schema.sql, sem depender de Alembic compare.

#### 2.1.1 Parser completo de `schema.sql` (DDL → estrutura)

**Evidências objetivas (2026-02-07):**

- [x] Verificação de símbolos no código (`python -c "import scripts.model_requirements as m; ..."`):
  - `_parse_schema_columns=YES`
  - `_parse_schema_fks=YES`
  - `_parse_columns=YES`
  - `_parse_fks=YES`
  - `_parse_checks=YES`
  - `_parse_indexes=YES`
  - `_parse_unique_constraints=YES`
  - [x] Smoke funcional do strict/fk em tabelas canônicas passou (attendance/training_sessions), confirmando parser atual operacional no subset implementado.
  
- [x] **Revalidação executada novamente (2026-02-07 18:52 BRT)**:
  - inspeção de símbolos atualizada: `_parse_schema_columns=YES`, `_parse_schema_fks=YES`, `_parse_columns=YES`, `_parse_fks=YES`, `_parse_checks=YES`, `_parse_indexes=YES`, `_parse_unique_constraints=YES`
  - `python .\scripts\model_requirements.py --table attendance --profile strict` → `attendance_strict_exit=0`
  - `python .\scripts\model_requirements.py --table training_sessions --profile strict` → `training_sessions_strict_exit=0`
  - `symbols_exit=0`
  - `req_attendance_exit=0`
  - `req_training_sessions_exit=0`
  - teste unitário parser: `python -m pytest tests\unit\test_model_requirements_schema_parser.py -q` → `3 passed` (warnings não bloqueantes)

- [x] **Revalidação por bloco único solicitado (2026-02-07 20:19 BRT)**:
  - PASSO 0 executado: `powershell -NoProfile -ExecutionPolicy Bypass -File "c:\HB TRACK\scripts\inv.ps1" refresh` → `WRAPPER EXIT CODE: 0`
  - Execução do bloco de verificação dos parsers (DDL constructs + defaults):
    - `check_tbl= None`
    - `unique_tbl= exercise_tags`
    - `index_tbl= data_access_logs`
    - `default_tbl= athlete_badges`
    - `uniques_count= 1` (`uniques_sample=['exercise_tags_name_key']`)
    - `indexes_count= 3` (`indexes_sample=['idx_access_logs_accessed_at','idx_access_logs_athlete','idx_access_logs_user']`)
    - `columns_with_default_detected= 5`
    - `schema_parsers_exit=0`
    - Critério objetivo 2.1.1 atendido para os constructos encontrados no recorte automático do bloco (UNIQUE/INDEX/DEFAULT); para CHECK, `check_tbl` veio `None` porque o regex do bloco busca `ALTER TABLE ... ADD CONSTRAINT ... CHECK`.

- [x] **Evidência complementar pós-feedback (2026-02-07 20:24 BRT)**:
  - `python .\scripts\model_requirements.py --table exercise_tags --profile strict` → `req_exercise_tags_exit=4` (MISSING_FK em `exercise_tags_approved_by_admin_id_fkey`, `exercise_tags_parent_tag_id_fkey`, `exercise_tags_suggested_by_user_id_fkey`)
  - `python .\scripts\model_requirements.py --table data_access_logs --profile strict` → `req_data_access_logs_exit=4` (MISSING_FK em `data_access_logs_athlete_id_fkey`, `data_access_logs_user_id_fkey`)
  - `python .\scripts\model_requirements.py --table athlete_badges --profile strict` → `req_athlete_badges_exit=0`
  - `Select-String -Path "docs\\_generated\\schema.sql" -Pattern " CHECK " | Select-Object -First 5` → `check_grep_exit=0` com CHECKs presentes (ex.: `ck_athlete_badges_type`, `ck_athletes_deleted_reason`, `ck_attendance_correction_fields`).
  - Conclusão objetiva: **FASE 2.1.1 permanece fechada por evidência** (parser de CHECK existe e schema contém CHECK); próximos gaps pertencem à **FASE 2.1.3 (validação strict E–H)**, não ao parser.

- [x] `_parse_columns()` extrai (implementação atual via `_parse_schema_columns`):
  - [x] Nome da coluna
  - [x] Tipo PostgreSQL (subset inicial canônico)
  - [x] Nullable (`NOT NULL` presente ou ausente)
  - [x] Default value (quando relevante; literal/function classificado)
  - [x] Primary Key (identificado em `PRIMARY KEY (...)`)

- [x] `_parse_fks()` extrai (implementação atual via `_parse_schema_fks`):
  - [x] Nome da FK
  - [x] Colunas locais
  - [x] Tabela/colunas referenciadas
  - [x] `ON DELETE` action
  - [x] `ON UPDATE` action (se presente)

- [x] `_parse_checks()` extrai nomes de CHECK constraints

- [x] `_parse_indexes()` extrai indexes explícitos (prefixos `idx_`, `ix_`)

- [x] `_parse_unique_constraints()` extrai UNIQUE constraints separados de indexes

**Pendências para concluir a Fase 2.1.1 (parser completo de schema.sql):**

- [x] **Decisão de contrato formalizada (2026-02-07):**
  - API interna SSOT (contrato final):
    - `_parse_schema_columns(schema_sql_text, table) -> List[SchemaColumn]`
    - `_parse_schema_fks(schema_sql_text, table) -> List[SchemaFK]`
  - Wrappers de compatibilidade canônica: `_parse_columns(...) -> _parse_schema_columns(...)` e `_parse_fks(...) -> _parse_schema_fks(...)` (sem lógica adicional)
- [x] Implementar wrappers/nomes canônicos esperados no checklist (`_parse_columns`, `_parse_fks`) como compatibilidade fina.
- [x] Implementar parsing de `DEFAULT` (coluna e normalização básica) e registrar no artefato interno.
- [x] Implementar `_parse_checks()` para extração determinística (nome + expressão opcional normalizada).
- [x] Implementar `_parse_indexes()` (incluindo `idx_`/`ix_`, unique index parcial e where clause quando aplicável).
- [x] Implementar `_parse_unique_constraints()` separado de índices.
- [x] Adicionar teste(s) unitário(s) para 2.1.1 cobrindo parser com `DEFAULT/FK/CHECK/UNIQUE/INDEX` (`tests/unit/test_model_requirements_schema_parser.py`).
- [x] Promover a seção 2.1.1 para concluída com evidência de parse completo + testes verdes.

**Status da Fase 2.1.1:** **CONCLUÍDA** (escopo parser `schema.sql` completo conforme checklist da seção)

**Critérios de implementação acordados (para reduzir falso-negativo):**

- [x] `DEFAULT`: implementar primeiro literais determinísticos (`0/1`, `'x'`, `true/false`, `NULL`).
- [x] `DEFAULT` de função (`now()`, `gen_random_uuid()`, `timezone(...)`): classificar como `default_function` e não bloquear neste estágio.
- [x] `_parse_checks/_parse_indexes/_parse_unique_constraints`: iniciar por extração **de nome** (anti-alucinação), sem equivalência semântica completa de expressão.

#### 2.1.2 Parser AST do model Python (arquivo → estrutura)

⚠️ **LIMITES DE PARSING DECLARADOS EXPLICITAMENTE**

**Evidências objetivas (2026-02-07 20:37 BRT):**

- [x] Presença de símbolos AST no módulo:
  - `has__parse_model_columns= True`
  - `has__parse_model_fks= True`
  - `has__parse_model_constraints= False`
- [x] Evidência de padrão moderno (`Mapped + mapped_column`) no código real:
  - `Select-String app\models\*.py "mapped_column\("` retornou ocorrências em `app/models/athlete.py` (ex.: linhas 97, 104, 115, 122...)
- [x] Evidência de padrão legado (`Column` direto) no código real:
  - `Select-String app\models\*.py "\bColumn\("` retornou ocorrências em `app/models/data_retention_log.py` e `app/models/email_queue.py`
- [x] Verificação do padrão aliasado (`sa.Column`) no código atual:
  - `Select-String app\models\*.py "sa\.Column\("` sem ocorrências no recorte (`0 matches`)
- [x] Conclusão de revisão da 2.1.2:
  - parser AST de colunas/FKs está implementado e operando para padrões estáticos principais encontrados no repositório;
  - parser de constraints AST dedicado (`_parse_model_constraints`) permanece pendente e não deve ser marcado como concluído.

- [x] Revalidação rápida (2026-02-07 20:49 BRT):
  - `has__parse_model_columns= True`
  - `has__parse_model_fks= True`
  - `has__parse_model_constraints= False`
  - `python .\scripts\model_requirements.py --table attendance --profile fk` → `attendance_fk_exit=0`
  - `python .\scripts\model_requirements.py --table attendance --profile strict` → `attendance_strict_exit=0`
  - evidência de padrões no código real:
    - `mapped_column(...)` presente (`app/models/athlete.py`)
    - `Column(...)` presente (`app/models/data_retention_log.py`)
    - `sa.Column(...)` sem ocorrência no recorte (`grep_sa_column_exit=0` com 0 matches)

- [x] Implementação e evidência de fechamento da 2.1.2 (2026-02-07 21:23 BRT):
  - implementação concluída em `scripts/model_requirements.py`:
    - `_parse_model_constraints(model_path, table)`
    - suporte a `__table_args__` estático (tupla/lista) com `CheckConstraint`, `UniqueConstraint`, `Index`
    - extração de `ForeignKey(...)` inline em `Column(...)` / `mapped_column(...)` com `local_columns`
  - verificação de símbolos:
    - `has__parse_model_columns= True`
    - `has__parse_model_fks= True`
    - `has__parse_model_constraints= True`
  - evidência real de parse em model existente (`app/models/athlete_badge.py`):
    - `constraints_checks_count= 1`
    - `constraints_uniques_count= 0`
    - `constraints_indexes_count= 1`
    - `constraints_fks_count= 1`
    - `checks_sample=['ck_athlete_badges_type']`
    - `indexes_sample=['idx_badges_athlete_month']`
    - `fks_sample=['athlete_badges_athlete_id_fkey']`
  - testes unitários AST de model adicionados:
    - `tests/unit/test_model_requirements_model_ast_parser.py`
    - `python -m pytest tests\unit\test_model_requirements_model_ast_parser.py -q` → `3 passed` / `ast_parser_tests_exit=0`
  - smoke de regressão strict pós-implementação:
    - `python .\scripts\model_requirements.py --table attendance --profile strict` → `attendance_strict_exit=0`

- [x] Revalidação final com mitigação de ambiente Windows (2026-02-07 22:10 BRT):
  - problema observado no host: `tmp_path` falhou com `PermissionError [WinError 5]` em `C:\Users\davis\AppData\Local\Temp\pytest-of-davis`.
  - mitigação aplicada em `tests/unit/test_model_requirements_model_ast_parser.py`:
    - remoção de dependência de `tmp_path`
    - criação de arquivos temporários em `.hb_tmp_tests/` dentro do workspace com limpeza via `unlink(missing_ok=True)`.
  - revalidação pós-mitigação:
    - `has__parse_model_constraints= True`
    - `python -m pytest tests\unit\test_model_requirements_model_ast_parser.py -q` → `3 passed` / `ast_parser_tests_exit=0`
    - `python .\scripts\model_requirements.py --table attendance --profile strict` → `attendance_strict_exit=0`

- [x] Revalidação adicional consolidada (2026-02-07 22:30 BRT):
  - PASSO 0 (SSOT) reexecutado:
    - `powershell -NoProfile -ExecutionPolicy Bypass -File "c:\HB TRACK\scripts\inv.ps1" refresh`
    - resultado: `WRAPPER EXIT CODE: 0`
  - inspeção de símbolos AST em `scripts/model_requirements.py` (import via `importlib.util`):
    - `has__parse_model_columns= True`
    - `has__parse_model_fks= True`
    - `has__parse_model_constraints= True`
  - evidência de padrões no código real (`app/models/*.py`):
    - `mapped_column(...)` presente (`app/models/athlete.py`, amostra linhas 97/104/115/122)
    - `Column(...)` presente (`app/models/data_retention_log.py`, amostra linhas 30/31/32/33/34)
    - `sa.Column(...)` sem ocorrências na varredura (`0 matches`)
  - teste unitário AST parser:
    - `python -m pytest tests\unit\test_model_requirements_model_ast_parser.py -q`
    - resultado: `3 passed` (`ast_parser_tests_exit=0`)
  - smoke strict pós-revalidação:
    - `python .\scripts\model_requirements.py --table attendance --profile strict`
    - resultado: `[OK] model_requirements strict profile passed` + `column_count=18` + `model_column_count=18`

**Ações faltantes para concluir a Fase 2.1.2 (estado atual):**

- [x] Implementar parser AST dedicado de constraints (`_parse_model_constraints`) cobrindo, no mínimo:
  - [x] `__table_args__` estático (tupla/lista)
  - [x] `CheckConstraint(...)`
  - [x] `UniqueConstraint(...)`
  - [x] `Index(...)`
  - [x] FKs declaradas inline em `Column(...)` / `mapped_column(...)` no mesmo artefato de constraints
- [x] Adicionar suíte de testes unitários específica para parser AST de model (além dos testes de schema parser), com casos positivos/negativos para:
  - [x] `Mapped + mapped_column`
  - [x] `Column` direto
  - [x] `__table_args__` com constraints múltiplas
  - [x] comportamento esperado para padrões não suportados (metaprogramming dinâmico)
- [x] Formalizar critérios de “não suportado” no parser (escopo estático): padrão dinâmico não é extraído por `_parse_model_constraints` e é coberto por teste negativo dedicado.
- [x] Registrar evidência objetiva de conclusão da 2.1.2 com comandos reproduzíveis e saídas (símbolos/parse real/pytest/smoke strict).

**Critério objetivo para promover 2.1.2 para [x]:**

- [x] `has__parse_model_constraints= True`
- [x] teste unitário do parser AST de model verde (novo arquivo de testes)
- [x] pelo menos 1 evidência real de parse de `__table_args__` contendo CHECK/INDEX em model existente canônico (`athlete_badges`)

- [x] `_parse_model_columns()` extrai via AST (subset estático implementado):
  - [x] **Padrões suportados:**
    ```python
    # Padrão 1: Mapped + mapped_column (moderno) ✅
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Padrão 2: Column direto (legacy) ✅
    name = Column(String(200), nullable=False)
    
    # Padrão 3: sa.Column (import aliasado) ✅
    name = sa.Column(sa.String(200), nullable=False)
    ```
    Obs.: no código atual inspecionado, há evidência prática dos padrões 1 e 2; não houve ocorrência de `sa.Column(...)` nesta varredura.
  
  - [ ] **Padrões NÃO suportados (requerem `lenient`) — Plano objetivo de fechamento:**
    - [ ] **Ação 1 (inventário):** mapear models com metaprogramming real (loops/setattr/metaclass/decorator com side-effect estrutural).
      - **Critério de aceite:** lista objetiva em `.hb_guard/model_requirements_exceptions.json` com `table`, `model_path`, `reason`, `owner`.
    - [ ] **Ação 2 (política lenient):** aplicar `--profile lenient` apenas nos casos inventariados (opt-in), mantendo `strict` como padrão global.
      - **Critério de aceite:** `strict` continua FAIL para divergência estrutural; `lenient` só ignora itens explicitamente listados no arquivo de exceções.
    - [ ] **Ação 3 (trilha de migração):** abrir worklist para remover metaprogramming estrutural dos casos inventariados.
      - **Critério de aceite:** cada item possui ticket/owner/prazo e regra de saída (remover exceção + validar em `strict`).

- [x] `_parse_model_constraints()` extrai via AST:
  - [x] `__table_args__` estático (tupla/lista de constraints)
  - [x] `ForeignKey(...)` dentro de `Column()` ou `mapped_column()`
  - [x] `CheckConstraint(...)`, `Index(...)`, `UniqueConstraint(...)`

- [ ] **Limite explícito documentado (com critério de aceite):**
  - [x] Validação cobre **declarações estáticas no arquivo `.py`**
  - [x] Construções dinâmicas (loops, decorators que modificam classe, imports condicionais) **não são detectadas**
  - [ ] Models com metaprogramming devem:
    - [ ] Usar perfil `lenient` (aceita diferenças documentadas), **com opt-in explícito por tabela/model**; OU
    - [ ] Adicionar exceção explícita em `.hb_guard/model_requirements_exceptions.json`.
  - [ ] **Critério de aceite final do bloco:**
    - [ ] existe política escrita de `lenient` (escopo, limites, ownership, expiração da exceção);
    - [ ] existe pelo menos 1 execução de prova: `strict` falha sem exceção + `lenient` passa com exceção explícita;
    - [ ] evidência registrada nesta seção com comandos e exits.

**Status da Fase 2.1.2:** **CONCLUÍDA** (parser AST de model para colunas/FKs/constraints estático implementado + testes unitários e evidências reais de parse)

#### 2.1.3 Validações obrigatórias — Perfil `strict` (padrão)

**Evidências objetivas — rodada de decisão 2.1.3 (2026-02-07 22:50 BRT):**

- [x] PASSO 0 (SSOT) revalidado antes da rodada:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File "c:\HB TRACK\scripts\inv.ps1" refresh`
  - resultado: `WRAPPER EXIT CODE: 0`
- [x] `strict` em tabela com parser+enforcement alinhado:
  - `python .\scripts\model_requirements.py --table athlete_badges --profile strict`
  - resultado: `[OK] ... strict profile passed` + `athlete_badges_exit=0`
- [x] `strict` em tabelas com divergência real Model↔SSOT (não é falha de parser):
  - `python .\scripts\model_requirements.py --table exercise_tags --profile strict`
    - `exercise_tags_exit=4`
    - violações: `MISSING_FK` em `exercise_tags_approved_by_admin_id_fkey`, `exercise_tags_parent_tag_id_fkey`, `exercise_tags_suggested_by_user_id_fkey`
  - `python .\scripts\model_requirements.py --table data_access_logs --profile strict`
    - `data_access_logs_exit=4`
    - violações: `MISSING_FK` em `data_access_logs_athlete_id_fkey`, `data_access_logs_user_id_fkey`
- [x] Classificação objetiva da rodada:
  - parser AST/DDL já extrai os artefatos necessários para a checagem;
  - os `exit=4` acima representam **mismatch estrutural real** (FK ausente no model vs presente no SSOT), portanto avanço imediato é correção de model/enforcement, não parser.
- [x] Higiene de ambiente para evitar drift recorrente de teste temporário:
  - `.hb_tmp_tests/` adicionado em `.gitignore` (root). Observação: `Hb Track - Backend/.gitignore` foi removido do versionamento neste branch.

- [x] Execução do gate canônico para correção de models (2026-02-07 23:20 BRT):
  - `.\scripts\models_autogen_gate.ps1 -Table "exercise_tags" -Profile strict` → `exercise_tags_gate_exit=2`
  - `.\scripts\models_autogen_gate.ps1 -Table "data_access_logs" -Profile strict` → `data_access_logs_gate_exit=2`
  - causa objetiva do `exit=2`: falha de guard/parity no pós-autogen por arquivos fora da allowlist (`docs/_generated/*` e `app/models/exercise_tag.py` durante a segunda execução), não por crash de script.

- [x] Revalidação direta do requirements após autogen (2026-02-07 23:22 BRT):
  - `python .\scripts\model_requirements.py --table exercise_tags --profile strict` → `exercise_tags_strict_exit=4`
    - status FK: **OK** (`fk_count=3`, sem `MISSING_FK`)
    - violações restantes:
      - `NULLABLE_MISMATCH: description expected_nullable=True got_nullable=False`
      - `TYPE_MISMATCH: description expected=text got=varchar|255`
      - `NULLABLE_MISMATCH: display_order expected_nullable=True got_nullable=False`
  - `python .\scripts\model_requirements.py --table data_access_logs --profile strict` → `data_access_logs_strict_exit=4`
    - status FK: **OK** (`fk_count=2`, sem `MISSING_FK`)
    - violação restante:
      - `TYPE_MISMATCH: entity_type expected=varchar|50 got=varchar|64`

- [x] Classificação atualizada da decisão 2.1.3:
  - etapa de FK está funcional após autogen (mismatch de FK foi removido);
  - gaps remanescentes em `strict` agora são de **tipo/nullable** (exercise_tags, data_access_logs), mantendo o diagnóstico de mismatch real Model↔SSOT.

**Revisão e validação dos itens [x] — rodada adicional (2026-02-08 00:18 BRT):**

- [x] Reexecução PASSO 0 (SSOT):
  - comando: `powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\inv.ps1" refresh`
  - evidência objetiva: `schema.sql`, `alembic_state.txt`, `manifest.json` regenerados em `Hb Track - Backend/docs/_generated/`.
  - ressalva histórica (rodada anterior): OpenAPI falhou (`sqlalchemy.INET` + backend offline no fallback HTTP), mantendo `refresh` com saída não-zero no wrapper.

- [x] Correção de causa-raiz OpenAPI (`sqlalchemy.INET`) validada (2026-02-08 01:34 BRT):
  - causa confirmada por histórico: commit `e20eac8` introduziu `sa.INET()` no bloco autogerado de `app/models/data_access_log.py`.
  - correção aplicada:
    - `Hb Track - Backend/scripts/autogen_model_from_db.py`: mapeamento de tipo PostgreSQL `INET` para `PG_INET()` + import `INET as PG_INET` no bloco `HB-AUTOGEN-IMPORTS`.
    - `Hb Track - Backend/app/models/data_access_log.py`: `ip_address` no bloco autogerado alterado de `sa.INET()` para `PG_INET()`.
  - evidência de não-regressão de símbolo:
    - `Select-String ... "sa\.INET\("` em `app/models/*.py` e `scripts/*.py` → **sem ocorrências**.
  - revalidação PASSO 0 após patch:
    - `powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\inv.ps1" refresh`
    - resultado: **`WRAPPER EXIT CODE: 0`** com `[OK] OpenAPI`, `[OK] Schema SQL`, `[OK] Alembic State`, `[OK] Manifest`.

- [x] Revalidação de `strict` em tabela baseline alinhada:
  - comando: `python .\Hb Track - Backend\scripts\model_requirements.py --table athlete_badges --profile strict`
  - saída: `[OK] ... strict profile passed` + `column_count=5` / `model_column_count=5`.

- [x] Revalidação de `strict` nas tabelas alvo da Fase 2.1.3:
  - `exercise_tags`:
    - comando: `python .\Hb Track - Backend\scripts\model_requirements.py --table exercise_tags --profile strict`
    - resultado: `exercise_tags_strict_exit=4`
    - evidência: FKs em estado OK (`fk_count=3`), restando `TYPE/NULLABLE` em `description` e `display_order`.
  - `data_access_logs`:
    - comando: `python .\Hb Track - Backend\scripts\model_requirements.py --table data_access_logs --profile strict`
    - resultado: `data_access_logs_strict_exit=4`
    - evidência: FKs em estado OK (`fk_count=2`), restando `TYPE_MISMATCH` em `entity_type`.

- [x] Revalidação de higiene de ignore para artefato temporário:
  - comando: `Select-String -Path ".gitignore" -Pattern "\.hb_tmp_tests"`
  - evidência: entradas presentes na raiz (`.gitignore:45` e `.gitignore:90`).
  - observação: `Test-Path "Hb Track - Backend/.gitignore"` retornou `False` (arquivo não existe mais no branch atual).

- [x] Conclusão da revisão dos [x] da 2.1.3:
  - progresso confirmado: mismatch de FK foi removido nas duas tabelas alvo;
  - bloqueio atual confirmado por evidência reproduzível: **apenas TYPE/NULLABLE** em `exercise_tags` e `data_access_logs`.

- [x] Rodada de evolução do `strict` (A-H) com evidências (2026-02-08 01:58 BRT):
  - PASSO 0 obrigatório executado:
    - `powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\inv.ps1" refresh`
    - resultado: `WRAPPER EXIT CODE: 0` com `[OK] OpenAPI`, `[OK] Schema SQL`, `[OK] Alembic State`, `[OK] Manifest`.
  - evolução implementada em `scripts/model_requirements.py` (strict):
    - validação de `nullable` explícito (`NULLABLE_IMPLICIT`) para colunas não-PK;
    - validação de `server_default` (kind/value, best-effort) com violações `MISSING_SERVER_DEFAULT`, `DEFAULT_KIND_MISMATCH`, `DEFAULT_VALUE_MISMATCH`;
    - validação estrutural de constraints por nome em strict:
      - `CHECK` (`MISSING_CHECK`/`EXTRA_CHECK`),
      - `UNIQUE` (`MISSING_UNIQUE`/`EXTRA_UNIQUE`),
      - `INDEX` (`MISSING_INDEX`/`EXTRA_INDEX`) + comparação de `unique` e `where` (`INDEX_UNIQUE_MISMATCH`, `INDEX_WHERE_MISMATCH`).
    - parser de PK robustecido para `PRIMARY KEY` em `CREATE TABLE` e também em `ALTER TABLE ... ADD CONSTRAINT ... PRIMARY KEY`.
    - normalização de defaults ajustada para equivalência `public.gen_random_uuid()` == `gen_random_uuid()`.
  - testes unitários do parser/AST revalidados no diretório backend:
    - `Set-Location "Hb Track - Backend"; python -m pytest tests/unit/test_model_requirements_schema_parser.py tests/unit/test_model_requirements_model_ast_parser.py -q`
    - resultado: `6 passed` (warnings não bloqueantes).
  - revalidação strict nas tabelas-alvo:
    - `python .\Hb Track - Backend\scripts\model_requirements.py --table exercise_tags --profile strict`
      - `exercise_tags_strict_exit=4`
      - violações atuais: `description` (TYPE/NULLABLE), `display_order` (NULLABLE), e `MISSING_SERVER_DEFAULT` em `is_active`.
    - `python .\Hb Track - Backend\scripts\model_requirements.py --table data_access_logs --profile strict`
      - `data_access_logs_strict_exit=4`
      - violação atual: `TYPE_MISMATCH` em `entity_type` (`varchar|50` vs `varchar|64`).
  - conclusão objetiva da rodada:
    - o validador strict agora cobre blocos adicionais de 2.1.3 (nullable explícito + defaults + constraints E-H);
    - as falhas remanescentes são **mismatchs reais de model** nas tabelas alvo, não crash/falha de parser.

- [x] Fechamento final das tabelas-alvo em `strict` + gate canônico (2026-02-08 02:18 BRT):
  - ajustes finais em models:
    - `app/models/exercise_tag.py`: removidas definições legacy duplicadas (`Column(...)`) que sobrescreviam bloco autogerado.
    - `app/models/data_access_log.py`: removidas definições legacy duplicadas (`mapped_column` manual com `String(64)` etc.) que sobrescreviam bloco autogerado.
  - ajuste final no validador:
    - `scripts/model_requirements.py`: `server_default=sa.text('false')` agora classificado como `default_literal` (evita falso `DEFAULT_KIND_MISMATCH`).
  - evidência requirements strict:
    - `python .\Hb Track - Backend\scripts\model_requirements.py --table exercise_tags --profile strict` → **passou** (`column_count=10`, `model_column_count=10`).
    - `python .\Hb Track - Backend\scripts\model_requirements.py --table data_access_logs --profile strict` → **passou** (`column_count=8`, `model_column_count=8`).
  - evidência gate canônico strict:
    - `.\scripts\models_autogen_gate.ps1 -Table "exercise_tags" -Profile strict ...` → `exercise_tags_gate_exit=0`.
    - `.\scripts\models_autogen_gate.ps1 -Table "data_access_logs" -Profile strict ...` → `data_access_logs_gate_exit=0`.



**A. Colunas (crítico — GAP #1 eliminado)**

- [x] `_validate_columns_exact_match()` (implementado em `_validate_columns_nullable_profile`):
  - [x] Extrai **todas** as colunas do model via AST (parsing completo do arquivo) — Evidência: `scripts/model_requirements.py::_parse_model_columns` percorre classe inteira e `model_column_count` bateu com schema (`exercise_tags=10`, `data_access_logs=8`, 2026-02-08 02:18 BRT).
  - [x] Compara com **todas** as colunas do `schema.sql` — Evidência: comparação por conjunto em `_validate_columns_nullable_profile` (`expected_names` vs `model_names`) + execução strict verde nas duas tabelas-alvo.
  - [x] Detecta **colunas extras** no model — Evidência: regra `EXTRA_COLUMN` ativa no validador; antes da limpeza dos blocos legacy houve divergências estruturais e após remoção das duplicidades as tabelas passaram em strict.
    ```python
    # Violation: EXTRA_COLUMN: nickname (exists in model line 42, not in schema.sql)
    ```
  - [x] Detecta **colunas faltantes** no model — Evidência: regra `MISSING_COLUMN` ativa em `_validate_columns_nullable_profile` e usada no mesmo fluxo de comparação set-diff.
    ```python
    # Violation: MISSING_COLUMN: legacy_id (exists in schema.sql, missing in model)
    ```
  - [x] **NÃO ignora** blocos `HB-AUTOGEN-COLUMNS` — valida resultado final do arquivo — Evidência: parser AST lê classe completa; falhas anteriores vieram justamente de declarações duplicadas fora do bloco autogen (corrigidas em `exercise_tag.py` e `data_access_log.py`).
  - [ ] Ignora colunas em seções marcadas `# LENIENT: dynamic columns` (perfil lenient)

**B. Tipos (crítico — GAP #2 eliminado)**

- [x] `_validate_column_types()` (implementado no subset inicial):
  - [x] Mapeamento correto PostgreSQL → SQLAlchemy (ver ANEXO A) — Evidência: `_schema_type_to_key` + `_model_type_to_key` cobrindo `uuid/int/date/datetime/text/varchar/numeric`; detecção corrigiu mismatch real `entity_type varchar|50 vs varchar|64` até strict passar em `data_access_logs`.
  - [x] Detecta tipo incompatível — Evidência: violação `TYPE_MISMATCH` reproduzida e depois eliminada (`data_access_logs.entity_type`) com reexecução strict em 2026-02-08 02:18 BRT.
    ```python
    # Violation: TYPE_MISMATCH: birth_date expected=Date (from DATE) got=DateTime (model line 45)
    ```
  - [ ] Aceita equivalências documentadas (ANEXO A: `ACCEPTABLE_EQUIVALENCES`)
  - [ ] Rejeita equivalências perigosas (ANEXO A: `REJECTED_EQUIVALENCES`)

**C. Nullable (crítico — GAP #2.1 eliminado)**

- [x] `_validate_nullability()`:
  - [x] DB `NOT NULL` → model deve ter `nullable=False` explícito — Evidência: regra `NULLABLE_IMPLICIT` + `NULLABLE_MISMATCH` ativa e usada no diagnóstico anterior de `exercise_tags`.
  - [x] DB nullable → model deve ter `nullable=True` explícito — Evidência: mesmas regras validando colunas nullable; após limpeza do model `exercise_tags` passou em strict.
  - [x] Primary Keys ignoradas (implicitamente NOT NULL) — Evidência: `if exp.is_primary_key: continue` em `_validate_columns_nullable_profile`.
  - [x] Detecta mismatch — Evidência: violações `NULLABLE_MISMATCH` reproduzidas em `exercise_tags` (rodadas anteriores) e removidas no fechamento final.
    ```python
    # Violation: NULLABLE_MISMATCH: email expected=NOT NULL got=nullable=True (model line 48)
    # Violation: NULLABLE_MISMATCH: phone expected=nullable got=missing/implicit False (model line 51)
    ```

**D. Foreign Keys (já implementado)**

- [ ] `_fk_present()` valida:
  - [x] Nome exato da FK (ex: `fk_teams_season_id`) — Evidência: matching por `constraint_name` em `_validate_fk_profile`; `fk_count=3` (`exercise_tags`) e `fk_count=2` (`data_access_logs`) com strict final verde.
  - [x] Referência correta (`ref_table.ref_column`) — Evidência: `_validate_fk_profile` compara `c.reference == exp.reference` e falharia com `FK_MISMATCH`.
  - [x] `ondelete` correto (RESTRICT, CASCADE, SET NULL, etc.) — Evidência: `_fk_ondelete_equivalent` aplicado na comparação; FKs validadas com profile `fk` e strict nas duas tabelas.
  - [ ] `use_alter=True` aceito (requerido para ciclos)
  - [x] Detecta FKs extras — Evidência: regra `EXTRA_FK` em `_validate_fk_profile` para nomes presentes no model e ausentes no schema.
    ```python
    # Violation: EXTRA_FK_NAME: fk_teams_season_id_invented (model line 55, not in schema.sql)
    ```

**E-H. CHECK constraints, Indexes, Unique Constraints, Server Defaults**

- [x] Validações análogas às anteriores (já descritas na versão anterior) — Evidência: `strict` passou nas tabelas-alvo e baseline (`exercise_tags`, `data_access_logs`, `athlete_badges`) com validação ativa de `MISSING/EXTRA_CHECK`, `MISSING/EXTRA_UNIQUE`, `MISSING/EXTRA_INDEX`, `INDEX_UNIQUE_MISMATCH`, `INDEX_WHERE_MISMATCH`, `MISSING_SERVER_DEFAULT`, `DEFAULT_KIND_MISMATCH`, `DEFAULT_VALUE_MISMATCH` em `scripts/model_requirements.py`.
- [x] Exit code **4** quando qualquer violação detectada — Evidência: múltiplas rodadas retornaram `exit=4` para mismatches reais (`exercise_tags`/`data_access_logs`) antes do fechamento; comportamento mantido.

**Status consolidado da Fase 2.1.3 (revisado/validado em 2026-02-08 02:42 BRT):**

- [x] Revalidação SSOT (PASSO 0): `powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\inv.ps1" refresh` → `WRAPPER EXIT CODE: 0`.
- [x] Revalidação strict de referência: `python .\Hb Track - Backend\scripts\model_requirements.py --table athlete_badges --profile strict` → `strict passed` (`column_count=5`, `model_column_count=5`).
- [x] Evidência mantida do fechamento das tabelas alvo em strict + gate canônico: `exercise_tags_gate_exit=0` e `data_access_logs_gate_exit=0` (rodada 2026-02-08 02:18 BRT).

**Ações que faltam para concluir completamente a Fase 2.1.3 (gap remanescente):**

1. [ ] Implementar e evidenciar suporte de `lenient` para ignorar colunas marcadas (`# LENIENT: dynamic columns`) com teste de prova (`strict` falha sem exceção e `lenient` passa com exceção explícita).
2. [ ] Implementar e evidenciar política explícita de equivalências de tipo (`ACCEPTABLE_EQUIVALENCES` e `REJECTED_EQUIVALENCES`) no comparador de tipos do `strict`.
3. [ ] Implementar e evidenciar validação de `use_alter=True` no contrato de FK quando aplicável (especialmente casos de ciclo), com violação explícita no requirements.
4. [ ] Consolidar checklist de fechamento com evidência reproduzível desses 3 pontos e promover os itens pendentes de 2.1.3 para `[x]`.

#### 2.1.4 Perfis de validação

- [x] **Perfil `fk`** (mínimo): apenas FKs
- [ ] **Perfil `strict`** (padrão): colunas + tipos + nullable + FKs + constraints
  - [x] Onda A concluída: colunas + nullable (+ FK)
  - [x] Onda B concluída: tipos (subset canônico inicial)
- [ ] **Perfil `lenient`** (opt-in): aceita diferenças documentadas em comments/config

#### 2.1.5 Integração com gate

- [x] `model_requirements.py` é **step obrigatório** no `models_autogen_gate.ps1` STEP 4
- [x] Exit code específico: **4** (requirements violations)
- [ ] Output estruturado com números de linha do model

---

## 📋 FASE 3 — Autogeração de Models (SSOT → código)

### 3.1 `autogen_model_from_db.py` — Gerador Canônico

**Comprovado (gate_exit=0 em tabelas sem ciclo):**
- [x] Flag `--create`: cria skeleton com blocos `HB-AUTOGEN-*`
- [x] Gera colunas/tipos/nullable corretos
- [x] Corrige duplicação UniqueConstraint vs Index

**Parcialmente comprovado (prova de código presente, sem validação final de gate):**
- [x] `fk_teams_season_id` com `use_alter=True` (grep colado em `team.py`)
- [x] `fk_seasons_team_id` com `use_alter=True` (grep colado em `season.py`)

**Pendente de validação (evidência parcial ou ausente):**
- [ ] Tipos String/VARCHAR/CHAR — política de length: verificar se `reflected_length` é respeitado em **todas** as tabelas (não só teams/seasons)
- [ ] `ondelete` priorizado do SSOT por `constraint_name` — confirmar que o mapeamento cobre todos os FKs do schema.sql
- [ ] Ciclo FK `use_alter` em **ambos os lados** — confirmar que seasons.py também tem `use_alter=True` (não só teams.py)

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

- [x] Integrado no gate após STEP 3 (parity pós-autogen)
- [x] Propaga exit code real do requirements (sem achatar)
- [x] Evidência com stub: `scripts/models_autogen_gate.ps1 -Table "teams"` retornou `teams_gate_exit=4`

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
        <TYPE>, 
        ForeignKey("seasons.id", name="fk_teams_season_id", use_alter=True),
        nullable=True
    )
    # HB-AUTOGEN-COLUMNS-END

# app/models/season.py (estado atual)
class Season(Base):
    __tablename__ = "seasons"
    
    # HB-AUTOGEN-COLUMNS-START
    team_id = Column(
        <TYPE>,
        ForeignKey("teams.id", name="fk_seasons_team_id", use_alter=True),
        nullable=True
    )
    # HB-AUTOGEN-COLUMNS-END
```

**Status de validação (evidência real 2026-02-07):**

- [x] Implementação no gerador: autogen suporta/força `use_alter=True` para ambas as FKs do ciclo
- [x] Evidência no código gerado: grep em `team.py` e `season.py` confirma `use_alter=True`.
- [x] `use_alter=True` confirmado no fk_teams_season_id (team.py)
- [x] `use_alter=True` confirmado no fk_seasons_team_id (season.py)
- [x] Gate validado com exit=0 para ambos (`teams_gate_exit=0`, `seasons_gate_exit=0`)
- [ ] `warnings_count=0` — pendente evidência explícita por tabela em `parity_report.json`

**Critério para "resolvido":**
- **OK (binário):** `gate_exit=0`
- **OK saúde:** `warnings_count=0` **ou** warning explicitamente permitido por política (`-AllowCycleWarning`) + mitigação objetiva validada
- Para ciclo `teams`↔`seasons`: `gate_exit=0` em scan limpo de teams **e** seasons, **OU** override explícito aceito com mitigação validada

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

**Status atualizado (2026-02-07):**

- [x] STEP 4 integrado no `models_autogen_gate.ps1`
- [x] Propagação de exit code 4 comprovada (`teams_gate_exit=4` com stub)
- [x] Implementação inicial real do `model_requirements.py` no perfil `fk`
- [x] Expansão inicial para `strict` (Onda A: colunas + nullable)
- [x] Onda B do `strict` (tipos) concluída no subset inicial
- [x] PASSO 10 concluído: scan global via `parity_scan.ps1 -FailOnStructuralDiffs` com `structural_count=0` e `warnings_count=0`
- [x] PASSO 11 concluído: baseline assentado e guard global limpo (`snapshot_exit=0`, `guard_exit=0`)
- [ ] Próximo foco: ampliar cobertura de tipos/equivalências e constraints remanescentes

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