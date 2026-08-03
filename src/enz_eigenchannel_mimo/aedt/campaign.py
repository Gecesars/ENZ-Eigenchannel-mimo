"""Orquestração build/validate/solve/export da campanha G0."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import platform
import sys
import time
from typing import Any

from enz_eigenchannel_mimo.geometry import G0GeometrySpec, build_geometry_plan

from .artifacts import RunArtifactStore
from .builder import AedtGeometryBuilder
from .runtime import AedtRuntimeSpec
from .session import Aedt2024R2Session
from .validation import preflight_offline, validate_live_design


@dataclass(frozen=True, slots=True)
class CampaignRequest:
    spec: G0GeometrySpec
    runtime: AedtRuntimeSpec
    output_root: str
    solve: bool = False
    scientific_run: bool = False
    project_name: str = "ENZ_G0_Validation.aedt"
    design_name: str = "HFSS_ENZ_G0"


@dataclass(frozen=True, slots=True)
class CampaignResult:
    run_id: str
    run_directory: str
    project_path: str
    solved: bool
    elapsed_s: float
    manifest_path: str


class G0CampaignRunner:
    def run(self, request: CampaignRequest) -> CampaignResult:
        started = time.monotonic()
        plan = build_geometry_plan(request.spec)
        run_id = RunArtifactStore.timestamp_run_id(
            f"{request.spec.identificador}_{request.spec.variante.value}"
        )
        store = RunArtifactStore(request.output_root, run_id)
        project_path = store.path(request.project_name)
        offline = preflight_offline(
            request.spec,
            plan,
            project_path=project_path,
            scientific_run=request.scientific_run,
        )
        store.write_json("spec.json", request.spec.as_manifest())
        store.write_json("geometry_plan.json", plan.as_manifest())
        store.write_json("preflight_offline.json", offline.as_manifest())
        offline.require_ok()

        solution_type = "Eigenmode" if plan.solution_type == "Eigenmode" else "Modal"
        build_manifest: dict[str, Any] = {}
        live_manifest: dict[str, Any] = {}
        runtime_manifest: dict[str, Any] = request.runtime.as_manifest()
        solved = False

        with Aedt2024R2Session(request.runtime) as session:
            app = session.connect(
                project=project_path,
                design=request.design_name,
                solution_type=solution_type,
            )
            runtime_manifest = session.identity.as_manifest()
            builder = AedtGeometryBuilder(app)
            build = builder.build(plan, project_path=project_path, configure_analysis=True)
            build_manifest = build.as_manifest()
            live = validate_live_design(app, plan)
            live_manifest = live.as_manifest()
            store.write_json("validation_live.json", live_manifest)
            live.require_ok()

            if request.solve:
                setup_name = build.setup_names[0]
                result = app.analyze_setup(setup_name)
                if result is False:
                    raise RuntimeError(f"solve HFSS falhou em {setup_name}")
                solved = True
                session.save(project_path)

        elapsed = time.monotonic() - started
        manifest = {
            "schema": "enz-eigenchannel-mimo/aedt-run/v1",
            "run_id": run_id,
            "scientific_run": request.scientific_run,
            "solve_requested": request.solve,
            "solved": solved,
            "runtime": runtime_manifest,
            "host": {
                "platform": platform.platform(),
                "python": sys.version,
            },
            "spec": request.spec.as_manifest(),
            "plan": plan.as_manifest(),
            "build": build_manifest,
            "preflight_offline": offline.as_manifest(),
            "validation_live": live_manifest,
            "elapsed_s": elapsed,
        }
        manifest_path = store.finalize(manifest)
        return CampaignResult(
            run_id=run_id,
            run_directory=str(store.root),
            project_path=str(project_path),
            solved=solved,
            elapsed_s=elapsed,
            manifest_path=str(manifest_path),
        )
