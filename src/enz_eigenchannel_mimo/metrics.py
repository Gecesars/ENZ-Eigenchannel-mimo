from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

VELOCIDADE_LUZ_VACUO = 299_792_458.0


def _matriz_complexa(valor: ArrayLike, nome: str) -> NDArray[np.complex128]:
    arr = np.asarray(valor, dtype=np.complex128)
    if arr.ndim != 2:
        raise ValueError(f"{nome} deve ser uma matriz bidimensional")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{nome} contém valores não finitos")
    if 0 in arr.shape:
        raise ValueError(f"{nome} não pode ter dimensão vazia")
    return arr


def _vetor_complexo(valor: ArrayLike, nome: str) -> NDArray[np.complex128]:
    arr = np.asarray(valor, dtype=np.complex128)
    if arr.ndim != 1:
        raise ValueError(f"{nome} deve ser um vetor unidimensional")
    if arr.size == 0:
        raise ValueError(f"{nome} não pode ser vazio")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{nome} contém valores não finitos")
    return arr


def rank_efetivo(matriz: ArrayLike, *, tolerancia: float = 1e-15) -> float:
    """Rank efetivo entrópico a partir dos valores singulares.

    r_eff = exp(-sum p_i ln p_i), com p_i = sigma_i^2 / sum sigma_i^2.
    """
    if tolerancia < 0 or not np.isfinite(tolerancia):
        raise ValueError("tolerancia deve ser finita e não negativa")
    a = _matriz_complexa(matriz, "matriz")
    s = np.linalg.svd(a, compute_uv=False)
    energia = np.square(np.abs(s))
    total = float(np.sum(energia))
    if total <= tolerancia:
        return 0.0
    p = energia / total
    p = p[p > tolerancia]
    return float(np.exp(-np.sum(p * np.log(p))))


def potencia_aceita(matriz_s: ArrayLike, excitacao: ArrayLike) -> float:
    """Potência aceita normalizada a partir de ondas de potência complexas.

    O resultado preserva eventual valor negativo, que indica rede ativa,
    inconsistência de normalização ou erro numérico a ser auditado.
    """
    s = _matriz_complexa(matriz_s, "matriz_s")
    if s.shape[0] != s.shape[1]:
        raise ValueError("matriz_s deve ser quadrada")
    a = _vetor_complexo(excitacao, "excitacao")
    if a.size != s.shape[1]:
        raise ValueError("excitacao incompatível com matriz_s")
    b = s @ a
    return float(np.real(np.vdot(a, a) - np.vdot(b, b)))


def tarc(
    matriz_s: ArrayLike,
    excitacao: ArrayLike,
    *,
    tolerancia: float = 1e-15,
) -> float:
    """Total Active Reflection Coefficient para uma excitação complexa."""
    if tolerancia < 0 or not np.isfinite(tolerancia):
        raise ValueError("tolerancia deve ser finita e não negativa")
    s = _matriz_complexa(matriz_s, "matriz_s")
    if s.shape[0] != s.shape[1]:
        raise ValueError("matriz_s deve ser quadrada")
    a = _vetor_complexo(excitacao, "excitacao")
    if a.size != s.shape[1]:
        raise ValueError("excitacao incompatível com matriz_s")
    incidente = float(np.real(np.vdot(a, a)))
    if incidente <= tolerancia:
        raise ValueError("potência incidente deve ser positiva")
    refletida = float(np.real(np.vdot(s @ a, s @ a)))
    return float(np.sqrt(max(refletida, 0.0) / incidente))


def matriz_gram_radiante(
    campos: ArrayLike,
    pesos: ArrayLike,
) -> NDArray[np.complex128]:
    """Matriz de Gram de padrões embarcados vetoriais complexos.

    ``campos`` deve ter forma ``(portas, amostras, componentes)``. ``pesos``
    contém os pesos reais de quadratura, incluindo ``sin(theta)`` quando uma
    grade uniforme em theta/phi for usada.
    """
    f = np.asarray(campos, dtype=np.complex128)
    if f.ndim != 3 or 0 in f.shape:
        raise ValueError(
            "campos deve ter forma não vazia (portas, amostras, componentes)"
        )
    if not np.all(np.isfinite(f)):
        raise ValueError("campos contém valores não finitos")
    w = np.asarray(pesos, dtype=np.float64)
    if w.ndim != 1 or w.size != f.shape[1]:
        raise ValueError("pesos incompatíveis com o eixo de amostras")
    if not np.all(np.isfinite(w)) or np.any(w < 0):
        raise ValueError("pesos deve conter valores finitos e não negativos")
    if not np.any(w > 0):
        raise ValueError("ao menos um peso deve ser positivo")
    return np.asarray(
        np.einsum("isc,jsc,s->ij", f, f.conj(), w, optimize=True),
        dtype=np.complex128,
    )


def ecc_campo(campos: ArrayLike, pesos: ArrayLike) -> NDArray[np.float64]:
    """Matriz de ECC por campo, preservando fase e polarização complexas."""
    gram = matriz_gram_radiante(campos, pesos)
    potencias = np.real(np.diag(gram))
    if np.any(potencias <= 0):
        raise ValueError("cada porta deve possuir potência radiante positiva")
    denominador = np.outer(potencias, potencias)
    ecc = np.square(np.abs(gram)) / denominador
    return np.asarray(np.clip(np.real(ecc), 0.0, 1.0), dtype=np.float64)


def erro_balanco_potencia(
    incidente: float,
    refletida: float,
    radiada: float,
    perdas: float,
    guiada_saida: float = 0.0,
) -> tuple[float, float]:
    """Retorna resíduo absoluto e relativo do balanço de potência."""
    valores = np.asarray(
        [incidente, refletida, radiada, perdas, guiada_saida], dtype=np.float64
    )
    if not np.all(np.isfinite(valores)) or np.any(valores < 0):
        raise ValueError("potências devem ser finitas e não negativas")
    if incidente <= 0:
        raise ValueError("potência incidente deve ser positiva")
    residuo = float(incidente - np.sum(valores[1:]))
    return residuo, abs(residuo) / incidente


def frequencia_modal_cavidade_retangular_pec(
    indices: tuple[int, int, int],
    dimensoes_m: tuple[float, float, float],
    *,
    velocidade_m_s: float = VELOCIDADE_LUZ_VACUO,
) -> float:
    """Frequência analítica da união dos modos TE/TM de cavidade PEC retangular.

    A família física exige índices inteiros não negativos e pelo menos dois
    índices não nulos. A identificação TE/TM permanece separada desta função.
    """
    if len(indices) != 3 or any(
        isinstance(indice, bool) or not isinstance(indice, (int, np.integer))
        for indice in indices
    ):
        raise ValueError("indices deve conter três inteiros")
    if (
        any(indice < 0 for indice in indices)
        or sum(indice > 0 for indice in indices) < 2
    ):
        raise ValueError("modo PEC retangular exige ao menos dois índices positivos")
    dimensoes = np.asarray(dimensoes_m, dtype=np.float64)
    if (
        dimensoes.shape != (3,)
        or not np.all(np.isfinite(dimensoes))
        or np.any(dimensoes <= 0)
    ):
        raise ValueError("dimensoes_m deve conter três comprimentos positivos")
    if not np.isfinite(velocidade_m_s) or velocidade_m_s <= 0:
        raise ValueError("velocidade_m_s deve ser positiva e finita")
    termos = np.asarray(indices, dtype=np.float64) / dimensoes
    return float(velocidade_m_s * np.linalg.norm(termos) / 2.0)


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
