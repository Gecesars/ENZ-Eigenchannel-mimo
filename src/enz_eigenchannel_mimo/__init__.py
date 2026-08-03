"""Núcleo científico do projeto ENZ Eigenchannel MIMO."""

from .claims import ClasseEvidencia, RegistroEvidencia
from .metrics import capacidade_mimo, rank_efetivo

__all__ = ["ClasseEvidencia", "RegistroEvidencia", "capacidade_mimo", "rank_efetivo"]
__version__ = "0.0.1"
