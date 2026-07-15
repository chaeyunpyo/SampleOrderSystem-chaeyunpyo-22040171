from sample_order_system.model.sample import Sample
from sample_order_system.model.sample_repository import SampleRepository
from tests._helpers import make_controller, register_sample


def test_sample_ids_increment_sequentially_as_s_prefixed(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")

    first_id = repo.next_id()
    repo.create(Sample(sample_id=first_id, name="A", avg_production_time=1.0, yield_rate=0.9))
    second_id = repo.next_id()
    repo.create(Sample(sample_id=second_id, name="B", avg_production_time=1.0, yield_rate=0.9))

    assert first_id == "S0001"
    assert second_id == "S0002"


def test_order_ids_increment_sequentially_as_o_prefixed(tmp_path):
    controller = make_controller(tmp_path)
    sample = register_sample(controller, stock=10)

    order1 = controller.order_controller.create_order(sample.sample_id, "고객A", 1)
    order2 = controller.order_controller.create_order(sample.sample_id, "고객B", 1)

    assert order1.order_id == "O0001"
    assert order2.order_id == "O0002"


def test_next_id_resumes_correctly_after_reload_from_disk(tmp_path):
    data_path = tmp_path / "samples.json"
    repo = SampleRepository(data_path)
    repo.create(Sample(sample_id=repo.next_id(), name="A", avg_production_time=1.0, yield_rate=0.9))
    repo.create(Sample(sample_id=repo.next_id(), name="B", avg_production_time=1.0, yield_rate=0.9))

    reloaded_repo = SampleRepository(data_path)

    assert reloaded_repo.next_id() == "S0003"
