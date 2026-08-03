from __future__ import annotations

import csv
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .builder import ErroConstrucaoAedt, ResultadoConstrucao


def _arquivo_nao_vazio(caminho: Path) -> bool:
    return caminho.is_file() and caminho.stat().st_size > 0


def _exigir_convergencia(caminho: Path) -> None:
    if not _arquivo_nao_vazio(caminho):
        raise ErroConstrucaoAedt("relatório de convergência não foi exportado")
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    if not re.search(
        r"^\s*Converged\s*:\s*Yes\s*$", texto, re.IGNORECASE | re.MULTILINE
    ):
        raise ErroConstrucaoAedt(
            "setup não declarou convergência no relatório exportado"
        )


def _escalar_solucao(dados: Any, expressao: str) -> float:
    if not dados:
        raise ErroConstrucaoAedt(f"AEDT não retornou dados para {expressao}")
    try:
        valor = float(dados.get_expression_data()[1][0])
    except (AttributeError, IndexError, TypeError, ValueError) as exc:
        raise ErroConstrucaoAedt(f"resposta inválida ao extrair {expressao}") from exc
    if not math.isfinite(valor):
        raise ErroConstrucaoAedt(f"valor não finito em {expressao}")
    return valor


def _exportar_eigenmodes(app: Any, caminho: Path, num_modes: int) -> None:
    # Fluxo recomendado pelo exemplo oficial Eigenmode do PyAEDT: descobrir as
    # expressões do próprio AEDT e consultar cada valor pela categoria Eigenmode.
    q_nomes = list(app.post.available_report_quantities(quantities_category="Eigen Q"))
    f_nomes = list(
        app.post.available_report_quantities(quantities_category="Eigen Modes")
    )
    if len(q_nomes) < num_modes or len(f_nomes) < num_modes:
        raise ErroConstrucaoAedt(
            f"AEDT expôs {len(f_nomes)} frequências e {len(q_nomes)} fatores Q; "
            f"esperados {num_modes}"
        )

    linhas: list[tuple[int, float, float, str, str]] = []
    for modo, (q_nome, f_nome) in enumerate(
        zip(q_nomes[:num_modes], f_nomes[:num_modes], strict=True), start=1
    ):
        q_dados = app.post.get_solution_data(
            expressions=q_nome, report_category="Eigenmode"
        )
        f_dados = app.post.get_solution_data(
            expressions=f_nome, report_category="Eigenmode"
        )
        q_fator = _escalar_solucao(q_dados, q_nome)
        frequencia_hz = _escalar_solucao(f_dados, f_nome)
        if q_fator < 0 or frequencia_hz <= 0:
            raise ErroConstrucaoAedt(
                f"modo {modo} retornou frequência/Q fisicamente inválidos"
            )
        linhas.append((modo, frequencia_hz, q_fator, f_nome, q_nome))

    if len({round(linha[1], 6) for linha in linhas}) != num_modes:
        raise ErroConstrucaoAedt("frequências modais retornadas não são distintas")
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            [
                "mode",
                "frequency_hz",
                "q_factor",
                "frequency_expression",
                "q_expression",
            ]
        )
        escritor.writerows(linhas)


def exportar_resultados(
    app: Any,
    etapa: Mapping[str, Any],
    construcao: ResultadoConstrucao,
    diretorio_run: Path,
) -> list[Path]:
    artefatos: list[Path] = []
    setup = construcao.setup_name

    convergence = diretorio_run / "metrics" / "convergence.csv"
    mesh = diretorio_run / "metrics" / "mesh_stats.csv"
    profile = diretorio_run / "metrics" / "solver_profile.csv"
    for metodo, destino, obrigatorio in (
        (app.export_convergence, convergence, True),
        (app.export_mesh_stats, mesh, True),
        (app.export_profile, profile, False),
    ):
        resultado = metodo(setup, output_file=str(destino))
        if resultado and _arquivo_nao_vazio(destino):
            artefatos.append(destino)
        elif obrigatorio:
            raise ErroConstrucaoAedt(
                f"artefato obrigatório ausente ou vazio: {destino.name}"
            )
    _exigir_convergencia(convergence)

    preview = diretorio_run / "plots" / "design.jpg"
    if app.export_design_preview_to_jpg(preview) and _arquivo_nao_vazio(preview):
        artefatos.append(preview)

    if etapa["solucao"] == "Eigenmode":
        num_modes = int(etapa["setup"]["propriedades"].get("NumModes", 1))
        eigen_csv = diretorio_run / "metrics" / "eigenmodes.csv"
        _exportar_eigenmodes(app, eigen_csv, num_modes)
        if not _arquivo_nao_vazio(eigen_csv):
            raise ErroConstrucaoAedt("falha ao exportar frequências e fatores Q")
        artefatos.append(eigen_csv)
        return artefatos

    excitacoes = list(app.excitation_names)
    if not excitacoes:
        raise ErroConstrucaoAedt(
            "nenhuma excitação disponível para exportar Touchstone"
        )
    touchstone = diretorio_run / "network" / f"sparameters.s{len(excitacoes)}p"
    exportado = app.export_touchstone(setup=setup, output_file=str(touchstone))
    if not exportado:
        raise ErroConstrucaoAedt("falha ao exportar Touchstone")
    caminho_touchstone = Path(exportado) if isinstance(exportado, str) else touchstone
    if caminho_touchstone.is_file():
        artefatos.append(caminho_touchstone)

    if construcao.sphere_name and etapa.get("frequencias_exportacao_hz"):
        farfield_dir = diretorio_run / "farfield"
        sucesso = app.export_antenna_metadata(
            frequencies=etapa["frequencias_exportacao_hz"],
            setup=f"{setup} : LastAdaptive",
            sphere=construcao.sphere_name,
            output_dir=str(farfield_dir),
            variations={},
            export_element_pattern=True,
            export_objects=False,
            export_touchstone=True,
            export_power=True,
        )
        if not sucesso:
            raise ErroConstrucaoAedt("falha ao exportar padrões embarcados complexos")
        artefatos.extend(
            caminho for caminho in farfield_dir.rglob("*") if caminho.is_file()
        )

    return artefatos
