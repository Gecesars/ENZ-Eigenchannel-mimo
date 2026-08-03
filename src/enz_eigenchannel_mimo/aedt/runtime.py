from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


class ErroRuntimeAedt(RuntimeError):
    """Falha de preflight ou violação da seleção estrita do AEDT."""


@dataclass(frozen=True, slots=True)
class AedtRuntimeSpec:
    version: str = "2024.2"
    pyaedt_version: str = "1.3.0"
    strict_version: bool = True
    non_graphical: bool = True
    new_desktop: bool = True
    close_on_exit: bool = True
    machine: str = ""
    port: int = 0
    process_id: int | None = None
    cores: int = 14
    tasks: int = 1
    gpus: int = 0
    startup_timeout_s: int = 180
    solve_timeout_s: int = 21600

    def __post_init__(self) -> None:
        if self.version != "2024.2":
            raise ValueError("o runtime científico primário deve ser AEDT 2024.2")
        if not self.strict_version:
            raise ValueError("fallback de versão AEDT é proibido")
        if self.startup_timeout_s <= 0 or self.solve_timeout_s <= 0:
            raise ValueError("timeouts devem ser positivos")
        if not 0 <= self.port <= 65535:
            raise ValueError("porta gRPC inválida")


        if self.cores <= 0:
            raise ValueError("cores deve ser positivo")
        if self.tasks <= 0:
            raise ValueError("tasks deve ser positivo")
        if self.gpus < 0:
            raise ValueError("gpus nao pode ser negativo")


@dataclass(frozen=True, slots=True)
class ResultadoPreflightAedt:
    executable: Path
    pyaedt_version: str
    license_status: str


def localizar_executavel_2024r2() -> Path:
    candidatos: list[Path] = []
    raiz_env = os.getenv("ANSYSEM_ROOT242")
    if raiz_env:
        candidatos.append(Path(raiz_env) / "Win64" / "ansysedt.exe")
    candidatos.extend(
        [
            Path(r"C:\Program Files\AnsysEM\v242\Win64\ansysedt.exe"),
            Path(r"C:\Program Files\ANSYS Inc\v242\AnsysEM\Win64\ansysedt.exe"),
        ]
    )
    for candidato in candidatos:
        if candidato.is_file():
            return candidato.resolve()
    raise ErroRuntimeAedt("AEDT 2024 R2 não encontrado nos caminhos estritos")


def _versao_pyaedt() -> str:
    try:
        return version("pyaedt")
    except PackageNotFoundError as exc:
        raise ErroRuntimeAedt("PyAEDT não está instalado; use o extra [aedt]") from exc


def _status_licenca() -> str:
    try:
        from ansys.aedt.core.generic.file_utils import available_license_feature

        disponiveis = int(available_license_feature())
    except Exception as exc:  # noqa: BLE001 -- API externa usa exceções heterogêneas
        return f"DESCONHECIDO: preflight de licença falhou ({type(exc).__name__})"
    if disponiveis > 0:
        return f"DISPONIVEL: available_license_feature={disponiveis}"
    if disponiveis == 0:
        return "INDISPONIVEL: available_license_feature=0"
    return "DESCONHECIDO: servidor de licença não identificado"


def preflight_aedt(runtime: AedtRuntimeSpec) -> ResultadoPreflightAedt:
    if platform.system() != "Windows":
        raise ErroRuntimeAedt("este worker local AEDT 2024 R2 exige Windows")
    executavel = localizar_executavel_2024r2()
    pyaedt = _versao_pyaedt()
    if pyaedt != runtime.pyaedt_version:
        raise ErroRuntimeAedt(
            f"PyAEDT {pyaedt} instalado; versão estrita esperada {runtime.pyaedt_version}"
        )
    licenca = _status_licenca()
    if licenca.startswith("INDISPONIVEL"):
        raise ErroRuntimeAedt(licenca)
    return ResultadoPreflightAedt(
        executable=executavel, pyaedt_version=pyaedt, license_status=licenca
    )


def capturar_runtime_app(app: Any, runtime: AedtRuntimeSpec) -> dict[str, Any]:
    desktop = app.desktop_class
    versao_exata = str(desktop.odesktop.GetVersion())
    versao_id = str(getattr(desktop, "aedt_version_id", versao_exata[:6]))
    if runtime.strict_version and versao_id != runtime.version:
        raise ErroRuntimeAedt(
            f"AEDT iniciado em {versao_exata}; exigido exatamente {runtime.version}"
        )
    return {
        "build": versao_exata,
        "pid": int(desktop.aedt_process_id),
        "grpc_port": int(desktop.port),
    }
