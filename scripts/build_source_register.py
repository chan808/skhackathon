"""Merge provenance records without turning mirrors into independent evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
EXTRA = [
    {"title": "Python venv", "url": "https://docs.python.org/3/library/venv.html", "authority": "Python 공식", "supports": ["가상환경 생성과 직접 실행 및 재생성"]},
    {"title": "uv Using environments", "url": "https://docs.astral.sh/uv/pip/environments/", "authority": "Astral 공식", "supports": ["uv 가상환경 생성"]},
    {"title": "Python version status", "url": "https://devguide.python.org/versions/", "authority": "Python 공식", "supports": ["지원 상태와 Python 3.9 지원 종료"]},
]


def main():
    by_url = {}
    local_checks = []
    inputs = ["event-sources.json", "ai-sources.json", "semiconductor-sources.json", "readiness-sources.json", "agent-sources.json",
              "notice-sources.json", "foundation-sources.json", "advanced-quiz-sources.json", "setup-sources.json"]
    for filename in inputs:
        document = json.loads((ROOT / "research" / filename).read_text(encoding="utf-8-sig"))
        sources = document if isinstance(document, list) else document.get("sources", document.get("records", []))
        for source in sources:
            url = source.get("url")
            if not url:
                local_checks.append({"register": filename, **source})
                continue
            entry = by_url.setdefault(url, {"url": url, "title": source["title"], "records": []})
            entry["records"].append({"register": filename, **{key: value for key, value in source.items() if key != "url"}})
    for source in EXTRA:
        entry = by_url.setdefault(source["url"], {"url": source["url"], "title": source["title"], "records": []})
        entry["records"].append({"register": "preparation", "checked_on_kst": "2026-10-13", **{key: value for key, value in source.items() if key != "url"}})
    result = {"compiled_on_kst": "2026-10-14", "source_checks": "Individual check dates and access status are recorded per source.", "unique_url_count": len(by_url),
              "count_note": "URL 개수는 독립 근거 개수와 다르다. 동일 보도자료·미러·서로 다른 언어판·접근 제한은 records의 caveats를 따른다.",
              "local_checks": local_checks,
              "sources": sorted(by_url.values(), key=lambda item: item["url"])}
    output = ROOT / "research" / "sources.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 해커톤과 기술 조사 출처", "",
             "2026년 10월 14일 KST에 통합한 참고 URL이다. 원문별 확인 날짜는 등록부의 개별 기록을 따른다. URL 수는 독립적인 근거 수와 다르다. 동일 보도자료와 미러, 언어판을 중복 근거로 해석하지 않는다. 원 배포처의 접근 제한과 미확인 라이선스는 각 상세 조사와 JSON 등록부에 표시했다.", "",
             "세부 확인 범위와 날짜 및 한계는 [통합 등록부](sources.json)에 있다.", "",
             "| 출처 | 발행기관 또는 권위 | 확인 방식 |", "| --- | --- | --- |"]
    for entry in result["sources"]:
        record = entry["records"][0]
        title = entry["title"].replace("|", " ").replace("[", "").replace("]", "")
        publisher = record.get("publisher", record.get("authority", "공식 문서"))
        method = record.get("read_method", record.get("verification", "공식 본문 확인"))
        lines.append("| [%s](%s) | %s | %s |" % (title, entry["url"], str(publisher).replace("|", " "), str(method).replace("|", " ")))
    (ROOT / "research" / "SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Registered %d unique source URLs" % len(by_url))


if __name__ == "__main__":
    main()
