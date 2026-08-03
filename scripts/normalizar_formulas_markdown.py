#!/usr/bin/env python3
"""Normaliza matemática Markdown para a sintaxe nativa do GitHub.

Política do repositório:
- matemática inline permanece entre ``$...$``;
- matemática de bloco usa cercas `````math``;
- delimitadores isolados ``$$`` e ``\[``/``\]`` são convertidos;
- blocos de código comuns não são alterados;
- delimitadores desbalanceados interrompem a validação.

Uso:
    python scripts/normalizar_formulas_markdown.py --check
    python scripts/normalizar_formulas_markdown.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", "venv", "build", "dist", "site"}
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})([^`]*)$")
ONE_LINE_DOLLAR_RE = re.compile(r"^(?P<indent>\s*)\$\$(?P<body>.+?)\$\$\s*$")


@dataclass(frozen=True, slots=True)
class ResultadoArquivo:
    caminho: Path
    alterado: bool
    erros: tuple[str, ...]


def arquivos_markdown() -> list[Path]:
    arquivos: list[Path] = []
    for caminho in ROOT.rglob("*.md"):
        if any(parte in IGNORED_PARTS for parte in caminho.relative_to(ROOT).parts):
            continue
        arquivos.append(caminho)
    return sorted(arquivos)


def normalizar_texto(texto: str, caminho: Path) -> tuple[str, tuple[str, ...]]:
    linhas = texto.splitlines(keepends=True)
    saida: list[str] = []
    erros: list[str] = []

    cerca_codigo: str | None = None
    bloco_matematico: str | None = None
    linha_abertura = 0

    for numero, linha_com_fim in enumerate(linhas, start=1):
        fim = "\n" if linha_com_fim.endswith("\n") else ""
        linha = linha_com_fim[:-1] if fim else linha_com_fim
        sem_cr = linha[:-1] if linha.endswith("\r") else linha
        indentada = sem_cr.lstrip()

        if bloco_matematico is not None:
            fecha = (
                bloco_matematico == "$$" and re.fullmatch(r"\s*\$\$\s*", sem_cr)
            ) or (
                bloco_matematico == "\\[" and re.fullmatch(r"\s*\\\]\s*", sem_cr)
            )
            if fecha:
                saida.append("```" + fim)
                bloco_matematico = None
                linha_abertura = 0
            else:
                saida.append(sem_cr + fim)
            continue

        cerca = FENCE_RE.match(sem_cr)
        if cerca:
            marcador = cerca.group(1)
            if cerca_codigo is None:
                cerca_codigo = marcador[0]
            elif marcador.startswith(cerca_codigo):
                cerca_codigo = None
            saida.append(sem_cr + fim)
            continue

        if cerca_codigo is not None:
            saida.append(sem_cr + fim)
            continue

        if re.fullmatch(r"\s*\$\$\s*", sem_cr):
            saida.append("```math" + fim)
            bloco_matematico = "$$"
            linha_abertura = numero
            continue

        if re.fullmatch(r"\s*\\\[\s*", sem_cr):
            saida.append("```math" + fim)
            bloco_matematico = "\\["
            linha_abertura = numero
            continue

        uma_linha = ONE_LINE_DOLLAR_RE.match(sem_cr)
        if uma_linha:
            corpo = uma_linha.group("body").strip()
            saida.extend(("```math\n", corpo + "\n", "```" + fim))
            continue

        # Evita LaTeX de bloco que o GitHub não reconhece fora de delimitadores.
        if indentada.startswith("\\begin{") and "equation" in indentada:
            erros.append(
                f"{caminho.relative_to(ROOT)}:{numero}: ambiente LaTeX de bloco sem cerca math"
            )

        saida.append(sem_cr + fim)

    if bloco_matematico is not None:
        erros.append(
            f"{caminho.relative_to(ROOT)}:{linha_abertura}: bloco {bloco_matematico} não fechado"
        )
    if cerca_codigo is not None:
        erros.append(f"{caminho.relative_to(ROOT)}: cerca de código não fechada")

    return "".join(saida), tuple(erros)


def processar(caminho: Path, aplicar: bool) -> ResultadoArquivo:
    original = caminho.read_text(encoding="utf-8")
    normalizado, erros = normalizar_texto(original, caminho)
    alterado = normalizado != original
    if aplicar and alterado and not erros:
        caminho.write_text(normalizado, encoding="utf-8", newline="\n")
    return ResultadoArquivo(caminho=caminho, alterado=alterado, erros=erros)


def main() -> int:
    parser = argparse.ArgumentParser()
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--check", action="store_true", help="não modifica; falha se houver normalização pendente")
    grupo.add_argument("--apply", action="store_true", help="aplica a normalização segura")
    argumentos = parser.parse_args()

    resultados = [processar(caminho, argumentos.apply) for caminho in arquivos_markdown()]
    erros = [erro for resultado in resultados for erro in resultado.erros]
    alterados = [resultado.caminho for resultado in resultados if resultado.alterado]

    for erro in erros:
        print(f"ERRO: {erro}", file=sys.stderr)

    if argumentos.check and alterados:
        for caminho in alterados:
            print(f"NORMALIZAÇÃO PENDENTE: {caminho.relative_to(ROOT)}", file=sys.stderr)

    if argumentos.apply:
        print(f"Arquivos Markdown normalizados: {len(alterados)}")
    else:
        print(f"Arquivos Markdown verificados: {len(resultados)}")

    return 1 if erros or (argumentos.check and alterados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
