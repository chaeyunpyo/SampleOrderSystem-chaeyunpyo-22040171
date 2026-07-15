import pytest

from sample_order_system.model.order import OrderStatus
from tests._helpers import make_controller, register_sample


def test_reject_order_from_reserved_moves_to_rejected(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    rejected = controller.order_controller.reject_order(order.order_id)

    assert rejected.status == OrderStatus.REJECTED


def test_approve_order_sufficient_stock_moves_to_confirmed(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    approved = controller.order_controller.approve_order(order.order_id)

    assert approved.status == OrderStatus.CONFIRMED


def test_approve_order_insufficient_stock_moves_to_producing(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=2)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    approved = controller.order_controller.approve_order(order.order_id)

    assert approved.status == OrderStatus.PRODUCING


def test_approve_rejected_order_raises_value_error(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.reject_order(order.order_id)

    with pytest.raises(ValueError):
        controller.order_controller.approve_order(order.order_id)


def test_reject_confirmed_order_raises_value_error(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    with pytest.raises(ValueError):
        controller.order_controller.reject_order(order.order_id)


def test_ship_order_not_confirmed_raises_value_error(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    with pytest.raises(ValueError):
        controller.shipping_controller.ship_order(order.order_id)


def test_ship_confirmed_order_moves_to_release(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    released = controller.shipping_controller.ship_order(order.order_id)

    assert released.status == OrderStatus.RELEASE
