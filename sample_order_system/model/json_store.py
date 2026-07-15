from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_REPLACE_RETRIES = 5
_REPLACE_RETRY_DELAY_SECONDS = 0.05


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    _replace_with_retry(tmp_path, path)


def _replace_with_retry(tmp_path: Path, path: Path) -> None:
    """os.replace() can transiently fail on Windows (e.g. antivirus/indexer holding
    a brief lock on the just-written temp file). Retry a few times before giving up."""
    for attempt in range(_REPLACE_RETRIES):
        try:
            os.replace(tmp_path, path)
            return
        except PermissionError:
            if attempt == _REPLACE_RETRIES - 1:
                raise
            time.sleep(_REPLACE_RETRY_DELAY_SECONDS)


def next_prefixed_id(existing_ids: list[str], prefix: str, width: int = 4) -> str:
    max_seq = 0
    for existing_id in existing_ids:
        if not existing_id.startswith(prefix):
            continue
        suffix = existing_id[len(prefix):]
        if suffix.isdigit():
            max_seq = max(max_seq, int(suffix))
    return f"{prefix}{max_seq + 1:0{width}d}"
