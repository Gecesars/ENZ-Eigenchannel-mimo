"""Extração defensiva de rede, campos e evidências do HFSS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True, slots=True)
class NetworkTrace:
    expression: str
    frequencies_ghz: tuple[float, ...]
    real: tuple[float, ...]
    imag: tuple[float, ...]

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FarFieldGrid:
    frequency_ghz: float
    theta_deg: tuple[float, ...]
    phi_deg: tuple[float, ...]
    e_theta_real: tuple[tuple[float, ...], ...]
    e_theta_imag: tuple[tuple[float, ...], ...]
    e_phi_real: tuple[tuple[float, ...], ...]
    e_phi_imag: tuple[tuple[float, ...], ...]

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)


class HfssPostProcessor:
    def __init__(self, app: Any) -> None:
        self.app = app

    def export_touchstone(
        self,
        *,
        setup_name: str,
        sweep_name: str,
        output_file: str | Path,
    ) -> Path:
        target = Path(output_file).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        attempts = (
            lambda: self.app.export_touchstone(
                solution_name=setup_name,
                sweep_name=sweep_name,
                file_name=str(target),
            ),
            lambda: self.app.export_touchstone(
                setup_name,
                sweep_name,
                str(target),
            ),
            lambda: self.app.export_touchstone(
                solution_name=f"{setup_name} : {sweep_name}",
                file_name=str(target),
            ),
        )
        errors: list[str] = []
        for attempt in attempts:
            try:
                result = attempt()
                if result is not False and target.exists():
                    return target
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
        raise RuntimeError("falha ao exportar Touchstone: " + " | ".join(errors))

    def extract_network_traces(
        self,
        *,
        setup_sweep: str,
        expressions: Iterable[str],
    ) -> tuple[NetworkTrace, ...]:
        traces: list[NetworkTrace] = []
        for expression in expressions:
            solution = self.app.post.get_solution_data(
                expressions=[expression],
                setup_sweep_name=setup_sweep,
                domain="Sweep",
                primary_sweep_variable="Freq",
            )
            if solution is None or solution is False:
                raise RuntimeError(f"HFSS não retornou {expression}")
            frequencies = np.asarray(solution.primary_sweep_values, dtype=float).reshape(-1)
            try:
                real = np.asarray(solution.data_real(expression), dtype=float).reshape(-1)
                imag = np.asarray(solution.data_imag(expression), dtype=float).reshape(-1)
            except Exception:
                complex_values = np.asarray(solution.get_expression_data(expression), dtype=complex).reshape(-1)
                real = complex_values.real
                imag = complex_values.imag
            if not (len(frequencies) == len(real) == len(imag)):
                raise RuntimeError(f"dimensões inconsistentes para {expression}")
            traces.append(
                NetworkTrace(
                    expression=expression,
                    frequencies_ghz=tuple(float(v) for v in frequencies),
                    real=tuple(float(v) for v in real),
                    imag=tuple(float(v) for v in imag),
                )
            )
        return tuple(traces)

    def ensure_farfield_sphere(self, name: str = "FF_Sphere_1deg") -> str:
        existing = set(str(value) for value in getattr(self.app, "field_setup_names", []))
        if name in existing:
            return name
        sphere = self.app.insert_infinite_sphere(
            definition="Theta-Phi",
            x_start=-180,
            x_stop=180,
            x_step=1,
            y_start=-180,
            y_stop=180,
            y_step=1,
            name=name,
        )
        if sphere is False or sphere is None:
            raise RuntimeError("falha ao criar esfera de campo distante")
        return str(getattr(sphere, "name", name))

    @staticmethod
    def write_network_json(path: str | Path, traces: Iterable[NetworkTrace]) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps([trace.as_manifest() for trace in traces], indent=2),
            encoding="utf-8",
        )
        return target
