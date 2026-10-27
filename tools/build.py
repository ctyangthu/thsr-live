"""Inline timetable + map data into src/app.html and write the site into dist/.

    python3 tools/build.py

dist/index.html     standalone page (GitHub Pages, or open directly in a browser)
dist/artifact.html  page body only, for hosts that add their own document skeleton
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "src" / "app.html").read_text(encoding="utf-8")
tt = json.loads((ROOT / "data" / "timetable-2026-02-02.json").read_text(encoding="utf-8"))
geo = json.loads((ROOT / "data" / "map.json").read_text(encoding="utf-8"))

compact = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
body = src.replace("__TIMETABLE_JSON__", compact(tt)).replace("__MAP_JSON__", compact(geo))
assert "__TIMETABLE_JSON__" not in body and "__MAP_JSON__" not in body

# title, fonts and styles come before the app markup; they belong in <head>
split = body.index('<div class="app">')
standalone = (
    '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="description" content="依台灣高鐵 2026/2/2 起適用時刻表，在台灣地圖上推算南港—左營列車位置，週一到週日各自套用不同班表。">\n'
    + body[:split] + "</head>\n<body>\n" + body[split:] + "\n</body>\n</html>\n"
)
dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
(dist / "index.html").write_text(standalone, encoding="utf-8")
(dist / "artifact.html").write_text(body, encoding="utf-8")
print(f"dist/index.html + dist/artifact.html written: {len(body.encode('utf-8')) / 1024:.1f} KB, {len(tt)} trains")
