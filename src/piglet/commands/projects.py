"""Projects commands"""

import click

from piglet.helpers import require_client
from piglet.output import output

# Column definitions for projects output
PROJECT_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("api_token", "API Token"),
    ("created_at", "Created"),
]


@click.group()
def projects() -> None:
    """Manage PostHog projects"""
    pass


@projects.command("list")
@click.pass_context
def list_projects(ctx: click.Context) -> None:
    """List all projects"""
    client = require_client(ctx)
    result = client.list_projects()

    output(
        result,
        PROJECT_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
        title="Projects",
    )


@projects.command("get")
@click.argument("project_id", type=int)
@click.pass_context
def get_project(ctx: click.Context, project_id: int) -> None:
    """Get details of a specific project"""
    client = require_client(ctx)
    result = client.get_project(project_id)

    output(
        result,
        PROJECT_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )
