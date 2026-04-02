from __future__ import annotations

import base64
import pathlib
import shutil
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[3]


def resolve_executable(candidates: list[str], fallback: pathlib.Path) -> str:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    if fallback.exists():
        return str(fallback)
    raise RuntimeError(f"Executable not found. Tried {candidates} and fallback {fallback}.")


def resolve_git_value(args: list[str], *, cwd: pathlib.Path) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=cwd,
        text=True,
    ).strip()


def resolve_version(env: dict[str, str], env_key: str, *, cwd: pathlib.Path) -> str:
    return (
        env.get(env_key)
        or env.get("GITHUB_SHA")
        or resolve_git_value(["rev-parse", "HEAD"], cwd=cwd)
    )


def resolve_branch(env: dict[str, str], env_key: str, *, cwd: pathlib.Path) -> str:
    return (
        env.get(env_key)
        or env.get("GITHUB_REF_NAME")
        or resolve_git_value(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    )


def resolve_broker_auth_args(env: dict[str, str], broker_url: str) -> list[str]:
    username = env.get("PACT_BROKER_USERNAME", "").strip()
    password = env.get("PACT_BROKER_PASSWORD", "").strip()
    token = env.get("PACT_BROKER_TOKEN", "").strip()
    auth_mode = env.get("PACT_BROKER_AUTH_MODE", "").strip().lower()
    use_token_auth = auth_mode == "token" or "pactflow" in broker_url.lower()

    if not password and token and not use_token_auth:
        password = token
    if password and not username:
        username = "hbtrack"

    if use_token_auth and token:
        return ["--broker-token", token]
    if username and password:
        return ["--broker-username", username, "--broker-password", password]
    return []


def broker_has_pacticipant(
    broker_url: str,
    pacticipant: str,
    *,
    env: dict[str, str],
) -> bool:
    auth_args = resolve_broker_auth_args(env, broker_url)
    headers: dict[str, str] = {}

    if auth_args[:1] == ["--broker-token"] and len(auth_args) == 2:
        headers["Authorization"] = f"Bearer {auth_args[1]}"
    elif len(auth_args) == 4 and auth_args[0] == "--broker-username":
        token = base64.b64encode(f"{auth_args[1]}:{auth_args[3]}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {token}"

    request = Request(
        f"{broker_url.rstrip('/')}/pacticipants/{pacticipant}",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status == 200
    except HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    except URLError:
        raise


def run_checked(cmd: list[str], *, cwd: pathlib.Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def format_called_process_error(exc: subprocess.CalledProcessError) -> str:
    cmd = exc.cmd if isinstance(exc.cmd, str) else " ".join(str(part) for part in exc.cmd)
    return f"Command failed with exit code {exc.returncode}: {cmd}"
