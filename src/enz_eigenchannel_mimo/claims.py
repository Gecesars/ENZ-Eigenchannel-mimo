from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class ClasseEvidencia(StrEnum):
    PUBLICADO = "PUBLICADO"
    DERIVADO = "DERIVADO"
    SIMULADO = "SIMULADO"
    MEDIDO = "MEDIDO"
    INFERIDO = "INFERIDO"
    HIPOTESE = "HIPÓTESE"
    DESCONHECIDO = "DESCONHECIDO"


CLASSES_EVIDENCIA = tuple(item.value for item in ClasseEvidencia)


@dataclass(frozen=True, slots=True)
class RegistroEvidencia:
    identificador: str
    classe: ClasseEvidencia
    descricao: str
    fonte: str | None = None
    observacao: str | None = None
    runs: tuple[str, ...] = ()
    medicoes: tuple[str, ...] = ()
    limitacoes: tuple[str, ...] = ()
    revisor: str | None = None
    data_revisao: date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "runs", tuple(self.runs))
        object.__setattr__(self, "medicoes", tuple(self.medicoes))
        object.__setattr__(self, "limitacoes", tuple(self.limitacoes))
        self.validar()

    def validar(self) -> None:
        if not isinstance(self.classe, ClasseEvidencia):
            raise TypeError("classe fora da ontologia científica")
        if not self.identificador.strip():
            raise ValueError("identificador vazio")
        if not self.descricao.strip():
            raise ValueError("descrição vazia")
        if self.fonte is not None and not self.fonte.strip():
            raise ValueError("fonte vazia")
        if self.classe is ClasseEvidencia.PUBLICADO and not self.fonte:
            raise ValueError("afirmação PUBLICADA exige fonte")
        if self.classe is ClasseEvidencia.DERIVADO and not (
            self.fonte or self.observacao
        ):
            raise ValueError("afirmação DERIVADA exige fonte ou derivação declarada")
        if self.classe is ClasseEvidencia.SIMULADO and not self.runs:
            raise ValueError("afirmação SIMULADA exige ao menos um run")
        if self.classe is ClasseEvidencia.MEDIDO and not self.medicoes:
            raise ValueError("afirmação MEDIDA exige ao menos uma medição")
        for campo, valores in (
            ("runs", self.runs),
            ("medicoes", self.medicoes),
            ("limitacoes", self.limitacoes),
        ):
            if any(not valor.strip() for valor in valores):
                raise ValueError(f"{campo} contém item vazio")
