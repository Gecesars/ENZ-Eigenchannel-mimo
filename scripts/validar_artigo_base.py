"""Gera a validacao aritmetica auditavel do artigo-base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from enz_eigenchannel_mimo.article_validation import validar_artigo_base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("doc/pdfs/validacao_numerica_artigo.json"),
    )
    args = parser.parse_args()
    resultado = validar_artigo_base()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    divergentes = [
        item
        for item in resultado["checagens_aritmeticas"]
        if item["resultado"] != "CONSISTENTE"
    ]
    print(
        json.dumps(
            {
                "checagens": len(resultado["checagens_aritmeticas"]),
                "divergentes": len(divergentes),
                "saida": str(args.saida),
            },
            ensure_ascii=False,
        )
    )
    return 0 if not divergentes else 1


if __name__ == "__main__":
    raise SystemExit(main())
