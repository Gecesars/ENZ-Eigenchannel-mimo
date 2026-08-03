"""Núcleo científico do projeto ENZ Eigenchannel MIMO."""

from .claims import CLASSES_EVIDENCIA, ClasseEvidencia, RegistroEvidencia
from .metrics import (
    capacidade_mimo,
    ecc_campo,
    erro_balanco_potencia,
    frequencia_modal_cavidade_retangular_pec,
    matriz_gram_radiante,
    potencia_aceita,
    rank_efetivo,
    tarc,
)

__all__ = [
    "CLASSES_EVIDENCIA",
    "ClasseEvidencia",
    "RegistroEvidencia",
    "capacidade_mimo",
    "ecc_campo",
    "erro_balanco_potencia",
    "frequencia_modal_cavidade_retangular_pec",
    "matriz_gram_radiante",
    "potencia_aceita",
    "rank_efetivo",
    "tarc",
]
__version__ = "0.0.1"
