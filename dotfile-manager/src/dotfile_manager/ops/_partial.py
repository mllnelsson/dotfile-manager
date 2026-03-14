from rich.console import Console
from rich.prompt import Confirm

from dotfile_manager.tui._panels import _make_hunk_panel

_CONTEXT_LINES = 3


def _split_into_hunks(diff_lines: list[str]) -> list[list[str]]:
    """Split unified diff lines into individual change hunks."""
    hunks: list[list[str]] = []
    current_hunk: list[str] = []
    in_change = False
    context_countdown = 0

    for line in diff_lines:
        # Skip file headers
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            if current_hunk:
                hunks.append(current_hunk)
                current_hunk = []
            in_change = False
            context_countdown = 0
            continue

        is_change = line.startswith("+") or line.startswith("-")

        if is_change:
            current_hunk.append(line)
            in_change = True
            context_countdown = _CONTEXT_LINES
        elif in_change:
            if context_countdown > 0:
                current_hunk.append(line)
                context_countdown -= 1
            else:
                # Gap between hunks — flush current
                if current_hunk:
                    hunks.append(current_hunk)
                    current_hunk = []
                in_change = False

    if current_hunk:
        hunks.append(current_hunk)
    return hunks


def _apply_selected_hunks(
    original_lines: list[str],
    all_hunks: list[list[str]],
    selected: list[bool],
) -> list[str]:
    """Return new file content applying only the selected hunks."""
    # Build the set of lines to remove and lines to add
    # For simplicity: reconstruct from the diff perspective
    # Lines starting with '-' in selected hunks are removed from original
    # Lines starting with '+' in selected hunks are added

    lines_to_remove: set[str] = set()
    lines_to_add: list[str] = []

    for hunk, keep in zip(all_hunks, selected):
        if keep:
            for line in hunk:
                if line.startswith("-"):
                    lines_to_remove.add(line[1:])
                elif line.startswith("+"):
                    lines_to_add.append(line[1:])

    result = [line for line in original_lines if line not in lines_to_remove]
    result.extend(lines_to_add)
    return result


def prompt_hunks(diff_lines: list[str], console: Console) -> list[bool]:
    """Interactively prompt the user to accept or reject each hunk."""
    hunks = _split_into_hunks(diff_lines)
    if not hunks:
        return []
    selected: list[bool] = []
    for i, hunk in enumerate(hunks, start=1):
        console.print(_make_hunk_panel(hunk, n=i, total=len(hunks)))
        accept = Confirm.ask("Apply this hunk?", default=True, console=console)
        selected.append(accept)
    return selected


__all__ = ["_split_into_hunks", "_apply_selected_hunks", "prompt_hunks"]
