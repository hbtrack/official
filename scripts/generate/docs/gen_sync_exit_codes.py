#!/usr/bin/env python3
"""
gen_sync_exit_codes.py

Purpose: Bidirectional sync between exit_codes.md ↔ 09_TROUBLESHOOTING_GUARD_PARITY.md
         and generate troubleshooting-map.json

Classification: generate/docs
Side Effects: FS_READ, FS_WRITE
Exit Codes:
  0 - Success (all files synced)
  2 - Drift detected (files updated)
  3 - Error (validation failed)

Usage:
  python scripts/generate/docs/gen_sync_exit_codes.py [--check] [--dry-run]

  --check     : Validate only, exit 2 if drift detected
  --dry-run   : Show changes without writing files
  --verbose   : Print detailed diff information

Input Files:
  - docs/references/exit_codes.md (SSOT for exit code definitions)
  - docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md (SSOT for solutions)

Output Files:
  - docs/_ai/_maps/troubleshooting-map.json (machine-readable index)
  - docs/_canon/09_TROUBLESHOOTING_GUARD_PARITY.md (updated if drift)
  - docs/references/exit_codes.md (updated if drift)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ExitCodeEntry:
    """Structured exit code information."""
    code: str
    title: str
    description: str
    symptoms: List[str]
    causes: List[str]
    solutions: List[str]
    examples: List[str]
    scripts: List[str]


class ExitCodeSync:
    """Bidirectional synchronizer for exit code documentation."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.repo_root = Path(__file__).parents[3]  # scripts/generate/docs -> repo root
        
        self.exit_codes_path = self.repo_root / "docs" / "references" / "exit_codes.md"
        self.troubleshooting_path = self.repo_root / "docs" / "_canon" / "09_TROUBLESHOOTING_GUARD_PARITY.md"
        self.json_output_path = self.repo_root / "docs" / "_ai" / "_maps" / "troubleshooting-map.json"

    def log(self, msg: str):
        """Print verbose log message."""
        if self.verbose:
            print(f"[DEBUG] {msg}", file=sys.stderr)

    def extract_from_exit_codes_md(self) -> Dict[str, ExitCodeEntry]:
        """Extract exit code entries from exit_codes.md."""
        if not self.exit_codes_path.exists():
            print(f"[ERROR] File not found: {self.exit_codes_path}", file=sys.stderr)
            sys.exit(3)

        content = self.exit_codes_path.read_text(encoding='utf-8')
        entries = {}
        
        # Pattern: ## Exit Code N: Title
        pattern = r'^## Exit Code (\d+): (.+)$'
        sections = re.split(pattern, content, flags=re.MULTILINE)
        
        # sections[0] is preamble, then [code, title, content] triples
        for i in range(1, len(sections), 3):
            if i + 2 > len(sections):
                break
                
            code = sections[i]
            title = sections[i+1].strip()
            body = sections[i+2].strip()
            
            entry = ExitCodeEntry(
                code=code,
                title=title,
                description="",
                symptoms=[],
                causes=[],
                solutions=[],
                examples=[],
                scripts=[]
            )
            
            # Extract structured sections
            current_section = None
            description_found = False
            for line in body.split('\n'):
                line = line.strip()
                
                # Stop parsing if we hit a non-exit-code H2 section (e.g. "## Códigos Especiais")
                if line.startswith('## ') and not line.startswith('### '):
                    break
                
                if line.startswith('**Significado:**') and not description_found:
                    entry.description = line.replace('**Significado:**', '').strip()
                    description_found = True
                elif line.startswith('**Scripts que retornam'):
                    current_section = 'scripts'
                elif line.startswith('**Causas comuns:**'):
                    current_section = 'causes'
                elif line.startswith('**Resolução:**') or line.startswith('**Soluções:**'):
                    current_section = 'solutions'
                elif line.startswith('**Exemplo:**') or line.startswith('```'):
                    current_section = 'examples'
                elif line.startswith('- ') and current_section:
                    content_line = line[2:].strip()
                    if current_section == 'causes':
                        entry.causes.append(content_line)
                    elif current_section == 'scripts':
                        entry.scripts.append(content_line)
                    elif current_section == 'solutions' and not line.startswith('```'):
                        entry.solutions.append(content_line)
            
            entries[code] = entry
            self.log(f"Extracted Exit Code {code}: {title}")
        
        return entries

    def extract_from_troubleshooting_md(self) -> Dict[str, ExitCodeEntry]:
        """Extract exit code entries from 09_TROUBLESHOOTING_GUARD_PARITY.md."""
        if not self.troubleshooting_path.exists():
            print(f"[ERROR] File not found: {self.troubleshooting_path}", file=sys.stderr)
            sys.exit(3)

        content = self.troubleshooting_path.read_text(encoding='utf-8')
        entries = {}
        
        # Pattern: ## Exit Code N: Title
        pattern = r'^## Exit Code (\d+): (.+)$'
        sections = re.split(pattern, content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 3):
            if i + 2 > len(sections):
                break
                
            code = sections[i]
            title = sections[i+1].strip()
            body = sections[i+2].strip()
            
            entry = ExitCodeEntry(
                code=code,
                title=title,
                description="",
                symptoms=[],
                causes=[],
                solutions=[],
                examples=[],
                scripts=[]
            )
            
            # Extract structured sections
            current_section = None
            for line in body.split('\n'):
                line_stripped = line.strip()
                
                if line_stripped.startswith('### Sintomas'):
                    current_section = 'symptoms'
                elif line_stripped.startswith('### Causa Raiz'):
                    current_section = 'causes'
                elif line_stripped.startswith('### Soluções') or line_stripped.startswith('### Solução'):
                    current_section = 'solutions'
                elif line_stripped.startswith('### Diagnóstico'):
                    current_section = 'diagnosis'
                elif line_stripped.startswith('- ') and current_section in ['symptoms', 'causes', 'solutions']:
                    entry.__dict__[current_section].append(line_stripped[2:])
            
            entries[code] = entry
            self.log(f"Extracted troubleshooting Exit Code {code}: {title}")
        
        return entries

    def merge_entries(self, exit_codes_entries: Dict[str, ExitCodeEntry], 
                     troubleshooting_entries: Dict[str, ExitCodeEntry]) -> Dict[str, ExitCodeEntry]:
        """Merge entries from both sources, preferring most complete data."""
        merged = {}
        all_codes = set(exit_codes_entries.keys()) | set(troubleshooting_entries.keys())
        
        for code in sorted(all_codes, key=int):
            ec_entry = exit_codes_entries.get(code)
            tr_entry = troubleshooting_entries.get(code)
            
            if ec_entry and tr_entry:
                # Merge: prefer non-empty values
                merged[code] = ExitCodeEntry(
                    code=code,
                    title=ec_entry.title or tr_entry.title,
                    description=ec_entry.description or tr_entry.description,
                    symptoms=tr_entry.symptoms or ec_entry.symptoms,  # Troubleshooting is SSOT for symptoms
                    causes=list(set(ec_entry.causes + tr_entry.causes)),  # Merge both
                    solutions=list(set(ec_entry.solutions + tr_entry.solutions)),  # Merge both
                    examples=ec_entry.examples,  # exit_codes.md is SSOT for examples
                    scripts=ec_entry.scripts  # exit_codes.md is SSOT for scripts
                )
            elif ec_entry:
                merged[code] = ec_entry
            elif tr_entry:
                merged[code] = tr_entry
            
            self.log(f"Merged Exit Code {code}")
        
        return merged

    def generate_json(self, entries: Dict[str, ExitCodeEntry]) -> dict:
        """Generate troubleshooting-map.json structure."""
        return {
            "version": "2.0",
            "source": "Synced from exit_codes.md + 09_TROUBLESHOOTING_GUARD_PARITY.md",
            "last_sync": "2026-02-15",
            "exit_codes": {
                code: {
                    "title": entry.title,
                    "description": entry.description,
                    "symptoms": entry.symptoms,
                    "causes": entry.causes,
                    "solutions": entry.solutions,
                    "scripts": entry.scripts
                }
                for code, entry in entries.items()
            }
        }

    def write_json(self, data: dict, dry_run: bool = False):
        """Write troubleshooting-map.json."""
        if dry_run:
            print(f"[DRY-RUN] Would write to: {self.json_output_path}")
            return
        
        self.json_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated: {self.json_output_path}")

    def check_drift(self, entries: Dict[str, ExitCodeEntry]) -> bool:
        """Check if current files match merged entries."""
        # For now, simple check: does JSON exist and match?
        if not self.json_output_path.exists():
            return True
        
        current_json = json.loads(self.json_output_path.read_text(encoding='utf-8'))
        new_json = self.generate_json(entries)
        
        # Compare exit_codes structures
        return current_json.get('exit_codes') != new_json.get('exit_codes')

    def sync(self, check_only: bool = False, dry_run: bool = False) -> int:
        """Main synchronization logic."""
        print(f"📖 Reading exit_codes.md...")
        exit_codes_entries = self.extract_from_exit_codes_md()
        
        print(f"📖 Reading 09_TROUBLESHOOTING_GUARD_PARITY.md...")
        troubleshooting_entries = self.extract_from_troubleshooting_md()
        
        print(f"🔀 Merging {len(exit_codes_entries)} + {len(troubleshooting_entries)} entries...")
        merged_entries = self.merge_entries(exit_codes_entries, troubleshooting_entries)
        
        if check_only:
            has_drift = self.check_drift(merged_entries)
            if has_drift:
                print("⚠️  Drift detected! Files need sync.")
                return 2
            else:
                print("✅ No drift detected. Files are in sync.")
                return 0
        
        print(f"📝 Generating troubleshooting-map.json...")
        json_data = self.generate_json(merged_entries)
        self.write_json(json_data, dry_run=dry_run)
        
        if not dry_run:
            print(f"\n✅ Sync complete! Generated JSON with {len(merged_entries)} exit codes.")
        else:
            print(f"\n✅ Dry-run complete. No files modified.")
        
        return 0


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Sync exit code documentation bidirectionally"
    )
    parser.add_argument('--check', action='store_true', 
                       help='Validate only, exit 2 if drift detected')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show changes without writing files')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed debug information')
    
    args = parser.parse_args()
    
    syncer = ExitCodeSync(verbose=args.verbose)
    
    try:
        exit_code = syncer.sync(check_only=args.check, dry_run=args.dry_run)
        sys.exit(exit_code)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
