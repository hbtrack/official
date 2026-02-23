import os
import json
import sys
from pathlib import Path

def check_plans_ar_sync():
    # Use paths relative to workspace root (cwd)
    root_dir = Path.cwd()
    plans_dir = root_dir / "docs" / "_canon" / "planos"
    ars_dir = root_dir / "docs" / "hbtrack" / "ars"
    reports_dir = root_dir / "_reports" / "audit" / "PLANS_AR_SYNC"
    
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    orphan_plans = []
    total_plans = 0
    total_ars = 0
    
    # Scan plans
    if not plans_dir.exists():
        print(f"ERROR: Plans directory not found: {plans_dir}", file=sys.stderr)
        return 3
        
    plan_files = list(plans_dir.glob("*.json"))
    for plan_file in plan_files:
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
        except Exception as e:
            print(f"WARNING: Could not read {plan_file}: {e}", file=sys.stderr)
            continue
            
        # Ignore non-plan JSONs (must have 'tasks' field)
        if 'tasks' not in plan_data:
            continue
            
        total_plans += 1
        tasks = plan_data.get('tasks', [])
        if not tasks:
            continue
            
        # Check for AR for each task in the plan
        for task in tasks:
            task_id = str(task.get('id'))
            if not task_id:
                continue
                
            # Canonical match: AR_{ID}_*.md
            # Use glob to handle variable titles
            ar_pattern = f"AR_{task_id}_*.md"
            matching_ars = list(ars_dir.glob(ar_pattern))
            
            # Special case for exact AR_{ID}.md if title is missing or complex
            if not matching_ars:
                exact_ar = ars_dir / f"AR_{task_id}.md"
                if exact_ar.exists():
                    matching_ars = [exact_ar]
            
            if not matching_ars:
                orphan_plans.append({
                    "plan": str(plan_file.relative_to(root_dir)),
                    "task_id": task_id,
                    "reason": "AR materialization missing"
                })
    
    status = "PASS" if not orphan_plans else "FAIL"
    exit_code = 0 if status == "PASS" else 2
    
    # Count total ARs for metadata
    total_ars = len(list(ars_dir.glob("AR_*.md")))
    
    result = {
        "status": status,
        "orphan_plans": orphan_plans,
        "total_plans": total_plans,
        "total_ars": total_ars
    }
    
    with open(reports_dir / "result.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        
    if status == "FAIL":
        print(f"VIOLATION: Found {len(orphan_plans)} orphan plan tasks without ARs.", file=sys.stderr)
        for orphan in orphan_plans:
            print(f"  - Plan: {orphan['plan']} | Task ID: {orphan['task_id']}", file=sys.stderr)
            
    return exit_code

if __name__ == "__main__":
    sys.exit(check_plans_ar_sync())
