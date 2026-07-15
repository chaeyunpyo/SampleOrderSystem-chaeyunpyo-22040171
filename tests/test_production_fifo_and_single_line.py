from sample_order_system.model.clock import FakeClock
from sample_order_system.model.order import OrderStatus
from tests._helpers import make_controller, register_sample


def _approve_into_production(controller, sample, quantity):
    order = controller.order_controller.create_order(sample.sample_id, "고객A", quantity)
    return controller.order_controller.approve_order(order.order_id)


def test_multiple_producing_orders_complete_in_fifo_order(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)

    order1 = _approve_into_production(controller, sample, 3)  # shortage 3, total_time 6
    order2 = _approve_into_production(controller, sample, 2)  # shortage 2, total_time 4

    controller.production_controller.tick()  # activates order1
    clock.advance(minutes=6)
    completed_first = controller.production_controller.tick()  # completes order1, activates order2
    clock.advance(minutes=4)
    completed_second = controller.production_controller.tick()  # completes order2

    assert [o.order_id for o in completed_first] == [order1.order_id]
    assert [o.order_id for o in completed_second] == [order2.order_id]


def test_only_one_order_active_at_a_time(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)

    _approve_into_production(controller, sample, 3)
    _approve_into_production(controller, sample, 2)

    controller.production_controller.tick()

    active = controller.production_controller.get_active_status()
    waiting = controller.production_controller.get_waiting_queue()
    assert active is not None
    assert len(waiting) == 1


def test_tick_before_due_time_does_not_complete(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = _approve_into_production(controller, sample, 3)  # total_time 6

    controller.production_controller.tick()
    clock.advance(minutes=5)
    completed = controller.production_controller.tick()

    assert completed == []
    assert controller.order_repository.get(order.order_id).status == OrderStatus.PRODUCING


def test_tick_after_exact_due_time_completes(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = _approve_into_production(controller, sample, 3)  # total_time 6

    controller.production_controller.tick()
    clock.advance(minutes=6)
    completed = controller.production_controller.tick()

    assert [o.order_id for o in completed] == [order.order_id]
    assert controller.order_repository.get(order.order_id).status == OrderStatus.CONFIRMED


def test_second_item_needs_its_own_full_duration_after_activating(tmp_path):
    """단일 생산 라인 제약: 큐가 밀려 있어도, 새로 활성화된 항목은 자신의 생산시간만큼
    다시 경과해야 완료된다 — 이전 항목이 밀린 시간을 이어받지 않는다."""
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)

    order1 = _approve_into_production(controller, sample, 3)  # total_time 6
    order2 = _approve_into_production(controller, sample, 2)  # total_time 4

    controller.production_controller.tick()  # activates order1
    clock.advance(minutes=100)  # far overdue
    completed = controller.production_controller.tick()

    # order1 completes, order2 becomes active but has NOT had its own time elapse yet
    assert [o.order_id for o in completed] == [order1.order_id]
    assert controller.order_repository.get(order2.order_id).status == OrderStatus.PRODUCING
    active = controller.production_controller.get_active_status()
    assert active["order_id"] == order2.order_id
    assert active["elapsed_minutes"] == 0
