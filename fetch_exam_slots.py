#!/usr/bin/env python3
"""
Fetch exam slots from https://iitg.ac.in/acad/offered_courses.php
and update the exam_slot column in data/courses_csv.csv by matching course codes.

Usage:
    python fetch_exam_slots.py
    python fetch_exam_slots.py --semester July26.xlsx|exam_slot_july_nov_2026.pdf
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import re
import argparse

# ── Config ────────────────────────────────────────────────────────────────────

# Default to the current semester (July-Nov 2026). Change if needed.
DEFAULT_SEASON = "July26.xlsx|exam_slot_july_nov_2026.pdf"

TABLE_URL = "https://iitg.ac.in/acad/excel_files/offered_courses/table.part.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://iitg.ac.in/acad/offered_courses.php",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Determine data directory (same logic as rest of the project)
if os.path.exists("/code"):
    DATA_DIR = "/code/data"
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

CSV_PATH = os.path.join(DATA_DIR, "courses_csv.csv")


# ── Helpers ───────────────────────────────────────────────────────────────────

def normalize_code(code: str) -> str:
    """Strip all whitespace from a course code (e.g. 'ME 679' → 'ME679')."""
    return re.sub(r"\s+", "", str(code)).upper()


def fetch_exam_slot_map(season: str) -> dict:
    """
    Fetch the offered-courses table for *season* and return a dict
    mapping  normalized_course_code → exam_slot  (first slot found wins).

    Exam slots like 'NA', '--', '' are stored as empty string.
    """
    print(f"🌐 Fetching offered courses for season: {season}")
    resp = requests.get(TABLE_URL, params={"season": season}, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="dataTable")
    if not table:
        raise ValueError(
            "Could not find <table id='dataTable'> in the response. "
            "The page structure may have changed."
        )

    # Parse header row to find column indices
    thead = table.find("thead")
    header_cells = thead.find("tr").find_all("th")
    headers = [th.get_text(strip=True) for th in header_cells]

    try:
        code_idx = next(
            i for i, h in enumerate(headers)
            if "course" in h.lower() and "code" in h.lower()
        )
        slot_idx = next(
            i for i, h in enumerate(headers)
            if "exam" in h.lower() and "slot" in h.lower()
        )
    except StopIteration:
        raise ValueError(f"Could not locate required columns in headers: {headers}")

    print(f"   → Columns found: code={headers[code_idx]!r}, slot={headers[slot_idx]!r}")

    exam_map: dict[str, str] = {}
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) <= max(code_idx, slot_idx):
            continue

        raw_code = cells[code_idx].get_text(strip=True)
        raw_slot = cells[slot_idx].get_text(strip=True)

        code = normalize_code(raw_code)
        # Treat 'NA', '--', '' as no exam slot
        slot = "" if raw_slot.upper() in ("NA", "--", "") else raw_slot.strip()

        if code and code not in exam_map:
            # First occurrence wins (keeps it deterministic for duplicate rows)
            exam_map[code] = slot

    print(f"✅ Scraped {len(exam_map)} unique course codes from offered courses page.")
    return exam_map


def update_csv(exam_map: dict, csv_path: str) -> None:
    """
    Read courses_csv.csv, fill the exam_slot column where a match is found,
    then overwrite the file. All other columns are left untouched.
    """
    print(f"\n📂 Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path, dtype=str)

    if "exam_slot" not in df.columns:
        print("⚠️  'exam_slot' column not found – adding it now.")
        df["exam_slot"] = ""

    filled = 0
    skipped = 0
    not_found = 0

    for idx, row in df.iterrows():
        norm = normalize_code(str(row["code"]))
        if norm in exam_map:
            new_slot = exam_map[norm]
            existing = str(row["exam_slot"]) if pd.notna(row["exam_slot"]) else ""
            if existing.strip() and existing.strip() == new_slot:
                # Already correct – no change needed
                skipped += 1
            else:
                df.at[idx, "exam_slot"] = new_slot
                if new_slot:
                    filled += 1
        else:
            not_found += 1

    df.to_csv(csv_path, index=False)

    print(f"\n📊 Update summary:")
    print(f"   ✏️  Exam slots written / updated : {filled}")
    print(f"   ✔️  Already correct (no change)  : {skipped}")
    print(f"   ❓  Course codes not in web data  : {not_found}")
    print(f"\n💾 Saved updated CSV → {csv_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch exam slots from IITG offered-courses page and update courses_csv.csv"
    )
    parser.add_argument(
        "--semester",
        default=DEFAULT_SEASON,
        help=(
            "Season string used by the IITG table endpoint, e.g. "
            "'July26.xlsx|exam_slot_july_nov_2026.pdf' (default). "
            "Other options: 'Jan26.xlsx|exam_slot_ jan_may_2026.pdf', etc."
        ),
    )
    parser.add_argument(
        "--csv",
        default=CSV_PATH,
        help=f"Path to courses_csv.csv (default: {CSV_PATH})",
    )
    args = parser.parse_args()

    try:
        exam_map = fetch_exam_slot_map(args.semester)
        update_csv(exam_map, args.csv)
        print("\n🎉 Done!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
