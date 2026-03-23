#!/usr/bin/env python3
"""Preflight do pipeline de video.

Falha se o ambiente ou os arquivos obrigatorios nao estiverem prontos.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "video_pipeline" / "config_video.json"
ALLOWLIST_PATH = ROOT / "video_pipeline" / "cenas_premium_autorizadas.csv"


def check(condition: bool, label: str, detail: str, failures: list[str]) -> None:
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}: {detail}")
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []

    check(CONFIG_PATH.exists(), "config_video.json", str(CONFIG_PATH), failures)
    check(ALLOWLIST_PATH.exists(), "cenas_premium_autorizadas.csv", str(ALLOWLIST_PATH), failures)

    if not CONFIG_PATH.exists():
        print("\nPreflight interrompido: configuracao ausente.")
        return 1

    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        config = json.load(fh)

    source_project_dir = Path(config["source_project_dir"])
    required_source_files = config.get("required_source_files", [])

    check(source_project_dir.exists(), "source_project_dir", str(source_project_dir), failures)
    for relative_name in required_source_files:
        target = source_project_dir / relative_name
        check(target.exists(), f"source_file:{relative_name}", str(target), failures)

    for command_name in ("ffmpeg", "piper"):
        command_path = shutil.which(command_name)
        check(command_path is not None, f"command:{command_name}", command_path or "ausente", failures)

    for env_name in config.get("vertex_required_env", []):
        value = os.environ.get(env_name, "")
        check(bool(value), f"env:{env_name}", value or "ausente", failures)
        if env_name == "GOOGLE_APPLICATION_CREDENTIALS" and value:
            check(Path(value).exists(), "credentials_file", value, failures)

    for relative_log in config.get("required_logs", []):
        log_path = ROOT / "video_pipeline" / relative_log.replace("logs/", "logs/", 1)
        check(log_path.exists(), f"log:{relative_log}", str(log_path), failures)

    print("\nResumo:")
    if failures:
        print(f"Preflight reprovado com {len(failures)} bloqueio(s).")
        print("Nenhuma chamada paga ao Veo deve ser executada ate todos os bloqueios serem resolvidos.")
        return 1

    print("Preflight aprovado. O ambiente esta apto para continuar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
