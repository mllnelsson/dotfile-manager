import shutil
from pathlib import Path

from rich.console import Console

from dotfile_manager.diff import compute_diff
from dotfile_manager.errors import LocalPathNotFoundError
from dotfile_manager.local_paths import resolve_local_path
from dotfile_manager.registry.model import DotfileEntry
from dotfile_manager.tool_config import TOOL_CONFIG
from dotfile_manager.tui import render_diff

from ._partial import _apply_selected_hunks, _split_into_hunks, prompt_hunks

_console = Console()


def compare(entry: DotfileEntry) -> None:
    local_path = resolve_local_path(entry)
    if not local_path.exists():
        raise LocalPathNotFoundError(f"Local path does not exist: {local_path}")
    diff = compute_diff(entry, local_path)
    render_diff(diff, title=entry.name)


def update_source(entry: DotfileEntry, partial: bool = False) -> None:
    """Copy local → source repo."""
    local_path = resolve_local_path(entry)
    if not local_path.exists():
        raise LocalPathNotFoundError(f"Local path does not exist: {local_path}")
    source_path = TOOL_CONFIG.root_source / entry.source_path

    if entry.is_dir:
        _sync_dir(local_path, source_path, partial=partial, direction="local→source")
    else:
        _sync_file(local_path, source_path, partial=partial, direction="local→source")


def sync_local(entry: DotfileEntry, partial: bool = False) -> None:
    """Copy source repo → local."""
    local_path = resolve_local_path(entry)
    source_path = TOOL_CONFIG.root_source / entry.source_path

    if not source_path.exists():
        raise LocalPathNotFoundError(f"Source path does not exist: {source_path}")

    if entry.is_dir:
        _sync_dir(source_path, local_path, partial=partial, direction="source→local")
    else:
        _sync_file(source_path, local_path, partial=partial, direction="source→local")


def _sync_file(src: Path, dst: Path, *, partial: bool, direction: str) -> None:
    if not partial:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        _console.print(f"[green]Copied {src} → {dst}[/green]")
        return

    # Partial: hunk-by-hunk approval
    from dotfile_manager.diff._engine import _diff_files

    diff_lines = (
        _diff_files(src, dst) if dst.exists() else _diff_files(Path("/dev/null"), src)
    )
    if not diff_lines:
        _console.print("[green]No differences.[/green]")
        return

    selected = prompt_hunks(diff_lines, _console)
    hunks = _split_into_hunks(diff_lines)
    original = (
        dst.read_text(errors="replace").splitlines(keepends=True)
        if dst.exists()
        else []
    )
    new_lines = _apply_selected_hunks(original, hunks, selected)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(new_lines))
    _console.print(f"[green]Patched {dst} ({direction})[/green]")


def _sync_dir(src: Path, dst: Path, *, partial: bool, direction: str) -> None:
    if not partial:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        _console.print(f"[green]Synced {src} → {dst}[/green]")
        return

    # Partial for dirs: per-file prompting
    all_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    for rel in sorted(all_files):
        src_file = src / rel
        dst_file = dst / rel
        _console.print(f"\n[bold]File: {rel}[/bold]")
        _sync_file(src_file, dst_file, partial=True, direction=direction)


__all__ = ["compare", "update_source", "sync_local"]
