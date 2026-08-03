"""Ciclo de vida determinístico de uma sessão HFSS 2024 R2."""

from __future__ import annotations

from pathlib import Path
import threading
from typing import Any

from .runtime import (
    AedtRuntimeIdentity,
    AedtRuntimeSpec,
    detect_runtime_identity,
    import_hfss_class,
)


class Aedt2024R2Session:
    """Context manager para uma única conexão PyAEDT/gRPC.

    O objeto vivo do HFSS nunca deve atravessar IPC nem ser serializado. Um
    worker/processo possui a sessão e devolve apenas DTOs e arquivos.
    """

    def __init__(self, spec: AedtRuntimeSpec | None = None) -> None:
        self.spec = spec or AedtRuntimeSpec()
        self.spec.validate()
        self._app: Any | None = None
        self._identity: AedtRuntimeIdentity | None = None
        self._lock = threading.RLock()

    @property
    def app(self) -> Any:
        if self._app is None:
            raise RuntimeError("sessão AEDT não conectada")
        return self._app

    @property
    def identity(self) -> AedtRuntimeIdentity:
        if self._identity is None:
            raise RuntimeError("identidade AEDT ainda não disponível")
        return self._identity

    @property
    def is_connected(self) -> bool:
        return self._app is not None

    def connect(
        self,
        *,
        project: str | Path,
        design: str,
        solution_type: str,
    ) -> Any:
        with self._lock:
            if self._app is not None:
                return self._app
            project_path = Path(project).expanduser().resolve()
            project_path.parent.mkdir(parents=True, exist_ok=True)
            Hfss = import_hfss_class()
            kwargs = self.spec.pyaedt_kwargs()
            app = Hfss(
                project=str(project_path),
                design=design,
                solution_type=solution_type,
                **kwargs,
            )
            try:
                identity = detect_runtime_identity(app, self.spec)
            except Exception:
                self._release(app, close_owned=self.spec.new_desktop)
                raise
            self._app = app
            self._identity = identity
            return app

    def save(self, project: str | Path | None = None) -> None:
        target = str(Path(project).expanduser().resolve()) if project else None
        if target:
            result = self.app.save_project(target)
        else:
            result = self.app.save_project()
        if result is False:
            raise RuntimeError("AEDT recusou o salvamento do projeto")

    def close(self) -> None:
        with self._lock:
            app = self._app
            self._app = None
            self._identity = None
            if app is None:
                return
            self._release(app, close_owned=self.spec.new_desktop and self.spec.close_on_exit)

    @staticmethod
    def _release(app: Any, *, close_owned: bool) -> None:
        try:
            app.release_desktop(
                close_projects=close_owned,
                close_desktop=close_owned,
            )
            return
        except TypeError:  # compatibilidade com assinaturas PyAEDT anteriores
            pass
        except Exception:
            if not close_owned:
                return
        try:
            app.release_desktop(
                close_projects=close_owned,
                close_on_exit=close_owned,
            )
        except Exception:
            if close_owned:
                try:
                    app.close_project(save_project=False)
                except Exception:
                    pass

    def __enter__(self) -> "Aedt2024R2Session":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
