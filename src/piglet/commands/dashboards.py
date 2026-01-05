"""Dashboards commands"""

import click

from piglet.helpers import require_client, require_project_id
from piglet.output import format_bool, output

# Column definitions for dashboards output
DASHBOARD_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("pinned", "Pinned", format_bool),
    ("created_at", "Created"),
]

DASHBOARD_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("pinned", "Pinned", format_bool),
    ("created_at", "Created"),
    ("created_by", "Created By", lambda x: x.get("email", "-") if x else "-"),
    ("tiles", "Tiles", lambda x: len(x) if x else 0),
]


@click.group()
def dashboards() -> None:
    """Manage dashboards"""
    pass


@dashboards.command("list")
@click.option("--pinned", "pinned_filter", flag_value=True, help="Show only pinned dashboards")
@click.option("--limit", default=100, help="Maximum results to return")
@click.pass_context
def list_dashboards(
    ctx: click.Context,
    pinned_filter: bool | None,
    limit: int,
) -> None:
    """List all dashboards"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.list_dashboards(project_id)
    dashboards_data = result.get("results", [])

    # Apply filters
    if pinned_filter is not None:
        dashboards_data = [d for d in dashboards_data if d.get("pinned") == pinned_filter]

    # Exclude deleted dashboards
    dashboards_data = [d for d in dashboards_data if not d.get("deleted")]

    output(
        dashboards_data[:limit],
        DASHBOARD_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
        title="Dashboards",
    )


@dashboards.command("get")
@click.argument("dashboard_id", type=int)
@click.pass_context
def get_dashboard(ctx: click.Context, dashboard_id: int) -> None:
    """Get details of a specific dashboard"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.get_dashboard(project_id, dashboard_id)

    output(
        result,
        DASHBOARD_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )


@dashboards.command("create")
@click.option("--name", required=True, help="Dashboard name")
@click.option("--description", help="Dashboard description")
@click.option("--pinned/--not-pinned", default=False, help="Whether dashboard is pinned")
@click.pass_context
def create_dashboard(
    ctx: click.Context,
    name: str,
    description: str | None,
    pinned: bool,
) -> None:
    """Create a new dashboard"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {
        "name": name,
        "pinned": pinned,
    }
    if description:
        data["description"] = description

    result = client.create_dashboard(project_id, data)

    output(
        result,
        DASHBOARD_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nDashboard '{name}' created successfully!")


@dashboards.command("update")
@click.argument("dashboard_id", type=int)
@click.option("--name", help="Dashboard name")
@click.option("--description", help="Dashboard description")
@click.option("--pinned/--not-pinned", default=None, help="Whether dashboard is pinned")
@click.pass_context
def update_dashboard(
    ctx: click.Context,
    dashboard_id: int,
    name: str | None,
    description: str | None,
    pinned: bool | None,
) -> None:
    """Update an existing dashboard"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if pinned is not None:
        data["pinned"] = pinned

    if not data:
        raise click.UsageError("At least one update option required")

    result = client.update_dashboard(project_id, dashboard_id, data)

    output(
        result,
        DASHBOARD_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nDashboard {dashboard_id} updated successfully!")


@dashboards.command("delete")
@click.argument("dashboard_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_dashboard(ctx: click.Context, dashboard_id: int, yes: bool) -> None:
    """Delete a dashboard (soft delete)"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    if not yes:
        click.confirm(f"Are you sure you want to delete dashboard {dashboard_id}?", abort=True)

    client.delete_dashboard(project_id, dashboard_id)

    if ctx.obj["output_json"]:
        output({"deleted": True, "id": dashboard_id}, [], as_json=True)
    else:
        click.echo(f"Dashboard {dashboard_id} deleted successfully!")
