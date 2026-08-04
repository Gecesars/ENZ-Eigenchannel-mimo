from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from enz_eigenchannel_mimo.aedt.runtime import (
    AedtRuntimeSpec,
    capturar_runtime_app,
    preflight_aedt,
)
from enz_eigenchannel_mimo.specifications import sha256_arquivo


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return str(value)


def _capture(
    errors: list[dict[str, str]], label: str, function: Callable[[], Any]
) -> Any:
    try:
        return _jsonable(function())
    except Exception as exc:  # noqa: BLE001 -- toda falha externa fica registrada
        errors.append(
            {"field": label, "error_type": type(exc).__name__, "error": str(exc)}
        )
        return None


def _capture_raw(
    errors: list[dict[str, str]], label: str, function: Callable[[], Any]
) -> Any:
    try:
        return function()
    except Exception as exc:  # noqa: BLE001 -- toda falha externa fica registrada
        errors.append(
            {"field": label, "error_type": type(exc).__name__, "error": str(exc)}
        )
        return None


def _objects(app: Any, errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for name in sorted(app.modeler.object_names):
        obj = app.modeler[name]
        result.append(
            {
                "name": name,
                "id": _capture(errors, f"object.{name}.id", lambda obj=obj: obj.id),
                "object_type": _capture(
                    errors,
                    f"object.{name}.object_type",
                    lambda obj=obj: obj.object_type,
                ),
                "material": _capture(
                    errors,
                    f"object.{name}.material",
                    lambda obj=obj: obj.material_name,
                ),
                "group": _capture(
                    errors, f"object.{name}.group", lambda obj=obj: obj.group_name
                ),
                "is_model": _capture(
                    errors, f"object.{name}.is_model", lambda obj=obj: obj.is_model
                ),
                "solve_inside": _capture(
                    errors,
                    f"object.{name}.solve_inside",
                    lambda obj=obj: obj.solve_inside,
                ),
                "bounding_box_model_units": _capture(
                    errors,
                    f"object.{name}.bounding_box",
                    lambda obj=obj: obj.bounding_box,
                ),
            }
        )
    return result


def _named_objects(
    entries: list[Any], errors: list[dict[str, str]], prefix: str
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            result.append(
                {
                    "name": entry,
                    "python_type": "str",
                    "type": None,
                    "properties": None,
                }
            )
            continue
        name = _capture(
            errors, f"{prefix}.{index}.name", lambda entry=entry: entry.name
        )
        native_type = type(entry).__name__
        type_value = (
            _capture(
                errors,
                f"{prefix}.{name}.type",
                lambda entry=entry: entry.type,
            )
            if hasattr(entry, "type")
            else native_type
        )
        properties = (
            _capture(
                errors,
                f"{prefix}.{name}.properties",
                lambda entry=entry: entry.props,
            )
            if hasattr(entry, "props")
            else None
        )
        result.append(
            {
                "name": name,
                "python_type": native_type,
                "type": type_value,
                "properties": properties,
            }
        )
    return result


def _field_plots(app: Any, errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    plots = _capture_raw(errors, "field_plots", lambda: app.post.field_plots) or {}
    result: list[dict[str, Any]] = []
    for name, plot in plots.items():
        row: dict[str, Any] = {"name": name, "python_type": type(plot).__name__}
        for attribute in (
            "plot_folder",
            "quantity",
            "solution",
            "intrinsics",
            "surfaces",
            "volumes",
            "cutplanes",
            "lines",
            "seeding_faces",
        ):
            if hasattr(plot, attribute):
                row[attribute] = _capture(
                    errors,
                    f"field_plot.{name}.{attribute}",
                    lambda plot=plot, attribute=attribute: getattr(plot, attribute),
                )
        result.append(row)
    return result


def inspect_model(app: Any, project: Path, output_dir: Path) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    object_inventory = _objects(app, errors)
    setups: list[dict[str, Any]] = []
    for setup in app.setups:
        setup_name = _capture(
            errors, "setup.name", lambda setup=setup: setup.name
        )
        sweeps = _named_objects(
            list(
                _capture_raw(
                    errors,
                    f"setup.{setup_name}.sweeps",
                    lambda setup=setup: setup.sweeps,
                )
                or []
            ),
            errors,
            f"setup.{setup_name}.sweeps",
        )
        setups.append(
            {
                "name": setup_name,
                "properties": _capture(
                    errors,
                    f"setup.{setup_name}.properties",
                    lambda setup=setup: setup.props,
                ),
                "sweeps": sweeps,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    preview = output_dir / "hfss_design_preview.jpg"
    preview_ok = bool(app.export_design_preview_to_jpg(preview))
    if not preview_ok or not preview.is_file() or preview.stat().st_size == 0:
        errors.append(
            {
                "field": "hfss_design_preview",
                "error_type": "ExportError",
                "error": "AEDT não exportou uma prévia não vazia",
            }
        )

    messages_path = output_dir / "aedt_messages.log"
    messages = _capture(
        errors,
        "aedt_messages",
        lambda: list(app.desktop_class.odesktop.GetMessages("", "", 0)),
    )
    messages_path.write_text(
        "\n".join(str(item) for item in (messages or [])) + "\n", encoding="utf-8"
    )

    field_plots = _field_plots(app, errors)
    coordinate_systems = _named_objects(
        list(
            _capture_raw(
                errors, "coordinate_systems", lambda: app.modeler.coordinate_systems
            )
            or []
        ),
        errors,
        "coordinate_systems",
    )
    mesh_operations = _named_objects(
        list(
            _capture_raw(
                errors, "mesh_operations", lambda: app.mesh.meshoperations
            )
            or []
        ),
        errors,
        "mesh_operations",
    )
    boundaries = _named_objects(
        list(_capture_raw(errors, "boundaries", lambda: app.boundaries) or []),
        errors,
        "boundaries",
    )
    parametrics = _named_objects(
        list(
            _capture_raw(errors, "parametrics", lambda: app.parametrics.setups)
            or []
        ),
        errors,
        "parametrics",
    )

    return {
        "schema": "enz-eigenchannel-mimo/q0-hfss-inspection/v1",
        "classification": "SIMULADO",
        "purpose": "inspeção Q0 somente leitura; não promove o modelo a validado",
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "project": {
            "path": str(project),
            "bytes": project.stat().st_size,
            "sha256_before_open": sha256_arquivo(project),
            "project_name": _capture(errors, "project_name", lambda: app.project_name),
            "design_name": _capture(errors, "design_name", lambda: app.design_name),
            "solution_type": _capture(
                errors, "solution_type", lambda: app.solution_type
            ),
            "model_units": _capture(
                errors, "model_units", lambda: app.modeler.model_units
            ),
        },
        "counts": {
            "objects": len(object_inventory),
            "solids": len(app.modeler.solid_names),
            "sheets": len(app.modeler.sheet_names),
            "lines": len(app.modeler.line_names),
            "points": len(app.modeler.point_names),
            "boundaries": len(boundaries),
            "excitations": len(app.excitation_names),
            "setups": len(setups),
            "reports": len(app.post.all_report_names),
            "field_plots": len(field_plots),
            "coordinate_systems": len(coordinate_systems),
            "mesh_operations": len(mesh_operations),
            "parametric_setups": len(parametrics),
        },
        "objects": object_inventory,
        "boundaries": boundaries,
        "excitations": list(app.excitation_names),
        "setups": setups,
        "existing_analysis_sweeps": _capture(
            errors, "existing_analysis_sweeps", lambda: app.existing_analysis_sweeps
        ),
        "reports": list(app.post.all_report_names),
        "field_plots": field_plots,
        "coordinate_systems": coordinate_systems,
        "mesh_operations": mesh_operations,
        "parametric_setups": parametrics,
        "design_variables": _capture(
            errors,
            "design_variables",
            lambda: app.variable_manager.design_variables,
        ),
        "project_variables": _capture(
            errors,
            "project_variables",
            lambda: app.variable_manager.project_variables,
        ),
        "visual_artifacts": {
            "preview": str(preview) if preview_ok else None,
            "messages": str(messages_path),
        },
        "extraction_errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Abre o candidato Q0 no HFSS, captura inventário e deixa a sessão aberta."
    )
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artefatos/q0/hfss_inspection"),
    )
    parser.add_argument("--deixar-aedt-aberto", action="store_true")
    parser.add_argument("--porta-grpc", type=int, default=0)
    args = parser.parse_args()

    project = args.project.resolve()
    output_dir = args.output.resolve()
    runtime = AedtRuntimeSpec(
        non_graphical=False, close_on_exit=False, port=args.porta_grpc
    )
    preflight = preflight_aedt(runtime)
    app: Any | None = None
    try:
        from ansys.aedt.core import Hfss

        app = Hfss(
            project=str(project),
            version=runtime.version,
            non_graphical=False,
            new_desktop=args.porta_grpc == 0,
            close_on_exit=False,
            remove_lock=False,
        )
        result = inspect_model(app, project, output_dir)
        result["runtime"] = {
            **capturar_runtime_app(app, runtime),
            "pyaedt": preflight.pyaedt_version,
            "license": preflight.license_status,
            "transport": "native AEDT gRPC via PyAEDT",
            "session_left_open": args.deixar_aedt_aberto,
        }
        result["project"]["sha256_after_inspection"] = sha256_arquivo(project)
        result["project"]["unchanged_by_inspection"] = (
            result["project"]["sha256_before_open"]
            == result["project"]["sha256_after_inspection"]
        )
        output = output_dir / "hfss_inspection.json"
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(result["runtime"], ensure_ascii=False, indent=2))
        print(json.dumps(result["counts"], ensure_ascii=False, indent=2))
        print(f"inspection={output}")
        return 0
    finally:
        if app is not None:
            close = args.porta_grpc == 0 and not args.deixar_aedt_aberto
            app.release_desktop(close_projects=close, close_desktop=close)


if __name__ == "__main__":
    raise SystemExit(main())
