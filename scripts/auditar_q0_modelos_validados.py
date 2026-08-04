from __future__ import annotations

import argparse
import json
from pathlib import Path

from enz_eigenchannel_mimo.q0_audit import escrever_auditoria

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita o gate Q0 sem promover candidatos não validados."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artefatos" / "q0"
    )
    args = parser.parse_args()
    missing_path, inventory_path = escrever_auditoria(
        args.root.resolve(), args.output.resolve()
    )
    result = json.loads(missing_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": result["status"],
                "validated_instances_found": result["validated_instances_found"],
                "missing_manifest_count": sum(
                    not item["validated"] for item in result["component_status"]
                ),
                "missing_report": str(missing_path),
                "inventory": str(inventory_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
