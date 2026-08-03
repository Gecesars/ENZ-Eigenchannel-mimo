from pathlib import Path
from enz_eigenchannel_mimo.aedt.validation import preflight_offline
from enz_eigenchannel_mimo.geometry import VarianteModelo, build_geometry_plan, engineering_smoke_seed


def test_smoke_seed_avisa_em_execucao_nao_cientifica(tmp_path: Path):
    spec = engineering_smoke_seed(VarianteModelo.M2_CINCO_RANHURAS)
    report = preflight_offline(spec, build_geometry_plan(spec), project_path=tmp_path / "x.aedt", scientific_run=False)
    assert report.ok
    assert any(item.code == "HYPOTHESIS_GEOMETRY" for item in report.findings)


def test_smoke_seed_e_rejeitado_em_execucao_cientifica(tmp_path: Path):
    spec = engineering_smoke_seed(VarianteModelo.M2_CINCO_RANHURAS)
    report = preflight_offline(spec, build_geometry_plan(spec), project_path=tmp_path / "x.aedt", scientific_run=True)
    assert not report.ok
