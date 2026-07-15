import pytest

from sample_order_system.model.order import OrderStatus
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.sample_repository import SampleRepository
from tools.dummy_data_generator import DUMMY_ORDER_STATUSES, run


def test_generates_requested_counts(tmp_path):
    run(samples_count=5, orders_count=8, reset=False, data_dir=tmp_path)

    samples = SampleRepository(tmp_path / "samples.json").list_all()
    orders = OrderRepository(tmp_path / "orders.json").list_all()

    assert len(samples) == 5
    assert len(orders) == 8


def test_reset_wipes_existing_data_before_generating(tmp_path):
    run(samples_count=3, orders_count=3, reset=False, data_dir=tmp_path)
    run(samples_count=2, orders_count=2, reset=True, data_dir=tmp_path)

    samples = SampleRepository(tmp_path / "samples.json").list_all()
    orders = OrderRepository(tmp_path / "orders.json").list_all()

    assert len(samples) == 2
    assert len(orders) == 2


def test_without_reset_appends_and_continues_id_sequence(tmp_path):
    run(samples_count=2, orders_count=2, reset=False, data_dir=tmp_path)
    run(samples_count=3, orders_count=3, reset=False, data_dir=tmp_path)

    samples = SampleRepository(tmp_path / "samples.json").list_all()
    orders = OrderRepository(tmp_path / "orders.json").list_all()

    assert len(samples) == 5
    assert len(orders) == 5
    sample_ids = sorted(s.sample_id for s in samples)
    assert sample_ids == ["S0001", "S0002", "S0003", "S0004", "S0005"]


def test_dummy_orders_never_use_producing_status(tmp_path):
    run(samples_count=5, orders_count=50, reset=False, data_dir=tmp_path)

    orders = OrderRepository(tmp_path / "orders.json").list_all()

    assert OrderStatus.PRODUCING not in DUMMY_ORDER_STATUSES
    assert all(o.status != OrderStatus.PRODUCING for o in orders)


def test_negative_samples_count_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        run(samples_count=-1, orders_count=5, reset=False, data_dir=tmp_path)


def test_negative_orders_count_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        run(samples_count=5, orders_count=-1, reset=False, data_dir=tmp_path)
