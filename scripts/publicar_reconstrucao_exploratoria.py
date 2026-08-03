"""Publica uma reconstrução HFSS exploratória sem promovê-la a reprodução."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


def sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _carregar_json(caminho: Path) -> dict[str, Any]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if not isinstance(dados, dict):
        raise TypeError(f"JSON não é objeto: {caminho}")
    return dados


def _validar_run_imutavel(run: Path) -> dict[str, Any]:
    manifesto = _carregar_json(run / "manifest.json")
    if manifesto["status"] != "COMPLETED" or manifesto["errors"]:
        raise ValueError("run limpo não está COMPLETED ou contém erros")
    runtime = manifesto["runtime"]
    solver = manifesto["solver"]
    if not (
        runtime["requested_aedt"] == "2024.2"
        and runtime["strict_version"] is True
        and str(runtime["build"]).startswith("2024.2.")
        and runtime["pyaedt"] == "1.3.0"
        and runtime["orphan_after_close"] is False
        and solver["cores"] == 14
        and solver["tasks"] == 1
        and solver["gpus"] == 0
        and solver["solve_requested"] is True
    ):
        raise ValueError("gates de runtime/solver do run limpo falharam")
    for artefato in manifesto["artifacts"]:
        caminho = run / artefato["path"]
        if not caminho.is_file():
            raise FileNotFoundError(caminho)
        if caminho.stat().st_size != artefato["bytes"]:
            raise ValueError(f"tamanho divergente: {caminho}")
        if sha256(caminho) != artefato["sha256"]:
            raise ValueError(f"hash divergente: {caminho}")
    return manifesto


def _contagem_ambiente(dados: dict[str, Any], categoria: str) -> int:
    return len(dados["criados"][categoria]) + len(dados["existentes"][categoria])


def publicar(
    raiz: Path,
    run_limpo: Path,
    projeto_configurado: Path,
    especificacao: Path,
    manifesto_pos: Path,
    validacao: Path,
    relatorios: Path,
    destino: Path,
) -> dict[str, Any]:
    raiz = raiz.resolve()
    run_limpo = run_limpo.resolve()
    projeto_configurado = projeto_configurado.resolve()
    especificacao = especificacao.resolve()
    manifesto_pos = manifesto_pos.resolve()
    validacao = validacao.resolve()
    relatorios = relatorios.resolve()
    destino = destino.resolve()
    permitido = (raiz / "poros_aedt" / "reconstrucoes_exploratorias").resolve()
    if destino.parent != permitido:
        raise ValueError(f"destino deve ser filho direto de {permitido}")
    if destino.exists():
        raise FileExistsError(destino)

    manifesto_run = _validar_run_imutavel(run_limpo)
    pos = _carregar_json(manifesto_pos)
    validacao_dados = _carregar_json(validacao)
    if pos["erros"] or pos["pendentes_sem_solucao"]["plots_campo"]:
        raise ValueError("ambiente de pós-processamento contém falha ou pendência")
    esperado = {
        "cortes": 8,
        "plots_campo": 8,
        "relatorios": 8,
        "estudos_parametricos": 3,
    }
    observado = {nome: _contagem_ambiente(pos, nome) for nome in esperado}
    if observado != esperado:
        raise ValueError(f"contagens de pós-processamento divergentes: {observado}")
    if validacao_dados["classificacao_global"] != "HIPÓTESE":
        raise ValueError("reconstrução deve permanecer classificada como HIPÓTESE")
    if not projeto_configurado.is_file() or not relatorios.is_dir():
        raise FileNotFoundError("projeto configurado ou relatórios ausentes")

    destino.mkdir(parents=True)
    pasta_projeto = destino / "projeto_configurado"
    pasta_run = destino / "run_limpo"
    pasta_pos = destino / "posprocessamento"
    pasta_projeto.mkdir()
    pasta_run.mkdir()
    pasta_pos.mkdir()

    shutil.copy2(especificacao, destino / especificacao.name)
    shutil.copy2(projeto_configurado, pasta_projeto / projeto_configurado.name)
    projeto_limpo_rel = next(
        Path(item["path"])
        for item in manifesto_run["artifacts"]
        if item["path"].endswith(".aedt")
    )
    resultados = (run_limpo / projeto_limpo_rel).with_name(
        projeto_limpo_rel.name + "results"
    )
    if not resultados.is_dir():
        raise FileNotFoundError(resultados)
    shutil.copytree(
        resultados,
        pasta_projeto / resultados.name,
        ignore=shutil.ignore_patterns("*.lock", "*.semaphore"),
    )

    for nome in ("manifest.json",):
        shutil.copy2(run_limpo / nome, pasta_run / nome)
    for subpasta in ("input", "logs", "metrics", "network"):
        shutil.copytree(run_limpo / subpasta, pasta_run / subpasta)
    shutil.copy2(manifesto_pos, pasta_pos / manifesto_pos.name)
    shutil.copy2(validacao, pasta_pos / validacao.name)
    shutil.copytree(relatorios, pasta_pos / "relatorios_artigo")
    documento = raiz / "docs" / "35_waveport_z_e_ambiente_de_plots.md"
    shutil.copy2(documento, destino / documento.name)

    readme = destino / "README.md"
    readme.write_text(
        "# G0 Figura 2 v7 — reconstrução exploratória\n\n"
        "**HIPÓTESE:** este pacote não é uma reprodução validada do artigo. "
        "Ele contém a waveport corrigida em Z, o projeto HFSS configurado, "
        "resultados complexos, relatórios e evidências de execução.\n\n"
        "**SIMULADO:** o run limpo foi executado no AEDT 2024 R2 com 14 cores "
        f"e está em `run_limpo/` ({manifesto_run['run_id']}).\n\n"
        "**SIMULADO:** o gate estrito de passividade falhou em 25,87 GHz: "
        "a potência radiada excedeu a aceita em 2,16235%. Consulte "
        "`posprocessamento/validacao_cientifica_exploratoria.json`.\n\n"
        "Os dados medidos e os CADs dos Modelos I–IX não estão disponíveis e "
        "não foram inventados. O PDF primário permanece em "
        "`../../evidencias/VilasBoas_2026_OJAP_FlatTop.pdf`.\n",
        encoding="utf-8",
    )

    arquivos = []
    for caminho in sorted(p for p in destino.rglob("*") if p.is_file()):
        arquivos.append(
            {
                "path": caminho.relative_to(destino).as_posix(),
                "sha256": sha256(caminho),
                "bytes": caminho.stat().st_size,
            }
        )
    pacote = {
        "schema": "enz-eigenchannel-mimo/exploratory-package/v1",
        "classificacao": "HIPÓTESE",
        "run_limpo": manifesto_run["run_id"],
        "run_limpo_artifacts_verified": True,
        "postprocessing_counts": observado,
        "strict_passivity_gate": "FAIL",
        "files": arquivos,
    }
    (destino / "manifest.json").write_text(
        json.dumps(pacote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return pacote


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-limpo", type=Path, required=True)
    parser.add_argument("--projeto-configurado", type=Path, required=True)
    parser.add_argument("--especificacao", type=Path, required=True)
    parser.add_argument("--manifesto-pos", type=Path, required=True)
    parser.add_argument("--validacao", type=Path, required=True)
    parser.add_argument("--relatorios", type=Path, required=True)
    parser.add_argument("--destino", type=Path, required=True)
    parser.add_argument(
        "--raiz", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    pacote = publicar(
        args.raiz,
        args.run_limpo,
        args.projeto_configurado,
        args.especificacao,
        args.manifesto_pos,
        args.validacao,
        args.relatorios,
        args.destino,
    )
    print(json.dumps(pacote, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
