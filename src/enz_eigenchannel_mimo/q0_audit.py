from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .specifications import sha256_arquivo

Q0_STATUS_BLOCKED = "BLOCKED_MISSING_VALIDATED_ARTIFACTS"
REQUIRED_RADIATORS = ("RAD_A1", "RAD_A2", "RAD_B1", "RAD_B2")
SEARCH_SUFFIXES = (
    ".aedt",
    ".a3dcomp",
    ".step",
    ".stp",
    ".sat",
    ".x_t",
    ".s1p",
    ".s2p",
    ".s3p",
    ".s4p",
    ".ffd",
    ".json",
    ".yaml",
    ".csv",
)
REQUIRED_MANIFEST_FIELDS = (
    "id",
    "source_file",
    "source_sha256",
    "source_git_commit",
    "aedt_version",
    "pyaedt_version",
    "design_name",
    "solution_type",
    "port_name",
    "port_mode",
    "frequency_center_ghz",
    "frequency_band_ghz",
    "coordinate_system",
    "orientation",
    "materials",
    "boundaries",
    "setups",
    "sweeps",
    "mesh_summary",
    "convergence_artifact",
    "touchstone_artifact",
    "farfield_artifact",
    "validation_report",
    "evidence_class",
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _ignored(path: Path, root: Path) -> bool:
    parts = path.resolve().relative_to(root.resolve()).parts
    generated_audit = len(parts) >= 2 and parts[0] == "artefatos" and parts[1] in {
        "preflight",
        "q0",
    }
    return any(
        part in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"}
        for part in parts
    ) or generated_audit or any(
        part in {"failed_publications", "report_preview", "sensitive_ephemeral"}
        for part in parts
    )


def inventariar_artefatos(root: Path) -> list[dict[str, Any]]:
    encontrados: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if not path.is_file() or _ignored(path, root):
            continue
        if path.suffix.lower() not in SEARCH_SUFFIXES:
            continue
        encontrados.append(
            {
                "path": _relative(path, root),
                "suffix": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": sha256_arquivo(path),
            }
        )
    return sorted(encontrados, key=lambda item: item["path"].casefold())


def _carregar_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _evidencia_candidato(path: str, root: Path) -> tuple[str, list[str], list[str]]:
    normalized = path.casefold()
    evidence: list[str] = []
    reasons: list[str] = []
    classification = "DESCONHECIDO"
    candidate_path = root / path
    run_manifest: dict[str, Any] | None = None
    for parent in candidate_path.parents:
        if parent == root.parent:
            break
        manifest_path = parent / "manifest.json"
        manifest = _carregar_json(manifest_path)
        if manifest and str(manifest.get("schema", "")).endswith("run-manifest/v2"):
            run_manifest = manifest
            evidence.append(_relative(manifest_path, root))
            break
    if run_manifest:
        specification = str(run_manifest.get("specification", {}).get("path", ""))
        if "hipotese" in specification.casefold():
            classification = "HIPÓTESE"
            reasons.append("a especificação do run é explicitamente HIPÓTESE")
        status = run_manifest.get("status")
        solve = run_manifest.get("solver", {}).get("solve_requested")
        reasons.append(f"manifesto do run registra status={status} e solve_requested={solve}")
    if "smoke" in normalized:
        classification = "HIPÓTESE"
        reasons.append(
            "cavidade sintética Eigenmode destinada apenas ao smoke test; "
            "não é radiador Driven Modal validado"
        )
        evidence.append(
            "poros_aedt/runs/ENZ-20260803-173105-52288067/metrics/validacao_gates.json"
        )
    elif "g0_figura2_v5" in normalized:
        classification = "HIPÓTESE"
        manifest_path = root / (
            "poros_aedt/reconstrucoes_exploratorias/G0_figura2_v5/"
            "build_manifest.json"
        )
        manifest = _carregar_json(manifest_path)
        evidence.append(_relative(manifest_path, root))
        if manifest:
            solve = manifest.get("solver", {}).get("solve_requested")
            status = manifest.get("status")
            reasons.append(f"manifesto registra status={status} e solve_requested={solve}")
        else:
            reasons.append("manifesto de build ausente ou ilegível")
    elif "g0_figura2_v7" in normalized:
        classification = "HIPÓTESE"
        validation_path = root / (
            "poros_aedt/reconstrucoes_exploratorias/G0_figura2_v7/"
            "posprocessamento/validacao_cientifica_exploratoria.json"
        )
        validation = _carregar_json(validation_path)
        evidence.append(_relative(validation_path, root))
        if validation:
            reasons.extend(
                [
                    "classificação global HIPÓTESE",
                    "gate estrito de passividade FAIL",
                    "gate de correspondência de S11 FAIL",
                ]
            )
        else:
            reasons.append("relatório de validação ausente ou ilegível")
    elif "g0_figura2_reconstrucao" in normalized:
        classification = "HIPÓTESE"
        reasons.append("reconstrução exploratória sem promoção a reprodução validada")
    else:
        reasons.append("não existe manifesto de componente validado associado")
    reasons.append(
        "não existe manifesto modelos/componentes_validados/RAD_*/manifest.json "
        "que vincule este arquivo a uma instância Q0"
    )
    return classification, reasons, evidence


def _validar_manifesto_componente(
    root: Path, radiator_id: str
) -> tuple[bool, list[str], dict[str, Any] | None]:
    manifest_path = root / "modelos" / "componentes_validados" / radiator_id / "manifest.json"
    manifest = _carregar_json(manifest_path)
    if manifest is None:
        return False, [f"manifesto ausente: {_relative(manifest_path, root)}"], None
    reasons: list[str] = []
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
    if missing:
        reasons.append("campos obrigatórios ausentes: " + ", ".join(missing))
    if manifest.get("id") != radiator_id:
        reasons.append("id do manifesto não corresponde à instância")
    if manifest.get("aedt_version") != "2024.2":
        reasons.append("aedt_version deve ser 2024.2")
    if manifest.get("evidence_class") != "SIMULADO":
        reasons.append("evidence_class deve ser SIMULADO")
    source = manifest.get("source_file")
    if not isinstance(source, str) or not source:
        reasons.append("source_file vazio")
    else:
        source_path = root / source
        if not source_path.is_file():
            reasons.append("source_file não encontrado")
        elif manifest.get("source_sha256") != sha256_arquivo(source_path):
            reasons.append("source_sha256 divergente")
    for field in (
        "convergence_artifact",
        "touchstone_artifact",
        "farfield_artifact",
        "validation_report",
    ):
        value = manifest.get(field)
        if not isinstance(value, str) or not value or not (root / value).is_file():
            reasons.append(f"{field} ausente ou não encontrado")
    return not reasons, reasons, manifest


def auditar_q0(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = root.resolve()
    inventory = inventariar_artefatos(root)
    aedt_candidates = [item for item in inventory if item["suffix"] == ".aedt"]
    candidates: list[dict[str, Any]] = []
    for item in aedt_candidates:
        classification, reasons, evidence = _evidencia_candidato(item["path"], root)
        candidates.append(
            {
                **item,
                "classification": classification,
                "eligible_as_validated_radiator": False,
                "reasons": reasons,
                "evidence": evidence,
            }
        )

    component_status: list[dict[str, Any]] = []
    validated_count = 0
    for radiator_id in REQUIRED_RADIATORS:
        valid, reasons, manifest = _validar_manifesto_componente(root, radiator_id)
        validated_count += int(valid)
        component_status.append(
            {
                "id": radiator_id,
                "validated": valid,
                "reasons": reasons,
                "manifest": manifest,
            }
        )

    missing_docs = [
        path
        for path in (
            "docs/30_implementacao_aedt_2024r2.md",
            "docs/31_planejamento_mimo_2x2_quatro_radiadores_guia.md",
        )
        if not (root / path).is_file()
    ]
    status = "PASS" if validated_count == len(REQUIRED_RADIATORS) else Q0_STATUS_BLOCKED
    missing = {
        "schema": "enz-eigenchannel-mimo/q0-missing-validated-models/v1",
        "gate": "Q0",
        "status": status,
        "classification": "DESCONHECIDO" if status != "PASS" else "SIMULADO",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git": {
            "branch": _git(root, "branch", "--show-current"),
            "commit": _git(root, "rev-parse", "HEAD"),
            "dirty": bool(_git(root, "status", "--porcelain")),
        },
        "required_instances": list(REQUIRED_RADIATORS),
        "validated_instances_found": validated_count,
        "component_status": component_status,
        "aedt_candidates": candidates,
        "missing_referenced_documents": missing_docs,
        "prohibited_progression": ["Q1", "Q2", "Q3", "Q4", "Q5"],
        "required_action": (
            "Fornecer quatro manifestos de componentes validados, seus projetos AEDT, "
            "Touchstone, convergência, padrões complexos e relatórios de regressão."
        ),
        "risk": (
            "Duplicar a reconstrução v7 promoveria uma hipótese reprovada a componente "
            "validado e contaminaria todas as métricas MIMO posteriores."
        ),
    }
    inventory_document = {
        "schema": "enz-eigenchannel-mimo/q0-artifact-inventory/v1",
        "classification": "DERIVADO",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "search_suffixes": list(SEARCH_SUFFIXES),
        "file_count": len(inventory),
        "files": inventory,
    }
    return missing, inventory_document


def escrever_auditoria(root: Path, output_dir: Path) -> tuple[Path, Path]:
    missing, inventory = auditar_q0(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    missing_path = output_dir / "missing_validated_models.json"
    inventory_path = output_dir / "artifact_inventory.json"
    missing_path.write_text(
        json.dumps(missing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    inventory_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return missing_path, inventory_path
