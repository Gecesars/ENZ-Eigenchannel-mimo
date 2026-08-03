"""Materiais dielétricos rastreáveis para a campanha em 25,87 GHz."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class DielectricMaterialSpec:
    identifier: str
    manufacturer: str | None
    product: str | None
    epsilon_r: float
    loss_tangent: float
    reference_frequency_ghz: float | None
    source: str
    classification: str
    valid_at_operating_frequency: bool = False
    notes: str = ""

    def validate(self) -> None:
        if not self.identifier.strip():
            raise ValueError("material sem identificador")
        if self.epsilon_r <= 1.0:
            raise ValueError("epsilon_r deve ser maior que 1")
        if not 0.0 <= self.loss_tangent < 1.0:
            raise ValueError("loss_tangent inválida")
        if self.reference_frequency_ghz is not None and self.reference_frequency_ghz <= 0:
            raise ValueError("frequência de referência inválida")
        if not self.source.strip():
            raise ValueError("material exige fonte")

    def as_manifest(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


TMM4_10GHZ = DielectricMaterialSpec(
    identifier="Rogers_TMM4_10GHz",
    manufacturer="Rogers Corporation",
    product="TMM 4",
    epsilon_r=4.50,
    loss_tangent=0.0020,
    reference_frequency_ghz=10.0,
    source="Rogers High Frequency Electronics Product Selector Guide",
    classification="PUBLISHED_DATASHEET",
    notes="Não extrapolar silenciosamente para 25,87 GHz; reotimizar e medir.",
)

RO4350B_10GHZ = DielectricMaterialSpec(
    identifier="Rogers_RO4350B_10GHz",
    manufacturer="Rogers Corporation",
    product="RO4350B",
    epsilon_r=3.48,
    loss_tangent=0.0037,
    reference_frequency_ghz=10.0,
    source="Rogers RO4350B data sheet",
    classification="PUBLISHED_DATASHEET",
    notes="Dk de processo; registrar também Dk de projeto quando usado.",
)

RO3003_10GHZ = DielectricMaterialSpec(
    identifier="Rogers_RO3003_10GHz",
    manufacturer="Rogers Corporation",
    product="RO3003",
    epsilon_r=3.00,
    loss_tangent=0.0010,
    reference_frequency_ghz=10.0,
    source="Rogers RO3003 data sheet",
    classification="PUBLISHED_DATASHEET",
    notes="Candidato de baixa perda; exige reotimização da inclusão.",
)

RT_DUROID_5880_10GHZ = DielectricMaterialSpec(
    identifier="Rogers_RT_duroid_5880_10GHz",
    manufacturer="Rogers Corporation",
    product="RT/duroid 5880",
    epsilon_r=2.20,
    loss_tangent=0.0009,
    reference_frequency_ghz=10.0,
    source="Rogers RT/duroid 5880 data sheet",
    classification="PUBLISHED_DATASHEET",
    notes="Referência de perda muito baixa; forte alteração modal esperada.",
)


def fr4_hypothesis(epsilon_r: float, loss_tangent: float) -> DielectricMaterialSpec:
    """Cria um ponto DOE, explicitamente não associado a um produto FR4."""

    return DielectricMaterialSpec(
        identifier=f"FR4_HYPOTHESIS_er{epsilon_r:g}_td{loss_tangent:g}",
        manufacturer=None,
        product=None,
        epsilon_r=float(epsilon_r),
        loss_tangent=float(loss_tangent),
        reference_frequency_ghz=25.87,
        source="DOE numérico; não representa especificação comercial",
        classification="HYPOTHESIS",
        valid_at_operating_frequency=False,
        notes="Somente análise de sensibilidade; proibido como claim de material.",
    )


def fr4_doe() -> tuple[DielectricMaterialSpec, ...]:
    return tuple(
        fr4_hypothesis(epsilon_r, loss_tangent)
        for epsilon_r in (3.6, 3.9, 4.2, 4.5, 4.8)
        for loss_tangent in (0.002, 0.005, 0.010, 0.020, 0.030)
    )


def candidate_materials() -> tuple[DielectricMaterialSpec, ...]:
    return (TMM4_10GHZ, RO4350B_10GHZ, RO3003_10GHZ, RT_DUROID_5880_10GHZ)


def apply_dielectric_material(app: Any, spec: DielectricMaterialSpec) -> str:
    """Cria/atualiza material isotrópico no AEDT com propriedades explícitas."""

    spec.validate()
    materials = app.materials
    material = None
    try:
        material = materials[spec.identifier]
    except Exception:
        material = materials.add_material(spec.identifier)
    material.permittivity = spec.epsilon_r
    material.dielectric_loss_tangent = spec.loss_tangent
    try:
        material.update()
    except Exception:
        pass
    return spec.identifier


def material_manifest(materials: Iterable[DielectricMaterialSpec]) -> list[dict[str, Any]]:
    return [material.as_manifest() for material in materials]
