from __future__ import annotations

import argparse
import json
from pathlib import Path

from .specifications import EspecificacaoGeometrica


def validar_spec_main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida schema, semântica e prontidão de uma especificação ENZ."
    )
    parser.add_argument("especificacao", type=Path)
    args = parser.parse_args()
    spec = EspecificacaoGeometrica.carregar(args.especificacao)
    resumo = {
        "modelo": spec.modelo,
        "schema": spec.dados["schema"],
        "sha256": spec.sha256,
        "etapas": {
            nome: {
                "pronta": spec.prontidao(nome).pronta,
                "bloqueios": list(spec.prontidao(nome).ausentes),
            }
            for nome in spec.etapas
        },
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


def aedt_worker_main() -> int:
    parser = argparse.ArgumentParser(
        description="Worker de uma única sessão AEDT 2024 R2 sobre gRPC nativo."
    )
    parser.add_argument("especificacao", type=Path)
    parser.add_argument(
        "--etapa", choices=["M0", "M1", "M2", "M3", "M4"], required=True
    )
    parser.add_argument("--runs-dir", type=Path, default=Path("artefatos/runs"))
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--graphical", action="store_true")
    parser.add_argument("--cores", type=int, default=14)
    args = parser.parse_args()

    from .aedt.worker import executar_worker

    run_dir = executar_worker(
        args.especificacao,
        args.etapa,
        args.runs_dir,
        solve=args.solve,
        non_graphical=not args.graphical,
        cores=args.cores,
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(validar_spec_main())
