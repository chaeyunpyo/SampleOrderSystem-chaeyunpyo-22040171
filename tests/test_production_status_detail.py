from sample_order_system.model.clock import FakeClock
from tests._helpers import make_controller, register_sample


def _approve_into_production(controller, sample, quantity, customer_name="고객A"):
    order = controller.order_controller.create_order(sample.sample_id, customer_name, quantity)
    return controller.order_controller.approve_order(order.order_id)


def test_active_status_includes_customer_and_quantity_breakdown(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = _approve_into_production(controller, sample, 3, customer_name="김철수")

    controller.production_controller.tick()  # activates it
    active = controller.production_controller.get_active_status()

    assert active["customer_name"] == "김철수"
    assert active["order_quantity"] == 3
    assert active["shortage_qty"] == 3
    assert active["target_qty"] == 3


def test_active_status_remaining_minutes_decreases_as_clock_advances(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    _approve_into_production(controller, sample, 3)  # total_time 6

    controller.production_controller.tick()
    assert controller.production_controller.get_active_status()["remaining_minutes"] == 6

    clock.advance(minutes=4)
    assert controller.production_controller.get_active_status()["remaining_minutes"] == 2

    clock.advance(minutes=10)  # overshoot: remaining should clamp at 0, not go negative
    assert controller.production_controller.get_active_status()["remaining_minutes"] == 0


def test_waiting_queue_status_reports_expected_wait_in_fifo_order(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)

    order1 = _approve_into_production(controller, sample, 3, customer_name="1번고객")  # total_time 6
    order2 = _approve_into_production(controller, sample, 2, customer_name="2번고객")  # total_time 4
    order3 = _approve_into_production(controller, sample, 1, customer_name="3번고객")  # total_time 2

    controller.production_controller.tick()  # activates order1, order2/order3 wait

    waiting = controller.production_controller.get_waiting_queue_status()

    assert [row["order_id"] for row in waiting] == [order2.order_id, order3.order_id]
    assert [row["position"] for row in waiting] == [1, 2]
    # order2 waits for order1's full remaining time (6, nothing elapsed yet)
    assert waiting[0]["expected_wait_minutes"] == 6
    # order3 waits for order1's remaining (6) + order2's own duration (4) = 10
    assert waiting[1]["expected_wait_minutes"] == 10
    assert waiting[0]["customer_name"] == "2번고객"


def test_waiting_queue_status_empty_when_nothing_waiting(tmp_path):
    controller = make_controller(tmp_path)
    register_sample(controller, stock=10)

    assert controller.production_controller.get_waiting_queue_status() == []
