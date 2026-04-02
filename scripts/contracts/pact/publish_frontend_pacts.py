from __future__ import annotations

import os
import pathlib
import subprocess
import sys

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from common import (  # noqa: E402
    format_called_process_error,
    repo_root,
    resolve_broker_auth_args,
    resolve_branch,
    resolve_executable,
    resolve_version,
    run_checked,
)


def build_publish_command(root: pathlib.Path, env: dict[str, str]) -> list[str]:
    broker_url = env.get("PACT_BROKER_BASE_URL", "").strip()
    if not broker_url:
        raise RuntimeError("PACT_BROKER_BASE_URL is required to publish consumer pacts.")

    pact_cli = resolve_executable(
        ["pact-broker", "pact-broker-cli"],
        root / "pact" / "bin" / "pact-broker",
    )
    version = resolve_version(env, "CONSUMER_APP_VERSION", cwd=root)
    branch = resolve_branch(env, "CONSUMER_VERSION_BRANCH", cwd=root)
    pacts_dir = root / "frontend" / "pacts"

    cmd = [
        pact_cli,
        "publish",
        str(pacts_dir),
        "--consumer-app-version",
        version,
        "--broker-base-url",
        broker_url,
    ]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend(resolve_broker_auth_args(env, broker_url))
    return cmd


def main() -> int:
    root = repo_root()
    frontend_dir = root / "frontend"
    pacts_dir = frontend_dir / "pacts"
    env = dict(os.environ)

    if not any(pacts_dir.glob("*.json")):
        run_checked(["npm", "run", "test:pact"], cwd=frontend_dir)

    run_checked(build_publish_command(root, env), cwd=root)
    return 0


def cli_main() -> int:
    try:
        return main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(format_called_process_error(exc), file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(cli_main())
