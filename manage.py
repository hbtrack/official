#!/usr/bin/env python
"""
Django management utility — HB Track.
Referência: ADR-031-backend-framework.md
"""
import os
import sys
from pathlib import Path


def main():
    # Adiciona src/ ao path para que Django encontre os módulos
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Activate the virtualenv: "
            ".venv/bin/activate"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
