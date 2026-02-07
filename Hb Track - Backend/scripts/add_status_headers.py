#!/usr/bin/env python3
"""
Add STATUS headers to all .md files in docs/

This script adds a STATUS comment header to the top of all markdown files
in the docs/ directory based on the rules defined in docs-registry.md.

Features:
- Idempotent: won't duplicate headers if already present
- Preserves BOM if file has one
- Writes in UTF-8
- Reads notes from registry for specific files

Usage:
    python scripts/add_status_headers.py
"""
import os
import re
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

BACKEND_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = BACKEND_ROOT.parent
DOCS_DIR = WORKSPACE_ROOT / "docs"

# Files with specific notes (from registry)
NOTES_MAP = {
    # Schema/API verification notes
    'API_ANALYTICS_ENDPOINTS.md': 'verificar contra openapi.json',
    'API_CONTRACT.md': 'verificar contra openapi.json',
    'ESTRUTURA_BANCO.md': 'verificar contra schema.sql',
    'MIGRATIONS_SUMMARY.txt': 'verificar contra alembic_state',
    '01-sistema-atual/SCHEMA_CANONICO_DATABASE.md': 'verificar contra schema.sql',
    '02-modulos/teams/teams-CONTRACT.md': 'verificar contra openapi.json',
    '02-modulos/training/TRAINING_V2_API.md': 'verificar contra openapi.json',
    '02-modulos/training/training-CONTRACT.md': 'verificar contra openapi.json',
    # OpenAPI yamls
    'openapi/athletes.yaml': 'verificar contra _generated/openapi.json',
    'openapi/audit_logs.yaml': 'verificar contra _generated/openapi.json',
    'openapi/competitions.yaml': 'verificar contra _generated/openapi.json',
    'openapi/match_subresources.yaml': 'verificar contra _generated/openapi.json',
    'openapi/memberships.yaml': 'verificar contra _generated/openapi.json',
    'openapi/rbac.yaml': 'verificar contra _generated/openapi.json',
    'openapi/team_registrations.yaml': 'verificar contra _generated/openapi.json',
    'openapi/training_sessions.yaml': 'verificar contra _generated/openapi.json',
    'openapi/wellness.yaml': 'verificar contra _generated/openapi.json',
    # Other specific notes
    'README.md': 'indice principal',
}

# Duplicate index files
DUPLICATE_INDICES = ['_README.md', '_INDICE.md', '_MAPA.md', '_ESTRUTURA_DOCS.md']


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_status_and_note(rel_path: str) -> tuple[str, str]:
    """
    Determine STATUS and note for a file based on its path.

    Returns:
        tuple: (status, note)
    """
    # Normalize path separators
    rel_path = rel_path.replace('\\', '/')

    # Registry - VERIFIED
    if rel_path == '00-registry/docs-registry.md':
        return 'VERIFIED', 'evidencia: registry gerado em 2026-01-27'

    # Duplicate index files - DEPRECATED
    if rel_path in DUPLICATE_INDICES:
        return 'DEPRECATED', 'replaced by docs/README.md'

    # _archived/* - DEPRECATED
    if rel_path.startswith('_archived/'):
        return 'DEPRECATED', 'arquivado'

    # 03-implementacoes-concluidas/* - DEPRECATED
    if rel_path.startswith('03-implementacoes-concluidas/'):
        return 'DEPRECATED', 'implementacao concluida'

    # Check for specific note in map
    note = NOTES_MAP.get(rel_path, '')

    return 'NEEDS_REVIEW', note


def add_header_to_file(filepath: Path, status: str, note: str) -> bool:
    """
    Add STATUS header to a file.

    Returns:
        bool: True if file was modified, False if skipped (already has header)
    """
    # Read file as bytes to detect BOM
    with open(filepath, 'rb') as f:
        raw = f.read()

    # Detect and preserve UTF-8 BOM
    bom = b''
    if raw.startswith(b'\xef\xbb\xbf'):
        bom = b'\xef\xbb\xbf'
        raw = raw[3:]

    # Decode content
    content = raw.decode('utf-8', errors='replace')

    # IDEMPOTENCY: skip if already has STATUS header
    if content.lstrip().startswith('<!-- STATUS:'):
        return False

    # Build header
    if note:
        header = f'<!-- STATUS: {status} | {note} -->\n\n'
    else:
        header = f'<!-- STATUS: {status} -->\n\n'

    # Write back with header, preserving BOM if existed
    with open(filepath, 'wb') as f:
        f.write(bom)
        f.write(header.encode('utf-8'))
        f.write(content.encode('utf-8'))

    return True


def find_all_md_files(docs_dir: Path) -> list[Path]:
    """Find all .md files in docs directory recursively."""
    return sorted(docs_dir.rglob('*.md'))


def main():
    print(f"\n{'='*60}")
    print("Add STATUS Headers to Documentation")
    print(f"{'='*60}")
    print(f"Docs directory: {DOCS_DIR}")
    print(f"{'='*60}\n")

    if not DOCS_DIR.exists():
        print(f"[ERROR] Docs directory not found: {DOCS_DIR}")
        return 1

    # Find all .md files
    md_files = find_all_md_files(DOCS_DIR)
    print(f"Found {len(md_files)} .md files\n")

    # Process each file
    modified_count = 0
    skipped_count = 0
    stats = {'VERIFIED': 0, 'DEPRECATED': 0, 'NEEDS_REVIEW': 0}

    for filepath in md_files:
        rel_path = str(filepath.relative_to(DOCS_DIR)).replace('\\', '/')
        status, note = get_status_and_note(rel_path)

        was_modified = add_header_to_file(filepath, status, note)

        if was_modified:
            modified_count += 1
            stats[status] += 1
            note_display = f" | {note}" if note else ""
            print(f"[OK] {rel_path} -> {status}{note_display}")
        else:
            skipped_count += 1
            print(f"[SKIP] {rel_path} (already has STATUS)")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Total files found: {len(md_files)}")
    print(f"  Modified: {modified_count}")
    print(f"  Skipped (already had STATUS): {skipped_count}")
    print(f"\n  By status:")
    print(f"    VERIFIED: {stats['VERIFIED']}")
    print(f"    DEPRECATED: {stats['DEPRECATED']}")
    print(f"    NEEDS_REVIEW: {stats['NEEDS_REVIEW']}")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
