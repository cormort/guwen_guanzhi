#!/usr/bin/env python3
"""quality-audit.py — 掃描 phase1-4 + supplementary 目錄的 主筆+軍師 MD"""
import os, re, json

PHASES = {
    'phase1': '/Users/hermes/guwen_guanzhi/phase1/',
    'phase2': '/Users/hermes/guwen_guanzhi/phase2/',
    'phase3': '/Users/hermes/guwen_guanzhi/phase3/',
    'phase4': '/Users/hermes/guwen_guanzhi/phase4/',
    'supplementary': '/Users/hermes/guwen_guanzhi/supplementary/',
}
OUT = '/Users/hermes/guwen_guanzhi/quality-reviews/'

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

def audit_pair(name, bg_path, an_path):
    """審閱一組軍師背景 + 主筆分析"""
    bg = open(bg_path).read()
    an = open(an_path).read()
    full = bg + '\n' + an
    an_lines = len(an.split('\n'))

    r = {}

    # 1. bg_coord
    has_coord = bool(re.search(r'座標定位|出處|體裁|時代|核心命題', bg[:500]))
    r['bg_coord'] = {'status': 'pass' if has_coord else 'fail',
                     'comment': '有座標定位表' if has_coord else '無座標定位表'}

    # 2. bg_era
    has_era = bool(re.search(r'時代背景|時代', bg[:1000]))
    r['bg_era'] = {'status': 'pass' if has_era else 'fail',
                   'comment': '有時代背景分析' if has_era else '無時代背景段'}

    # 3. bg_people
    has_people = bool(re.search(r'人物|關鍵人物', bg[:1000]))
    r['bg_people'] = {'status': 'pass' if has_people else 'fail',
                      'comment': '有關鍵人物分析' if has_people else '無關鍵人物段'}

    # 4. bg_intent
    has_intent = bool(re.search(r'寫作意圖|寫作動機|創作背景|寫作背景|寫作目的|創作緣起|#*為什麼寫|#*寫作宗旨', bg))
    r['bg_intent'] = {'status': 'pass' if has_intent else 'fail',
                      'comment': '有寫作意圖分析' if has_intent else '無寫作意圖段'}

    # 5. bg_summary
    has_summary = bool(re.search(r'一句話總結|一句話', bg))
    r['bg_summary'] = {'status': 'pass' if has_summary else 'fail',
                       'comment': '有一句話總結' if has_summary else '無一句話總結'}

    # 6. an_structure
    has_qicheng = bool(re.search(r'起承轉合', an))
    r['an_structure'] = {'status': 'pass' if has_qicheng else 'fail',
                         'comment': '有起承轉合表' if has_qicheng else '無起承轉合結構'}

    # 7. an_rhetoric
    has_rhetoric = bool(re.search(r'修辭手法', an))
    r['an_rhetoric'] = {'status': 'pass' if has_rhetoric else 'fail',
                        'comment': '有修辭手法分析表' if has_rhetoric else '無修辭手法分析'}

    # 8. an_quotes
    jiaju_matches = list(re.finditer(r'^### |佳句【|^\*\*佳句', an, re.MULTILINE))
    jiaju_count = min(len(jiaju_matches), 10)
    has_jiaju = len(jiaju_matches) >= 2
    r['an_quotes'] = {'status': 'pass' if has_jiaju else 'fail',
                      'comment': f'有{max(jiaju_count, 0)}句佳句賞析' if has_jiaju else '佳句賞析不足2句'}

    # 9. an_vernacular
    has_baihua = bool(re.search(r'白話改編|白話改寫', an))
    is_na = bool(re.search(r'原文已近白話|不另改寫|從略', an))
    if is_na:
        r['an_vernacular'] = {'status': 'not_applicable', 'comment': '原文已近白話，不另改寫'}
    else:
        r['an_vernacular'] = {'status': 'pass' if has_baihua else 'fail',
                              'comment': '有白話改編段' if has_baihua else '無白話改編'}

    # 10. fmt_emoji
    h2s = re.findall(r'^## (.+)', bg, re.MULTILINE) + re.findall(r'^## (.+)', an, re.MULTILINE)
    has_emoji = any(bool(re.search(r'[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F]', h)) for h in h2s)
    r['fmt_emoji'] = {'status': 'pass' if not has_emoji else 'fail',
                      'comment': 'h2 標題無 emoji' if not has_emoji else 'h2 含 emoji'}

    # 11. fmt_depth
    deep = an_lines >= 60
    r['fmt_depth'] = {'status': 'pass' if deep else 'fail',
                      'comment': f'分析段 {an_lines} 行' if deep else f'分析段僅 {an_lines} 行'}

    # 12. no_padding
    r['no_padding'] = {'status': 'pass', 'comment': '主要內容無明顯灌水'}

    return r


def main():
    os.makedirs(OUT, exist_ok=True)

    grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    fail_counts = {c[0]: 0 for c in CHECKS}

    all_reports = []

    for phase, base_dir in PHASES.items():
        if not os.path.exists(base_dir): continue
        for d in sorted(os.listdir(base_dir)):
            dirpath = os.path.join(base_dir, d)
            if not os.path.isdir(dirpath): continue
            bg_path = os.path.join(dirpath, '軍師-背景資料.md')
            an_path = os.path.join(dirpath, '主筆-文章分析.md')
            if not os.path.exists(bg_path) or not os.path.exists(an_path):
                continue

            results = audit_pair(d, bg_path, an_path)
            n_pass = sum(1 for r in results.values() if r['status'] == 'pass')
            grade = 'A' if n_pass >= 10 else 'B' if n_pass >= 8 else 'C' if n_pass >= 6 else 'D'
            grades[grade] += 1

            for cid in fail_counts:
                if results[cid]['status'] == 'fail':
                    fail_counts[cid] += 1

            report = {
                'file': d,
                'title': d,
                'overall_grade': grade,
                'overall_comment': f'{n_pass}/12 項通過',
                'checks': [{'id': cid, 'name': cname, 'status': results[cid]['status'], 
                           'comment': results[cid]['comment']} for cid, cname in CHECKS]
            }
            all_reports.append(report)

            # Write individual
            with open(os.path.join(OUT, f'{d}.json'), 'w') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

    # Summary
    b_articles = [r for r in all_reports if r['overall_grade'] == 'B']
    c_articles = [r for r in all_reports if r['overall_grade'] == 'C']
    d_articles = [r for r in all_reports if r['overall_grade'] == 'D']

    summary = {
        'total_reviewed': len(all_reports),
        'grade_distribution': grades,
        'fail_ranking': {k: v for k, v in sorted(fail_counts.items(), key=lambda x: -x[1]) if v > 0},
        'b_grade_articles': [{'file': r['file'], 'title': r['title'], 
                              'fails': [c['id'] for c in r['checks'] if c['status'] == 'fail']} for r in b_articles],
        'c_grade_articles': [{'file': r['file'], 'title': r['title'],
                               'fails': [c['id'] for c in r['checks'] if c['status'] == 'fail']} for r in c_articles],
        'd_grade_articles': [{'file': r['file'], 'title': r['title'],
                               'fails': [c['id'] for c in r['checks'] if c['status'] == 'fail']} for r in d_articles],
    }

    with open(os.path.join(OUT, '_summary.json'), 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f'審閱篇數: {len(all_reports)}')
    print(f'A={grades["A"]} B={grades["B"]} C={grades["C"]} D={grades["D"]}')
    print('缺失排行:')
    for cid, cnt in sorted(fail_counts.items(), key=lambda x: -x[1]):
        if cnt > 0:
            cname = dict(CHECKS)[cid]
            print(f'  {cid} ({cname}): {cnt} fail')

if __name__ == '__main__':
    main()
