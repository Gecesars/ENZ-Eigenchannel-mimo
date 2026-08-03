"""CLI do gerador/validador AEDT 2024 R2."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from enz_eigenchannel_mimo.geometry import VarianteModelo, engineering_smoke_seed

from .campaign import CampaignRequest, G0CampaignRunner
from .runtime import AedtRuntimeSpec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="enz-aedt",
        description="Gera e valida modelos G0/M0-M4 no Ansys AEDT/HFSS 2024 R2.",
    )
    parser.add_argument("variant", choices=[value.value for value in VarianteModelo])
    parser.add_argument("--output", default="artefatos/runs")
    parser.add_argument("--graphical", action="store_true")
    parser.add_argument("--attach-port", type=int, default=0)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument(
        "--scientific-run",
        action="store_true",
        help="rejeita qualquer dimensão hipotética/inferida",
    )
    parser.add_argument(
        "--allow-smoke-seed",
        action="store_true",
        help="usa geometria provisória somente para validar automação/CAD",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    variant = VarianteModelo(args.variant)
    if not args.allow_smoke_seed:
        raise SystemExit(
            "Nenhuma geometria publicável foi completada ainda. Use --allow-smoke-seed "
            "somente para validar a automação ou forneça uma especificação auditada."
        )
    spec = engineering_smoke_seed(variant)
    runtime = AedtRuntimeSpec(
        non_graphical=not args.graphical,
        new_desktop=args.attach_port <= 0,
        close_on_exit=args.attach_port <= 0,
        port=args.attach_port,
    )
    result = G0CampaignRunner().run(
        CampaignRequest(
            spec=spec,
            runtime=runtime,
            output_root=str(Path(args.output)),
            solve=args.solve,
            scientific_run=args.scientific_run,
            design_name=f"HFSS_ENZ_G0_{variant.value}",
        )
    )
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
