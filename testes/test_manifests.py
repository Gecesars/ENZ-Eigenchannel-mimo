from pathlib import Path

from enz_eigenchannel_mimo.manifests import ManifestoExecucao
from enz_eigenchannel_mimo.specifications import EspecificacaoGeometrica

ROOT = Path(__file__).resolve().parents[1]
SMOKE = (
    ROOT
    / "modelos"
    / "especificacoes"
    / "m0_cavidade_retangular_smoke.hipotese.v1.yaml"
)


def test_manifesto_atualiza_hash_de_artefato_mutavel(tmp_path):
    spec = EspecificacaoGeometrica.carregar(SMOKE)
    manifesto = ManifestoExecucao.criar(tmp_path, spec, "M0", False, ROOT)
    assert manifesto.dados["schema"].endswith("/v2")
    assert manifesto.dados["solver"]["cores"] == 14
    assert manifesto.dados["solver"]["tasks"] == 1
    assert manifesto.dados["solver"]["gpus"] == 0
    artefato = manifesto.caminho.parent / "projeto.aedt"
    artefato.write_bytes(b"antes")
    manifesto.registrar_artefatos([artefato], manifesto.caminho.parent)
    hash_antes = manifesto.dados["artifacts"][0]["sha256"]
    artefato.write_bytes(b"depois")
    manifesto.registrar_artefatos([artefato], manifesto.caminho.parent)
    assert len(manifesto.dados["artifacts"]) == 1
    assert manifesto.dados["artifacts"][0]["sha256"] != hash_antes
