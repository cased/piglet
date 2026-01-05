"""Tests for CLI commands"""

import json

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


class TestRootCLI:
    """Tests for root CLI group"""

    def test_help_shows_usage(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Piglet - PostHog Management CLI" in result.output

    def test_version_shows_version(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "piglet, version" in result.output

    def test_missing_api_key_shows_error(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, ["flags", "list"])
        assert result.exit_code == 1
        assert "API key required" in result.output

    def test_missing_project_id_shows_error(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, ["--api-key", "test", "flags", "list"])
        assert result.exit_code == 1
        assert "Project ID required" in result.output


class TestFlagsCommands:
    """Tests for flags subcommands"""

    def test_flags_list_help(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, ["flags", "list", "--help"])
        assert result.exit_code == 0
        assert "List all feature flags" in result.output

    def test_flags_list_active_filter(self, runner, sample_flag, httpx_mock):
        from piglet.cli import cli
        inactive_flag = {**sample_flag, "id": 124, "key": "inactive-flag", "active": False}
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/",
            json={"results": [sample_flag, inactive_flag]},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "list", "--active"
        ])
        assert result.exit_code == 0
        assert "test-flag" in result.output
        assert "inactive-flag" not in result.output

    def test_flags_get_by_id(self, runner, sample_flag, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/123/",
            json=sample_flag,
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "get", "123"
        ])
        assert result.exit_code == 0
        assert "test-flag" in result.output

    def test_flags_get_by_key(self, runner, sample_flag, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/",
            json={"results": [sample_flag]},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "get", "test-flag"
        ])
        assert result.exit_code == 0
        assert "test-flag" in result.output

    def test_flags_get_not_found(self, runner, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/",
            json={"results": []},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "get", "nonexistent"
        ])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_flags_create(self, runner, sample_flag, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/",
            method="POST",
            json=sample_flag,
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "create",
            "--key", "test-flag",
            "--name", "Test Flag",
            "--rollout-percentage", "50"
        ])
        assert result.exit_code == 0
        assert "created successfully" in result.output

    def test_flags_update(self, runner, sample_flag, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/123/",
            method="PATCH",
            json={**sample_flag, "active": False},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "update", "123",
            "--inactive"
        ])
        assert result.exit_code == 0
        assert "updated successfully" in result.output

    def test_flags_update_requires_option(self, runner):
        from piglet.cli import cli
        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "update", "123"
        ])
        assert result.exit_code == 2
        assert "At least one update option required" in result.output

    def test_flags_delete_with_confirmation(self, runner, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/123/",
            method="PATCH",
            json={"deleted": True},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "delete", "123"
        ], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.output

    def test_flags_delete_skip_confirmation(self, runner, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/feature_flags/123/",
            method="PATCH",
            json={"deleted": True},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "flags", "delete", "123", "--yes"
        ])
        assert result.exit_code == 0
        assert "deleted successfully" in result.output


class TestCohortsCommands:
    """Tests for cohorts subcommands"""

    def test_cohorts_list(self, runner, sample_cohort, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/cohorts/",
            json={"results": [sample_cohort]},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "cohorts", "list"
        ])
        assert result.exit_code == 0
        assert "Test Cohort" in result.output

    def test_cohorts_create(self, runner, sample_cohort, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/cohorts/",
            method="POST",
            json=sample_cohort,
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "cohorts", "create",
            "--name", "Test Cohort"
        ])
        assert result.exit_code == 0
        assert "created successfully" in result.output


class TestProjectsCommands:
    """Tests for projects subcommands"""

    def test_projects_list(self, runner, sample_project, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/",
            json={"results": [sample_project]},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "projects", "list"
        ])
        assert result.exit_code == 0
        assert "Test Project" in result.output


class TestDashboardsCommands:
    """Tests for dashboards subcommands"""

    def test_dashboards_list(self, runner, sample_dashboard, httpx_mock):
        from piglet.cli import cli
        httpx_mock.add_response(
            url="https://us.posthog.com/api/projects/123/dashboards/",
            json={"results": [sample_dashboard]},
        )

        result = runner.invoke(cli, [
            "--api-key", "test",
            "--project-id", "123",
            "dashboards", "list"
        ])
        assert result.exit_code == 0
        assert "Test Dashboard" in result.output


