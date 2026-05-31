from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

if TYPE_CHECKING:
    from docx.document import Document as DocxDocument

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import DOCS_DIR, OUTPUT_DOC_DIR


def clean_inline_markdown(text: str) -> str:
    text = text.replace("`", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    return text.strip()


def add_heading(document: "DocxDocument", text: str, level: int) -> None:
    heading = document.add_heading(clean_inline_markdown(text), level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT


def add_paragraph(document: "DocxDocument", text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.line_spacing = 1.05
    run = paragraph.add_run(clean_inline_markdown(text))
    run.font.name = "Calibri"
    run.font.size = Pt(10)


def add_bullet(document: "DocxDocument", text: str) -> None:
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run(clean_inline_markdown(text))
    run.font.name = "Calibri"
    run.font.size = Pt(10)


def add_quote(document: "DocxDocument", text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.25)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.05
    run = paragraph.add_run(clean_inline_markdown(text))
    run.italic = True
    run.font.name = "Calibri"
    run.font.size = Pt(10)


def add_code(document: "DocxDocument", text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.2)
    paragraph.paragraph_format.space_after = Pt(4)
    run = paragraph.add_run(text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(9)


def build_document() -> "DocxDocument":
    source_path = DOCS_DIR / "guia_celulas_notebook.md"
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

    in_code_block = False
    code_lines: list[str] = []

    for raw_line in source_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code_block:
                add_code(document, "\n".join(code_lines))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not line.strip():
            continue

        if line.startswith("# "):
            title = document.add_heading(clean_inline_markdown(line[2:]), level=0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle = document.add_paragraph("Apoio de fala para demonstrar o notebook de EDA")
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle.runs[0].font.size = Pt(10)
        elif line.startswith("## "):
            add_heading(document, line[3:], level=1)
        elif line.startswith("### "):
            add_heading(document, line[4:], level=2)
        elif line.startswith("> "):
            add_quote(document, line[2:])
        elif line.startswith("- "):
            add_bullet(document, line[2:])
        else:
            add_paragraph(document, line)

    if code_lines:
        add_code(document, "\n".join(code_lines))

    return document


def main() -> None:
    OUTPUT_DOC_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DOC_DIR / "guia_celulas_notebook.docx"
    document = build_document()
    document.save(output_path)
    print(output_path)


if __name__ == "__main__":
    main()
