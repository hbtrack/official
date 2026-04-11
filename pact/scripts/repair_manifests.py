#!/usr/bin/env python3
"""Repair traceability manifest hashes after contract modifications.

Reads each manifest, recomputes SHA-256 for all source_contracts and
generated_artifacts entries (using actual file content), updates
source_tree_sha256 / generated_tree_sha256, and writes back.
"""
import hashlib
import sys
from pathlib import Path

import yaml

root = Path(".")


def sha256_file(path: str) -> str | None:
    f = root / path
    if not f.exists():
        return None
    return hashlib.sha256(f.read_bytes()).hexdigest()


def tree_hash(entries: list[dict]) -> str:
    h = hashlib.sha256()
    for e in sorted(entries, key=lambda x: x["path"]):
        h.update(e["path"].encode("utf-8"))
        h.update(b"\x00")
        h.update(e["sha256"].encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def repair_entry_list(entries: list[dict], label: str) -> tuple[list[dict], int]:
    updated = 0
    for entry in entries:
        p = entry.get("path", "")
        actual = sha256_file(p)
        if actual is None:
            print(f"  WARN: file not found: {p}")
            continue
        stored = entry.get("sha256", "")
        if actual != stored:
            print(f"  FIX [{label}] {p}")
            print(f"       {stored[:16]}... → {actual[:16]}...")
            entry["sha256"] = actual
            updated += 1
    return entries, updated


manifests = sorted(Path("generated/manifests").glob("*.traceability.yaml"))
print(f"Found {len(manifests)} manifests\n")

total_fixed = 0
manifests_changed = []

for mpath in manifests:
    raw = mpath.read_text()
    data = yaml.safe_load(raw)
    tm = data.get("traceability_manifest", {})

    changed = 0

    # Repair source_inputs (individual hashes only, no tree hash)
    si = tm.get("source_inputs") or []
    if si:
        si, n = repair_entry_list(si, "inp")
        changed += n
        if n:
            tm["source_inputs"] = si

    # Repair source_contracts + recompute source_tree_sha256
    sc = tm.get("source_contracts") or []
    if sc:
        sc, n = repair_entry_list(sc, "src")
        changed += n
        if n:
            tm["source_contracts"] = sc
        # Always recompute tree if source_inputs changed (tree only covers source_contracts,
        # but recompute anyway to ensure consistency)
        new_tree = tree_hash(sc)
        old_tree = tm.get("source_tree_sha256", "")
        if new_tree != old_tree:
            print(f"  FIX source_tree_sha256: {old_tree[:16]}... → {new_tree[:16]}...")
            tm["source_tree_sha256"] = new_tree
            changed += 1

    # Repair generated_artifacts + recompute generated_tree_sha256
    ga = tm.get("generated_artifacts") or []
    if ga:
        ga, n = repair_entry_list(ga, "gen")
        changed += n
        if n:
            tm["generated_artifacts"] = ga
        new_tree = tree_hash(ga)
        old_tree = tm.get("generated_tree_sha256", "")
        if new_tree != old_tree:
            print(f"  FIX generated_tree_sha256: {old_tree[:16]}... → {new_tree[:16]}...")
            tm["generated_tree_sha256"] = new_tree
            changed += 1

    if changed:
        print(f"  Saving {mpath.name} ({changed} changes)\n")
        data["traceability_manifest"] = tm
        mpath.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        )
        total_fixed += changed
        manifests_changed.append(mpath.name)

print(f"\n{'='*60}")
print(f"Total fixes: {total_fixed}")
print(f"Manifests changed: {len(manifests_changed)}")
for m in manifests_changed:
    print(f"  - {m}")
