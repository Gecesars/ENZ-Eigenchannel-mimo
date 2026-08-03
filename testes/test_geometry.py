import pytest
from enz_eigenchannel_mimo.geometry import (
    VarianteModelo,
    build_geometry_plan,
    engineering_smoke_seed,
    published_skeleton,
)


@pytest.mark.parametrize("variant", list(VarianteModelo))
def test_smoke_seed_produz_plano_valido(variant):
    spec = engineering_smoke_seed(variant)
    spec.validate()
    plan = build_geometry_plan(spec)
    plan.validate()
    assert plan.variant == variant.value
    assert "Cavity_Metal" in {p.name for p in plan.primitives}


def test_contagem_de_ranhuras_por_fase():
    expected = {"M0": 0, "M1": 3, "M2": 5, "M3": 5, "M4": 5}
    for variant in VarianteModelo:
        plan = build_geometry_plan(engineering_smoke_seed(variant))
        cutters = [p for p in plan.primitives if p.name.endswith("_Cutter")]
        assert len(cutters) == expected[variant.value]


def test_esqueleto_publicado_nao_inventa_dimensoes():
    spec = published_skeleton(VarianteModelo.M0_CAVIDADE_FECHADA)
    with pytest.raises(ValueError, match="dimensão obrigatória ausente"):
        spec.validate()


def test_m0_eigenmode_sem_porta_ou_regiao_aberta():
    plan = build_geometry_plan(engineering_smoke_seed(VarianteModelo.M0_CAVIDADE_FECHADA))
    assert plan.solution_type == "Eigenmode"
    assert plan.ports == ()
    assert plan.open_region_frequency is None


def test_m4_inclui_dopante_pinos_e_chanfro():
    plan = build_geometry_plan(engineering_smoke_seed(VarianteModelo.M4_FABRICAVEL))
    names = {p.name for p in plan.primitives}
    assert "Photonic_Dopant" in names
    assert sum(name.startswith("Mode_Suppression_Pin") for name in names) == 4
    assert any(op.kind == "chamfer" for op in plan.operations)
