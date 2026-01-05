"""Cohorts commands"""

import click

from piglet.helpers import require_client, require_project_id
from piglet.output import format_bool, output

# Column definitions for cohorts output
COHORT_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("count", "Count"),
    ("is_static", "Static", format_bool),
    ("created_at", "Created"),
]

COHORT_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("count", "Count"),
    ("is_static", "Static", format_bool),
    ("is_calculating", "Calculating", format_bool),
    ("created_at", "Created"),
    ("created_by", "Created By", lambda x: x.get("email", "-") if x else "-"),
]


@click.group()
def cohorts() -> None:
    """Manage cohorts"""
    pass


@cohorts.command("list")
@click.option("--static", "static_filter", flag_value=True, help="Show only static cohorts")
@click.option("--dynamic", "static_filter", flag_value=False, help="Show only dynamic cohorts")
@click.option("--limit", default=100, help="Maximum results to return")
@click.pass_context
def list_cohorts(
    ctx: click.Context,
    static_filter: bool | None,
    limit: int,
) -> None:
    """List all cohorts"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.list_cohorts(project_id)
    cohorts_data = result.get("results", [])

    # Apply filters
    if static_filter is not None:
        cohorts_data = [c for c in cohorts_data if c.get("is_static") == static_filter]

    # Exclude deleted cohorts
    cohorts_data = [c for c in cohorts_data if not c.get("deleted")]

    output(
        cohorts_data[:limit],
        COHORT_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
        title="Cohorts",
    )


@cohorts.command("get")
@click.argument("cohort_id", type=int)
@click.pass_context
def get_cohort(ctx: click.Context, cohort_id: int) -> None:
    """Get details of a specific cohort"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.get_cohort(project_id, cohort_id)

    output(
        result,
        COHORT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )


@cohorts.command("create")
@click.option("--name", required=True, help="Cohort name")
@click.option("--description", help="Cohort description")
@click.option("--static/--dynamic", default=False, help="Whether cohort is static")
@click.pass_context
def create_cohort(
    ctx: click.Context,
    name: str,
    description: str | None,
    static: bool,
) -> None:
    """Create a new cohort

    Static cohorts have a fixed list of users.
    Dynamic cohorts are defined by filters and update automatically.
    """
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {
        "name": name,
        "is_static": static,
    }
    if description:
        data["description"] = description

    # Dynamic cohorts need filters (empty by default)
    if not static:
        data["groups"] = []

    result = client.create_cohort(project_id, data)

    output(
        result,
        COHORT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nCohort '{name}' created successfully!")


@cohorts.command("update")
@click.argument("cohort_id", type=int)
@click.option("--name", help="Cohort name")
@click.option("--description", help="Cohort description")
@click.pass_context
def update_cohort(
    ctx: click.Context,
    cohort_id: int,
    name: str | None,
    description: str | None,
) -> None:
    """Update an existing cohort"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description

    if not data:
        raise click.UsageError("At least one update option required")

    result = client.update_cohort(project_id, cohort_id, data)

    output(
        result,
        COHORT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nCohort {cohort_id} updated successfully!")


@cohorts.command("delete")
@click.argument("cohort_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_cohort(ctx: click.Context, cohort_id: int, yes: bool) -> None:
    """Delete a cohort (soft delete)"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    if not yes:
        click.confirm(f"Are you sure you want to delete cohort {cohort_id}?", abort=True)

    client.delete_cohort(project_id, cohort_id)

    if ctx.obj["output_json"]:
        output({"deleted": True, "id": cohort_id}, [], as_json=True)
    else:
        click.echo(f"Cohort {cohort_id} deleted successfully!")
