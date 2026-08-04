from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

VELOCIDADE_LUZ_M_S = 299_792_458.0


@dataclass(frozen=True, slots=True)
class Mimo2x2C0Spec:
    """Baseline exploratório Q4-C0 derivado da reconstrução v7 aberta.

    O eixo largo do WR-28 está em Z no modelo fonte. Os espaçamentos não são
    publicados no artigo e permanecem classificados como HIPÓTESE.
    """

    frequency_ghz: float = 25.87
    sweep_start_ghz: float = 25.0
    sweep_stop_ghz: float = 27.0
    wg_a_z_mm: float = 7.11
    wg_b_x_mm: float = 3.56
    source_port_y_mm: float = -18.0
    source_housing_span_x_mm: float = 36.0
    source_housing_z_min_mm: float = 0.0
    source_housing_z_max_mm: float = 11.11
    source_air_z_min_mm: float = 3.0
    pair_spacing_mm: float = 42.0
    interpair_spacing_mm: float = 96.0
    wall_mm: float = 1.0
    region_x_padding_mm: float = 18.0
    region_y_max_mm: float = 32.4
    region_z_min_mm: float = -13.792
    region_z_max_mm: float = 25.002

    def __post_init__(self) -> None:
        positive = {
            "frequency_ghz": self.frequency_ghz,
            "wg_a_z_mm": self.wg_a_z_mm,
            "wg_b_x_mm": self.wg_b_x_mm,
            "pair_spacing_mm": self.pair_spacing_mm,
            "interpair_spacing_mm": self.interpair_spacing_mm,
            "wall_mm": self.wall_mm,
        }
        if any(not math.isfinite(value) or value <= 0 for value in positive.values()):
            raise ValueError(f"parâmetros positivos inválidos: {positive}")
        if not self.sweep_start_ghz < self.frequency_ghz < self.sweep_stop_ghz:
            raise ValueError("a frequência adaptativa deve pertencer à varredura")
        if self.pair_spacing_mm <= self.source_housing_span_x_mm:
            raise ValueError("pair_spacing_mm causaria colisão entre radiadores")
        minimum_interpair = (
            self.pair_spacing_mm + self.source_housing_span_x_mm
        )
        if self.interpair_spacing_mm <= minimum_interpair:
            raise ValueError("interpair_spacing_mm causaria colisão entre pares")
        if not self.fc10_ghz < self.frequency_ghz:
            raise ValueError("TE10 não propaga na frequência de projeto")
        if not self.frequency_ghz < min(self.fc20_ghz, self.fc01_ghz):
            raise ValueError("a seção de referência não é monomodo em f0")

    @property
    def fc10_ghz(self) -> float:
        return VELOCIDADE_LUZ_M_S / (2 * self.wg_a_z_mm * 1e-3) / 1e9

    @property
    def fc20_ghz(self) -> float:
        return VELOCIDADE_LUZ_M_S / (self.wg_a_z_mm * 1e-3) / 1e9

    @property
    def fc01_ghz(self) -> float:
        return VELOCIDADE_LUZ_M_S / (2 * self.wg_b_x_mm * 1e-3) / 1e9

    @property
    def lambda0_mm(self) -> float:
        return VELOCIDADE_LUZ_M_S / (self.frequency_ghz * 1e9) * 1e3

    @property
    def lambda_g_mm(self) -> float:
        ratio = self.fc10_ghz / self.frequency_ghz
        return self.lambda0_mm / math.sqrt(1.0 - ratio * ratio)

    @property
    def branch_length_mm(self) -> float:
        return self.lambda_g_mm

    @property
    def junction_length_mm(self) -> float:
        return self.lambda_g_mm / 4.0

    @property
    def input_length_mm(self) -> float:
        return self.lambda_g_mm

    @property
    def pair_centers_x_mm(self) -> dict[str, float]:
        half = self.interpair_spacing_mm / 2.0
        return {"A": -half, "B": half}

    @property
    def radiator_centers_x_mm(self) -> dict[str, float]:
        pair_half = self.pair_spacing_mm / 2.0
        pairs = self.pair_centers_x_mm
        return {
            "RAD_A1": pairs["A"] - pair_half,
            "RAD_A2": pairs["A"] + pair_half,
            "RAD_B1": pairs["B"] - pair_half,
            "RAD_B2": pairs["B"] + pair_half,
        }

    @property
    def junction_y_min_mm(self) -> float:
        return self.source_port_y_mm - self.branch_length_mm - self.junction_length_mm

    @property
    def branch_y_min_mm(self) -> float:
        return self.source_port_y_mm - self.branch_length_mm

    @property
    def external_port_y_mm(self) -> float:
        return self.junction_y_min_mm - self.input_length_mm

    @property
    def manifold_air_width_mm(self) -> float:
        return self.pair_spacing_mm + self.wg_b_x_mm

    @property
    def feed_housing_width_mm(self) -> float:
        return self.manifold_air_width_mm + 2.0 * self.wall_mm

    @property
    def region_bounds_mm(self) -> list[float]:
        centers = self.radiator_centers_x_mm.values()
        half_housing = self.source_housing_span_x_mm / 2.0
        x_min = min(centers) - half_housing - self.region_x_padding_mm
        x_max = max(centers) + half_housing + self.region_x_padding_mm
        return [
            x_min,
            self.external_port_y_mm,
            self.region_z_min_mm,
            x_max,
            self.region_y_max_mm,
            self.region_z_max_mm,
        ]

    def classifications(self) -> dict[str, str]:
        return {
            "frequency_ghz": "PUBLICADO",
            "sweep_start_ghz": "PUBLICADO",
            "sweep_stop_ghz": "PUBLICADO",
            "wg_a_z_mm": "PUBLICADO",
            "wg_b_x_mm": "PUBLICADO",
            "source_port_y_mm": "DERIVADO",
            "source_housing_span_x_mm": "PUBLICADO",
            "source_housing_z_min_mm": "DERIVADO",
            "source_housing_z_max_mm": "PUBLICADO",
            "source_air_z_min_mm": "DERIVADO",
            "pair_spacing_mm": "HIPÓTESE",
            "interpair_spacing_mm": "HIPÓTESE",
            "wall_mm": "HIPÓTESE",
            "branch_length_mm": "DERIVADO",
            "junction_length_mm": "DERIVADO",
            "input_length_mm": "DERIVADO",
            "manifold_air_width_mm": "DERIVADO",
            "feed_housing_width_mm": "DERIVADO",
            "region_bounds_mm": "DERIVADO",
        }

    def to_manifest(self) -> dict[str, object]:
        return {
            "schema": "enz-eigenchannel-mimo/q4-c0-spec/v1",
            "classification": "HIPÓTESE",
            "parameters": asdict(self),
            "derived": {
                "fc10_ghz": self.fc10_ghz,
                "fc20_ghz": self.fc20_ghz,
                "fc01_ghz": self.fc01_ghz,
                "lambda0_mm": self.lambda0_mm,
                "lambda_g_mm": self.lambda_g_mm,
                "branch_length_mm": self.branch_length_mm,
                "junction_length_mm": self.junction_length_mm,
                "input_length_mm": self.input_length_mm,
                "pair_centers_x_mm": self.pair_centers_x_mm,
                "radiator_centers_x_mm": self.radiator_centers_x_mm,
                "external_port_y_mm": self.external_port_y_mm,
                "manifold_air_width_mm": self.manifold_air_width_mm,
                "feed_housing_width_mm": self.feed_housing_width_mm,
                "region_bounds_mm": self.region_bounds_mm,
            },
            "classifications": self.classifications(),
        }


def ler_touchstone_s2p(
    caminho: str | Path,
) -> tuple[NDArray[np.float64], NDArray[np.complex128]]:
    """Lê Touchstone 1.0 S2P preservando números complexos e ordem de portas."""

    path = Path(caminho)
    option = ["ghz", "s", "ma", "r", "50"]
    numeric_tokens: list[float] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            option = line[1:].lower().split()
            continue
        if line.startswith("["):
            raise ValueError("Touchstone 2.0 não é suportado por este leitor S2P")
        numeric_tokens.extend(float(token) for token in line.split())
    if len(numeric_tokens) % 9:
        raise ValueError("S2P deve conter nove valores numéricos por frequência")

    unit = option[0]
    parameter = option[1]
    representation = option[2]
    if parameter != "s":
        raise ValueError("o arquivo deve conter parâmetros S")
    scale = {"hz": 1.0, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}.get(unit)
    if scale is None:
        raise ValueError(f"unidade Touchstone desconhecida: {unit}")

    def complex_value(first: float, second: float) -> complex:
        if representation == "ri":
            return complex(first, second)
        if representation == "ma":
            return first * np.exp(1j * np.deg2rad(second))
        if representation == "db":
            return 10.0 ** (first / 20.0) * np.exp(1j * np.deg2rad(second))
        raise ValueError(f"representação Touchstone desconhecida: {representation}")

    rows = len(numeric_tokens) // 9
    frequencies = np.empty(rows, dtype=np.float64)
    matrices = np.empty((rows, 2, 2), dtype=np.complex128)
    for row in range(rows):
        record = numeric_tokens[row * 9 : (row + 1) * 9]
        frequencies[row] = record[0] * scale
        s11 = complex_value(record[1], record[2])
        s21 = complex_value(record[3], record[4])
        s12 = complex_value(record[5], record[6])
        s22 = complex_value(record[7], record[8])
        matrices[row] = [[s11, s12], [s21, s22]]
    return frequencies, matrices


def ler_ffd_complexo(
    caminho: str | Path,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.complex128]]:
    r"""Lê um padrão HFSS FFD preservando fase e componentes vetoriais.

    Retorna os eixos ``theta`` e ``phi`` em graus e um arranjo complexo com
    formato ``(n_theta, n_phi, 2)``. No FFD do HFSS, :math:`\phi` varia mais
    rapidamente que :math:`\theta`. A última dimensão contém
    :math:`(E_\theta, E_\phi)`.
    """

    lines = Path(caminho).read_text(
        encoding="utf-8", errors="strict"
    ).splitlines()
    if len(lines) < 5:
        raise ValueError("FFD incompleto")

    def axis(line: str, name: str) -> NDArray[np.float64]:
        tokens = line.split()
        if len(tokens) != 3:
            raise ValueError(f"eixo {name} inválido no FFD")
        start, stop = (float(tokens[0]), float(tokens[1]))
        count = int(tokens[2])
        if count < 2 or not math.isfinite(start) or not math.isfinite(stop):
            raise ValueError(f"eixo {name} inválido no FFD")
        return np.linspace(start, stop, count, dtype=np.float64)

    theta = axis(lines[0], "theta")
    phi = axis(lines[1], "phi")
    if lines[2].strip().lower() != "frequencies 1":
        raise ValueError("somente FFD com uma frequência é suportado")
    frequency_tokens = lines[3].split()
    if len(frequency_tokens) != 2 or frequency_tokens[0].lower() != "frequency":
        raise ValueError("frequência ausente no FFD")

    numeric = np.loadtxt(lines[4:], dtype=np.float64)
    expected = theta.size * phi.size
    if numeric.shape != (expected, 4):
        raise ValueError(
            f"FFD deveria conter {expected} amostras vetoriais; "
            f"encontrado {numeric.shape}"
        )
    fields = np.empty((theta.size, phi.size, 2), dtype=np.complex128)
    fields[..., 0] = (
        numeric[:, 0] + 1j * numeric[:, 1]
    ).reshape(theta.size, phi.size)
    fields[..., 1] = (
        numeric[:, 2] + 1j * numeric[:, 3]
    ).reshape(theta.size, phi.size)
    return theta, phi, fields


def ecc_campos_complexos(
    theta_deg: NDArray[np.float64],
    phi_deg: NDArray[np.float64],
    campo_1: NDArray[np.complex128],
    campo_2: NDArray[np.complex128],
) -> float:
    r"""Calcula ECC pelo produto interno vetorial dos campos complexos.

    A discretização implementa

    .. math::

       \rho_e = \frac{\left|\int_\Omega \mathbf{E}_1\cdot
       \mathbf{E}_2^*\,d\Omega\right|^2}
       {\int_\Omega |\mathbf{E}_1|^2d\Omega\;
       \int_\Omega |\mathbf{E}_2|^2d\Omega}.

    Se :math:`\phi=360^\circ` duplicar :math:`\phi=0^\circ`, a amostra final
    é removida antes da quadratura.
    """

    theta = np.asarray(theta_deg, dtype=np.float64)
    phi = np.asarray(phi_deg, dtype=np.float64)
    first = np.asarray(campo_1, dtype=np.complex128)
    second = np.asarray(campo_2, dtype=np.complex128)
    expected = (theta.size, phi.size, 2)
    if first.shape != expected or second.shape != expected:
        raise ValueError(f"campos devem ter formato {expected}")
    if np.isclose(phi[-1] - phi[0], 360.0):
        phi = phi[:-1]
        first = first[:, :-1]
        second = second[:, :-1]

    weights = np.sin(np.deg2rad(theta))[:, None, None]
    cross = np.sum(first * np.conjugate(second) * weights)
    power_1 = float(np.sum(np.abs(first) ** 2 * weights))
    power_2 = float(np.sum(np.abs(second) ** 2 * weights))
    if power_1 <= 0.0 or power_2 <= 0.0:
        raise ValueError("campo com potência angular nula")
    return float(abs(cross) ** 2 / (power_1 * power_2))
