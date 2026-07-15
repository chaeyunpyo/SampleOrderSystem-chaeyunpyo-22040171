from __future__ import annotations

import ctypes
import os

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"

RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"

STATUS_COLORS = {
    "RESERVED": YELLOW,
    "CONFIRMED": CYAN,
    "PRODUCING": MAGENTA,
    "RELEASE": GREEN,
    "REJECTED": DIM,
}

TIER_COLORS = {
    "여유": GREEN,
    "부족": YELLOW,
    "고갈": RED,
}


def enable_windows_ansi() -> None:
    """Windows 콘솔에서 ANSI 이스케이프 코드를 해석하도록 활성화한다.
    실패해도(구버전 콘솔 등) 조용히 무시 — 이 경우 이스케이프 코드가 그대로 출력될 뿐,
    앱 동작에는 영향이 없다."""
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return
        kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except OSError:
        pass


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def status_text(status: str) -> str:
    return colorize(status, STATUS_COLORS.get(status, ""))


def tier_text(tier: str) -> str:
    return colorize(tier, TIER_COLORS.get(tier, ""))


def success(text: str) -> str:
    return colorize(text, GREEN)


def failure(text: str) -> str:
    return colorize(text, RED)


def muted(text: str) -> str:
    return colorize(text, DIM)
