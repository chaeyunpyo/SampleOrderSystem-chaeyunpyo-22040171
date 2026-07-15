import pytest

from sample_order_system.model.errors import DataIntegrityError
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.production_state_repository import ProductionStateRepository
from sample_order_system.model.sample_repository import SampleRepository


def test_sample_repository_raises_data_integrity_error_on_malformed_json(tmp_path):
    data_path = tmp_path / "samples.json"
    data_path.write_text("not valid json {{{", encoding="utf-8")

    with pytest.raises(DataIntegrityError):
        SampleRepository(data_path)


def test_sample_repository_raises_data_integrity_error_on_missing_field(tmp_path):
    data_path = tmp_path / "samples.json"
    data_path.write_text('[{"name": "웨이퍼"}]', encoding="utf-8")  # sample_id 누락

    with pytest.raises(DataIntegrityError):
        SampleRepository(data_path)


def test_sample_repository_coerces_numeric_fields_stored_as_strings(tmp_path):
    data_path = tmp_path / "samples.json"
    data_path.write_text(
        '[{"sample_id": "S0001", "name": "웨이퍼", "avg_production_time": "2.0", '
        '"yield_rate": "0.9", "stock_quantity": "5"}]',
        encoding="utf-8",
    )

    repo = SampleRepository(data_path)
    sample = repo.get("S0001")
    assert sample.avg_production_time == 2.0
    assert sample.yield_rate == 0.9
    assert sample.stock_quantity == 5


def test_order_repository_raises_data_integrity_error_on_malformed_json(tmp_path):
    data_path = tmp_path / "orders.json"
    data_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(DataIntegrityError):
        OrderRepository(data_path)


def test_order_repository_raises_data_integrity_error_on_invalid_status(tmp_path):
    data_path = tmp_path / "orders.json"
    data_path.write_text(
        '[{"order_id": "O0001", "sample_id": "S0001", "customer_name": "A", '
        '"quantity": 1, "status": "NOT_A_REAL_STATUS", "created_at": "2026-01-01T00:00:00"}]',
        encoding="utf-8",
    )

    with pytest.raises(DataIntegrityError):
        OrderRepository(data_path)


def test_order_repository_raises_data_integrity_error_on_invalid_datetime(tmp_path):
    data_path = tmp_path / "orders.json"
    data_path.write_text(
        '[{"order_id": "O0001", "sample_id": "S0001", "customer_name": "A", '
        '"quantity": 1, "status": "RESERVED", "created_at": "not-a-date"}]',
        encoding="utf-8",
    )

    with pytest.raises(DataIntegrityError):
        OrderRepository(data_path)


def test_production_state_repository_raises_on_queue_not_a_list(tmp_path):
    data_path = tmp_path / "production_state.json"
    data_path.write_text('{"queue": "not-a-list", "active": null}', encoding="utf-8")

    with pytest.raises(DataIntegrityError):
        ProductionStateRepository(data_path).load()


def test_production_state_repository_raises_on_active_missing_fields(tmp_path):
    data_path = tmp_path / "production_state.json"
    data_path.write_text('{"queue": [], "active": {"order_id": "O0001"}}', encoding="utf-8")

    with pytest.raises(DataIntegrityError):
        ProductionStateRepository(data_path).load()
