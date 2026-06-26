#!/usr/bin/env bash
# 古文觀止資料驗證腳本 — 純結構性檢查，不需 LLM
# 用法: bash validate.sh [project_root]
set -uo pipefail

ROOT="${1:-$(cd "$(dirname "$0")" && pwd)}"
ERRORS=0
WARNS=0

red()    { printf "\033[31m%s\033[0m\n" "$1"; }
yellow() { printf "\033[33m%s\033[0m\n" "$1"; }
green()  { printf "\033[32m%s\033[0m\n" "$1"; }

err()  { red  "  ✗ $1"; ((ERRORS++)); }
warn() { yellow "  ⚠ $1"; ((WARNS++)); }
ok()   { green "  ✓ $1"; }

# ─── 1. 命名格式檢查 ───
echo "═══ 1. 命名格式檢查（NNN-keyword 格式）═══"
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    if ! [[ "$name" =~ ^[0-9]+-[a-z] ]]; then
      err "$phase/$name — 不符合 NNN-keyword 格式"
    fi
  done
done
ok "命名格式檢查完成"

# ─── 2. 檔案完整性檢查 ───
echo ""
echo "═══ 2. 檔案完整性（每篇須有 軍師-背景資料.md + 主筆-文章分析.md）═══"
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    [[ -f "$dir/軍師-背景資料.md" ]] || err "$phase/$name 缺少 軍師-背景資料.md"
    [[ -f "$dir/主筆-文章分析.md" ]] || err "$phase/$name 缺少 主筆-文章分析.md"
  done
done
ok "檔案完整性檢查完成"

# ─── 3. 章節完整性掃描（軍師-背景資料.md）───
echo ""
echo "═══ 3. 章節完整性掃描（軍師-背景資料.md 必要章節）═══"
REQUIRED_SECTIONS=("座標定位" "時代" "一句話總結")
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    file="$dir/軍師-背景資料.md"
    [[ -f "$file" ]] || continue
    for section in "${REQUIRED_SECTIONS[@]}"; do
      if ! grep -q "$section" "$file"; then
        err "$phase/$name/軍師-背景資料.md 缺少「$section」"
      fi
    done
  done
done
ok "章節完整性掃描完成"

# ─── 4. 跨階段重複檢查 ───
echo ""
echo "═══ 4. 跨階段重複檢查（同一篇名出現在多個 phase）═══"
# 用目錄名去掉數字前綴，收集所有 keyword，找重複
ALL_KEYWORDS=""
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    keyword="${name#*-}"
    ALL_KEYWORDS="$ALL_KEYWORDS
$keyword|$phase/$name"
  done
done
echo "$ALL_KEYWORDS" | grep -v '^$' | sort -t'|' -k1,1 | awk -F'|' '
  prev==$1 { print "  ⚠ 可能重複：" $2 " vs " prev_full " (keyword: " $1 ")" }
  { prev=$1; prev_full=$2 }
'
ok "跨階段重複檢查完成"

# ─── 5. 篇數統計 ───
echo ""
echo "═══ 5. 篇數統計 ═══"
TOTAL=0
for phase in phase1 phase2 phase3 phase4; do
  count=$(find "$ROOT/$phase" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  echo "  $phase: $count 篇"
  TOTAL=$((TOTAL + count))
done
echo "  合計: $TOTAL 篇（古文觀止共 222 篇）"
if [[ "$TOTAL" -ne 222 ]]; then
  warn "總篇數 $TOTAL ≠ 222"
else
  ok "總篇數正確：222"
fi

# ─── 6. 空檔案檢查 ───
echo ""
echo "═══ 6. 空檔案 / 過短檔案檢查 ═══"
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    for f in "$dir"*.md; do
      [[ -f "$f" ]] || continue
      lines=$(wc -l < "$f" | tr -d ' ')
      if [[ "$lines" -lt 10 ]]; then
        err "$phase/$name/$(basename "$f") 只有 ${lines} 行，疑似不完整"
      fi
    done
  done
done
ok "空檔案檢查完成"

# ─── 7. 編號連續性檢查 ───
echo ""
echo "═══ 7. 編號連續性檢查 ═══"
ALL_NUMS=()
for phase in phase1 phase2 phase3 phase4; do
  for dir in "$ROOT/$phase"/*/; do
    name=$(basename "$dir")
    num="${name%%-*}"
    ALL_NUMS+=("$num")
  done
done
# 排序後檢查是否有缺號
IFS=$'\n' SORTED=($(printf '%s\n' "${ALL_NUMS[@]}" | sort -n)); unset IFS
PREV=0
for n in "${SORTED[@]}"; do
  n_int=$((10#$n))
  if [[ $((PREV + 1)) -ne "$n_int" ]] && [[ "$PREV" -ne 0 || "$n_int" -ne 1 ]]; then
    expected=$((PREV + 1))
    while [[ "$expected" -lt "$n_int" ]]; do
      warn "缺少編號 $expected"
      expected=$((expected + 1))
    done
  fi
  PREV=$n_int
done
ok "編號連續性檢查完成"

# ─── 8. 篇目比對（wikisource 標準清單）───
echo ""
echo "═══ 8. 篇目比對（wikisource 標準清單）═══"
if [[ -f "$ROOT/wikisource_toc.txt" ]]; then
  python3 "$ROOT/verify_toc.py" 2>&1 | while IFS= read -r line; do echo "  $line"; done
else
  warn "找不到 wikisource_toc.txt，跳過篇目比對"
fi

# ─── 總結 ───
echo ""
echo "════════════════════════════════"
if [[ "$ERRORS" -eq 0 ]] && [[ "$WARNS" -eq 0 ]]; then
  green "全部通過 ✓"
else
  [[ "$ERRORS" -gt 0 ]] && red "錯誤: $ERRORS"
  [[ "$WARNS"  -gt 0 ]] && yellow "警告: $WARNS"
fi
exit "$ERRORS"
