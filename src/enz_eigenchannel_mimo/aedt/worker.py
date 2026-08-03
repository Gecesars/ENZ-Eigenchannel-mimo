from __future__ import annotations

import shutil
import subprocess
import time
import traceback
from pathlib import Path
from typing import Any

from ..manifests import ManifestoExecucao, StatusExecucao
from ..specifications import EspecificacaoGeometrica
from .builder import ConstrutorDeclarativoAedt
from .exports import exportar_resultados
from .runtime import AedtRuntimeSpec, capturar_runtime_app, preflight_aedt


def _repo_root(caminho: Path) -> Path:
    texto = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=caminho.parent,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return Path(texto).resolve()


def _preparar_diretorios(run_dir: Path) -> None:
    for nome in (
        "input",
        "aedt",
        "network",
        "fields",
        "farfield",
        "metrics",
        "plots",
        "logs",
    ):
        (run_dir / nome).mkdir(exist_ok=False)


def _processo_existe(pid: int | None) -> bool | None:
    if pid is None:
        return None
    try:
        import psutil
    except ImportError:
        return None
    return psutil.pid_exists(pid)


def _aguardar_encerramento(pid: int | None, timeout_s: float = 10.0) -> bool | None:
    estado = _processo_existe(pid)
    if estado is None:
        return None
    limite = time.monotonic() + timeout_s
    while estado and time.monotonic() < limite:
        time.sleep(0.25)
        estado = bool(_processo_existe(pid))
    return estado


def _exportar_mensagens_aedt(app: Any, destino: Path) -> Path:
    mensagens = [
        str(mensagem) for mensagem in app.desktop_class.odesktop.GetMessages("", "", 0)
    ]
    if not mensagens:
        mensagens = ["AEDT não retornou mensagens para esta sessão."]
    destino.write_text("\n".join(mensagens) + "\n", encoding="utf-8")
    return destino


def executar_worker(
    especificacao: str | Path,
    etapa: str,
    base_runs: str | Path,
    *,
    solve: bool,
    non_graphical: bool = True,
    cores: int = 14,
) -> Path:
    """Executa uma única sessão AEDT pertencente ao processo worker atual."""
    spec = EspecificacaoGeometrica.carregar(especificacao)
    spec.exigir_pronta(etapa)
    repo_root = _repo_root(spec.caminho)
    base = Path(base_runs).resolve()
    base.mkdir(parents=True, exist_ok=True)
    runtime = AedtRuntimeSpec(non_graphical=non_graphical, cores=cores)
    manifesto = ManifestoExecucao.criar(
        base,
        spec,
        etapa,
        solve,
        repo_root,
        cores=runtime.cores,
        tasks=runtime.tasks,
        gpus=runtime.gpus,
    )
    run_dir = manifesto.caminho.parent
    _preparar_diretorios(run_dir)
    spec_copiada = run_dir / "input" / spec.caminho.name
    shutil.copy2(spec.caminho, spec_copiada)
    manifesto.registrar_artefatos([spec_copiada], run_dir)

    app: Any | None = None
    pid: int | None = None
    sucesso = False
    try:
        manifesto.atualizar_status(StatusExecucao.PREFLIGHT)
        preflight = preflight_aedt(runtime)
        manifesto.dados["runtime"]["pyaedt"] = preflight.pyaedt_version
        manifesto.dados["runtime"]["license"] = preflight.license_status
        manifesto.salvar()

        manifesto.atualizar_status(StatusExecucao.CONNECTING)
        from ansys.aedt.core import Hfss
        from ansys.aedt.core.generic.settings import settings

        settings.enable_screen_logs = False
        settings.enable_file_logs = False
        settings.enable_global_log_file = False

        project_file = run_dir / "aedt" / f"{spec.modelo}_{etapa}.aedt"
        design_name = f"HFSS_ENZ_{spec.modelo}_{etapa}"
        solution_type = (
            "Modal" if spec.etapa(etapa)["solucao"] == "DrivenModal" else "Eigenmode"
        )
        app = Hfss(
            project=str(project_file),
            design=design_name,
            solution_type=solution_type,
            version=runtime.version,
            non_graphical=runtime.non_graphical,
            new_desktop=runtime.new_desktop,
            close_on_exit=runtime.close_on_exit,
            machine=runtime.machine,
            port=runtime.port,
            aedt_process_id=runtime.process_id,
            remove_lock=False,
        )
        info_runtime = capturar_runtime_app(app, runtime)
        pid = info_runtime["pid"]
        manifesto.dados["runtime"].update(info_runtime)
        manifesto.salvar()

        manifesto.atualizar_status(StatusExecucao.BUILDING)
        construcao = ConstrutorDeclarativoAedt(app).construir(spec, etapa)

        if not app.save_project(project_file):
            raise RuntimeError("AEDT não salvou o projeto antes da validação/solução")
        manifesto.registrar_artefatos([project_file], run_dir)

        manifesto.atualizar_status(StatusExecucao.VALIDATING_GEOMETRY)
        validation_log = run_dir / "logs" / "validation.log"
        validacao = app.validate_simple(validation_log)
        if validation_log.is_file():
            mensagens = validation_log.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
            manifesto.dados["solver"]["validation_messages"] = mensagens
            manifesto.registrar_artefatos([validation_log], run_dir)
        if validacao != 1:
            raise RuntimeError("ValidateDesign falhou; consulte validation.log")

        if not solve:
            aedt_log = _exportar_mensagens_aedt(
                app, run_dir / "logs" / "aedt_messages.log"
            )
            manifesto.registrar_artefatos([aedt_log], run_dir)
            manifesto.atualizar_status(StatusExecucao.BUILT)
            sucesso = True
            return run_dir

        manifesto.atualizar_status(StatusExecucao.MESHING)
        manifesto.atualizar_status(StatusExecucao.SOLVING)
        if not app.analyze_setup(
            construcao.setup_name,
            cores=runtime.cores,
            tasks=runtime.tasks,
            gpus=runtime.gpus,
            blocking=True,
        ):
            raise RuntimeError(f"solve falhou no setup {construcao.setup_name}")

        manifesto.atualizar_status(StatusExecucao.POSTPROCESSING)
        manifesto.atualizar_status(StatusExecucao.EXPORTING)
        artefatos = exportar_resultados(app, spec.etapa(etapa), construcao, run_dir)
        artefatos.append(
            _exportar_mensagens_aedt(app, run_dir / "logs" / "aedt_messages.log")
        )
        if not app.save_project(project_file):
            raise RuntimeError("AEDT não salvou o projeto solucionado")
        artefatos.append(project_file)
        manifesto.registrar_artefatos(artefatos, run_dir)
        sucesso = True
        return run_dir
    except BaseException:
        manifesto.registrar_erro(traceback.format_exc())
        raise
    finally:
        sucesso_antes_encerrar = sucesso
        erro_encerramento: str | None = None
        if app is not None:
            try:
                app.release_desktop(close_projects=True, close_desktop=True)
            except BaseException:  # noqa: BLE001 -- encerramento deve registrar até interrupção
                erro_encerramento = "falha ao encerrar AEDT:\n" + traceback.format_exc()
                manifesto.dados["errors"].append(erro_encerramento)
                sucesso = False
        orfao = _aguardar_encerramento(pid)
        manifesto.dados["runtime"]["orphan_after_close"] = orfao
        if pid is not None and orfao is not False:
            erro_encerramento = (
                f"teste de encerramento inconclusivo ou falho: PID {pid}, "
                f"orphan_after_close={orfao!r}"
            )
            manifesto.dados["errors"].append(erro_encerramento)
            sucesso = False
        logs = [
            caminho for caminho in (run_dir / "logs").rglob("*") if caminho.is_file()
        ]
        manifesto.registrar_artefatos(logs, run_dir)
        if sucesso:
            if solve:
                manifesto.atualizar_status(StatusExecucao.COMPLETED)
            else:
                manifesto.atualizar_status(StatusExecucao.BUILT)
        elif manifesto.dados["status"] != StatusExecucao.FAILED.value:
            manifesto.atualizar_status(StatusExecucao.FAILED)
        if sucesso_antes_encerrar and erro_encerramento is not None:
            raise RuntimeError(erro_encerramento)
