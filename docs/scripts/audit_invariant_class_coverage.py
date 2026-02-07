#!/usr/bin/env python3
"""
Auditoria de cobertura de invariantes por classe.

Usa o InvariantsParser real para analisar INVARIANTS_TRAINING.md
e gerar relatório detalhado de cobertura por classe.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from verify_invariants_tests.py
try:
    from verify_invariants_tests import InvariantsParser, ALLOWED_CLASSES, IMPLEMENTED_CLASSES
except ImportError:
    print("ERROR: Could not import from verify_invariants_tests.py")
    sys.exit(1)


def audit_class_coverage(md_path: Path, output_dir: Path):
    """
    Audita cobertura de invariantes por classe.
    
    Args:
        md_path: Path to INVARIANTS_TRAINING.md
        output_dir: Directory for output reports
    """
    
    # Parse invariants
    parser = InvariantsParser()
    invariants, spec_violations = parser.parse(md_path, strict_spec=False)
    
    if spec_violations:
        print(f"WARNING: {len(spec_violations)} SPEC violations found during parsing")
    
    # Import class taxonomy from verifier
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from verify_invariants_tests import ALLOWED_CLASSES, IMPLEMENTED_CLASSES
    
    # Statistics
    stats = {
        'total_invariants': len(invariants),
        'by_status': defaultdict(int),
        'by_class': defaultdict(int),
        'test_required': 0,
        'test_optional': 0,
        'classes_without_validator': set()
    }
    
    # Inventory by class
    inventory = defaultdict(list)
    
    # Process each invariant
    for inv in invariants:
        # Status
        stats['by_status'][inv.status] += 1
        
        # Test required
        if inv.test_required:
            stats['test_required'] += 1
        else:
            stats['test_optional'] += 1
        
        # Classes
        for unit in inv.units:
            class_type = unit.class_type
            stats['by_class'][class_type] += 1
            
            # Check if class has validator
            if class_type not in IMPLEMENTED_CLASSES and class_type != 'UNKNOWN':
                stats['classes_without_validator'].add(class_type)
            
            # Add to inventory
            inventory[class_type].append({
                'id': inv.id,
                'status': inv.status,
                'test_required': inv.test_required,
                'tests_primary': inv.tests.get('primary') if inv.tests else None,
                'tests_node': inv.tests.get('node') if inv.tests else None,
                'unit_key': unit.unit_key,
                'unit_required': unit.required,
                'description': unit.description
            })
    
    # Generate text report
    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("INVARIANTS CLASS COVERAGE AUDIT")
    txt_lines.append("=" * 80)
    txt_lines.append(f"Generated: {datetime.now().isoformat()}")
    txt_lines.append(f"Source: {md_path}")
    txt_lines.append("")
    
    # Summary
    txt_lines.append("SUMMARY")
    txt_lines.append("-" * 80)
    txt_lines.append(f"Total invariants: {stats['total_invariants']}")
    txt_lines.append(f"Test required: {stats['test_required']}")
    txt_lines.append(f"Test optional: {stats['test_optional']}")
    txt_lines.append("")
    
    txt_lines.append("By Status:")
    for status in sorted(stats['by_status'].keys()):
        count = stats['by_status'][status]
        txt_lines.append(f"  {status:20s}: {count:3d}")
    txt_lines.append("")
    
    txt_lines.append("By Class:")
    for class_type in sorted(stats['by_class'].keys()):
        count = stats['by_class'][class_type]
        validator_status = "[YES]" if class_type in IMPLEMENTED_CLASSES else "[NO]"
        txt_lines.append(f"  {class_type:20s}: {count:3d}  {validator_status}")
    txt_lines.append("")
    
    if stats['classes_without_validator']:
        txt_lines.append("CLASSES WITHOUT VALIDATOR:")
        for class_type in sorted(stats['classes_without_validator']):
            txt_lines.append(f"  - {class_type}")
        txt_lines.append("")
    
    # Detailed inventory by class
    txt_lines.append("=" * 80)
    txt_lines.append("DETAILED INVENTORY BY CLASS")
    txt_lines.append("=" * 80)
    txt_lines.append("")
    
    for class_type in sorted(inventory.keys()):
        invs = inventory[class_type]
        txt_lines.append(f"CLASS {class_type} ({len(invs)} invariants)")
        txt_lines.append("-" * 80)
        
        validator_status = "[YES]" if class_type in IMPLEMENTED_CLASSES else "[NO]"
        txt_lines.append(f"Validator status: {validator_status}")
        txt_lines.append("")
        
        for item in invs:
            txt_lines.append(f"  {item['id']:20s} | Status: {item['status']:12s} | Test: {item['test_required']}")
            txt_lines.append(f"    Primary: {item['tests_primary']}")
            txt_lines.append(f"    Node:    {item['tests_node']}")
            if item['description']:
                txt_lines.append(f"    Desc:    {item['description'][:60]}...")
            txt_lines.append("")
        
        txt_lines.append("")
    
    # Write text report
    txt_path = output_dir / "class_coverage_matrix.txt"
    txt_path.write_text("\n".join(txt_lines), encoding='utf-8')
    print(f"[OK] Text report written to: {txt_path}")
    
    # Generate JSON report
    json_data = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'source': str(md_path),
            'total_invariants': stats['total_invariants']
        },
        'summary': {
            'by_status': dict(stats['by_status']),
            'by_class': dict(stats['by_class']),
            'test_required': stats['test_required'],
            'test_optional': stats['test_optional']
        },
        'supported_classes': sorted(list(IMPLEMENTED_CLASSES)),
        'classes_without_validator': sorted(list(stats['classes_without_validator'])),
        'inventory': {class_type: invs for class_type, invs in inventory.items()}
    }
    
    json_path = output_dir / "class_coverage_matrix.json"
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"[OK] JSON report written to: {json_path}")
    
    return stats, inventory


def main():
    """Main entry point"""
    
    # Paths
    root = Path(r"C:\HB TRACK")
    md_path = root / "docs" / "02-modulos" / "training" / "INVARIANTS_TRAINING.md"
    output_dir = root / "docs" / "_generated" / "_reports"
    
    # Validate paths
    if not md_path.exists():
        print(f"ERROR: INVARIANTS_TRAINING.md not found at {md_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("INVARIANTS CLASS COVERAGE AUDIT")
    print("=" * 80)
    print(f"Source: {md_path}")
    print(f"Output: {output_dir}")
    print("")
    
    # Run audit
    stats, inventory = audit_class_coverage(md_path, output_dir)
    
    print("")
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"Total invariants analyzed: {stats['total_invariants']}")
    print(f"Classes found: {len(stats['by_class'])}")
    print(f"Classes without validator: {len(stats['classes_without_validator'])}")
    
    if stats['classes_without_validator']:
        print("")
        print("WARNING: The following classes have no validator:")
        for class_type in sorted(stats['classes_without_validator']):
            print(f"  - {class_type}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
