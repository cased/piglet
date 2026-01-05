"""PostHog API client"""

from typing import Any

import httpx

from piglet.exceptions import (
    AuthenticationError,
    NotFoundError,
    PostHogAPIError,
    RateLimitError,
)


class PostHogClient:
    """PostHog API client with error handling"""

    def __init__(self, api_key: str, host: str, timeout: float = 30.0):
        self.api_key = api_key
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.host,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client"""
        if self._client is not None:
            self._client.close()
            self._client = None

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", status_code=401)
        elif response.status_code == 403:
            # Parse error detail from PostHog API response
            try:
                error_data = response.json()
                detail = error_data.get("detail", "Permission denied")
            except Exception:
                detail = "Permission denied"
            raise AuthenticationError(detail, status_code=403)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found", status_code=404)
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", status_code=429)
        elif response.status_code >= 400:
            raise PostHogAPIError(
                f"API error: {response.status_code} - {response.text}",
                status_code=response.status_code,
            )

        # Handle empty responses (e.g., 204 No Content)
        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        """Make GET request"""
        response = self.client.get(path, params=params)
        return self._handle_response(response)

    def post(self, path: str, data: dict) -> Any:
        """Make POST request"""
        response = self.client.post(path, json=data)
        return self._handle_response(response)

    def patch(self, path: str, data: dict) -> Any:
        """Make PATCH request"""
        response = self.client.patch(path, json=data)
        return self._handle_response(response)

    def delete(self, path: str) -> Any:
        """Make DELETE request"""
        response = self.client.delete(path)
        return self._handle_response(response)

    # ==================== Projects ====================

    def list_projects(self) -> dict:
        """List all projects"""
        return self.get("/api/projects/")

    def get_project(self, project_id: int) -> dict:
        """Get a specific project"""
        return self.get(f"/api/projects/{project_id}/")

    def get_current_organization(self) -> dict:
        """Get current organization"""
        return self.get("/api/organizations/@current/")

    # ==================== Feature Flags ====================

    def list_feature_flags(self, project_id: int) -> dict:
        """List all feature flags"""
        return self.get(f"/api/projects/{project_id}/feature_flags/")

    def get_feature_flag(self, project_id: int, flag_id: int) -> dict:
        """Get a specific feature flag"""
        return self.get(f"/api/projects/{project_id}/feature_flags/{flag_id}/")

    def create_feature_flag(self, project_id: int, data: dict) -> dict:
        """Create a new feature flag"""
        return self.post(f"/api/projects/{project_id}/feature_flags/", data)

    def update_feature_flag(self, project_id: int, flag_id: int, data: dict) -> dict:
        """Update a feature flag"""
        return self.patch(f"/api/projects/{project_id}/feature_flags/{flag_id}/", data)

    def delete_feature_flag(self, project_id: int, flag_id: int) -> dict:
        """Soft delete a feature flag"""
        return self.patch(
            f"/api/projects/{project_id}/feature_flags/{flag_id}/",
            {"deleted": True},
        )

    # ==================== Cohorts ====================

    def list_cohorts(self, project_id: int) -> dict:
        """List all cohorts"""
        return self.get(f"/api/projects/{project_id}/cohorts/")

    def get_cohort(self, project_id: int, cohort_id: int) -> dict:
        """Get a specific cohort"""
        return self.get(f"/api/projects/{project_id}/cohorts/{cohort_id}/")

    def create_cohort(self, project_id: int, data: dict) -> dict:
        """Create a new cohort"""
        return self.post(f"/api/projects/{project_id}/cohorts/", data)

    def update_cohort(self, project_id: int, cohort_id: int, data: dict) -> dict:
        """Update a cohort"""
        return self.patch(f"/api/projects/{project_id}/cohorts/{cohort_id}/", data)

    def delete_cohort(self, project_id: int, cohort_id: int) -> dict:
        """Soft delete a cohort"""
        return self.patch(
            f"/api/projects/{project_id}/cohorts/{cohort_id}/",
            {"deleted": True},
        )

    # ==================== Dashboards ====================

    def list_dashboards(self, project_id: int) -> dict:
        """List all dashboards"""
        return self.get(f"/api/projects/{project_id}/dashboards/")

    def get_dashboard(self, project_id: int, dashboard_id: int) -> dict:
        """Get a specific dashboard"""
        return self.get(f"/api/projects/{project_id}/dashboards/{dashboard_id}/")

    def create_dashboard(self, project_id: int, data: dict) -> dict:
        """Create a new dashboard"""
        return self.post(f"/api/projects/{project_id}/dashboards/", data)

    def update_dashboard(self, project_id: int, dashboard_id: int, data: dict) -> dict:
        """Update a dashboard"""
        return self.patch(f"/api/projects/{project_id}/dashboards/{dashboard_id}/", data)

    def delete_dashboard(self, project_id: int, dashboard_id: int) -> dict:
        """Soft delete a dashboard"""
        return self.patch(
            f"/api/projects/{project_id}/dashboards/{dashboard_id}/",
            {"deleted": True},
        )

    # ==================== Insights ====================

    def list_insights(self, project_id: int) -> dict:
        """List all insights"""
        return self.get(f"/api/projects/{project_id}/insights/")

    def get_insight(self, project_id: int, insight_id: int) -> dict:
        """Get a specific insight"""
        return self.get(f"/api/projects/{project_id}/insights/{insight_id}/")

    def create_insight(self, project_id: int, data: dict) -> dict:
        """Create a new insight"""
        return self.post(f"/api/projects/{project_id}/insights/", data)

    def update_insight(self, project_id: int, insight_id: int, data: dict) -> dict:
        """Update an insight"""
        return self.patch(f"/api/projects/{project_id}/insights/{insight_id}/", data)

    def delete_insight(self, project_id: int, insight_id: int) -> dict:
        """Soft delete an insight"""
        return self.patch(
            f"/api/projects/{project_id}/insights/{insight_id}/",
            {"deleted": True},
        )
