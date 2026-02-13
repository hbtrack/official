from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUS = {"PASS", "FAIL", "DRIFT"}
MAIN_LIMIT = 150

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "docs" / "execution_tasks" / "artifacts"
ARCHIVE_DIR = REPO_ROOT / "docs" / "execution_tasks" / "_archive"

CHANGELOG_PATH = REPO_ROOT / "docs" / "ADR" / "architecture" / "CHANGELOG.md"
EXECUTIONLOG_PATH = REPO_ROOT / "docs" / "ADR" / "workflows" / "EXECUTIONLOG.md"

ARCHIVE_CHANGELOG_PATH = ARCHIVE_DIR / "CHANGELOG.md"
ARCHIVE_EXECUTIONLOG_PATH = ARCHIVE_DIR / "EXECUTIONLOG.md"


def _parse_iso8601(ts: str) -> datetime:
    if not isinstance(ts, str) or not ts.strip():
        raise ValueError("timestamp is empty or not a string")
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _norm_iso_utc(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def _sanitize(value: Any, max_len: int) -> str:
    s = "" if value is None else (value if isinstance(value, str) else str(value))
    s = s.replace("\r", " ").replace("\n", " ").strip()
    s = s.replace("|", "/")
    if max_len > 0 and len(s) > max_len:
        s = s[: max_len - 1] + "…"
    return s


@dataclass(frozen=True)
class Event:
    task_id: str
    timestamp_start: datetime
    timestamp_end: datetime
    status: str
    short_title: str
    scope: str
    artifacts: list[str]
    notes_short: str

    @property
    def ts_end_utc(self) -> str:
        return _norm_iso_utc(self.timestamp_end)


def _load_event(path: Path) -> Event:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "task_id",
        "timestamp_start",
        "timestamp_end",
        "status",
        "short_title",
        "scope",
        "artifacts",
        "notes_short",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"{path.as_posix()}: missing keys {missing}")

    status = data["status"]
    if status not in ALLOWED_STATUS:
        raise ValueError(f"{path.as_posix()}: invalid status '{status}'")

    artifacts = data["artifacts"]
    if not isinstance(artifacts, list):
        raise ValueError(f"{path.as_posix()}: artifacts must be a list")

    dt_start = _parse_iso8601(data["timestamp_start"])
    dt_end = _parse_iso8601(data["timestamp_end"])
    if dt_end < dt_start:
        raise ValueError(f"{path.as_posix()}: timestamp_end < timestamp_start")

    return Event(
        task_id=_sanitize(data["task_id"], 96),
        timestamp_start=dt_start,
        timestamp_end=dt_end,
        status=status,
        short_title=_sanitize(data["short_title"], 80),
        scope=_sanitize(data["scope"], 32),
        artifacts=[_sanitize(x, 260) for x in artifacts],
        notes_short=_sanitize(data["notes_short"], 200),
    )


def _write_index(path: Path, title: str, marker: str, lines: list[str], dry_run: bool = False) -> bool:
    """
    Write index file with retention policy and task list.
    
    Args:
        path: Target file path
        title: Document title
        marker: Auto-generated marker comment
        lines: Task lines
        dry_run: If True, skip writing and return change status
        
    Returns:
        True if file would be/was changed, False if identical
    """
    content = [
        f"# {title}",
        marker,
        "",
        "## Retention/Detail Policy",
        "- Recent tasks (last 150) are kept in the active list.",
        "- Detailed evidence for every task is archived in `docs/execution_tasks/artifacts/<TASK_ID>/`.",
        "- Use `scripts/compact_exec_logs.py` to maintain this document.",
        "",
        "## Tasks",
    ]
    content.extend(lines)
    content.append("")  # trailing newline
    new_text = "\n".join(content)

    old_text = ""
    if path.exists():
        old_text = path.read_text(encoding="utf-8")

    if old_text == new_text:
        return False

    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_text, encoding="utf-8", newline="\n")
    
    return True


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compact execution logs (CHANGELOG + EXECUTIONLOG)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Apply updates (default)
  %(prog)s --dry-run          # Preview without applying
  %(prog)s --output text      # Human-readable output
  %(prog)s --output json      # JSON output (default)
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing files'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='json',
        help='Output format (default: json)'
    )
    return parser.parse_args()


def main() -> int:
    """
    Main execution logic.
    
    Exit Codes:
      0: noop (no files changed)
      1: updated (files changed successfully)
      2: validation_error (invalid event.json)
      3: runtime_error (unexpected exception)
    """
    args = parse_args()
    
    marker = "<!-- AUTO-GENERATED. Source: docs/execution_tasks/artifacts/*/event.json -->"

    errors: list[str] = []
    events_by_task: dict[str, Event] = {}

    if ARTIFACTS_DIR.exists():
        for ev_path in sorted(ARTIFACTS_DIR.glob("*/event.json")):
            try:
                ev = _load_event(ev_path)
                prev = events_by_task.get(ev.task_id)
                if prev is None or ev.timestamp_end > prev.timestamp_end:
                    events_by_task[ev.task_id] = ev
            except Exception as e:
                errors.append(str(e))

    if errors:
        out = {"status": "validation_error", "errors": errors}
        if args.output == 'json':
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print(f"❌ Validation errors:")
            for err in errors:
                print(f"  - {err}")
        return 2

    events = list(events_by_task.values())
    events.sort(key=lambda e: (-e.timestamp_end.timestamp(), e.task_id))

    main_events = events[:MAIN_LIMIT]
    archived_events = events[MAIN_LIMIT:]

    def changelog_line(ev: Event) -> str:
        return f"- {ev.ts_end_utc} | {ev.task_id} | {ev.status} | {ev.scope} | {ev.short_title}"

    def executionlog_line(ev: Event) -> str:
        return f"- {ev.ts_end_utc} | {ev.task_id} | {ev.status} | {ev.short_title} | {ev.notes_short}"

    changed: list[str] = []

    if _write_index(
        CHANGELOG_PATH,
        "CHANGELOG",
        marker,
        [changelog_line(e) for e in main_events],
        dry_run=args.dry_run,
    ):
        changed.append(CHANGELOG_PATH.as_posix())

    if _write_index(
        EXECUTIONLOG_PATH,
        "EXECUTIONLOG",
        marker,
        [executionlog_line(e) for e in main_events],
        dry_run=args.dry_run,
    ):
        changed.append(EXECUTIONLOG_PATH.as_posix())

    # Archives: write only if needed (overflow) or if archive files already exist.
    if archived_events or ARCHIVE_CHANGELOG_PATH.exists() or ARCHIVE_EXECUTIONLOG_PATH.exists():
        if not args.dry_run:
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

        if _write_index(
            ARCHIVE_CHANGELOG_PATH,
            "CHANGELOG (ARCHIVE)",
            marker,
            [changelog_line(e) for e in archived_events],
            dry_run=args.dry_run,
        ):
            changed.append(ARCHIVE_CHANGELOG_PATH.as_posix())

        if _write_index(
            ARCHIVE_EXECUTIONLOG_PATH,
            "EXECUTIONLOG (ARCHIVE)",
            marker,
            [executionlog_line(e) for e in archived_events],
            dry_run=args.dry_run,
        ):
            changed.append(ARCHIVE_EXECUTIONLOG_PATH.as_posix())

    # Determine exit code: 0=noop, 1=updated
    exit_code = 1 if changed else 0
    
    # Output
    if args.output == 'json':
        out = {
            "status": "ok",
            "events_total": len(events),
            "main_events": len(main_events),
            "archived_events": len(archived_events),
            "changed_files": changed,
            "dry_run": args.dry_run,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if args.dry_run:
            if changed:
                print(f"✅ [DRY-RUN] Would update {len(changed)} file(s):")
                for f in changed:
                    print(f"  - {f}")
            else:
                print("✅ [DRY-RUN] No changes needed (logs already current)")
        else:
            if changed:
                print(f"✅ Updated {len(changed)} file(s):")
                for f in changed:
                    print(f"  - {f}")
            else:
                print("✅ No changes needed (logs already current)")
        print(f"\nEvents: {len(main_events)} main, {len(archived_events)} archived")
    
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        out = {"status": "runtime_error", "error": str(e)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        raise SystemExit(3)
