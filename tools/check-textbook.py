"""Optional authoring QA for the standalone book; requires pypdf/pdfplumber/reportlab.

--visual-reviewed records completed human inspection of the rendered final PDF.
It does not assess a learner or guarantee actual exam coverage.
"""
import argparse
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pdfplumber
from pypdf import PdfReader
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).absolute().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--visual-reviewed', action='store_true')
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/malgun.ttf'))
    args = parser.parse_args()
    source_path = ROOT/'etc/analysis/study-guide.md'
    pdf_path = ROOT/'output/pdf/AI-prelim-complete-textbook.pdf'
    source = source_path.read_text(encoding='utf-8')
    chapters = list(map(int,re.findall(r'^## (\d+)장(?:\s|$)',source,re.M)))
    if chapters != list(range(22)):
        raise ValueError('Expected introduction0 and chapters1 through21')
    a_labels = re.findall(r'^\*\*A(\d+)\.\*\*',source,re.M)
    if Counter(a_labels) != Counter({str(i):2 for i in range(1,13)}):
        raise ValueError('Core self-check questions/answers incomplete')
    b_labels = re.findall(r'^\*\*자기 점검 (\d+[AB])\.\*\*',source,re.M)
    c_labels = re.findall(r'^\*\*문제 (\d+-[AB])\.\*\*',source,re.M)
    if set(b_labels) != {str(i)+letter for i in range(7,12) for letter in 'AB'}:
        raise ValueError('Data/evaluation self-checks incomplete')
    if set(c_labels) != {str(i)+'-'+letter for i in range(12,17) for letter in 'AB'}:
        raise ValueError('Risk/workflow self-checks incomplete')
    question_block = source.split('## 18장',1)[1].split('## 19장',1)[0]
    questions = re.findall(r'^### M(\d{2})\s',question_block,re.M)
    if questions != [str(i).zfill(2) for i in range(1,21)]:
        raise ValueError('Integrated question sequence incomplete')
    if any(len(re.findall(r'^'+letter+r'\.\s',question_block,re.M)) != 20 for letter in 'ABCD'):
        raise ValueError('Every integrated question needs four choices')
    answers = re.findall(r'^### M(\d{2}) 정답 ([A-D])$',source,re.M)
    intended = 'BDACDB C A B D A C D B A C B A D C'.replace(' ','')
    if ''.join(letter for _,letter in answers) != intended or len(answers) != 20:
        raise ValueError('Reviewed answer key changed')
    glossary = source.split('## 20장',1)[1].split('## 21장',1)[0]
    glossary_entries = sum(1 for line in glossary.splitlines() if line.startswith('|')
                           and not re.fullmatch(r'[|\s:-]+',line) and not line.startswith('| 용어 |'))
    calculations = {
        'case_snack': 6 == 3+3 and 4 == 3+1,
        'case_subscription': 12*40 == 480 and 12*28 + (42000-12*3000)*.01 == 396 and 10*28+(42000-10*3000)*.01 == 400,
        'case_temperature': math.isclose((158-32)*5/9,70),
        'gradient_step': math.isclose(1-.1*(-8),1.8) and math.isclose((1.8*2-4)**2,.16),
        'chapter_confusion': math.isclose((18+68)/100,.86) and math.isclose(18/30,.6) and math.isclose(18/20,.9) and math.isclose(36/50,.72),
        'threshold_costs': 8*10+2 == 82 and 2*10+18 == 38,
        'question_confusion': math.isclose(12/15,.8) and math.isclose(12/16,.75),
        'weighted_ratio': math.isclose(100/120,5/6),
        'regression_errors': math.isclose((1+2)/2,1.5) and math.isclose((1+4)/2,2.5),
        'call_budget': (18000-4000)//3500 == 4 and math.ceil(20/4)+2 == 7,
    }
    if not all(calculations.values()):
        raise ValueError('Independent arithmetic checks failed')
    font = TTFont('qa-font',str(args.font))
    missing_glyphs = sorted(c for c in set(source) if c.isprintable() and ord(c) not in font.face.charToGlyph)
    if missing_glyphs:
        raise ValueError('Missing font glyphs: ' + repr(missing_glyphs))
    reader = PdfReader(pdf_path)
    texts = [page.extract_text() or '' for page in reader.pages]
    if any(len(text.strip()) < 70 for text in texts):
        raise ValueError('PDF has an unexpectedly empty text page')
    combined = '\n'.join(texts)
    if any(token in combined for token in ['BOOKLINK','PLACEHOLDER','AUTO_TOC']):
        raise ValueError('Unresolved authoring marker in PDF')
    if len(reader.outline) != 23:
        raise ValueError('PDF bookmarks incomplete')
    for destination in reader.outline:
        page_number = reader.get_destination_page_number(destination)
        if re.sub(r'\s+','',destination.title) not in re.sub(r'\s+','',texts[page_number]):
            raise ValueError('Bookmark does not point to its heading')
    layout_issues = []
    with pdfplumber.open(pdf_path) as document:
        for index,page in enumerate(document.pages,1):
            for char in page.chars:
                if (char['x0'] < 34 or char['x1'] > page.width-34 or char['top'] < 18 or char['bottom'] > page.height-15):
                    layout_issues.append({'page':index,'character':char['text']})
                    break
    if layout_issues:
        raise ValueError('Text outside layout bounds: ' + repr(layout_issues))
    result = {
        'checked_at_kst': datetime.now(timezone(timedelta(hours=9))).isoformat(),
        'source_characters':len(source),'source_lines':len(source.splitlines()),
        'core_chapters':16,'worked_cases':3,'self_check_questions':12+len(b_labels)+len(c_labels),
        'integrated_questions':len(questions),'total_questions':12+len(b_labels)+len(c_labels)+len(questions),
        'glossary_entries':glossary_entries,'pdf_pages':len(reader.pages),'pdf_bookmarks':len(reader.outline),
        'linked_reference_urls':len(set(re.findall(r'\]\((https://[^)]+)\)',source))),
        'answer_key_distribution':dict(Counter(letter for _,letter in answers)),
        'independent_arithmetic_checks':calculations,'missing_glyphs':missing_glyphs,'layout_geometry_issues':layout_issues,
        'rendered_pages_visually_checked':args.visual_reviewed,
        'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'pdf_sha256':hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        'limits':'Authoring, arithmetic and rendering checks; does not establish exam coverage, learner readiness or real exam access.'}
    target = ROOT/'etc/analysis/study-guide-check.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
