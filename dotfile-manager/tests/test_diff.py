from pathlib import Path

from dotfile_manager.diff._engine import _diff_files, _diff_dirs


def test_diff_files_identical(tmp_path: Path) -> None:
    src = tmp_path / "src.txt"
    loc = tmp_path / "loc.txt"
    src.write_text("same\n")
    loc.write_text("same\n")
    assert _diff_files(src, loc) == []


def test_diff_files_different(tmp_path: Path) -> None:
    src = tmp_path / "src.txt"
    loc = tmp_path / "loc.txt"
    src.write_text("line1\nline2\n")
    loc.write_text("line1\nline2 changed\n")
    diff = _diff_files(src, loc)
    assert any("-line2\n" in line for line in diff)
    assert any("+line2 changed\n" in line for line in diff)


def test_diff_dirs_identical(tmp_path: Path) -> None:
    src = tmp_path / "src"
    loc = tmp_path / "loc"
    src.mkdir()
    loc.mkdir()
    (src / "a.txt").write_text("same\n")
    (loc / "a.txt").write_text("same\n")
    result = _diff_dirs(src, loc)
    assert result == {}


def test_diff_dirs_different(tmp_path: Path) -> None:
    src = tmp_path / "src"
    loc = tmp_path / "loc"
    src.mkdir()
    loc.mkdir()
    (src / "a.txt").write_text("old\n")
    (loc / "a.txt").write_text("new\n")
    result = _diff_dirs(src, loc)
    assert "a.txt" in result
    assert len(result["a.txt"]) > 0
