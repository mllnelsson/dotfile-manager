import re

from rich.console import Console
from rich.prompt import Confirm

from dotfile_manager.tui._panels import _make_hunk_panel


def _split_into_hunks(diff_lines: list[str]) -> list[list[str]]:
    """Split unified diff lines into hunks; each hunk begins with its @@ header.

    The file-header lines (--- and +++) that precede the first @@ are skipped.
    After the first @@ we are inside hunk content, so lines starting with ---
    or +++ are kept (they represent deletions/additions of lines that begin with
    -- or ++, e.g. Lua comments).
    """
    hunks: list[list[str]] = []
    current: list[str] = []
    in_hunk = False

    for line in diff_lines:
        if not in_hunk and (line.startswith("---") or line.startswith("+++")):
            continue
        if line.startswith("@@"):
            in_hunk = True
            if current:
                hunks.append(current)
            current = [line]
        elif current:
            current.append(line)

    if current:
        hunks.append(current)
    return hunks


def _parse_hunk_header(header: str) -> int:
    """Parse @@ -old_start[,count] +... @@ and return old_start as a 0-based index.

    old_start is the starting line in original_lines (the a-side of the diff).
    """
    m = re.match(r"@@ -(\d+)", header)
    if not m:
        raise ValueError(f"Cannot parse hunk header: {header!r}")
    return int(m.group(1)) - 1  # unified diff is 1-based


def _apply_selected_hunks(
    original_lines: list[str],
    all_hunks: list[list[str]],
    selected: list[bool],
) -> list[str]:
    """Return file content with only the selected hunks applied.

    original_lines is the a-side of unified_diff(a, b).

    For each hunk:
    - apply=True:  accept the change; produce b-side content at this location.
    - apply=False: reject the change; keep a-side (original) content.

    Line types in the hunk:
    - '-' lines: from a (original). Advance orig_pos; skip when applying.
    - '+' lines: from b (new). Do NOT advance orig_pos; include when applying.
    - context: in both. Advance orig_pos; always keep from original.
    """
    result: list[str] = []
    orig_pos = 0  # 0-based cursor into original_lines (a side)

    for hunk, apply in zip(all_hunks, selected):
        old_start = _parse_hunk_header(hunk[0])

        # Copy original lines that precede this hunk
        result.extend(original_lines[orig_pos:old_start])
        orig_pos = old_start

        for line in hunk[1:]:
            if line.startswith("+"):
                if apply:
                    result.append(line[1:])
            elif line.startswith("-"):
                if not apply:
                    result.append(original_lines[orig_pos])
                orig_pos += 1
            else:
                # context line — always keep from original (authoritative)
                result.append(original_lines[orig_pos])
                orig_pos += 1

    # Copy any trailing original lines after the last hunk
    result.extend(original_lines[orig_pos:])
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
