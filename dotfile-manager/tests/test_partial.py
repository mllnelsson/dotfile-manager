from dotfile_manager.ops._partial import _apply_selected_hunks, _split_into_hunks


def test_split_into_hunks_empty() -> None:
    assert _split_into_hunks([]) == []


def test_split_into_hunks_no_changes() -> None:
    lines = [" context\n", " more context\n"]
    assert _split_into_hunks(lines) == []


def test_split_into_hunks_single_change() -> None:
    lines = ["-old line\n", "+new line\n"]
    hunks = _split_into_hunks(lines)
    assert len(hunks) == 1
    assert "-old line\n" in hunks[0]
    assert "+new line\n" in hunks[0]


def test_split_into_hunks_multiple_changes() -> None:
    lines = [
        "-first removed\n",
        "+first added\n",
        " context1\n",
        " context2\n",
        " context3\n",
        " context4\n",  # gap > 3 lines of context
        "-second removed\n",
        "+second added\n",
    ]
    hunks = _split_into_hunks(lines)
    assert len(hunks) == 2


def test_apply_selected_hunks_all_accepted() -> None:
    original = ["line1\n", "old line\n", "line3\n"]
    hunks = [["-old line\n", "+new line\n"]]
    result = _apply_selected_hunks(original, hunks, [True])
    assert "new line\n" in result
    assert "old line\n" not in result


def test_apply_selected_hunks_all_rejected() -> None:
    original = ["line1\n", "old line\n", "line3\n"]
    hunks = [["-old line\n", "+new line\n"]]
    result = _apply_selected_hunks(original, hunks, [False])
    assert "old line\n" in result
    assert "new line\n" not in result


def test_apply_selected_hunks_partial_selection() -> None:
    original = ["line1\n", "remove1\n", "line3\n", "remove2\n"]
    hunks = [
        ["-remove1\n", "+add1\n"],
        ["-remove2\n", "+add2\n"],
    ]
    result = _apply_selected_hunks(original, hunks, [True, False])
    assert "add1\n" in result
    assert "remove1\n" not in result
    assert "remove2\n" in result
    assert "add2\n" not in result
