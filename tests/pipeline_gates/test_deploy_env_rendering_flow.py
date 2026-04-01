from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RENDERER_PATH = ROOT / "scripts" / "deploy" / "render_env_from_contract.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "deploy.yml"
DEPLOY_CONTRACT_PATH = ROOT / "docs" / "_canon" / "graph" / "ops" / "deploy_contract.yaml"
INJECT_SCRIPT_PATH = ROOT / "scripts" / "deploy" / "inject_env.sh"


def _load_renderer_module():
    spec = importlib.util.spec_from_loader(
        "hb_render_env_from_contract_module",
        importlib.machinery.SourceFileLoader(
            "hb_render_env_from_contract_module",
            str(RENDERER_PATH),
        ),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


renderer = _load_renderer_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_render_env_from_contract_resolves_required_values_and_derivations(tmp_path: Path):
    _write(
        tmp_path / "infra" / "env" / ".env.staging.template",
        "\n".join(
            [
                "# template",
                "REGISTRY=ghcr.io/hbtrack",
                "IMAGE_TAG=latest",
                "SECRET_KEY=CHANGE_ME_SECRET",
                "DB_PASSWORD=CHANGE_ME_DB_PASSWORD",
                "POSTGRES_PASSWORD=CHANGE_ME_DB_PASSWORD",
                "CLOUDINARY_CLOUD_NAME=CHANGE_ME_CLOUD_NAME",
                "CLOUDINARY_API_KEY=CHANGE_ME_CLOUDINARY_KEY",
                "CLOUDINARY_API_SECRET=CHANGE_ME_CLOUDINARY_SECRET",
                "CLOUDINARY_URL=CHANGE_ME_cloudinary://API_KEY:API_SECRET@CLOUD_NAME",
                "RESEND_API_KEY=CHANGE_ME_RESEND",
                "GEMINI_API_KEY=CHANGE_ME_GEMINI",
            ]
        )
        + "\n",
    )
    _write(
        tmp_path / "compiled_ops" / "deploy" / "staging.env.fragment",
        "\n".join(
            [
                "REGISTRY=ghcr.io/hbtrack",
                "IMAGE_TAG=latest",
                "SECRET_KEY=CHANGE_ME_SECRET",
                "DB_PASSWORD=CHANGE_ME_DB_PASSWORD",
                "POSTGRES_PASSWORD=CHANGE_ME_DB_PASSWORD",
                "CLOUDINARY_CLOUD_NAME=CHANGE_ME_CLOUD_NAME",
                "CLOUDINARY_API_KEY=CHANGE_ME_CLOUDINARY_KEY",
                "CLOUDINARY_API_SECRET=CHANGE_ME_CLOUDINARY_SECRET",
                "CLOUDINARY_URL=CHANGE_ME_cloudinary://API_KEY:API_SECRET@CLOUD_NAME",
                "RESEND_API_KEY=CHANGE_ME_RESEND",
                "GEMINI_API_KEY=CHANGE_ME_GEMINI",
            ]
        )
        + "\n",
    )

    rendered = renderer.render_env_content(
        root=tmp_path,
        env_name="staging",
        process_env={
            "HB_ENV_SECRET_KEY": "secret-value",
            "HB_ENV_DB_PASSWORD": "db-pass",
            "HB_ENV_CLOUDINARY_CLOUD_NAME": "hbtrack",
            "HB_ENV_CLOUDINARY_API_KEY": "cloud-key",
            "HB_ENV_CLOUDINARY_API_SECRET": "cloud-secret",
            "HB_ENV_RESEND_API_KEY": "resend-key",
            "HB_ENV_GEMINI_API_KEY": "gemini-key",
        },
        cli_sets=["IMAGE_TAG=abc1234"],
    )

    assert "IMAGE_TAG=abc1234" in rendered
    assert "SECRET_KEY=secret-value" in rendered
    assert "DB_PASSWORD=db-pass" in rendered
    assert "POSTGRES_PASSWORD=db-pass" in rendered
    assert "CLOUDINARY_URL=cloudinary://cloud-key:cloud-secret@hbtrack" in rendered
    assert "RESEND_API_KEY=resend-key" in rendered
    assert "GEMINI_API_KEY=gemini-key" in rendered


def test_render_env_from_contract_fails_when_required_values_are_missing(tmp_path: Path):
    _write(
        tmp_path / "infra" / "env" / ".env.production.template",
        "IMAGE_TAG=latest\nSECRET_KEY=CHANGE_ME_SECRET\nDB_PASSWORD=CHANGE_ME_DB_PASSWORD\n",
    )
    _write(
        tmp_path / "compiled_ops" / "deploy" / "production.env.fragment",
        "IMAGE_TAG=latest\nSECRET_KEY=CHANGE_ME_SECRET\nDB_PASSWORD=CHANGE_ME_DB_PASSWORD\n",
    )

    try:
        renderer.render_env_content(
            root=tmp_path,
            env_name="production",
            process_env={},
            cli_sets=["IMAGE_TAG=abc1234"],
        )
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("renderer deveria falhar quando faltam valores obrigatórios")

    assert "SECRET_KEY" in message
    assert "DB_PASSWORD" in message


def test_deploy_workflow_uses_contract_renderer_and_has_no_inline_bootstrap():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    deploy_contract = yaml.safe_load(DEPLOY_CONTRACT_PATH.read_text(encoding="utf-8"))
    inject_text = INJECT_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "scripts/deploy/inject_env.sh staging" in workflow_text
    assert "scripts/deploy/inject_env.sh production" in workflow_text
    assert ".deploy/staging.env" in workflow_text
    assert ".deploy/production.env" in workflow_text
    assert 'echo "REGISTRY=' not in workflow_text
    assert 'echo "SECRET_KEY=' not in workflow_text
    assert "if [ ! -f .env ]" not in workflow_text
    assert "grep -qvP" not in workflow_text

    env_rendering = deploy_contract["env_rendering"]
    assert env_rendering["renderer_ref"] == "scripts/deploy/render_env_from_contract.py"
    assert env_rendering["injector_ref"] == "scripts/deploy/inject_env.sh"
    assert env_rendering["generated_targets"]["staging"]["workspace_output"] == ".deploy/staging.env"
    assert env_rendering["generated_targets"]["production"]["workspace_output"] == ".deploy/production.env"

    assert "render_env_from_contract.py" in inject_text
