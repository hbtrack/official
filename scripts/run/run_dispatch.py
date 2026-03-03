#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HB Track — Dispatch Runner (dispatch.v1)
Purpose:
  - Provide deterministic file-queue primitives for role handoffs via _reports/dispatch/
  - Atomic token creation (drop) and atomic claiming (claim) using os.replace
  - Anti-race: validate handoff_sha256 against handoff_path content

This script intentionally does NOT execute hb plan/report/verify.
It only manages tokens and receipts.

Python-only policy respected. No shell scripts.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import socket
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


DISPATCH_ROOT_DEFAULT = Path("_reports/dispatch")
SCHEMA_VERSION = "dispatch.v1"

VALID_ROLES = {"ARQUITETO", "EXECUTOR", "TESTADOR", "HUMANO"}
VALID_REASONS = {
    "READY_FOR_EXECUTION",
    "READY_FOR_VERIFY",
    "REJECTED_IMPL",
    "AH_DIVERGENCE",
    "BLOCKED_INPUT",
    "PLAN_AMBIGUOUS",
    "WRITE_SCOPE_INVALID",
    "BLOCKED_INFRA",
    "PASS_FOR_SEAL",
}

TOKEN_SUFFIX_TODO = ".todo.json"
TOKEN_SUFFIX_INPROGRESS = ".inprogress.json"
TOKEN_SUFFIX_DONE = ".done.json"
TOKEN_SUFFIX_FAIL = ".fail.json"
TOKEN_SUFFIX_BLOCKED = ".blocked.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def token_filename(run_id: str, ar_id: str, attempt: int, from_role: str, to_role: str) -> str:
    # Deterministic and filesystem-friendly.
    return f"{run_id}__AR_{ar_id}__A{attempt}__{from_role}_TO_{to_role}{TOKEN_SUFFIX_TODO}"


@dataclass(frozen=True)
class Token:
    schema_version: str
    run_id: str
    from_role: str
    to_role: str
    ar_id: str
    handoff_path: str
    handoff_sha256: str
    reason: str
    attempt: int
    created_utc: str
    next_action: Optional[Dict[str, Any]] = None
    receipt: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = dataclasses.asdict(self)
        # remove nulls for cleanliness
        return {k: v for k, v in d.items() if v is not None}


def validate_token_fields(t: Token) -> None:
    if t.schema_version != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if t.from_role not in VALID_ROLES:
        raise ValueError(f"from_role invalid: {t.from_role}")
    if t.to_role not in VALID_ROLES:
        raise ValueError(f"to_role invalid: {t.to_role}")
    if t.reason not in VALID_REASONS:
        raise ValueError(f"reason invalid: {t.reason}")
    if not (len(t.ar_id) == 3 and t.ar_id.isdigit()):
        raise ValueError(f"ar_id must be 3 digits: {t.ar_id}")
    if len(t.handoff_sha256) != 64 or any(c not in "0123456789abcdef" for c in t.handoff_sha256):
        raise ValueError("handoff_sha256 must be lowercase hex sha256")
    if t.attempt < 0 or t.attempt > 99:
        raise ValueError("attempt out of range (0..99)")


def write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    safe_mkdir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.write_text(data, encoding="utf-8")
    os.replace(str(tmp), str(path))  # atomic rename


def drop_token(
    dispatch_root: Path,
    run_id: str,
    from_role: str,
    to_role: str,
    ar_id: str,
    handoff_path: Path,
    reason: str,
    attempt: int,
    next_action: Optional[Dict[str, Any]] = None,
) -> Path:
    if from_role not in VALID_ROLES or to_role not in VALID_ROLES:
        raise ValueError("Invalid role")
    if reason not in VALID_REASONS:
        raise ValueError("Invalid reason")

    if not handoff_path.exists():
        raise FileNotFoundError(f"handoff_path not found: {handoff_path}")

    handoff_hash = sha256_file(handoff_path)
    token = Token(
        schema_version=SCHEMA_VERSION,
        run_id=run_id,
        from_role=from_role,
        to_role=to_role,
        ar_id=ar_id,
        handoff_path=str(handoff_path).replace("\\", "/"),
        handoff_sha256=handoff_hash,
        reason=reason,
        attempt=attempt,
        created_utc=utc_now_iso(),
        next_action=next_action,
    )
    validate_token_fields(token)

    queue_dir = dispatch_root / to_role
    safe_mkdir(queue_dir)
    final_path = queue_dir / token_filename(run_id, ar_id, attempt, from_role, to_role)
    write_json_atomic(final_path, token.to_dict())
    return final_path


def list_todo_tokens(queue_dir: Path) -> list[Path]:
    if not queue_dir.exists():
        return []
    # Deterministic ordering: lexicographic (filename includes run_id/ar_id/attempt)
    return sorted([p for p in queue_dir.iterdir() if p.is_file() and p.name.endswith(TOKEN_SUFFIX_TODO)])


def claim_one(queue_dir: Path) -> Optional[Tuple[Path, Dict[str, Any]]]:
    todos = list_todo_tokens(queue_dir)
    for todo in todos:
        inprogress = todo.with_name(todo.name.replace(TOKEN_SUFFIX_TODO, TOKEN_SUFFIX_INPROGRESS))
        try:
            os.replace(str(todo), str(inprogress))  # atomic claim
        except FileNotFoundError:
            continue  # lost race; try next
        payload = json.loads(inprogress.read_text(encoding="utf-8"))
        return inprogress, payload
    return None


def finalize_token(
    inprogress_path: Path,
    payload: Dict[str, Any],
    result: str,
    note: str,
) -> Path:
    if result not in {"DONE", "FAIL", "BLOCKED"}:
        raise ValueError("result must be DONE|FAIL|BLOCKED")

    worker = f"{socket.gethostname()}:{os.getenv('USER') or os.getenv('USERNAME') or 'unknown'}"
    receipt = {
        "finished_utc": utc_now_iso(),
        "result": result,
        "note": note[:300],
        "worker_id": worker[:120],
    }
    payload["receipt"] = receipt

    # choose suffix
    if result == "DONE":
        suffix = TOKEN_SUFFIX_DONE
    elif result == "FAIL":
        suffix = TOKEN_SUFFIX_FAIL
    else:
        suffix = TOKEN_SUFFIX_BLOCKED

    final_path = inprogress_path.with_name(inprogress_path.name.replace(TOKEN_SUFFIX_INPROGRESS, suffix))
    write_json_atomic(final_path, payload)
    # remove inprogress after writing final (keep only final)
    try:
        inprogress_path.unlink(missing_ok=True)
    except Exception:
        # best-effort; not fatal
        pass
    return final_path


def validate_handoff_hash(payload: Dict[str, Any]) -> Tuple[bool, str]:
    handoff_path = Path(payload["handoff_path"])
    expected = payload["handoff_sha256"]
    if not handoff_path.exists():
        return False, "BLOCKED_MISSING_HANDOFF_FILE"
    actual = sha256_file(handoff_path)
    if actual != expected:
        return False, "BLOCKED_STALE_HANDOFF"
    return True, "OK"


def cmd_hash(args: argparse.Namespace) -> int:
    p = Path(args.path)
    if not p.exists():
        print(f"NOT_FOUND: {p}", file=sys.stderr)
        return 4
    print(sha256_file(p))
    return 0


def cmd_drop(args: argparse.Namespace) -> int:
    try:
        dispatch_root = Path(args.dispatch_root)
        token_path = drop_token(
            dispatch_root=dispatch_root,
            run_id=args.run_id,
            from_role=args.from_role,
            to_role=args.to_role,
            ar_id=args.ar_id,
            handoff_path=Path(args.handoff_path),
            reason=args.reason,
            attempt=args.attempt,
            next_action=None,
        )
        print(str(token_path).replace("\\", "/"))
        return 0
    except Exception as e:
        print(f"DROP_FAIL: {e}", file=sys.stderr)
        return 3


def cmd_claim(args: argparse.Namespace) -> int:
    queue_dir = Path(args.dispatch_root) / args.role
    claim = claim_one(queue_dir)
    if not claim:
        print("NO_TOKENS")
        return 2

    inprogress_path, payload = claim
    ok, reason = validate_handoff_hash(payload)
    if not ok:
        final_path = finalize_token(inprogress_path, payload, "BLOCKED", reason)
        print(f"BLOCKED: {final_path}")
        return 4

    # Successful claim, print inprogress path + payload summary (deterministic, short)
    inprogress_posix = str(inprogress_path).replace('\\', '/')
    print(f"INPROGRESS: {inprogress_posix}")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_finish(args: argparse.Namespace) -> int:
    inprogress = Path(args.inprogress_path)
    if not inprogress.exists() or not inprogress.name.endswith(TOKEN_SUFFIX_INPROGRESS):
        print("INVALID_INPROGRESS_PATH", file=sys.stderr)
        return 4

    payload = json.loads(inprogress.read_text(encoding="utf-8"))
    # Optional re-check before finishing
    if args.recheck_hash:
        ok, reason = validate_handoff_hash(payload)
        if not ok and args.result != "BLOCKED":
            # Force BLOCKED if stale discovered at finish
            args.result = "BLOCKED"
            args.note = reason

    final_path = finalize_token(inprogress, payload, args.result, args.note)
    print(str(final_path).replace("\\", "/"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hb_dispatch.py")
    p.add_argument("--dispatch-root", default=str(DISPATCH_ROOT_DEFAULT), help="default: _reports/dispatch")

    sp = p.add_subparsers(dest="cmd", required=True)

    p_hash = sp.add_parser("hash", help="sha256 of a file")
    p_hash.add_argument("path")
    p_hash.set_defaults(func=cmd_hash)

    p_drop = sp.add_parser("drop", help="drop a token into target role queue")
    p_drop.add_argument("--run-id", required=True)
    p_drop.add_argument("--from-role", required=True, choices=sorted(VALID_ROLES))
    p_drop.add_argument("--to-role", required=True, choices=sorted(VALID_ROLES))
    p_drop.add_argument("--ar-id", required=True)
    p_drop.add_argument("--handoff-path", required=True)
    p_drop.add_argument("--reason", required=True, choices=sorted(VALID_REASONS))
    p_drop.add_argument("--attempt", type=int, default=0)
    p_drop.set_defaults(func=cmd_drop)

    p_claim = sp.add_parser("claim", help="claim one token from a role queue (todo -> inprogress)")
    p_claim.add_argument("--role", required=True, choices=sorted(VALID_ROLES))
    p_claim.set_defaults(func=cmd_claim)

    p_finish = sp.add_parser("finish", help="finish an inprogress token (-> done/fail/blocked)")
    p_finish.add_argument("--inprogress-path", required=True)
    p_finish.add_argument("--result", required=True, choices=["DONE", "FAIL", "BLOCKED"])
    p_finish.add_argument("--note", required=True)
    p_finish.add_argument("--recheck-hash", action="store_true", help="re-check handoff hash before finishing")
    p_finish.set_defaults(func=cmd_finish)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())