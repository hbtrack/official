# contracts/_waivers/

Waivers **machine-readable** para o pipeline de contract gates.

## Regras

- **Proibido waiver textual** (ADR/comentário/Markdown não libera gate).
- Waivers devem viver em: `contracts/_waivers/<gate_id>/<waiver_name>.json`
- Waivers **expirados** ou **inválidos** devem falhar o pipeline (fail-closed).

## Schema (SSOT)

- `contracts/_waivers/waiver.schema.json`

## Gate suportado (no momento)

- `CONTRACT_BREAKING_CHANGE_GATE`
  - pasta: `contracts/_waivers/CONTRACT_BREAKING_CHANGE_GATE/`
  - `fingerprint.value` deve ser o **sha256** publicado no FAIL do gate (fingerprint do diff detectado).

## Como criar um waiver (breaking change)

1) Rode os gates e capture o `fingerprint_sha256` no FAIL do `CONTRACT_BREAKING_CHANGE_GATE`:
   - `python3 scripts/validate_contracts.py`
2) Crie um arquivo em `contracts/_waivers/CONTRACT_BREAKING_CHANGE_GATE/<nome>.json` seguindo o schema.
3) Reexecute os gates. Se o waiver for válido e o fingerprint bater, o gate passa.
