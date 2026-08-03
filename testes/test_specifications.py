from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from enz_eigenchannel_mimo.specifications import (
    SCHEMA_CLAIM,
    SCHEMA_GEOMETRIA,
    SCHEMA_MANIFESTO,
    EspecificacaoGeometrica,
    EspecificacaoIncompleta,
    carregar_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "modelos" / "especificacoes"


def test_schemas_sao_validos_no_draft_2020_12():
    for schema_id in (SCHEMA_GEOMETRIA, SCHEMA_CLAIM, SCHEMA_MANIFESTO):
        Draft202012Validator.check_schema(carregar_schema(schema_id))


def test_auditoria_g0_permanece_bloqueada_sem_cotas():
    spec = EspecificacaoGeometrica.carregar(SPECS / "g0_artigo_base.auditado.v3.yaml")
    assert spec.prontidao("M0").pronta is False
    assert "cavidade_comprimento" in spec.prontidao("M0").ausentes
    with pytest.raises(EspecificacaoIncompleta):
        spec.exigir_pronta("M4")


def test_smoke_m0_e_executavel_e_variaveis_tem_unidades():
    spec = EspecificacaoGeometrica.carregar(
        SPECS / "m0_cavidade_retangular_smoke.hipotese.v1.yaml"
    )
    assert spec.prontidao("M0").pronta is True
    assert spec.variaveis_aedt("M0") == {
        "cavidade_comprimento": "20.0mm",
        "cavidade_largura": "14.0mm",
        "cavidade_altura": "7.7143mm",
    }


def test_v6_fixa_waveport_em_z_e_declara_ambiente_de_plots():
    spec = EspecificacaoGeometrica.carregar(
        SPECS / "g0_figura2_reconstrucao_exploratoria.hipotese.v6.yaml"
    )
    etapa = spec.etapa("M4")
    porta = etapa["portas"][0]
    assert porta["linha_integracao"] == [
        ["0mm", "-18mm", "3mm"],
        ["0mm", "-18mm", "10.11mm"],
    ]
    objetos = {objeto["nome"]: objeto for objeto in etapa["objetos"]}
    assert objetos["Port_WR28_Sheet"]["tamanho"] == [
        "altura_interna_wr28",
        "largura_interna_wr28",
    ]
    pos = spec.dados["posprocessamento"]
    assert len(pos["cortes"]) == 8
    assert len(pos["plots_campo"]) == 8
    assert len(pos["relatorios"]) == 8
    assert len(pos["estudos_parametricos"]) == 3


def test_v7_salva_campos_radiados_nas_frequencias_da_figura_4():
    spec = EspecificacaoGeometrica.carregar(
        SPECS / "g0_figura2_reconstrucao_exploratoria.hipotese.v7.yaml"
    )
    etapa = spec.etapa("M4")
    sweep = etapa["varredura_campos_artigo"]
    assert sweep["frequencias"] == [25.65, 25.87, 26.22]
    assert sweep["salvar_campos"] is True
    assert sweep["salvar_campos_radiados"] is True
    relatorios = {
        relatorio["nome"]: relatorio
        for relatorio in spec.dados["posprocessamento"]["relatorios"]
    }
    assert relatorios["Fig4_EPlane_CoCross_MultiFreq"]["solucao"].endswith(
        "Sweep_Fields_Article"
    )
    assert relatorios["Fig4_HPlane_CoCross_MultiFreq"]["solucao"].endswith(
        "Sweep_Fields_Article"
    )
