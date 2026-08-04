from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _executar(*argumentos: str) -> dict[str, Any]:
    ambiente = os.environ.copy()
    ambiente["PYTHONUTF8"] = "1"
    ambiente["PYTHONIOENCODING"] = "utf-8"
    processo = subprocess.run(
        list(argumentos),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ambiente,
        check=False,
    )
    return {
        "command": list(argumentos),
        "returncode": processo.returncode,
        "stdout": processo.stdout,
        "stderr": processo.stderr,
    }


def _versao_pacote(nome: str) -> str | None:
    try:
        return version(nome)
    except PackageNotFoundError:
        return None


def _memoria_total() -> int | None:
    try:
        import psutil

        return int(psutil.virtual_memory().total)
    except ImportError:
        return None


def _aedt_preflight() -> dict[str, Any]:
    from enz_eigenchannel_mimo.aedt.runtime import AedtRuntimeSpec, preflight_aedt

    try:
        resultado = preflight_aedt(AedtRuntimeSpec())
    except Exception as exc:  # noqa: BLE001 -- o artefato deve registrar a falha externa
        return {
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "requested_version": "2024.2",
            "token": "242",
        }
    return {
        "status": "PASS",
        "requested_version": "2024.2",
        "token": "242",
        "executable": str(resultado.executable),
        "pyaedt_version": resultado.pyaedt_version,
        "license_status": resultado.license_status,
    }


def _agora() -> tuple[str, str]:
    local = datetime.now().astimezone()
    return local.astimezone(UTC).isoformat(), local.isoformat()


def registrar(destino: Path, preexisting_changes: list[str] | None = None) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    utc, local = _agora()
    estado = _executar("git", "status", "--short")
    branch = _executar("git", "branch", "--show-current")
    commit = _executar("git", "rev-parse", "HEAD")
    log = _executar("git", "log", "-1", "--oneline")

    repository_state = {
        "schema": "enz-eigenchannel-mimo/preflight-repository/v1",
        "classification": "DERIVADO",
        "captured_at_utc": utc,
        "captured_at_local": local,
        "working_directory": str(ROOT),
        "branch": branch["stdout"].strip(),
        "initial_commit": commit["stdout"].strip(),
        "initial_log": log["stdout"].strip(),
        "changes_at_capture": [
            linha for linha in estado["stdout"].splitlines() if linha.strip()
        ],
        "preexisting_changes": preexisting_changes
        if preexisting_changes is not None
        else [linha for linha in estado["stdout"].splitlines() if linha.strip()],
    }
    (destino / "repository_state.json").write_text(
        json.dumps(repository_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    environment = {
        "schema": "enz-eigenchannel-mimo/preflight-environment/v1",
        "classification": "DERIVADO",
        "captured_at_utc": utc,
        "captured_at_local": local,
        "working_directory": str(ROOT),
        "python": sys.version,
        "python_executable": sys.executable,
        "pip": _versao_pacote("pip"),
        "pyaedt": _versao_pacote("pyaedt"),
        "operating_system": platform.platform(),
        "hostname": socket.gethostname(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "memory_bytes": _memoria_total(),
        "aedt": _aedt_preflight(),
    }
    (destino / "environment.json").write_text(
        json.dumps(environment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    comandos = [
        ("git status --short", ("git", "status", "--short")),
        ("git branch --show-current", ("git", "branch", "--show-current")),
        ("git log -1 --oneline", ("git", "log", "-1", "--oneline")),
        ("python --version", (sys.executable, "--version")),
        ("python -m pip --version", (sys.executable, "-m", "pip", "--version")),
        ("python -m pip check", (sys.executable, "-m", "pip", "check")),
        ("python -m pytest -q", (sys.executable, "-m", "pytest", "-q")),
        (
            "python -m compileall -q src scripts testes",
            (sys.executable, "-m", "compileall", "-q", "src", "scripts", "testes"),
        ),
        (
            "python -m ruff check src scripts testes",
            (sys.executable, "-m", "ruff", "check", "src", "scripts", "testes"),
        ),
        (
            "python scripts/normalizar_formulas_markdown.py --check",
            (sys.executable, "scripts/normalizar_formulas_markdown.py", "--check"),
        ),
    ]
    linhas = [
        "PRE-FLIGHT MIMO 2x2 / Q0",
        f"UTC: {utc}",
        f"LOCAL: {local}",
        f"WORKDIR: {ROOT}",
        "CLASSIFICACAO: DERIVADO",
        "",
    ]
    for rotulo, comando in comandos:
        resultado = _executar(*comando)
        linhas.extend(
            [
                f"$ {rotulo}",
                f"RETURN_CODE={resultado['returncode']}",
                resultado["stdout"].rstrip(),
                resultado["stderr"].rstrip(),
                "",
            ]
        )
    (destino / "test_baseline.txt").write_text(
        "\n".join(linhas).rstrip() + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Registra o pré-flight Q0 auditável.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artefatos" / "preflight",
    )
    parser.add_argument(
        "--preexisting-change",
        action="append",
        default=None,
        help="Linha de git status observada antes da tarefa; opção repetível.",
    )
    args = parser.parse_args()
    registrar(args.output.resolve(), args.preexisting_change)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
