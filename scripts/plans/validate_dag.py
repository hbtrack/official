#!/usr/bin/env python3
"""
Plan DAG Validator
===================
Validates execution order for Plans with dependencies.
Prevents circular dependencies and ensures correct execution sequence.

Usage:
    # Validate DAG file
    python scripts/validate_dag.py docs/plans/fase-5-3-dag.yaml
    
    # Get execution order
    python scripts/validate_dag.py docs/plans/fase-5-3-dag.yaml --order
    
    # Check if a specific Plan can be executed now
    python scripts/validate_dag.py docs/plans/fase-5-3-dag.yaml --can-execute FASE-5-3-B

DAG file format (YAML):
    plans:
      - id: FASE-5-3-A
        depends_on: []
        provides: [model_x, service_y]
      
      - id: FASE-5-3-B
        depends_on: [FASE-5-3-A]
        provides: [router_z]
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict, deque

try:
    from . import config
except ImportError:
    import config

IMPLEMENTED_DIR = config.IMPLEMENTED_DIR


class DAGError(Exception):
    """DAG validation error."""
    pass


class PlanDAG:
    """Represents a DAG of Plan dependencies."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.plans = []
        self.graph = defaultdict(list)  # id -> [dependencies]
        self.reverse_graph = defaultdict(list)  # id -> [dependents]
        self.provides_map = {}  # id -> [artifacts provided]
        
        self._load_config()
        self._build_graph()
    
    def _load_config(self):
        """Load and validate YAML config."""
        if not self.config_path.exists():
            raise DAGError(f"DAG file not found: {self.config_path}")
        
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        
        if "plans" not in data:
            raise DAGError("DAG file must contain 'plans' key")
        
        self.plans = data["plans"]
        
        # Validate structure
        for plan in self.plans:
            if "id" not in plan:
                raise DAGError(f"Plan missing 'id': {plan}")
            if "depends_on" not in plan:
                plan["depends_on"] = []
            if "provides" not in plan:
                plan["provides"] = []
    
    def _build_graph(self):
        """Build dependency graph."""
        plan_ids = {p["id"] for p in self.plans}
        
        for plan in self.plans:
            plan_id = plan["id"]
            deps = plan["depends_on"]
            
            # Validate dependencies exist
            for dep in deps:
                if dep not in plan_ids:
                    raise DAGError(
                        f"Plan {plan_id} depends on unknown Plan: {dep}"
                    )
            
            self.graph[plan_id] = deps
            self.provides_map[plan_id] = plan["provides"]
            
            # Build reverse graph (for finding dependents)
            for dep in deps:
                self.reverse_graph[dep].append(plan_id)
    
    def detect_cycles(self) -> Optional[List[str]]:
        """Detect cycles using DFS. Returns cycle path if found."""
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.reverse_graph[node]:
                if neighbor not in visited:
                    cycle = dfs(neighbor, path[:])
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        for node in self.graph:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    return cycle
        
        return None
    
    def topological_sort(self) -> List[str]:
        """Return Plans in valid execution order (topological sort)."""
        # Kahn's algorithm
        in_degree = {plan_id: len(deps) for plan_id, deps in self.graph.items()}
        queue = deque([plan_id for plan_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Reduce in-degree for dependents
            for dependent in self.reverse_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.graph):
            raise DAGError("Topological sort failed — cycle detected")
        
        return result
    
    def can_execute(self, plan_id: str, executed_plans: Set[str]) -> tuple[bool, List[str]]:
        """Check if a Plan can be executed given already-executed Plans.
        
        Returns (can_execute, missing_dependencies).
        """
        if plan_id not in self.graph:
            raise DAGError(f"Unknown Plan ID: {plan_id}")
        
        deps = self.graph[plan_id]
        missing = [d for d in deps if d not in executed_plans]
        
        return (len(missing) == 0, missing)
    
    def get_execution_order(self) -> List[Dict]:
        """Get execution order with metadata."""
        order = self.topological_sort()
        result = []
        
        for i, plan_id in enumerate(order):
            plan = next(p for p in self.plans if p["id"] == plan_id)
            result.append({
                "order": i + 1,
                "id": plan_id,
                "depends_on": plan["depends_on"],
                "provides": plan["provides"],
                "can_parallel": self._can_run_parallel(plan_id, order[:i])
            })
        
        return result
    
    def _can_run_parallel(self, plan_id: str, already_ordered: List[str]) -> List[str]:
        """Find Plans that can run in parallel with this one."""
        parallel = []
        plan_deps = set(self.graph[plan_id])
        
        for other_id in self.graph:
            if other_id == plan_id:
                continue
            if other_id in already_ordered:
                continue
            
            other_deps = set(self.graph[other_id])
            
            # Can run in parallel if:
            # 1. Neither depends on the other
            # 2. Both have their dependencies satisfied by already_ordered
            if (plan_id not in other_deps and 
                other_id not in plan_deps and
                other_deps.issubset(set(already_ordered))):
                parallel.append(other_id)
        
        return parallel


def print_execution_order(dag: PlanDAG):
    """Print execution order with details."""
    order = dag.get_execution_order()
    
    print("=" * 80)
    print("EXECUTION ORDER")
    print("=" * 80)
    print()
    
    for item in order:
        print(f"{item['order']}. {item['id']}")
        
        if item['depends_on']:
            print(f"   Depends on: {', '.join(item['depends_on'])}")
        else:
            print(f"   Depends on: (none — can execute immediately)")
        
        if item['provides']:
            print(f"   Provides: {', '.join(item['provides'])}")
        
        if item['can_parallel']:
            print(f"   Can run in parallel with: {', '.join(item['can_parallel'])}")
        
        print()


def check_can_execute(dag: PlanDAG, plan_id: str):
    """Check if a Plan can be executed now."""
    # Get list of executed Plans from docs/implemented/
    executed = set()
    
    if IMPLEMENTED_DIR.exists():
        for plan_file in IMPLEMENTED_DIR.glob("*.md"):
            # Extract TASK-ID from filename or content
            executed.add(plan_file.stem)
    
    can_exec, missing = dag.can_execute(plan_id, executed)
    
    print("=" * 80)
    print(f"CAN EXECUTE: {plan_id}?")
    print("=" * 80)
    print()
    
    if can_exec:
        print(f"✅ YES — {plan_id} can be executed now")
        print()
        print("All dependencies satisfied:")
        for dep in dag.graph[plan_id]:
            print(f"  ✓ {dep}")
    else:
        print(f"❌ NO — {plan_id} cannot be executed yet")
        print()
        print("Missing dependencies:")
        for dep in missing:
            print(f"  ✗ {dep} (not in docs/implemented/)")
        print()
        print("Execute these Plans first:")
        for dep in missing:
            print(f"  python scripts/executor_workflow.py docs/plans/{dep}.md")


def validate_dag(dag: PlanDAG):
    """Validate DAG and report issues."""
    print("=" * 80)
    print(f"VALIDATING DAG: {dag.config_path}")
    print("=" * 80)
    print()
    
    # Check for cycles
    cycle = dag.detect_cycles()
    if cycle:
        print("❌ CYCLE DETECTED:")
        print("   " + " → ".join(cycle))
        print()
        print("Action required: Break the cycle by:")
        print("  1. Removing a dependency, OR")
        print("  2. Splitting a Plan into smaller Plans")
        sys.exit(1)
    
    print(f"✅ No cycles detected ({len(dag.plans)} Plans)")
    print()
    
    # Validate provides/depends relationships
    all_provides = set()
    for plan in dag.plans:
        all_provides.update(plan["provides"])
    
    unmet_needs = []
    for plan in dag.plans:
        for dep_id in plan["depends_on"]:
            dep_plan = next(p for p in dag.plans if p["id"] == dep_id)
            # Check what the dependency provides
            if not dep_plan["provides"]:
                unmet_needs.append(
                    f"{plan['id']} depends on {dep_id}, but {dep_id} doesn't provide anything"
                )
    
    if unmet_needs:
        print("⚠️  WARNINGS:")
        for warning in unmet_needs:
            print(f"  {warning}")
        print()
    
    print(f"✅ DAG is valid — {len(dag.plans)} Plans can be executed")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/validate_dag.py <dag.yaml>                    # Validate")
        print("  python scripts/validate_dag.py <dag.yaml> --order            # Show order")
        print("  python scripts/validate_dag.py <dag.yaml> --can-execute ID  # Check Plan")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        dag = PlanDAG(config_path)
    except DAGError as e:
        print(f"❌ DAG Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading DAG: {e}")
        sys.exit(1)
    
    if "--order" in sys.argv:
        print_execution_order(dag)
    elif "--can-execute" in sys.argv:
        idx = sys.argv.index("--can-execute")
        if idx + 1 >= len(sys.argv):
            print("Error: --can-execute requires a Plan ID")
            sys.exit(1)
        plan_id = sys.argv[idx + 1]
        check_can_execute(dag, plan_id)
    else:
        validate_dag(dag)


if __name__ == "__main__":
    main()
