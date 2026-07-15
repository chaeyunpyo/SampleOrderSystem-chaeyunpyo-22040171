from sample_order_system.model.clock import FakeClock
from tests._helpers import make_controller, register_sample


def test_tick_discards_active_item_whose_order_no_longer_exists(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    controller.production_controller.tick()  # 활성화
    clock.advance(minutes=10)

    # 데이터 손상/수동 편집 상황 시뮬레이션: 참조 중인 주문이 사라짐
    controller.order_repository._orders.clear()
    controller.order_repository._save()

    completed = controller.production_controller.tick()  # 크래시하지 않고 항목을 폐기해야 함

    assert completed == []
    assert controller.production_controller.get_active_status() is None


def test_get_active_status_returns_none_when_referenced_sample_missing(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)
    controller.production_controller.tick()  # 활성화

    controller.sample_repository._samples.clear()
    controller.sample_repository._save()

    assert controller.production_controller.get_active_status() is None


def test_get_waiting_queue_status_skips_entries_with_missing_references(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order1 = controller.order_controller.create_order(sample.sample_id, "고객A", 3)
    order2 = controller.order_controller.create_order(sample.sample_id, "고객B", 2)
    controller.order_controller.approve_order(order1.order_id)
    controller.order_controller.approve_order(order2.order_id)
    controller.production_controller.tick()  # order1 활성화, order2 대기

    # order2를 삭제해서 대기 큐 항목의 참조를 깨뜨림
    del controller.order_repository._orders[order2.order_id]
    controller.order_repository._save()

    waiting = controller.production_controller.get_waiting_queue_status()

    assert waiting == []
