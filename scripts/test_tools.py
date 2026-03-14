#!/usr/bin/env python3
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "contracts/validate"))
from validate_contracts import _try_tool

print("Testing node...")
rc, out, err = _try_tool("node", "--version")
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

print("\nTesting redocly...")
rc, out, err = _try_tool("redocly", "--version")
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

print("\nTesting spectral...")
rc, out, err = _try_tool("spectral", "--version")
print(f"  RC={rc}, OUT={out.strip()}, ERR={err.strip()}")

print("\nTesting asyncapi...")
rc, out, err = _try_tool("asyncapi", "--version")
print(f"  RC={rc}, OUT={out.strip()[:100]}, ERR={err.strip()[:100]}")
