"""Preflight geométrico e validação de design antes do solve."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from enz_eigenchannel_mimo.geometry.plan import GeometryPlan
from enz_eigenchannel_mimo.geometry.spec import G0GeometrySpec, OrigemDado


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    code: str
    severity: Severity
    message: str
    context: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PreflightReport:
    findings: tuple[ValidationFinding, ...]

    @property
    def ok(self) -> bool:
        return not any(item.severity is Severity.ERROR for item in self.findings)

    def require_ok(self) -> None:
        if not self.ok:
            messages = " | ".join(
                f"{item.code}: {item.message}"
                for item in self.findings
                if item.severity is Severity.ERROR
            )
            raise RuntimeError(f"preflight rejeitado: {messages}")

    def as_manifest(self) -> dict[str, Any]:
        return {"ok": self.ok, "findings": [asdict(item) for item in self.findings]}


def preflight_offline(
    spec: G0GeometrySpec,
    plan: GeometryPlan,
    *,
    project_path: str | Path,
    scientific_run: bool,
) -> PreflightReport:
    findings: list[ValidationFinding] = []
    try:
        spec.validate()
    except Exception as exc:
        findings.append(
            ValidationFinding("SPEC_INVALID", Severity.ERROR, str(exc), {})
        )
    try:
        plan.validate()
    except Exception as exc:
        findings.append(
            ValidationFinding("PLAN_INVALID", Severity.ERROR, str(exc), {})
        )

    hypotheses = [
        path
        for path, value in spec.iter_grandezas()
        if value.origem in {OrigemDado.HIPOTESE, OrigemDado.INFERIDO}
    ]
    if hypotheses:
        findings.append(
            ValidationFinding(
                "HYPOTHESIS_GEOMETRY",
                Severity.ERROR if scientific_run else Severity.WARNING,
                "geometria contém dimensões hipotéticas/inferidas",
                {"paths": hypotheses},
            )
        )

    target = Path(project_path).expanduser().resolve()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        probe = target.parent / ".enz_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        findings.append(
            ValidationFinding(
                "OUTPUT_NOT_WRITABLE",
                Severity.ERROR,
                f"pasta de saída não gravável: {exc}",
                {"path": str(target.parent)},
            )
        )

    if plan.solution_type == "Modal" and len(plan.ports) != 1:
        findings.append(
            ValidationFinding(
                "PORT_COUNT",
                Severity.ERROR,
                "G0 Driven Modal deve possuir exatamente uma porta",
                {"count": len(plan.ports)},
            )
        )
    if plan.solution_type == "Eigenmode" and plan.open_region_frequency is not None:
        findings.append(
            ValidationFinding(
                "EIGEN_OPEN_REGION",
                Severity.ERROR,
                "M0 fechado não deve habilitar domínio aberto",
                {},
            )
        )

    if not findings:
        findings.append(
            ValidationFinding("PREFLIGHT_OK", Severity.INFO, "preflight offline aprovado", {})
        )
    return PreflightReport(tuple(findings))


def validate_live_design(app: Any, plan: GeometryPlan) -> PreflightReport:
    findings: list[ValidationFinding] = []
    object_names = set(str(name) for name in getattr(app.modeler, "object_names", []))
    expected_objects = {
        primitive.name for primitive in plan.primitives if not primitive.non_model
    }
    for operation in plan.operations:
        if operation.kind in {"subtract", "unite"}:
            expected_objects.difference_update(operation.tools)
    missing = sorted(expected_objects - object_names)
    if missing:
        findings.append(
            ValidationFinding(
                "MISSING_OBJECTS",
                Severity.ERROR,
                "objetos CAD esperados ausentes",
                {"objects": missing},
            )
        )

    ports = set(str(name) for name in getattr(app, "ports", []))
    expected_ports = {port.name for port in plan.ports}
    missing_ports = sorted(expected_ports - ports)
    if missing_ports:
        findings.append(
            ValidationFinding(
                "MISSING_PORTS",
                Severity.ERROR,
                "portas esperadas ausentes",
                {"ports": missing_ports},
            )
        )

    setups = set(str(name) for name in getattr(app, "setup_names", []))
    if not setups:
        findings.append(
            ValidationFinding("NO_SETUP", Severity.ERROR, "design sem setup", {})
        )

    try:
        result = app.validate_full_design(
            design=getattr(app, "design_name", None),
            ports=len(plan.ports),
        )
        if isinstance(result, tuple) and result and result[0] is False:
            findings.append(
                ValidationFinding(
                    "AEDT_VALIDATE_FAILED",
                    Severity.ERROR,
                    "validate_full_design retornou falha",
                    {"raw": repr(result)},
                )
            )
    except TypeError:
        try:
            result = app.validate_simple()
            if result is False:
                findings.append(
                    ValidationFinding(
                        "AEDT_VALIDATE_FAILED",
                        Severity.ERROR,
                        "validate_simple retornou falha",
                        {},
                    )
                )
        except Exception as exc:
            findings.append(
                ValidationFinding(
                    "AEDT_VALIDATE_EXCEPTION",
                    Severity.ERROR,
                    str(exc),
                    {},
                )
            )
    except Exception as exc:
        findings.append(
            ValidationFinding(
                "AEDT_VALIDATE_EXCEPTION", Severity.ERROR, str(exc), {}
            )
        )

    if not findings:
        findings.append(
            ValidationFinding("LIVE_VALIDATION_OK", Severity.INFO, "design AEDT aprovado", {})
        )
    return PreflightReport(tuple(findings))
