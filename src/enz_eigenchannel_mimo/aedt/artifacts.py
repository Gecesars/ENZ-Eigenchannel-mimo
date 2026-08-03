"""Pacote rastreável de artefatos de uma execução AEDT."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    relative_path: str
    sha256: str
    bytes: int


class RunArtifactStore:
    def __init__(self, root: str | Path, run_id: str) -> None:
        self.root = Path(root).expanduser().resolve() / run_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id

    @staticmethod
    def timestamp_run_id(prefix: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{prefix}_{stamp}"

    def path(self, *parts: str) -> Path:
        target = self.root.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_json(self, relative_path: str, payload: Mapping[str, Any] | list[Any]) -> Path:
        target = self.path(relative_path)
        target.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        return target

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.path(relative_path)
        target.write_text(content, encoding="utf-8")
        return target

    def inventory(self) -> tuple[ArtifactRecord, ...]:
        records: list[ArtifactRecord] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            data = path.read_bytes()
            records.append(
                ArtifactRecord(
                    relative_path=str(path.relative_to(self.root)).replace("\\", "/"),
                    sha256=hashlib.sha256(data).hexdigest(),
                    bytes=len(data),
                )
            )
        return tuple(records)

    def finalize(self, manifest: Mapping[str, Any]) -> Path:
        first = self.write_json("manifest.json", dict(manifest))
        inventory = [asdict(record) for record in self.inventory() if record.relative_path != "inventory.json"]
        self.write_json("inventory.json", inventory)
        return first
