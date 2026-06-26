#!/usr/bin/env python3
"""
build_index.py — 產生新版目錄頁 index.html（水墨宣紙風，涵蓋全部 222 篇）

掃描 phase1 / phase2 / phase3 各篇目錄，從「軍師-背景資料.md」擷取
篇名、作者、出處，依吳氏選本順序排列，輸出 index.html。

特性：純標準函式庫、無外部相依；路徑相對於本腳本所在資料夾。
用法：  python build_index.py
（請先用 build_v2.py 產生 articles/*.html，目錄頁才有對應連結。）
"""

import os, re, json
from author_data import AUTHOR_MAP, AUTHOR_INFO

ROOT = os.path.dirname(os.path.abspath(__file__))
PHASES = ["phase1", "phase2", "phase3", "phase4", "supplementary"]


def dir_keyword(dirname):
    return dirname.split("-", 1)[1] if re.match(r'^\d+-', dirname) else dirname


def clean_h1(h1):
    h1 = re.sub(r'^#+\s*', '', h1)
    h1 = re.sub(r'[\U0001F300-\U0001FAFF☀-➿🏯]', '', h1)
    h1 = re.sub(r'[〈〉《》「」]', '', h1)
    h1 = re.sub(r'^[^：:—\-]*(?:軍師|檔案|簡報)[^：:—\-]*[：:—\-]+\s*', '', h1)
    h1 = re.sub(r'(背景資料|背景分析|軍師背景資料|軍師背景分析|軍師分析|軍師戰情分析|'
                r'軍師戰情室|軍師視角|軍師策論|軍師點評|軍師檔案|軍師簡報|背景|分析|軍師)', '', h1)
    h1 = re.sub(r'[（(][^）)]*[）)]', '', h1)
    h1 = re.sub(r'[—·\-：:]+\s*$', '', h1)
    h1 = re.sub(r'——.*$', '', h1)
    h1 = re.sub(r'\s+', '', h1)
    return h1.strip()


def get_title(dirpath):
    bg = os.path.join(dirpath, "軍師-背景資料.md")
    if os.path.exists(bg):
        with open(bg, "r", encoding="utf-8") as f:
            first = f.readline().strip()
        title = clean_h1(first)
        if title:
            return title
    base = os.path.basename(dirpath)
    return base.split("-", 1)[1] if "-" in base else base


def get_author_era(dirpath):
    keyword = dir_keyword(os.path.basename(dirpath))
    entry = AUTHOR_MAP.get(keyword)
    if entry:
        return entry["author"], entry["era"]
    return "", ""


def collect():
    entries = []
    n = 0
    for phase in PHASES:
        pdir = os.path.join(ROOT, phase)
        if not os.path.isdir(pdir):
            continue
        for d in sorted(os.listdir(pdir)):
            dirpath = os.path.join(pdir, d)
            if not os.path.isdir(dirpath):
                continue
            n += 1
            title = get_title(dirpath)
            author, era = get_author_era(dirpath)
            keyword = dir_keyword(d)
            dynasty = AUTHOR_MAP.get(keyword, {}).get("dynasty", "其他")
            entries.append({"n": n, "id": d, "title": title,
                            "author": author, "era": era,
                            "dynasty": dynasty, "phase": phase})
    return entries


def raw_lines(entries):
    out = []
    for e in entries:
        out.append("    {n:%d,id:%s,title:%s,author:%s,era:%s,dynasty:%s,phase:%s}," % (
            e["n"], json.dumps(e["id"], ensure_ascii=False),
            json.dumps(e["title"], ensure_ascii=False),
            json.dumps(e["author"], ensure_ascii=False),
            json.dumps(e["era"], ensure_ascii=False),
            json.dumps(e["dynasty"], ensure_ascii=False),
            json.dumps(e["phase"], ensure_ascii=False)))
    return "\n".join(out)


def author_info_js():
    out = []
    for name, info in sorted(AUTHOR_INFO.items()):
        out.append("    %s:{full:%s,courtesy:%s,dynasty:%s,intro:%s}," % (
            json.dumps(name, ensure_ascii=False),
            json.dumps(info["full_name"], ensure_ascii=False),
            json.dumps(info["courtesy"], ensure_ascii=False),
            json.dumps(info["dynasty"], ensure_ascii=False),
            json.dumps(info["intro"], ensure_ascii=False)))
    return "\n".join(out)


def main():
    entries = collect()
    html = TEMPLATE.replace("__RAW_ENTRIES__", raw_lines(entries))
    html = html.replace("__AUTHOR_INFO__", author_info_js())
    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ 已產生 index.html，共 %d 篇" % len(entries))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>古文觀止導覽</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@300;400;500;600;700;900&family=Ma+Shan+Zheng&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div class="container">

    <header class="masthead">
      <div class="corner-seal"><span>觀止</span></div>
      <div class="cover">
        <p class="editor">清 · 吳楚材 吳調侯 選輯</p>
        <h1>古文觀止</h1>
        <p class="tagline">結構分析 · 寫作技巧 · 白話改編</p>
      </div>
    </header>

    <section class="intro">
      <div class="blurb">
        <p>《古文觀止》成書於清康熙年間，由吳楚材、吳調侯叔姪二人編選，上起<span class="hi">東周</span>、下訖<span class="hi">明末</span>，凡 <strong>222</strong> 篇。所選皆歷代散文菁華，三百年來流傳最廣，為讀古文者之圭臬。</p>
        <p>本導覽逐篇拆解<strong>篇章結構</strong>、<strong>寫作技巧</strong>與<strong>佳句賞析</strong>，並附<strong>白話對照</strong>，循序通讀全帙。</p>
      </div>
      <div class="progress-card">
        <div class="pc-top">
          <span class="pc-label">研讀進度</span>
          <span class="pc-total">全書 222 篇</span>
        </div>
        <div class="pc-count">
          <span class="pc-num" id="readCount">0</span>
          <span class="pc-of">／ <span id="totalCount">0</span> 篇 已讀</span>
        </div>
        <div class="pc-bar"><div class="pc-fill" id="progressFill"></div></div>
        <p class="pc-hint">本導覽現收錄 <span id="corpusCount">0</span> 篇 · 點按篇目右側 <span class="seal">朱印</span> 標記已讀</p>
      </div>
    </section>

    <div class="controls">
      <div class="tabs" id="tabs"></div>
      <div class="search">
        <span class="icon">⌕</span>
        <input id="search" type="text" placeholder="搜尋篇名、作者、出處…" autocomplete="off">
      </div>
    </div>
    <div class="divider"></div>
    <p class="result-meta" id="resultMeta"></p>

    <div id="list"></div>

    <footer class="site-footer">
      <span class="sf-left">古文觀止導覽 · 結構 · 技巧 · 白話</span>
      <span class="sf-right">觀古今於須臾</span>
    </footer>
  </div>

  <script>
  const RAW = [
__RAW_ENTRIES__
  ];
  const AUTHORS = {
__AUTHOR_INFO__
  };

  function genreOf(t){
    const last=t[t.length-1];
    if(last==="記") return "記";
    if(last==="序") return "序";
    if(last==="表") return "表";
    if(last==="賦") return "賦";
    if(last==="書") return "書";
    if(last==="說"||last==="説") return "說";
    if(last==="傳") return "傳";
    if(last==="論") return "論";
    if(last==="辭") return "辭";
    if(/檄|討武/.test(t)) return "檄";
    if(/原道|廉恥|進學解|十思疏/.test(t)) return "論";
    if(/卜居/.test(t)) return "辭";
    return "史傳";
  }
  const ESSAYS = RAW.map(e=>({...e, genre:genreOf(e.title), isSupp:e.phase==="supplementary"}));

  const READ_KEY = "guwen:read";
  let read = (()=>{ try { return new Set(JSON.parse(localStorage.getItem(READ_KEY)||"[]")); } catch(e){ return new Set(); } })();
  let dim = "卷次";
  let query = "";

  const DIM_SUBS = { 周文:"左傳・國語・戰國策・楚辭", 秦文:"李斯", 漢文:"史記・兩漢", 六朝文:"晉宋齊", 唐文:"韓柳諸家", 宋文:"歐蘇王曾", 明文:"宋濂・歸有光", 清文:"顧炎武" };
  const JUAN = { 周文:"卷一 ─ 四", 秦文:"卷四", 漢文:"卷五 ─ 六", 六朝文:"卷七", 唐文:"卷七 ─ 九", 宋文:"卷九 ─ 十一", 明文:"卷十二", 清文:"補遺" };
  const DYN_ORDER = ["周文","秦文","漢文","六朝文","唐文","宋文","明文","清文","其他"];
  const GENRE_ORDER = ["史傳","論","記","序","表","賦","書","說","傳","辭","檄"];
  const DYN_AUTHOR_ORDER = ["周","秦","漢","六朝","唐","宋","明","清"];

  function el(tag, cls, html){ const n=document.createElement(tag); if(cls) n.className=cls; if(html!=null) n.innerHTML=html; return n; }

  function buildGroups(){
    const q = query.trim();
    const filtered = ESSAYS.filter(e => !q || e.title.includes(q) || e.author.includes(q) || e.era.includes(q));
    if(dim==="全部"){
      return [{label:"全部選文", sub:"依吳氏選本卷次", items:filtered.slice().sort((a,b)=>a.n-b.n)}];
    }
    if(dim==="作者") return buildAuthorGroups(filtered);
    const key = dim==="卷次" ? "dynasty" : "genre";
    let order = dim==="卷次" ? DYN_ORDER : GENRE_ORDER;
    const map = {};
    filtered.forEach(e=>{ const k=e[key]||"其他"; (map[k]=map[k]||[]).push(e); });
    const seen = order.filter(k=>map[k]);
    Object.keys(map).forEach(k=>{ if(seen.indexOf(k)<0) seen.push(k); });
    return seen.map(k=>({
      label:k, sub: dim==="卷次" ? (DIM_SUBS[k]||"") : "", juan: dim==="卷次" ? (JUAN[k]||"") : "",
      items: map[k].sort((a,b)=>a.n-b.n)
    }));
  }

  function buildAuthorGroups(filtered){
    const byAuthor = {};
    filtered.forEach(e=>{ const a=e.author||"佚名"; (byAuthor[a]=byAuthor[a]||[]).push(e); });
    const byDynasty = {};
    Object.keys(byAuthor).forEach(a=>{
      const info = AUTHORS[a];
      const dyn = info ? info.dynasty : "其他";
      (byDynasty[dyn] = byDynasty[dyn] || []).push(a);
    });
    const groups = [];
    DYN_AUTHOR_ORDER.concat(["其他"]).forEach(dyn=>{
      const authors = byDynasty[dyn];
      if(!authors) return;
      authors.sort((a,b)=>byAuthor[a][0].n - byAuthor[b][0].n);
      groups.push({ dynasty: dyn, authors: authors.map(a=>({
        name: a, info: AUTHORS[a] || null,
        items: byAuthor[a].sort((x,y)=>x.n-y.n)
      }))});
    });
    return groups;
  }

  function renderTabs(){
    const wrap = document.getElementById("tabs");
    wrap.innerHTML = "";
    ["卷次","作者","文體","全部"].forEach(name=>{
      const label = name==="全部" ? "全部" : "依"+name;
      const b = el("button", "tab"+(name===dim?" active":""), "<span>"+label+"</span>");
      b.onclick = ()=>{ dim=name; renderTabs(); renderList(); };
      wrap.appendChild(b);
    });
  }

  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

  function renderRow(e){
    const isRead = read.has(e.id);
    const row = el("div","row"+(e.isSupp?" supp":""));
    row.innerHTML =
      '<span class="num">'+String(e.n).padStart(2,"0")+'</span>'+
      '<a class="link" href="articles/'+e.id+'.html">'+
        '<span class="title">'+esc(e.title)+'</span>'+
        (e.isSupp?'<span class="supp-badge">補</span>':'')+
        '<span class="author">'+esc(e.author)+'</span>'+
        '<span class="era">'+esc(e.era)+'</span>'+
      '</a>'+
      '<span class="genre">'+esc(e.genre)+'</span>'+
      '<span class="mark" title="標記已讀">'+
        (isRead ? '<span class="seal">讀</span>' : '<span class="dot"></span>')+
      '</span>';
    row.querySelector(".mark").onclick = (ev)=>{ ev.preventDefault(); toggleRead(e.id); };
    return row;
  }

  function renderList(){
    const q = query.trim();
    const count = ESSAYS.filter(e=>!q||e.title.includes(q)||e.author.includes(q)||e.era.includes(q)).length;
    document.getElementById("resultMeta").textContent = "共 "+count+" 篇 · 依"+dim+"排列";

    const list = document.getElementById("list");
    list.innerHTML = "";

    if(dim==="作者"){
      renderAuthorView(list);
      return;
    }

    const groups = buildGroups();
    groups.forEach(g=>{
      const sec = el("section","group");
      const head = el("div","group-head");
      head.innerHTML =
        '<div class="gh-left"><span class="diamond"></span><h2>'+esc(g.label)+'</h2></div>'+
        (g.juan ? '<span class="juan-tag">'+esc(g.juan)+'</span>' : '')+
        '<span class="gh-sub">'+esc(g.sub||"")+'</span>'+
        '<span class="gh-count">'+g.items.length+' 篇</span>';
      sec.appendChild(head);
      const gl = el("div","group-list");
      g.items.forEach(e=> gl.appendChild(renderRow(e)));
      sec.appendChild(gl);
      list.appendChild(sec);
    });
  }

  function renderAuthorView(list){
    const q = query.trim();
    const filtered = ESSAYS.filter(e => !q || e.title.includes(q) || e.author.includes(q) || e.era.includes(q));
    const groups = buildAuthorGroups(filtered);
    groups.forEach(g=>{
      const dynSec = el("section","group");
      const dynHead = el("div","group-head");
      dynHead.innerHTML = '<div class="gh-left"><span class="diamond"></span><h2>'+esc(g.dynasty)+'</h2></div>'+
        '<span class="gh-count">'+g.authors.reduce((s,a)=>s+a.items.length,0)+' 篇</span>';
      dynSec.appendChild(dynHead);

      g.authors.forEach(a=>{
        const card = el("div","author-card");
        const info = a.info;
        let bioHtml = '<h3 class="author-name">'+esc(a.name)+'</h3>';
        if(info){
          bioHtml += '<p class="author-meta">'+esc(info.full||info.full_name||"")+(info.courtesy?' · '+esc(info.courtesy):'')+'</p>';
          bioHtml += '<p class="author-intro">'+esc(info.intro)+'</p>';
        }
        card.innerHTML = bioHtml;

        const gl = el("div","group-list author-articles");
        a.items.forEach(e=> gl.appendChild(renderRow(e)));
        card.appendChild(gl);
        dynSec.appendChild(card);
      });

      list.appendChild(dynSec);
    });
  }

  function renderProgress(){
    const total = ESSAYS.length;
    const rc = ESSAYS.filter(e=>read.has(e.id)).length;
    document.getElementById("readCount").textContent = rc;
    document.getElementById("totalCount").textContent = total;
    document.getElementById("corpusCount").textContent = total;
    document.getElementById("progressFill").style.width = (total? Math.round(rc/total*100):0)+"%";
  }

  function toggleRead(id){
    read.has(id) ? read.delete(id) : read.add(id);
    try { localStorage.setItem(READ_KEY, JSON.stringify([...read])); } catch(e){}
    renderList(); renderProgress();
  }

  document.getElementById("search").addEventListener("input", (e)=>{ query=e.target.value; renderList(); });

  renderTabs();
  renderList();
  renderProgress();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
