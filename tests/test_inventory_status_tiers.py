from sample_order_system.controller.monitoring_controller import MonitoringController


def test_stock_equal_to_pending_is_sufficient():
    assert MonitoringController._inventory_tier(stock_quantity=5, pending_qty=5) == "여유"


def test_stock_above_pending_is_sufficient():
    assert MonitoringController._inventory_tier(stock_quantity=10, pending_qty=5) == "여유"


def test_stock_one_below_pending_is_shortage():
    assert MonitoringController._inventory_tier(stock_quantity=4, pending_qty=5) == "부족"


def test_stock_zero_with_pending_is_depleted():
    assert MonitoringController._inventory_tier(stock_quantity=0, pending_qty=5) == "고갈"


def test_stock_zero_with_no_pending_is_sufficient():
    assert MonitoringController._inventory_tier(stock_quantity=0, pending_qty=0) == "여유"
