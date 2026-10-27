import json
import os
import shutil
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

RecordT = TypeVar("RecordT", bound=BaseModel)


class JsonFileStore(Generic[RecordT]):
    """Reads and writes a JSON array of records, validated with a Pydantic model."""

    def __init__(self, path: Path, model: type[RecordT]):
        self.path = path
        self.model = model

    def read_all(self) -> list[RecordT]:
        raw_records = json.loads(self.path.read_text(encoding="utf-8"))
        return [self.model.model_validate(raw) for raw in raw_records]

    def write_all(self, records: list[RecordT]) -> None:
        # Write to a temp file and swap it in, so a crash never leaves a half-written file.
        payload = [record.model_dump(mode="json") for record in records]
        tmp_path = self.path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp_path, self.path)


def ensure_data_files(data_dir: Path, seed_dir: Path) -> None:
    """Copy the seed files into the data directory the first time the app runs."""
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in ("employees.json", "leave_requests.json"):
        target = data_dir / name
        if not target.exists():
            shutil.copyfile(seed_dir / name, target)
