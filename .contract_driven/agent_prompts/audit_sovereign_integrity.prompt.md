---
name: audit_sovereign_integrity
description: "Auditoria estrutural: detecta duplicação de autoridade e artefatos soberanos ausentes (audit-only, não produz artefato normativo)"
---

# AUDITORIA DE INTEGRIDADE SOBERANA

## 1. Objetivo Exato

Detectar **duplicação de autoridade** (dois artefatos reivindicam SSOT sobre o mesmo conceito)
e **ausência de artefato soberano obrigatório** listado em `CONTRACT_SYSTEM_RULES.md §3`.

Não é "revisar documentação". É provar que cada conceito tem exatamente uma fonte —
nem zero nem duas.

---

## 2. Escopo Exato

| Camada | Artefatos verificados |
|--------|----------------------|
| Governança do sistema | `.contract_driven/CONTRACT_SYSTEM_RULES.md`, `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`, `.contract_driven/GLOBAL_TEMPLATES.md` |
| Canon global | Todos os arquivos listados em `CONTRACT_SYSTEM_RULES.md §3.2` |
| Contratos técnicos | `contracts/openapi/openapi.yaml`, `contracts/openapi/paths/*.yaml`, `contracts/schemas/**/*.schema.json`, `contracts/workflows/**/*.arazzo.yaml`, `contracts/asyncapi/**/*.yaml` |
| Docs de módulo (mínimo obrigatório) | `docs/hbtrack/modulos/<MODULE>/README.md`, `MODULE_SCOPE_<MODULE>.md`, `DOMAIN_RULES_<MODULE>.md`, `INVARIANTS_<MODULE>.md`, `TEST_MATRIX_<MODULE>.md` para cada módulo com status ≥ `draft_contract` |

**Fora de escopo**: conteúdo semântico dos artefatos, conformidade de API, lógica de negócio.

---

## 3. Tipo de Teste

**Auditoria estrutural de autoridade.**

Verifica: presença canônica, ausência de duplicata soberana, hierarquia de precedência respeitada.
Não verifica: validade de conteúdo, completude semântica, cobertura de domínio.

---

## 4. Critérios Operacionais (não "qualidade")

| Critério | Definição binária de PASS |
|----------|--------------------------|
| **C1 — Presença** | Cada artefato listado em `RULES §3.1–§3.6` existe no path canônico exato |
| **C2 — Unicidade** | Nenhum conceito tem dois artefatos reivindicando `SSOT`, `canônico` ou `fonte soberana` sem disclaimer explícito |
| **C3 — Precedência** | Conflito entre dois artefatos é resolvível pela ordem de `RULES §5` sem ambiguidade |
| **C4 — Sem intrusos** | Nenhum arquivo fora da allowlist de `docs/_canon/` usa linguagem de autoridade (gate `CANON_ALLOWLIST_GATE` + `SHADOW_AUTHORITY_GATE`) |
| **C5 — Boot classifica** | Todo artefato de governça promovido tem classificação em `boot_minimo` / `boot_condicional` / `gate_only` em `docs/_canon/AGENT_INSTRUCTIONS.md §7` |

FAIL em qualquer critério = bloqueio da auditoria com código explícito. Não há "parcialmente OK".

---

## 5. Formato de Saída Obrigatório

### 5.1 Scorecard de Presença

```
AUDITORIA SOBERANA — HB TRACK
Data: <ISO-8601>
Executor: audit_sovereign_integrity.prompt.md v1.0.0

CRITÉRIO C1 — PRESENÇA CANÔNICA
| Artefato | Path esperado | Existe? | Código de bloqueio |
|----------|--------------|---------|-------------------|
| CONTRACT_SYSTEM_RULES.md | .contract_driven/ | PASS/FAIL | — ou BLOCKED_REQUIRED_ARTIFACT_MISSING |
| ... (todos os §3.1–§3.6) |

CRITÉRIO C2 — UNICIDADE SOBERANA
| Conceito | Artefato A | Artefato B | Duplicata detectada? | Código |
|----------|-----------|-----------|---------------------|--------|
| ...

CRITÉRIO C3 — PRECEDÊNCIA
| Conflito encontrado | Resolvível por RULES §5? | PASS/FAIL |
| ...

CRITÉRIO C4 — INTRUSOS EM CANON
| Arquivo suspeito | Path | Linguagem de autoridade detectada | PASS/FAIL |
| ...

CRITÉRIO C5 — CLASSIFICAÇÃO DE BOOT
| Artefato novo | Classificação em docs/_canon/AGENT_INSTRUCTIONS.md §7 | PASS/FAIL |
| ...

RESULTADO FINAL: PASS | FAIL
Bloqueios ativos: [lista de códigos ou NENHUM]
```

### 5.2 Instrução de iteração

Se FAIL: listar exatamente quais artefatos precisam ser criados, movidos ou desambiguados.
Não sugerir workaround textual. Cada item de FAIL gera uma ação corretiva específica.

---

## 6. Restrições de Execução

- **Não dar PASS por aparência.** Arquivo existente com nome errado = FAIL em C1.
- **Não inferir autoridade.** Se não há declaração explícita de SSOT, não presuma que existe.
- **Não consolidar dois FAILs num "parcial".** Cada critério é binário e independente.
- **Não sugerir ações além do escopo desta auditoria.** Correções são tarefa de outro worker.
- **Não aumentar prolixidade.** Linhas sem violação = uma linha `PASS` na tabela, sem comentário.

---

## 7. Iteração Guiada por Falha

Após execução inicial:
- Qualquer C2 (duplicata soberana) detectado → promover à regra em `RULES §3` + registrar no `SHADOW_AUTHORITY_GATE`
- Qualquer C5 (sem classificação de boot) detectado → promover à regra em `RULES §2A.4`
- Repetir auditoria até resultado PASS completo antes de autorizar qualquer novo contrato
