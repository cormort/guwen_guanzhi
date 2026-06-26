#!/usr/bin/env python3
"""
build_v2.py — 建立全部文章內頁（水墨宣紙風）

掃描 phase1 / phase2 / phase3 各篇目錄，讀取
「軍師-背景資料.md」與「主筆-文章分析.md」，轉成 HTML，
套用新版版型輸出到 articles/。

相依：pip install markdown
用法：python build_v2.py    （之後再跑 build_index.py 產生目錄頁）
"""

import os, re, markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT, "articles")
PHASES = ["phase1", "phase2", "phase3", "phase4", "supplementary"]


def get_title(dirpath):
    bg = os.path.join(dirpath, "軍師-背景資料.md")
    if os.path.exists(bg):
        with open(bg, "r", encoding="utf-8") as f:
            first = f.readline().strip()
        title = first.lstrip("#").strip()
        title = re.sub(r"[〈〉「」《》]", "", title)
        title = re.sub(r"[—\-].*", "", title).strip()
        if title:
            return title
    base = os.path.basename(dirpath)
    return base.split("-", 1)[1] if "-" in base else base


def get_author_era(dirpath):
    bg = os.path.join(dirpath, "軍師-背景資料.md")
    if not os.path.exists(bg):
        return "", ""
    with open(bg, "r", encoding="utf-8") as f:
        content = f.read()
    author, era = "", ""
    for line in content.split("\n"):
        line = line.strip()
        if "作者" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and not author:
                author = re.sub(r"[*《》]", "", parts[2]).split("（")[0].strip()
        if "出處" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and not era:
                era = re.sub(r"[*]", "", parts[2]).strip()
    return author, era


def read_md(dirpath, filename):
    path = os.path.join(dirpath, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def md_to_html(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])


os.makedirs(OUTPUT_DIR, exist_ok=True)

# 收集所有篇目（依 phase 與目錄名排序）
all_dirs = []
for phase in PHASES:
    pdir = os.path.join(ROOT, phase)
    if os.path.isdir(pdir):
        for d in sorted(os.listdir(pdir)):
            if os.path.isdir(os.path.join(pdir, d)):
                all_dirs.append((phase, d))

entries = []
for phase, d in all_dirs:
    dirpath = os.path.join(ROOT, phase, d)
    title = get_title(dirpath)
    author, era = get_author_era(dirpath)
    entries.append((phase, d, title, author, era))

for i, (phase, d, title, author, era) in enumerate(entries):
    dirpath = os.path.join(ROOT, phase, d)
    bg_md = read_md(dirpath, "軍師-背景資料.md")
    analysis_md = read_md(dirpath, "主筆-文章分析.md")

    num = i + 1

    prev_link_s = ""
    if i > 0:
        prev_d = entries[i - 1][1]
        prev_title = entries[i - 1][2][:8]
        prev_link_s = f'<a href="{prev_d}.html" class="nav-prev">← {prev_title}</a>'

    next_link_s = ""
    if i < len(entries) - 1:
        next_d = entries[i + 1][1]
        next_title = entries[i + 1][2][:8]
        next_link_s = f'<a href="{next_d}.html" class="nav-next">{next_title} →</a>'

    nav_links = prev_link_s + next_link_s

    bg_html = md_to_html(bg_md) if bg_md else "<p><em>背景資料待補</em></p>"
    analysis_html = md_to_html(analysis_md) if analysis_md else "<p><em>文章分析待補</em></p>"

    has_bg = "✅" if bg_md else "❌"
    has_analysis = "✅" if analysis_md else "❌"

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — 古文觀止導覽</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;500;600;700;900&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/article.css">
</head>
<body class="article-page">
    <nav class="article-nav">
        <a href="../index.html" class="nav-home">⟵ 回目錄</a>
        <span class="nav-pos">#{num} · {title}</span>
        <div class="nav-links">{nav_links}</div>
    </nav>

    <article class="article-container">
        <header class="article-header">
            <h1>{title}</h1>
            <p class="article-meta">{author}{' · ' if author and era else ''}{era}</p>
        </header>

        <section class="article-section bg-section">
            <h2>時代背景與寫作意旨</h2>
            <div class="section-content">{bg_html}</div>
        </section>

        <section class="article-section analysis-section">
            <h2>文章分析</h2>
            <div class="section-content">{analysis_html}</div>
        </section>
    </article>

    <nav class="article-footer-nav">
        {prev_link_s}
        <a href="../index.html" class="nav-home">回目錄</a>
        {next_link_s}
    </nav>

    <footer>
        <p>古文觀止導覽 · 結構 · 技巧 · 白話</p>
    </footer>

    <script src="../js/article.js"></script>
</body>
</html>"""

    outpath = os.path.join(OUTPUT_DIR, f"{d}.html")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(outpath)
    print(f"  #{num:3d} {has_bg} {has_analysis} {d}: {title} ({size:,} bytes)")

print(f"\n🎉 {len(entries)} 篇文章頁面全部建立完成！")
