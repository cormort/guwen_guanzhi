#!/usr/bin/env python3
"""比對本地篇目 vs wikisource 古文觀止標準清單"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# 讀 wikisource 標準清單
ws_titles = []
with open(os.path.join(ROOT, "wikisource_toc.txt"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "|" in line:
            ws_titles.append(line.split("|", 1)[1])

# 從本地目錄讀取篇名（從軍師-背景資料.md 第一行提取）
def extract_title(filepath):
    """從 md 第一行提取核心篇名"""
    with open(filepath, encoding="utf-8") as f:
        h1 = f.readline().strip()
    h1 = re.sub(r'^#+\s*', '', h1)
    # 去掉 emoji (所有 Unicode emoji 區段)
    h1 = re.sub(r'[\U0001F300-\U0001FAFF☀-➿]', '', h1)
    # 去掉書名號
    h1 = re.sub(r'[〈〉《》「」]', '', h1)
    # 去掉所有裝飾後綴：背景資料、軍師、分析等
    h1 = re.sub(r'(背景資料|背景分析|軍師背景資料|軍師背景分析|軍師分析|軍師戰情分析|'
                r'軍師戰情室|軍師視角|軍師策論|軍師點評|軍師檔案|背景|分析|軍師)', '', h1)
    # 去掉分隔符號
    h1 = re.sub(r'[—·\-：:]+', '', h1)
    h1 = re.sub(r'\s+', '', h1)
    return h1.strip()

local_titles = {}
for phase in ["phase1", "phase2", "phase3", "phase4"]:
    phase_dir = os.path.join(ROOT, phase)
    if not os.path.isdir(phase_dir):
        continue
    for d in sorted(os.listdir(phase_dir)):
        fp = os.path.join(phase_dir, d, "軍師-背景資料.md")
        if os.path.isfile(fp):
            title = extract_title(fp)
            local_titles[f"{phase}/{d}"] = title

# 正規化函數：去空白、統一異體字
def normalize(s):
    s = re.sub(r'\s+', '', s)
    # 常見異體字對照
    table = str.maketrans({
        '於': '于', '爲': '為', '讎': '仇', '陋': '陃',
        '鼂': '晁', '觶': '觚', '讋': '龍', '煖': '諼',
        '斶': '触', '寘': '置', '圉': '圄',
        '姦': '奸', '愿': '願',
    })
    s = s.translate(table)
    return s

# 建立 wikisource 正規化 -> 原名 映射
ws_norm = {}
for t in ws_titles:
    ws_norm[normalize(t)] = t

# 建立本地正規化 -> (path, 原名) 映射
local_norm = {}
for path, t in local_titles.items():
    local_norm[normalize(t)] = (path, t)

# 模糊匹配：檢查一個字串是否包含另一個
def fuzzy_match(needle, haystack_dict):
    """找 haystack 中包含 needle 或被 needle 包含的"""
    matches = []
    for k, v in haystack_dict.items():
        if len(needle) >= 2 and len(k) >= 2:
            if needle in k or k in needle:
                matches.append((k, v))
    return matches

# ── 比對 ──
print("═══ 篇目比對：wikisource vs 本地 ═══\n")

# wikisource 有但本地沒有
missing = []
for wn, wt in ws_norm.items():
    if wn not in local_norm:
        fuzz = fuzzy_match(wn, {k: v[1] for k, v in local_norm.items()})
        if fuzz:
            print(f"  ⚠ wikisource「{wt}」未精確匹配，可能對應：{', '.join(f[1] for f in fuzz)}")
        else:
            missing.append(wt)

if missing:
    print(f"\n  ✗ wikisource 有但本地缺少（{len(missing)} 篇）：")
    for m in missing:
        print(f"    - {m}")

# 本地有但 wikisource 沒有
extra = []
for ln, (path, lt) in local_norm.items():
    if ln not in ws_norm:
        fuzz = fuzzy_match(ln, ws_norm)
        if not fuzz:
            extra.append((path, lt))

if extra:
    print(f"\n  ⚠ 本地有但 wikisource 沒有（{len(extra)} 篇，可能是額外收錄或篇名不同）：")
    for path, t in extra:
        print(f"    - {path}: {t}")

if not missing and not extra:
    print("  ✓ 完全匹配")

print(f"\n  統計：wikisource {len(ws_titles)} 篇 / 本地 {len(local_titles)} 篇")
