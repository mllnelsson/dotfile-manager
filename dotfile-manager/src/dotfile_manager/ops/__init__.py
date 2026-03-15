from pathlib import Path

from rich.console import Console

from dotfile_manager.diff import compute_diff
from dotfile_manager.errors import LocalPathNotFoundError
from dotfile_manager.registry import DotfileEntry
from dotfile_manager.tool_config import TOOL_CONFIG
from dotfile_manager.tui import render_diff

from ._partial import _apply_selected_hunks, _split_into_hunks, prompt_hunks

_console = Console()


def _resolve_local_path(entry: DotfileEntry) -> Path:
    return TOOL_CONFIG.local_root / entry.local_path


def compare(entry: DotfileEntry) -> None:
    local_path = _resolve_local_path(entry)
    if not local_path.exists():
        raise LocalPathNotFoundError(f"Local path does not exist: {local_path}")
    diff = compute_diff(entry, local_path)
    render_diff(diff, title=entry.name)


def update_source(entry: DotfileEntry) -> None:
    """Copy local → source repo (hunk-by-hunk approval)."""
    local_path = _resolve_local_path(entry)
    if not local_path.exists():
        raise LocalPathNotFoundError(f"Local path does not exist: {local_path}")
    source_path = TOOL_CONFIG.source_root / entry.source_path

    if source_path.is_dir():
        return _sync_dir(local_path, source_path, direction="local→source")
    _sync_file(local_path, source_path, direction="local→source")


def sync_local(entry: DotfileEntry) -> None:
    """Copy source repo → local (hunk-by-hunk approval)."""
    local_path = _resolve_local_path(entry)
    source_path = TOOL_CONFIG.source_root / entry.source_path

    if not source_path.exists():
        raise LocalPathNotFoundError(f"Source path does not exist: {source_path}")

    if source_path.is_dir():
        return _sync_dir(source_path, local_path, direction="source→local")
    _sync_file(source_path, local_path, direction="source→local")


def _sync_file(src: Path, dst: Path, *, direction: str) -> None:
    from dotfile_manager.diff._engine import _diff_files

    # Diff FROM dst TO src so that original=dst is the a-side.
    # apply=True then produces src-side content, which is what we write to dst.
    if dst.exists():
        diff_lines = _diff_files(dst, src)
        original = dst.read_text(errors="replace").splitlines(keepends=True)
    else:
        diff_lines = _diff_files(Path("/dev/null"), src)
        original = []

    if not diff_lines:
        _console.print("[green]No differences.[/green]")
        return

    selected = prompt_hunks(diff_lines, _console)
    hunks = _split_into_hunks(diff_lines)
    new_lines = _apply_selected_hunks(original, hunks, selected)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(new_lines))
    _console.print(f"[green]Patched {dst} ({direction})[/green]")


def _sync_dir(src: Path, dst: Path, *, direction: str) -> None:
    all_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    for rel in sorted(all_files):
        src_file = src / rel
        dst_file = dst / rel
        _console.print(f"\n[bold]File: {rel}[/bold]")
        _sync_file(src_file, dst_file, direction=direction)


__all__ = ["compare", "update_source", "sync_local"]
