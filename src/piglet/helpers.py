"""Helper functions for CLI commands"""

import click

from piglet.client import PostHogClient


def require_client(ctx: click.Context) -> PostHogClient:
    """Get client from context, raising error if not configured"""
    client = ctx.obj.get("client")
    if client is None:
        raise click.ClickException(
            "API key required. Set POSTHOG_API_KEY or use --api-key"
        )
    return client


def require_project_id(ctx: click.Context) -> int:
    """Get project ID from context, raising error if not configured"""
    project_id = ctx.obj["config"].project_id
    if project_id is None:
        raise click.ClickException(
            "Project ID required. Set POSTHOG_PROJECT_ID or use --project-id"
        )
    return project_id
