import pytest

from tests._helpers import make_controller, register_sample


def test_register_sample_rejects_blank_name(tmp_path):
    controller = make_controller(tmp_path)

    with pytest.raises(ValueError):
        controller.sample_controller.register_sample("  ", 2.0, 0.9)


def test_register_sample_rejects_non_positive_production_time(tmp_path):
    controller = make_controller(tmp_path)

    with pytest.raises(ValueError):
        controller.sample_controller.register_sample("웨이퍼", 0, 0.9)


def test_register_sample_rejects_yield_rate_out_of_range(tmp_path):
    controller = make_controller(tmp_path)

    with pytest.raises(ValueError):
        controller.sample_controller.register_sample("웨이퍼", 2.0, 1.5)


def test_create_order_rejects_non_positive_quantity(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)

    with pytest.raises(ValueError):
        controller.order_controller.create_order(sample.sample_id, "고객A", 0)


def test_create_order_rejects_unregistered_sample_id(tmp_path):
    controller = make_controller(tmp_path)

    with pytest.raises(ValueError):
        controller.order_controller.create_order("S9999", "고객A", 5)
