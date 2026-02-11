# AGENT_RULES_ENGINE.md

## Descrição
Motor de regras que governa decisões do agente. Contém as 7 regras fundamentais de autoridade, validação de CWD, repo hygiene, e anti-alucinação.

---

## Regras Fundamentais

### Regra 1: Canon Vence Sempre
Se houver conflito entre opinião e doc canônico → siga canon.

### Regra 2: SSOT Vence Opinião
Verdades técnicas vêm de artefatos gerados:
- `schema.sql` (DB source of truth)
- `openapi.json` (API contracts)
- `parity_report.json` (structural validation)
- `.hb_guard/baseline.json` (guard baseline)

### Regra 3: Não Invente Comandos
Só cmdlets/scripts em `08_APPROVED_COMMANDS.md`.

### Regra 4: Respeite Exit Codes
Não aplaine 0/1/2/3/4 — propague conforme `exit_codes.md`.

### Regra 5: Evidência Obrigatória
Toda conclusão técnica = doc canônico + evidência (log/diff/artefato).

### Regra 6: CWD é Contrato
- `inv.ps1 refresh` → repo root
- Gates/models → backend root
- Se CWD errado → PARE

### Regra 7: Repo Hygiene
- Sem gates com repo sujo
- Sempre `git status --porcelain` antes de write

---

## TODO
- [ ] Adicionar fluxo de decisão (diagrama)
- [ ] Criar lookup table para cada regra
- [ ] Documentar exceções (se houver)
