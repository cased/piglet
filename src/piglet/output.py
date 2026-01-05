"""Output formatting for Piglet CLI"""

import json
from collections.abc import Callable
from typing import Any

import click
from rich.console import Console
from rich.table import Table

console = Console()


def output_json(data: Any) -> None:
    """Output data as formatted JSON"""
    click.echo(json.dumps(data, indent=2, default=str))


def output_plain_table(
    data: list[dict],
    columns: list[tuple[str, str] | tuple[str, str, Callable]],
) -> None:
    """Output data as tab-separated plain text"""
    if not data:
        click.echo("No results found")
        return

    # Header row
    headers = [col[1] for col in columns]
    click.echo("\t".join(headers))

    # Data rows
    for item in data:
        row = []
        for col in columns:
            key = col[0]
            formatter = col[2] if len(col) > 2 else str
            value = item.get(key)
            if value is not None:
                formatted = str(formatter(value))
                # Strip rich markup for plain output
                formatted = _strip_rich_markup(formatted)
                row.append(formatted)
            else:
                row.append("")
        click.echo("\t".join(row))


def output_plain_single(
    data: dict,
    columns: list[tuple[str, str] | tuple[str, str, Callable]],
) -> None:
    """Output a single item as plain key: value pairs"""
    for col in columns:
        key = col[0]
        label = col[1]
        formatter = col[2] if len(col) > 2 else str
        value = data.get(key)
        if value is not None:
            formatted = str(formatter(value))
            formatted = _strip_rich_markup(formatted)
            click.echo(f"{label}: {formatted}")
        else:
            click.echo(f"{label}: -")


def _strip_rich_markup(text: str) -> str:
    """Remove rich markup tags from text"""
    import re
    return re.sub(r'\[/?[^\]]+\]', '', text)


def output_table(
    data: list[dict],
    columns: list[tuple[str, str] | tuple[str, str, Callable]],
    title: str | None = None,
) -> None:
    """Output data as a Rich table"""
    if not data:
        console.print("[dim]No results found[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")

    for col in columns:
        table.add_column(col[1])

    for item in data:
        row = []
        for col in columns:
            key = col[0]
            formatter = col[2] if len(col) > 2 else str
            value = item.get(key)
            if value is not None:
                row.append(str(formatter(value)))
            else:
                row.append("")
        table.add_row(*row)

    console.print(table)


def output_single(
    data: dict,
    columns: list[tuple[str, str] | tuple[str, str, Callable]],
) -> None:
    """Output a single item as key-value pairs"""
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for col in columns:
        key = col[0]
        label = col[1]
        formatter = col[2] if len(col) > 2 else str
        value = data.get(key)
        if value is not None:
            table.add_row(label, str(formatter(value)))
        else:
            table.add_row(label, "[dim]-[/dim]")

    console.print(table)


def output(
    data: Any,
    columns: list[tuple[str, str] | tuple[str, str, Callable]],
    as_json: bool = False,
    as_plain: bool = False,
    title: str | None = None,
) -> None:
    """Unified output function

    Args:
        data: The data to output
        columns: Column definitions (key, header, optional_formatter)
        as_json: Output as JSON
        as_plain: Output as plain tab-separated text
        title: Optional title for table output
    """
    if as_json:
        output_json(data)
        return

    # Handle paginated responses
    if isinstance(data, dict) and "results" in data:
        items = data["results"]
    elif isinstance(data, list):
        items = data
    else:
        # Single item
        if as_plain:
            output_plain_single(data, columns)
        else:
            output_single(data, columns)
        return

    if as_plain:
        output_plain_table(items, columns)
    else:
        output_table(items, columns, title)


def format_bool(value: bool) -> str:
    """Format boolean for display"""
    return "[green]Yes[/green]" if value else "[red]No[/red]"


def format_percentage(value: int | float | None) -> str:
    """Format percentage for display"""
    if value is None:
        return "-"
    return f"{value}%"
