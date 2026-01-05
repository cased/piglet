"""Main CLI entry point for Piglet"""

import sys

import click

from piglet import __version__
from piglet.client import PostHogClient
from piglet.config import get_config
from piglet.exceptions import PostHogAPIError


class PigletGroup(click.Group):
    """Custom group that handles API errors gracefully"""

    def invoke(self, ctx: click.Context):
        try:
            return super().invoke(ctx)
        except PostHogAPIError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@click.group(cls=PigletGroup)
@click.version_option(version=__version__, prog_name="piglet")
@click.option(
    "--api-key",
    envvar="POSTHOG_API_KEY",
    help="PostHog personal API key",
)
@click.option(
    "--host",
    envvar="POSTHOG_HOST",
    help="PostHog host (us, eu, or full URL)",
)
@click.option(
    "--project-id",
    envvar="POSTHOG_PROJECT_ID",
    type=int,
    help="PostHog project ID",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--plain",
    "output_plain",
    is_flag=True,
    help="Output as plain tab-separated text",
)
@click.pass_context
def cli(
    ctx: click.Context,
    api_key: str | None,
    host: str | None,
    project_id: int | None,
    output_json: bool,
    output_plain: bool,
) -> None:
    """Piglet - PostHog Management CLI

    Manage PostHog feature flags, cohorts, dashboards, and more from the command line.

    \b
    Configuration (in order of precedence):
      1. CLI options (--api-key, --host, --project-id)
      2. Environment variables (POSTHOG_API_KEY, POSTHOG_HOST, POSTHOG_PROJECT_ID)
      3. Config file (~/.piglet/config.toml)

    \b
    Host shortcuts:
      us  -> https://us.posthog.com
      eu  -> https://eu.posthog.com
    """
    ctx.ensure_object(dict)

    # Load configuration
    config = get_config(api_key=api_key, host=host, project_id=project_id)

    ctx.obj["config"] = config
    ctx.obj["output_json"] = output_json
    ctx.obj["output_plain"] = output_plain

    # Create client lazily - only if we have an API key
    # Some commands may not need it
    if config.api_key:
        ctx.obj["client"] = PostHogClient(
            api_key=config.api_key,
            host=config.host,
        )
    else:
        ctx.obj["client"] = None


# Import and register command groups (after cli is defined to avoid circular imports)
from piglet.commands import cohorts, dashboards, flags, insights, projects  # noqa: E402

cli.add_command(projects.projects)
cli.add_command(flags.flags)
cli.add_command(cohorts.cohorts)
cli.add_command(dashboards.dashboards)
cli.add_command(insights.insights)


if __name__ == "__main__":
    cli()
