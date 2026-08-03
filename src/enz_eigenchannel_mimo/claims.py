from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ClasseEvidencia(StrEnum):
    PUBLICADO = "PUBLICADO"
    DERIVADO = "DERIVADO"
    SIMULADO = "SIMULADO"
    MEDIDO = "MEDIDO"
    INFERIDO = "INFERIDO"
    HIPOTESE = "HIPÓTESE"
    DESCONHECIDO = "DESCONHECIDO"


@dataclass(frozen=True, slots=True)
class RegistroEvidencia:
    identificador: str
    classe: ClasseEvidencia
    descricao: str
    fonte: str | None = None
    observacao: str | None = None

    def validar(self) -> None:
        if not self.identificador.strip():
            raise ValueError("identificador vazio")
        if not self.descricao.strip():
            raise ValueError("descrição vazia")
        if self.classe is ClasseEvidencia.PUBLICADO and not self.fonte:
            raise ValueError("afirmação PUBLICADA exige fonte")
