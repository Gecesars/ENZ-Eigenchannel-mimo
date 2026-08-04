from __future__ import annotations

import math
from itertools import pairwise

import numpy as np
import pytest

from enz_eigenchannel_mimo.mimo2x2 import (
    Mimo2x2C0Spec,
    ecc_campos_complexos,
    ler_ffd_complexo,
    ler_touchstone_s2p,
)


def test_q4_c0_wr28_e_monomodo() -> None:
    spec = Mimo2x2C0Spec()
    assert spec.fc10_ghz == pytest.approx(21.0824513361)
    assert spec.fc20_ghz == pytest.approx(42.1649026723)
    assert spec.fc01_ghz == pytest.approx(42.1056823034)
    assert spec.fc10_ghz < spec.frequency_ghz
    assert spec.frequency_ghz < min(spec.fc20_ghz, spec.fc01_ghz)
    assert spec.lambda_g_mm == pytest.approx(19.9956242278)
    assert spec.junction_length_mm == pytest.approx(spec.lambda_g_mm / 4)


def test_q4_c0_centros_sem_colisao() -> None:
    spec = Mimo2x2C0Spec()
    centers = spec.radiator_centers_x_mm
    assert centers == {
        "RAD_A1": -69.0,
        "RAD_A2": -27.0,
        "RAD_B1": 27.0,
        "RAD_B2": 69.0,
    }
    ordered = sorted(centers.values())
    separations = [b - a for a, b in pairwise(ordered)]
    assert min(separations) > spec.source_housing_span_x_mm
    assert spec.region_bounds_mm[0] < ordered[0]
    assert spec.region_bounds_mm[3] > ordered[-1]


def test_q4_c0_classifica_dimensoes_nao_publicadas() -> None:
    classifications = Mimo2x2C0Spec().classifications()
    assert classifications["pair_spacing_mm"] == "HIPÓTESE"
    assert classifications["interpair_spacing_mm"] == "HIPÓTESE"
    assert classifications["branch_length_mm"] == "DERIVADO"
    assert all(
        value in {"PUBLICADO", "DERIVADO", "HIPÓTESE"}
        for value in classifications.values()
    )


def test_q4_c0_rejeita_colisoes() -> None:
    with pytest.raises(ValueError, match="pair_spacing"):
        Mimo2x2C0Spec(pair_spacing_mm=36.0)
    with pytest.raises(ValueError, match="interpair_spacing"):
        Mimo2x2C0Spec(interpair_spacing_mm=78.0)


def test_q4_c0_porta_externa_e_finita() -> None:
    spec = Mimo2x2C0Spec()
    assert math.isfinite(spec.external_port_y_mm)
    assert spec.external_port_y_mm < spec.source_port_y_mm


def test_ler_touchstone_s2p_preserva_ordem_complexa(tmp_path) -> None:
    path = tmp_path / "system.s2p"
    path.write_text(
        "# GHz S RI R 50\n"
        "25 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8\n",
        encoding="utf-8",
    )
    frequencies, matrices = ler_touchstone_s2p(path)
    assert frequencies.tolist() == [25e9]
    assert matrices[0, 0, 0] == 0.1 + 0.2j
    assert matrices[0, 1, 0] == 0.3 + 0.4j
    assert matrices[0, 0, 1] == 0.5 + 0.6j
    assert matrices[0, 1, 1] == 0.7 + 0.8j


def test_ler_ffd_complexo_e_ecc(tmp_path) -> None:
    path = tmp_path / "element.ffd"
    path.write_text(
        "0 180 3\n"
        "0 360 3\n"
        "Frequencies 1\n"
        "Frequency 2.587e10\n"
        + "\n".join(f"{value} 0 0 0" for value in range(1, 10))
        + "\n",
        encoding="utf-8",
    )
    theta, phi, field = ler_ffd_complexo(path)
    assert theta.tolist() == [0.0, 90.0, 180.0]
    assert phi.tolist() == [0.0, 180.0, 360.0]
    assert field.shape == (3, 3, 2)
    assert field[0, 1, 0] == 2.0 + 0.0j
    assert field[1, 0, 0] == 4.0 + 0.0j
    assert ecc_campos_complexos(theta, phi, field, field) == pytest.approx(1.0)

    orthogonal = np.empty_like(field)
    orthogonal[..., 0] = 0.0
    orthogonal[..., 1] = 1.0
    assert ecc_campos_complexos(theta, phi, field, orthogonal) == pytest.approx(0.0)
