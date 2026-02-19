#!/usr/bin/env python3
"""Insert VPS .py-only policy into MANUAL_CANONICO_DETERMINISMO.md"""

from pathlib import Path

manual_path = Path("docs/_canon/MANUAL_CANONICO_DETERMINISMO.md")

# Read with UTF-8
text = manual_path.read_text(encoding="utf-8", errors="replace")

# Check if already inserted
if "0.3.1 Politica VPS" in text:
    print("INFO: 0.3.1 Politica VPS already exists in manual")
else:
    # Policy text to insert
    policy_text = """
0.3.1 Politica VPS (PY-ONLY)

Na VPS, somente scripts Python (.py) sao implantados/executados.
Wrappers locais (.ps1/.sh) MAY existir para desenvolvimento local, mas MUST NOT ser requisito de operacao na VPS.
"""
    
    # Find insertion point
    marker = "0.3 Automacao/infra"
    idx = text.find(marker)
    
    if idx == -1:
        # Marker not found, append at end
        text = text + "\n" + policy_text
        print("INFO: Marker '0.3 Automacao/infra' not found, appending at end")
    else:
        # Find end of 0.3 section
        end_idx = idx + len(marker)
        # Find next newline to insert after section heading
        next_newline = text.find("\n\n", end_idx)
        if next_newline == -1:
            next_newline = len(text)
        else:
            next_newline += 2  # Include both newlines
        
        # Insert policy after 0.3 section
        text = text[:next_newline] + policy_text + text[next_newline:]
        print("INFO: Inserted after section 0.3")
    
    # Write back with UTF-8
    manual_path.write_text(text, encoding="utf-8", newline="\n")
    print("OK: inserted 0.3.1 (utf-8)")
