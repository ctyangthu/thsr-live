"""Parse the train tables of a THSR announcement page (saved HTML) into JSON.

    python3 tools/parse_announcement.py <page.html> <year> <out.json>

Each table: 方向 | 日期 | 車次 | 12 stations (southbound tables list 南港→左營,
northbound 左營→南港). "—" = passes without stopping, empty = outside the route.
"""
import sys, re, json, html, datetime

ZH = ["南港","台北","板橋","桃園","新竹","苗栗","台中","彰化","雲林","嘉義","台南","左營"]


def cells(tr):
    out = []
    for m in re.finditer(r"<t([dh])([^>]*)>(.*?)</t[dh]>", tr, re.S):
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(3)))).strip()
        rs = re.search(r'rowspan="?(\d+)', m.group(2))
        out.append((txt, int(rs.group(1)) if rs else 1))
    return out


def main(src, year, out_path):
    page = open(src, encoding="utf-8", errors="ignore").read()
    title = html.unescape(re.search(r"<title>(.*?)</title>", page, re.S).group(1)).split("–")[0].strip()
    trains = []
    for table in re.findall(r"<table.*?</table>", page, re.S):
        rows = [cells(tr) for tr in re.findall(r"<tr.*?</tr>", table, re.S)]
        head = [c[0] for c in rows[0]]
        if "車次" not in head: continue
        order = [ZH.index(h) for h in head[3:]]
        assert sorted(order) == list(range(12)), head
        carry = []  # values of rowspan cells (方向, 日期) still covering later rows
        for r in rows[1:]:
            vals = [c[0] for c in r]
            if carry and carry[0][1] > 0:
                vals = [c[0] for c in carry] + vals
                carry = [(v, n - 1) for v, n in carry]
            else:
                carry = [(c[0], c[1] - 1) for c in r[:2] if c[1] > 1]
            direction = {"南下": "S", "北上": "N"}[vals[0]]
            mo, d = re.match(r"(\d+)/(\d+)", vals[1]).groups()
            times = [None] * 12
            for col, v in zip(order, vals[3:]):
                times[col] = "─" if v in ("—", "-", "─") else (v or None)
            trains.append({"no": vals[2], "dir": direction,
                           "dates": [datetime.date(year, int(mo), int(d)).isoformat()], "t": times})
    json.dump({"title": title, "trains": trains}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{title}: {len(trains)} trains", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
