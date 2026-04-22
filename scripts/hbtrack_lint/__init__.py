"""
LEGACY — DEPRECATED

Este módulo (hbtrack_lint) está legado e não faz parte do caminho crítico.

O gate LEGACY_CRITICAL_PATH_GATE (GATES_REGISTRY.yaml, ordem 20I) proíbe
o uso de hbtrack_lint em qualquer chamada do caminho crítico de validação.

Qualquer lógica de linting de contratos deve usar:
  scripts/contracts/validate/validate_contracts.py

Este arquivo existe apenas para satisfazer o gate TestHbtrackLintLegacyMarker
que verifica que o marcador de legado está presente.
"""

# legado / deprecated / LEGACY — não importar neste módulo em código de produção.
