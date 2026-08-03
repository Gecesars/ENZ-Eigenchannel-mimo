"""Especificação auditável da família geométrica G0/M0-M4."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import math
from pathlib import Path
from typing import Any, Mapping


class OrigemDado(StrEnum):
    PUBLICADO_TEXTO = "PUBLISHED_TEXT"
    PUBLICADO_FIGURA = "PUBLISHED_FIGURE"
    DERIVADO = "DERIVED"
    INFERIDO = "INFERRED"
    OTIMIZADO = "OPTIMIZED"
    HIPOTESE = "HYPOTHESIS"
    DESCONHECIDO = "UNKNOWN"


class VarianteModelo(StrEnum):
    M0_CAVIDADE_FECHADA = "M0"
    M1_TRES_RANHURAS = "M1"
    M2_CINCO_RANHURAS = "M2"
    M3_DEGRAU = "M3"
    M4_FABRICAVEL = "M4"


@dataclass(frozen=True, slots=True)
class Grandeza:
    valor: float | None
    unidade: str = "mm"
    origem: OrigemDado = OrigemDado.DESCONHECIDO
    fonte: str | None = None
    incerteza: float | None = None

    def require(self, nome: str, *, positivo: bool = True) -> float:
        if self.valor is None:
            raise ValueError(f"dimensão obrigatória ausente: {nome}")
        valor = float(self.valor)
        if not math.isfinite(valor):
            raise ValueError(f"dimensão não finita: {nome}")
        if positivo and valor <= 0:
            raise ValueError(f"dimensão deve ser positiva: {nome}")
        return valor


@dataclass(frozen=True, slots=True)
class CavidadeSpec:
    largura: Grandeza
    altura: Grandeza
    comprimento: Grandeza
    espessura_parede: Grandeza
    area_alvo_mm2: float = 108.0

    def validate(self) -> None:
        largura = self.largura.require("cavidade.largura")
        altura = self.altura.require("cavidade.altura")
        self.comprimento.require("cavidade.comprimento")
        espessura = self.espessura_parede.require("cavidade.espessura_parede")
        if espessura >= min(largura, altura) / 2:
            raise ValueError("espessura da parede inviabiliza a cavidade interna")
        erro = abs(largura * altura - self.area_alvo_mm2) / self.area_alvo_mm2
        if erro > 5e-3:
            raise ValueError(
                f"área transversal {largura * altura:.6g} mm² difere do alvo "
                f"{self.area_alvo_mm2:.6g} mm² em {100 * erro:.3f}%"
            )


@dataclass(frozen=True, slots=True)
class GuiaSpec:
    a: Grandeza
    b: Grandeza
    comprimento: Grandeza
    espessura_parede: Grandeza
    nome_porta: str = "P1_WR28"

    def validate(self) -> None:
        self.a.require("guia.a")
        self.b.require("guia.b")
        self.comprimento.require("guia.comprimento")
        self.espessura_parede.require("guia.espessura_parede")
        if not self.nome_porta.strip():
            raise ValueError("nome da porta vazio")


@dataclass(frozen=True, slots=True)
class RanhuraSpec:
    nome: str
    centro_x: Grandeza
    centro_y: Grandeza
    comprimento: Grandeza
    largura: Grandeza
    angulo_deg: float = 0.0

    def validate(self) -> None:
        if not self.nome.strip():
            raise ValueError("ranhura sem nome")
        self.centro_x.require(f"{self.nome}.centro_x", positivo=False)
        self.centro_y.require(f"{self.nome}.centro_y", positivo=False)
        self.comprimento.require(f"{self.nome}.comprimento")
        self.largura.require(f"{self.nome}.largura")
        if not math.isfinite(self.angulo_deg):
            raise ValueError(f"ângulo inválido em {self.nome}")


@dataclass(frozen=True, slots=True)
class DegrauSpec:
    nome: str
    origem_x: Grandeza
    origem_y: Grandeza
    comprimento_x: Grandeza
    largura_y: Grandeza
    altura_z: Grandeza
    operacao: str = "add_metal"

    def validate(self) -> None:
        if self.operacao not in {"add_metal", "remove_metal"}:
            raise ValueError("degrau.operacao deve ser add_metal ou remove_metal")
        self.origem_x.require("degrau.origem_x", positivo=False)
        self.origem_y.require("degrau.origem_y", positivo=False)
        self.comprimento_x.require("degrau.comprimento_x")
        self.largura_y.require("degrau.largura_y")
        self.altura_z.require("degrau.altura_z")


@dataclass(frozen=True, slots=True)
class DieletricoSpec:
    nome: str
    material: str
    origem_xyz: tuple[Grandeza, Grandeza, Grandeza]
    tamanho_xyz: tuple[Grandeza, Grandeza, Grandeza]

    def validate(self) -> None:
        if not self.nome.strip() or not self.material.strip():
            raise ValueError("inclusão dielétrica sem nome/material")
        for eixo, grandeza in zip("xyz", self.origem_xyz, strict=True):
            grandeza.require(f"dieletrico.origem_{eixo}", positivo=False)
        for eixo, grandeza in zip("xyz", self.tamanho_xyz, strict=True):
            grandeza.require(f"dieletrico.tamanho_{eixo}")


@dataclass(frozen=True, slots=True)
class PinoSpec:
    nome: str
    centro_x: Grandeza
    centro_y: Grandeza
    diametro: Grandeza
    altura: Grandeza

    def validate(self) -> None:
        if not self.nome.strip():
            raise ValueError("pino sem nome")
        self.centro_x.require(f"{self.nome}.centro_x", positivo=False)
        self.centro_y.require(f"{self.nome}.centro_y", positivo=False)
        self.diametro.require(f"{self.nome}.diametro")
        self.altura.require(f"{self.nome}.altura")


@dataclass(frozen=True, slots=True)
class ChanfroSpec:
    objeto: str
    edge_indices: tuple[int, ...]
    distancia: Grandeza

    def validate(self) -> None:
        if not self.objeto.strip() or not self.edge_indices:
            raise ValueError("chanfro exige objeto e índices de aresta explícitos")
        if any(index < 0 for index in self.edge_indices):
            raise ValueError("índice de aresta do chanfro deve ser não negativo")
        self.distancia.require("chanfro.distancia")


@dataclass(frozen=True, slots=True)
class G0GeometrySpec:
    identificador: str
    variante: VarianteModelo
    cavidade: CavidadeSpec
    guia: GuiaSpec | None = None
    ranhuras: tuple[RanhuraSpec, ...] = ()
    degrau: DegrauSpec | None = None
    dieletrico: DieletricoSpec | None = None
    pinos: tuple[PinoSpec, ...] = ()
    chanfros: tuple[ChanfroSpec, ...] = ()
    material_metal: str = "aluminum"
    frequencia_central_ghz: float = 25.87
    allow_hypothesis_geometry: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.identificador.strip():
            raise ValueError("identificador geométrico vazio")
        if self.frequencia_central_ghz <= 0:
            raise ValueError("frequência central inválida")
        self.cavidade.validate()

        if self.variante is not VarianteModelo.M0_CAVIDADE_FECHADA:
            if self.guia is None:
                raise ValueError(f"{self.variante.value} exige guia de alimentação")
            self.guia.validate()

        expected_slots = {
            VarianteModelo.M0_CAVIDADE_FECHADA: 0,
            VarianteModelo.M1_TRES_RANHURAS: 3,
            VarianteModelo.M2_CINCO_RANHURAS: 5,
            VarianteModelo.M3_DEGRAU: 5,
            VarianteModelo.M4_FABRICAVEL: 5,
        }[self.variante]
        if len(self.ranhuras) != expected_slots:
            raise ValueError(
                f"{self.variante.value} exige {expected_slots} ranhuras; "
                f"recebidas {len(self.ranhuras)}"
            )
        for slot in self.ranhuras:
            slot.validate()

        if self.variante in {VarianteModelo.M3_DEGRAU, VarianteModelo.M4_FABRICAVEL}:
            if self.degrau is None:
                raise ValueError(f"{self.variante.value} exige perfil em degrau")
            self.degrau.validate()

        if self.variante is VarianteModelo.M4_FABRICAVEL:
            if self.dieletrico is None:
                raise ValueError("M4 exige inclusão dielétrica")
            self.dieletrico.validate()
            if not self.pinos:
                raise ValueError("M4 exige pinos metálicos")
            for pin in self.pinos:
                pin.validate()
            for chamfer in self.chanfros:
                chamfer.validate()

        if not self.allow_hypothesis_geometry:
            for path, grandeza in self.iter_grandezas():
                if grandeza.origem in {OrigemDado.HIPOTESE, OrigemDado.INFERIDO}:
                    raise ValueError(
                        f"geometria {path} é {grandeza.origem.value}; "
                        "use allow_hypothesis_geometry somente para smoke tests"
                    )

    def iter_grandezas(self) -> list[tuple[str, Grandeza]]:
        items: list[tuple[str, Grandeza]] = [
            ("cavidade.largura", self.cavidade.largura),
            ("cavidade.altura", self.cavidade.altura),
            ("cavidade.comprimento", self.cavidade.comprimento),
            ("cavidade.espessura_parede", self.cavidade.espessura_parede),
        ]
        if self.guia:
            items.extend(
                [
                    ("guia.a", self.guia.a),
                    ("guia.b", self.guia.b),
                    ("guia.comprimento", self.guia.comprimento),
                    ("guia.espessura_parede", self.guia.espessura_parede),
                ]
            )
        for slot in self.ranhuras:
            items.extend(
                [
                    (f"ranhuras.{slot.nome}.centro_x", slot.centro_x),
                    (f"ranhuras.{slot.nome}.centro_y", slot.centro_y),
                    (f"ranhuras.{slot.nome}.comprimento", slot.comprimento),
                    (f"ranhuras.{slot.nome}.largura", slot.largura),
                ]
            )
        if self.degrau:
            items.extend(
                [
                    ("degrau.origem_x", self.degrau.origem_x),
                    ("degrau.origem_y", self.degrau.origem_y),
                    ("degrau.comprimento_x", self.degrau.comprimento_x),
                    ("degrau.largura_y", self.degrau.largura_y),
                    ("degrau.altura_z", self.degrau.altura_z),
                ]
            )
        if self.dieletrico:
            for eixo, value in zip("xyz", self.dieletrico.origem_xyz, strict=True):
                items.append((f"dieletrico.origem_{eixo}", value))
            for eixo, value in zip("xyz", self.dieletrico.tamanho_xyz, strict=True):
                items.append((f"dieletrico.tamanho_{eixo}", value))
        for pin in self.pinos:
            items.extend(
                [
                    (f"pinos.{pin.nome}.centro_x", pin.centro_x),
                    (f"pinos.{pin.nome}.centro_y", pin.centro_y),
                    (f"pinos.{pin.nome}.diametro", pin.diametro),
                    (f"pinos.{pin.nome}.altura", pin.altura),
                ]
            )
        for index, chamfer in enumerate(self.chanfros):
            items.append((f"chanfros.{index}.distancia", chamfer.distancia))
        return items

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)


def g(valor: float | None, origem: OrigemDado, fonte: str | None = None) -> Grandeza:
    return Grandeza(valor=valor, origem=origem, fonte=fonte)


def published_skeleton(variant: VarianteModelo = VarianteModelo.M0_CAVIDADE_FECHADA) -> G0GeometrySpec:
    """Esqueleto que preserva desconhecidos; não é executável até ser completado."""

    paper = "Vilas Boas et al., IEEE OJAP, 2026, DOI 10.1109/OJAP.2026.3703713"
    return G0GeometrySpec(
        identificador=f"G0_{variant.value}_published_skeleton",
        variante=variant,
        cavidade=CavidadeSpec(
            largura=g(14.0, OrigemDado.PUBLICADO_TEXTO, paper),
            altura=g(7.7143, OrigemDado.PUBLICADO_TEXTO, paper),
            comprimento=g(None, OrigemDado.DESCONHECIDO, paper),
            espessura_parede=g(None, OrigemDado.DESCONHECIDO, paper),
        ),
        guia=GuiaSpec(
            a=g(7.11, OrigemDado.PUBLICADO_TEXTO, paper),
            b=g(3.56, OrigemDado.PUBLICADO_TEXTO, paper),
            comprimento=g(None, OrigemDado.DESCONHECIDO, paper),
            espessura_parede=g(None, OrigemDado.DESCONHECIDO, paper),
        )
        if variant is not VarianteModelo.M0_CAVIDADE_FECHADA
        else None,
        metadata={"status": "documental_nao_executavel"},
    )


def engineering_smoke_seed(variant: VarianteModelo) -> G0GeometrySpec:
    """Seed explícito para validar código/CAD, nunca para gerar claims científicos."""

    c0 = 299_792_458.0
    wavelength_mm = c0 / (25.87e9) * 1e3
    length = 3.10 * wavelength_mm  # dimensão global publicada, interpretação provisória
    wall = 1.0
    slot_length = 0.50 * wavelength_mm
    slot_width = 0.08 * wavelength_mm
    positions = [length * fraction for fraction in (0.18, 0.34, 0.50, 0.66, 0.82)]
    slots = tuple(
        RanhuraSpec(
            nome=f"Slot_{index + 1}",
            centro_x=g(x, OrigemDado.DERIVADO, "seed de smoke test"),
            centro_y=g(0.0, OrigemDado.HIPOTESE, "seed de smoke test"),
            comprimento=g(slot_length, OrigemDado.HIPOTESE, "seed de smoke test"),
            largura=g(slot_width, OrigemDado.HIPOTESE, "seed de smoke test"),
            angulo_deg=90.0,
        )
        for index, x in enumerate(positions[: 3 if variant is VarianteModelo.M1_TRES_RANHURAS else 5])
    )
    if variant is VarianteModelo.M0_CAVIDADE_FECHADA:
        slots = ()

    cavity = CavidadeSpec(
        largura=g(14.0, OrigemDado.PUBLICADO_TEXTO),
        altura=g(7.7143, OrigemDado.PUBLICADO_TEXTO),
        comprimento=g(length, OrigemDado.DERIVADO, "3,10 lambda0"),
        espessura_parede=g(wall, OrigemDado.HIPOTESE, "somente smoke test"),
    )
    guide = None
    if variant is not VarianteModelo.M0_CAVIDADE_FECHADA:
        guide = GuiaSpec(
            a=g(7.11, OrigemDado.PUBLICADO_TEXTO),
            b=g(3.56, OrigemDado.PUBLICADO_TEXTO),
            comprimento=g(1.25 * wavelength_mm, OrigemDado.HIPOTESE),
            espessura_parede=g(wall, OrigemDado.HIPOTESE),
        )

    step = None
    if variant in {VarianteModelo.M3_DEGRAU, VarianteModelo.M4_FABRICAVEL}:
        step = DegrauSpec(
            nome="Step_Profile",
            origem_x=g(length * 0.35, OrigemDado.HIPOTESE),
            origem_y=g(-4.5, OrigemDado.HIPOTESE),
            comprimento_x=g(length * 0.30, OrigemDado.HIPOTESE),
            largura_y=g(9.0, OrigemDado.PUBLICADO_TEXTO),
            altura_z=g(1.0, OrigemDado.PUBLICADO_TEXTO),
            operacao="add_metal",
        )

    dielectric = None
    pins: tuple[PinoSpec, ...] = ()
    chamfers: tuple[ChanfroSpec, ...] = ()
    if variant is VarianteModelo.M4_FABRICAVEL:
        dielectric = DieletricoSpec(
            nome="Photonic_Dopant",
            material="FR4_HYPOTHESIS",
            origem_xyz=(
                g(length * 0.40, OrigemDado.HIPOTESE),
                g(-2.0, OrigemDado.HIPOTESE),
                g(0.0, OrigemDado.HIPOTESE),
            ),
            tamanho_xyz=(
                g(length * 0.20, OrigemDado.HIPOTESE),
                g(4.0, OrigemDado.HIPOTESE),
                g(1.6, OrigemDado.HIPOTESE),
            ),
        )
        pin_x = (length * 0.36, length * 0.64)
        pin_y = (-3.0, 3.0)
        pins = tuple(
            PinoSpec(
                nome=f"Mode_Suppression_Pin_{i + 1}",
                centro_x=g(x, OrigemDado.HIPOTESE),
                centro_y=g(y, OrigemDado.HIPOTESE),
                diametro=g(1.0, OrigemDado.HIPOTESE),
                altura=g(7.7143, OrigemDado.DERIVADO),
            )
            for i, (x, y) in enumerate((
                (pin_x[0], pin_y[0]),
                (pin_x[0], pin_y[1]),
                (pin_x[1], pin_y[0]),
                (pin_x[1], pin_y[1]),
            ))
        )
        chamfers = (
            ChanfroSpec(
                objeto="Cavity_Metal",
                edge_indices=(0, 1),
                distancia=g(3.0, OrigemDado.PUBLICADO_TEXTO),
            ),
        )

    return G0GeometrySpec(
        identificador=f"G0_{variant.value}_engineering_smoke_seed",
        variante=variant,
        cavidade=cavity,
        guia=guide,
        ranhuras=slots,
        degrau=step,
        dieletrico=dielectric,
        pinos=pins,
        chanfros=chamfers,
        allow_hypothesis_geometry=True,
        metadata={
            "status": "smoke_test_only",
            "proibido_para_claims": True,
            "coordinate_system": "X longitudinal, Y transversal, Z vertical",
        },
    )


def load_yaml_spec(path: str | Path) -> Mapping[str, Any]:
    """Carrega YAML sem tornar PyYAML dependência do núcleo matemático."""

    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - dependência opcional
        raise RuntimeError("PyYAML é necessário para carregar especificações YAML") from exc
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError("especificação YAML deve ser um mapeamento")
    return data
