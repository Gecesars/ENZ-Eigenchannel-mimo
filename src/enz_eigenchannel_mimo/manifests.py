from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from .specifications import (
    SCHEMA_MANIFESTO,
    EspecificacaoGeometrica,
    sha256_arquivo,
    validar_documento,
)


class StatusExecucao(StrEnum):
    CREATED = "CREATED"
    PREFLIGHT = "PREFLIGHT"
    CONNECTING = "CONNECTING"
    BUILDING = "BUILDING"
    VALIDATING_GEOMETRY = "VALIDATING_GEOMETRY"
    BUILT = "BUILT"
    MESHING = "MESHING"
    SOLVING = "SOLVING"
    POSTPROCESSING = "POSTPROCESSING"
    EXPORTING = "EXPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


def _agora() -> str:
    return datetime.now(UTC).isoformat()


def _git(cwd: Path) -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    return {"commit": commit, "dirty": dirty}


def _host() -> dict[str, Any]:
    ram: int | None = None
    try:
        import psutil

        ram = int(psutil.virtual_memory().total)
    except ImportError:
        pass
    return {
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "hostname": socket.gethostname(),
        "cpu_count": os.cpu_count(),
        "ram_bytes": ram,
    }


def identidade_arquivo(caminho: Path, base: Path | None = None) -> dict[str, Any]:
    origem = caminho.resolve()
    path = str(origem.relative_to(base.resolve())) if base else str(origem)
    return {
        "path": path,
        "sha256": sha256_arquivo(origem),
        "bytes": origem.stat().st_size,
    }


@dataclass(slots=True)
class ManifestoExecucao:
    caminho: Path
    dados: dict[str, Any]

    @classmethod
    def criar(
        cls,
        base_runs: Path,
        spec: EspecificacaoGeometrica,
        etapa: str,
        solve_requested: bool,
        repo_root: Path,
        *,
        cores: int = 14,
        tasks: int = 1,
        gpus: int = 0,
    ) -> ManifestoExecucao:
        instante = datetime.now(UTC)
        run_id = f"ENZ-{instante:%Y%m%d-%H%M%S}-{spec.sha256[:8]}"
        diretorio_run = base_runs.resolve() / run_id
        diretorio_run.mkdir(parents=True, exist_ok=False)
        etapa_dados = spec.etapa(etapa)
        dados: dict[str, Any] = {
            "schema": SCHEMA_MANIFESTO,
            "run_id": run_id,
            "status": StatusExecucao.CREATED.value,
            "created_at": instante.isoformat(),
            "updated_at": instante.isoformat(),
            "completed_at": None,
            "specification": identidade_arquivo(spec.caminho),
            "git": _git(repo_root),
            "host": _host(),
            "runtime": {
                "requested_aedt": "2024.2",
                "strict_version": True,
                "pyaedt": None,
                "transport": "native AEDT gRPC via PyAEDT",
                "license": "DESCONHECIDO: preflight ainda não executado",
                "pid": None,
                "grpc_port": None,
                "build": None,
                "orphan_after_close": None,
            },
            "solver": {
                "stage": etapa,
                "solution_type": etapa_dados["solucao"],
                "setup": etapa_dados["setup"]["nome"],
                "solve_requested": solve_requested,
                "cores": cores,
                "tasks": tasks,
                "gpus": gpus,
                "validation_messages": [],
            },
            "artifacts": [],
            "errors": [],
        }
        manifesto = cls(caminho=diretorio_run / "manifest.json", dados=dados)
        manifesto.salvar()
        return manifesto

    def atualizar_status(self, status: StatusExecucao) -> None:
        self.dados["status"] = status.value
        self.dados["updated_at"] = _agora()
        if status in {
            StatusExecucao.BUILT,
            StatusExecucao.COMPLETED,
            StatusExecucao.FAILED,
            StatusExecucao.CANCELLED,
        }:
            self.dados["completed_at"] = self.dados["updated_at"]
        self.salvar()

    def registrar_erro(self, erro: BaseException | str) -> None:
        self.dados["errors"].append(str(erro))
        self.atualizar_status(StatusExecucao.FAILED)

    def registrar_artefatos(self, caminhos: list[Path], base: Path) -> None:
        indices = {
            item["path"]: indice for indice, item in enumerate(self.dados["artifacts"])
        }
        for caminho in caminhos:
            if caminho.is_file():
                identidade = identidade_arquivo(caminho, base)
                indice = indices.get(identidade["path"])
                if indice is None:
                    self.dados["artifacts"].append(identidade)
                    indices[identidade["path"]] = len(self.dados["artifacts"]) - 1
                else:
                    # O projeto AEDT e os logs continuam mudando durante o run.
                    # O manifesto deve conservar a identidade final, não a primeira.
                    self.dados["artifacts"][indice] = identidade
        self.salvar()

    def salvar(self) -> None:
        validar_documento(self.dados, SCHEMA_MANIFESTO)
        temporario = self.caminho.with_suffix(".json.tmp")
        temporario.write_text(
            json.dumps(self.dados, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporario.replace(self.caminho)
