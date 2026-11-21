# 台灣高鐵動態系統

線上版：<https://ctyangthu.github.io/thsr-live/>

依台灣高鐵〈2026/2/2 起適用時刻表〉，在台灣地圖上推算南港—左營 12 站之間每一班列車的位置，以 N700ST 新世代列車呈現。

## 功能

- **依星期套用班表**：每日固定 131 班，其餘車次只在指定星期行駛，所以每天班次不同（一 156、二 149、三 149、四 158、五 179、六 161、日 182）。
- **特別疏運班表**：指定日期落在疏運期間時，改用該期間的時刻表。目前收錄〈2026 選舉疏運時刻表〉（11/27–11/30，各日 205／171／192／160 班），其中 11/27 另含 10 班深夜紅眼班次（最晚 01:59 抵達左營）。
- **即時與模擬**：預設使用台灣現在時間；可切換星期、指定日期、拖曳時間軸，並以 1×–900× 播放。凌晨 3 點前仍算前一天的班表，跨午夜的末班車與紅眼班次會繼續顯示。
- **地圖**：可拖曳與縮放，列車依實際靠左行駛，南下橘色、北上藍色，虛框表示停靠中。
- **列車詳情**：停靠與通過車站、下一站、估算時速、行駛日。
- **車站看板**：各站南下／北上接下來的班次。
- **時刻表**：南下／北上、本日行駛篩選、車次搜尋。

## 限制

- 列車位置依時刻表推算（每站停 1 分鐘，加減速為估算），不含誤點等即時資訊。
- 除 2026 選舉疏運外，其他國定假日與連假的疏運時刻表未納入。
- N700ST 依新聞報導預計 2027 年 7 月 1 日投入營運；本系統以 N700ST 呈現所有車次。

## 專案結構

```
src/app.html                      網頁原始碼（資料以佔位字串嵌入）
data/timetable-2026-02-02.json    由官方 PDF 解析出的 214 個車次與行駛日
data/counties-10t.json            縣市界 TopoJSON（taiwan-atlas）
data/map.json                     投影並簡化後的地圖路徑
data/specials.json                特別疏運期間設定（時刻表檔、加開班次、公告連結）
data/special-2026-election.json   2026 選舉疏運時刻表（228 車次，含各車次行駛日期）
data/special-2026-11-27-redeye.json  11/27 紅眼班次公告（10 車次）
tools/parse_timetable.py          解析高鐵時刻表 PDF（需要 pdfplumber）
tools/parse_special.py            解析疏運時刻表 PDF（行駛日為日期）
tools/parse_announcement.py       解析高鐵公告網頁中的車次表
tools/build_map.py                產生 data/map.json
tools/build.py                    組出 dist/index.html
```

## 建置

```bash
python3 tools/build.py
```

產出的 `dist/index.html` 可直接用瀏覽器開啟。推送到 `main` 後，GitHub Actions 會自動建置並部署到 GitHub Pages。

更新時刻表時，先下載新的 PDF，再執行：

```bash
python3 tools/parse_timetable.py 新時刻表.pdf data/timetable-2026-02-02.json
python3 tools/build.py
```

加入疏運時刻表：解析 PDF 與公告網頁後，在 `data/specials.json` 新增一筆期間設定，再重新建置。

```bash
python3 tools/parse_special.py 疏運時刻表.pdf 2026 data/special-XXXX.json
python3 tools/parse_announcement.py 公告.html 2026 data/special-XXXX-extra.json
python3 tools/build.py
```

## 資料來源

- 時刻表：[台灣高鐵〈2026/2/2 起適用時刻表〉與〈2026 選舉疏運時刻表〉](https://www.thsrc.com.tw/ArticleContent/a3b630bb-1066-4352-a1ef-58c7b4e8ef7c)
- 紅眼班次：[11/27(五)提供10班「紅眼班次」全面77折](https://www.thsrc.com.tw/ArticleContent/25425adb-288e-4a11-95ea-71e45184c4be)
- 地圖：[taiwan-atlas](https://github.com/dkaoster/taiwan-atlas)（原始資料為內政部國土測繪中心開放資料）
