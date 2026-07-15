from sample_order_system.model.clock import FakeClock
from tests._helpers import make_controller, register_sample


def test_two_insufficient_orders_on_same_sample_never_go_negative(tmp_path):
    """회귀 테스트: 같은 시료에 대해 재고 부족 주문 2건이 겹치면, 수정 전에는
    두 생산이 모두 완료된 뒤 재고가 음수로 떨어졌다 (2 -> 0 -> -2)."""
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=2, avg_production_time=2.0, yield_rate=1.0)

    order1 = controller.order_controller.create_order(sample.sample_id, "고객A", 5)  # shortage 3
    order2 = controller.order_controller.create_order(sample.sample_id, "고객B", 3)  # shortage 3 (재고 이미 선점됨)

    controller.order_controller.approve_order(order1.order_id)
    assert controller.sample_repository.get(sample.sample_id).stock_quantity == 0

    controller.order_controller.approve_order(order2.order_id)
    assert controller.sample_repository.get(sample.sample_id).stock_quantity == 0

    controller.production_controller.tick()  # order1 활성화
    clock.advance(minutes=6)  # order1 total_time = 2*3 = 6
    controller.production_controller.tick()  # order1 완료, order2 활성화

    assert controller.sample_repository.get(sample.sample_id).stock_quantity == 0

    clock.advance(minutes=6)  # order2 total_time = 2*3 = 6
    controller.production_controller.tick()  # order2 완료

    final_stock = controller.sample_repository.get(sample.sample_id).stock_quantity
    assert final_stock == 0
    assert final_stock >= 0


def test_sufficient_order_cannot_steal_stock_already_reserved_by_pending_production(tmp_path):
    """회귀 테스트: 부족 주문이 생산 대기 중인 상태에서 같은 시료의 다른 주문이
    아직 안 줄어든 재고를 기준으로 '충분'하다고 잘못 승인되는 것을 방지."""
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=10, avg_production_time=2.0, yield_rate=1.0)

    order_a = controller.order_controller.create_order(sample.sample_id, "고객A", 15)  # shortage 5
    approved_a = controller.order_controller.approve_order(order_a.order_id)
    assert approved_a.status.value == "PRODUCING"
    assert controller.sample_repository.get(sample.sample_id).stock_quantity == 0

    order_b = controller.order_controller.create_order(sample.sample_id, "고객B", 8)
    approved_b = controller.order_controller.approve_order(order_b.order_id)
    # 재고가 이미 0으로 선점되어 있으므로 B도 부족 판정을 받아 생산 큐로 가야 한다.
    assert approved_b.status.value == "PRODUCING"

    controller.production_controller.tick()  # order_a 활성화
    clock.advance(minutes=10)  # order_a total_time = 2*5 = 10
    controller.production_controller.tick()  # order_a 완료, order_b 활성화
    clock.advance(minutes=16)  # order_b total_time = 2*8 = 16
    controller.production_controller.tick()  # order_b 완료

    final_stock = controller.sample_repository.get(sample.sample_id).stock_quantity
    assert final_stock == 0
    assert final_stock >= 0
