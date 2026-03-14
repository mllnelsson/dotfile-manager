from typing import Annotated

import typer
from rich.console import Console

from dotfile_manager.errors import DfmError, EntryNotFoundError
from dotfile_manager import ops
from dotfile_manager.registry import load_entries_from_file
from dotfile_manager.registry.model import DotfileEntry
from dotfile_manager.tui import render_summary

app = typer.Typer(
    name="dfm",
    help="Dotfile manager — sync files between source repo and local config.",
)
_console = Console()
_err_console = Console(stderr=True)


def _get_entries(name: str | None) -> list[DotfileEntry]:
    entries = load_entries_from_file()
    if name is None:
        return entries
    for entry in entries:
        if entry.name == name:
            return [entry]
    raise EntryNotFoundError(f"No entry named '{name}' in registry.")


@app.command(name="list")
def list_entries() -> None:
    """List all dotfile entries in the registry."""
    entries = load_entries_from_file()
    rows = [(e.name, str(e.local_path), str(e.source_path)) for e in entries]
    render_summary(rows)


@app.command()
def compare(
    name: Annotated[
        str | None, typer.Argument(help="Entry name (omit for all)")
    ] = None,
) -> None:
    """Show diff between source repo and local config."""
    entries = _get_entries(name)
    for entry in entries:
        _console.rule(f"[bold]{entry.name}[/bold]")
        ops.compare(entry)


@app.command()
def update(
    name: Annotated[
        str | None, typer.Argument(help="Entry name (omit for all)")
    ] = None,
    partial: Annotated[
        bool, typer.Option("--partial", help="Approve hunks interactively")
    ] = False,
) -> None:
    """Copy local config → source repo."""
    entries = _get_entries(name)
    for entry in entries:
        _console.rule(f"[bold]{entry.name}[/bold]")
        ops.update_source(entry, partial=partial)


@app.command()
def sync(
    name: Annotated[
        str | None, typer.Argument(help="Entry name (omit for all)")
    ] = None,
    partial: Annotated[
        bool, typer.Option("--partial", help="Approve hunks interactively")
    ] = False,
) -> None:
    """Copy source repo → local config."""
    entries = _get_entries(name)
    for entry in entries:
        _console.rule(f"[bold]{entry.name}[/bold]")
        ops.sync_local(entry, partial=partial)


def main() -> None:
    try:
        app()
    except DfmError as exc:
        _err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
