"""Gera o dossiê técnico auditável da reconstrução ENZ/HFSS."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import fitz
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PilImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
ARTICLE = ROOT / "doc" / "pdfs" / "VilasBoas_2026_OJAP_FlatTop.pdf"
SPECIFICATION = (
    ROOT
    / "modelos"
    / "especificacoes"
    / "g0_figura2_reconstrucao_exploratoria.hipotese.v7.yaml"
)
VALIDATION = (
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "G0_figura2_v7"
    / "posprocessamento"
    / "validacao_cientifica_exploratoria.json"
)
POSTPROCESSING = (
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "G0_figura2_v7"
    / "posprocessamento"
    / "postprocessing_environment.json"
)
CLEAN_METRICS = [
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "G0_figura2_v7"
    / "run_limpo"
    / "metrics"
    / name
    for name in ("convergence.csv", "mesh_stats.csv", "solver_profile.csv")
]
OUTPUT_NAME = "Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v1.pdf"
MANIFEST_NAME = "Relatorio_Tecnico_ENZ_Cavidade_VilasBoas_v1.manifest.json"
OUTPUT = ROOT / "doc" / "pdfs" / OUTPUT_NAME
MANIFEST = ROOT / "doc" / "pdfs" / MANIFEST_NAME
POROS_DIR = ROOT / "poros_aedt" / "relatorios"
ASSET_DIR = ROOT / "doc" / "relatorio_tecnico" / "assets"

CORE_DOCS = [
    ROOT / "docs" / "36_relatorio_tecnico_completo.md",
    *sorted(
        path
        for path in (ROOT / "docs").glob("[0-3][0-9]*.md")
        if path.name != "36_relatorio_tecnico_completo.md"
    ),
    ROOT / "docs" / "GUIA_RENDERIZACAO_MATEMATICA.md",
    ROOT / "CREDITOS.md",
]

GEOMETRY_SEED_IMAGES = [
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-180323-ae961d5a"
    / "plots"
    / "geometry_isometric.png",
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-180323-ae961d5a"
    / "plots"
    / "geometry_front.png",
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-180323-ae961d5a"
    / "plots"
    / "geometry_top.png",
]

FIELD_SEED_IMAGES = [
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-190101-821f2cf6"
    / "plots"
    / "article_environment"
    / "EMag_ZX_ArrayCenter_25p87.jpg",
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-190101-821f2cf6"
    / "plots"
    / "article_environment"
    / "EMag_XY_MidHeight_25p87.jpg",
    ROOT
    / "artefatos"
    / "runs"
    / "ENZ-20260803-190101-821f2cf6"
    / "plots"
    / "article_environment"
    / "EMag_YZ_Slot1_25p87.jpg",
]

GEOMETRY_IMAGES = [
    ASSET_DIR / "geometry_isometric.png",
    ASSET_DIR / "geometry_front.png",
    ASSET_DIR / "geometry_top.png",
]

FIELD_IMAGES = [
    ASSET_DIR / "EMag_ZX_ArrayCenter_25p87.jpg",
    ASSET_DIR / "EMag_XY_MidHeight_25p87.jpg",
    ASSET_DIR / "EMag_YZ_Slot1_25p87.jpg",
]

REPORT_DIR = (
    ROOT
    / "poros_aedt"
    / "reconstrucoes_exploratorias"
    / "G0_figura2_v7"
    / "posprocessamento"
    / "relatorios_artigo"
)
REPORT_IMAGES = [
    REPORT_DIR / "Fig2b_S11_25_27GHz.jpg",
    REPORT_DIR / "Fig2b_RadiationEfficiency.jpg",
    REPORT_DIR / "Fig3c_PeakRealizedGain.jpg",
    REPORT_DIR / "Fig1b_d_EPlane_25p87.jpg",
    REPORT_DIR / "Fig3d_EPlane_25p87.jpg",
    REPORT_DIR / "Fig4_EPlane_CoCross_MultiFreq.jpg",
    REPORT_DIR / "Fig4_HPlane_CoCross_MultiFreq.jpg",
    REPORT_DIR / "Gain3D_25p87.jpg",
]

CLASSIFICATION_COLORS = {
    "PUBLICADO": "#005A9C",
    "DERIVADO": "#4B5563",
    "SIMULADO": "#006B3C",
    "MEDIDO": "#6B21A8",
    "INFERIDO": "#8A4B08",
    "HIPÓTESE": "#A11B1B",
    "DESCONHECIDO": "#6B7280",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def register_fonts() -> None:
    candidates = [
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/consola.ttf"),
        ),
        (
            Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf",
            Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans-Bold.ttf",
            Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSansMono.ttf",
        ),
    ]
    for regular, bold, mono in candidates:
        if all(path.is_file() for path in (regular, bold, mono)):
            pdfmetrics.registerFont(TTFont("TechSans", str(regular)))
            pdfmetrics.registerFont(TTFont("TechSansBold", str(bold)))
            pdfmetrics.registerFont(TTFont("TechMono", str(mono)))
            pdfmetrics.registerFontFamily(
                "TechSans", normal="TechSans", bold="TechSansBold"
            )
            return
    raise FileNotFoundError("nenhuma família de fontes Unicode foi encontrada")


def build_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}
    styles["Title"] = ParagraphStyle(
        "Title",
        parent=sample["Title"],
        fontName="TechSansBold",
        fontSize=25,
        leading=29,
        textColor=colors.HexColor("#16324F"),
        alignment=TA_LEFT,
        spaceAfter=8 * mm,
    )
    styles["Subtitle"] = ParagraphStyle(
        "Subtitle",
        fontName="TechSans",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#335C81"),
        spaceAfter=4 * mm,
    )
    styles["Heading1"] = ParagraphStyle(
        "Heading1",
        fontName="TechSansBold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#16324F"),
        spaceBefore=7 * mm,
        spaceAfter=3 * mm,
        keepWithNext=True,
    )
    styles["Heading2"] = ParagraphStyle(
        "Heading2",
        fontName="TechSansBold",
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor("#24557A"),
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        keepWithNext=True,
    )
    styles["Heading3"] = ParagraphStyle(
        "Heading3",
        fontName="TechSansBold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#3B6787"),
        spaceBefore=3 * mm,
        spaceAfter=1.5 * mm,
        keepWithNext=True,
    )
    styles["Body"] = ParagraphStyle(
        "Body",
        fontName="TechSans",
        fontSize=8.2,
        leading=10.4,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#17212B"),
        spaceAfter=2.1 * mm,
        splitLongWords=True,
    )
    styles["Small"] = ParagraphStyle(
        "Small",
        fontName="TechSans",
        fontSize=7.1,
        leading=8.7,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#273746"),
        spaceAfter=1.5 * mm,
    )
    styles["Bullet"] = ParagraphStyle(
        "Bullet",
        parent=styles["Body"],
        leftIndent=5 * mm,
        firstLineIndent=-3 * mm,
        bulletIndent=1 * mm,
        spaceAfter=1 * mm,
    )
    styles["Quote"] = ParagraphStyle(
        "Quote",
        parent=styles["Body"],
        leftIndent=7 * mm,
        rightIndent=5 * mm,
        borderColor=colors.HexColor("#9EB3C2"),
        borderWidth=0.6,
        borderPadding=5,
        backColor=colors.HexColor("#F4F7F9"),
    )
    styles["Equation"] = ParagraphStyle(
        "Equation",
        fontName="TechMono",
        fontSize=7.2,
        leading=9,
        leftIndent=7 * mm,
        rightIndent=7 * mm,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#273746"),
        backColor=colors.HexColor("#F5F6F7"),
        borderPadding=5,
        spaceBefore=1.5 * mm,
        spaceAfter=2 * mm,
    )
    styles["Code"] = ParagraphStyle(
        "Code",
        fontName="TechMono",
        fontSize=6.5,
        leading=8,
        leftIndent=3 * mm,
        rightIndent=3 * mm,
        textColor=colors.HexColor("#1F2937"),
        backColor=colors.HexColor("#F3F4F6"),
        borderPadding=5,
        spaceAfter=2 * mm,
    )
    styles["Table"] = ParagraphStyle(
        "Table",
        fontName="TechSans",
        fontSize=6.5,
        leading=8,
        alignment=TA_LEFT,
        splitLongWords=True,
    )
    styles["TableHead"] = ParagraphStyle(
        "TableHead",
        parent=styles["Table"],
        fontName="TechSansBold",
        textColor=colors.white,
    )
    styles["Caption"] = ParagraphStyle(
        "Caption",
        fontName="TechSans",
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
        spaceBefore=1 * mm,
        spaceAfter=3 * mm,
    )
    styles["CoverInfo"] = ParagraphStyle(
        "CoverInfo",
        fontName="TechSans",
        fontSize=9.2,
        leading=12.5,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=2 * mm,
    )
    return styles


def inline_markup(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<u><font color="#24557A">\1</font></u>',
        value,
    )
    value = re.sub(
        r"`([^`]+)`", r'<font name="TechMono" color="#7C2D12">\1</font>', value
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    for label, color in CLASSIFICATION_COLORS.items():
        value = value.replace(
            f"<b>{label}:</b>", f'<b><font color="{color}">{label}:</font></b>'
        )
    return value


def count_markdown_tables(text: str) -> int:
    lines = text.splitlines()
    count = 0
    for index in range(len(lines) - 1):
        if lines[index].lstrip().startswith("|") and re.match(
            r"^\s*\|?\s*:?-+", lines[index + 1]
        ):
            count += 1
    return count


def markdown_table(
    rows: list[list[str]], styles: dict[str, ParagraphStyle], width: float
) -> Table:
    columns = max(len(row) for row in rows)
    normalized = [row + [""] * (columns - len(row)) for row in rows]
    data: list[list[Paragraph]] = []
    for row_index, row in enumerate(normalized):
        style = styles["TableHead"] if row_index == 0 else styles["Table"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(
        data,
        colWidths=[width / columns] * columns,
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#335C81")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9AAAB7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F5F7F9")],
                ),
            ]
        )
    )
    return table


def wrap_code(lines: list[str], width: int = 105) -> str:
    wrapped: list[str] = []
    for line in lines:
        chunks = textwrap.wrap(
            line,
            width=width,
            replace_whitespace=False,
            drop_whitespace=False,
            subsequent_indent="  ",
        )
        wrapped.extend(chunks or [""])
    return "\n".join(wrapped)


def render_markdown(
    text: str,
    story: list[Any],
    styles: dict[str, ParagraphStyle],
    page_width: float,
    skip_first_h1: bool = False,
) -> None:
    lines = text.splitlines()
    index = 0
    paragraph: list[str] = []
    first_h1_skipped = False

    def flush_paragraph() -> None:
        if paragraph:
            merged = " ".join(part.strip() for part in paragraph).strip()
            if merged:
                story.append(Paragraph(inline_markup(merged), styles["Body"]))
            paragraph.clear()

    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        if stripped.startswith("<!--"):
            flush_paragraph()
            while index < len(lines) and "-->" not in lines[index]:
                index += 1
            index += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            story.append(Preformatted(wrap_code(code), styles["Code"]))
            index += 1
            continue
        if stripped == "$$":
            flush_paragraph()
            index += 1
            equation: list[str] = []
            while index < len(lines) and lines[index].strip() != "$$":
                equation.append(lines[index].strip())
                index += 1
            story.append(Paragraph(html.escape(" ".join(equation)), styles["Equation"]))
            index += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            title = heading.group(2)
            if skip_first_h1 and level == 1 and not first_h1_skipped:
                first_h1_skipped = True
                index += 1
                continue
            story.append(
                Paragraph(inline_markup(title), styles[f"Heading{min(level, 3)}"])
            )
            index += 1
            continue
        if (
            stripped.startswith("|")
            and index + 1 < len(lines)
            and re.match(r"^\s*\|?\s*:?-+", lines[index + 1])
        ):
            flush_paragraph()
            table_lines = [stripped]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            rows = [
                [cell.strip() for cell in row.strip("|").split("|")]
                for row in table_lines
            ]
            story.append(markdown_table(rows, styles, page_width))
            story.append(Spacer(1, 2 * mm))
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet or numbered:
            flush_paragraph()
            body = (bullet or numbered).group(1)  # type: ignore[union-attr]
            marker = "•" if bullet else stripped.split(maxsplit=1)[0]
            story.append(
                Paragraph(
                    f"{marker}&nbsp;&nbsp;{inline_markup(body)}", styles["Bullet"]
                )
            )
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote = stripped.lstrip("> ")
            story.append(Paragraph(inline_markup(quote), styles["Quote"]))
            index += 1
            continue
        if re.match(r"^[-*_]{3,}$", stripped):
            flush_paragraph()
            story.append(
                HRFlowable(
                    width="100%", thickness=0.4, color=colors.HexColor("#9AAAB7")
                )
            )
            index += 1
            continue
        if stripped.startswith("<") and stripped.endswith(">"):
            index += 1
            continue
        paragraph.append(stripped)
        index += 1
    flush_paragraph()


class TechnicalDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, styles: dict[str, ParagraphStyle]) -> None:
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=17 * mm,
            bottomMargin=16 * mm,
            title="Dossiê técnico da cavidade ENZ e do ambiente HFSS",
            author="Projeto ENZ-Eigenchannel-mimo — Geraldo César Simão",
            subject="Auditoria e reconstrução exploratória de Vilas Boas et al.",
        )
        self.styles = styles
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="body",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(
            [PageTemplate(id="technical", frames=[frame], onPage=self.decorate_page)]
        )
        self.heading_number = 0

    def decorate_page(self, canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setTitle("Dossiê técnico da cavidade ENZ e do ambiente HFSS")
        canvas.setAuthor("Projeto ENZ-Eigenchannel-mimo — Geraldo César Simão")
        canvas.setSubject("Reconstrução exploratória creditada a Vilas Boas et al.")
        if doc.page > 1:
            canvas.setStrokeColor(colors.HexColor("#B7C3CC"))
            canvas.setLineWidth(0.35)
            canvas.line(15 * mm, A4[1] - 12 * mm, A4[0] - 15 * mm, A4[1] - 12 * mm)
            canvas.setFont("TechSans", 6.5)
            canvas.setFillColor(colors.HexColor("#4B5563"))
            canvas.drawString(
                15 * mm,
                A4[1] - 9.5 * mm,
                "ENZ-Eigenchannel-mimo — dossiê técnico auditável",
            )
            canvas.drawRightString(
                A4[0] - 15 * mm,
                A4[1] - 9.5 * mm,
                "Vilas Boas et al. — DOI 10.1109/OJAP.2026.3703713",
            )
            canvas.line(15 * mm, 11 * mm, A4[0] - 15 * mm, 11 * mm)
            canvas.drawString(
                15 * mm,
                7.5 * mm,
                "HIPÓTESE — a reconstrução local não reproduz o artigo",
            )
            canvas.drawRightString(A4[0] - 15 * mm, 7.5 * mm, f"p. {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable: Any) -> None:
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        if style_name not in {"Heading1", "Heading2", "Heading3"}:
            return
        level = {"Heading1": 0, "Heading2": 1, "Heading3": 2}[style_name]
        text = flowable.getPlainText()
        key = getattr(flowable, "_technical_bookmark", None)
        if key is None:
            key = f"heading-{self.heading_number}"
            flowable._technical_bookmark = key
            self.heading_number += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
        self.notify("TOCEntry", (level, text, self.page, key))


def scaled_image(path: Path, max_width: float, max_height: float) -> Image:
    with PilImage.open(path) as source:
        width, height = source.size
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def image_block(
    path: Path,
    caption: str,
    styles: dict[str, ParagraphStyle],
    width: float,
    height: float,
) -> list[Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return [
        scaled_image(path, width, height),
        Paragraph(inline_markup(caption), styles["Caption"]),
    ]


def image_grid(
    entries: list[tuple[Path, str]],
    styles: dict[str, ParagraphStyle],
    page_width: float,
    columns: int = 2,
    max_height: float = 75 * mm,
) -> Table:
    cell_width = page_width / columns
    cells: list[list[Any]] = []
    row: list[Any] = []
    for path, caption in entries:
        content = image_block(
            path,
            caption,
            styles,
            width=cell_width - 5 * mm,
            height=max_height,
        )
        row.append(content)
        if len(row) == columns:
            cells.append(row)
            row = []
    if row:
        row.extend([""] * (columns - len(row)))
        cells.append(row)
    table = Table(cells, colWidths=[cell_width] * columns, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def create_article_crop() -> Path:
    target = ASSET_DIR / "vilasboas_figura2_dimensoes.png"
    document = fitz.open(ARTICLE)
    page = document[3]
    clip = fitz.Rect(42, 54, page.rect.width - 38, 360)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2), clip=clip, alpha=False)
    pixmap.save(target)
    document.close()
    return target


def create_waveport_diagram() -> Path:
    target = ASSET_DIR / "waveport_integracao_z.png"
    fig, ax = plt.subplots(figsize=(7.2, 5.1), dpi=180)
    x0, x1 = -1.78, 1.78
    z0, z1 = 3.0, 10.11
    ax.add_patch(
        plt.Rectangle(
            (x0, z0),
            x1 - x0,
            z1 - z0,
            facecolor="#DCEAF4",
            edgecolor="#16324F",
            linewidth=2,
        )
    )
    ax.annotate(
        "linha de integração modal (Z)",
        xy=(0, z1 - 0.25),
        xytext=(0, z0 + 0.35),
        arrowprops={"arrowstyle": "->", "lw": 3, "color": "#B42318"},
        ha="center",
        va="bottom",
        color="#B42318",
        fontsize=10,
        weight="bold",
    )
    ax.annotate(
        "3,56 mm em X",
        xy=(x1, z0 - 0.35),
        xytext=(x0, z0 - 0.35),
        arrowprops={"arrowstyle": "<->", "color": "#24557A"},
        ha="center",
        va="top",
        fontsize=9,
    )
    ax.annotate(
        "7,11 mm em Z",
        xy=(x1 + 0.35, z1),
        xytext=(x1 + 0.35, z0),
        arrowprops={"arrowstyle": "<->", "color": "#24557A"},
        ha="left",
        va="center",
        rotation=90,
        fontsize=9,
    )
    ax.scatter(
        [0],
        [(z0 + z1) / 2],
        s=130,
        facecolors="none",
        edgecolors="#006B3C",
        linewidths=2,
    )
    ax.scatter([0], [(z0 + z1) / 2], s=20, color="#006B3C")
    ax.text(
        0.2,
        (z0 + z1) / 2,
        "normal +Y (saindo do plano)",
        color="#006B3C",
        fontsize=9,
        va="center",
    )
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")
    ax.set_title("DERIVADO — waveport no plano XZ, em y = −18 mm")
    ax.set_xlim(-3.3, 4.1)
    ax.set_ylim(1.8, 11.1)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.18)
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def create_cut_diagram() -> Path:
    target = ASSET_DIR / "atlas_cortes_declarativos.png"
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2), dpi=180)
    ax = axes[0]
    outline_x = [-18, -15, 15, 18, 18, 15, 4.5, 4.5, -4.5, -4.5, -15, -18, -18]
    outline_y = [3, 0, 0, 3, 6, 9, 9, 10, 10, 9, 9, 6, 3]
    ax.fill(outline_x, outline_y, color="#E4E7EB", edgecolor="#16324F")
    for number, x in enumerate([-8, -4, 0, 4, 8], 1):
        ax.plot([x, x], [1.67, 7.33], color="#202020", linewidth=2)
        ax.axvline(x, color="#B42318", alpha=0.55, linestyle="--", linewidth=1)
        ax.text(x, 9.35, f"YZ{number}", ha="center", fontsize=7, color="#B42318")
    ax.axhline(4.5, color="#006B3C", linestyle="-.", linewidth=1.5)
    ax.text(-17, 4.8, "ZX central", fontsize=8, color="#006B3C")
    ax.set_title("Vista XY — cinco cortes YZ")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.15)

    ax = axes[1]
    ax.add_patch(
        plt.Rectangle((-18, 3), 27, 7.11, facecolor="#DCEAF4", edgecolor="#16324F")
    )
    ax.axvline(-18, color="#B42318", linewidth=2, label="Cut_ZX_Port")
    ax.axvline(4.5, color="#006B3C", linewidth=2, label="Cut_ZX_ArrayCenter")
    ax.axhline(
        6.555, color="#7C3AED", linestyle="--", linewidth=1.5, label="Cut_XY_MidHeight"
    )
    ax.set_title("Esquema longitudinal YZ")
    ax.set_xlabel("Y [mm]")
    ax.set_ylabel("Z [mm]")
    ax.legend(fontsize=6, loc="lower right")
    ax.grid(True, alpha=0.15)

    ax = axes[2]
    ax.add_patch(
        plt.Rectangle((-1.78, 3), 3.56, 7.11, facecolor="#DCEAF4", edgecolor="#16324F")
    )
    ax.annotate(
        "Z",
        xy=(0, 9.8),
        xytext=(0, 3.3),
        arrowprops={"arrowstyle": "->", "color": "#B42318", "lw": 2},
        ha="center",
        color="#B42318",
    )
    ax.set_title("Cut_ZX_Port / waveport")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.15)
    fig.suptitle(
        "DERIVADO — atlas dos oito cortes definidos na especificação v7",
        fontsize=13,
        weight="bold",
    )
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def create_convergence_plot() -> Path:
    target = ASSET_DIR / "convergencia_malha_v7.png"
    passes = [1, 2, 3, 4]
    elements = [17889, 20975, 24571, 28772]
    delta = [None, 0.047718, 0.011616, 0.0041377]
    fig, left = plt.subplots(figsize=(8.5, 4.5), dpi=180)
    right = left.twinx()
    left.plot(
        passes[1:],
        delta[1:],
        marker="o",
        linewidth=2.2,
        color="#B42318",
        label="Max Mag. ΔS",
    )
    left.axhline(
        0.02, color="#006B3C", linestyle="--", linewidth=1.7, label="meta 0,02"
    )
    right.bar(
        passes, elements, color="#9CC3DD", alpha=0.55, label="elementos resolvidos"
    )
    left.set_yscale("log")
    left.set_xticks(passes)
    left.set_xlabel("Passe adaptativo")
    left.set_ylabel("Max Mag. ΔS")
    right.set_ylabel("Elementos resolvidos")
    left.grid(True, which="both", alpha=0.2)
    lines, labels = left.get_legend_handles_labels()
    bars, bar_labels = right.get_legend_handles_labels()
    left.legend(lines + bars, labels + bar_labels, loc="upper right", fontsize=8)
    left.set_title("SIMULADO — convergência adaptativa a 25,87 GHz")
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def prepare_assets() -> dict[str, Path]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for source, target in zip(GEOMETRY_SEED_IMAGES, GEOMETRY_IMAGES, strict=True):
        if source.is_file():
            shutil.copy2(source, target)
        elif not target.is_file():
            raise FileNotFoundError(f"vista geométrica ausente: {source} / {target}")
    for source, target in zip(FIELD_SEED_IMAGES, FIELD_IMAGES, strict=True):
        if source.is_file():
            shutil.copy2(source, target)
        elif not target.is_file():
            raise FileNotFoundError(f"plot de campo ausente: {source} / {target}")
    return {
        "article": create_article_crop(),
        "waveport": create_waveport_diagram(),
        "cuts": create_cut_diagram(),
        "convergence": create_convergence_plot(),
    }


def article_metrics() -> dict[str, int]:
    document = fitz.open(ARTICLE)
    text = "\n".join(page.get_text("text") for page in document)
    pages = document.page_count
    document.close()
    figures = {
        int(value) for value in re.findall(r"FIGURE\s+(\d+)", text, re.IGNORECASE)
    }
    tables = {int(value) for value in re.findall(r"TABLE\s+(\d+)", text, re.IGNORECASE)}
    return {
        "pages": pages,
        "words": len(re.findall(r"\b[\wÀ-ÿ]+\b", text, re.UNICODE)),
        "figures": len(figures),
        "tables": len(tables),
        "elements": len(figures) + len(tables),
    }


def build_story(
    styles: dict[str, ParagraphStyle],
    assets: dict[str, Path],
    metrics: dict[str, int],
) -> tuple[list[Any], int]:
    story: list[Any] = []
    page_width = A4[0] - 30 * mm
    story.extend(
        [
            Spacer(1, 24 * mm),
            Paragraph("Dossiê técnico da cavidade ENZ", styles["Title"]),
            Paragraph(
                "Geometria declarativa, teoria eletromagnética, cortes de campo, ambiente HFSS, diagramas de radiação e validação científica",
                styles["Subtitle"],
            ),
            Spacer(1, 5 * mm),
            HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#335C81")),
            Spacer(1, 9 * mm),
            Paragraph(
                "<b>Artigo-base creditado</b><br/>Evandro C. Vilas Boas, Sofia B. de Vasconcellos, Arismar Cerqueira Sodré Jr. e Felipe A. P. de Figueiredo<br/><i>A Millimeter-Wave Flat-Top Fan-Beam Antenna Array Based on a Geometry-Independent Resonant Cavity</i><br/>IEEE OJAP, 2026 — DOI 10.1109/OJAP.2026.3703713 — CC BY 4.0",
                styles["CoverInfo"],
            ),
            Spacer(1, 5 * mm),
            Paragraph(
                "<b>Organização técnica e repositório</b><br/>Projeto ENZ-Eigenchannel-mimo — coordenação de Geraldo César Simão",
                styles["CoverInfo"],
            ),
            Spacer(1, 10 * mm),
            Table(
                [
                    [
                        Paragraph(
                            '<b><font color="#A11B1B">HIPÓTESE</font></b>',
                            styles["CoverInfo"],
                        ),
                        Paragraph(
                            "A reconstrução HFSS v7 é exploratória e não reproduz validamente o artigo.",
                            styles["CoverInfo"],
                        ),
                    ],
                    [
                        Paragraph(
                            '<b><font color="#006B3C">SIMULADO</font></b>',
                            styles["CoverInfo"],
                        ),
                        Paragraph(
                            "AEDT 2024 R2, PyAEDT 1.3.0, gRPC nativo, 14 cores, malha convergida.",
                            styles["CoverInfo"],
                        ),
                    ],
                    [
                        Paragraph(
                            '<b><font color="#B42318">GATE</font></b>',
                            styles["CoverInfo"],
                        ),
                        Paragraph(
                            "Passividade e correspondência de S11 reprovadas; divergências preservadas.",
                            styles["CoverInfo"],
                        ),
                    ],
                ],
                colWidths=[32 * mm, page_width - 32 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F7F9")),
                        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#9AAAB7")),
                        (
                            "INNERGRID",
                            (0, 0),
                            (-1, -1),
                            0.35,
                            colors.HexColor("#C5CED5"),
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            ),
            Spacer(1, 14 * mm),
            Paragraph(
                f"Gate editorial: artigo com {metrics['words']:,} palavras recuperáveis e {metrics['elements']} figuras+tabelas; o PDF final exige ≥ {2 * metrics['words']:,} palavras e ≥ {2 * metrics['elements']} elementos técnicos.",
                styles["Small"],
            ),
            Spacer(1, 6 * mm),
            Paragraph(
                f"Versão 1 — gerada em {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
                styles["Small"],
            ),
            PageBreak(),
            Paragraph("Sumário", styles["Heading1"]),
        ]
    )
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            name="TOC1",
            fontName="TechSansBold",
            fontSize=8.5,
            leading=11,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=2,
        ),
        ParagraphStyle(
            name="TOC2",
            fontName="TechSans",
            fontSize=7.5,
            leading=9.5,
            leftIndent=8 * mm,
            firstLineIndent=0,
        ),
        ParagraphStyle(
            name="TOC3",
            fontName="TechSans",
            fontSize=6.8,
            leading=8.5,
            leftIndent=15 * mm,
            firstLineIndent=0,
            textColor=colors.HexColor("#4B5563"),
        ),
    ]
    story.extend(
        [
            toc,
            PageBreak(),
            Paragraph("Parte I — Síntese técnica e gates", styles["Heading1"]),
        ]
    )
    executive = CORE_DOCS[0].read_text(encoding="utf-8")
    render_markdown(executive, story, styles, page_width, skip_first_h1=True)
    story.extend(
        [PageBreak(), Paragraph("Parte II — Atlas visual", styles["Heading1"])]
    )

    visual_count = 0
    story.append(
        Paragraph("Dimensões publicadas e referência primária", styles["Heading2"])
    )
    story.extend(
        image_block(
            assets["article"],
            "**PUBLICADO.** Figura 2 do artigo-base, com dimensões e variações paramétricas. Fonte: Vilas Boas et al., IEEE OJAP, 2026, DOI 10.1109/OJAP.2026.3703713, CC BY 4.0. Recorte para auditoria; autoria preservada.",
            styles,
            page_width,
            118 * mm,
        )
    )
    visual_count += 1

    story.append(Paragraph("Vistas da geometria exploratória", styles["Heading2"]))
    geometry_entries = [
        (
            GEOMETRY_IMAGES[0],
            "**SIMULADO.** Vista isométrica da reconstrução exploratória versionada; não equivale ao CAD publicado.",
        ),
        (
            GEOMETRY_IMAGES[1],
            "**SIMULADO.** Vista frontal, destacando FR4 e seção transversal interna.",
        ),
        (
            GEOMETRY_IMAGES[2],
            "**SIMULADO.** Vista superior do corpo, flange e cinco ranhuras.",
        ),
    ]
    story.append(
        image_grid(geometry_entries, styles, page_width, columns=2, max_height=72 * mm)
    )
    visual_count += len(geometry_entries)

    story.append(Paragraph("Waveport e planos de corte", styles["Heading2"]))
    derived_entries = [
        (
            assets["waveport"],
            "**DERIVADO.** Auditoria da folha XZ e da linha de integração modal paralela a Z.",
        ),
        (
            assets["cuts"],
            "**DERIVADO.** Atlas esquemático dos oito cortes declarados na v7.",
        ),
    ]
    story.append(
        image_grid(derived_entries, styles, page_width, columns=1, max_height=102 * mm)
    )
    visual_count += len(derived_entries)

    story.append(Paragraph("Campos elétricos em cortes", styles["Heading2"]))
    field_entries = [
        (
            FIELD_IMAGES[0],
            "**SIMULADO.** |E| no corte ZX central, 25,87 GHz. Solução v6 geometricamente equivalente à v7 exceto pela sweep discreta adicional.",
        ),
        (
            FIELD_IMAGES[1],
            "**SIMULADO.** |E| no corte XY de meia-altura, 25,87 GHz.",
        ),
        (
            FIELD_IMAGES[2],
            "**SIMULADO.** |E| no corte YZ da primeira ranhura, 25,87 GHz.",
        ),
    ]
    story.append(
        image_grid(field_entries, styles, page_width, columns=1, max_height=103 * mm)
    )
    visual_count += len(field_entries)
    story.append(
        Paragraph(
            "<b>DERIVADO:</b> as imagens acima são vistas de magnitude. Os campos complexos permanecem nos resultados AEDT; não se infere fase, potência ou coerência apenas pela escala de cores.",
            styles["Quote"],
        )
    )

    story.append(Paragraph("Convergência, rede e potência", styles["Heading2"]))
    story.extend(
        image_block(
            assets["convergence"],
            "**SIMULADO.** Quatro passes adaptativos; ΔS final 0,0041377, abaixo da meta 0,02. A convergência numérica local não corrige a falha de passividade.",
            styles,
            page_width,
            95 * mm,
        )
    )
    visual_count += 1

    story.append(Paragraph("Relatórios e diagramas de radiação", styles["Heading2"]))
    report_captions = [
        "**SIMULADO.** S11 entre 25 e 27 GHz; a curva local diverge da banda publicada.",
        "**SIMULADO.** Eficiências de radiação e total; o valor acima de unidade reprova o gate estrito.",
        "**SIMULADO.** Ganho realizado de pico na sweep local.",
        "**SIMULADO.** E-plane co/cross em 25,87 GHz; valores absolutos em dB.",
        "**SIMULADO.** Segunda vista E-plane configurada para comparação com a Figura 3(d).",
        "**SIMULADO.** E-plane co/cross em 25,65, 25,87 e 26,22 GHz.",
        "**SIMULADO.** H-plane co/cross em 25,65, 25,87 e 26,22 GHz.",
        "**SIMULADO.** Diagrama tridimensional de ganho total em 25,87 GHz.",
    ]
    report_entries = list(zip(REPORT_IMAGES, report_captions, strict=True))
    story.append(
        image_grid(report_entries, styles, page_width, columns=2, max_height=67 * mm)
    )
    visual_count += len(report_entries)

    story.extend(
        [
            PageBreak(),
            Paragraph(
                "Parte III — Corpus teórico e reprodutibilidade", styles["Heading1"]
            ),
        ]
    )
    for path in CORE_DOCS[1:]:
        story.append(PageBreak())
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1) if title_match else path.stem
        story.append(Paragraph(inline_markup(title), styles["Heading1"]))
        story.append(
            Paragraph(
                f'Fonte interna consolidada: <font name="TechMono">{path.relative_to(ROOT).as_posix()}</font>',
                styles["Small"],
            )
        )
        render_markdown(text, story, styles, page_width, skip_first_h1=True)
    return story, visual_count


def validate_pdf(
    output: Path,
    article: dict[str, int],
    visual_count: int,
    markdown_tables: int,
) -> dict[str, Any]:
    reader = PdfReader(str(output), strict=True)
    if len(reader.pages) < 1:
        raise ValueError("PDF sem páginas")
    document = fitz.open(output)
    extracted = "\n".join(page.get_text("text") for page in document)
    pages = document.page_count
    document.close()
    words = len(re.findall(r"\b[\wÀ-ÿ]+\b", extracted, re.UNICODE))
    elements = visual_count + markdown_tables
    gates = {
        "pdf_header": output.read_bytes()[:5] == b"%PDF-",
        "pdf_eof": b"%%EOF" in output.read_bytes()[-8192:],
        "pypdf_strict_parse": True,
        "word_count_at_least_2x_article": words >= 2 * article["words"],
        "technical_elements_at_least_2x_article": elements >= 2 * article["elements"],
        "primary_doi_present": "10.1109/OJAP.2026.3703713" in extracted,
        "mandatory_claim_labels_present": all(
            label in extracted
            for label in (
                "PUBLICADO",
                "DERIVADO",
                "SIMULADO",
                "HIPÓTESE",
                "DESCONHECIDO",
            )
        ),
    }
    if not all(gates.values()):
        raise ValueError(f"gates do PDF falharam: {gates}")
    return {
        "pages": pages,
        "extracted_words": words,
        "visual_figures": visual_count,
        "markdown_tables": markdown_tables,
        "technical_elements": elements,
        "gates": gates,
    }


def generate() -> dict[str, Any]:
    assets = prepare_assets()
    required = [
        GENERATOR,
        ARTICLE,
        SPECIFICATION,
        VALIDATION,
        POSTPROCESSING,
        *CLEAN_METRICS,
        *CORE_DOCS,
        *GEOMETRY_IMAGES,
        *FIELD_IMAGES,
        *REPORT_IMAGES,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("fontes ausentes:\n" + "\n".join(missing))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    POROS_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    styles = build_styles()
    article = article_metrics()
    story, visual_count = build_story(styles, assets, article)
    markdown_tables = sum(
        count_markdown_tables(path.read_text(encoding="utf-8")) for path in CORE_DOCS
    )
    document = TechnicalDocTemplate(str(OUTPUT), styles)
    document.multiBuild(story)
    validation = validate_pdf(OUTPUT, article, visual_count, markdown_tables)
    sources = []
    for path in sorted(
        {
            GENERATOR,
            ARTICLE,
            SPECIFICATION,
            VALIDATION,
            POSTPROCESSING,
            *CLEAN_METRICS,
            *CORE_DOCS,
            *GEOMETRY_IMAGES,
            *FIELD_IMAGES,
            *REPORT_IMAGES,
            *assets.values(),
        }
    ):
        sources.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema": "enz-eigenchannel-mimo/technical-report-manifest/v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "classification": "HIPÓTESE",
        "title": "Dossiê técnico da cavidade ENZ e do ambiente HFSS",
        "primary_source": {
            "authors": [
                "Evandro C. Vilas Boas",
                "Sofia B. de Vasconcellos",
                "Arismar Cerqueira Sodré Jr.",
                "Felipe A. P. de Figueiredo",
            ],
            "doi": "10.1109/OJAP.2026.3703713",
            "license": "CC BY 4.0",
            "metrics": article,
        },
        "report": {
            "path": OUTPUT.relative_to(ROOT).as_posix(),
            "bytes": OUTPUT.stat().st_size,
            "sha256": sha256(OUTPUT),
            **validation,
        },
        "scientific_gates": {
            "waveport_integration_axis_z": "PASS",
            "adaptive_convergence": "PASS",
            "strict_passivity": "FAIL",
            "published_s11_correspondence": "FAIL",
            "global_reproduction_classification": "HIPÓTESE",
        },
        "sources": sources,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(OUTPUT, POROS_DIR / OUTPUT.name)
    shutil.copy2(MANIFEST, POROS_DIR / MANIFEST.name)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
