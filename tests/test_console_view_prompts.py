import builtins

import pytest

from sample_order_system.view.console_view import ConsoleView


@pytest.fixture
def view():
    # 입력 헬퍼는 self.controller를 쓰지 않으므로 MainController를 구성할 필요가 없다.
    return ConsoleView.__new__(ConsoleView)


def _feed_inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(iterator))


def test_read_required_returns_none_on_blank_input(view, monkeypatch):
    _feed_inputs(monkeypatch, [""])
    assert view._read_required("이름") is None


def test_read_required_returns_stripped_value(view, monkeypatch):
    _feed_inputs(monkeypatch, ["  웨이퍼  "])
    assert view._read_required("이름") == "웨이퍼"


def test_read_int_retries_on_invalid_then_succeeds(view, monkeypatch):
    _feed_inputs(monkeypatch, ["abc", "5"])
    assert view._read_int("수량") == 5


def test_read_int_returns_none_on_blank_input(view, monkeypatch):
    _feed_inputs(monkeypatch, [""])
    assert view._read_int("수량") is None


def test_read_float_retries_on_invalid_then_succeeds(view, monkeypatch):
    _feed_inputs(monkeypatch, ["not-a-number", "2.5"])
    assert view._read_float("생산시간") == 2.5


def test_read_float_returns_none_on_blank_input(view, monkeypatch):
    _feed_inputs(monkeypatch, [""])
    assert view._read_float("생산시간") is None
