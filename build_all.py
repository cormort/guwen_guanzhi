#!/usr/bin/env python3
"""Build Phase 2 article detail pages + update index.html for both phases."""

import os, re, json, markdown

SITE_DIR = "/tmp/guwen_final"
PHASE2 = os.path.join(SITE_DIR, "phase2")
OUTPUT_DIR = os.path.join(SITE_DIR, "articles")

PHASE2_ESSAYS = [
    ("31-shique", "石碏諫寵州吁", "左丘明", "左傳·隱公三年"),
    ("32-zangxibo", "臧僖伯諫觀魚", "左丘明", "左傳·隱公五年"),
    ("33-jiliang", "季梁諫追楚師", "左丘明", "左傳·桓公六年"),
    ("34-qihuan-gong", "齊桓公伐楚盟屈完", "左丘明", "左傳·僖公四年"),
    ("35-ziyu", "子魚論戰", "左丘明", "左傳·僖公二十二年"),
    ("36-jiezhitui", "介之推不言祿", "左丘明", "左傳·僖公二十四年"),
    ("37-yanzi", "晏子不死君難", "左丘明", "左傳·襄公二十五年"),
    ("38-zichan", "子產不毀鄉校", "左丘明", "左傳·襄公三十一年"),
    ("39-jingjiang", "敬姜論勞逸", "左丘明", "國語·魯語"),
    ("40-goujian", "勾踐滅吳", "左丘明", "國語·越語"),
    ("41-suqin", "蘇秦以連橫說秦", "劉向", "戰國策·秦策"),
    ("42-simacuo", "司馬錯論伐蜀", "劉向", "戰國策·秦策"),
    ("43-zhaoweihou", "趙威后問齊使", "劉向", "戰國策·齊策"),
    ("44-boyi", "伯夷列傳", "司馬遷", "史記"),
    ("45-quyuan", "屈原列傳", "司馬遷", "史記"),
    ("46-huaji", "滑稽列傳", "司馬遷", "史記"),
    ("47-guogin", "過秦論", "賈誼", "漢文"),
    ("48-da-suwu", "答蘇武書", "李陵", "漢文"),
    ("49-yuzhong", "獄中上梁王書", "鄒陽", "漢文"),
    ("50-shangde", "尚德緩刑書", "路溫舒", "漢文"),
    ("51-beishan", "北山移文", "孔稚珪", "六朝文"),
    ("52-weixu-jingye", "為徐敬業討武曌檄", "駱賓王", "唐文"),
    ("53-tengwang-ge", "滕王閣序", "王勃", "唐文"),
    ("54-yu-han", "與韓荊州書", "李白", "唐文"),
    ("55-yuandao", "原道", "韓愈", "唐文"),
    ("56-mashuo", "雜說四·馬說", "韓愈", "唐文"),
    ("57-jinxue-jie", "進學解", "韓愈", "唐文"),
    ("58-song-liyuan", "送李愿歸盤谷序", "韓愈", "唐文"),
    ("59-song-dongshao", "送董邵南序", "韓愈", "唐文"),
    ("60-bushezhe", "捕蛇者說", "柳宗元", "唐文"),
    ("61-zhongshu", "種樹郭橐駝傳", "柳宗元", "唐文"),
    ("62-yuxi", "愚溪詩序", "柳宗元", "唐文"),
    ("63-dai-zhuiye", "桐葉封弟辨", "柳宗元", "唐文"),
    ("64-huanggang", "黃岡竹樓記", "王禹偁", "宋文"),
    ("65-zongqiu", "縱囚論", "歐陽脩", "宋文"),
    ("66-bianjian", "辨姦論", "蘇洵", "宋文"),
    ("67-kuangzai", "黃州快哉亭記", "蘇轍", "宋文"),
    ("68-fengle", "豐樂亭記", "歐陽脩", "宋文"),
    ("69-chibifu2", "後赤壁賦", "蘇軾", "宋文"),
    ("70-shizhong", "石鐘山記", "蘇軾", "宋文"),
    ("71-fangshan", "方山子傳", "蘇軾", "宋文"),
    ("72-da-sima", "答司馬諫議書", "王安石", "宋文"),
    ("73-shang-zhongyong", "傷仲永", "王安石", "宋文"),
    ("74-yitian", "義田記", "錢公輔", "宋文"),
    ("75-canglang", "滄浪亭記", "蘇舜欽", "宋文"),
    ("76-chaozhou", "潮州韓文公廟碑", "蘇軾", "宋文"),
    ("77-longan", "瀧岡阡表", "歐陽脩", "宋文"),
    ("78-song-dongyang", "送東陽馬生序", "宋濂", "明文"),
    ("79-xiangling", "項脊軒志", "歸有光", "明文"),
    ("80-lianchi", "廉恥", "顧炎武", "清文"),
]

ALL_ESSAYS = []  # Will be combined from index.html data + phase2

def read_md(dirpath, filename):
    path = os.path.join(dirpath, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def md_to_html(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])

def build_article(eid, title, author, era, bg_md, analysis_md, prev_link, next_link):
    bg_html = md_to_html(bg_md)
    analysis_html = md_to_html(analysis_md)
    nav_links_html = "".join(
        f'<a href="{l["href"]}" class="nav-{l["cls"]}">{l["text"]}</a>'
        for l in [prev_link, next_link] if l
    )

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — 古文觀止導覽</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/article.css">
</head>
<body class="article-page">
    <nav class="article-nav">
        <a href="../index.html" class="nav-home">← 回目錄</a>
        <span class="nav-pos">{title}</span>
        <div class="nav-links">{nav_links_html}</div>
    </nav>

    <article class="article-container">
        <header class="article-header">
            <h1>{title}</h1>
            <p class="article-meta">{author} · {era}</p>
        </header>

        <section class="article-section bg-section">
            <h2>📜 時代背景與寫作意旨</h2>
            <div class="section-content">{bg_html}</div>
        </section>

        <section class="article-section analysis-section">
            <h2>📖 文章分析</h2>
            <div class="section-content">{analysis_html}</div>
        </section>
    </article>

    <nav class="article-footer-nav">
        {prev_link_s if prev_link else '<span></span>' if not next_link else ''}
        <a href="../index.html" class="nav-home">← 回目錄</a>
        {next_link_s if next_link else '<span></span>' if not prev_link else ''}
    </nav>

    <footer>
        <p>github.com/cormort/guwen_guanzhi · 全 222 篇建置中</p>
    </footer>
</body>
</html>"""

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Combine Phase 1 essays (from index.html) + Phase 2
# Read Phase 1 essays from index.html
import html as html_mod

all_essays = []

# Phase 1 essays (parsed from index.html JS)
phase1_titles = [
    ("01-zhengbo-keduan", "鄭伯克段于鄢", "左丘明", "左傳·隱公元年"),
    ("02-caogui-lunzhan", "曹劌論戰", "左丘明", "左傳·莊公十年"),
    ("03-gongzhiqi", "宮之奇諫假道", "左丘明", "左傳·僖公五年"),
    ("04-zhuwuzhi", "燭之武退秦師", "左丘明", "左傳·僖公三十年"),
    ("05-jianshu", "蹇叔哭師", "左丘明", "左傳·僖公三十二年"),
    ("06-zhaogong", "召公諫厲王止謗", "左丘明", "國語·周語"),
    ("07-zouji", "鄒忌諷齊王納諫", "劉向", "戰國策·齊策"),
    ("08-chuzhe", "觸讋說趙太后", "劉向", "戰國策·趙策"),
    ("09-fengxuan", "馮諼客孟嘗君", "劉向", "戰國策·齊策"),
    ("10-jianzhuke", "諫逐客書", "李斯", "秦文"),
    ("11-buju", "卜居", "屈原", "楚辭"),
    ("12-hongmen", "鴻門宴", "司馬遷", "史記·項羽本紀"),
    ("13-baoren", "報任少卿書", "司馬遷", "漢文"),
    ("14-chushi", "出師表", "諸葛亮", "漢文"),
    ("15-chenqing", "陳情表", "李密", "六朝文"),
    ("16-lanting", "蘭亭集序", "王羲之", "六朝文"),
    ("17-guiqulai", "歸去來辭", "陶淵明", "六朝文"),
    ("18-taohuayuan", "桃花源記", "陶淵明", "六朝文"),
    ("19-wuliu", "五柳先生傳", "陶淵明", "六朝文"),
    ("20-jianzong", "諫太宗十思疏", "魏徵", "唐文"),
    ("21-shiyue", "師說", "韓愈", "唐文"),
    ("22-jishier", "祭十二郎文", "韓愈", "唐文"),
    ("23-efang", "阿房宮賦", "杜牧", "唐文"),
    ("24-yueyang", "岳陽樓記", "范仲淹", "宋文"),
    ("25-zuiong", "醉翁亭記", "歐陽脩", "宋文"),
    ("26-qiusheng", "秋聲賦", "歐陽脩", "宋文"),
    ("27-chibifu", "前赤壁賦", "蘇軾", "宋文"),
    ("28-liuguo", "六國論", "蘇洵", "宋文"),
    ("29-du-mengchang", "讀孟嘗君傳", "王安石", "宋文"),
    ("30-you-baochanshan", "遊褒禪山記", "王安石", "宋文"),
]

all_essays = phase1_titles + PHASE2_ESSAYS

# Track previous/next for nav
for i, (eid, title, author, era) in enumerate(all_essays):
    dirpath = os.path.join(SITE_DIR, "phase1" if i < 30 else "phase2", eid)
    bg_md = read_md(dirpath, "軍師-背景資料.md")
    analysis_md = read_md(dirpath, "主筆-文章分析.md")
    
    prev_link = next_link = None
    if i > 0:
        peid = all_essays[i-1][0]
        prev_link = {"href": f"{peid}.html", "cls": "prev", "text": f"← {all_essays[i-1][1][:6]}"}
    if i < len(all_essays) - 1:
        neid = all_essays[i+1][0]
        next_link = {"href": f"{neid}.html", "cls": "next", "text": f"{all_essays[i+1][1][:6]} →"}

    prev_link_s = f'<a href="{prev_link["href"]}" class="nav-prev">{prev_link["text"]}</a>' if prev_link else ''
    next_link_s = f'<a href="{next_link["href"]}" class="nav-next">{next_link["text"]}</a>' if next_link else ''

    bg_html = md_to_html(bg_md)
    analysis_html = md_to_html(analysis_md)
    nav_links_html = prev_link_s + next_link_s

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — 古文觀止導覽</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/article.css">
</head>
<body class="article-page">
    <nav class="article-nav">
        <a href="../index.html" class="nav-home">← 回目錄</a>
        <span class="nav-pos">#{i+1} · {title}</span>
        <div class="nav-links">{nav_links_html}</div>
    </nav>

    <article class="article-container">
        <header class="article-header">
            <h1>{title}</h1>
            <p class="article-meta">{author} · {era}</p>
        </header>

        <section class="article-section bg-section">
            <h2>📜 時代背景與寫作意旨</h2>
            <div class="section-content">{bg_html}</div>
        </section>

        <section class="article-section analysis-section">
            <h2>📖 文章分析</h2>
            <div class="section-content">{analysis_html}</div>
        </section>
    </article>

    <nav class="article-footer-nav">
        {prev_link_s}
        <a href="../index.html" class="nav-home">← 回目錄</a>
        {next_link_s}
    </nav>

    <footer>
        <p>github.com/cormort/guwen_guanzhi</p>
    </footer>
</body>
</html>"""

    outpath = os.path.join(OUTPUT_DIR, f"{eid}.html")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)
    
    size = os.path.getsize(outpath)
    print(f"  {'✅' if bg_md and analysis_md else '⚠️'} {eid}: {title} ({size:,} bytes)")

print(f"\n🎉 {len(all_essays)} 篇文章頁面已建立 → {OUTPUT_DIR}/")
print(f"   Phase 1: {len(phase1_titles)} | Phase 2: {len(PHASE2_ESSAYS)}")
