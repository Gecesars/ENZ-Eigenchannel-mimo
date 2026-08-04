from __future__ import annotations

import json
from pathlib import Path

from enz_eigenchannel_mimo.q0_audit import (
    Q0_STATUS_BLOCKED,
    REQUIRED_RADIATORS,
    auditar_q0,
    escrever_auditoria,
)

ROOT = Path(__file__).resolve().parents[1]


def test_q0_bloqueia_sem_quatro_manifestos_validados() -> None:
    missing, inventory = auditar_q0(ROOT)
    assert missing["status"] == Q0_STATUS_BLOCKED
    assert missing["classification"] == "DESCONHECIDO"
    assert missing["validated_instances_found"] == 0
    assert [item["id"] for item in missing["component_status"]] == list(
        REQUIRED_RADIATORS
    )
    assert all(not item["validated"] for item in missing["component_status"])
    assert len(missing["aedt_candidates"]) >= 3
    assert all(
        not item["eligible_as_validated_radiator"]
        for item in missing["aedt_candidates"]
    )
    assert inventory["file_count"] >= len(missing["aedt_candidates"])


def test_q0_escreve_jsons_reprodutiveis(tmp_path: Path) -> None:
    missing_path, inventory_path = escrever_auditoria(ROOT, tmp_path)
    missing = json.loads(missing_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert missing["gate"] == "Q0"
    assert inventory["schema"].endswith("q0-artifact-inventory/v1")
    assert all(len(item["sha256"]) == 64 for item in inventory["files"])


def test_inspecao_hfss_q0_preserva_projeto_e_nao_silencia_excecoes() -> None:
    inspection_path = ROOT / "artefatos" / "q0" / "hfss_inspection" / "hfss_inspection.json"
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
    assert inspection["runtime"]["build"] == "2024.2.0"
    assert inspection["runtime"]["pyaedt"] == "1.3.0"
    assert inspection["project"]["unchanged_by_inspection"] is True
    assert inspection["project"]["sha256_before_open"] == inspection["project"][
        "sha256_after_inspection"
    ]
    assert inspection["counts"]["excitations"] == 1
    assert inspection["counts"]["reports"] == 8
    assert inspection["counts"]["field_plots"] == 8
    assert inspection["extraction_errors"] == []
