"""Parse a THSR special-period timetable PDF (e.g. 2026選舉疏運時刻表) into JSON.

    python3 tools/parse_special.py <pdf> <year> <out.json>

These PDFs list one table per page: train no, operating dates (blank = every day
of the period), then 12 station columns. Cells are assigned to columns by x position.
Times "HH:MM", "-" = passes without stopping, empty = outside the train's route.
"""
import sys, re, json, datetime, pdfplumber

EN = ["Nangang","Taipei","Banqiao","Taoyuan","Hsinchu","Miaoli","Taichung","Changhua","Yunlin","Chiayi","Tainan","Zuoying"]


def expand_dates(text, year, period):
    """'11/27~11/28, 11/30' -> ['2026-11-27','2026-11-28','2026-11-30']; '' -> whole period."""
    if not text.strip():
        return list(period)
    out = []
    for part in re.split(r"[,，]\s*", text.strip().rstrip(",")):
        a, _, b = part.partition("~")
        d0 = datetime.date(year, *map(int, a.split("/")))
        d1 = datetime.date(year, *map(int, b.split("/"))) if b else d0
        while d0 <= d1:
            out.append(d0.isoformat()); d0 += datetime.timedelta(days=1)
    bad = [d for d in out if d not in period]
    if bad:
        raise ValueError(f"dates outside period: {bad} ({text})")
    return out


def main(pdf_path, year, out_path):
    pdf = pdfplumber.open(pdf_path)
    first = pdf.pages[0].extract_text()
    m = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})~(\d{4})/(\d{1,2})/(\d{1,2})", first)
    d0 = datetime.date(int(m[1]), int(m[2]), int(m[3])); d1 = datetime.date(int(m[4]), int(m[5]), int(m[6]))
    period = []
    while d0 <= d1:
        period.append(d0.isoformat()); d0 += datetime.timedelta(days=1)
    trains = []
    for pi, pg in enumerate(pdf.pages):
        ws = pg.extract_words()
        head = [w for w in ws if w["text"] in EN]
        hy = min(w["top"] for w in head)
        head = sorted([w for w in head if abs(w["top"] - hy) < 3], key=lambda w: w["x0"])
        names = [w["text"] for w in head]
        assert len(names) == 12, (pi, names)
        direction = "S" if names[0] == "Nangang" else "N"
        cols = [(w["x0"] + w["x1"]) / 2 for w in head]
        day_x0, day_x1 = 75, cols[0] - 25   # between the train-no column and the first station
        body = [w for w in ws if w["top"] > hy + 4]
        for t in [w for w in body if re.fullmatch(r"\d{3,4}", w["text"]) and w["x0"] < 80]:
            row = [w for w in body if abs(w["top"] - t["top"]) < 3 and w is not t]
            days = " ".join(w["text"] for w in sorted(row, key=lambda w: w["x0"]) if day_x0 < w["x0"] < day_x1)
            times = [None] * 12
            for w in row:
                if w["x0"] < day_x1: continue
                cx = (w["x0"] + w["x1"]) / 2
                i = min(range(12), key=lambda k: abs(cols[k] - cx))
                if abs(cols[i] - cx) > 20:
                    raise ValueError(f"cell far from column: {t['text']} {w['text']}")
                if re.fullmatch(r"\d\d:\d\d", w["text"]): times[i] = w["text"]
                elif w["text"] in ("-", "─", "—"): times[i] = "─"
                else: raise ValueError(f"unexpected cell: {t['text']} {w['text']!r}")
            if direction == "N": times = times[::-1]   # store north -> south like the regular data
            trains.append({"no": t["text"], "dir": direction, "dates": expand_dates(days, year, period), "t": times})
    out = {"from": period[0], "to": period[-1], "trains": trains}
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(trains)} trains, period {period[0]}..{period[-1]}", file=sys.stderr)
    for d in period:
        n = [x for x in trains if d in x["dates"]]
        print(f"  {d}: {len(n)} trains (S {sum(x['dir']=='S' for x in n)} / N {sum(x['dir']=='N' for x in n)})", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
