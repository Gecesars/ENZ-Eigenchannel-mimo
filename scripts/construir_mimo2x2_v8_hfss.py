from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import traceback
import xml.etree.ElementTree as ET
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from enz_eigenchannel_mimo.aedt.runtime import (
    AedtRuntimeSpec,
    capturar_runtime_app,
    preflight_aedt,
)
from enz_eigenchannel_mimo.metrics import potencia_aceita, tarc
from enz_eigenchannel_mimo.mimo2x2 import (
    Mimo2x2C0Spec,
    ecc_campos_complexos,
    ler_ffd_complexo,
    ler_touchstone_s2p,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DEFAULT = (
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "G0_figura2_v7"
    / "projeto_configurado"
    / "G0_figura2_reconstrucao_v7_M4.aedt"
)
PACKAGE_DEFAULT = (
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "Q4_mimo2x2_c0_v8"
)
TARGET_DEFAULT = (
    PACKAGE_DEFAULT
    / "projeto_configurado"
    / "Q4_mimo2x2_c0_v8_HIPOTESE.aedt"
)
ARTIFACT_DEFAULT = ROOT / "artefatos" / "q4_mimo2x2_c0_v8"
DESIGN_NAME = "HFSS_ENZ_Q4_mimo2x2_c0_v8"
SETUP_NAME = "Setup_Q4_MIMO2X2"
SWEEP_NAME = "Sweep_Q4_25_27GHz"
SPHERE_NAME = "FF_Q4_3D"
BASE_OBJECTS = [
    "Cavity_Air",
    "FR4_Slab",
    "Housing_Cavity",
    "MountHole_L",
    "MountHole_R",
    "Rod_PEC_NE",
    "Rod_PEC_NW",
    "Rod_PEC_SE",
    "Rod_PEC_SW",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return str(value)


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(data), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def require(result: Any, message: str) -> Any:
    if not result:
        raise RuntimeError(message)
    return result


def clean_previous_configuration(app: Any) -> None:
    for setup in list(getattr(app.parametrics, "setups", [])):
        require(
            app.parametrics.delete(setup.name),
            f"falha ao excluir estudo paramétrico {setup.name}",
        )
    for plot in list(getattr(app.post, "field_plots", {}).values()):
        require(plot.delete(), f"falha ao excluir field plot {plot.name}")
    for report in list(app.post.all_report_names):
        require(app.post.delete_report(report), f"falha ao excluir report {report}")
    for field_setup in list(getattr(app, "field_setups", [])):
        require(
            field_setup.delete(),
            f"falha ao excluir field setup {field_setup.name}",
        )
    for setup in list(app.setups):
        require(setup.delete(), f"falha ao excluir setup {setup.name}")
    for boundary in list(app.boundaries):
        require(boundary.delete(), f"falha ao excluir boundary {boundary.name}")
    for coordinate_system in list(app.modeler.coordinate_systems):
        require(
            coordinate_system.delete(),
            f"falha ao excluir CS {coordinate_system.name}",
        )
    require(
        app.modeler.delete(["Open_Region", "Port_WR28_Sheet"]),
        "falha ao excluir região/porta da v7",
    )


def rename_clone_set(
    app: Any,
    source_names: list[str],
    clone_names: list[str],
    target_id: str,
) -> list[str]:
    renamed: list[str] = []
    for source_name in source_names:
        root_name = source_name.removesuffix("_RAD_A1")
        candidates = [name for name in clone_names if name.startswith(source_name)]
        if len(candidates) != 1:
            raise RuntimeError(
                f"clone ambíguo para {source_name}: {sorted(candidates)}"
            )
        target_name = f"{root_name}_{target_id}"
        app.modeler[candidates[0]].name = target_name
        renamed.append(target_name)
    return renamed


def duplicate_radiators(app: Any, spec: Mimo2x2C0Spec) -> dict[str, list[str]]:
    missing = [name for name in BASE_OBJECTS if name not in app.modeler.object_names]
    if missing:
        raise RuntimeError(f"objetos fonte ausentes: {missing}")

    source_names: list[str] = []
    for name in BASE_OBJECTS:
        target_name = f"{name}_RAD_A1"
        app.modeler[name].name = target_name
        source_names.append(target_name)
    first_x = spec.radiator_centers_x_mm["RAD_A1"]
    require(
        app.modeler.move(source_names, [first_x, 0.0, 0.0]),
        "falha ao posicionar RAD_A1",
    )
    result = {"RAD_A1": source_names}
    for target_id in ("RAD_A2", "RAD_B1", "RAD_B2"):
        vector_x = spec.radiator_centers_x_mm[target_id] - first_x
        success, clone_names = app.modeler.duplicate_along_line(
            source_names,
            [vector_x, 0.0, 0.0],
            clones=2,
            attach=False,
            duplicate_assignment=False,
        )
        require(success, f"falha ao duplicar {target_id}")
        result[target_id] = rename_clone_set(
            app, source_names, list(clone_names), target_id
        )
    app.modeler.refresh_all_ids()
    return result


def build_feed(
    app: Any,
    spec: Mimo2x2C0Spec,
    pair: str,
    port_name: str,
) -> dict[str, Any]:
    pair_center = spec.pair_centers_x_mm[pair]
    outer_x_min = pair_center - spec.feed_housing_width_mm / 2.0
    outer_y_min = spec.external_port_y_mm
    outer_y_size = spec.source_port_y_mm - outer_y_min
    housing_name = f"WG_{pair}_Housing_PEC"
    housing = require(
        app.modeler.create_box(
            [outer_x_min, outer_y_min, spec.source_housing_z_min_mm],
            [
                spec.feed_housing_width_mm,
                outer_y_size,
                spec.source_housing_z_max_mm
                - spec.source_housing_z_min_mm,
            ],
            name=housing_name,
            material="pec",
        ),
        f"falha ao criar {housing_name}",
    )

    air_height = spec.wg_a_z_mm
    main = require(
        app.modeler.create_box(
            [
                pair_center - spec.wg_b_x_mm / 2.0,
                spec.external_port_y_mm,
                spec.source_air_z_min_mm,
            ],
            [spec.wg_b_x_mm, spec.input_length_mm, air_height],
            name=f"WG_{pair}_Main_Air",
            material="vacuum",
        ),
        f"falha ao criar main WG-{pair}",
    )
    junction = require(
        app.modeler.create_box(
            [
                pair_center - spec.manifold_air_width_mm / 2.0,
                spec.junction_y_min_mm,
                spec.source_air_z_min_mm,
            ],
            [
                spec.manifold_air_width_mm,
                spec.junction_length_mm,
                air_height,
            ],
            name=f"WG_{pair}_Junction_Air",
            material="vacuum",
        ),
        f"falha ao criar junção WG-{pair}",
    )
    branch_names: list[str] = []
    pair_half = spec.pair_spacing_mm / 2.0
    for index, x_center in enumerate(
        (pair_center - pair_half, pair_center + pair_half),
        start=1,
    ):
        branch = require(
            app.modeler.create_box(
                [
                    x_center - spec.wg_b_x_mm / 2.0,
                    spec.branch_y_min_mm,
                    spec.source_air_z_min_mm,
                ],
                [spec.wg_b_x_mm, spec.branch_length_mm, air_height],
                name=f"WG_{pair}_Branch{index}_Air",
                material="vacuum",
            ),
            f"falha ao criar branch {index} de WG-{pair}",
        )
        branch_names.append(branch.name)
    air_name = require(
        app.modeler.unite(
            [main.name, junction.name, *branch_names],
            purge=True,
            keep_originals=False,
        ),
        f"falha ao unir canal de WG-{pair}",
    )
    air = app.modeler[air_name]
    air.name = f"WG_{pair}_Air"
    require(
        app.modeler.subtract(housing, air, keep_originals=True),
        f"falha ao subtrair canal de WG-{pair}",
    )

    port_sheet = require(
        app.modeler.create_rectangle(
            "ZX",
            [
                pair_center - spec.wg_b_x_mm / 2.0,
                spec.external_port_y_mm,
                spec.source_air_z_min_mm,
            ],
            [spec.wg_a_z_mm, spec.wg_b_x_mm],
            name=f"{port_name}_Sheet",
            material="vacuum",
        ),
        f"falha ao criar sheet {port_name}",
    )
    integration_line = [
        [
            pair_center,
            spec.external_port_y_mm,
            spec.source_air_z_min_mm,
        ],
        [
            pair_center,
            spec.external_port_y_mm,
            spec.source_air_z_min_mm + spec.wg_a_z_mm,
        ],
    ]
    port = require(
        app.wave_port(
            assignment=port_sheet,
            reference=[housing],
            create_port_sheet=False,
            integration_line=integration_line,
            modes=1,
            impedance=50,
            name=port_name,
            renormalize=True,
            deembed=0,
        ),
        f"falha ao criar waveport {port_name}",
    )
    return {
        "housing": housing.name,
        "air": air.name,
        "sheet": port_sheet.name,
        "boundary": port.name,
        "integration_line_mm": integration_line,
        "pair_center_x_mm": pair_center,
    }


def build_region(app: Any, spec: Mimo2x2C0Spec) -> dict[str, Any]:
    x_min, y_min, z_min, x_max, y_max, z_max = spec.region_bounds_mm
    region = require(
        app.modeler.create_box(
            [x_min, y_min, z_min],
            [x_max - x_min, y_max - y_min, z_max - z_min],
            name="Open_Region_Q4",
            material="air",
        ),
        "falha ao criar região aberta Q4",
    )
    faces = list(region.faces)
    y_min_face = min(faces, key=lambda face: float(face.center[1]))
    radiation_faces = [face for face in faces if face.id != y_min_face.id]
    boundary = require(
        app.assign_radiation_boundary_to_faces(
            radiation_faces,
            name="Radiation_Q4_5Faces",
        ),
        "falha ao criar Radiation_Q4_5Faces",
    )
    return {
        "object": region.name,
        "bounds_mm": spec.region_bounds_mm,
        "excluded_y_min_face_id": y_min_face.id,
        "radiation_face_ids": [face.id for face in radiation_faces],
        "boundary": boundary.name,
    }


def create_coordinate_systems(app: Any, spec: Mimo2x2C0Spec) -> dict[str, str]:
    planes = cutplane_mapping(spec)
    for radiator, center in spec.radiator_centers_x_mm.items():
        require(
            app.modeler.create_coordinate_system(
                origin=[center, 0.0, 0.0],
                name=f"CS_{radiator}",
            ),
            f"falha ao criar CS_{radiator}",
        )
        cut_name = f"Cut_Q4_YZ_{radiator}"
        require(
            app.modeler.create_coordinate_system(
                origin=[center, 0.0, 0.0],
                name=cut_name,
            ),
            f"falha ao criar {cut_name}",
        )
    for pair, center in spec.pair_centers_x_mm.items():
        require(
            app.modeler.create_coordinate_system(
                origin=[center, spec.external_port_y_mm, 0.0],
                name=f"CS_WG_{pair}",
            ),
            f"falha ao criar CS_WG_{pair}",
        )
        cut_name = f"Cut_Q4_YZ_WG_{pair}"
        require(
            app.modeler.create_coordinate_system(
                origin=[center, 0.0, 0.0],
                name=cut_name,
            ),
            f"falha ao criar {cut_name}",
        )
    fixed_cuts = {
        "Cut_Q4_XY_MidHeight": (
            [0.0, 0.0, spec.source_air_z_min_mm + spec.wg_a_z_mm / 2.0],
            "XY",
            "EMag_XY_MidHeight_25p87",
        ),
        "Cut_Q4_XZ_ArrayCenter": (
            [0.0, 4.5, 0.0],
            "XZ",
            "EMag_XZ_ArrayCenter_25p87",
        ),
        "Cut_Q4_XZ_Feed": (
            [0.0, (spec.external_port_y_mm + spec.source_port_y_mm) / 2.0, 0.0],
            "XZ",
            "EMag_XZ_Feed_25p87",
        ),
    }
    for name, (origin, plane, plot_name) in fixed_cuts.items():
        require(
            app.modeler.create_coordinate_system(origin=origin, name=name),
            f"falha ao criar {name}",
        )
    return planes


def cutplane_mapping(spec: Mimo2x2C0Spec) -> dict[str, str]:
    planes = {
        f"EMag_YZ_{radiator}_25p87": f"Cut_Q4_YZ_{radiator}:YZ"
        for radiator in spec.radiator_centers_x_mm
    }
    planes.update(
        {
            f"EMag_YZ_WG_{pair}_25p87": f"Cut_Q4_YZ_WG_{pair}:YZ"
            for pair in spec.pair_centers_x_mm
        }
    )
    planes.update(
        {
            "EMag_XY_MidHeight_25p87": "Cut_Q4_XY_MidHeight:XY",
            "EMag_XZ_ArrayCenter_25p87": "Cut_Q4_XZ_ArrayCenter:XZ",
            "EMag_XZ_Feed_25p87": "Cut_Q4_XZ_Feed:XZ",
        }
    )
    return planes


def configure_mesh(
    app: Any,
    module_objects: Mapping[str, list[str]],
    feed_data: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    field_air = [
        name
        for names in module_objects.values()
        for name in names
        if name.startswith("Cavity_Air")
    ]
    field_air.extend(data["air"] for data in feed_data.values())
    mesh_air = require(
        app.mesh.assign_length_mesh(
            assignment=field_air,
            inside_selection=True,
            maximum_length=1.2,
            maximum_elements=1_000_000,
            name="Mesh_Q4_WG_Cavity_Air_1p2mm",
        ),
        "falha ao criar mesh dos canais",
    )
    fr4 = [
        name
        for names in module_objects.values()
        for name in names
        if name.startswith("FR4_Slab")
    ]
    mesh_fr4 = require(
        app.mesh.assign_length_mesh(
            assignment=fr4,
            inside_selection=True,
            maximum_length=0.35,
            maximum_elements=500_000,
            name="Mesh_Q4_FR4_0p35mm",
        ),
        "falha ao criar mesh dos slabs FR4",
    )
    return [mesh_air.name, mesh_fr4.name]


def configure_setup(app: Any, spec: Mimo2x2C0Spec) -> dict[str, Any]:
    setup = require(
        app.create_setup(SETUP_NAME, setup_type="HFSSDriven"),
        f"falha ao criar {SETUP_NAME}",
    )
    properties = {
        "Frequency": f"{spec.frequency_ghz}GHz",
        "MaxDeltaS": 0.02,
        "MaximumPasses": 12,
        "MinimumPasses": 2,
        "MinimumConvergedPasses": 2,
        "PercentRefinement": 20,
        "BasisOrder": 1,
        "SaveAnyFields": True,
        "SaveRadFieldsOnly": False,
    }
    for key, value in properties.items():
        setup.props[key] = value
    require(setup.update(), f"falha ao atualizar {SETUP_NAME}")
    sweep = require(
        app.create_linear_count_sweep(
            setup=SETUP_NAME,
            unit="GHz",
            start_frequency=spec.sweep_start_ghz,
            stop_frequency=spec.sweep_stop_ghz,
            num_of_freq_points=81,
            name=SWEEP_NAME,
            save_fields=False,
            save_rad_fields=False,
            sweep_type="Interpolating",
            interpolation_tol=0.5,
            interpolation_max_solutions=250,
        ),
        f"falha ao criar {SWEEP_NAME}",
    )
    sphere = require(
        app.insert_infinite_sphere(
            phi_start=0,
            phi_stop=360,
            phi_step=2,
            theta_start=0,
            theta_stop=180,
            theta_step=2,
            name=SPHERE_NAME,
        ),
        f"falha ao criar {SPHERE_NAME}",
    )
    return {
        "setup": setup.name,
        "properties": properties,
        "sweep": sweep.name,
        "sphere": sphere.name,
    }


def create_s_report(app: Any) -> str:
    report_name = "S_Q4_2Port_25_27GHz"
    report = require(
        app.post.create_report(
            expressions=[
                "dB(S(P1_WG_A,P1_WG_A))",
                "dB(S(P1_WG_A,P2_WG_B))",
                "dB(S(P2_WG_B,P1_WG_A))",
                "dB(S(P2_WG_B,P2_WG_B))",
            ],
            setup_sweep_name=f"{SETUP_NAME} : {SWEEP_NAME}",
            domain="Sweep",
            primary_sweep_variable="Freq",
            report_category="Modal Solution Data",
            plot_type="Rectangular Plot",
            plot_name=report_name,
        ),
        "falha ao criar report de S-parâmetros",
    )
    return report.plot_name


def design_inventory(app: Any) -> dict[str, Any]:
    objects = []
    for name in sorted(app.modeler.object_names):
        obj = app.modeler[name]
        objects.append(
            {
                "name": name,
                "id": obj.id,
                "type": obj.object_type,
                "material": obj.material_name,
                "bounding_box_mm": list(obj.bounding_box),
            }
        )
    return {
        "objects": objects,
        "object_count": len(objects),
        "solid_count": len(app.modeler.solid_names),
        "sheet_count": len(app.modeler.sheet_names),
        "boundaries": [
            {"name": boundary.name, "type": boundary.type}
            for boundary in app.boundaries
        ],
        "excitations": list(app.excitation_names),
        "setups": list(app.setup_names),
        "sweeps": list(app.existing_analysis_sweeps),
        "mesh_operations": [operation.name for operation in app.mesh.meshoperations],
        "coordinate_systems": [
            coordinate_system.name
            for coordinate_system in app.modeler.coordinate_systems
        ],
    }


def attach(project: Path, grpc_port: int, pid: int | None) -> tuple[Any, dict[str, Any]]:
    runtime = AedtRuntimeSpec(
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        port=grpc_port,
        process_id=pid,
    )
    preflight = preflight_aedt(runtime)
    from ansys.aedt.core import Hfss

    app = Hfss(
        project=str(project),
        version=runtime.version,
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        port=grpc_port,
        aedt_process_id=pid,
        remove_lock=False,
    )
    runtime_data = {
        **capturar_runtime_app(app, runtime),
        "pyaedt": preflight.pyaedt_version,
        "license": preflight.license_status,
        "transport": "native AEDT gRPC via PyAEDT",
        "cores": 14,
        "tasks": 1,
        "gpus": 0,
    }
    return app, runtime_data


def build(
    source: Path,
    target: Path,
    artifact_dir: Path,
    grpc_port: int,
    pid: int | None,
) -> dict[str, Any]:
    spec = Mimo2x2C0Spec()
    source_hash_before = sha256(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    app: Any | None = None
    result: dict[str, Any] = {
        "schema": "enz-eigenchannel-mimo/q4-c0-build/v1",
        "classification": "HIPÓTESE",
        "status": "BUILDING",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "source": {
            "path": str(source.relative_to(ROOT)),
            "sha256_before": source_hash_before,
            "promoted_as_validated": False,
        },
        "specification": spec.to_manifest(),
        "gates": {
            "source_radiator_validation": "FAIL",
            "build_geometry": "PENDING",
            "validate_design": "PENDING",
            "adaptive_convergence": "PENDING",
            "strict_passivity": "PENDING",
            "mimo_claim": "BLOCKED_SOURCE_MODEL_HIPOTESE",
        },
        "errors": [],
    }
    manifest_path = artifact_dir / "build_manifest.json"
    write_json(manifest_path, result)
    try:
        if target.exists():
            raise FileExistsError(
                f"o alvo versionado já existe e não será substituído: {target}"
            )
        app, runtime = attach(source, grpc_port, pid)
        result["runtime"] = runtime
        result["source"]["project_name"] = app.project_name
        result["source"]["design_name"] = app.design_name
        require(
            app.save_project(target, overwrite=False, refresh_ids=True),
            f"falha ao salvar cópia versionada {target}",
        )
        require(app.rename_design(DESIGN_NAME, save=False), "falha ao renomear design")
        clean_previous_configuration(app)

        for name, expression in {
            "q4_frequency": f"{spec.frequency_ghz}GHz",
            "q4_wg_a_z": f"{spec.wg_a_z_mm}mm",
            "q4_wg_b_x": f"{spec.wg_b_x_mm}mm",
            "q4_pair_spacing": f"{spec.pair_spacing_mm}mm",
            "q4_interpair_spacing": f"{spec.interpair_spacing_mm}mm",
            "q4_lambda_g": f"{spec.lambda_g_mm}mm",
            "q4_branch_length": f"{spec.branch_length_mm}mm",
            "q4_junction_length": f"{spec.junction_length_mm}mm",
            "q4_input_length": f"{spec.input_length_mm}mm",
            "q4_external_port_y": f"{spec.external_port_y_mm}mm",
        }.items():
            app[name] = expression

        module_objects = duplicate_radiators(app, spec)
        feed_data = {
            "WG_A": build_feed(app, spec, "A", "P1_WG_A"),
            "WG_B": build_feed(app, spec, "B", "P2_WG_B"),
        }
        region = build_region(app, spec)
        cutplanes = create_coordinate_systems(app, spec)
        mesh_operations = configure_mesh(app, module_objects, feed_data)
        setup = configure_setup(app, spec)
        s_report = create_s_report(app)
        require(app.save_project(target), "falha ao salvar antes de ValidateDesign")

        validation_log = artifact_dir / "logs" / "validation_build.log"
        validation_log.parent.mkdir(parents=True, exist_ok=True)
        validation_result = app.validate_simple(validation_log)
        result["gates"]["validate_design"] = (
            "PASS" if validation_result == 1 else "FAIL"
        )
        if validation_result != 1:
            raise RuntimeError(f"ValidateDesign falhou; consulte {validation_log}")

        preview = artifact_dir / "plots" / "design_build.jpg"
        preview.parent.mkdir(parents=True, exist_ok=True)
        require(
            app.export_design_preview_to_jpg(preview),
            "falha ao exportar preview do build",
        )
        require(app.save_project(target), "falha ao salvar projeto construído")
        result.update(
            {
                "status": "BUILT",
                "completed_at_utc": datetime.now(UTC).isoformat(),
                "target": {
                    "path": str(target.relative_to(ROOT)),
                    "bytes": target.stat().st_size,
                    "sha256": sha256(target),
                    "project_name": app.project_name,
                    "design_name": app.design_name,
                    "solution_type": app.solution_type,
                },
                "geometry": {
                    "modules": module_objects,
                    "feeds": feed_data,
                    "region": region,
                    "cutplanes": cutplanes,
                    "mesh_operations": mesh_operations,
                },
                "setup": setup,
                "reports": [s_report],
                "inventory": design_inventory(app),
                "artifacts": {
                    "validation_log": str(validation_log.relative_to(ROOT)),
                    "preview": str(preview.relative_to(ROOT)),
                },
            }
        )
        result["gates"]["build_geometry"] = "PASS"
        result["source"]["sha256_after"] = sha256(source)
        result["source"]["unchanged"] = (
            result["source"]["sha256_before"]
            == result["source"]["sha256_after"]
        )
        if not result["source"]["unchanged"]:
            raise RuntimeError("o projeto fonte foi modificado durante SaveAs/build")
        write_json(manifest_path, result)
        return result
    except BaseException:
        result["status"] = "FAILED"
        result["completed_at_utc"] = datetime.now(UTC).isoformat()
        result["errors"].append(traceback.format_exc())
        write_json(manifest_path, result)
        raise
    finally:
        if app is not None:
            app.release_desktop(close_projects=False, close_desktop=False)


def expected_geometry(spec: Mimo2x2C0Spec) -> dict[str, Any]:
    modules = {
        radiator: [f"{base}_{radiator}" for base in BASE_OBJECTS]
        for radiator in spec.radiator_centers_x_mm
    }
    feeds: dict[str, Any] = {}
    for pair, port_name in (("A", "P1_WG_A"), ("B", "P2_WG_B")):
        pair_center = spec.pair_centers_x_mm[pair]
        feeds[f"WG_{pair}"] = {
            "housing": f"WG_{pair}_Housing_PEC",
            "air": f"WG_{pair}_Air",
            "sheet": f"{port_name}_Sheet",
            "boundary": port_name,
            "integration_line_mm": [
                [
                    pair_center,
                    spec.external_port_y_mm,
                    spec.source_air_z_min_mm,
                ],
                [
                    pair_center,
                    spec.external_port_y_mm,
                    spec.source_air_z_min_mm + spec.wg_a_z_mm,
                ],
            ],
            "pair_center_x_mm": pair_center,
        }
    return {
        "modules": modules,
        "feeds": feeds,
        "region": {
            "object": "Open_Region_Q4",
            "bounds_mm": spec.region_bounds_mm,
            "boundary": "Radiation_Q4_5Faces",
        },
        "cutplanes": cutplane_mapping(spec),
        "mesh_operations": [
            "Mesh_Q4_WG_Cavity_Air_1p2mm",
            "Mesh_Q4_FR4_0p35mm",
        ],
    }


def repair_build(
    source: Path,
    target: Path,
    artifact_dir: Path,
    grpc_port: int,
    pid: int | None,
) -> dict[str, Any]:
    spec = Mimo2x2C0Spec()
    manifest_path = artifact_dir / "build_manifest.json"
    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    if result["status"] != "FAILED":
        raise RuntimeError("repair-build exige build_manifest com status FAILED")
    app: Any | None = None
    try:
        app, runtime = attach(target, grpc_port, pid)
        result["runtime"] = runtime
        deleted_parametrics = []
        for setup in list(app.parametrics.setups):
            require(
                app.parametrics.delete(setup.name),
                f"falha ao excluir estudo paramétrico órfão {setup.name}",
            )
            deleted_parametrics.append(setup.name)
        remaining_parametrics = [setup.name for setup in app.parametrics.setups]
        if remaining_parametrics:
            raise RuntimeError(
                f"estudos paramétricos órfãos restantes: {remaining_parametrics}"
            )
        validation_log = artifact_dir / "logs" / "validation_build_repair.log"
        validation_result = app.validate_simple(validation_log)
        result["gates"]["validate_design"] = (
            "PASS" if validation_result == 1 else "FAIL"
        )
        if validation_result != 1:
            raise RuntimeError(
                f"ValidateDesign ainda falhou; consulte {validation_log}"
            )
        expected_excitations = {"P1_WG_A:1", "P2_WG_B:1"}
        if set(app.excitation_names) != expected_excitations:
            raise RuntimeError(
                f"excitações {app.excitation_names}; esperado {expected_excitations}"
            )
        if SETUP_NAME not in app.setup_names:
            raise RuntimeError(f"setup obrigatório ausente: {SETUP_NAME}")
        preview = artifact_dir / "plots" / "design_build.jpg"
        preview.parent.mkdir(parents=True, exist_ok=True)
        require(
            app.export_design_preview_to_jpg(preview),
            "falha ao exportar preview reparado",
        )
        require(app.save_project(target), "falha ao salvar build reparado")
        historical_errors = list(result.get("errors", []))
        result.update(
            {
                "status": "BUILT",
                "completed_at_utc": datetime.now(UTC).isoformat(),
                "target": {
                    "path": str(target.relative_to(ROOT)),
                    "bytes": target.stat().st_size,
                    "sha256": sha256(target),
                    "project_name": app.project_name,
                    "design_name": app.design_name,
                    "solution_type": app.solution_type,
                },
                "geometry": expected_geometry(spec),
                "setup": {
                    "setup": SETUP_NAME,
                    "properties": jsonable(app.get_setup(SETUP_NAME).props),
                    "sweep": SWEEP_NAME,
                    "sphere": SPHERE_NAME,
                },
                "reports": list(app.post.all_report_names),
                "inventory": design_inventory(app),
                "artifacts": {
                    "validation_log": str(validation_log.relative_to(ROOT)),
                    "preview": str(preview.relative_to(ROOT)),
                },
                "repair": {
                    "cause": "optimetrics órfãos da v7 após remoção do setup fonte",
                    "deleted_parametrics": deleted_parametrics,
                },
                "historical_errors": historical_errors,
                "errors": [],
            }
        )
        result["gates"]["build_geometry"] = "PASS"
        result["source"]["sha256_after"] = sha256(source)
        result["source"]["unchanged"] = (
            result["source"]["sha256_before"]
            == result["source"]["sha256_after"]
        )
        if not result["source"]["unchanged"]:
            raise RuntimeError("o projeto fonte foi modificado durante repair-build")
        write_json(manifest_path, result)
        return result
    except BaseException:
        result["status"] = "FAILED"
        result["completed_at_utc"] = datetime.now(UTC).isoformat()
        result.setdefault("errors", []).append(traceback.format_exc())
        write_json(manifest_path, result)
        raise
    finally:
        if app is not None:
            app.release_desktop(close_projects=False, close_desktop=False)


def capture_call(
    errors: list[dict[str, str]],
    label: str,
    function: Callable[[], Any],
) -> Any:
    try:
        return function()
    except Exception as exc:  # noqa: BLE001 -- falha externa é registrada
        errors.append(
            {
                "operation": label,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        return None


def create_postprocessing(
    app: Any,
    artifact_dir: Path,
    cutplanes: Mapping[str, str],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    fields_dir = artifact_dir / "fields"
    reports_dir = artifact_dir / "plots"
    fields_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    created_plots: list[str] = []
    exported_fields: list[str] = []
    for plot_name, cutplane in cutplanes.items():
        plot = capture_call(
            errors,
            f"create_fieldplot:{plot_name}",
            lambda plot_name=plot_name, cutplane=cutplane: (
                app.post.create_fieldplot_cutplane(
                    [cutplane],
                    "Mag_E",
                    setup=f"{SETUP_NAME} : LastAdaptive",
                    intrinsics={"Freq": "25.87GHz", "Phase": "0deg"},
                    plot_name=plot_name,
                )
            ),
        )
        if not plot:
            continue
        created_plots.append(plot_name)
        jpg = fields_dir / f"{plot_name}.jpg"
        exported = capture_call(
            errors,
            f"export_field_jpg:{plot_name}",
            lambda plot=plot, jpg=jpg, plot_name=plot_name: app.post.export_field_jpg(
                str(jpg),
                plot_name,
                plot.plot_folder,
                orientation="isometric",
                width=1600,
                height=1000,
                display_wireframe=True,
                show_region="Default",
            ),
        )
        if exported and jpg.is_file():
            exported_fields.append(str(jpg.relative_to(ROOT)))

    farfield_reports = {
        "Q4_EPlane_RealizedGain_25p87": {
            "primary": "Theta",
            "variations": {
                "Freq": ["25.87GHz"],
                "Phi": ["0deg"],
                "Theta": ["All"],
            },
        },
        "Q4_HPlane_RealizedGain_25p87": {
            "primary": "Theta",
            "variations": {
                "Freq": ["25.87GHz"],
                "Phi": ["90deg"],
                "Theta": ["All"],
            },
        },
        "Q4_Gain3D_25p87": {
            "primary": "Phi",
            "secondary": "Theta",
            "variations": {
                "Freq": ["25.87GHz"],
                "Phi": ["All"],
                "Theta": ["All"],
            },
        },
    }
    created_reports: list[str] = []
    exported_reports: list[str] = []
    for name, definition in farfield_reports.items():
        report = capture_call(
            errors,
            f"create_report:{name}",
            lambda name=name, definition=definition: app.post.create_report(
                expressions=["dB(RealizedGainTheta)", "dB(RealizedGainPhi)"],
                setup_sweep_name=f"{SETUP_NAME} : LastAdaptive",
                domain="Sweep",
                variations=definition["variations"],
                primary_sweep_variable=definition["primary"],
                secondary_sweep_variable=definition.get("secondary"),
                report_category="Far Fields",
                plot_type=(
                    "3D Polar Plot"
                    if definition.get("secondary")
                    else "Radiation Pattern"
                ),
                context=SPHERE_NAME,
                plot_name=name,
            ),
        )
        if not report:
            continue
        created_reports.append(name)
        jpg = reports_dir / f"{name}.jpg"
        csv = reports_dir / f"{name}.csv"
        jpg_ok = capture_call(
            errors,
            f"export_report_jpg:{name}",
            lambda name=name: app.post.export_report_to_jpg(
                str(reports_dir), name, width=1600, height=1000
            ),
        )
        csv_result = capture_call(
            errors,
            f"export_report_csv:{name}",
            lambda name=name: app.post.export_report_to_csv(
                str(reports_dir), name
            ),
        )
        if jpg_ok and jpg.is_file():
            exported_reports.append(str(jpg.relative_to(ROOT)))
        csv_path = Path(csv_result) if isinstance(csv_result, str) else csv
        if csv_path.is_file():
            exported_reports.append(str(csv_path.relative_to(ROOT)))
    return {
        "field_plots_created": created_plots,
        "field_artifacts": exported_fields,
        "farfield_reports_created": created_reports,
        "report_artifacts": exported_reports,
        "errors": errors,
    }


def sparameter_validation(touchstone: Path, frequency_ghz: float) -> dict[str, Any]:
    frequencies, matrices = ler_touchstone_s2p(touchstone)
    target_hz = frequency_ghz * 1e9
    index = int(np.argmin(np.abs(frequencies - target_hz)))
    matrix = matrices[index]
    floor = np.finfo(float).tiny

    def db(value: complex) -> float:
        return float(20.0 * np.log10(max(abs(value), floor)))

    singular_values = np.linalg.svd(matrices, compute_uv=False)
    max_singular = float(np.max(singular_values))
    excitation = np.asarray([1 / math.sqrt(2), 1 / math.sqrt(2)], dtype=complex)
    active = matrix @ excitation / excitation
    tarc_value = tarc(matrix, excitation)
    accepted = potencia_aceita(matrix, excitation)
    s11_db = db(matrix[0, 0])
    s22_db = db(matrix[1, 1])
    s12_db = db(matrix[0, 1])
    s21_db = db(matrix[1, 0])
    return {
        "frequency_hz": float(frequencies[index]),
        "samples": int(frequencies.size),
        "s_matrix": jsonable(matrix),
        "s11_db": s11_db,
        "s22_db": s22_db,
        "s12_db": s12_db,
        "s21_db": s21_db,
        "active_reflection": jsonable(active),
        "active_reflection_db": [db(value) for value in active],
        "tarc_linear": tarc_value,
        "tarc_db": db(tarc_value),
        "accepted_power_normalized_w": accepted,
        "maximum_singular_value_over_sweep": max_singular,
        "reciprocity_error_at_f0": float(abs(matrix[0, 1] - matrix[1, 0])),
        "gates": {
            "s11_below_minus10_db": s11_db < -10.0,
            "s22_below_minus10_db": s22_db < -10.0,
            "isolation_below_minus15_db": max(s12_db, s21_db) < -15.0,
            "strict_passivity_1pct": max_singular <= 1.01,
            "reciprocity_1e_minus3": abs(matrix[0, 1] - matrix[1, 0]) <= 1e-3,
        },
    }


def convergence_declared(text: str) -> bool:
    """Reconhece a declaração de convergência exportada pelo AEDT."""

    return bool(
        re.search(r"^\s*Converged\s*:\s*Yes\s*$", text, re.IGNORECASE | re.MULTILINE)
    )


def power_metadata(xml_path: Path) -> dict[str, Any]:
    """Extrai potências por fonte do XML de metadados de antena."""

    root = ET.parse(xml_path).getroot()
    sources: dict[str, Any] = {}
    for source in root.findall("./ElementPatterns/Source"):
        name = source.attrib["name"]
        power = source.find("./PowerInfo/Power")
        if power is None:
            continue
        values = {
            "frequency_hz": float(power.attrib["Freq"]),
            "incident_w": float(power.findtext("IncidentPower", "nan")),
            "accepted_w": float(power.findtext("AcceptedPower", "nan")),
            "radiated_w": float(power.findtext("RadiatedPower", "nan")),
        }
        values["power_balance_relative_error"] = (
            abs(values["radiated_w"] - values["accepted_w"])
            / values["accepted_w"]
        )
        values["power_balance_within_1pct"] = (
            values["power_balance_relative_error"] <= 0.01
        )
        sources[name] = values
    return sources


def realized_gain_peak(csv_path: Path) -> dict[str, float]:
    """Calcula o pico do ganho realizado total a partir das componentes."""

    best: dict[str, float] | None = None
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            gain_theta = float(row["dB(RealizedGainTheta)"])
            gain_phi = float(row["dB(RealizedGainPhi)"])
            total = 10.0 * math.log10(
                10.0 ** (gain_theta / 10.0) + 10.0 ** (gain_phi / 10.0)
            )
            if best is None or total > best["realized_gain_total_db"]:
                best = {
                    "realized_gain_total_db": total,
                    "phi_deg": float(row["Phi[deg]"]),
                    "theta_deg": float(row["Theta[deg]"]),
                    "realized_gain_theta_db": gain_theta,
                    "realized_gain_phi_db": gain_phi,
                }
    if best is None:
        raise ValueError(f"CSV de ganho vazio: {csv_path}")
    return best


def revalidate_artifacts(artifact_dir: Path) -> dict[str, Any]:
    """Recalcula gates e métricas somente a partir dos artefatos exportados."""

    validation_path = artifact_dir / "validation.json"
    result = json.loads(validation_path.read_text(encoding="utf-8"))
    convergence = artifact_dir / "metrics" / "convergence.csv"
    converged = convergence_declared(
        convergence.read_text(encoding="utf-8", errors="replace")
    )
    result["gates"]["adaptive_convergence"] = "PASS" if converged else "FAIL"

    sweep_path = artifact_dir / "network" / "system.s2p"
    exact_paths = sorted((artifact_dir / "farfield").rglob("LastAdaptive*.s2p"))
    if len(exact_paths) != 1:
        raise RuntimeError(
            f"esperado um Touchstone LastAdaptive; encontrados {len(exact_paths)}"
        )
    sweep = sparameter_validation(sweep_path, 25.87)
    exact = sparameter_validation(exact_paths[0], 25.87)
    result["sparameters"] = {
        "at_exact_f0": exact,
        "sweep_25_27_ghz": sweep,
        "note": (
            "Métricas em f0 usam LastAdaptive em 25,87 GHz; "
            "passividade de banda usa a varredura de 81 pontos."
        ),
    }
    result["gates"]["strict_passivity"] = (
        "PASS" if sweep["gates"]["strict_passivity_1pct"] else "FAIL"
    )
    result["gates"]["s11"] = (
        "PASS" if exact["gates"]["s11_below_minus10_db"] else "FAIL"
    )
    result["gates"]["s22"] = (
        "PASS" if exact["gates"]["s22_below_minus10_db"] else "FAIL"
    )
    result["gates"]["isolation"] = (
        "PASS" if exact["gates"]["isolation_below_minus15_db"] else "FAIL"
    )
    result["gates"]["reciprocity"] = (
        "PASS" if exact["gates"]["reciprocity_1e_minus3"] else "FAIL"
    )

    xml_paths = sorted((artifact_dir / "farfield").glob("*.xml"))
    if len(xml_paths) != 1:
        raise RuntimeError(f"esperado um XML de antena; encontrados {len(xml_paths)}")
    result["power"] = power_metadata(xml_paths[0])
    result["gates"]["power_balance"] = (
        "PASS"
        if result["power"]
        and all(item["power_balance_within_1pct"] for item in result["power"].values())
        else "FAIL"
    )

    ffd_paths = sorted((artifact_dir / "farfield").rglob("exportfield_*.ffd"))
    if len(ffd_paths) != 2:
        raise RuntimeError(f"esperados dois FFD; encontrados {len(ffd_paths)}")
    theta_1, phi_1, field_1 = ler_ffd_complexo(ffd_paths[0])
    theta_2, phi_2, field_2 = ler_ffd_complexo(ffd_paths[1])
    if not np.array_equal(theta_1, theta_2) or not np.array_equal(phi_1, phi_2):
        raise RuntimeError("grades angulares dos padrões embarcados são distintas")
    result["mimo_diagnostics"] = {
        "field_ecc_complex": ecc_campos_complexos(
            theta_1, phi_1, field_1, field_2
        ),
        "theta_samples": int(theta_1.size),
        "phi_samples_including_duplicate_360deg": int(phi_1.size),
        "formula": (
            "rho_e=|integral(E1 dot conj(E2))dOmega|^2/"
            "(integral(|E1|^2)dOmega integral(|E2|^2)dOmega)"
        ),
        "classification": "SIMULADO",
        "claim_limit": (
            "ECC isolada não valida diversidade, rank, capacidade ou throughput; "
            "o radiador fonte permanece HIPÓTESE e está severamente descasado."
        ),
    }
    result["farfield_metrics"] = realized_gain_peak(
        artifact_dir / "plots" / "Q4_Gain3D_25p87.csv"
    )
    result["revalidated_at_utc"] = datetime.now(UTC).isoformat()
    result["revalidation_method"] = "artifact-only; no AEDT re-solve"
    write_json(validation_path, result)
    return result


def solve(
    target: Path,
    artifact_dir: Path,
    grpc_port: int,
    pid: int | None,
) -> dict[str, Any]:
    build_manifest_path = artifact_dir / "build_manifest.json"
    build_manifest = json.loads(build_manifest_path.read_text(encoding="utf-8"))
    if build_manifest["status"] != "BUILT":
        raise RuntimeError("solve exige build_manifest com status BUILT")
    app: Any | None = None
    result: dict[str, Any] = {
        "schema": "enz-eigenchannel-mimo/q4-c0-validation/v1",
        "classification": "SIMULADO",
        "model_classification": "HIPÓTESE",
        "status": "SOLVING",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "target": {
            "path": str(target.relative_to(ROOT)),
            "sha256_before_solve": sha256(target),
        },
        "runtime_requested": {"cores": 14, "tasks": 1, "gpus": 0},
        "gates": {
            "source_radiator_validation": "FAIL",
            "validate_design": "PENDING",
            "adaptive_convergence": "PENDING",
            "strict_passivity": "PENDING",
            "s11": "PENDING",
            "s22": "PENDING",
            "isolation": "PENDING",
            "complex_embedded_patterns": "PENDING",
            "mimo_claim": "BLOCKED_SOURCE_MODEL_HIPOTESE",
        },
        "errors": [],
    }
    validation_path = artifact_dir / "validation.json"
    write_json(validation_path, result)
    try:
        app, runtime = attach(target, grpc_port, pid)
        result["runtime"] = runtime
        if app.design_name != DESIGN_NAME:
            raise RuntimeError(
                f"design ativo {app.design_name!r}; esperado {DESIGN_NAME!r}"
            )
        validation_log = artifact_dir / "logs" / "validation_pre_solve.log"
        validation_log.parent.mkdir(parents=True, exist_ok=True)
        validation_result = app.validate_simple(validation_log)
        result["gates"]["validate_design"] = (
            "PASS" if validation_result == 1 else "FAIL"
        )
        if validation_result != 1:
            raise RuntimeError(f"ValidateDesign falhou; consulte {validation_log}")
        require(
            app.save_project(target),
            "falha ao salvar imediatamente antes do solve",
        )
        solved = app.analyze_setup(
            SETUP_NAME,
            cores=14,
            tasks=1,
            gpus=0,
            use_auto_settings=False,
            blocking=True,
        )
        require(solved, f"solve falhou em {SETUP_NAME}")

        require(
            app.edit_sources(
                {
                    "P1_WG_A:1": ("0.5W", "0deg"),
                    "P2_WG_B:1": ("0.5W", "0deg"),
                },
                include_port_post_processing=True,
            ),
            "falha ao aplicar estado C0 EVEN/EVEN normalizado para 1 W total",
        )
        metrics_dir = artifact_dir / "metrics"
        network_dir = artifact_dir / "network"
        farfield_dir = artifact_dir / "farfield"
        for directory in (metrics_dir, network_dir, farfield_dir):
            directory.mkdir(parents=True, exist_ok=True)
        convergence = metrics_dir / "convergence.csv"
        mesh_stats = metrics_dir / "mesh_stats.csv"
        profile = metrics_dir / "solver_profile.csv"
        require(
            app.export_convergence(SETUP_NAME, output_file=str(convergence)),
            "falha ao exportar convergência",
        )
        require(
            app.export_mesh_stats(SETUP_NAME, output_file=str(mesh_stats)),
            "falha ao exportar estatísticas de malha",
        )
        profile_result = app.export_profile(SETUP_NAME, output_file=str(profile))
        if not profile_result:
            result["errors"].append(
                {
                    "operation": "export_profile",
                    "error": "AEDT não exportou solver profile",
                }
            )
        convergence_text = convergence.read_text(
            encoding="utf-8", errors="replace"
        )
        converged = convergence_declared(convergence_text)
        result["gates"]["adaptive_convergence"] = "PASS" if converged else "FAIL"

        touchstone = network_dir / "system.s2p"
        exported_touchstone = app.export_touchstone(
            setup=SETUP_NAME,
            sweep=SWEEP_NAME,
            output_file=str(touchstone),
            renormalization=True,
            impedance=50,
            gamma_impedance_comments=True,
        )
        require(exported_touchstone, "falha ao exportar system.s2p")
        if isinstance(exported_touchstone, str):
            touchstone = Path(exported_touchstone)
        s_validation = sparameter_validation(touchstone, 25.87)
        result["sparameters"] = s_validation
        result["gates"]["strict_passivity"] = (
            "PASS"
            if s_validation["gates"]["strict_passivity_1pct"]
            else "FAIL"
        )
        result["gates"]["s11"] = (
            "PASS" if s_validation["gates"]["s11_below_minus10_db"] else "FAIL"
        )
        result["gates"]["s22"] = (
            "PASS" if s_validation["gates"]["s22_below_minus10_db"] else "FAIL"
        )
        result["gates"]["isolation"] = (
            "PASS"
            if s_validation["gates"]["isolation_below_minus15_db"]
            else "FAIL"
        )

        farfield_ok = app.export_antenna_metadata(
            frequencies=[25.87e9],
            setup=f"{SETUP_NAME} : LastAdaptive",
            sphere=SPHERE_NAME,
            variations={},
            output_dir=str(farfield_dir),
            export_element_pattern=True,
            export_objects=False,
            export_touchstone=True,
            export_power=True,
        )
        complex_patterns = [
            path
            for path in farfield_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".ffd", ".txt", ".json"}
        ]
        result["gates"]["complex_embedded_patterns"] = (
            "PASS" if farfield_ok and complex_patterns else "FAIL"
        )

        cutplanes = build_manifest["geometry"]["cutplanes"]
        post = create_postprocessing(app, artifact_dir, cutplanes)
        result["postprocessing"] = post
        result["errors"].extend(post["errors"])
        s_report_dir = artifact_dir / "plots"
        s_report_dir.mkdir(parents=True, exist_ok=True)
        s_report_jpg = app.post.export_report_to_jpg(
            str(s_report_dir),
            "S_Q4_2Port_25_27GHz",
            width=1600,
            height=1000,
        )
        s_report_csv = app.post.export_report_to_csv(
            str(s_report_dir), "S_Q4_2Port_25_27GHz"
        )
        result["postprocessing"]["s_report"] = {
            "jpg_exported": bool(s_report_jpg),
            "csv": str(Path(s_report_csv).relative_to(ROOT))
            if s_report_csv
            else None,
        }

        preview = artifact_dir / "plots" / "design_solved.jpg"
        require(
            app.export_design_preview_to_jpg(preview),
            "falha ao exportar preview solucionado",
        )
        require(app.save_project(target), "falha ao salvar projeto solucionado")
        result.update(
            {
                "status": "COMPLETED_WITH_SCIENTIFIC_BLOCK",
                "completed_at_utc": datetime.now(UTC).isoformat(),
                "target": {
                    **result["target"],
                    "bytes_after_solve": target.stat().st_size,
                    "sha256_after_solve": sha256(target),
                },
                "artifacts": {
                    "convergence": str(convergence.relative_to(ROOT)),
                    "mesh_stats": str(mesh_stats.relative_to(ROOT)),
                    "solver_profile": str(profile.relative_to(ROOT))
                    if profile.is_file()
                    else None,
                    "touchstone": str(touchstone.relative_to(ROOT)),
                    "farfield": [
                        str(path.relative_to(ROOT))
                        for path in farfield_dir.rglob("*")
                        if path.is_file()
                    ],
                    "preview": str(preview.relative_to(ROOT)),
                    "validation_log": str(validation_log.relative_to(ROOT)),
                },
                "inventory_after_solve": design_inventory(app),
            }
        )
        write_json(validation_path, result)
        return result
    except BaseException:
        result["status"] = "FAILED"
        result["completed_at_utc"] = datetime.now(UTC).isoformat()
        result["errors"].append(traceback.format_exc())
        write_json(validation_path, result)
        raise
    finally:
        if app is not None:
            app.release_desktop(close_projects=False, close_desktop=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("build", "repair-build", "solve", "revalidate")
    )
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--target", type=Path, default=TARGET_DEFAULT)
    parser.add_argument("--artifacts", type=Path, default=ARTIFACT_DEFAULT)
    parser.add_argument("--grpc-port", type=int)
    parser.add_argument("--pid", type=int)
    args = parser.parse_args()

    source = args.source.resolve()
    target = args.target.resolve()
    artifacts = args.artifacts.resolve()
    if args.command != "revalidate" and args.grpc_port is None:
        parser.error("--grpc-port é obrigatório para build, repair-build e solve")
    if args.command == "build":
        result = build(source, target, artifacts, args.grpc_port, args.pid)
    elif args.command == "repair-build":
        result = repair_build(
            source, target, artifacts, args.grpc_port, args.pid
        )
    elif args.command == "solve":
        result = solve(target, artifacts, args.grpc_port, args.pid)
    else:
        result = revalidate_artifacts(artifacts)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": result["classification"],
                "gates": result["gates"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
