import pytest

from sample_order_system.view import table
from sample_order_system.view.colors import GREEN, RESET, colorize


def test_visible_len_ignores_ansi_codes():
    colored = colorize("ab", GREEN)
    assert table.visible_len(colored) == 2
    assert len(colored) > 2


def test_visible_len_counts_wide_hangul_chars_as_two_columns():
    # "여유" = 한글 2글자 = 터미널 표시 폭 4칸 (문자 개수 2가 아님)
    assert table.visible_len("여유") == 4


def test_pad_left_aligns_by_visible_length():
    assert table.pad("ab", 5) == "ab   "


def test_pad_right_aligns_by_visible_length():
    assert table.pad("ab", 5, align="right") == "   ab"


def test_pad_accounts_for_wide_chars_when_aligning():
    # "여유"는 표시 폭 4이므로 폭 6에 맞추면 공백 2칸만 추가되어야 한다.
    assert table.pad("여유", 6) == "여유  "


def test_pad_accounts_for_ansi_codes_when_aligning():
    colored = colorize("ab", GREEN)
    padded = table.pad(colored, 5)
    assert padded == f"{colored}   "
    assert table.visible_len(padded) == 5


def test_pad_does_not_truncate_when_text_exceeds_width():
    assert table.pad("longtext", 3) == "longtext"


def test_render_table_aligns_columns_by_widest_cell():
    lines = table.render_table(
        headers=["ID", "이름"],
        rows=[["S0001", "웨이퍼"], ["S0002", "매우긴이름시료"]],
    )
    header, separator, row1, row2 = lines
    assert table.visible_len(header) == table.visible_len(row1) == table.visible_len(row2)
    assert set(separator) == {"-"}


def test_render_table_keeps_alignment_with_colored_cells():
    colored_tier = colorize("고갈", GREEN)
    lines = table.render_table(
        headers=["이름", "상태"],
        rows=[["웨이퍼", colored_tier], ["매우긴이름시료", "여유"]],
    )
    body_lines = lines[2:]
    widths = {table.visible_len(line) for line in body_lines}
    assert len(widths) == 1  # 색상이 섞여도 보이는 폭은 모두 동일해야 함


def test_render_table_right_aligns_numeric_column():
    lines = table.render_table(
        headers=["상태", "수량"],
        rows=[["RESERVED", "1"], ["CONFIRMED", "120"]],
        aligns=["left", "right"],
    )
    assert lines[2].rstrip().endswith("1")
    assert lines[3].rstrip().endswith("120")


def test_render_table_raises_on_row_length_mismatch():
    with pytest.raises(ValueError):
        table.render_table(headers=["a", "b"], rows=[["1", "2", "3"]])


def test_render_table_raises_on_row_too_short():
    with pytest.raises(ValueError):
        table.render_table(headers=["a", "b"], rows=[["1"]])


def test_render_table_raises_on_aligns_length_mismatch():
    with pytest.raises(ValueError):
        table.render_table(headers=["a", "b"], rows=[["1", "2"]], aligns=["left"])
