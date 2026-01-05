"""Pytest fixtures for piglet tests"""

import pytest
from click.testing import CliRunner

from piglet.cli import cli
from piglet.client import PostHogClient


@pytest.fixture
def runner():
    """Click CLI test runner"""
    return CliRunner()


@pytest.fixture
def mock_api_response():
    """Factory for mock API responses"""
    def _make_response(results=None, **kwargs):
        if results is not None:
            return {"results": results, "count": len(results), **kwargs}
        return kwargs
    return _make_response


@pytest.fixture
def sample_flag():
    """Sample feature flag data"""
    return {
        "id": 123,
        "key": "test-flag",
        "name": "Test Flag",
        "active": True,
        "rollout_percentage": 50,
        "deleted": False,
        "created_at": "2024-01-01T00:00:00Z",
        "created_by": {"email": "test@example.com"},
        "filters": {
            "groups": [{"properties": [], "rollout_percentage": 50}]
        },
    }


@pytest.fixture
def sample_cohort():
    """Sample cohort data"""
    return {
        "id": 456,
        "name": "Test Cohort",
        "description": "A test cohort",
        "count": 100,
        "is_static": False,
        "is_calculating": False,
        "deleted": False,
        "created_at": "2024-01-01T00:00:00Z",
        "created_by": {"email": "test@example.com"},
    }


@pytest.fixture
def sample_dashboard():
    """Sample dashboard data"""
    return {
        "id": 789,
        "name": "Test Dashboard",
        "description": "A test dashboard",
        "pinned": False,
        "deleted": False,
        "created_at": "2024-01-01T00:00:00Z",
        "created_by": {"email": "test@example.com"},
        "tiles": [],
    }


@pytest.fixture
def sample_project():
    """Sample project data"""
    return {
        "id": 12345,
        "name": "Test Project",
        "api_token": "phc_test_token",
        "created_at": "2024-01-01T00:00:00Z",
    }
