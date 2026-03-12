# generated/ — artefatos derivados (NÃO-SSOT)

Esta pasta contém **artefatos derivados** gerados de forma determinística a partir das fontes soberanas do HB Track.

Regras:
- **Nunca** editar manualmente arquivos sob `generated/`.
- Toda alteração deve vir de (re)geração via compiler determinístico:
  - `python3 scripts/contracts/validate/api/compile_api_policy.py --all`
- O validador de contratos deve detectar drift entre `generated/` e as fontes soberanas.

Subpastas (atuais):
- `generated/resolved_policy/` — política resolvida por módulo + surface.
- `generated/contracts/` — cópias derivadas dos contratos SSOT (para consumo/integrações).
- `generated/manifests/` — manifestos de rastreabilidade (hash + insumos).

