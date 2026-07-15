from sample_order_system.model.clock import FakeClock
from tests._helpers import make_controller, register_sample


def test_approve_sufficient_stock_deducts_immediately(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    controller.order_controller.approve_order(order.order_id)

    updated = controller.sample_repository.get(sample.sample_id)
    assert updated.stock_quantity == 5


def test_approve_insufficient_stock_reserves_existing_stock_immediately(tmp_path):
    """부족 승인 시 남아있던 재고 전량을 즉시 이 주문에 선점(0으로) 시켜야
    같은 시료의 다른 주문이 동일 재고를 이중으로 사용하지 못한다
    (겹치는 주문 시나리오는 tests/test_overlapping_orders_stock.py 참고)."""
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=2)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)

    controller.order_controller.approve_order(order.order_id)

    updated = controller.sample_repository.get(sample.sample_id)
    assert updated.stock_quantity == 0


def test_production_completion_net_change_is_actual_qty_minus_order_qty(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=2, avg_production_time=2.0, yield_rate=0.5)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    # shortage = 5 - 2 = 3, actual_production_qty = ceil(3/0.5) = 6, total_production_time = 2*6 = 12
    controller.production_controller.tick()  # activates the item
    clock.advance(minutes=12)
    controller.production_controller.tick()  # completes it

    updated_sample = controller.sample_repository.get(sample.sample_id)
    # net change: stock(2) + actual(6) - order.quantity(5) = 3
    assert updated_sample.stock_quantity == 3


def test_ship_order_does_not_change_stock(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    before = controller.sample_repository.get(sample.sample_id).stock_quantity
    controller.shipping_controller.ship_order(order.order_id)
    after = controller.sample_repository.get(sample.sample_id).stock_quantity

    assert before == after == 5
