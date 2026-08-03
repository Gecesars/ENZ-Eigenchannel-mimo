from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _matriz_complexa(valor: ArrayLike, nome: str) -> NDArray[np.complex128]:
    arr = np.asarray(valor, dtype=np.complex128)
    if arr.ndim != 2:
        raise ValueError(f"{nome} deve ser uma matriz bidimensional")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{nome} contém valores não finitos")
    return arr


def rank_efetivo(matriz: ArrayLike, *, tolerancia: float = 1e-15) -> float:
    """Rank efetivo entrópico a partir dos valores singulares.

    r_eff = exp(-sum p_i ln p_i), com p_i = sigma_i^2 / sum sigma_i^2.
    """
    a = _matriz_complexa(matriz, "matriz")
    s = np.linalg.svd(a, compute_uv=False)
    energia = np.square(np.abs(s))
    total = float(np.sum(energia))
    if total <= tolerancia:
        return 0.0
    p = energia / total
    p = p[p > tolerancia]
    return float(np.exp(-np.sum(p * np.log(p))))


def capacidade_mimo(
    canal: ArrayLike,
    snr_linear: float,
    *,
    normalizar_por_transmissor: bool = True,
) -> float:
    """Capacidade espectral de Shannon em bit/s/Hz para CSI no receptor.

    A função não representa throughput de protocolo, BLER, overhead ou MCS.
    """
    h = _matriz_complexa(canal, "canal")
    if snr_linear < 0 or not np.isfinite(snr_linear):
        raise ValueError("snr_linear deve ser finita e não negativa")
    nr, nt = h.shape
    escala = snr_linear / nt if normalizar_por_transmissor and nt else snr_linear
    gram = h @ h.conj().T
    sinal, logdet = np.linalg.slogdet(np.eye(nr, dtype=np.complex128) + escala * gram)
    if np.real(sinal) <= 0:
        raise ArithmeticError("determinante não positivo; verifique a matriz de canal")
    return float(np.real(logdet) / np.log(2.0))
