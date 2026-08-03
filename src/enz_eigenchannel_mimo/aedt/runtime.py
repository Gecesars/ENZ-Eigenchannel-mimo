"""Contrato estrito do runtime Ansys Electronics Desktop 2024 R2.

O módulo não importa PyAEDT no carregamento. Isso mantém testes, documentação e
análises matemáticas executáveis em máquinas sem AEDT/licença.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

AEDT_VERSION = "2024.2"
AEDT_VERSION_TOKEN = "242"


class AedtRuntimeError(RuntimeError):
    """Falha de disponibilidade, conexão ou identidade do AEDT."""


@dataclass(frozen=True, slots=True)
class AedtRuntimeSpec:
    """Configuração serializável para uma única sessão AEDT/HFSS.

    Campanhas oficiais usam uma instância dedicada em modo não gráfico. Para
    inspeção manual, ``new_desktop=False`` exige porta gRPC ou PID explícito;
    não há descoberta ambígua nem fallback silencioso de versão.
    """

    version: str = AEDT_VERSION
    strict_version: bool = True
    non_graphical: bool = True
    new_desktop: bool = True
    close_on_exit: bool = True
    student_version: bool = False
    machine: str = "localhost"
    port: int = 0
    process_id: int | None = None
    remove_lock: bool = False
    startup_timeout_s: int = 180
    solve_timeout_s: int = 21_600

    def validate(self) -> None:
        if self.strict_version and normalize_aedt_version(self.version) != AEDT_VERSION:
            raise ValueError(
                f"Este projeto exige AEDT {AEDT_VERSION}; recebido {self.version!r}."
            )
        if self.port < 0 or self.port > 65_535:
            raise ValueError("porta gRPC fora da faixa válida")
        if self.process_id is not None and self.process_id <= 0:
            raise ValueError("process_id deve ser positivo")
        if self.startup_timeout_s <= 0 or self.solve_timeout_s <= 0:
            raise ValueError("timeouts devem ser positivos")
        if not self.new_desktop and self.port <= 0 and self.process_id is None:
            raise ValueError(
                "attach explícito exige port>0 ou process_id; descoberta implícita é proibida"
            )
        if self.new_desktop and self.process_id is not None:
            raise ValueError("new_desktop e process_id não podem ser combinados")

    def pyaedt_kwargs(self) -> dict[str, Any]:
        self.validate()
        return {
            "version": AEDT_VERSION,
            "non_graphical": self.non_graphical,
            "new_desktop": self.new_desktop,
            "close_on_exit": False,
            "student_version": self.student_version,
            "machine": self.machine,
            "port": self.port,
            "aedt_process_id": self.process_id,
            "remove_lock": self.remove_lock,
        }

    def as_manifest(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["normalized_version"] = normalize_aedt_version(self.version)
        payload["version_token"] = AEDT_VERSION_TOKEN
        return payload


@dataclass(frozen=True, slots=True)
class AedtRuntimeIdentity:
    requested_version: str
    detected_version: str
    process_id: int | None
    port: int
    non_graphical: bool
    project_name: str
    design_name: str

    def as_manifest(self) -> dict[str, Any]:
        return asdict(self)


def normalize_aedt_version(value: object) -> str:
    """Converte variantes usuais de versão para ``YYYY.R``."""

    text = str(value or "").strip().lower().replace(",", ".")
    if not text:
        return ""
    token = re.search(r"(?<!\d)(\d{3})(?!\d)", text)
    if token:
        raw = token.group(1)
        return f"20{raw[:2]}.{int(raw[2])}"
    year_release = re.search(r"(20\d{2})\s*(?:r|\.|\s)\s*(\d+)", text)
    if year_release:
        return f"{int(year_release.group(1))}.{int(year_release.group(2))}"
    dotted = re.fullmatch(r"(20\d{2})\.(\d+)", text)
    if dotted:
        return f"{int(dotted.group(1))}.{int(dotted.group(2))}"
    return text


def import_hfss_class() -> type[Any]:
    """Importa ``ansys.aedt.core.Hfss`` sob demanda."""

    errors: list[str] = []
    try:
        from ansys.aedt.core import Hfss  # type: ignore

        return Hfss
    except Exception as exc:  # pragma: no cover - depende do runtime externo
        errors.append(f"ansys.aedt.core: {type(exc).__name__}: {exc}")
    try:
        from pyaedt import Hfss  # type: ignore

        return Hfss
    except Exception as exc:  # pragma: no cover - fallback legado
        errors.append(f"pyaedt: {type(exc).__name__}: {exc}")
    raise AedtRuntimeError(
        "PyAEDT não está disponível. Instale o ambiente AEDT 2024 R2 definido "
        "em requirements-aedt-2024.2.txt. Detalhes: " + " | ".join(errors)
    )


def detect_runtime_identity(app: Any, spec: AedtRuntimeSpec) -> AedtRuntimeIdentity:
    """Extrai e valida a identidade real da sessão conectada."""

    detected = ""
    desktop_class = getattr(app, "desktop_class", None)
    for candidate in (
        getattr(desktop_class, "aedt_version_id", None),
        getattr(app, "aedt_version_id", None),
    ):
        normalized = normalize_aedt_version(candidate)
        if normalized:
            detected = normalized
            break
    if not detected:
        try:  # pragma: no cover - requer AEDT
            detected = normalize_aedt_version(app.odesktop.GetVersion())
        except Exception as exc:  # pragma: no cover
            raise AedtRuntimeError("não foi possível consultar a versão do AEDT") from exc

    if spec.strict_version and detected != AEDT_VERSION:
        raise AedtRuntimeError(
            f"sessão incompatível: solicitado {AEDT_VERSION}, conectado {detected}"
        )

    process_id = None
    for candidate in (
        getattr(desktop_class, "aedt_process_id", None),
        getattr(app, "aedt_process_id", None),
    ):
        try:
            value = int(candidate or 0)
        except (TypeError, ValueError):
            value = 0
        if value > 0:
            process_id = value
            break

    port = 0
    for candidate in (
        getattr(desktop_class, "port", None),
        getattr(app, "port", None),
        spec.port,
    ):
        try:
            value = int(candidate or 0)
        except (TypeError, ValueError):
            value = 0
        if value > 0:
            port = value
            break

    return AedtRuntimeIdentity(
        requested_version=AEDT_VERSION,
        detected_version=detected,
        process_id=process_id,
        port=port,
        non_graphical=spec.non_graphical,
        project_name=str(getattr(app, "project_name", "") or ""),
        design_name=str(getattr(app, "design_name", "") or ""),
    )
