#!/usr/bin/env python3
"""Reconstrói e publica a suíte AEDT/HFSS 2024 R2 nesta branch.

Este bootstrap é transitório: após validar o conteúdo, remove a si próprio,
o payload e o workflow que o executou.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = ROOT / "tools" / "bootstrap_aedt_payload"
WORKFLOW = ROOT / ".github" / "workflows" / "bootstrap_aedt_2024r2.yml"

README_SECTION = """

---

## 12. Automação AEDT/HFSS 2024 R2

O repositório contém uma camada Python executável para geração e validação dos modelos **M0–M4** no Ansys Electronics Desktop 2024 R2. A implementação mantém importação tardia do PyAEDT, versão estrita `2024.2`, sessão gRPC única por processo, geometria declarativa, build separado do solve, preflight offline e pacote de artefatos com SHA-256.

Os modelos preparados são: cavidade fechada Eigenmode, três ranhuras, cinco ranhuras, perfil em degrau e modelo fabricável com inclusão dielétrica, pinos e chanfros. Dimensões desconhecidas permanecem bloqueadas. Existe um seed explicitamente hipotético apenas para testar a automação CAD; ele é rejeitado automaticamente em execução científica.

Documentação e comandos: [`docs/30_implementacao_aedt_2024r2.md`](docs/30_implementacao_aedt_2024r2.md).
"""

AGENT_SECTION = """

## Automação AEDT 2024 R2

- Importar PyAEDT somente dentro da camada `aedt`; testes offline não podem exigir AEDT.
- Manter `version="2024.2"` e rejeitar fallback silencioso.
- Uma sessão ou worker possui `Desktop`, `Hfss`, `modeler`, `post` e setups.
- Toda geometria nasce de `G0GeometrySpec` e `GeometryPlan`; não criar objetos ad hoc no runner.
- `engineering_smoke_seed()` é proibido para resultados científicos.
- Build sem solve deve ser um gate independente.
- Não declarar validação AEDT sem artefatos de execução licenciada.
- Preservar nomes determinísticos, unidades explícitas e manifestos SHA-256.
"""


def executar(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def carregar_arquivos() -> dict[str, str]:
    partes = sorted(PAYLOAD_DIR.glob("*.txt"))
    if not partes:
        raise RuntimeError("payload AEDT não encontrado")
    blob = "".join(path.read_text(encoding="utf-8") for path in partes)
    bruto = zlib.decompress(base64.b85decode(blob.encode("ascii")))
    dados = json.loads(bruto.decode("utf-8"))
    if not isinstance(dados, dict) or not dados:
        raise RuntimeError("payload AEDT inválido ou vazio")
    return {str(path): str(content) for path, content in dados.items()}


def gravar_arquivos(arquivos: dict[str, str]) -> None:
    for relativo, conteudo in arquivos.items():
        destino = (ROOT / relativo).resolve()
        if ROOT not in destino.parents and destino != ROOT:
            raise RuntimeError(f"caminho fora do repositório: {relativo}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="utf-8", newline="\n")


def complementar_documentacao() -> None:
    readme = ROOT / "README.md"
    texto = readme.read_text(encoding="utf-8")
    if "## 12. Automação AEDT/HFSS 2024 R2" not in texto:
        readme.write_text(texto.rstrip() + README_SECTION + "\n", encoding="utf-8")

    index = ROOT / "docs" / "INDEX.md"
    linha = "- [Implementação Python para AEDT/HFSS 2024 R2](30_implementacao_aedt_2024r2.md)"
    texto = index.read_text(encoding="utf-8")
    if linha not in texto:
        index.write_text(texto.rstrip() + "\n" + linha + "\n", encoding="utf-8")

    agents = ROOT / "AGENTS.md"
    texto = agents.read_text(encoding="utf-8")
    if "## Automação AEDT 2024 R2" not in texto:
        agents.write_text(texto.rstrip() + AGENT_SECTION + "\n", encoding="utf-8")


def limpar_bootstrap() -> None:
    shutil.rmtree(PAYLOAD_DIR, ignore_errors=True)
    if WORKFLOW.exists():
        WORKFLOW.unlink()
    Path(__file__).unlink(missing_ok=True)


def main() -> int:
    arquivos = carregar_arquivos()
    gravar_arquivos(arquivos)
    complementar_documentacao()
    limpar_bootstrap()

    executar("python", "-m", "pytest", "-q")
    executar("python", "-m", "compileall", "-q", "src", "scripts", "testes")
    executar("python", "scripts/normalizar_formulas_markdown.py", "--check")

    executar("git", "config", "user.name", "github-actions[bot]")
    executar(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    executar("git", "add", "-A")
    executar("git", "commit", "-m", "feat: prepara geração e validação AEDT HFSS 2024 R2")
    executar("git", "push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
