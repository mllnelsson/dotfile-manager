from rich.console import Console

from ._panels import _make_diff_panel, _make_hunk_panel, _make_status_table  # noqa: F401

_console = Console()


def render_diff(diff: list[str] | dict[str, list[str]], title: str = "Diff") -> None:
    if isinstance(diff, dict):
        for filename, lines in diff.items():
            if lines:
                _console.print(_make_diff_panel(lines, title=f"{title} — {filename}"))
    else:
        if diff:
            _console.print(_make_diff_panel(diff, title=title))
        else:
            _console.print(f"[green]No differences found for {title}[/green]")


def render_summary(rows: list[tuple[str, str, str]]) -> None:
    _console.print(_make_status_table(rows))


__all__ = ["render_diff", "render_summary"]
