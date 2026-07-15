import json

from sample_order_system.model.clock import FakeClock
from sample_order_system.model.order import OrderStatus
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.sample import Sample
from sample_order_system.model.sample_repository import SampleRepository
from tests._helpers import make_controller, register_sample


def test_sample_data_persists_across_new_repository_instances(tmp_path):
    data_path = tmp_path / "samples.json"
    repo = SampleRepository(data_path)
    repo.create(Sample(sample_id="S0001", name="웨이퍼", avg_production_time=2.0, yield_rate=0.9, stock_quantity=3))

    reloaded_repo = SampleRepository(data_path)
    reloaded = reloaded_repo.get("S0001")

    assert reloaded.name == "웨이퍼"
    assert reloaded.stock_quantity == 3


def test_order_status_enum_round_trips_as_string(tmp_path):
    data_path = tmp_path / "orders.json"
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 5)
    controller.order_controller.approve_order(order.order_id)

    raw = json.loads(data_path.read_text(encoding="utf-8"))
    assert raw[0]["status"] == "CONFIRMED"

    reloaded_repo = OrderRepository(data_path)
    reloaded = reloaded_repo.get(order.order_id)
    assert reloaded.status == OrderStatus.CONFIRMED


def test_production_state_survives_restart_including_started_at(tmp_path):
    clock = FakeClock()
    controller = make_controller(tmp_path, clock=clock)
    sample = register_sample(controller, stock=0, avg_production_time=2.0, yield_rate=1.0)
    order = controller.order_controller.create_order(sample.sample_id, "고객A", 3)
    controller.order_controller.approve_order(order.order_id)
    controller.production_controller.tick()  # activates the item, sets started_at

    active_before = controller.production_controller.get_active_status()

    # 앱 재시작 시뮬레이션: 같은 데이터 경로로 새 MainController 생성
    restarted = make_controller(tmp_path, clock=clock)
    active_after = restarted.production_controller.get_active_status()

    assert active_after is not None
    assert active_after["order_id"] == active_before["order_id"]
    assert active_after["elapsed_minutes"] == active_before["elapsed_minutes"]


def test_atomic_write_leaves_valid_json_after_repeated_saves(tmp_path):
    data_path = tmp_path / "samples.json"
    repo = SampleRepository(data_path)
    from sample_order_system.model.sample import Sample

    for i in range(5):
        repo.create(Sample(sample_id=f"S{i:04d}", name=f"샘플{i}", avg_production_time=1.0, yield_rate=0.9))

    assert data_path.exists()
    assert not data_path.with_suffix(".json.tmp").exists()
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    assert len(raw) == 5
