"""Optional authoring tool for the complete Korean study book.

Requires reportlab and Korean TrueType fonts only when rebuilding the PDF.
Reading the PDF and running normal contest checks do not require these packages.
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
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).absolute().parents[1]
FONT_ROOT = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 43
CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2


def slug(value):
    return re.sub(r'[^\w\s-]', '', value.lower()).replace(' ', '-')


def table_cells(line):
    cells, current, code, escaped = [], [], False, False
    for char in line.strip().strip('|'):
        if escaped:
            current.append(char)
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '`':
            code = not code
            current.append(char)
        elif char == '|' and not code:
            cells.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append(''.join(current).strip())
    return cells


def inline(value, anchors):
    saved = []

    def link(match):
        label, url = match.groups()
        if url.startswith('#'):
            target = anchors.get(url[1:])
            if target is None:
                return label
            url = '#' + target
        elif not url.startswith(('https://', 'http://')):
            url = 'https://github.com/chan808/skhackathon/blob/main/etc/analysis/' + url
        saved.append('<link href="%s" color="#176482">%s</link>' % (escape(url, quote=True), escape(label)))
        return 'BOOKLINK%dPLACEHOLDER' % (len(saved)-1)

    def code(match):
        saved.append('<font color="#18536e">%s</font>' % escape(match.group(1)))
        return 'BOOKLINK%dPLACEHOLDER' % (len(saved)-1)

    protected = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, value)
    protected = re.sub(r'`([^`]+)`', code, protected)
    result = escape(protected)
    result = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', result)
    for index, item in enumerate(saved):
        result = result.replace('BOOKLINK%dPLACEHOLDER' % index, item)
    return result


class BookDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        key = getattr(flowable, '_book_key', None)
        if key is None:
            return
        self.canv.bookmarkPage(key)
        label = flowable.getPlainText()
        self.canv.addOutlineEntry(label, key, level=0, closed=False)
        self.notify('TOCEntry', (0, label, self.page, key))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#d4dfe7'))
    canvas.line(MARGIN, 35, PAGE_WIDTH-MARGIN, 35)
    canvas.setFillColor(colors.HexColor('#526979'))
    canvas.setFont('KR', 8)
    canvas.drawString(MARGIN, 22, 'AI 기초와 예선 문제 풀이 통합 교재 | 2026년 10월 15일')
    canvas.drawRightString(PAGE_WIDTH-MARGIN, 22, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'etc/analysis/study-guide.md')
    parser.add_argument('--output', type=Path, default=ROOT/'output/pdf/AI-prelim-complete-textbook.pdf')
    parser.add_argument('--font', type=Path, default=FONT_ROOT/'malgun.ttf')
    parser.add_argument('--bold-font', type=Path, default=FONT_ROOT/'malgunbd.ttf')
    args = parser.parse_args()
    pdfmetrics.registerFont(TTFont('KR', str(args.font)))
    pdfmetrics.registerFont(TTFont('KR-Bold', str(args.bold_font)))
    pdfmetrics.registerFontFamily('KR', normal='KR', bold='KR-Bold', italic='KR', boldItalic='KR-Bold')
    styles = {
        'title': ParagraphStyle('title', fontName='KR-Bold', fontSize=25, leading=36, spaceAfter=20, textColor=colors.HexColor('#163e58'), wordWrap='CJK'),
        'subtitle': ParagraphStyle('subtitle', fontName='KR', fontSize=13, leading=22, spaceAfter=16, textColor=colors.HexColor('#406477'), wordWrap='CJK'),
        'h2': ParagraphStyle('h2', fontName='KR-Bold', fontSize=17, leading=25, spaceAfter=15, textColor=colors.HexColor('#163e58'), wordWrap='CJK', keepWithNext=True),
        'h3': ParagraphStyle('h3', fontName='KR-Bold', fontSize=12, leading=18, spaceBefore=12, spaceAfter=7, textColor=colors.HexColor('#224b62'), wordWrap='CJK', keepWithNext=True),
        'h4': ParagraphStyle('h4', fontName='KR-Bold', fontSize=11, leading=17, spaceBefore=8, spaceAfter=6, wordWrap='CJK', keepWithNext=True),
        'answer_h3': ParagraphStyle('answer_h3', fontName='KR-Bold', fontSize=11, leading=17, spaceBefore=7, spaceAfter=5, textColor=colors.HexColor('#224b62'), wordWrap='CJK', keepWithNext=True),
        'body': ParagraphStyle('body', fontName='KR', fontSize=10.6, leading=17, spaceAfter=8, wordWrap='CJK'),
        'list': ParagraphStyle('list', fontName='KR', fontSize=10.6, leading=17, leftIndent=11, firstLineIndent=-6, spaceAfter=6, wordWrap='CJK'),
        'cell': ParagraphStyle('cell', fontName='KR', fontSize=9.4, leading=14, wordWrap='CJK'),
        'code': ParagraphStyle('code', fontName='KR', fontSize=9.1, leading=14, leftIndent=10, rightIndent=8, spaceAfter=3, wordWrap='CJK', backColor=colors.HexColor('#f0f5f8')),
        'toc': ParagraphStyle('toc', fontName='KR', fontSize=10.2, leading=16, leftIndent=6, firstLineIndent=-6, spaceBefore=5, wordWrap='CJK'),
    }
    source = args.source.read_text(encoding='utf-8-sig')
    headers = re.findall(r'^## (.+)$', source, re.M)
    anchors = {slug(text): 'section-%d' % index for index, text in enumerate(headers)}
    lines = source.splitlines()
    first_section = next(i for i,line in enumerate(lines) if line.startswith('## '))
    intro = '\n'.join(lines[1:first_section]).strip()
    story = [Spacer(1, 60), Paragraph('AI 기초와 예선 문제 풀이<br/>통합 교재', styles['title']),
             Paragraph('백엔드 개발자를 위한 개념 · 원리 · 사례 · 문제 · 해설', styles['subtitle'])]
    for paragraph in intro.split('\n\n'):
        if paragraph.strip():
            story.append(Paragraph(inline(paragraph.replace('\n',' '), anchors),styles['body']))
    story.extend([Spacer(1, 18), Paragraph('이 파일 안에서 정의부터 종합 연습까지 순서대로 읽습니다.', styles['subtitle']), PageBreak(),
                  Paragraph('목차', styles['h2'])])
    toc = TableOfContents()
    toc.levelStyles = [styles['toc']]
    toc.tableStyle = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
                                ('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])
    story.extend([toc, PageBreak()])
    index, buffer, code, skip_toc, section_index = first_section, [], False, False, 0
    question_start = None

    def flush():
        if buffer:
            paragraph = Paragraph(inline(' '.join(buffer), anchors), styles['body'])
            if buffer[0].startswith('최종적으로 다음 작업을'):
                paragraph.keepWithNext = True
            story.append(paragraph)
            buffer.clear()

    def close_question():
        nonlocal question_start
        if question_start is not None:
            block = story[question_start:]
            del story[question_start:]
            story.append(KeepTogether(block))
            question_start = None

    while index < len(lines):
        raw_line = lines[index].rstrip()
        line = raw_line if code else raw_line.strip()
        index += 1
        if line == '<!-- TOC_START -->':
            flush()
            skip_toc = True
            continue
        if line == '<!-- TOC_END -->':
            skip_toc = False
            continue
        if skip_toc:
            continue
        if line.startswith('```'):
            flush()
            code = not code
            story.append(Spacer(1,5))
            continue
        if code:
            text = escape(line).replace('  ', '&#160;&#160;') or '&#160;'
            story.append(Paragraph(text, styles['code']))
            continue
        if line.startswith('|'):
            flush()
            rows = [table_cells(line)]
            while index < len(lines) and lines[index].strip().startswith('|'):
                rows.append(table_cells(lines[index].strip()))
                index += 1
            rows = [row for row in rows if not all(re.fullmatch(r'[:\s-]+', cell) for cell in row)]
            columns = len(rows[0])
            if any(len(row) != columns for row in rows):
                raise ValueError('Unequal table columns near: ' + repr(rows[:2]))
            if columns == 2:
                widths = [CONTENT_WIDTH*.25, CONTENT_WIDTH*.75]
            elif columns == 3:
                widths = [CONTENT_WIDTH*.25, CONTENT_WIDTH*.37, CONTENT_WIDTH*.38]
            else:
                widths = [CONTENT_WIDTH/columns]*columns
            cells = [[Paragraph(inline(cell,anchors),styles['cell']) for cell in row] for row in rows]
            table = Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f5')),
                ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#cddae3')),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([KeepTogether([table]) if len(rows) <= 5 else table,Spacer(1,8)])
            continue
        if line.startswith('## '):
            flush()
            close_question()
            if section_index:
                story.append(PageBreak())
            paragraph = Paragraph(inline(line[3:],anchors),styles['h2'])
            paragraph._book_key = 'section-%d' % section_index
            story.append(paragraph)
            section_index += 1
            continue
        if line.startswith('### ') or line.startswith('#### '):
            flush()
            close_question()
            level = 'h4' if line.startswith('#### ') else 'h3'
            if re.match(r'^### M\d{2}\s',line):
                if '정답' in line:
                    level = 'answer_h3'
                else:
                    question_start = len(story)
            story.append(Paragraph(inline(line.split(' ',1)[1],anchors),styles[level]))
            continue
        if not line:
            flush()
            continue
        if line == '---' or line.startswith('<!--'):
            flush()
            continue
        if re.match(r'^\d+[.)]\s',line):
            flush()
            rows = [line]
            while index < len(lines):
                next_index = index
                while next_index < len(lines) and not lines[next_index].strip():
                    next_index += 1
                if next_index >= len(lines) or not re.match(r'^\d+[.)]\s',lines[next_index].strip()):
                    break
                rows.append(lines[next_index].strip())
                index = next_index + 1
            block = [Paragraph(inline(row,anchors),styles['list']) for row in rows]
            story.extend([KeepTogether(block)] if len(rows) <= 8 else block)
            continue
        if line.startswith(('- ', '* ', '> ')) or re.match(r'^[A-D]\.\s',line):
            flush()
            story.append(Paragraph(inline(line.removeprefix('> '),anchors),styles['list']))
            continue
        buffer.append(line)
    flush()
    close_question()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    document = BookDoc(str(args.output), pagesize=A4, leftMargin=MARGIN,rightMargin=MARGIN,topMargin=39,bottomMargin=49,
                       title='AI 기초와 예선 문제 풀이 통합 교재',author='SK hackathon study kit')
    document.addPageTemplates([PageTemplate(id='book',frames=[Frame(MARGIN,49,CONTENT_WIDTH,PAGE_HEIGHT-88,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer)])
    document.multiBuild(story)
    print(str(args.output))


if __name__ == '__main__':
    main()
