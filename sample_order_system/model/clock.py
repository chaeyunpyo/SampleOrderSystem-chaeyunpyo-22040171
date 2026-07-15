from __future__ import annotations

from datetime import datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()


class FakeClock:
    def __init__(self, start: datetime | None = None) -> None:
        self._current = start or datetime(2026, 1, 1)

    def now(self) -> datetime:
        return self._current

    def advance(self, *, minutes: float = 0, seconds: float = 0) -> None:
        self._current += timedelta(minutes=minutes, seconds=seconds)

    def set(self, dt: datetime) -> None:
        self._current = dt
