#!/usr/bin/env python3
import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "contracts" / "validate"))
from validate_contracts import _try_tool, _try_node_cli

print("Testing node...")
rc, out, err = _try_tool("node", "--version")
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

# Ferramentas Node.js: usar _try_node_cli para evitar resolução do binário Windows via PATH/nvm.sh
print("\nTesting redocly...")
rc, out, err = _try_node_cli(REPO_ROOT, tool="redocly", args=["--version"])
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

print("\nTesting spectral...")
rc, out, err = _try_node_cli(REPO_ROOT, tool="spectral", args=["--version"])
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

print("\nTesting asyncapi...")
rc, out, err = _try_node_cli(REPO_ROOT, tool="asyncapi", args=["--version"])
print(f"  RC={rc}, OUT={out.strip()[:100]}, ERR={err.strip()[:100]}")
