import pathlib
root = pathlib.Path("c:/HB TRACK")

# DOC-GATE-014: hb_watch.py tokens
t = (root / "scripts/run/hb_watch.py").read_text(encoding="utf-8")
checks_014 = [".hb_lock", "--cached", "--name-only", "docs/hbtrack/_INDEX.md", "_reports/dispatch"]
print("=== DOC-GATE-014: hb_watch.py ===")
for c in checks_014:
    print(f"  {repr(c)}: {'PRESENTE' if c in t else 'AUSENTE'}")

# DOC-GATE-015: Dev Flow.md tokens
df = (root / "docs/_canon/contratos/Dev Flow.md").read_text(encoding="utf-8")
checks_015 = ["hb_watch.py", "_reports/dispatch", "hb seal", "último gate", "evidence", "STAGED"]
print("\n=== DOC-GATE-015: Dev Flow.md ===")
for c in checks_015:
    print(f"  {repr(c)}: {'PRESENTE' if c in df else 'AUSENTE'}")
