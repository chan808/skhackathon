"""Deterministic synthetic-data exercises using only Python's standard library."""
import csv
import json
import math
import random
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# absolute() avoids Windows final-path handle queries blocked by some sandboxes.
ROOT = Path(__file__).absolute().parents[1]
FIELDS = ["lot_id", "timestamp", "equipment", "product", "tested_dies", "good_dies", "temperature", "temperature_unit"]


def generate_rows():
    rng = random.Random(20261013)
    rows = []
    start = datetime(2026, 9, 1, 8)
    for index in range(240):
        day, position = divmod(index, 20)
        equipment = "E" + str(index % 3 + 1)
        product = "A" if index % 2 == 0 else "B"
        tested = rng.randint(600, 1200) if product == "A" else rng.randint(80, 180)
        defect_rate = 0.03 if product == "A" else 0.12
        if equipment == "E3" and day >= 8:
            defect_rate += 0.08
        bad = max(0, min(tested, round(tested * (defect_rate + rng.uniform(-0.01, 0.01)))))
        rows.append({
            "lot_id": "L%04d" % (index + 1),
            "timestamp": (start + timedelta(days=day, minutes=position * 30)).isoformat(),
            "equipment": equipment, "product": product,
            "tested_dies": str(tested), "good_dies": str(tested - bad),
            "temperature": str(round(70 + rng.uniform(-4, 4), 2)), "temperature_unit": "C",
        })
    # Explicit data-quality traps for training; not a physical process simulation.
    for index in [9, 39, 89]:
        rows[index]["good_dies"] = ""
    for index in [19, 59]:
        rows[index]["tested_dies"] = "0"
    for index in [29, 69]:
        rows[index]["good_dies"] = str(int(rows[index]["tested_dies"]) + 1)
    rows[79]["timestamp"] = "not-a-date"
    rows[99]["temperature"] = "158"
    rows[99]["temperature_unit"] = "F"
    rows.extend(dict(rows[index]) for index in [0, 1, 2, 3, 4])
    return rows


def write_dataset(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(generate_rows())


def read_dataset(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV columns do not match the exercise schema")
        return list(reader)


def clean_rows(rows):
    seen = {}
    accepted = []
    rejected = Counter()
    conversions = 0
    for row in rows:
        if set(row) != set(FIELDS) or any(not isinstance(row[field], str) for field in FIELDS) or not row["lot_id"].strip():
            rejected["invalid_row_shape"] += 1
            continue
        key = row["lot_id"]
        if key in seen:
            if row != seen[key]:
                raise ValueError("Conflicting duplicate lot_id: " + key)
            rejected["exact_duplicate"] += 1
            continue
        seen[key] = dict(row)
        try:
            timestamp = datetime.fromisoformat(row["timestamp"]).isoformat()
        except ValueError:
            rejected["invalid_timestamp"] += 1
            continue
        try:
            tested = int(row["tested_dies"])
            good = int(row["good_dies"])
        except ValueError:
            rejected["missing_or_invalid_count"] += 1
            continue
        if not 0 < tested <= 2**63 - 1 or not 0 <= good <= tested:
            rejected["invalid_count_range"] += 1
            continue
        try:
            temperature = float(row["temperature"])
            if not math.isfinite(temperature):
                raise ValueError("non-finite temperature")
            unit = row["temperature_unit"]
            if unit == "F":
                temperature = (temperature - 32) * 5 / 9
            elif unit != "C":
                raise ValueError("unknown temperature unit")
            if not math.isfinite(temperature):
                raise ValueError("conversion produced a non-finite temperature")
            if unit == "F":
                conversions += 1
        except ValueError:
            rejected["invalid_temperature"] += 1
            continue
        accepted.append({"lot_id": key, "timestamp": timestamp,
                         "equipment": row["equipment"], "product": row["product"],
                         "tested_dies": tested, "good_dies": good,
                         "temperature_c": temperature})
    return accepted, dict(rejected), conversions


def make_database(rows):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE lots (lot_id TEXT PRIMARY KEY, timestamp TEXT, equipment TEXT, product TEXT, tested_dies INTEGER, good_dies INTEGER, temperature_c REAL)")
    connection.executemany("INSERT INTO lots VALUES (:lot_id, :timestamp, :equipment, :product, :tested_dies, :good_dies, :temperature_c)", rows)
    return connection


def analyze(path):
    raw = read_dataset(path)
    clean, rejected, conversions = clean_rows(raw)
    if not clean:
        raise ValueError("No valid lots remain")
    tested = sum(row["tested_dies"] for row in clean)
    good = sum(row["good_dies"] for row in clean)
    weighted_yield = good / tested
    unweighted_yield = sum(row["good_dies"] / row["tested_dies"] for row in clean) / len(clean)
    connection = make_database(clean)
    sql_yield = connection.execute("SELECT 1.0 * SUM(good_dies) / SUM(tested_dies) FROM lots").fetchone()[0]
    groups = connection.execute("SELECT equipment, product, COUNT(*), SUM(tested_dies), SUM(good_dies), 1.0 * SUM(good_dies) / SUM(tested_dies) FROM lots GROUP BY equipment, product ORDER BY equipment, product").fetchall()
    periods = connection.execute("SELECT equipment, CASE WHEN timestamp < '2026-09-09' THEN 'before' ELSE 'after' END AS period, COUNT(*), 1.0 * SUM(good_dies) / SUM(tested_dies) FROM lots GROUP BY equipment, period ORDER BY equipment, period").fetchall()
    connection.close()
    if not math.isclose(weighted_yield, sql_yield, rel_tol=1e-12):
        raise AssertionError("Python and SQLite calculations disagree")
    return {"kind": "synthetic_training_only", "raw_rows": len(raw), "clean_rows": len(clean),
            "rejected": rejected, "temperature_conversions": conversions,
            "tested_dies": tested, "good_dies": good, "weighted_yield": weighted_yield,
            "unweighted_lot_yield": unweighted_yield, "sqlite_weighted_yield": sql_yield,
            "equipment_product": [dict(zip(["equipment", "product", "lots", "tested_dies", "good_dies", "yield"], row)) for row in groups],
            "equipment_period": [dict(zip(["equipment", "period", "lots", "yield"], row)) for row in periods],
            "interpretation": "This synthetic association does not prove a real manufacturing root cause."}


def load_quiz(path=None):
    path = Path(path) if path else ROOT / "practice" / "quiz.json"
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    ids = set()
    for question in document["questions"]:
        if question["id"] in ids:
            raise ValueError("Duplicate question ID")
        ids.add(question["id"])
        if len(question["options"]) != 4 or type(question["answer"]) is not int or not 0 <= question["answer"] < 4:
            raise ValueError("Invalid answer/options for " + question["id"])
        sources = question.get("source_urls")
        synthetic = question.get("source_type") == "synthetic_arithmetic_or_evidence"
        if (not question["explanation"] or not isinstance(sources, list)
                or any(not isinstance(url, str) or not url.startswith("https://") for url in sources)
                or (not sources and not synthetic)):
            raise ValueError("Missing explanation/source for " + question["id"])
    return document


def validate_answer(document):
    """Check shape and provenance references, without judging factual truth."""
    errors = []
    for key in ["answer", "claims", "limitations"]:
        if key not in document:
            errors.append("missing: " + key)
    if not isinstance(document.get("answer"), str) or not document.get("answer", "").strip():
        errors.append("answer must be a nonempty string")
    claims = document.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a nonempty list")
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append("claim %d must be an object" % index)
                continue
            for key in ["text", "source", "evidence"]:
                if not isinstance(claim.get(key), str) or not claim.get(key, "").strip():
                    errors.append("claim %d missing %s" % (index, key))
    if not isinstance(document.get("limitations"), list) or not all(isinstance(item, str) for item in document.get("limitations", [])):
        errors.append("limitations must be a list of strings")
    return errors
