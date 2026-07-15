import pytest

from tools.run_monitor import run


def test_negative_interval_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        run(data_dir=tmp_path, interval=-1, once=False)


def test_zero_interval_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        run(data_dir=tmp_path, interval=0, once=False)


def test_negative_interval_allowed_when_once(tmp_path):
    # --once면 sleep을 쓰지 않으므로 interval 값이 무의미 -> 검증하지 않는다.
    run(data_dir=tmp_path, interval=-1, once=True)
