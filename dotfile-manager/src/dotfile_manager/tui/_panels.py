from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _make_diff_panel(diff_lines: list[str], title: str) -> Panel:
    text = Text()
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            text.append(line, style="green")
        elif line.startswith("-") and not line.startswith("---"):
            text.append(line, style="red")
        elif line.startswith("@@"):
            text.append(line, style="cyan")
        else:
            text.append(line, style="dim")
    return Panel(text, title=title, border_style="blue")


def _make_hunk_panel(hunk_lines: list[str], n: int, total: int) -> Panel:
    text = Text()
    for line in hunk_lines:
        if line.startswith("+") and not line.startswith("+++"):
            text.append(line, style="green")
        elif line.startswith("-") and not line.startswith("---"):
            text.append(line, style="red")
        else:
            text.append(line, style="dim")
    return Panel(text, title=f"Hunk {n}/{total}", border_style="yellow")


def _make_status_table(rows: list[tuple[str, str, str]]) -> Table:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Status")
    for name, file_type, status in rows:
        table.add_row(name, file_type, status)
    return table
