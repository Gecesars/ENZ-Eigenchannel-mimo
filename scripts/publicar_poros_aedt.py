"""Publica em ``poros_aedt`` somente um run aprovado pelos gates cientificos."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from enz_eigenchannel_mimo.article_validation import C0_M_S


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _valor_parametro(spec: dict[str, Any], nome: str) -> float:
    return float(spec["parametros"][nome]["valor"])


def _validar_run(run: Path) -> dict[str, Any]:
    manifesto = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifesto["status"] != "COMPLETED" or manifesto["errors"]:
        raise ValueError("run nao esta COMPLETED ou contem erros")
    runtime = manifesto["runtime"]
    solver = manifesto["solver"]
    gates_booleanos = {
        "aedt_2024r2_estrito": runtime["requested_aedt"] == "2024.2"
        and runtime["strict_version"] is True
        and str(runtime["build"]).startswith("2024.2."),
        "pyaedt_1p3p0": runtime["pyaedt"] == "1.3.0",
        "grpc_nativo": runtime["transport"] == "native AEDT gRPC via PyAEDT",
        "licenca_disponivel": str(runtime["license"]).startswith("DISPONIVEL"),
        "sem_processo_orfao": runtime["orphan_after_close"] is False,
        "recursos_14_1_0": (solver["cores"], solver["tasks"], solver["gpus"])
        == (14, 1, 0),
        "solve_executado": solver["solve_requested"] is True,
    }
    if not all(gates_booleanos.values()):
        raise ValueError(f"gates de runtime falharam: {gates_booleanos}")

    hashes_ok = True
    for artefato in manifesto["artifacts"]:
        caminho = run / artefato["path"]
        hashes_ok &= (
            caminho.is_file()
            and caminho.stat().st_size == artefato["bytes"]
            and sha256(caminho) == artefato["sha256"]
        )
    if not hashes_ok:
        raise ValueError("identidade de artefato divergente do manifesto do run")

    convergencia_texto = (run / "metrics" / "convergence.csv").read_text(
        encoding="utf-8"
    )
    atual = re.search(r"Current\s*:\s*([0-9.]+)", convergencia_texto)
    alvo = re.search(r"Target\s*:\s*([0-9.]+)", convergencia_texto)
    passes = re.search(r"Completed\s*:\s*([0-9]+)", convergencia_texto)
    convergiu = "Converged : Yes" in convergencia_texto
    if not (atual and alvo and passes and convergiu):
        raise ValueError("arquivo de convergencia incompleto")
    delta_atual = float(atual.group(1))
    delta_alvo = float(alvo.group(1))
    if delta_atual > delta_alvo:
        raise ValueError("criterio de convergencia nao atendido")

    malha_texto = (run / "metrics" / "mesh_stats.csv").read_text(encoding="utf-8")
    tets_match = re.search(r"Total number of mesh elements:\s*([0-9]+)", malha_texto)
    if not tets_match or int(tets_match.group(1)) <= 0:
        raise ValueError("estatistica de malha ausente ou vazia")

    spec_path = run / "input" / Path(manifesto["specification"]["path"]).name
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    dimensoes_m = (
        _valor_parametro(spec, "cavidade_comprimento") * 1e-3,
        _valor_parametro(spec, "cavidade_largura") * 1e-3,
        _valor_parametro(spec, "cavidade_altura") * 1e-3,
    )
    indices = ((2, 1, 0), (1, 0, 1), (0, 1, 1), (1, 2, 0))
    esperadas = [
        C0_M_S
        / 2.0
        * math.sqrt(sum((indice / lado) ** 2 for indice, lado in zip(modo, dimensoes_m)))
        for modo in indices
    ]
    with (run / "metrics" / "eigenmodes.csv").open(encoding="utf-8", newline="") as arquivo:
        observadas = [float(linha["frequency_hz"]) for linha in csv.DictReader(arquivo)]
    if len(observadas) != 4 or observadas != sorted(observadas):
        raise ValueError("lista de quatro autovalores ordenados nao encontrada")
    erros_percentuais = [
        abs(observada - esperada) / esperada * 100.0
        for observada, esperada in zip(observadas, esperadas, strict=True)
    ]
    if max(erros_percentuais) > 0.01:
        raise ValueError("autofrequencias divergem mais de 0.01% da cavidade PEC analitica")

    mensagens = (run / "logs" / "aedt_messages.log").read_text(encoding="utf-8")
    if "[error]" in mensagens.lower():
        raise ValueError("log AEDT contem erro")
    avisos = mensagens.lower().count("[warning]")
    return {
        "manifesto": manifesto,
        "gates_booleanos": {**gates_booleanos, "hashes_artefatos": hashes_ok},
        "convergencia": {
            "classificacao": "SIMULADO",
            "passes": int(passes.group(1)),
            "delta_f_percentual": delta_atual,
            "alvo_percentual": delta_alvo,
            "convergiu": convergiu,
        },
        "malha": {
            "classificacao": "SIMULADO",
            "tetraedros": int(tets_match.group(1)),
        },
        "validacao_analitica_modos": {
            "classificacao": "DERIVADO",
            "indices_mnp": [list(modo) for modo in indices],
            "frequencias_esperadas_hz": esperadas,
            "frequencias_simuladas_hz": observadas,
            "erros_percentuais": erros_percentuais,
            "limite_percentual": 0.01,
        },
        "balanco_potencia": {
            "classificacao": "DERIVADO",
            "resultado": "NAO_APLICAVEL",
            "motivo": "M0 e uma cavidade PEC fechada em Eigenmode, sem portas, perdas ou potencia incidente.",
        },
        "avisos_aedt": {
            "quantidade": avisos,
            "explicacao": "Avisos de variavel Phase sem sweep durante exportacao; nenhum erro AEDT.",
        },
    }


def publicar(raiz: Path, run: Path, destino: Path) -> dict[str, Any]:
    raiz = raiz.resolve()
    run = run.resolve()
    destino = destino.resolve()
    if destino.exists():
        raise FileExistsError(f"destino ja existe: {destino}")
    if destino.parent != raiz:
        raise ValueError("por seguranca, poros_aedt deve ser filho direto do repositorio")
    validacao = _validar_run(run)

    pasta_run = destino / "runs" / run.name
    pasta_run.mkdir(parents=True)
    manifesto_run = validacao["manifesto"]
    for artefato in manifesto_run["artifacts"]:
        origem = run / artefato["path"]
        alvo = pasta_run / artefato["path"]
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, alvo)

    projeto = next(
        pasta_run / item["path"]
        for item in manifesto_run["artifacts"]
        if item["path"].endswith(".aedt")
    )
    resultados_origem = run / "aedt" / (projeto.name + "results")
    resultados_alvo = pasta_run / "aedt" / resultados_origem.name
    if resultados_origem.is_dir():
        shutil.copytree(
            resultados_origem,
            resultados_alvo,
            ignore=shutil.ignore_patterns("*.lock", "*.semaphore"),
        )

    evidencias = destino / "evidencias"
    especificacoes = destino / "especificacoes"
    evidencias.mkdir()
    especificacoes.mkdir()
    for origem in (
        raiz / "doc" / "pdfs" / "VilasBoas_2026_OJAP_FlatTop.pdf",
        raiz / "doc" / "pdfs" / "manifest.json",
        raiz / "doc" / "pdfs" / "validacao_numerica_artigo.json",
    ):
        shutil.copy2(origem, evidencias / origem.name)
    for origem in (
        raiz / "modelos" / "especificacoes" / "g0_artigo_base.auditado.v4.yaml",
        raiz / "modelos" / "especificacoes" / "m0_cavidade_retangular_smoke.hipotese.v1.yaml",
    ):
        shutil.copy2(origem, especificacoes / origem.name)

    validacao_path = pasta_run / "metrics" / "validacao_gates.json"
    validacao_path.write_text(
        json.dumps({key: value for key, value in validacao.items() if key != "manifesto"}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    readme = destino / "README.md"
    readme.write_text(
        "# poros_aedt — artefatos aprovados\n\n"
        "**SIMULADO:** este pacote contem um smoke test M0 de cavidade PEC fechada, "
        "executado no AEDT 2024 R2 com 14 cores.\n\n"
        "**HIPÓTESE:** a geometria M0 e sintetica e valida a infraestrutura; ela nao "
        "reproduz a antena do artigo.\n\n"
        "**DESCONHECIDO:** a reproducao fiel permanece bloqueada pelos parametros "
        "listados em `especificacoes/g0_artigo_base.auditado.v4.yaml`.\n\n"
        "O PDF principal e sua validacao numerica estao em `evidencias/`. O projeto "
        "AEDT solucionado, resultados, metricas e logs estao em `runs/`.\n",
        encoding="utf-8",
    )

    inventario = []
    for caminho in sorted(p for p in destino.rglob("*") if p.is_file()):
        inventario.append(
            {
                "path": caminho.relative_to(destino).as_posix(),
                "sha256": sha256(caminho),
                "bytes": caminho.stat().st_size,
            }
        )
    pacote = {
        "schema_version": "poros-aedt-package-v1",
        "classificacao_resultado": "SIMULADO",
        "classificacao_geometria": "HIPÓTESE",
        "run_id": run.name,
        "gates": {key: value for key, value in validacao.items() if key != "manifesto"},
        "arquivos": inventario,
    }
    (destino / "manifest.json").write_text(
        json.dumps(pacote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return pacote


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destino", type=Path, default=Path("poros_aedt"))
    args = parser.parse_args()
    pacote = publicar(args.raiz, args.run, args.destino)
    print(
        json.dumps(
            {"run_id": pacote["run_id"], "arquivos": len(pacote["arquivos"])},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
