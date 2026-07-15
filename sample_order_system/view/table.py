from __future__ import annotations

import re
import unicodedata

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _char_width(ch: str) -> int:
    # 한글/한자 등 동아시아 넓은 문자(Wide/Fullwidth)는 대부분의 터미널에서
    # 고정폭 글꼴 기준으로 칸을 2개씩 차지한다. 문자 개수가 아니라 이 폭을
    # 기준으로 정렬해야 영문/숫자와 한글이 섞여도 열이 맞는다.
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def visible_len(text: str) -> int:
    """ANSI 색상 이스케이프 코드를 제외하고, 동아시아 넓은 문자 폭을 반영한
    실제 터미널 표시 폭을 구한다."""
    plain = _ANSI_RE.sub("", text)
    return sum(_char_width(ch) for ch in plain)


def pad(text: str, width: int, align: str = "left") -> str:
    extra = max(width - visible_len(text), 0)
    fill = " " * extra
    return (fill + text) if align == "right" else (text + fill)


def render_table(headers: list[str], rows: list[list[str]], aligns: list[str] | None = None) -> list[str]:
    """헤더/행을 색상 코드에 영향받지 않고 열 정렬된 문자열 리스트로 렌더링한다.
    각 셀은 미리 색상이 적용된 텍스트여도 무방하다."""
    aligns = aligns or ["left"] * len(headers)
    if len(aligns) != len(headers):
        raise ValueError(f"aligns 길이({len(aligns)})는 headers 길이({len(headers)})와 같아야 합니다.")
    for row in rows:
        if len(row) != len(headers):
            raise ValueError(f"행의 셀 개수({len(row)})가 headers 개수({len(headers)})와 다릅니다: {row}")

    widths = [visible_len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], visible_len(cell))

    def render_row(cells: list[str]) -> str:
        return "  ".join(pad(cell, widths[i], aligns[i]) for i, cell in enumerate(cells))

    header_line = render_row(headers)
    separator = "-" * visible_len(header_line)

    lines = [header_line, separator]
    lines.extend(render_row(row) for row in rows)
    return lines


def render_bar(percent: float, width: int = 20) -> str:
    """0~100 사이의 퍼센트를 `[████░░░░] 42.0%` 형태의 막대 문자열로 렌더링한다.
    범위를 벗어난 값은 0~100으로 clamp한다."""
    clamped = max(0.0, min(100.0, percent))
    filled = round(width * clamped / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {clamped:.1f}%"
