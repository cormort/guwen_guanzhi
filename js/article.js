/* ============================================================
   古文觀止導覽 — 文章頁增強腳本 (optional)
   功能：自動側欄目錄 + 捲動高亮 · 字級調整 · 標記已讀
   用法：在文章頁 </body> 前加入
         <script src="../js/article.js"></script>
   無此腳本時，文章頁仍以 article.css 正常呈現。
   ============================================================ */
(function () {
  "use strict";

  /* ---------- 1. 標記本篇為已讀 ---------- */
  try {
    var file = location.pathname.split("/").pop().replace(/\.html?$/i, "");
    if (file) {
      var read = new Set(JSON.parse(localStorage.getItem("guwen:read") || "[]"));
      read.add(file);
      localStorage.setItem("guwen:read", JSON.stringify([].concat([...read])));
    }
  } catch (e) {}

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var container = document.querySelector(".article-container");
    if (!container) return;

    /* ---------- 2. 收集標題，建立目錄 ---------- */
    var headers = [].slice.call(container.querySelectorAll("h2"));
    var items = [];
    headers.forEach(function (h, i) {
      if (!h.id) h.id = "sec-" + i;
      h.style.scrollMarginTop = "80px";
      var sub = !!h.closest(".section-content");
      var label = h.textContent.replace(/^[\s\p{Emoji_Presentation}\p{Extended_Pictographic}·\-—]+/u, "").trim();
      if (label.length > 12) label = label.slice(0, 11) + "…";
      items.push({ id: h.id, label: label, sub: sub, el: h });
    });

    /* ---------- 3. 注入側欄佈局 ---------- */
    if (items.length > 1) {
      document.body.classList.add("has-toc");
      var shell = document.createElement("div");
      shell.className = "article-shell";
      container.parentNode.insertBefore(shell, container);

      var aside = document.createElement("aside");
      aside.className = "article-toc";
      var html = '<p class="toc-title">篇 章 導 覽</p>';
      items.forEach(function (it) {
        html += '<a href="#' + it.id + '" data-target="' + it.id + '"'
              + (it.sub ? ' style="padding-left:14px"' : '') + '>'
              + '<span class="bar"></span>'
              + '<span class="lbl" style="' + (it.sub ? 'font-size:13.5px;color:#8a8071' : '') + '">' + it.label + '</span></a>';
      });
      html += '<div class="toc-seal"><div class="stamp"><span>觀止</span></div></div>';
      aside.innerHTML = html;

      shell.appendChild(aside);
      shell.appendChild(container);

      // 平滑捲動（避免 scrollIntoView）
      aside.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function (ev) {
          ev.preventDefault();
          var t = document.getElementById(a.getAttribute("data-target"));
          if (t) window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 72, behavior: "smooth" });
        });
      });

      // 捲動高亮
      var links = [].slice.call(aside.querySelectorAll("a"));
      function spy() {
        var y = window.scrollY + 120, cur = items[0].id;
        items.forEach(function (it) { if (it.el.offsetTop <= y) cur = it.id; });
        links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("data-target") === cur); });
      }
      window.addEventListener("scroll", spy, { passive: true });
      spy();
    }

    /* ---------- 4. 字級調整 ---------- */
    var nav = document.querySelector(".article-nav");
    if (nav) {
      var FS_KEY = "guwen:fs";
      var fs = parseInt(localStorage.getItem(FS_KEY) || "18", 10);
      if (isNaN(fs)) fs = 18;
      var contents = [].slice.call(document.querySelectorAll(".section-content"));
      function applyFs() {
        contents.forEach(function (c) { c.style.fontSize = fs + "px"; });
        try { localStorage.setItem(FS_KEY, String(fs)); } catch (e) {}
      }
      var tools = document.createElement("div");
      tools.className = "reader-tools";
      tools.innerHTML = '<button class="rt-sm" title="縮小字級">小</button><button class="rt-lg" title="放大字級">大</button>';
      var btns = tools.querySelectorAll("button");
      btns[0].onclick = function () { fs = Math.max(15, fs - 1); applyFs(); };
      btns[1].onclick = function () { fs = Math.min(24, fs + 1); applyFs(); };

      var links2 = nav.querySelector(".nav-links");
      if (links2) nav.insertBefore(tools, links2);
      else nav.appendChild(tools);
      applyFs();
    }
  });
})();
