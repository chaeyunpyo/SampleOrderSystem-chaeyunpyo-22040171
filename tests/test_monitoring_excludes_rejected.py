from sample_order_system.model.order import OrderStatus
from tests._helpers import make_controller, register_sample


def test_status_counts_exclude_rejected_orders(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)

    reserved = controller.order_controller.create_order(sample.sample_id, "고객A", 1)
    to_reject = controller.order_controller.create_order(sample.sample_id, "고객B", 2)
    controller.order_controller.reject_order(to_reject.order_id)

    counts = controller.monitoring_controller.count_by_status()

    assert "REJECTED" not in counts
    assert counts[OrderStatus.RESERVED.value]["count"] == 1
    assert counts[OrderStatus.RESERVED.value]["quantity"] == 1


def test_rejected_order_absent_from_all_status_buckets(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 3)
    controller.order_controller.reject_order(order.order_id)

    counts = controller.monitoring_controller.count_by_status()
    total_count = sum(bucket["count"] for bucket in counts.values())

    assert total_count == 0
