"""Atualiza o inventário SHA-256 global de ``poros_aedt``."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POROS = ROOT / "poros_aedt"
MANIFEST = POROS / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"JSON não é objeto: {path}")
    return data


def update() -> dict[str, Any]:
    if not POROS.is_dir():
        raise FileNotFoundError(POROS)
    ephemeral = [
        path
        for path in POROS.rglob("*")
        if path.is_file()
        and (path.name.endswith(".aedt.lock") or path.name.endswith(".semaphore"))
    ]
    versionable_ephemeral = [path for path in ephemeral if path.stat().st_size > 0]
    if versionable_ephemeral:
        raise ValueError(
            "locks não vazios não podem ser publicados: "
            + ", ".join(str(path) for path in versionable_ephemeral)
        )

    report_manifest_path = (
        POROS
        / "relatorios"
        / "Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v1.manifest.json"
    )
    reconstruction_manifest_path = (
        POROS
        / "reconstrucoes_exploratorias"
        / "G0_figura2_v7"
        / "manifest.json"
    )
    report = load_json(report_manifest_path)
    reconstruction = load_json(reconstruction_manifest_path)
    files = []
    for path in sorted(item for item in POROS.rglob("*") if item.is_file()):
        if path == MANIFEST or path in ephemeral:
            continue
        files.append(
            {
                "path": path.relative_to(POROS).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": "poros-aedt-package-v2",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "classificacao_resultado": "SIMULADO",
        "classificacao_geometria": "HIPÓTESE",
        "primary_source": {
            "doi": "10.1109/OJAP.2026.3703713",
            "authors": report["primary_source"]["authors"],
            "license": report["primary_source"]["license"],
        },
        "packages": {
            "m0_infrastructure_run": "ENZ-20260803-173105-52288067",
            "g0_exploratory_reconstruction": reconstruction["run_limpo"],
            "technical_report": report["report"]["sha256"],
        },
        "scientific_gates": {
            "m0_infrastructure": "PASS",
            "g0_waveport_axis_z": "PASS",
            "g0_adaptive_convergence": "PASS",
            "g0_strict_passivity": "FAIL",
            "g0_published_s11_correspondence": "FAIL",
            "global_reproduction_classification": "HIPÓTESE",
        },
        "ephemeral_files_excluded": [
            path.relative_to(POROS).as_posix() for path in ephemeral
        ],
        "arquivos": files,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    manifest = update()
    print(
        json.dumps(
            {
                "schema_version": manifest["schema_version"],
                "arquivos": len(manifest["arquivos"]),
                "ephemeral_files_excluded": manifest["ephemeral_files_excluded"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
