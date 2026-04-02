from __future__ import annotations

import os
import pathlib
import subprocess
import sys
from urllib.error import HTTPError, URLError

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from common import (  # noqa: E402
    broker_has_pacticipant,
    format_called_process_error,
    repo_root,
    resolve_broker_auth_args,
    resolve_branch,
    resolve_executable,
    resolve_version,
    run_checked,
)


def build_verify_command(root: pathlib.Path, env: dict[str, str]) -> list[str]:
    broker_url = env.get("PACT_BROKER_BASE_URL", "").strip()
    if not broker_url:
        raise RuntimeError("PACT_BROKER_BASE_URL is required to verify provider pacts.")

    provider_base_url = (
        env.get("PACT_PROVIDER_BASE_URL", "").strip()
        or env.get("HB_STAGING_URL", "").strip()
    )
    if not provider_base_url:
        raise RuntimeError("PACT_PROVIDER_BASE_URL or HB_STAGING_URL is required.")

    verifier = resolve_executable(
        ["pact-provider-verifier"],
        root / "pact" / "bin" / "pact-provider-verifier",
    )
    provider_name = env.get("PACT_PROVIDER_NAME", "hbtrack-api").strip() or "hbtrack-api"
    provider_version = resolve_version(env, "PROVIDER_APP_VERSION", cwd=root)
    provider_branch = resolve_branch(env, "PROVIDER_VERSION_BRANCH", cwd=root)

    cmd = [
        verifier,
        "--pact-broker-base-url",
        broker_url,
        "--provider",
        provider_name,
        "--provider-base-url",
        provider_base_url,
        "--publish-verification-results",
        "--provider-app-version",
        provider_version,
        "--enable-pending",
        "--wait",
        "30",
    ]
    if provider_branch:
        cmd.extend(["--provider-version-branch", provider_branch])
    cmd.extend(resolve_broker_auth_args(env, broker_url))
    return cmd


def main() -> int:
    root = repo_root()
    env = dict(os.environ)
    broker_url = env.get("PACT_BROKER_BASE_URL", "").strip()
    if not broker_url:
        raise RuntimeError("PACT_BROKER_BASE_URL is required to verify provider pacts.")

    try:
        has_pacticipant = broker_has_pacticipant(broker_url, "hbtrack-app", env=env)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError(
                "Pact Broker requires authentication. Configure PACT_BROKER_TOKEN "
                "or PACT_BROKER_USERNAME/PACT_BROKER_PASSWORD before verifying the provider."
            ) from exc
        raise RuntimeError(f"Failed to query Pact Broker: HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to reach Pact Broker at {broker_url}: {exc.reason}") from exc

    if not has_pacticipant:
        print(
            "SKIP: Pact Broker configurado, mas `hbtrack-app` ainda não publicou o primeiro pact.",
            file=sys.stderr,
        )
        return 0

    run_checked(build_verify_command(root, env), cwd=root)
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
