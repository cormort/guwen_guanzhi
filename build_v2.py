#!/usr/bin/env python3
"""Rebuild with correct directory names and titles from markdown."""

import os, re, markdown

SITE_DIR = "/tmp/guwen_final"
OUTPUT_DIR = os.path.join(SITE_DIR, "articles")

# Read actual directory names and extract titles from background markdown
phase2_dirs = sorted(os.listdir(os.path.join(SITE_DIR, "phase2")))

# Parse title from markdown first line
def get_title(dirpath):
    bg = os.path.join(dirpath, "軍師-背景資料.md")
    if os.path.exists(bg):
        with open(bg, "r", encoding="utf-8") as f:
            first = f.readline().strip()
            # Remove # and brackets
            title = first.lstrip("#").strip()
            title = re.sub(r'[〈〉「」《》]', '', title)
            title = re.sub(r'[—\-].*', '', title).strip()
            if title:
                return title
    # Fall back to dir name
    return dirpath.split("-", 1)[1] if "-" in dirpath else dirpath

def get_author_era(dirpath):
    """Parse author and era from background markdown."""
    bg = os.path.join(dirpath, "軍師-背景資料.md")
    if not os.path.exists(bg):
        return "", ""
    with open(bg, "r", encoding="utf-8") as f:
        content = f.read()
    # Look for 座標定位 table
    author = ""
    era = ""
    for line in content.split("\n"):
        line = line.strip()
        if "作者" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                author = parts[2]
        if "出處" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                era = parts[2]
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

# Phase 1 dirs
phase1_dirs = sorted(os.listdir(os.path.join(SITE_DIR, "phase1")))
all_dirs = [("phase1", d) for d in phase1_dirs] + [("phase2", d) for d in phase2_dirs]

# First pass: get all titles
entries = []
for phase, d in all_dirs:
    dirpath = os.path.join(SITE_DIR, phase, d)
    title = get_title(dirpath)
    author, era = get_author_era(dirpath)
    entries.append((phase, d, title, author, era))

for i, (phase, d, title, author, era) in enumerate(entries):
    dirpath = os.path.join(SITE_DIR, phase, d)
    bg_md = read_md(dirpath, "軍師-背景資料.md")
    analysis_md = read_md(dirpath, "主筆-文章分析.md")
    
    num = i + 1
    
    prev_link_s = ""
    if i > 0:
        prev_d = entries[i-1][1]
        prev_title = entries[i-1][2][:8]
        prev_link_s = f'<a href="{prev_d}.html" class="nav-prev">← {prev_title}</a>'
    
    next_link_s = ""
    if i < len(entries) - 1:
        next_d = entries[i+1][1]
        next_title = entries[i+1][2][:8]
        next_link_s = f'<a href="{next_d}.html" class="nav-next">{next_title} →</a>'
    
    bg_html = md_to_html(bg_md) if bg_md else "<p><em>背景資料待補</em></p>"
    analysis_html = md_to_html(analysis_md) if analysis_md else "<p><em>文章分析待補</em></p>"
    nav_links = prev_link_s + next_link_s
    
    has_bg = "✅" if bg_md else "❌"
    has_analysis = "✅" if analysis_md else "❌"

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
        <span class="nav-pos">#{num} · {title}</span>
        <div class="nav-links">{nav_links}</div>
    </nav>

    <article class="article-container">
        <header class="article-header">
            <h1>{title}</h1>
            <p class="article-meta">{author}{' · ' if author and era else ''}{era}</p>
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

    outpath = os.path.join(OUTPUT_DIR, f"{d}.html")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)
    
    size = os.path.getsize(outpath)
    print(f"  #{num:2d} {has_bg} {has_analysis} {d}: {title} ({size:,} bytes)")

print(f"\n🎉 {len(entries)} 篇文章頁面全部建立完成！")
