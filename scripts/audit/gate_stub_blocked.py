from __future__ import annotations
import sys

def main() -> int:
    gate_id = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN_GATE"
    print(f"BLOCKED_INPUT: gate '{gate_id}' not implemented")
    return 4

if __name__ == "__main__":
    sys.exit(main())
