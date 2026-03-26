#!/usr/bin/env python3
"""Validador de teto financeiro do pipeline de video.

Conta segundos pagos registrados em logs/geracao_log.csv e bloqueia:
- cenas fora da allowlist
- tentativas acima do permitido por cena
- segundos pagos acima do teto configurado
- projecao em BRL acima do hard cap
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "video_pipeline" / "config_video.json"
ALLOWLIST_PATH = ROOT / "video_pipeline" / "cenas_premium_autorizadas.csv"
LOG_PATH = ROOT / "video_pipeline" / "logs" / "geracao_log.csv"


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "sim"}


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_allowlist() -> dict[str, dict[str, str]]:
    with ALLOWLIST_PATH.open("r", encoding="utf-8", newline="") as fh:
        return {row["scene_id"]: row for row in csv.DictReader(fh)}


def load_log_rows() -> list[dict[str, str]]:
    with LOG_PATH.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida o orcamento atual e, opcionalmente, a proxima chamada paga."
    )
    parser.add_argument("--next-scene", dest="next_scene")
    parser.add_argument("--next-seconds", dest="next_seconds", type=int)
    args = parser.parse_args()

    if bool(args.next_scene) != bool(args.next_seconds):
        parser.error("--next-scene e --next-seconds devem ser informados juntos.")

    return args


def main() -> int:
    args = parse_args()
    config = load_config()
    allowlist = load_allowlist()
    rows = load_log_rows()

    allowed_lengths = set(config["visual_generation"]["allowed_request_lengths_s"])
    price_usd_per_s = float(config["visual_generation"]["price_usd_per_s"])
    hard_cap_brl = float(config["budget_guard"]["hard_cap_brl"])
    operational_cost_brl_per_s = float(config["budget_guard"]["operational_cost_brl_per_s"])
    max_paid_seconds = int(config["budget_guard"]["max_paid_seconds"])

    failures: list[str] = []
    attempts = Counter()
    total_paid_seconds = 0

    for index, row in enumerate(rows, start=2):
        scene_id = row["scene_id"].strip()
        if not scene_id:
            continue

        if scene_id not in allowlist:
            failures.append(f"Linha {index}: scene_id '{scene_id}' fora da allowlist.")
            continue

        scene_rule = allowlist[scene_id]
        paid_request = truthy(row["paid_request"])
        if not paid_request:
            continue

        if not truthy(scene_rule["paid_generation_allowed"]):
            failures.append(f"Linha {index}: cena '{scene_id}' nao pode consumir geracao paga.")
            continue

        request_length_s = int(row["request_length_s"])
        billed_seconds = int(row["billed_seconds"])

        if request_length_s not in allowed_lengths:
            failures.append(
                f"Linha {index}: request_length_s={request_length_s} nao permitido. "
                f"Permitidos: {sorted(allowed_lengths)}."
            )

        if billed_seconds <= 0:
            failures.append(f"Linha {index}: billed_seconds deve ser > 0.")
            continue

        attempts[scene_id] += 1
        if attempts[scene_id] > int(scene_rule["max_attempts"]):
            failures.append(
                f"Linha {index}: cena '{scene_id}' excedeu max_attempts={scene_rule['max_attempts']}."
            )

        total_paid_seconds += billed_seconds

    projected_cost_usd = total_paid_seconds * price_usd_per_s
    projected_cost_brl = total_paid_seconds * operational_cost_brl_per_s
    remaining_seconds = max_paid_seconds - total_paid_seconds
    remaining_brl = hard_cap_brl - projected_cost_brl

    print("Resumo de orcamento atual:")
    print(f"- segundos pagos acumulados: {total_paid_seconds}")
    print(f"- custo projetado USD: {projected_cost_usd:.2f}")
    print(f"- custo projetado BRL: {projected_cost_brl:.2f}")
    print(f"- segundos restantes ate o teto: {remaining_seconds}")
    print(f"- margem restante em BRL: {remaining_brl:.2f}")

    if total_paid_seconds > max_paid_seconds:
        failures.append(
            f"Total pago de {total_paid_seconds}s excede max_paid_seconds={max_paid_seconds}s."
        )

    if projected_cost_brl > hard_cap_brl:
        failures.append(
            f"Custo projetado de R$ {projected_cost_brl:.2f} excede hard_cap_brl=R$ {hard_cap_brl:.2f}."
        )

    if args.next_scene:
        next_scene = args.next_scene.strip()
        next_seconds = int(args.next_seconds)
        print("\nProjecao da proxima chamada paga:")
        print(f"- scene_id: {next_scene}")
        print(f"- billed_seconds: {next_seconds}")

        if next_scene not in allowlist:
            failures.append(f"Proxima cena '{next_scene}' esta fora da allowlist.")
        else:
            scene_rule = allowlist[next_scene]
            if not truthy(scene_rule["paid_generation_allowed"]):
                failures.append(f"Proxima cena '{next_scene}' nao pode consumir geracao paga.")
            if next_seconds not in allowed_lengths:
                failures.append(
                    f"Proxima chamada usa {next_seconds}s, mas os comprimentos permitidos sao {sorted(allowed_lengths)}."
                )

            planned_attempts = attempts[next_scene] + 1
            if planned_attempts > int(scene_rule["max_attempts"]):
                failures.append(
                    f"Proxima chamada faria a cena '{next_scene}' exceder max_attempts={scene_rule['max_attempts']}."
                )

        next_total_paid_seconds = total_paid_seconds + next_seconds
        next_projected_cost_usd = next_total_paid_seconds * price_usd_per_s
        next_projected_cost_brl = next_total_paid_seconds * operational_cost_brl_per_s

        print(f"- segundos pagos apos a proxima chamada: {next_total_paid_seconds}")
        print(f"- custo USD apos a proxima chamada: {next_projected_cost_usd:.2f}")
        print(f"- custo BRL apos a proxima chamada: {next_projected_cost_brl:.2f}")

        if next_total_paid_seconds > max_paid_seconds:
            failures.append(
                f"Proxima chamada elevaria o total para {next_total_paid_seconds}s, acima de {max_paid_seconds}s."
            )

        if next_projected_cost_brl > hard_cap_brl:
            failures.append(
                f"Proxima chamada elevaria o custo para R$ {next_projected_cost_brl:.2f}, acima de R$ {hard_cap_brl:.2f}."
            )

    if failures:
        print("\nFalhas:")
        for failure in failures:
            print(f"- {failure}")
        print("\nOrcamento reprovado. Nenhuma nova chamada paga deve ser feita.")
        return 1

    print("\nOrcamento aprovado. O teto continua preservado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
