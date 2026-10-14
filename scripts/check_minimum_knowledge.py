"""Optional PDF authoring check; requires pypdf, unlike normal study tools.

--visual-reviewed records the operator's completed visual review. It does not
automatically judge layout, learner knowledge, or coverage of an actual exam.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).absolute().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--visual-reviewed", action="store_true", help="Record that the operator has inspected the latest rendered pages")
    args = parser.parse_args()
    source_path = ROOT / "MINIMUM-KNOWLEDGE.md"
    pdf_path = ROOT / "output/pdf/SK-hynix-minimum-AI-knowledge.pdf"
    source = source_path.read_text(encoding="utf-8-sig")
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages)
    urls = set(re.findall(r"\[[^\]]+\]\((https://[^)]+)\)", source))
    registered = {item["url"] for item in json.loads((ROOT / "research/sources.json").read_text(encoding="utf-8"))["sources"]}
    unregistered = sorted(urls - registered)
    lessons = re.findall(r"^## ([1-6]) ", source, re.MULTILINE)
    if lessons != list("123456") or unregistered or not 1 <= len(reader.pages) <= 16:
        raise ValueError("Check the six reading blocks, registered sources and PDF length")
    if not all((page.extract_text() or "").strip() for page in reader.pages):
        raise ValueError("PDF contains an empty text page")
    if "study.ps1 -Mode timed" not in text or not all(item in text for item in ["80%", "96%", "0.8"]):
        raise ValueError("Expected command or example figures are absent")
    tp, fp, fn, tn = 8, 2, 2, 88
    if not all([math.isclose(tp/(tp+fp), .8), math.isclose(tp/(tp+fn), .8),
                math.isclose((tp+tn)/(tp+fp+fn+tn), .96), math.isclose(2*tp/(2*tp+fp+fn), .8)]):
        raise ValueError("Classification example calculation disagrees")
    result = {"checked_on_kst": "2026-10-14", "reading_blocks": len(lessons), "source_characters": len(source),
              "pdf_pages": len(reader.pages), "linked_primary_urls": len(urls), "unregistered_urls": unregistered,
              "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
              "classification_example_independently_checked": True, "pdf_text_checked": True,
              "rendered_pages_visually_checked": args.visual_reviewed,
              "visual_check_mode": "operator_confirmed" if args.visual_reviewed else "not_confirmed",
              "limits": "File and rendering checks do not assess the learner or actual exam coverage."}
    (ROOT / "reports/minimum-knowledge-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
