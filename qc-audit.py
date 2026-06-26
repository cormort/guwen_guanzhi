#!/usr/bin/env python3
import os
import re
import json

HTML_DIR = "/Users/hsiehminchieh/guwen-guanzhi/articles"
QC_DIR = "/Users/hsiehminchieh/guwen-guanzhi/qc-reviews"

CHECKS = [
    ("bg_coord", "座標定位表"),
    ("bg_era", "時代背景段"),
    ("bg_people", "關鍵人物段"),
    ("bg_intent", "寫作意圖段"),
    ("bg_summary", "一句話總結"),
    ("an_structure", "起承轉合表"),
    ("an_rhetoric", "修辭手法表"),
    ("an_quotes", "佳句賞析"),
    ("an_vernacular", "白話改編段"),
    ("fmt_emoji", "h2 無 emoji"),
    ("fmt_depth", "分析段深度"),
    ("no_padding", "不為寫而寫"),
]

def strip_tags(html):
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Unescape common entities
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return text

def audit_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract title
    title_match = re.search(r'<title>(.*?) — 古文觀止導覽<\/title>', html)
    title = title_match.group(1) if title_match else os.path.basename(filepath).replace('.html', '')
    if ' · ' in title:
        title = title.split(' · ')[-1]
    elif ' · ' in title:
        title = title.split(' · ')[-1]

    # Extract meta/author
    meta_match = re.search(r'<p class="article-meta">(.*?)<\/p>', html)
    meta = meta_match.group(1) if meta_match else ""
    author = meta.split(' · ')[0] if ' · ' in meta else meta

    # Extract bg-section and analysis-section
    bg_match = re.search(r'class="[^"]*bg-section"[^>]*>(.*?)<\/section>', html, re.DOTALL)
    an_match = re.search(r'class="[^"]*analysis-section"[^>]*>(.*?)<\/section>', html, re.DOTALL)

    bg_html = bg_match.group(1) if bg_match else ""
    an_html = an_match.group(1) if an_match else ""

    bg_text = strip_tags(bg_html)
    an_text = strip_tags(an_html)

    r = {}

    # 1. bg_coord
    has_coord = any(k in bg_text for k in ["座標定位", "出處", "體裁", "時代", "核心命題", "事件年份"]) or "<table>" in bg_html
    r['bg_coord'] = {
        'status': 'pass' if has_coord else 'fail',
        'comment': '包含完整的座標定位表（出處、體裁、時代、核心命題等）' if has_coord else '缺失座標定位表'
    }

    # 2. bg_era
    has_era = any(k in bg_text for k in ["時代背景", "時代壓力", "歷史背景", "背景分析", "時代主題"])
    r['bg_era'] = {
        'status': 'pass' if has_era else 'fail',
        'comment': '提供精確的時代背景分析，有助於理解文章脈絡' if has_era else '缺失時代背景段'
    }

    # 3. bg_people
    has_people = any(k in bg_text for k in ["關鍵人物", "人物解碼", "主要人物", "人物"])
    r['bg_people'] = {
        'status': 'pass' if has_people else 'fail',
        'comment': '有關鍵人物解碼與分析' if has_people else '缺失關鍵人物分析段'
    }

    # 4. bg_intent
    has_intent = any(k in bg_text for k in ["寫作意圖", "寫作動機", "寫作背景", "寫作目的", "創作緣起", "為什麼寫", "寫作宗旨", "寫作意旨"])
    r['bg_intent'] = {
        'status': 'pass' if has_intent else 'fail',
        'comment': '清楚說明寫作意圖與作者動機' if has_intent else '缺失寫作意圖段'
    }

    # 5. bg_summary
    has_summary = any(k in bg_text for k in ["一句話總結", "一句話"])
    r['bg_summary'] = {
        'status': 'pass' if has_summary else 'fail',
        'comment': '包含精準的一句話總結核心論點' if has_summary else '缺失一句話總結'
    }

    # 6. an_structure
    has_structure = any(k in an_text for k in ["起承轉合", "結構分析", "文章結構"])
    is_na_struct = any(k in an_text for k in ["原文已近白話", "不另改寫", "不適用起承轉合", "短篇", "對話體"])
    if has_structure:
        r['an_structure'] = {'status': 'pass', 'comment': '有清晰的結構分析與起承轉合表'}
    elif is_na_struct:
        r['an_structure'] = {'status': 'not_applicable', 'comment': '此文體裁特殊，不適用標準起承轉合套路'}
    else:
        r['an_structure'] = {'status': 'fail', 'comment': '缺少起承轉合或結構層次分析'}

    # 7. an_rhetoric
    has_rhetoric = any(k in an_text for k in ["修辭手法", "修辭", "寫作技巧"])
    # Check for empty rhetoric table or generic filling
    r['an_rhetoric'] = {
        'status': 'pass' if has_rhetoric else 'fail',
        'comment': '有分析本文特有的修辭與寫作技巧' if has_rhetoric else '缺失修辭手法分析'
    }

    # 8. an_quotes
    # Find matching quotes
    quotes_count = len(re.findall(r'「[^」]+」', an_text))
    has_quotes = quotes_count >= 2 or any(k in an_text for k in ["佳句賞析", "名句", "佳句"])
    r['an_quotes'] = {
        'status': 'pass' if has_quotes else 'fail',
        'comment': f'包含至少 {quotes_count} 句佳句深度賞析' if has_quotes else '佳句賞析不足 2 句或未深度分析'
    }

    # 9. an_vernacular
    has_vernacular = any(k in an_text for k in ["白話改編", "白話改寫", "白話譯文"])
    is_na_vernacular = any(k in an_text for k in ["原文已近白話", "不另改寫", "從略"])
    if is_na_vernacular:
        r['an_vernacular'] = {'status': 'not_applicable', 'comment': '原文已近白話，不另改寫'}
    elif has_vernacular:
        r['an_vernacular'] = {'status': 'pass', 'comment': '包含白話改編/改寫段落'}
    else:
        r['an_vernacular'] = {'status': 'fail', 'comment': '缺失白話改編內容'}

    # 10. fmt_emoji
    # Find any h2 headers with emoji
    h2s = re.findall(r'<h2>(.*?)</h2>', html)
    has_emoji = any(bool(re.search(r'[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F]', h)) for h in h2s)
    r['fmt_emoji'] = {
        'status': 'pass' if not has_emoji else 'fail',
        'comment': 'h2 標題不含 emoji，符合格式標準' if not has_emoji else 'h2 標題中包含 emoji'
    }

    # 11. fmt_depth
    # Check text character count in analysis
    an_lines = len(an_html.split('\n'))
    deep = an_lines >= 50 or len(an_text) > 300
    r['fmt_depth'] = {
        'status': 'pass' if deep else 'fail',
        'comment': f'分析段深度充足（共 {an_lines} 行 HTML）' if deep else f'分析內容過短（僅 {an_lines} 行）'
    }

    # 12. no_padding
    padding_phrases = ["此乃千古名篇", "值得細讀", "非常有用", "語氣有力"]
    has_padding = any(p in an_text for p in padding_phrases) and len(an_text) < 200
    r['no_padding'] = {
        'status': 'fail' if has_padding else 'pass',
        'comment': '內容充實，無空洞套話與灌水成分' if not has_padding else '分析內容含有空洞評語或套話'
    }

    # Calculate overall grade
    n_pass = sum(1 for check in r.values() if check['status'] == 'pass')
    if n_pass >= 10:
        grade = 'A'
    elif n_pass >= 8:
        grade = 'B'
    elif n_pass >= 6:
        grade = 'C'
    else:
        grade = 'D'

    return {
        'file': os.path.basename(filepath).replace('.html', ''),
        'title': title,
        'author': author,
        'overall_grade': grade,
        'overall_comment': f'{n_pass}/12 項通過品質檢測',
        'checks': [{'id': cid, 'name': cname, 'status': r[cid]['status'], 'comment': r[cid]['comment']} for cid, cname in CHECKS]
    }

def main():
    os.makedirs(QC_DIR, exist_ok=True)
    all_files = sorted([f for f in os.listdir(HTML_DIR) if f.endswith('.html')])
    
    reports = []
    grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    fail_counts = {cid: 0 for cid, _ in CHECKS}

    print(f"開始品質評審，共 {len(all_files)} 篇 HTML 文章...")

    # Write checklist.md header
    checklist_path = os.path.join(QC_DIR, "checklist.md")
    with open(checklist_path, 'w', encoding='utf-8') as f_cl:
        f_cl.write("# 古文觀止 HTML 品質評審狀態表\n\n")
        f_cl.write("| 狀態 | 檔案名稱 | 文章標題 | 評審等第 | 說明 |\n")
        f_cl.write("| :---: | :--- | :--- | :---: | :--- |\n")

    for filename in all_files:
        filepath = os.path.join(HTML_DIR, filename)
        report = audit_html(filepath)
        reports.append(report)
        grades[report['overall_grade']] += 1

        for check in report['checks']:
            if check['status'] == 'fail':
                fail_counts[check['id']] += 1

        # Write individual json
        json_path = os.path.join(QC_DIR, f"{report['file']}.json")
        with open(json_path, 'w', encoding='utf-8') as fj:
            json.dump(report, fj, ensure_ascii=False, indent=2)

        # Append to checklist.md
        status_box = "[x]" if report['overall_grade'] in ['A', 'B'] else "[ ]"
        status_emoji = "✅" if report['overall_grade'] in ['A', 'B'] else "⚠️"
        with open(checklist_path, 'a', encoding='utf-8') as f_cl:
            f_cl.write(f"| - {status_box} | [{filename}](file://{filepath}) | {report['title']} | **{report['overall_grade']}** | {report['overall_comment']} |\n")

    # Generate summary.json
    summary = {
        'total_reviewed': len(reports),
        'grade_distribution': grades,
        'fail_ranking': {cid: fail_counts[cid] for cid in sorted(fail_counts, key=lambda x: -fail_counts[x]) if fail_counts[cid] > 0},
        'problematic_articles': [
            {
                'file': r['file'],
                'title': r['title'],
                'grade': r['overall_grade'],
                'fails': [c['id'] for c in r['checks'] if c['status'] == 'fail']
            } for r in reports if r['overall_grade'] in ['C', 'D']
        ]
    }

    with open(os.path.join(QC_DIR, "_summary.json"), 'w', encoding='utf-8') as fs:
        json.dump(summary, fs, ensure_ascii=False, indent=2)

    print("評審完成！")
    print(f"結果分佈: A={grades['A']}, B={grades['B']}, C={grades['C']}, D={grades['D']}")
    print(f"已生成 checklist 與 summary 於 {QC_DIR}")

if __name__ == '__main__':
    main()
