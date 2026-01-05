"""Feature flags commands"""

import click

from piglet.helpers import require_client, require_project_id
from piglet.output import format_bool, format_percentage, output

# Column definitions for flags output
FLAG_COLUMNS = [
    ("id", "ID"),
    ("key", "Key"),
    ("name", "Name"),
    ("active", "Active", format_bool),
    ("rollout_percentage", "Rollout", format_percentage),
]

FLAG_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("key", "Key"),
    ("name", "Name"),
    ("active", "Active", format_bool),
    ("rollout_percentage", "Rollout", format_percentage),
    ("created_at", "Created"),
    ("created_by", "Created By", lambda x: x.get("email", "-") if x else "-"),
]


@click.group()
def flags() -> None:
    """Manage feature flags"""
    pass


@flags.command("list")
@click.option("--active", "active_filter", flag_value=True, help="Show only active flags")
@click.option("--inactive", "active_filter", flag_value=False, help="Show only inactive flags")
@click.option("--limit", default=100, help="Maximum results to return")
@click.pass_context
def list_flags(
    ctx: click.Context,
    active_filter: bool | None,
    limit: int,
) -> None:
    """List all feature flags"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    result = client.list_feature_flags(project_id)
    flags_data = result.get("results", [])

    # Apply filters
    if active_filter is not None:
        flags_data = [f for f in flags_data if f.get("active") == active_filter]

    # Exclude deleted flags
    flags_data = [f for f in flags_data if not f.get("deleted")]

    output(
        flags_data[:limit],
        FLAG_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
        title="Feature Flags",
    )


@flags.command("get")
@click.argument("flag_id")
@click.pass_context
def get_flag(ctx: click.Context, flag_id: str) -> None:
    """Get details of a specific feature flag

    FLAG_ID can be the numeric ID or the flag key.
    """
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    # Support lookup by key or ID
    if flag_id.isdigit():
        result = client.get_feature_flag(project_id, int(flag_id))
    else:
        # Lookup by key
        all_flags = client.list_feature_flags(project_id)
        result = next(
            (f for f in all_flags.get("results", []) if f["key"] == flag_id),
            None,
        )
        if not result:
            raise click.ClickException(f"Flag with key '{flag_id}' not found")

    output(
        result,
        FLAG_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )


@flags.command("create")
@click.option("--key", required=True, help="Flag key (unique identifier)")
@click.option("--name", help="Human-readable name (defaults to key)")
@click.option(
    "--rollout-percentage",
    type=int,
    default=0,
    help="Percentage of users to enable (0-100)",
)
@click.option("--active/--inactive", default=True, help="Whether flag is active")
@click.pass_context
def create_flag(
    ctx: click.Context,
    key: str,
    name: str | None,
    rollout_percentage: int,
    active: bool,
) -> None:
    """Create a new feature flag"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data = {
        "key": key,
        "name": name or key,
        "active": active,
        "filters": {
            "groups": [
                {
                    "properties": [],
                    "rollout_percentage": rollout_percentage,
                }
            ]
        },
    }

    result = client.create_feature_flag(project_id, data)

    output(
        result,
        FLAG_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nFeature flag '{key}' created successfully!")


@flags.command("update")
@click.argument("flag_id", type=int)
@click.option("--name", help="Human-readable name")
@click.option("--rollout-percentage", type=int, help="Percentage of users (0-100)")
@click.option("--active/--inactive", default=None, help="Whether flag is active")
@click.pass_context
def update_flag(
    ctx: click.Context,
    flag_id: int,
    name: str | None,
    rollout_percentage: int | None,
    active: bool | None,
) -> None:
    """Update an existing feature flag"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    data: dict = {}
    if name is not None:
        data["name"] = name
    if active is not None:
        data["active"] = active
    if rollout_percentage is not None:
        # Get current flag to update filters
        current = client.get_feature_flag(project_id, flag_id)
        filters = current.get("filters", {"groups": [{"properties": []}]})
        if filters.get("groups"):
            filters["groups"][0]["rollout_percentage"] = rollout_percentage
        data["filters"] = filters

    if not data:
        raise click.UsageError("At least one update option required")

    result = client.update_feature_flag(project_id, flag_id, data)

    output(
        result,
        FLAG_DETAIL_COLUMNS,
        as_json=ctx.obj["output_json"],
        as_plain=ctx.obj["output_plain"],
    )

    if not ctx.obj["output_json"] and not ctx.obj["output_plain"]:
        click.echo(f"\nFeature flag {flag_id} updated successfully!")


@flags.command("delete")
@click.argument("flag_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_flag(ctx: click.Context, flag_id: int, yes: bool) -> None:
    """Delete a feature flag (soft delete)"""
    client = require_client(ctx)
    project_id = require_project_id(ctx)

    if not yes:
        click.confirm(f"Are you sure you want to delete flag {flag_id}?", abort=True)

    client.delete_feature_flag(project_id, flag_id)

    if ctx.obj["output_json"]:
        output({"deleted": True, "id": flag_id}, [], as_json=True)
    else:
        click.echo(f"Feature flag {flag_id} deleted successfully!")
