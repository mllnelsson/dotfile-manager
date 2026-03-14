import difflib
from pathlib import Path


def _diff_files(source: Path, local: Path) -> list[str]:
    source_lines = source.read_text(errors="replace").splitlines(keepends=True)
    local_lines = local.read_text(errors="replace").splitlines(keepends=True)
    return list(
        difflib.unified_diff(
            source_lines,
            local_lines,
            fromfile=str(source),
            tofile=str(local),
        )
    )


def _diff_dirs(source: Path, local: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    all_names = {
        str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()
    } | {str(p.relative_to(local)) for p in local.rglob("*") if p.is_file()}
    for name in sorted(all_names):
        src_file = source / name
        loc_file = local / name
        if not src_file.exists():
            result[name] = [f"--- {src_file} (missing)\n", f"+++ {loc_file}\n"]
            result[name] += [
                f"+{line}"
                for line in loc_file.read_text(errors="replace").splitlines(
                    keepends=True
                )
            ]
        elif not loc_file.exists():
            result[name] = [f"--- {src_file}\n", f"+++ {loc_file} (missing)\n"]
            result[name] += [
                f"-{line}"
                for line in src_file.read_text(errors="replace").splitlines(
                    keepends=True
                )
            ]
        else:
            diff = _diff_files(src_file, loc_file)
            if diff:
                result[name] = diff
    return result
