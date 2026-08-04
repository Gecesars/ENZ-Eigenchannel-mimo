from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "doc"
    / "pdfs"
    / "Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v3.manifest.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_relatorio_tecnico_publicado_e_integro() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = data["report"]
    pdf = ROOT / report["path"]
    poros = ROOT / "poros_aedt" / "relatorios" / pdf.name

    assert data["classification"] == "HIPÓTESE"
    assert data["primary_source"]["doi"] == "10.1109/OJAP.2026.3703713"
    assert data["primary_source"]["license"] == "CC BY 4.0"
    assert pdf.is_file()
    assert poros.is_file()
    assert pdf.stat().st_size == report["bytes"]
    assert _sha256(pdf) == report["sha256"]
    assert _sha256(poros) == report["sha256"]
    assert report["pages"] >= 99
    assert report["extracted_words"] >= 2 * data["primary_source"]["metrics"]["words"]
    assert report["technical_elements"] >= 2 * data["primary_source"]["metrics"]["elements"]
    assert all(report["gates"].values())


def test_fontes_do_relatorio_estao_versionaveis_e_integras() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for source in data["sources"]:
        path = ROOT / source["path"]
        assert path.is_file(), source["path"]
        assert path.stat().st_size == source["bytes"], source["path"]
        assert _sha256(path) == source["sha256"], source["path"]


def test_gates_cientificos_nao_sao_promovidos_silenciosamente() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    gates = data["scientific_gates"]
    assert gates["waveport_integration_axis_z"] == "PASS"
    assert gates["adaptive_convergence"] == "PASS"
    assert gates["strict_passivity"] == "FAIL"
    assert gates["published_s11_correspondence"] == "FAIL"
    assert gates["global_reproduction_classification"] == "HIPÓTESE"
    assert gates["q0_validated_radiators"] == "BLOCKED_MISSING_VALIDATED_ARTIFACTS"
    assert gates["q0_validated_instances"] == "0/4"
    assert gates["q4_adaptive_convergence"] == "PASS"
    assert gates["q4_strict_passivity"] == "PASS"
    assert gates["q4_s11_matching"] == "FAIL"
    assert gates["q4_s22_matching"] == "FAIL"
    assert gates["q4_complex_embedded_patterns"] == "PASS"
    assert gates["q4_mimo_claim"] == "BLOCKED_SOURCE_MODEL_HIPOTESE"
    assert gates["mimo2x2_system_classification"] == "HIPÓTESE"


def test_manifesto_global_poros_aedt() -> None:
    manifest_path = ROOT / "poros_aedt" / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "poros-aedt-package-v2"
    assert data["classificacao_geometria"] == "HIPÓTESE"
    assert data["scientific_gates"]["g0_strict_passivity"] == "FAIL"
    assert data["scientific_gates"]["g0_published_s11_correspondence"] == "FAIL"
    assert data["scientific_gates"]["q0_validated_instances"] == "0/4"
    assert data["scientific_gates"]["q4_adaptive_convergence"] == "PASS"
    assert data["scientific_gates"]["q4_s11_matching"] == "FAIL"
    assert data["scientific_gates"]["q4_s22_matching"] == "FAIL"
    assert data["scientific_gates"]["mimo_2x2_system"] == "HIPÓTESE"

    paths = [item["path"] for item in data["arquivos"]]
    assert len(paths) == len(set(paths))
    assert not any(path.endswith((".aedt.lock", ".semaphore")) for path in paths)
    assert not set(data["ephemeral_files_excluded"]) & set(paths)
    assert not set(data["active_session_generated_files_excluded"]) & set(paths)
    cache_paths = {
        item["path"] for item in data["nonportable_solver_cache_excluded"]
    }
    assert cache_paths
    assert not cache_paths & set(paths)
    for item in data["arquivos"]:
        path = ROOT / "poros_aedt" / item["path"]
        assert path.is_file(), item["path"]
        assert path.stat().st_size == item["bytes"], item["path"]
        assert _sha256(path) == item["sha256"], item["path"]
