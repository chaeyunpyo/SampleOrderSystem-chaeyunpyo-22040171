from sample_order_system.model.production_queue import ProductionQueueItem


def test_actual_production_qty_ceils_when_not_divisible():
    item = ProductionQueueItem(
        order_id="O0001", sample_id="S0001", shortage_qty=5,
        avg_production_time=2.0, yield_rate=0.9,
    )
    # ceil(5 / 0.9) = ceil(5.555...) = 6
    assert item.actual_production_qty == 6


def test_actual_production_qty_exact_when_divisible():
    item = ProductionQueueItem(
        order_id="O0001", sample_id="S0001", shortage_qty=9,
        avg_production_time=2.0, yield_rate=0.9,
    )
    # ceil(9 / 0.9) = ceil(10.0) = 10
    assert item.actual_production_qty == 10


def test_total_production_time_equals_avg_time_times_actual_qty():
    item = ProductionQueueItem(
        order_id="O0001", sample_id="S0001", shortage_qty=5,
        avg_production_time=3.5, yield_rate=0.9,
    )
    assert item.total_production_time == 3.5 * item.actual_production_qty


def test_yield_rate_one_actual_qty_equals_shortage():
    item = ProductionQueueItem(
        order_id="O0001", sample_id="S0001", shortage_qty=7,
        avg_production_time=2.0, yield_rate=1.0,
    )
    assert item.actual_production_qty == 7
