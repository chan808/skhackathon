"""Render the standalone Korean minimum-knowledge booklet.

Optional authoring dependency: reportlab. Reading the shipped PDF and running
the study tools require no extra Python packages or model API account.
"""
import argparse
import os
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).absolute().parents[1]
FONT_ROOT = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"


def inline(text):
    text = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    links = []

    def link(match):
        label, target = match.groups()
        if not target.startswith("https://"):
            target = "https://github.com/chan808/skhackathon/blob/main/" + target.removeprefix("./")
        links.append(f'<link href="{escape(target, quote=True)}" color="#24617c">{escape(label)}</link>')
        return f"LINKPLACEHOLDER{len(links) - 1}END"

    result = escape(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text))
    result = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", result)
    result = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8.8">\1</font>', result)
    for index, value in enumerate(links):
        result = result.replace(f"LINKPLACEHOLDER{index}END", value)
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d4e0e8"))
    canvas.line(42, 36, A4[0] - 42, 36)
    canvas.setFont("KR", 8)
    canvas.setFillColor(colors.HexColor("#536574"))
    canvas.drawString(42, 23, "백엔드 개발자의 예선 사전 학습 | 2026년 10월 14일")
    canvas.drawRightString(A4[0] - 42, 23, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=FONT_ROOT / "malgun.ttf")
    parser.add_argument("--bold-font", type=Path, default=FONT_ROOT / "malgunbd.ttf")
    args = parser.parse_args()
    pdfmetrics.registerFont(TTFont("KR", str(args.font)))
    pdfmetrics.registerFont(TTFont("KR-Bold", str(args.bold_font)))
    pdfmetrics.registerFontFamily("KR", normal="KR", bold="KR-Bold", italic="KR", boldItalic="KR-Bold")
    styles = {
        "title": ParagraphStyle("title", fontName="KR-Bold", fontSize=20, leading=28, spaceAfter=10, textColor=colors.HexColor("#163d56"), wordWrap="CJK"),
        "h2": ParagraphStyle("h2", fontName="KR-Bold", fontSize=15, leading=22, spaceBefore=10, spaceAfter=10, textColor=colors.HexColor("#163d56"), wordWrap="CJK", keepWithNext=True),
        "h3": ParagraphStyle("h3", fontName="KR-Bold", fontSize=11.5, leading=17, spaceBefore=8, spaceAfter=5, wordWrap="CJK", keepWithNext=True),
        "body": ParagraphStyle("body", fontName="KR", fontSize=10.8, leading=16.5, spaceAfter=9, wordWrap="CJK"),
        "list": ParagraphStyle("list", fontName="KR", fontSize=10.4, leading=16, leftIndent=10, spaceAfter=6, wordWrap="CJK"),
        "cell": ParagraphStyle("cell", fontName="KR", fontSize=9.4, leading=14, wordWrap="CJK"),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8.1, leading=12, spaceAfter=3, wordWrap="LTR"),
    }
    lines = (ROOT / "MINIMUM-KNOWLEDGE.md").read_text(encoding="utf-8-sig").splitlines()
    story, paragraph, index, module_seen, code = [], [], 0, False, False

    def flush():
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), styles["body"]))
            paragraph.clear()

    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if line.startswith("```"):
            flush()
            code = not code
            story.append(Spacer(1, 5))
            continue
        if code:
            # Escape code rather than executing or interpreting it.
            story.append(Paragraph(escape(line), styles["code"]))
            continue
        if line.startswith("|"):
            flush()
            rows = [line]
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
            cells = [row for row in cells if not all(re.fullmatch(r"[:\s-]+", cell) for cell in row)]
            width = (A4[0] - 84) / len(cells[0])
            table = Table([[Paragraph(inline(cell), styles["cell"]) for cell in row] for row in cells], colWidths=[width] * len(cells[0]), repeatRows=1)
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9f1f5")), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1dce3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
            story.extend([table, Spacer(1, 8)])
            continue
        if line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), styles["title"]))
            continue
        if line.startswith("## "):
            flush()
            heading = line[3:]
            numbered = re.match(r"^[1-6]\s", heading) is not None
            if numbered:
                if module_seen:
                    story.append(PageBreak())
                module_seen = True
            elif module_seen:
                story.append(PageBreak())
            story.append(Paragraph(inline(heading), styles["h2"]))
            continue
        if line.startswith("### "):
            flush()
            story.append(Paragraph(inline(line[4:]), styles["h3"]))
            continue
        if not line:
            flush()
            continue
        if line.startswith("- ") or re.match(r"^\d+[.)]\s", line):
            flush()
            story.append(Paragraph(inline(line), styles["list"]))
            continue
        paragraph.append(line)
    flush()
    target = ROOT / "output" / "pdf" / "SK-hynix-minimum-AI-knowledge.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(target), pagesize=A4, leftMargin=42, rightMargin=42, topMargin=34, bottomMargin=52, title="백엔드 개발자를 위한 최소 AI 지식", author="SK hackathon study kit").build(story, onFirstPage=footer, onLaterPages=footer)
    print(str(target))


if __name__ == "__main__":
    main()
