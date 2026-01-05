"""Tests for configuration module"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from piglet.config import (
    Config,
    get_config,
    get_config_path,
    load_config_file,
    resolve_host,
    DEFAULT_HOST,
    HOST_ALIASES,
)


class TestResolveHost:
    """Tests for resolve_host function"""

    def test_resolve_us_alias(self):
        assert resolve_host("us") == "https://us.posthog.com"

    def test_resolve_eu_alias(self):
        assert resolve_host("eu") == "https://eu.posthog.com"

    def test_resolve_us_alias_uppercase(self):
        assert resolve_host("US") == "https://us.posthog.com"

    def test_resolve_full_url_unchanged(self):
        url = "https://posthog.mycompany.com"
        assert resolve_host(url) == url

    def test_resolve_none_returns_default(self):
        assert resolve_host(None) == DEFAULT_HOST


class TestGetConfigPath:
    """Tests for get_config_path function"""

    def test_config_path_in_home_directory(self):
        path = get_config_path()
        assert path == Path.home() / ".piglet" / "config.toml"


class TestLoadConfigFile:
    """Tests for load_config_file function"""

    def test_returns_empty_dict_if_no_file(self, tmp_path):
        with patch("piglet.config.get_config_path", return_value=tmp_path / "nonexistent.toml"):
            result = load_config_file()
            assert result == {}

    def test_loads_toml_file(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
api_key = "phx_test_key"
host = "https://eu.posthog.com"
project_id = 12345
""")
        with patch("piglet.config.get_config_path", return_value=config_file):
            result = load_config_file()
            assert result["api_key"] == "phx_test_key"
            assert result["host"] == "https://eu.posthog.com"
            assert result["project_id"] == 12345


class TestGetConfig:
    """Tests for get_config function"""

    def test_cli_args_take_precedence(self, tmp_path):
        # Set up env vars and config file
        config_file = tmp_path / "config.toml"
        config_file.write_text('api_key = "file_key"\nproject_id = 111')

        with patch("piglet.config.get_config_path", return_value=config_file):
            with patch.dict(os.environ, {
                "POSTHOG_API_KEY": "env_key",
                "POSTHOG_PROJECT_ID": "222",
            }):
                config = get_config(
                    api_key="cli_key",
                    host="eu",
                    project_id=333,
                )
                assert config.api_key == "cli_key"
                assert config.host == "https://eu.posthog.com"
                assert config.project_id == 333

    def test_env_vars_take_precedence_over_file(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('api_key = "file_key"\nproject_id = 111')

        with patch("piglet.config.get_config_path", return_value=config_file):
            with patch.dict(os.environ, {
                "POSTHOG_API_KEY": "env_key",
                "POSTHOG_PROJECT_ID": "222",
            }, clear=False):
                config = get_config()
                assert config.api_key == "env_key"
                assert config.project_id == 222

    def test_file_config_used_when_no_env_or_cli(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('api_key = "file_key"\nproject_id = 111\nhost = "eu"')

        with patch("piglet.config.get_config_path", return_value=config_file):
            with patch.dict(os.environ, {}, clear=True):
                # Clear any existing POSTHOG_ env vars
                for key in list(os.environ.keys()):
                    if key.startswith("POSTHOG_"):
                        del os.environ[key]

                config = get_config()
                assert config.api_key == "file_key"
                assert config.project_id == 111

    def test_defaults_when_nothing_set(self, tmp_path):
        config_file = tmp_path / "nonexistent.toml"

        with patch("piglet.config.get_config_path", return_value=config_file):
            with patch.dict(os.environ, {}, clear=True):
                for key in list(os.environ.keys()):
                    if key.startswith("POSTHOG_"):
                        del os.environ[key]

                config = get_config()
                assert config.api_key is None
                assert config.host == DEFAULT_HOST
                assert config.project_id is None
