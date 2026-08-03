import pytest

from enz_eigenchannel_mimo.claims import ClasseEvidencia, RegistroEvidencia


def test_publicado_exige_fonte():
    with pytest.raises(ValueError, match="PUBLICADA exige fonte"):
        RegistroEvidencia("C1", ClasseEvidencia.PUBLICADO, "afirmação")


def test_simulado_exige_run_e_medido_exige_medicao():
    with pytest.raises(ValueError, match="SIMULADA exige"):
        RegistroEvidencia("C2", ClasseEvidencia.SIMULADO, "resultado")
    with pytest.raises(ValueError, match="MEDIDA exige"):
        RegistroEvidencia("C3", ClasseEvidencia.MEDIDO, "resultado")


def test_registros_com_proveniencia_sao_validos():
    simulado = RegistroEvidencia(
        "C4", ClasseEvidencia.SIMULADO, "resultado", runs=("ENZ-001",)
    )
    medido = RegistroEvidencia(
        "C5", ClasseEvidencia.MEDIDO, "resultado", medicoes=("VNA-001",)
    )
    assert simulado.runs == ("ENZ-001",)
    assert medido.medicoes == ("VNA-001",)


def test_classe_fora_da_ontologia_e_rejeitada():
    with pytest.raises(TypeError, match="fora da ontologia"):
        RegistroEvidencia("C6", "OTIMIZADO", "resultado")  # type: ignore[arg-type]
