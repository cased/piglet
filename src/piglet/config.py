"""Configuration management for Piglet CLI"""

import os
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]


HOST_ALIASES = {
    "us": "https://us.posthog.com",
    "eu": "https://eu.posthog.com",
}

DEFAULT_HOST = "https://us.posthog.com"


@dataclass
class Config:
    """Configuration container"""

    api_key: str | None = None
    host: str = DEFAULT_HOST
    project_id: int | None = None


def get_config_dir() -> Path:
    """Return path to config directory (~/.piglet/)"""
    return Path.home() / ".piglet"


def get_config_path() -> Path:
    """Return path to config file (~/.piglet/config.toml)"""
    return get_config_dir() / "config.toml"


def load_config_file() -> dict:
    """Load configuration from TOML file if it exists"""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}


def resolve_host(host: str | None) -> str:
    """Resolve host aliases (us, eu) to full URLs"""
    if host is None:
        return DEFAULT_HOST
    return HOST_ALIASES.get(host.lower(), host)


def get_config(
    api_key: str | None = None,
    host: str | None = None,
    project_id: int | None = None,
) -> Config:
    """
    Build configuration with precedence:
    1. CLI arguments (highest)
    2. Environment variables
    3. Config file
    4. Defaults (lowest)
    """
    file_config = load_config_file()

    # Resolve each setting with proper precedence
    resolved_api_key = (
        api_key
        or os.environ.get("POSTHOG_API_KEY")
        or file_config.get("api_key")
    )

    resolved_host = resolve_host(
        host
        or os.environ.get("POSTHOG_HOST")
        or file_config.get("host")
    )

    # Handle project_id (can be string in env, int in file)
    env_project_id = os.environ.get("POSTHOG_PROJECT_ID")
    resolved_project_id = (
        project_id
        or (int(env_project_id) if env_project_id else None)
        or file_config.get("project_id")
    )

    return Config(
        api_key=resolved_api_key,
        host=resolved_host,
        project_id=resolved_project_id,
    )
