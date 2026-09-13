import json
import subprocess
import sys

import pytest
from scripts.check_boundaries import violations
from src.config import ConfigError, LIVE_TEXT_KEYS, load_settings


def test_env_loads_without_interpolation_or_logging(tmp_path):
    path = tmp_path / ".env"
    path.write_text("LLM_MODE=dry_run\nLLM_DAILY_LIMIT_AUD=0.5\nAZURE_TENANT_ID='${PRIVATE}'\n")
    config = load_settings({}, path)
    assert str(config.daily_limit) == "0.5"
    assert config.azure["AZURE_TENANT_ID"] == "${PRIVATE}"
    assert "PRIVATE" not in repr(config)


@pytest.mark.parametrize("key,value", [("LLM_DAILY_LIMIT_AUD", "secret-sentinel"),
                                      ("LLM_DAILY_LIMIT_AUD", "NaN"),
                                      ("LLM_PROJECT_LIMIT_AUD", "40"),
                                      ("LLM_MODE", "secret-sentinel")])
def test_config_errors_never_echo_values(tmp_path, key, value):
    with pytest.raises(ConfigError) as error:
        load_settings({key: value}, tmp_path / "missing")
    assert value not in str(error.value)


def test_missing_live_keys_are_validated_on_import(tmp_path):
    import os
    env = {k: v for k, v in os.environ.items() if not k.startswith(("AZURE_", "LLM_"))}
    env.update(LLM_MODE="live", LLM_ALLOW_LIVE="true")
    env.update({key: "" for key in LIVE_TEXT_KEYS})
    result = subprocess.run([sys.executable, "-c", "import src.config"], env=env,
                             capture_output=True, text=True)
    assert result.returncode != 0
    assert "Missing required live configuration keys:" in result.stderr
    assert "AZURE_OPENAI_ENDPOINT" in result.stderr


@pytest.mark.parametrize("path,source", [
    ("src/agents/bad.py", "import openai"),
    ("src/controls/bad.py", "from anthropic import Anthropic"),
    ("src/controls/bad.py", "from src.gateway.llm_client import LLMClient"),
    ("src/agents/bad.py", "from importlib import import_module as load; load('openai')"),
    ("src/agents/bad.py", "import requests"),
    ("src/controls/bad.py", "path = 'data/ground_truth/control-cases.json'"),
    ("src/agents/bad.py", "from src.eval import scoring"),
    (".env", ""), ("nested/.env.production", ""),
])
def test_boundaries_reject_forbidden_files_and_imports(path, source):
    assert violations(path, source)


def test_gateway_and_template_are_allowed():
    assert not violations("src/gateway/llm_client.py", "from openai import AzureOpenAI")
    assert not violations(".env.example", "AZURE_TENANT_ID=")


def test_full_phase0_demo_is_offline(config, capsys):
    from src.__main__ import main
    main(config)
    output = json.loads(capsys.readouterr().out)
    assert output["mode"] == "dry_run"
    assert output["ledger"] == {"committed_microaud": 0, "held_microaud": 0}
