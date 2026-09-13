"""Local configuration only. Validation messages contain key names, never values."""

import os
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
AZURE_KEYS = (
    "AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_RESOURCE_GROUP", "AZURE_REGION",
    "AZURE_AI_FOUNDRY_PROJECT", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_CHEAP", "AZURE_OPENAI_DEPLOYMENT_STRONG",
    "AZURE_OPENAI_DEPLOYMENT_EMBED", "AZURE_OPENAI_ACCOUNT",
)
OPTIONAL_KEYS = (
    "DATABRICKS_HOST", "DATABRICKS_WAREHOUSE_ID", "DATABRICKS_CATALOG",
    "DATABRICKS_SCHEMA_PREFIX", "AZURE_AI_SEARCH_ENDPOINT", "AZURE_APIM_GATEWAY_URL",
    "AZURE_STORAGE_ACCOUNT",
)


class ConfigError(ValueError):
    pass


def read_env(path: Path) -> dict[str, str]:
    """Strict KEY=value subset; quotes supported, interpolation intentionally absent."""
    values = {}
    if not path.exists():
        return values
    try:
        lines = path.read_text().splitlines()
    except (OSError, UnicodeError):
        raise ConfigError("Cannot read .env as UTF-8 text") from None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or key in values:
            raise ConfigError("Invalid or duplicate entry in .env; expected KEY=value")
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise ConfigError("Invalid quoted value in .env")
            value = value[1:-1]
        values[key] = value
    return values


@dataclass(frozen=True, repr=False)
class Settings:
    mode: str
    allow_live: bool
    project_limit: Decimal
    daily_limit: Decimal
    state_dir: Path
    max_input_tokens: int
    max_output_tokens: int
    max_retries: int
    azure: dict[str, str]
    local_embedding_enabled: bool = False
    local_model_dir: Path = ROOT / ".local/models/minilm"
    corpus_dir: Path = ROOT / "data/cache/corpus"


def load_settings(environ=None, env_file: Path = ROOT / ".env") -> Settings:
    env = read_env(env_file)
    env.update(os.environ if environ is None else environ)

    def get(key, default=""):
        return env.get(key, "").strip() or default

    def number(key, default):
        try:
            value = Decimal(get(key, default))
            if not value.is_finite() or value < 0:
                raise InvalidOperation
            return value
        except (InvalidOperation, ValueError):
            raise ConfigError(f"Invalid nonnegative number: {key}") from None

    def integer(key, default, low, high):
        value = number(key, default)
        if value != value.to_integral_value() or not low <= value <= high:
            raise ConfigError(f"Invalid integer range: {key}")
        return int(value)

    mode = get("LLM_MODE", "dry_run")
    if mode not in {"dry_run", "cached", "live"}:
        raise ConfigError("LLM_MODE must be dry_run, cached, or live")
    flag = get("LLM_ALLOW_LIVE", "false").lower()
    if flag not in {"true", "false"}:
        raise ConfigError("LLM_ALLOW_LIVE must be true or false")
    local_flag = get("LOCAL_EMBEDDING_ENABLED", "false").lower()
    if local_flag not in {"true", "false"}:
        raise ConfigError("LOCAL_EMBEDDING_ENABLED must be true or false")
    lifetime = number("LLM_PROJECT_LIMIT_AUD", "6")
    daily = number("LLM_DAILY_LIMIT_AUD", "1")
    if not 0 < daily <= lifetime <= 10:
        raise ConfigError("Require 0 < LLM_DAILY_LIMIT_AUD <= LLM_PROJECT_LIMIT_AUD <= 10")
    azure = {key: get(key) for key in AZURE_KEYS + OPTIONAL_KEYS}
    if mode == "live":
        if flag != "true":
            raise ConfigError("Live mode also requires LLM_ALLOW_LIVE=true")
        missing = [key for key in AZURE_KEYS if not azure[key]]
        if missing:
            raise ConfigError("Missing required live configuration keys: " + ", ".join(missing))
        for key in ("AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID"):
            try:
                UUID(azure[key])
            except ValueError:
                raise ConfigError(f"Invalid identifier: {key}") from None
        for key in AZURE_KEYS:
            if key not in {"AZURE_OPENAI_ENDPOINT", "AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID"}:
                if not re.fullmatch(r"[A-Za-z0-9_.-]+", azure[key]):
                    raise ConfigError(f"Invalid identifier: {key}")
        try:
            url = urlsplit(azure["AZURE_OPENAI_ENDPOINT"])
            valid = (url.scheme == "https" and url.hostname and
                     url.hostname.endswith(".openai.azure.com") and not url.username and
                     not url.password and not url.port and not url.query and not url.fragment and
                     url.path in {"", "/"})
        except ValueError:
            valid = False
        if not valid:
            raise ConfigError("Invalid Azure endpoint: AZURE_OPENAI_ENDPOINT")
    state = Path(get("LLM_STATE_DIR", str(ROOT / ".local/llm"))).expanduser()
    if not state.is_absolute():
        state = ROOT / state
    return Settings(mode, flag == "true", lifetime, daily, state,
                    integer("LLM_MAX_INPUT_TOKENS", "4096", 128, 8192),
                    integer("LLM_MAX_OUTPUT_TOKENS", "1024", 1, 4096),
                    integer("LLM_MAX_RETRIES", "0", 0, 2), azure,
                    local_flag == "true")


# Offline imports need no invented cloud credentials. Live imports validate all required keys.
settings = load_settings()
