import numpy as np
import pytest

from enz_eigenchannel_mimo.metrics import (
    capacidade_mimo,
    ecc_campo,
    erro_balanco_potencia,
    frequencia_modal_cavidade_retangular_pec,
    matriz_gram_radiante,
    potencia_aceita,
    rank_efetivo,
    tarc,
)


def test_rank_efetivo_identidade_quatro():
    assert np.isclose(rank_efetivo(np.eye(4)), 4.0)


def test_rank_efetivo_rank_um():
    h = np.ones((4, 4), dtype=complex)
    assert np.isclose(rank_efetivo(h), 1.0)


def test_capacidade_siso():
    snr = 10.0
    esperado = np.log2(1.0 + snr)
    assert np.isclose(capacidade_mimo([[1.0]], snr), esperado)


def test_capacidade_quatro_canais_ortogonais():
    h = np.eye(4, dtype=complex)
    snr_total = 20.0
    esperado = 4.0 * np.log2(1.0 + snr_total / 4.0)
    assert np.isclose(capacidade_mimo(h, snr_total), esperado)


def test_tarc_e_potencia_aceita_preservam_excitacao_complexa():
    s = np.diag([0.1j, -0.2j])
    a = np.array([1.0, np.exp(1j * np.pi / 3)]) / np.sqrt(2.0)
    assert np.isclose(tarc(s, a), np.sqrt((0.1**2 + 0.2**2) / 2.0))
    assert np.isclose(potencia_aceita(s, a), 1.0 - (0.1**2 + 0.2**2) / 2.0)


def test_ecc_por_campo_complexo_ortogonal_e_coincidente():
    campos = np.array(
        [
            [[1.0, 0.0], [0.0, 1.0j]],
            [[0.0, 1.0], [1.0j, 0.0]],
        ],
        dtype=complex,
    )
    pesos = np.array([0.5, 2.0])
    gram = matriz_gram_radiante(campos, pesos)
    assert np.isclose(gram[0, 1], 0.0)
    assert np.isclose(ecc_campo(campos, pesos)[0, 1], 0.0)

    coincidentes = np.stack([campos[0], np.exp(0.7j) * campos[0]])
    assert np.isclose(ecc_campo(coincidentes, pesos)[0, 1], 1.0)


def test_balanco_potencia_retorna_residuo_com_sinal_e_erro_relativo():
    residuo, erro = erro_balanco_potencia(1.0, 0.1, 0.7, 0.1, 0.05)
    assert np.isclose(residuo, 0.05)
    assert np.isclose(erro, 0.05)


def test_metricas_rejeitam_entradas_vazias_ou_sem_potencia():
    with pytest.raises(ValueError):
        capacidade_mimo(np.empty((0, 2)), 1.0)
    with pytest.raises(ValueError):
        tarc(np.eye(2), np.zeros(2))


def test_frequencias_analiticas_validam_smoke_m0():
    dimensoes = (20e-3, 14e-3, 7.7143e-3)
    modos = [(2, 1, 0), (1, 0, 1), (0, 1, 1), (1, 2, 0)]
    simulado = np.array(
        [18.421495557916, 20.8270538581344, 22.186814834203, 22.6889942661079]
    )
    derivado = (
        np.array(
            [
                frequencia_modal_cavidade_retangular_pec(modo, dimensoes)
                for modo in modos
            ]
        )
        / 1e9
    )
    erro_relativo = np.abs(simulado - derivado) / derivado
    assert np.all(erro_relativo < 7e-5)


def test_frequencia_modal_rejeita_indice_nao_fisico():
    with pytest.raises(ValueError):
        frequencia_modal_cavidade_retangular_pec((1, 0, 0), (1.0, 1.0, 1.0))
