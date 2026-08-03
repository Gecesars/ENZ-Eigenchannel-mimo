"""Configura cortes, plots de campo e relatórios do artigo no HFSS.

O script não executa estudos paramétricos nem resolve o modelo. Ele somente
materializa no projeto AEDT os objetos declarados em ``posprocessamento``.
"""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path
from typing import Any

from enz_eigenchannel_mimo.aedt.runtime import (
    AedtRuntimeSpec,
    capturar_runtime_app,
    preflight_aedt,
)
from enz_eigenchannel_mimo.specifications import EspecificacaoGeometrica

PLANOS_AEDT = {"XY": "XY", "YZ": "YZ", "ZX": "XZ"}


def _arquivo_nao_vazio(caminho: Path) -> bool:
    return caminho.is_file() and caminho.stat().st_size > 0


def _nomes_solucoes(app: Any) -> set[str]:
    return {str(nome) for nome in app.existing_analysis_sweeps}


def _tem_solucao(app: Any, nome: str) -> bool:
    return nome in _nomes_solucoes(app)


def _normalizar_variacoes(dados: dict[str, Any] | None) -> dict[str, list[str]]:
    variacoes: dict[str, list[str]] = {}
    for nome, valores in (dados or {}).items():
        if isinstance(valores, list):
            variacoes[nome] = [str(valor) for valor in valores]
        else:
            variacoes[nome] = [str(valores)]
    return variacoes


def configurar_ambiente(
    app: Any,
    spec: EspecificacaoGeometrica,
    *,
    exportar_para: Path | None = None,
    exportar_imagens_campo: bool = True,
) -> dict[str, Any]:
    """Materializa o ambiente declarativo e retorna um manifesto auditável."""
    dados = spec.dados.get("posprocessamento")
    if not dados:
        raise ValueError("a especificação não declara posprocessamento")

    resultado: dict[str, Any] = {
        "schema": "enz-eigenchannel-mimo/aedt-postprocessing/v1",
        "classificacao": "SIMULADO",
        "modelo": spec.modelo,
        "especificacao": {
            "path": str(spec.caminho),
            "sha256": spec.sha256,
        },
        "solucoes_disponiveis": sorted(_nomes_solucoes(app)),
        "criados": {
            "cortes": [],
            "plots_campo": [],
            "relatorios": [],
            "estudos_parametricos": [],
        },
        "existentes": {
            "cortes": [],
            "plots_campo": [],
            "relatorios": [],
            "estudos_parametricos": [],
        },
        "pendentes_sem_solucao": {"plots_campo": [], "relatorios": []},
        "exportados": [],
        "erros": [],
    }

    nomes_cs = {str(cs.name) for cs in app.modeler.coordinate_systems}
    cortes_por_nome: dict[str, dict[str, Any]] = {}
    for corte in dados["cortes"]:
        nome = corte["nome"]
        cortes_por_nome[nome] = dict(corte)
        try:
            if nome in nomes_cs:
                resultado["existentes"]["cortes"].append(nome)
                continue
            cs = app.modeler.create_coordinate_system(
                origin=list(corte["origem"]),
                reference_cs="Global",
                name=nome,
                mode="axis",
                x_pointing=[1, 0, 0],
                y_pointing=[0, 1, 0],
            )
            if not cs:
                raise RuntimeError("AEDT não criou o sistema de coordenadas")
            resultado["criados"]["cortes"].append(nome)
            nomes_cs.add(nome)
        except BaseException:  # noqa: BLE001 -- registrar erro heterogêneo do AEDT
            resultado["erros"].append(
                {"tipo": "corte", "nome": nome, "traceback": traceback.format_exc()}
            )

    nomes_parametricos = {str(setup.name) for setup in app.parametrics.setups}
    for estudo in dados["estudos_parametricos"]:
        nome = estudo["nome"]
        try:
            if nome in nomes_parametricos:
                resultado["existentes"]["estudos_parametricos"].append(nome)
                continue
            setup = app.parametrics.add(
                variable=estudo["variavel"],
                start_point=estudo["inicio"],
                end_point=estudo["fim"],
                step=estudo["passo"],
                variation_type=estudo["tipo"],
                solution=estudo["solucao"],
                name=nome,
            )
            if not setup:
                raise RuntimeError("AEDT não criou o estudo paramétrico")
            resultado["criados"]["estudos_parametricos"].append(nome)
            nomes_parametricos.add(nome)
        except BaseException:  # noqa: BLE001 -- registrar erro heterogêneo do AEDT
            resultado["erros"].append(
                {
                    "tipo": "estudo_parametrico",
                    "nome": nome,
                    "traceback": traceback.format_exc(),
                }
            )

    nomes_relatorios = {str(nome) for nome in app.post.all_report_names}
    for relatorio in dados["relatorios"]:
        nome = relatorio["nome"]
        try:
            parametros_antena = relatorio["categoria"] == "Antenna Parameters"
            if nome in nomes_relatorios and parametros_antena:
                if not app.post.delete_report(nome):
                    raise RuntimeError("AEDT não removeu o relatório incompleto")
                nomes_relatorios.remove(nome)
            if nome in nomes_relatorios:
                resultado["existentes"]["relatorios"].append(nome)
                continue
            if not _tem_solucao(app, relatorio["solucao"]):
                resultado["pendentes_sem_solucao"]["relatorios"].append(nome)
                continue
            if parametros_antena:
                objeto_relatorio = app.post.reports_by_category.antenna_parameters(
                    expressions=list(relatorio["expressoes"]),
                    setup=relatorio["solucao"],
                    infinite_sphere=relatorio.get("contexto"),
                )
                if not objeto_relatorio:
                    raise RuntimeError("template Antenna Parameters indisponível")
                objeto_relatorio.report_type = relatorio["tipo"]
                objeto_relatorio.domain = relatorio.get("dominio", "Sweep")
                objeto_relatorio.primary_sweep = relatorio["sweep_primario"]
                objeto_relatorio.variations.update(
                    _normalizar_variacoes(relatorio.get("variacoes"))
                )
                criado = objeto_relatorio.create(nome)
            else:
                criado = app.post.create_report(
                    expressions=list(relatorio["expressoes"]),
                    setup_sweep_name=relatorio["solucao"],
                    domain=relatorio.get("dominio", "Sweep"),
                    variations=_normalizar_variacoes(relatorio.get("variacoes")),
                    primary_sweep_variable=relatorio["sweep_primario"],
                    secondary_sweep_variable=relatorio.get("sweep_secundario"),
                    report_category=relatorio["categoria"],
                    plot_type=relatorio["tipo"],
                    context=relatorio.get("contexto"),
                    plot_name=nome,
                    show=False,
                )
            if not criado:
                raise RuntimeError("AEDT não criou o relatório")
            resultado["criados"]["relatorios"].append(nome)
            nomes_relatorios.add(nome)
        except BaseException:  # noqa: BLE001 -- registrar erro heterogêneo do AEDT
            resultado["erros"].append(
                {
                    "tipo": "relatorio",
                    "nome": nome,
                    "traceback": traceback.format_exc(),
                }
            )

    nomes_plots = {str(nome) for nome in app.post.field_plots}
    for plot in dados["plots_campo"]:
        nome = plot["nome"]
        try:
            if nome in nomes_plots:
                resultado["existentes"]["plots_campo"].append(nome)
                continue
            corte = cortes_por_nome[plot["corte"]]
            etapa = spec.etapa("M4")
            setup_adaptativo = f"{etapa['setup']['nome']} : LastAdaptive"
            if not _tem_solucao(app, setup_adaptativo):
                resultado["pendentes_sem_solucao"]["plots_campo"].append(nome)
                continue
            plano = PLANOS_AEDT[corte["plano"]]
            criado = app.post.create_fieldplot_cutplane(
                assignment=f"{corte['nome']}:{plano}",
                quantity=plot["quantidade"],
                setup=setup_adaptativo,
                intrinsics={"Freq": plot["frequencia"], "Phase": plot["fase"]},
                plot_name=nome,
                filter_objects=corte.get("objetos_filtro"),
            )
            if not criado:
                raise RuntimeError("AEDT não criou o plot de campo")
            resultado["criados"]["plots_campo"].append(nome)
            nomes_plots.add(nome)
        except BaseException:  # noqa: BLE001 -- registrar erro heterogêneo do AEDT
            resultado["erros"].append(
                {
                    "tipo": "plot_campo",
                    "nome": nome,
                    "traceback": traceback.format_exc(),
                }
            )

    if not app.save_project():
        resultado["erros"].append(
            {"tipo": "salvamento", "nome": app.project_name, "traceback": ""}
        )

    if exportar_para is not None and not resultado["erros"]:
        exportar_para.mkdir(parents=True, exist_ok=True)
        for nome in sorted(nomes_relatorios):
            csv = Path(app.post.export_report_to_csv(str(exportar_para), nome))
            imagem = exportar_para / f"{nome}.jpg"
            if not app.post.export_report_to_jpg(str(imagem), nome, 1600, 900):
                raise RuntimeError(f"falha ao exportar imagem do relatório {nome}")
            if not _arquivo_nao_vazio(csv):
                raise RuntimeError(f"CSV ausente ou vazio para o relatório {nome}")
            if not _arquivo_nao_vazio(imagem):
                raise RuntimeError(f"imagem ausente ou vazia para o relatório {nome}")
            resultado["exportados"].extend([str(csv), str(imagem)])
        if exportar_imagens_campo:
            for nome, field_plot in app.post.field_plots.items():
                imagem = exportar_para / f"{nome}.jpg"
                if not app.post.export_field_jpg(
                    str(imagem),
                    nome,
                    field_plot.plot_folder,
                    width=1600,
                    height=900,
                    display_wireframe=True,
                ):
                    raise RuntimeError(f"falha ao exportar imagem do campo {nome}")
                if not _arquivo_nao_vazio(imagem):
                    raise RuntimeError(f"imagem de campo ausente ou vazia para {nome}")
                resultado["exportados"].append(str(imagem))

    if resultado["erros"]:
        tipos = ", ".join(
            f"{erro['tipo']}:{erro['nome']}" for erro in resultado["erros"]
        )
        raise RuntimeError(f"falhas explícitas na configuração: {tipos}")
    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("especificacao", type=Path)
    parser.add_argument("projeto", type=Path)
    parser.add_argument("--porta-grpc", type=int, default=0)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--manifesto", type=Path, required=True)
    parser.add_argument("--nao-grafico", action="store_true")
    parser.add_argument("--deixar-aedt-aberto", action="store_true")
    parser.add_argument("--nao-exportar-imagens-campo", action="store_true")
    args = parser.parse_args()

    spec = EspecificacaoGeometrica.carregar(args.especificacao)
    runtime = AedtRuntimeSpec(non_graphical=args.nao_grafico, port=args.porta_grpc)
    preflight = preflight_aedt(runtime)
    app: Any | None = None
    sessao_nova = args.porta_grpc == 0
    try:
        from ansys.aedt.core import Hfss

        app = Hfss(
            project=str(args.projeto.resolve()),
            version=runtime.version,
            non_graphical=runtime.non_graphical,
            new_desktop=sessao_nova,
            close_on_exit=False,
            port=runtime.port,
            remove_lock=False,
        )
        dados = configurar_ambiente(
            app,
            spec,
            exportar_para=args.saida,
            exportar_imagens_campo=not args.nao_exportar_imagens_campo,
        )
        dados["runtime"] = {
            **capturar_runtime_app(app, runtime),
            "pyaedt": preflight.pyaedt_version,
            "license": preflight.license_status,
            "cores_configurados_solve": 14,
        }
        args.manifesto.parent.mkdir(parents=True, exist_ok=True)
        args.manifesto.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        return 0
    finally:
        if app is not None:
            fechar = sessao_nova and not args.deixar_aedt_aberto
            app.release_desktop(close_projects=fechar, close_desktop=fechar)


if __name__ == "__main__":
    raise SystemExit(main())
