from __future__ import annotations

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


def _write_index(path: Path, title: str, marker: str, lines: list[str]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = [f"# {title}", marker]
    content.extend(lines)
    content.append("")  # trailing newline
    new_text = "\n".join(content)

    old_text = ""
    if path.exists():
        old_text = path.read_text(encoding="utf-8")

    if old_text == new_text:
        return False

    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
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
        print(json.dumps(out, ensure_ascii=False, indent=2))
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
    ):
        changed.append(CHANGELOG_PATH.as_posix())

    if _write_index(
        EXECUTIONLOG_PATH,
        "EXECUTIONLOG",
        marker,
        [executionlog_line(e) for e in main_events],
    ):
        changed.append(EXECUTIONLOG_PATH.as_posix())

    # Archives: write only if needed (overflow) or if archive files already exist.
    if archived_events or ARCHIVE_CHANGELOG_PATH.exists() or ARCHIVE_EXECUTIONLOG_PATH.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

        if _write_index(
            ARCHIVE_CHANGELOG_PATH,
            "CHANGELOG (ARCHIVE)",
            marker,
            [changelog_line(e) for e in archived_events],
        ):
            changed.append(ARCHIVE_CHANGELOG_PATH.as_posix())

        if _write_index(
            ARCHIVE_EXECUTIONLOG_PATH,
            "EXECUTIONLOG (ARCHIVE)",
            marker,
            [executionlog_line(e) for e in archived_events],
        ):
            changed.append(ARCHIVE_EXECUTIONLOG_PATH.as_posix())

    out = {
        "status": "ok",
        "events_total": len(events),
        "main_events": len(main_events),
        "archived_events": len(archived_events),
        "changed_files": changed,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        out = {"status": "runtime_error", "error": str(e)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        raise SystemExit(3)
