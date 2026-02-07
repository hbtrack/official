**Status: PROPOSED (plano completo, sem “ajustes depois”)**

Objetivo: **eliminar o falso requisito de `COMMENT ON COLUMN` para invariantes Classe B quando o enforcement real é trigger/function**, **sem abrir brecha para alucinação**, e manter o fluxo **prompt curto → execução confiável** via gate.

A base canônica já diz que **Classe B = DB Trigger/Function** e prova primária é **runtime (efeito colateral)**. ([Gist][1])
O protocolo/guardrails já definem o loop `refresh → gate` e (se infra mudou) `all → drift → promote → all`. ([Gist][2])

---

# Ações exatas

## Fase 0 — Congelar o contrato alvo (1 decisão técnica)

Você vai manter compatibilidade com o padrão atual (B “column+comment”) **e adicionar** um modo alternativo determinístico para B “trigger/function”.

**Contrato final para Classe B (determinístico):**

* **B1 (Column Doc, legado/atual):** exige anchors `db.table + db.column + db.comment` e valida existência de `COMMENT ON COLUMN` no `schema.sql`.
* **B2 (Enforcement, novo):** exige anchors `db.table + db.trigger + db.function` e valida no `schema.sql`:

  1. existe o `CREATE TRIGGER <tr>`
  2. o trigger é **ON public.<table>**
  3. o trigger **EXECUTE FUNCTION public.<fn>** (binding explícito)
  4. existe o `CREATE FUNCTION <fn>`

➡️ **Sem heurística**. O SPEC precisa declarar **tr e fn explícitos**; o verifier só aceita se o schema provar. Isso bloqueia alucinação.

---

## Fase 1 — Documentação “perfeita” (para o prompt continuar curto)

### 1.1 Atualizar `docs/_ai/INV_TASK_TEMPLATE.md`

Adicionar uma seção curta “**Classe B — Modos aceitos (B1/B2)**” + regra anti-alucinação:

* Se Classe B usar `db.column`, então **comment on column** é obrigatório.
* Se Classe B usar `db.trigger/db.function`, então **binding no schema.sql** é obrigatório (ON table + EXECUTE FUNCTION).
* Proibido declarar `db.function` ou `db.trigger` sem existir no schema (o verifier vai barrar).

Isso mantém o prompt curto porque a regra fica no template. ([Gist][3])

### 1.2 Atualizar `INVARIANTS_TESTING_CANON.md` (opcional mas recomendado)

Só uma nota curta: “Classe B aceita evidência secundária de binding no schema (tripwire), mas prova primária é runtime”. Isso já está alinhado com o CANON (“schema como mapa; runtime como território”). ([Gist][1])

---

## Fase 2 — Infra (verifier): suportar B2 sem abrir brecha

> Isso é **mudança de infra** ⇒ obrigatoriamente no final você roda `inv.ps1 all` e, se drift, `drift → promote → all`. ([Gist][4])

### 2.1 Alterar `docs/scripts/verify_invariants_tests.py`

No trecho onde hoje a Classe B está “hardcoded” para `['table','column','comment']` (você citou linha ~1588), mude para:

* Aceitar **B1 OR B2**:

  * Se encontrou anchors de B1 → validar comment on column (comportamento atual).
  * Senão, se encontrou anchors de B2 (`db.trigger` e `db.function`) → validar existência + binding no schema.

### 2.2 Implementar validações determinísticas (B2)

No verifier, para B2:

1. **Trigger existe** no `schema.sql` (match literal do nome `tr_*`)
2. **Function existe** no `schema.sql` (match literal do nome `fn_*`)
3. **Binding existe** no `schema.sql` com os 3 elementos no mesmo “bloco” do trigger:

   * `CREATE TRIGGER <tr>`
   * `ON public.<table>`
   * `EXECUTE FUNCTION public.<fn>` (ou equivalente do dump)

### 2.3 Códigos de erro novos (para debug rápido)

Adicionar violations claras (sem “string match humano”):

* `B_TRIGGER_NOT_FOUND`
* `B_FUNCTION_NOT_FOUND`
* `B_BINDING_NOT_FOUND`
* `B_ANCHORS_INVALID` (se não for B1 nem B2)

---

## Fase 3 — Corrigir a invariante que está falhando (`wellness_reminders.responded_at`)

### 3.1 Atualizar o SPEC (INVARIANTS_*.md correspondente)

Onde hoje está:

* `db.table: wellness_reminders`
* `db.column: responded_at`
* `db.comment: ...`

Mude para **B2**:

* `db.table: wellness_reminders`
* `db.trigger: tr_<nome_exato_no_schema>`
* `db.function: fn_update_wellness_response_timestamp` (exemplo do seu caso)

> Importante: **use nomes reais do schema.sql**, nada inventado.

### 3.2 Atualizar/criar o teste Classe B (runtime)

Teste deve provar **efeito colateral** (CANON):

1. inserir/alterar o registro que dispara o trigger
2. assert que `responded_at` foi setado/atualizado
3. rollback/isolamento adequado

CANON exige runtime como prova primária para B. ([Gist][1])

---

## Fase 4 — Execução do protocolo e fechamento com gate (sem atalhos)

### 4.1 Atualizar SSOT

```powershell
cd "C:\HB TRACK"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 refresh
```

(Regra 0 do protocolo.) ([Gist][2])

### 4.2 Rodar gate da INV afetada

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 gate INV-<AQUI>
```

Repetir até `EXIT_CODE=0`. ([Gist][2])

### 4.3 Como houve mudança de infra (verifier), rodar gate all

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 all
```

Se `EXIT=3` com verify/pytest OK:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 drift
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 promote
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inv.ps1 all
```

Exigir `EXIT_ALL=0`. ([Gist][4])

---

# Critérios de sucesso (objetivos, sem subjetividade)

1. O verifier **continua aceitando** B1 (column+comment) para invariantes antigas.
2. O verifier **aceita** B2 (trigger+function) **somente** quando:

   * trigger e function existem no `schema.sql`
   * existe binding ON `<table>` EXECUTE FUNCTION `<fn>` no schema
3. A invariante `wellness_reminders.responded_at` passa sem exigir `COMMENT ON COLUMN`.
4. `inv.ps1 all` termina em **EXIT_ALL=0**.

---

