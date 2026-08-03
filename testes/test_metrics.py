import numpy as np

from enz_eigenchannel_mimo.metrics import capacidade_mimo, rank_efetivo


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
