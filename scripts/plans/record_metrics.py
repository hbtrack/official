#!/usr/bin/env python3
"""
Executor Metrics Collector
============================
Tracks metrics to measure ROI of the Architect-Executor flow.

Usage:
    # Record a completed task
    python scripts/record_metrics.py FASE-5-3 \
        --plan-time 1.5 \
        --exec-time 0.5 \
        --homolog-time 0.3 \
        --bugs 0 \
        --rollbacks 0 \
        --rework 0
    
    # View metrics report
    python scripts/record_metrics.py --report
    
    # Compare with baseline (tasks done without the flow)
    python scripts/record_metrics.py --compare
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

try:
    from . import config
except ImportError:
    import config

METRICS_FILE = config.METRICS_FILE


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""
    task_id: str
    timestamp: str
    plan_time_hours: float
    exec_time_hours: float
    homolog_time_hours: float
    bugs_production: int
    rollbacks: int
    rework_hours: float
    used_flow: bool = True  # True = Architect-Executor, False = manual
    
    @property
    def total_time(self) -> float:
        return self.plan_time_hours + self.exec_time_hours + self.homolog_time_hours + self.rework_hours
    
    @property
    def quality_score(self) -> float:
        """Simple quality metric: 10 - bugs - rollbacks."""
        return max(0, 10 - self.bugs_production - self.rollbacks)


def load_metrics() -> List[TaskMetrics]:
    """Load existing metrics."""
    if not METRICS_FILE.exists():
        return []
    
    with open(METRICS_FILE) as f:
        data = json.load(f)
    
    return [TaskMetrics(**item) for item in data]


def save_metrics(metrics: List[TaskMetrics]):
    """Save metrics to file."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(METRICS_FILE, 'w') as f:
        json.dump([asdict(m) for m in metrics], f, indent=2)


def record_task(
    task_id: str,
    plan_time: float,
    exec_time: float,
    homolog_time: float,
    bugs: int,
    rollbacks: int,
    rework: float,
    used_flow: bool = True
):
    """Record metrics for a task."""
    metrics = load_metrics()
    
    # Check for duplicate
    if any(m.task_id == task_id for m in metrics):
        print(f"⚠️  Task {task_id} already recorded. Updating...")
        metrics = [m for m in metrics if m.task_id != task_id]
    
    new_metric = TaskMetrics(
        task_id=task_id,
        timestamp=datetime.now().isoformat(),
        plan_time_hours=plan_time,
        exec_time_hours=exec_time,
        homolog_time_hours=homolog_time,
        bugs_production=bugs,
        rollbacks=rollbacks,
        rework_hours=rework,
        used_flow=used_flow
    )
    
    metrics.append(new_metric)
    save_metrics(metrics)
    
    print(f"✅ Metrics recorded for {task_id}")
    print()
    print(f"Total time: {new_metric.total_time:.2f}h")
    print(f"Quality score: {new_metric.quality_score}/10")


def print_report():
    """Print metrics report."""
    metrics = load_metrics()
    
    if not metrics:
        print("No metrics recorded yet.")
        return
    
    # Separate by flow usage
    with_flow = [m for m in metrics if m.used_flow]
    without_flow = [m for m in metrics if not m.used_flow]
    
    print("=" * 80)
    print("EXECUTOR METRICS REPORT")
    print("=" * 80)
    print()
    
    if with_flow:
        print("TASKS WITH ARCHITECT-EXECUTOR FLOW:")
        print("-" * 80)
        print(f"{'Task ID':<20} {'Total':<8} {'Plan':<6} {'Exec':<6} {'QA':<6} {'Bugs':<6} {'Rollbacks':<10} {'Rework':<8}")
        print("-" * 80)
        
        total_time = 0
        total_bugs = 0
        total_rollbacks = 0
        total_rework = 0
        
        for m in with_flow:
            print(
                f"{m.task_id:<20} "
                f"{m.total_time:<8.2f} "
                f"{m.plan_time_hours:<6.2f} "
                f"{m.exec_time_hours:<6.2f} "
                f"{m.homolog_time_hours:<6.2f} "
                f"{m.bugs_production:<6} "
                f"{m.rollbacks:<10} "
                f"{m.rework_hours:<8.2f}"
            )
            total_time += m.total_time
            total_bugs += m.bugs_production
            total_rollbacks += m.rollbacks
            total_rework += m.rework_hours
        
        print("-" * 80)
        print(f"{'TOTALS':<20} {total_time:<8.2f} {'':6} {'':6} {'':6} {total_bugs:<6} {total_rollbacks:<10} {total_rework:<8.2f}")
        print()
        
        avg_time = total_time / len(with_flow)
        avg_quality = sum(m.quality_score for m in with_flow) / len(with_flow)
        
        print(f"Average time per task: {avg_time:.2f}h")
        print(f"Average quality score: {avg_quality:.1f}/10")
        print(f"Total rework: {total_rework:.2f}h ({(total_rework/total_time*100):.1f}% of total time)")
        print()
    
    if without_flow:
        print("TASKS WITHOUT FLOW (baseline):")
        print("-" * 80)
        print(f"{'Task ID':<20} {'Total':<8} {'Bugs':<6} {'Rollbacks':<10} {'Rework':<8}")
        print("-" * 80)
        
        total_time = 0
        total_bugs = 0
        total_rollbacks = 0
        total_rework = 0
        
        for m in without_flow:
            # Without flow, we only track total dev time + rework
            dev_time = m.exec_time_hours  # Store manual dev time in exec_time
            print(
                f"{m.task_id:<20} "
                f"{m.total_time:<8.2f} "
                f"{m.bugs_production:<6} "
                f"{m.rollbacks:<10} "
                f"{m.rework_hours:<8.2f}"
            )
            total_time += m.total_time
            total_bugs += m.bugs_production
            total_rollbacks += m.rollbacks
            total_rework += m.rework_hours
        
        print("-" * 80)
        print(f"{'TOTALS':<20} {total_time:<8.2f} {total_bugs:<6} {total_rollbacks:<10} {total_rework:<8.2f}")
        print()
        
        avg_time = total_time / len(without_flow)
        avg_quality = sum(m.quality_score for m in without_flow) / len(without_flow)
        
        print(f"Average time per task: {avg_time:.2f}h")
        print(f"Average quality score: {avg_quality:.1f}/10")
        print(f"Total rework: {total_rework:.2f}h ({(total_rework/total_time*100):.1f}% of total time)")
        print()


def print_comparison():
    """Compare metrics with vs without flow."""
    metrics = load_metrics()
    
    with_flow = [m for m in metrics if m.used_flow]
    without_flow = [m for m in metrics if not m.used_flow]
    
    if not with_flow or not without_flow:
        print("⚠️  Need metrics both WITH and WITHOUT flow for comparison.")
        print(f"   Tasks with flow: {len(with_flow)}")
        print(f"   Tasks without flow: {len(without_flow)}")
        return
    
    print("=" * 80)
    print("FLOW COMPARISON")
    print("=" * 80)
    print()
    
    # Calculate averages
    avg_with = {
        "time": sum(m.total_time for m in with_flow) / len(with_flow),
        "bugs": sum(m.bugs_production for m in with_flow) / len(with_flow),
        "rollbacks": sum(m.rollbacks for m in with_flow) / len(with_flow),
        "rework": sum(m.rework_hours for m in with_flow) / len(with_flow),
        "quality": sum(m.quality_score for m in with_flow) / len(with_flow),
    }
    
    avg_without = {
        "time": sum(m.total_time for m in without_flow) / len(without_flow),
        "bugs": sum(m.bugs_production for m in without_flow) / len(without_flow),
        "rollbacks": sum(m.rollbacks for m in without_flow) / len(without_flow),
        "rework": sum(m.rework_hours for m in without_flow) / len(without_flow),
        "quality": sum(m.quality_score for m in without_flow) / len(without_flow),
    }
    
    print(f"{'Metric':<20} {'With Flow':<15} {'Without Flow':<15} {'Difference':<15}")
    print("-" * 80)
    
    for metric in ["time", "bugs", "rollbacks", "rework", "quality"]:
        with_val = avg_with[metric]
        without_val = avg_without[metric]
        diff = with_val - without_val
        
        # For time, bugs, rollbacks, rework: negative is better
        # For quality: positive is better
        if metric == "quality":
            symbol = "↑" if diff > 0 else "↓"
            color = "✅" if diff > 0 else "❌"
        else:
            symbol = "↓" if diff < 0 else "↑"
            color = "✅" if diff < 0 else "❌"
        
        print(
            f"{metric.title():<20} "
            f"{with_val:<15.2f} "
            f"{without_val:<15.2f} "
            f"{color} {diff:+.2f} {symbol}"
        )
    
    print()
    print("INTERPRETATION:")
    
    if avg_with["time"] < avg_without["time"]:
        savings = avg_without["time"] - avg_with["time"]
        print(f"✅ Flow SAVES {savings:.2f}h per task on average")
    else:
        overhead = avg_with["time"] - avg_without["time"]
        print(f"⚠️  Flow ADDS {overhead:.2f}h overhead per task")
    
    if avg_with["rework"] < avg_without["rework"]:
        rework_saved = avg_without["rework"] - avg_with["rework"]
        print(f"✅ Flow REDUCES rework by {rework_saved:.2f}h per task")
    
    if avg_with["bugs"] < avg_without["bugs"]:
        print(f"✅ Flow produces {(1 - avg_with['bugs']/avg_without['bugs'])*100:.0f}% fewer bugs")
    
    if avg_with["quality"] > avg_without["quality"]:
        print(f"✅ Flow improves quality score by {avg_with['quality'] - avg_without['quality']:.1f} points")


def main():
    if "--report" in sys.argv:
        print_report()
        return
    
    if "--compare" in sys.argv:
        print_comparison()
        return
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Record task:")
        print("    python scripts/record_metrics.py TASK-ID \\")
        print("      --plan-time 1.5 --exec-time 0.5 --homolog-time 0.3 \\")
        print("      --bugs 0 --rollbacks 0 --rework 0 [--baseline]")
        print()
        print("  View report:")
        print("    python scripts/record_metrics.py --report")
        print()
        print("  Compare with/without flow:")
        print("    python scripts/record_metrics.py --compare")
        print()
        print("Options:")
        print("  --baseline    Mark this task as done WITHOUT the flow (for comparison)")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    # Parse arguments
    def get_arg(flag):
        try:
            idx = sys.argv.index(flag)
            return float(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print(f"Error: {flag} requires a numeric value")
            sys.exit(1)
    
    plan_time = get_arg("--plan-time") if "--plan-time" in sys.argv else 0
    exec_time = get_arg("--exec-time")
    homolog_time = get_arg("--homolog-time") if "--homolog-time" in sys.argv else 0
    bugs = int(get_arg("--bugs"))
    rollbacks = int(get_arg("--rollbacks"))
    rework = get_arg("--rework")
    
    used_flow = "--baseline" not in sys.argv
    
    record_task(
        task_id,
        plan_time,
        exec_time,
        homolog_time,
        bugs,
        rollbacks,
        rework,
        used_flow
    )


if __name__ == "__main__":
    main()
