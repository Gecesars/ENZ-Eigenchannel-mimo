"""Plano CAD declarativo, independente de PyAEDT."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class PrimitivePlan:
    name: str
    kind: str
    parameters: Mapping[str, Any]
    material: str
    non_model: bool = False


@dataclass(frozen=True, slots=True)
class OperationPlan:
    kind: str
    target: str
    tools: tuple[str, ...] = ()
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PortPlan:
    name: str
    sheet_name: str
    plane: str
    origin: tuple[str, str, str]
    sizes: tuple[str, str]
    modes: int = 1
    renormalize: bool = True


@dataclass(frozen=True, slots=True)
class MeshPlan:
    name: str
    assignment: tuple[str, ...]
    max_length: str
    restrict_length: bool = True


@dataclass(frozen=True, slots=True)
class GeometryPlan:
    schema: str
    identifier: str
    variant: str
    solution_type: str
    variables: Mapping[str, str]
    primitives: tuple[PrimitivePlan, ...]
    operations: tuple[OperationPlan, ...]
    ports: tuple[PortPlan, ...]
    meshes: tuple[MeshPlan, ...]
    open_region_frequency: str | None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.schema != "enz-eigenchannel-mimo/aedt-geometry-plan/v1":
            raise ValueError("schema de plano não suportado")
        names = [primitive.name for primitive in self.primitives]
        if len(names) != len(set(names)):
            raise ValueError("nomes de primitivas duplicados")
        known = set(names)
        for operation in self.operations:
            if operation.target not in known:
                raise ValueError(f"alvo de operação inexistente: {operation.target}")
            missing = [tool for tool in operation.tools if tool not in known]
            if missing:
                raise ValueError(f"ferramentas inexistentes: {missing}")
        for port in self.ports:
            if port.sheet_name not in known:
                raise ValueError(f"sheet de porta inexistente: {port.sheet_name}")
        if self.solution_type == "Eigenmode" and self.ports:
            raise ValueError("modelo Eigenmode não pode possuir porta excitada")
        if self.solution_type == "Modal" and not self.ports:
            raise ValueError("modelo Driven Modal exige pelo menos uma porta")

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)
