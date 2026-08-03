"""Interpretador PyAEDT para o plano CAD declarativo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from enz_eigenchannel_mimo.geometry.plan import GeometryPlan, PrimitivePlan


@dataclass(frozen=True, slots=True)
class BuildArtifacts:
    project_path: str
    design_name: str
    primitive_names: tuple[str, ...]
    port_names: tuple[str, ...]
    boundary_names: tuple[str, ...]
    mesh_names: tuple[str, ...]
    setup_names: tuple[str, ...]
    sweep_names: tuple[str, ...]

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)


class AedtGeometryBuilder:
    def __init__(self, app: Any) -> None:
        self.app = app

    def build(
        self,
        plan: GeometryPlan,
        *,
        project_path: str | Path,
        configure_analysis: bool = True,
    ) -> BuildArtifacts:
        plan.validate()
        self._set_units()
        self._set_variables(plan)
        created: dict[str, Any] = {}
        for primitive in plan.primitives:
            created[primitive.name] = self._create_primitive(primitive)
            if primitive.non_model:
                self._set_non_model(primitive.name)

        for operation in plan.operations:
            self._apply_operation(operation.kind, operation.target, operation.tools, dict(operation.parameters))

        port_names = tuple(self._create_port(port) for port in plan.ports)
        boundary_names: list[str] = []
        if plan.open_region_frequency:
            if not self._enable_auto_open(plan.open_region_frequency):
                raise RuntimeError("falha ao habilitar Auto-Open Region = Radiation")
            boundary_names.append("Auto-Open Region = Radiation")

        mesh_names = tuple(self._create_mesh(mesh) for mesh in plan.meshes)
        setup_names: tuple[str, ...] = ()
        sweep_names: tuple[str, ...] = ()
        if configure_analysis:
            setup_names, sweep_names = self._configure_analysis(plan)

        project = Path(project_path).expanduser().resolve()
        project.parent.mkdir(parents=True, exist_ok=True)
        result = self.app.save_project(str(project))
        if result is False:
            raise RuntimeError("AEDT recusou o salvamento após build")

        return BuildArtifacts(
            project_path=str(project),
            design_name=str(getattr(self.app, "design_name", "")),
            primitive_names=tuple(created),
            port_names=port_names,
            boundary_names=tuple(boundary_names),
            mesh_names=mesh_names,
            setup_names=setup_names,
            sweep_names=sweep_names,
        )

    def _set_units(self) -> None:
        modeler = self.app.modeler
        try:
            modeler.model_units = "mm"
        except Exception:
            try:
                modeler.set_model_units("mm")
            except Exception as exc:
                raise RuntimeError("não foi possível fixar as unidades em mm") from exc

    def _set_variables(self, plan: GeometryPlan) -> None:
        manager = getattr(self.app, "variable_manager", None)
        for name, expression in plan.variables.items():
            if manager is not None and hasattr(manager, "set_variable"):
                ok = manager.set_variable(
                    name=name,
                    expression=expression,
                    overwrite=True,
                    sweep=True,
                    description=f"ENZ plan {plan.identifier}",
                )
                if ok is False:
                    raise RuntimeError(f"falha ao criar variável AEDT {name}")
            else:
                self.app[name] = expression

    def _create_primitive(self, primitive: PrimitivePlan) -> Any:
        modeler = self.app.modeler
        p = dict(primitive.parameters)
        if primitive.kind == "box":
            return modeler.create_box(
                list(p["origin"]),
                list(p["sizes"]),
                name=primitive.name,
                material=primitive.material,
            )
        if primitive.kind == "rectangle":
            return modeler.create_rectangle(
                p["plane"],
                list(p["origin"]),
                list(p["sizes"]),
                name=primitive.name,
                material=primitive.material,
            )
        if primitive.kind == "cylinder":
            return modeler.create_cylinder(
                p["axis"],
                list(p["position"]),
                p["radius"],
                p["height"],
                name=primitive.name,
                material=primitive.material,
            )
        raise ValueError(f"primitiva não suportada: {primitive.kind}")

    def _set_non_model(self, name: str) -> None:
        modeler = self.app.modeler
        try:
            modeler.set_object_model_state(name, model=False)
        except TypeError:
            try:
                modeler.set_object_model_state([name], model=False)
            except Exception:
                pass
        except Exception:
            pass

    def _apply_operation(
        self,
        kind: str,
        target: str,
        tools: tuple[str, ...],
        parameters: dict[str, Any],
    ) -> None:
        modeler = self.app.modeler
        if kind == "subtract":
            result = modeler.subtract(
                target,
                list(tools),
                keep_originals=bool(parameters.get("keep_originals", False)),
            )
            if result is False:
                raise RuntimeError(f"subtract falhou: {target} - {tools}")
            return
        if kind == "unite":
            result = modeler.unite([target, *tools])
            if result is False:
                raise RuntimeError(f"unite falhou: {target}, {tools}")
            return
        if kind == "chamfer":
            obj = modeler[target]
            distance = parameters["distance"]
            for edge_index in parameters["edge_indices"]:
                edges = list(obj.edges)
                if edge_index >= len(edges):
                    raise RuntimeError(
                        f"aresta {edge_index} não existe em {target}; total={len(edges)}"
                    )
                if edges[edge_index].chamfer(left_distance=distance) is False:
                    raise RuntimeError(f"chanfro falhou em {target}.edge[{edge_index}]")
            return
        raise ValueError(f"operação CAD não suportada: {kind}")

    def _create_port(self, port: Any) -> str:
        boundary = self.app.wave_port(
            assignment=port.sheet_name,
            modes=port.modes,
            impedance=50,
            name=port.name,
            renormalize=port.renormalize,
        )
        if boundary is False or boundary is None:
            raise RuntimeError(f"falha ao criar wave port {port.name}")
        return str(getattr(boundary, "name", port.name))

    def _enable_auto_open(self, frequency: str) -> bool:
        if hasattr(self.app, "set_auto_open"):
            try:
                result = self.app.set_auto_open(True, opening_type="Radiation")
                if result is not False:
                    return True
            except Exception:
                pass
        if hasattr(self.app, "create_open_region"):
            try:
                return bool(self.app.create_open_region(frequency=frequency, boundary="Radiation"))
            except TypeError:
                return bool(self.app.create_open_region(frequency))
        return False

    def _create_mesh(self, mesh: Any) -> str:
        mesh_module = self.app.mesh
        result = mesh_module.assign_length_mesh(
            assignment=list(mesh.assignment),
            maximum_length=mesh.max_length,
            restrict_length=mesh.restrict_length,
            name=mesh.name,
        )
        if result is False or result is None:
            raise RuntimeError(f"falha ao criar malha local {mesh.name}")
        return str(getattr(result, "name", mesh.name))

    def _configure_analysis(self, plan: GeometryPlan) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if plan.solution_type == "Eigenmode":
            setup = self.app.create_setup(
                name="Setup_Eigenmode_18_32GHz",
                setup_type="HFSSEigen",
            )
            setup.props["MinimumFrequency"] = "18GHz"
            setup.props["NumModes"] = 12
            setup.props["MaxDeltaFreq"] = 0.1
            setup.props["MaximumPasses"] = 12
            setup.props["MinimumPasses"] = 2
            if setup.update() is False:
                raise RuntimeError("falha ao atualizar setup Eigenmode")
            return (str(setup.name),), ()

        setup = self.app.create_setup(
            name="Setup_Driven_25p87GHz",
            setup_type="HFSSDriven",
            Frequency="25.87GHz",
            MaximumPasses=15,
            MinimumPasses=2,
            MaxDeltaS=0.02,
            PercentRefinement=30,
            SaveFields=True,
            SaveRadFieldsOnly=False,
        )
        sweep = setup.add_sweep(name="Sweep_25p3_26p8GHz")
        sweep.props["RangeType"] = "LinearStep"
        sweep.props["RangeStart"] = "25.3GHz"
        sweep.props["RangeEnd"] = "26.8GHz"
        sweep.props["RangeStep"] = "0.01GHz"
        sweep.props["Type"] = "Interpolating"
        sweep.props["SaveFields"] = False
        sweep.props["SaveRadFieldsOnly"] = False
        if sweep.update() is False:
            raise RuntimeError("falha ao atualizar sweep Driven Modal")
        return (str(setup.name),), (str(sweep.name),)
