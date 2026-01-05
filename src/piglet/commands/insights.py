"""Insights commands"""

import click

from piglet.helpers import require_client, require_project_id
from piglet.output import format_bool, output

# Column definitions for insights output
INSIGHT_COLUMNS = [
    ("id", "ID"),
    ("short_id", "Short ID"),
    ("name", "Name"),
    ("saved", "Saved", format_bool),
    ("created_at", "Created"),
]

INSIGHT_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("short_id", "Short ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("saved", "Saved", format_bool),
    ("favorited", "Favorited", format_bool),
    ("created_at", "Created"),
    ("created_by", "Created By", lambda x: x.get("email", "-") if x else "-"),
    ("last_modified_at", "Last Modified"),
]


@click.group()
def insights() -> None:
    """Manage insights"""
    pass


@insights.command("list")
@click.option("--saved", "saved_filter", flag_value=True, help="Show only saved insights")
@click.option("--favorited", "favorited_filter", flag_value=True, help="Show only favorited")
@click.option("--limit", default=100, help="Maximum results to return")
@click.pass_context
def list_insights(
    ctx: click.Context,
    saved_filter: bool | None,
    favorited_filter: bool | None,
    limit: int,
) -> None:
    """List all insights"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.list_insights(project_id)
    insights_data = result.get("results", [])

    # Apply filters
    if saved_filter is not None:
        insights_data = [i for i in insights_data if i.get("saved") == saved_filter]
    if favorited_filter is not None:
        insights_data = [i for i in insights_data if i.get("favorited") == favorited_filter]

    # Exclude deleted insights
    insights_data = [i for i in insights_data if not i.get("deleted")]

    output(
        insights_data[:limit],
        INSIGHT_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
        title="Insights",
    )


@insights.command("get")
@click.argument("insight_id")
@click.pass_context
def get_insight(ctx: click.Context, insight_id: str) -> None:
    """Get details of a specific insight

    INSIGHT_ID can be the numeric ID or the short_id.
    """
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    # Support lookup by short_id or numeric ID
    if insight_id.isdigit():
        result = client.get_insight(project_id, int(insight_id))
    else:
        # Lookup by short_id - need to list and filter
        all_insights = client.list_insights(project_id)
        result = next(
            (i for i in all_insights.get("results", []) if i.get("short_id") == insight_id),
            None,
        )
        if not result:
            raise click.ClickException(f"Insight with short_id '{insight_id}' not found")

    output(
        result,
        INSIGHT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )


@insights.command("create")
@click.option("--name", required=True, help="Insight name")
@click.option("--description", help="Insight description")
@click.option("--saved/--unsaved", default=True, help="Whether insight is saved")
@click.pass_context
def create_insight(
    ctx: click.Context,
    name: str,
    description: str | None,
    saved: bool,
) -> None:
    """Create a new insight

    Creates a basic trends insight. For complex queries,
    use the PostHog UI or API directly.
    """
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {
        "name": name,
        "saved": saved,
        # Default to a simple trends query
        "query": {
            "kind": "TrendsQuery",
            "series": [],
        },
    }
    if description:
        data["description"] = description

    result = client.create_insight(project_id, data)

    output(
        result,
        INSIGHT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nInsight '{name}' created successfully!")


@insights.command("update")
@click.argument("insight_id", type=int)
@click.option("--name", help="Insight name")
@click.option("--description", help="Insight description")
@click.option("--saved/--unsaved", default=None, help="Whether insight is saved")
@click.pass_context
def update_insight(
    ctx: click.Context,
    insight_id: int,
    name: str | None,
    description: str | None,
    saved: bool | None,
) -> None:
    """Update an existing insight"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if saved is not None:
        data["saved"] = saved

    if not data:
        raise click.UsageError("At least one update option required")

    result = client.update_insight(project_id, insight_id, data)

    output(
        result,
        INSIGHT_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nInsight {insight_id} updated successfully!")


@insights.command("delete")
@click.argument("insight_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_insight(ctx: click.Context, insight_id: int, yes: bool) -> None:
    """Delete an insight (soft delete)"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    if not yes:
        click.confirm(f"Are you sure you want to delete insight {insight_id}?", abort=True)

    client.delete_insight(project_id, insight_id)

    if ctx.obj["output_json"]:
        output({"deleted": True, "id": insight_id}, [], as_json=True)
    else:
        click.echo(f"Insight {insight_id} deleted successfully!")
