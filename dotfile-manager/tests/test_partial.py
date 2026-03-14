import difflib

from dotfile_manager.ops._partial import _apply_selected_hunks, _split_into_hunks


def _make_diff(src: list[str], dst: list[str]) -> list[str]:
    return list(difflib.unified_diff(src, dst, fromfile="src", tofile="dst"))


# ---------------------------------------------------------------------------
# _split_into_hunks
# ---------------------------------------------------------------------------


def test_split_empty() -> None:
    assert _split_into_hunks([]) == []


def test_split_no_changes() -> None:
    diff = _make_diff(["a\n", "b\n"], ["a\n", "b\n"])
    assert _split_into_hunks(diff) == []


def test_split_single_hunk_starts_with_header() -> None:
    diff = _make_diff(["old\n"], ["new\n"])
    hunks = _split_into_hunks(diff)
    assert len(hunks) == 1
    assert hunks[0][0].startswith("@@")


def test_split_two_hunks() -> None:
    # Changes far apart (> 3 context lines) produce two separate hunks
    src = ["a\n"] + [f"ctx{i}\n" for i in range(8)] + ["b\n"]
    dst = ["A\n"] + [f"ctx{i}\n" for i in range(8)] + ["B\n"]
    diff = _make_diff(src, dst)
    hunks = _split_into_hunks(diff)
    assert len(hunks) == 2
    assert all(h[0].startswith("@@") for h in hunks)


def test_split_skips_file_headers() -> None:
    diff = _make_diff(["x\n"], ["y\n"])
    hunks = _split_into_hunks(diff)
    # No hunk line should be a --- or +++ file header
    for hunk in hunks:
        for line in hunk:
            assert not line.startswith("---")
            assert not line.startswith("+++")


# ---------------------------------------------------------------------------
# _apply_selected_hunks — correctness
# ---------------------------------------------------------------------------


def _round_trip(src: list[str], dst: list[str], selected: list[bool]) -> list[str]:
    diff = _make_diff(src, dst)
    hunks = _split_into_hunks(diff)
    return _apply_selected_hunks(src, hunks, selected)


def test_apply_all_produces_dst() -> None:
    src = ["line1\n", "old\n", "line3\n"]
    dst = ["line1\n", "new\n", "line3\n"]
    result = _round_trip(src, dst, [True])
    assert result == dst


def test_reject_all_preserves_src() -> None:
    src = ["line1\n", "old\n", "line3\n"]
    dst = ["line1\n", "new\n", "line3\n"]
    result = _round_trip(src, dst, [False])
    assert result == src


def test_addition_inserted_at_correct_position() -> None:
    # New line added in the middle — must appear between its neighbours, not at EOF
    src = ["a\n", "b\n", "c\n"]
    dst = ["a\n", "b\n", "inserted\n", "c\n"]
    result = _round_trip(src, dst, [True])
    assert result == dst
    assert result.index("inserted\n") == 2


def test_duplicate_lines_not_over_removed() -> None:
    # File full of identical lines — only the targeted one should change
    src = ["x\n"] * 5
    dst = ["x\n", "x\n", "CHANGED\n", "x\n", "x\n"]
    result = _round_trip(src, dst, [True])
    assert result == dst


def test_partial_apply_two_hunks_accept_first() -> None:
    src = ["a\n"] + [f"ctx{i}\n" for i in range(8)] + ["b\n"]
    dst = ["A\n"] + [f"ctx{i}\n" for i in range(8)] + ["B\n"]
    result = _round_trip(src, dst, [True, False])
    assert result[0] == "A\n"           # first hunk applied
    assert result[-1] == "b\n"          # second hunk rejected


def test_partial_apply_two_hunks_accept_second() -> None:
    src = ["a\n"] + [f"ctx{i}\n" for i in range(8)] + ["b\n"]
    dst = ["A\n"] + [f"ctx{i}\n" for i in range(8)] + ["B\n"]
    result = _round_trip(src, dst, [False, True])
    assert result[0] == "a\n"           # first hunk rejected
    assert result[-1] == "B\n"          # second hunk applied


def test_apply_addition_only_hunk() -> None:
    src = ["a\n", "b\n"]
    dst = ["a\n", "extra\n", "b\n"]
    result = _round_trip(src, dst, [True])
    assert result == dst


def test_apply_deletion_only_hunk() -> None:
    src = ["a\n", "remove\n", "b\n"]
    dst = ["a\n", "b\n"]
    result = _round_trip(src, dst, [True])
    assert result == dst
