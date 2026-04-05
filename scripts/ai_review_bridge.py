#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_text(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def normalize_severity(sev: str) -> str:
    sev = (sev or "").strip().lower()
    allowed = ["critical", "high", "medium", "low"]
    return sev if sev in allowed else "medium"


def extract_model_text(resp: Dict[str, Any]) -> str:
    for cand in resp.get("candidates", []):
        content = cand.get("content", {})
        for part in content.get("parts", []):
            if isinstance(part, dict) and "text" in part:
                return part["text"]
    return ""


def parse_model_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        # remove fenced code block if model ignored instructions
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def build_changed_line_index(files_payload: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for f in files_payload:
        path = f["filename"]
        patch = f.get("patch") or ""
        changed_new_lines = set()
        position_map = {}
        new_line = None
        pos = 0
        for raw in patch.splitlines():
            if raw.startswith("@@"):
                # @@ -a,b +c,d @@
                try:
                    plus = raw.split("+", 1)[1].split(" ", 1)[0]
                    start = plus.split(",", 1)[0]
                    new_line = int(start)
                except Exception:
                    new_line = None
                continue
            pos += 1
            if new_line is None:
                continue
            if raw.startswith("+") and not raw.startswith("+++"):
                changed_new_lines.add(new_line)
                position_map[new_line] = pos
                new_line += 1
            elif raw.startswith("-") and not raw.startswith("---"):
                continue
            else:
                position_map.setdefault(new_line, pos)
                new_line += 1
        index[path] = {
            "changed_new_lines": changed_new_lines,
            "position_map": position_map,
        }
    return index


def severity_rank(sev: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(sev, 0)


def load_config(path: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        print("PyYAML is required", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def filter_findings(findings: List[Dict[str, Any]], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    allowed = set(cfg["review"].get("allowed_severities", []))
    min_sev = cfg["review"].get("min_severity_to_publish", "medium")
    threshold = severity_rank(min_sev)
    out = []
    for f in findings:
        sev = normalize_severity(f.get("severity", "medium"))
        if sev not in allowed:
            continue
        if severity_rank(sev) < threshold:
            continue
        f["severity"] = sev
        out.append(f)
    max_comments = int(cfg["review"].get("max_comments", 6))
    out.sort(key=lambda x: severity_rank(x["severity"]), reverse=True)
    return out[:max_comments]


def build_inline_comments(findings: List[Dict[str, Any]], diff_index: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    inline = []
    residual = []
    seen = set()
    for f in findings:
        path = f.get("path")
        line = f.get("line")
        key = (path, line, f.get("title"), f.get("body"))
        if key in seen:
            continue
        seen.add(key)
        if not path or path not in diff_index:
            residual.append(f)
            continue
        if not isinstance(line, int):
            residual.append(f)
            continue
        file_info = diff_index[path]
        if line not in file_info["changed_new_lines"]:
            residual.append(f)
            continue
        body = f"[{f['severity'].upper()}] {f.get('title','Achado')}\n\n{f.get('body','').strip()}"
        suggestion = (f.get("suggestion") or "").strip()
        if suggestion:
            body += f"\n\nSugestão:\n```suggestion\n{suggestion}\n```"
        inline.append({
            "path": path,
            "line": line,
            "side": "RIGHT",
            "body": body,
        })
    return inline, residual


def build_summary(verdict: str, summary: str, residual: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("## Veredito")
    lines.append(verdict or "COMMENT")
    lines.append("")
    lines.append("## Resumo")
    lines.append(summary or "Sem resumo fornecido pelo modelo.")
    lines.append("")
    lines.append("## Achados não ancorados inline")
    if not residual:
        lines.append("Nenhum.")
    else:
        for f in residual:
            sev = f.get("severity", "medium").upper()
            path = f.get("path", "(sem path)")
            title = f.get("title", "Achado")
            body = f.get("body", "")
            lines.append(f"- [{sev}] `{path}` — **{title}**")
            if body:
                lines.append(f"  - {body}")
    lines.append("")
    lines.append("_Review automático advisory via Gemini; não substitui os gates oficiais do HB Track._")
    return "\n".join(lines) + "\n"


def main() -> None:
    cfg = load_config(os.environ.get("AI_REVIEW_CONFIG", ".github/ai-review/config.yaml"))
    model_resp = load_json(os.environ.get("AI_REVIEW_MODEL_RESPONSE", "gemini_response.json"))
    pr_files = load_json(os.environ.get("AI_REVIEW_PR_FILES", "pr_files.json"))

    raw_text = extract_model_text(model_resp)
    parsed = parse_model_json(raw_text)

    findings = parsed.get("findings", [])
    findings = findings if isinstance(findings, list) else []
    findings = filter_findings(findings, cfg)

    diff_index = build_changed_line_index(pr_files)
    inline, residual = build_inline_comments(findings, diff_index)
    summary = build_summary(parsed.get("verdict", "COMMENT"), parsed.get("summary", ""), residual)

    output_json_path = cfg.get("bridge", {}).get("output_json_path", "ai_review_findings.json")
    summary_md_path = cfg.get("bridge", {}).get("summary_markdown_path", "ai_review_summary.md")

    save_text(summary_md_path, summary)
    Path(output_json_path).write_text(
        json.dumps({"comments": inline}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"inline_comments={len(inline)}")
    print(f"residual_findings={len(residual)}")


if __name__ == "__main__":
    main()
