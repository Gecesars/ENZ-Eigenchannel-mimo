"""Adquire e valida o corpus PDF declarado em ``references.bib``.

O script usa apenas URLs de editoras, repositórios institucionais e
manuscritos dos autores. Falhas de acesso não são ocultadas: cada tentativa é
registrada em ``doc/pdfs/manifest.json`` e nenhum conteúdo HTML é aceito como
PDF.
"""

from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import json
import re
import shutil
import tempfile
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PdfReadError


@dataclass(frozen=True)
class Fonte:
    url: str
    tipo: str
    versao: str
    licenca: str | None = None
    md5_publicado: str | None = None


FONTES: dict[str, tuple[Fonte, ...]] = {
    "VilasBoas2026FlatTop": (
        Fonte(
            "https://ieeexplore.ieee.org/ielx8/8566058/8911222/"
            "11563493.pdf?arnumber=11563493",
            "editora",
            "accepted_author_version",
            "CC-BY-4.0",
        ),
    ),
    "VilasBoas2025PhotonicDoping": (
        Fonte(
            "https://pubs.aip.org/aip/jap/article-pdf/doi/10.1063/5.0296722/"
            "20811628/193106_1_5.0296722.pdf",
            "editora",
            "version_of_record",
            "CC-BY-4.0",
        ),
        Fonte(
            "https://www.researchgate.net/publication/journal/"
            "Journal-of-Applied-Physics-1089-7550/publication/397849186_"
            "Photonic_doping_of_epsilon-near-zero_waveguide_cavities_for_"
            "high-gain_millimeter-wave_antenna_arrays/links/"
            "6920e8edabe27c41e5144ecb/Photonic-doping-of-epsilon-near-zero-"
            "waveguide-cavities-for-high-gain-millimeter-wave-antenna-arrays.pdf",
            "pagina_dos_autores",
            "version_of_record",
            "CC-BY-4.0",
        ),
    ),
    "VilasBoas2026DielectricLoaded": (
        Fonte(
            "https://ieeexplore.ieee.org/ielx8/8/11477934/"
            "11346880.pdf?arnumber=11346880",
            "editora",
            "version_of_record",
        ),
    ),
    "Li2022GeometryIndependent": (
        Fonte(
            "https://oa.ee.tsinghua.edu.cn/~liyue/paper/"
            "2022_Geometry-independent%20antenna%20based%20on%20"
            "Epsilon-near-zero%20medium.pdf",
            "repositorio_do_autor",
            "version_of_record",
            "CC-BY-4.0",
        ),
    ),
    "Silveirinha2006Supercoupling": (
        Fonte(
            "https://harvest.aps.org/v2/journals/articles/"
            "10.1103/PhysRevLett.97.157403/fulltext",
            "editora",
            "version_of_record",
        ),
    ),
    "Liberal2017PhotonicDoping": (
        Fonte(
            "https://murimetasurfaces.hsites.harvard.edu/sites/g/files/"
            "omnuum8691/files/muri_metasurfaces/files/"
            "photonic_doping_science_march_10_2017.pdf",
            "repositorio_institucional_dos_autores",
            "version_of_record",
        ),
    ),
    "Liberal2017NZIPhotonics": (
        Fonte(
            "https://murimetasurfaces.hsites.harvard.edu/sites/g/files/"
            "omnuum8691/files/muri_metasurfaces/files/"
            "zim_review_article_nature_photonics_march_2017.pdf",
            "repositorio_institucional_dos_autores",
            "version_of_record",
        ),
    ),
    "Yan2024FanoENZ": (
        Fonte(
            "https://harvest.aps.org/v2/journals/articles/"
            "10.1103/PhysRevLett.133.256402/fulltext",
            "editora",
            "version_of_record",
        ),
    ),
    "Harrington1971CharacteristicModes": (
        Fonte(
            "https://ece-research.unm.edu/summa/notes/In/0195.pdf",
            "arquivo_academico",
            "author_manuscript",
        ),
    ),
    "Telatar1999Capacity": (
        Fonte(
            "https://infoscience.epfl.ch/server/api/core/bitstreams/"
            "ab2b6a45-d663-46f6-aa8f-f7f9b06c2bc4/content",
            "repositorio_institucional",
            "version_of_record",
            "openaccess",
            "304bb4ec06a007516c460a323730fff6",
        ),
    ),
    "Ayach2014SparsePrecoding": (
        Fonte(
            "https://arxiv.org/pdf/1305.2460",
            "repositorio_de_preprints",
            "author_manuscript",
        ),
    ),
    "Molisch2017HybridBeamforming": (
        Fonte(
            "https://arxiv.org/pdf/1609.05078",
            "repositorio_de_preprints",
            "author_manuscript",
        ),
    ),
    "Slater1946MicrowaveElectronics": (
        Fonte(
            "https://harvest.aps.org/v2/journals/articles/"
            "10.1103/RevModPhys.18.441/fulltext",
            "editora",
            "version_of_record",
        ),
    ),
    "Lai1990LeakingModes": (
        Fonte(
            "https://harvest.aps.org/v2/journals/articles/"
            "10.1103/PhysRevA.41.5187/fulltext",
            "editora",
            "version_of_record",
        ),
    ),
}

ANEXOS = (
    {
        "nome": "Li2022GeometryIndependent_supplementary.pdf",
        "relacao": "supplementary_information",
        "doi_artigo": "10.1038/s41467-022-31013-z",
        "fonte": Fonte(
            "https://pmc.ncbi.nlm.nih.gov/articles/instance/9217913/bin/"
            "41467_2022_31013_MOESM1_ESM.pdf",
            "repositorio_pubmed_central",
            "supplementary_information",
            "CC-BY-4.0",
        ),
    },
)

ARQUIVOS_EXISTENTES = {
    "VilasBoas2026FlatTop": "VilasBoas_2026_OJAP_FlatTop.pdf",
}


def _entradas_bibtex(texto: str) -> list[dict[str, str]]:
    entradas: list[dict[str, str]] = []
    for bloco in re.finditer(
        r"@article\{(?P<key>[^,]+),(?P<body>.*?)\n\}",
        texto,
        re.DOTALL | re.IGNORECASE,
    ):
        corpo = bloco.group("body")
        campos = {
            nome.lower(): valor.strip().replace("\n", " ")
            for nome, valor in re.findall(
                r"(\w+)\s*=\s*\{(.*?)\}", corpo, re.DOTALL
            )
        }
        entradas.append(
            {
                "key": bloco.group("key").strip(),
                "title": campos.get("title", ""),
                "doi": campos.get("doi", ""),
            }
        )
    return entradas


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", texto.lower()))


def _titulo_compativel(titulo: str, texto_pdf: str) -> tuple[bool, float]:
    esperadas = set(_normalizar(titulo).split())
    observadas = set(_normalizar(texto_pdf).split())
    if not esperadas:
        return False, 0.0
    cobertura = len(esperadas & observadas) / len(esperadas)
    return cobertura >= 0.60, cobertura


def _opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def _baixar(fonte: Fonte, destino: Path) -> dict[str, Any]:
    requisicao = urllib.request.Request(
        fonte.url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/138 Safari/537.36"
            ),
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.5",
            "Referer": fonte.url.split("/", 3)[0] + "//" + fonte.url.split("/", 3)[2] + "/",
        },
    )
    with _opener().open(requisicao, timeout=90) as resposta:
        tipo = resposta.headers.get_content_type()
        with destino.open("wb") as arquivo:
            shutil.copyfileobj(resposta, arquivo)
        return {"http_status": resposta.status, "content_type": tipo, "url_final": resposta.url}


def _validar_pdf(
    caminho: Path, titulo: str, doi: str, fonte: Fonte | None = None
) -> dict[str, Any]:
    dados = caminho.read_bytes()
    if not dados.startswith(b"%PDF-"):
        raise ValueError("assinatura PDF ausente")
    if b"%%EOF" not in dados[-8192:]:
        raise ValueError("marcador EOF ausente")
    leitor = PdfReader(caminho, strict=True)
    if len(leitor.pages) < 1:
        raise ValueError("PDF sem paginas")
    texto = "\n".join((pagina.extract_text() or "") for pagina in leitor.pages[:3])
    titulo_ok, cobertura = _titulo_compativel(titulo, texto)
    doi_normalizado = _normalizar(doi)
    doi_no_texto = doi_normalizado in _normalizar(texto)
    md5 = hashlib.md5(dados).hexdigest()
    md5_publicado_ok = fonte is not None and fonte.md5_publicado == md5
    if not titulo_ok and not md5_publicado_ok:
        raise ValueError(f"titulo incompativel (cobertura={cobertura:.3f})")
    return {
        "sha256": hashlib.sha256(dados).hexdigest(),
        "md5": md5,
        "bytes": len(dados),
        "paginas": len(leitor.pages),
        "titulo_cobertura": round(cobertura, 6),
        "titulo_metodo": "extracao_lexical" if titulo_ok else "checksum_do_repositorio",
        "md5_publicado_confirmado": md5_publicado_ok,
        "doi_encontrado_primeiras_3_paginas": doi_no_texto,
        "pdf_header": dados[:8].decode("latin-1"),
        "pdf_eof": True,
    }


def adquirir(raiz: Path) -> dict[str, Any]:
    bib = raiz / "referencias" / "references.bib"
    destino = raiz / "doc" / "pdfs"
    destino.mkdir(parents=True, exist_ok=True)
    entradas = _entradas_bibtex(bib.read_text(encoding="utf-8"))
    chaves = {entrada["key"] for entrada in entradas}
    ausentes_no_mapa = sorted(chaves - FONTES.keys())
    extras_no_mapa = sorted(FONTES.keys() - chaves)
    if ausentes_no_mapa or extras_no_mapa:
        raise RuntimeError(
            f"mapa de fontes divergente: ausentes={ausentes_no_mapa}; extras={extras_no_mapa}"
        )

    documentos: list[dict[str, Any]] = []
    for entrada in entradas:
        chave = entrada["key"]
        nome = ARQUIVOS_EXISTENTES.get(chave, f"{chave}.pdf")
        alvo = destino / nome
        registro: dict[str, Any] = {
            **entrada,
            "arquivo": alvo.relative_to(raiz).as_posix(),
            "status": "indisponivel",
            "tentativas": [],
        }
        if alvo.exists():
            try:
                registro["validacao"] = _validar_pdf(alvo, entrada["title"], entrada["doi"])
                registro["status"] = "validado"
                registro["origem"] = "arquivo_preexistente"
                documentos.append(registro)
                continue
            except (OSError, ValueError, PdfReadError) as erro:
                registro["tentativas"].append(
                    {"origem": "arquivo_preexistente", "erro": f"{type(erro).__name__}: {erro}"}
                )

        for fonte in FONTES[chave]:
            temporario: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=destino) as tmp:
                    temporario = Path(tmp.name)
                resposta = _baixar(fonte, temporario)
                validacao = _validar_pdf(
                    temporario, entrada["title"], entrada["doi"], fonte
                )
                temporario.replace(alvo)
                registro.update(
                    {
                        "status": "validado",
                        "origem": fonte.tipo,
                        "versao_documental": fonte.versao,
                        "licenca": fonte.licenca,
                        "url_obtencao": fonte.url,
                        "resposta": resposta,
                        "validacao": validacao,
                    }
                )
                break
            except (OSError, ValueError, urllib.error.URLError) as erro:
                registro["tentativas"].append(
                    {
                        "url": fonte.url,
                        "origem": fonte.tipo,
                        "versao_documental": fonte.versao,
                        "erro": f"{type(erro).__name__}: {erro}",
                    }
                )
            finally:
                if temporario is not None and temporario.exists():
                    temporario.unlink()
        if registro["status"] != "validado":
            pasta_links = destino / "indisponiveis"
            pasta_links.mkdir(exist_ok=True)
            link = pasta_links / f"{chave}.url"
            link.write_text(
                "[InternetShortcut]\nURL=https://doi.org/" + entrada["doi"] + "\n",
                encoding="utf-8",
            )
            registro["atalho_doi"] = link.relative_to(raiz).as_posix()
        documentos.append(registro)

    anexos: list[dict[str, Any]] = []
    for anexo in ANEXOS:
        fonte = anexo["fonte"]
        alvo = destino / str(anexo["nome"])
        registro_anexo: dict[str, Any] = {
            key: value for key, value in anexo.items() if key != "fonte"
        }
        temporario: Path | None = None
        try:
            if alvo.exists():
                leitor = PdfReader(alvo, strict=True)
                dados = alvo.read_bytes()
                if not dados.startswith(b"%PDF-") or not leitor.pages:
                    raise ValueError("anexo preexistente invalido")
            else:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=destino) as tmp:
                    temporario = Path(tmp.name)
                registro_anexo["resposta"] = _baixar(fonte, temporario)
                dados = temporario.read_bytes()
                leitor = PdfReader(temporario, strict=True)
                if not dados.startswith(b"%PDF-") or not leitor.pages:
                    raise ValueError("anexo adquirido invalido")
                temporario.replace(alvo)
            registro_anexo.update(
                {
                    "status": "validado",
                    "arquivo": alvo.relative_to(raiz).as_posix(),
                    "url_obtencao": fonte.url,
                    "licenca": fonte.licenca,
                    "sha256": hashlib.sha256(dados).hexdigest(),
                    "bytes": len(dados),
                    "paginas": len(leitor.pages),
                }
            )
        except (OSError, ValueError, urllib.error.URLError, PdfReadError) as erro:
            registro_anexo.update(
                {"status": "indisponivel", "erro": f"{type(erro).__name__}: {erro}"}
            )
        finally:
            if temporario is not None and temporario.exists():
                temporario.unlink()
        anexos.append(registro_anexo)

    validados = sum(doc["status"] == "validado" for doc in documentos)
    manifesto = {
        "schema_version": "pdf-corpus-manifest-v1",
        "gerado_em_utc": datetime.now(UTC).isoformat(),
        "escopo": {
            "descricao": "Todas as entradas @article de referencias/references.bib",
            "total_referencias": len(entradas),
            "validados": validados,
            "indisponiveis": len(entradas) - validados,
        },
        "criterios_validacao": [
            "assinatura %PDF",
            "marcador %%EOF nos ultimos 8192 bytes",
            "parse estrito pelo pypdf",
            "ao menos uma pagina",
            "cobertura lexical do titulo >= 60% nas tres primeiras paginas",
            "SHA-256 e tamanho registrados",
        ],
        "documentos": documentos,
        "anexos": anexos,
    }
    (destino / "manifest.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifesto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifesto = adquirir(args.raiz.resolve())
    print(json.dumps(manifesto["escopo"], ensure_ascii=False))
    return 0 if manifesto["escopo"]["indisponiveis"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
