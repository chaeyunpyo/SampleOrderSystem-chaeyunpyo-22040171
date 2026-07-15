from __future__ import annotations

from pathlib import Path

from sample_order_system.model.json_store import load_json, next_prefixed_id, save_json_atomic
from sample_order_system.model.sample import Sample

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "samples.json"


class SampleNotFoundError(Exception):
    pass


class SampleRepository:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self._samples: dict[str, Sample] = {}
        self._load()

    def _load(self) -> None:
        raw = load_json(self.data_path, default=[])
        self._samples = {item["sample_id"]: Sample.from_dict(item) for item in raw}

    def _save(self) -> None:
        save_json_atomic(self.data_path, [sample.to_dict() for sample in self._samples.values()])

    def next_id(self) -> str:
        return next_prefixed_id(list(self._samples.keys()), prefix="S")

    def create(self, sample: Sample) -> Sample:
        self._samples[sample.sample_id] = sample
        self._save()
        return sample

    def get(self, sample_id: str) -> Sample:
        try:
            return self._samples[sample_id]
        except KeyError:
            raise SampleNotFoundError(f"존재하지 않는 시료입니다: {sample_id}") from None

    def list_all(self) -> list[Sample]:
        return list(self._samples.values())

    def search_by_name(self, keyword: str) -> list[Sample]:
        keyword_lower = keyword.lower()
        return [s for s in self._samples.values() if keyword_lower in s.name.lower()]

    def save(self, sample: Sample) -> Sample:
        self._samples[sample.sample_id] = sample
        self._save()
        return sample
