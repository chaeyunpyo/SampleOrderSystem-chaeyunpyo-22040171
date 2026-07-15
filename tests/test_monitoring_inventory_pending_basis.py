from tests._helpers import make_controller, register_sample


def test_confirmed_orders_do_not_count_toward_pending_qty(tmp_path):
    """회귀 테스트: 0014 이후 CONFIRMED 주문은 승인 시점에 이미 재고에서
    선점·차감이 끝난 확정분이므로, 재고 부족 판정에 다시 반영되면 안 된다.
    수정 전에는 재고 10에서 8개를 승인(CONFIRMED)하면 남은 재고 2 < 8을
    기준으로 '부족'으로 잘못 표시됐다."""
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 8)
    controller.order_controller.approve_order(order.order_id)  # 재고 충분 -> 즉시 CONFIRMED

    report = controller.monitoring_controller.inventory_status()[0]

    assert report["pending_qty"] == 0
    assert report["tier"] == "여유"


def test_reserved_orders_count_toward_pending_qty(tmp_path):
    """RESERVED 주문(아직 재고 미확보 수요)은 여전히 부족 판정에 반영돼야 한다."""
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=2)
    controller.order_controller.create_order(sample.sample_id, "고객A", 5)  # 승인 안 함, RESERVED 유지

    report = controller.monitoring_controller.inventory_status()[0]

    assert report["pending_qty"] == 5
    assert report["tier"] == "부족"
