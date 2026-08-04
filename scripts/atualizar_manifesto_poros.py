"""Atualiza o inventário SHA-256 global de ``poros_aedt``."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POROS = ROOT / "poros_aedt"
MANIFEST = POROS / "manifest.json"
Q4_SOLVER_CACHE = (
    POROS
    / "reconstrucoes_exploratorias"
    / "Q4_mimo2x2_c0_v8"
    / "projeto_configurado"
    / "Q4_mimo2x2_c0_v8_HIPOTESE.aedtresults"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"JSON não é objeto: {path}")
    return data


def git_paths(*arguments: str) -> set[str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return {
        item.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for item in result.stdout.split(b"\0")
        if item
    }


def update(*, allow_active_locks: bool = False) -> dict[str, Any]:
    if not POROS.is_dir():
        raise FileNotFoundError(POROS)
    tracked_paths = git_paths("ls-files", "-z", "--", "poros_aedt")
    temporarily_absent = sorted(
        path.removeprefix("poros_aedt/")
        for path in git_paths(
            "diff",
            "--name-only",
            "--diff-filter=D",
            "-z",
            "--",
            "poros_aedt",
        )
    )
    ephemeral = [
        path
        for path in POROS.rglob("*")
        if path.is_file()
        and (
            path.name.endswith((".aedt.lock", ".semaphore"))
            or (
                path.name.endswith((".tmp", ".asol_priv"))
                and path.relative_to(ROOT).as_posix() not in tracked_paths
            )
        )
    ]
    versionable_ephemeral = [path for path in ephemeral if path.stat().st_size > 0]
    if versionable_ephemeral and not allow_active_locks:
        raise ValueError(
            "locks não vazios não podem ser publicados: "
            + ", ".join(str(path) for path in versionable_ephemeral)
        )

    report_manifest_path = (
        POROS
        / "relatorios"
        / "Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v3.manifest.json"
    )
    reconstruction_manifest_path = (
        POROS
        / "reconstrucoes_exploratorias"
        / "G0_figura2_v7"
        / "manifest.json"
    )
    report = load_json(report_manifest_path)
    reconstruction = load_json(reconstruction_manifest_path)
    solver_cache = [
        path
        for path in Q4_SOLVER_CACHE.rglob("*")
        if path.is_file() and path not in ephemeral
    ]
    files = []
    for path in sorted(item for item in POROS.rglob("*") if item.is_file()):
        if path == MANIFEST or path in ephemeral or path in solver_cache:
            continue
        files.append(
            {
                "path": path.relative_to(POROS).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": "poros-aedt-package-v2",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "classificacao_resultado": "SIMULADO",
        "classificacao_geometria": "HIPÓTESE",
        "primary_source": {
            "doi": "10.1109/OJAP.2026.3703713",
            "authors": report["primary_source"]["authors"],
            "license": report["primary_source"]["license"],
        },
        "packages": {
            "m0_infrastructure_run": "ENZ-20260803-173105-52288067",
            "g0_exploratory_reconstruction": reconstruction["run_limpo"],
            "technical_report": report["report"]["sha256"],
            "q0_validated_radiators": "BLOCKED_MISSING_VALIDATED_ARTIFACTS",
            "q4_exploratory_model": (
                "reconstrucoes_exploratorias/Q4_mimo2x2_c0_v8/"
                "projeto_configurado/Q4_mimo2x2_c0_v8_HIPOTESE.aedt"
            ),
        },
        "scientific_gates": {
            "m0_infrastructure": "PASS",
            "g0_waveport_axis_z": "PASS",
            "g0_adaptive_convergence": "PASS",
            "g0_strict_passivity": "FAIL",
            "g0_published_s11_correspondence": "FAIL",
            "q0_validated_instances": "0/4",
            "q4_adaptive_convergence": "PASS",
            "q4_strict_passivity": "PASS",
            "q4_s11_matching": "FAIL",
            "q4_s22_matching": "FAIL",
            "q4_complex_embedded_patterns": "PASS",
            "q4_mimo_claim": "BLOCKED_SOURCE_MODEL_HIPOTESE",
            "mimo_2x2_system": "HIPÓTESE",
            "global_reproduction_classification": "HIPÓTESE",
        },
        "active_session_locks_excluded": [
            path.relative_to(POROS).as_posix()
            for path in versionable_ephemeral
            if path.name.endswith(".aedt.lock")
        ],
        "active_session_generated_files_excluded": [
            path.relative_to(POROS).as_posix()
            for path in versionable_ephemeral
            if not path.name.endswith(".aedt.lock")
        ],
        "active_session_tracked_files_temporarily_absent": temporarily_absent,
        "nonportable_solver_cache_excluded": [
            {
                "path": path.relative_to(POROS).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "reason": (
                    "cache privado reproduzível pelo AEDT; arquivos individuais "
                    "excedem o limite de 100 MB do GitHub"
                ),
            }
            for path in sorted(solver_cache)
        ],
        "ephemeral_files_excluded": [
            path.relative_to(POROS).as_posix() for path in ephemeral
        ],
        "arquivos": files,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-active-locks",
        action="store_true",
        help=(
            "Exclui locks ativos do inventário. Use somente quando a sessão AEDT "
            "precisa permanecer aberta e está registrada em artefato de inspeção."
        ),
    )
    args = parser.parse_args()
    manifest = update(allow_active_locks=args.allow_active_locks)
    print(
        json.dumps(
            {
                "schema_version": manifest["schema_version"],
                "arquivos": len(manifest["arquivos"]),
                "ephemeral_files_excluded": manifest["ephemeral_files_excluded"],
                "active_session_locks_excluded": manifest[
                    "active_session_locks_excluded"
                ],
                "active_session_generated_files_excluded": manifest[
                    "active_session_generated_files_excluded"
                ],
                "active_session_tracked_files_temporarily_absent": manifest[
                    "active_session_tracked_files_temporarily_absent"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
