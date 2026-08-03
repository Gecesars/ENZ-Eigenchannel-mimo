"""Síntese declarativa das geometrias G0/M0-M4."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .plan import GeometryPlan, MeshPlan, OperationPlan, PortPlan, PrimitivePlan
from .spec import G0GeometrySpec, VarianteModelo


def mm(value: float) -> str:
    return f"{value:.12g}mm"


def ghz(value: float) -> str:
    return f"{value:.12g}GHz"


def build_geometry_plan(spec: G0GeometrySpec) -> GeometryPlan:
    spec.validate()
    cavity = spec.cavidade
    width = cavity.largura.require("cavidade.largura")
    height = cavity.altura.require("cavidade.altura")
    length = cavity.comprimento.require("cavidade.comprimento")
    wall = cavity.espessura_parede.require("cavidade.espessura_parede")

    variables: dict[str, str] = {
        "f0": ghz(spec.frequencia_central_ghz),
        "cav_w": mm(width),
        "cav_h": mm(height),
        "cav_l": mm(length),
        "wall_t": mm(wall),
    }
    primitives: list[PrimitivePlan] = [
        PrimitivePlan(
            name="Cavity_Metal",
            kind="box",
            parameters={
                "origin": ("0mm", f"-cav_w/2-wall_t", "-wall_t"),
                "sizes": ("cav_l", "cav_w+2*wall_t", "cav_h+2*wall_t"),
            },
            material=spec.material_metal,
        ),
        PrimitivePlan(
            name="Cavity_Void_Tool",
            kind="box",
            parameters={
                "origin": ("0mm", "-cav_w/2", "0mm"),
                "sizes": ("cav_l", "cav_w", "cav_h"),
            },
            material="vacuum",
            non_model=True,
        ),
    ]
    operations: list[OperationPlan] = [
        OperationPlan(
            kind="subtract",
            target="Cavity_Metal",
            tools=("Cavity_Void_Tool",),
            parameters={"keep_originals": False},
        )
    ]
    ports: list[PortPlan] = []

    if spec.guia is not None:
        guide = spec.guia
        a = guide.a.require("guia.a")
        b = guide.b.require("guia.b")
        feed_l = guide.comprimento.require("guia.comprimento")
        feed_wall = guide.espessura_parede.require("guia.espessura_parede")
        variables.update(
            {
                "wg_a": mm(a),
                "wg_b": mm(b),
                "wg_l": mm(feed_l),
                "wg_wall_t": mm(feed_wall),
            }
        )
        primitives.extend(
            [
                PrimitivePlan(
                    name="Feed_Metal",
                    kind="box",
                    parameters={
                        "origin": ("-wg_l", "-wg_a/2-wg_wall_t", "-wg_wall_t"),
                        "sizes": ("wg_l+wall_t", "wg_a+2*wg_wall_t", "wg_b+2*wg_wall_t"),
                    },
                    material=spec.material_metal,
                ),
                PrimitivePlan(
                    name="Feed_Void_Tool",
                    kind="box",
                    parameters={
                        "origin": ("-wg_l", "-wg_a/2", "0mm"),
                        "sizes": ("wg_l+wall_t", "wg_a", "wg_b"),
                    },
                    material="vacuum",
                    non_model=True,
                ),
                PrimitivePlan(
                    name="Port_Sheet",
                    kind="rectangle",
                    parameters={
                        "plane": "YZ",
                        "origin": ("-wg_l", "-wg_a/2", "0mm"),
                        "sizes": ("wg_a", "wg_b"),
                    },
                    material="vacuum",
                ),
            ]
        )
        operations.extend(
            [
                OperationPlan(
                    kind="subtract",
                    target="Feed_Metal",
                    tools=("Feed_Void_Tool",),
                    parameters={"keep_originals": False},
                ),
                OperationPlan(
                    kind="unite",
                    target="Cavity_Metal",
                    tools=("Feed_Metal",),
                ),
            ]
        )
        ports.append(
            PortPlan(
                name=guide.nome_porta,
                sheet_name="Port_Sheet",
                plane="YZ",
                origin=("-wg_l", "-wg_a/2", "0mm"),
                sizes=("wg_a", "wg_b"),
            )
        )

    for index, slot in enumerate(spec.ranhuras, start=1):
        sx = slot.centro_x.require(f"{slot.nome}.centro_x", positivo=False)
        sy = slot.centro_y.require(f"{slot.nome}.centro_y", positivo=False)
        sl = slot.comprimento.require(f"{slot.nome}.comprimento")
        sw = slot.largura.require(f"{slot.nome}.largura")
        prefix = f"slot_{index}"
        variables.update(
            {
                f"{prefix}_x": mm(sx),
                f"{prefix}_y": mm(sy),
                f"{prefix}_l": mm(sl),
                f"{prefix}_w": mm(sw),
                f"{prefix}_angle": f"{slot.angulo_deg:.12g}deg",
            }
        )
        cutter_name = f"{slot.nome}_Cutter"
        angle = slot.angulo_deg % 180.0
        if abs(angle) < 1e-9:
            origin_xy = (
                f"{prefix}_x-{prefix}_l/2",
                f"{prefix}_y-{prefix}_w/2",
            )
            sizes_xy = (f"{prefix}_l", f"{prefix}_w")
        elif abs(angle - 90.0) < 1e-9:
            origin_xy = (
                f"{prefix}_x-{prefix}_w/2",
                f"{prefix}_y-{prefix}_l/2",
            )
            sizes_xy = (f"{prefix}_w", f"{prefix}_l")
        else:
            raise ValueError(
                "builder G0/v1 aceita ranhuras alinhadas a 0/90 graus; "
                f"{slot.nome} usa {slot.angulo_deg:g} graus"
            )
        primitives.append(
            PrimitivePlan(
                name=cutter_name,
                kind="box",
                parameters={
                    "origin": (*origin_xy, "cav_h-wall_t/2"),
                    "sizes": (*sizes_xy, "2*wall_t"),
                },
                material="vacuum",
                non_model=True,
            )
        )
        operations.append(
            OperationPlan(
                kind="subtract",
                target="Cavity_Metal",
                tools=(cutter_name,),
                parameters={"keep_originals": False},
            )
        )

    if spec.degrau is not None:
        step = spec.degrau
        values = {
            "step_x": step.origem_x.require("degrau.origem_x", positivo=False),
            "step_y": step.origem_y.require("degrau.origem_y", positivo=False),
            "step_l": step.comprimento_x.require("degrau.comprimento_x"),
            "step_w": step.largura_y.require("degrau.largura_y"),
            "step_h": step.altura_z.require("degrau.altura_z"),
        }
        variables.update({key: mm(value) for key, value in values.items()})
        primitives.append(
            PrimitivePlan(
                name=step.nome,
                kind="box",
                parameters={
                    "origin": ("step_x", "step_y", "cav_h-step_h"),
                    "sizes": ("step_l", "step_w", "step_h"),
                },
                material=spec.material_metal if step.operacao == "add_metal" else "vacuum",
                non_model=step.operacao == "remove_metal",
            )
        )
        operations.append(
            OperationPlan(
                kind="unite" if step.operacao == "add_metal" else "subtract",
                target="Cavity_Metal",
                tools=(step.nome,),
                parameters={"keep_originals": False},
            )
        )

    if spec.dieletrico is not None:
        dielectric = spec.dieletrico
        origin = [
            value.require(f"dieletrico.origem_{axis}", positivo=False)
            for axis, value in zip("xyz", dielectric.origem_xyz, strict=True)
        ]
        size = [
            value.require(f"dieletrico.tamanho_{axis}")
            for axis, value in zip("xyz", dielectric.tamanho_xyz, strict=True)
        ]
        for axis, value in zip("xyz", origin, strict=True):
            variables[f"dopant_{axis}"] = mm(value)
        for axis, value in zip("xyz", size, strict=True):
            variables[f"dopant_d{axis}"] = mm(value)
        primitives.append(
            PrimitivePlan(
                name=dielectric.nome,
                kind="box",
                parameters={
                    "origin": ("dopant_x", "dopant_y", "dopant_z"),
                    "sizes": ("dopant_dx", "dopant_dy", "dopant_dz"),
                },
                material=dielectric.material,
            )
        )

    for index, pin in enumerate(spec.pinos, start=1):
        px = pin.centro_x.require(f"{pin.nome}.centro_x", positivo=False)
        py = pin.centro_y.require(f"{pin.nome}.centro_y", positivo=False)
        diameter = pin.diametro.require(f"{pin.nome}.diametro")
        pin_height = pin.altura.require(f"{pin.nome}.altura")
        prefix = f"pin_{index}"
        variables.update(
            {
                f"{prefix}_x": mm(px),
                f"{prefix}_y": mm(py),
                f"{prefix}_r": mm(diameter / 2.0),
                f"{prefix}_h": mm(pin_height),
            }
        )
        primitives.append(
            PrimitivePlan(
                name=pin.nome,
                kind="cylinder",
                parameters={
                    "axis": "Z",
                    "position": (f"{prefix}_x", f"{prefix}_y", "0mm"),
                    "radius": f"{prefix}_r",
                    "height": f"{prefix}_h",
                },
                material=spec.material_metal,
            )
        )
        operations.append(
            OperationPlan(kind="unite", target="Cavity_Metal", tools=(pin.nome,))
        )

    for chamfer in spec.chanfros:
        operations.append(
            OperationPlan(
                kind="chamfer",
                target=chamfer.objeto,
                parameters={
                    "edge_indices": chamfer.edge_indices,
                    "distance": mm(chamfer.distancia.require("chanfro.distancia")),
                },
            )
        )

    meshes = (
        MeshPlan(
            name="Mesh_Cavity_Slot_Region",
            assignment=("Cavity_Metal",),
            max_length=mm(max(0.05, min(width, height) / 30.0)),
        ),
    ) if spec.ranhuras else ()

    plan = GeometryPlan(
        schema="enz-eigenchannel-mimo/aedt-geometry-plan/v1",
        identifier=spec.identificador,
        variant=spec.variante.value,
        solution_type=(
            "Eigenmode"
            if spec.variante is VarianteModelo.M0_CAVIDADE_FECHADA
            else "Modal"
        ),
        variables=variables,
        primitives=tuple(primitives),
        operations=tuple(operations),
        ports=tuple(ports),
        meshes=meshes,
        open_region_frequency=(
            None
            if spec.variante is VarianteModelo.M0_CAVIDADE_FECHADA
            else ghz(spec.frequencia_central_ghz)
        ),
        metadata={
            "coordinate_system": "X longitudinal, Y transversal, Z vertical",
            "source_spec": asdict(spec),
        },
    )
    plan.validate()
    return plan
