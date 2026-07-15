from __future__ import annotations

from sample_order_system.model.sample import Sample
from sample_order_system.model.sample_repository import SampleRepository


class SampleController:
    def __init__(self, repository: SampleRepository) -> None:
        self.repository = repository

    def register_sample(self, name: str, avg_production_time: float, yield_rate: float) -> Sample:
        if not name.strip():
            raise ValueError("시료 이름은 비어 있을 수 없습니다.")
        if avg_production_time <= 0:
            raise ValueError("평균 생산시간은 0보다 커야 합니다.")
        if not (0 < yield_rate <= 1):
            raise ValueError("수율은 0보다 크고 1 이하여야 합니다.")

        sample_id = self.repository.next_id()
        sample = Sample(
            sample_id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock_quantity=0,
        )
        return self.repository.create(sample)

    def list_samples(self) -> list[Sample]:
        return self.repository.list_all()

    def search_by_name(self, keyword: str) -> list[Sample]:
        return self.repository.search_by_name(keyword)
