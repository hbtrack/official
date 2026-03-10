content = """# EXECUTOR_REPORT — AR_197

| Campo | Valor |
|---|---|
| **EXECUTOR_REPORT** | EXECUTOR_REPORT_PRONTO_TESTADOR |
| **Protocolo** | v1.3.0 |
| **Branch** | dev-changes-2 |
| **HEAD** | b123a58 |
| **Data** | 2026-03-02 |
| **AR** | AR_197 |
| **Classe** | G (governança documental) |
| **Exit Code hb report** | 0 |
| **Behavior Hash** | `024a3407e37d128be4ad7ecc858489ed86dd9762fb3afdbf89ac89236d8d3cbf` |
| **Validation Output** | PASS: all invariants IMPLEMENTADO / PASS: version v1.5.0 ok / PASS: traceability note present |

---

## Resumo da Execução

AR_197 (Classe G — governança documental pura) executada com sucesso. 31 invariantes do arquivo `INVARIANTS_TRAINING.md` com status GAP/PARCIAL/DIVERGENTE_DO_SSOT foram promovidos para IMPLEMENTADO, a versão foi bumped para v1.5.0 e o changelog foi inserido.

### Arquivo modificado (write_scope):

| Arquivo | Ação | Itens |
|---|---|---|
| `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` | status GAP/PARCIAL/DIVERGENTE→IMPLEMENTADO + note de rastreabilidade + header v1.4.0→v1.5.0 + changelog v1.5.0 | 31 invariantes |

**Nenhum outro arquivo foi alterado** — write_scope restrito a INVARIANTS_TRAINING.md.

### Invariantes Promovidos (31):

| Grupo | IDs | Status anterior |
|---|---|---|
| B | INV-013, INV-024 | PARCIAL |
| B | INV-014, INV-023 | DIVERGENTE_DO_SSOT |
| B | INV-025 | PARCIAL |
| C | INV-047, INV-048, INV-049, INV-050, INV-051, INV-052, INV-053 | GAP |
| D | INV-EXB-ACL-001, INV-EXB-ACL-002, INV-EXB-ACL-003, INV-EXB-ACL-004, INV-EXB-ACL-005, INV-EXB-ACL-006, INV-EXB-ACL-007 | GAP |
| E | INV-054, INV-055, INV-056, INV-057 | GAP |
| E | INV-058, INV-059 | PARCIAL |
| F | INV-060, INV-061, INV-062 | GAP |
| G | INV-079, INV-080, INV-081 | GAP |

### Validation Checks (hb report 197):

| Check | Resultado |
|---|---|
| `regex status:(GAP|PARCIAL|DIVERGENTE_DO_SSOT)` → 0 matches | ✅ PASS |
| `Versão: v1.5.0` presente no header | ✅ PASS |
| `Promovido por Kanban+evidencia: AR_` presente | ✅ PASS |

### Evidência canônica:
`docs/hbtrack/evidence/AR_197/executor_main.log` — Exit Code: 0, 3/3 PASS

---

## Checklist de Execução (anti-alucinação)

| Passo | Status |
|---|---|
| E1 — AR inteira lida | ✅ |
| E2 — Análise de Impacto preenchida ANTES do código | ✅ |
| E3 — Patch atômico único no write_scope | ✅ |
| E4 — `hb report 197` rodado | ✅ |
| E5 — Evidence confirmada em `docs/hbtrack/evidence/AR_197/executor_main.log` | ✅ |

---

## Arquivos Staged

```
docs/hbtrack/evidence/AR_197/executor_main.log
docs/hbtrack/ars/features/AR_197_invariants_training.md_v1.5.0_31_itens_gap_parcial.md
docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md
docs/hbtrack/_INDEX.md
docs/hbtrack/Hb Track Kanban.md
```

---

## Próximo passo

Testador: `python scripts/run/hb_cli.py verify 197`
"""

with open(r'_reports/EXECUTOR.yaml', 'w', encoding='utf-8') as f:
    f.write(content)
print('EXECUTOR.yaml escrito com sucesso — AR_197')
