#!/usr/bin/env python3
"""
DISABLED — não conectado a nenhuma cadeia de hooks ativa.

Motivo: este script era um no-op incondicional (sys.exit(0)) sem nenhum enforcement real.
Removido da cadeia PreToolUse em settings.local.json conforme HBCONTROL.md Onda 0.

Para reativar: implementar política real de backend gate e reconectar em settings.local.json.
"""
import sys

raise RuntimeError(
    "check_backend_gate está DISABLED. Não deve ser chamado. "
    "Ver HBCONTROL.md Onda 0 para contexto."
)
