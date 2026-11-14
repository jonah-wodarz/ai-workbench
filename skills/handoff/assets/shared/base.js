/* shared base: helpers used by every handoff template */
const HF = (() => {
  const SVGNS = "http://www.w3.org/2000/svg";
  const PROPS = ["checked", "value", "disabled", "selected"];
  function apply(el, a) {
    if (!a) return el;
    for (const [k, v] of Object.entries(a)) {
      if (v == null || v === false) continue;
      if (k === "class") el.setAttribute("class", v);
      else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
      else if (PROPS.includes(k)) el[k] = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    return el;
  }
  function add(el, kids) {
    for (const c of kids) {
      if (c == null || c === false) continue;
      if (Array.isArray(c)) add(el, c);
      else el.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  const h = (tag, a, ...kids) => add(apply(document.createElement(tag), a), kids);
  const s = (tag, a, ...kids) => add(apply(document.createElementNS(SVGNS, tag), a), kids);
  const $ = (sel, root = document) => root.querySelector(sel);
  const clear = (el) => { while (el.firstChild) el.removeChild(el.firstChild); return el; };

  /* inline markup: **term** and `code`; data is never parsed as HTML */
  function md(text) {
    return String(text ?? "").split(/(\*\*[^*]+\*\*|`[^`]+`)/).filter(Boolean).map((p) =>
      p.startsWith("**") ? h("strong", { class: "term" }, p.slice(2, -2))
      : p.startsWith("`") ? h("code", null, p.slice(1, -1)) : p);
  }

  const THEMES = ["auto", "light", "dark"];
  function themeButton() {
    let i = 0;
    const b = h("button", { class: "btn ghost noprint", type: "button" }, "Theme: auto");
    b.addEventListener("click", () => {
      i = (i + 1) % 3;
      const root = document.documentElement;
      if (THEMES[i] === "auto") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", THEMES[i]);
      b.textContent = "Theme: " + THEMES[i];
    });
    return b;
  }

  function header(d, kind, defaultAsk) {
    const dl = h("dl", { class: "meta" },
      h("dt", null, "Date"), h("dd", { class: "num" }, d.date),
      h("dt", null, "Source"), h("dd", { class: "src" }, d.source),
      h("dt", null, "Format"), h("dd", null, kind));
    return h("header", { class: "hd" },
      h("div", { class: "hd-top" }, h("span", { class: "chip" }, kind), themeButton()),
      h("div", null,
        h("h1", null, d.title),
        h("p", { class: "bottom" }, md(d.bottom_line)),
        h("p", { class: "ask" }, h("b", null, "Your move. "), md(d.ask || defaultAsk))),
      dl);
  }

  /* one copyable answer block per page; copyBtn() makes extra buttons wired to the same text */
  function answerBlock(heading, hint) {
    const ta = h("textarea", { readonly: true, rows: 6, "aria-label": heading, id: "answer-text" });
    const note = h("span", { class: "sr", role: "status", "aria-live": "polite" });
    const copyBtn = () => {
      const btn = h("button", { class: "btn pri copy-btn", type: "button" }, "Copy answers");
      btn.addEventListener("click", async () => {
        let ok = false;
        try { await navigator.clipboard.writeText(ta.value); ok = true; } catch (e) {
          ta.focus(); ta.select();
          try { ok = document.execCommand("copy"); } catch (e2) { ok = false; }
        }
        btn.textContent = ok ? "Copied" : "Selected, press Ctrl/Cmd+C";
        note.textContent = btn.textContent;
        setTimeout(() => { btn.textContent = "Copy answers"; }, 2200);
      });
      return btn;
    };
    const el = h("section", { class: "answer panel", "aria-labelledby": "answer-h" },
      h("h2", { id: "answer-h" }, heading), h("p", null, hint), ta, h("div", { class: "row" }, copyBtn(), note));
    return { el, copyBtn, set(text) { ta.value = text; ta.rows = Math.min(18, Math.max(5, text.split("\n").length + 1)); } };
  }

  /* hover and focus tooltip */
  let tipEl = null;
  function tip(el, textFn) {
    const show = (e) => {
      if (!tipEl) { tipEl = h("div", { class: "tip", role: "tooltip" }); document.body.append(tipEl); }
      tipEl.textContent = typeof textFn === "function" ? textFn() : textFn;
      tipEl.hidden = false;
      const r = e.type === "focus" ? el.getBoundingClientRect() : { left: e.clientX, bottom: e.clientY + 10, top: e.clientY };
      const w = tipEl.offsetWidth, x = Math.min(Math.max(8, r.left + 8), window.innerWidth - w - 8);
      tipEl.style.left = x + "px"; tipEl.style.top = Math.min(r.bottom + 6, window.innerHeight - 40) + "px";
    };
    const hide = () => { if (tipEl) tipEl.hidden = true; };
    el.addEventListener("mousemove", show); el.addEventListener("mouseenter", show);
    el.addEventListener("mouseleave", hide); el.addEventListener("focus", show); el.addEventListener("blur", hide);
  }

  function boot(render) {
    const root = document.getElementById("app");
    try {
      const data = JSON.parse(document.getElementById("handoff-data").textContent);
      document.title = data.title || document.title;
      render(root, data);
    } catch (err) {
      clear(root).append(h("div", { class: "fail", role: "alert" }, "This page could not render its data: " + err.message));
      console.error(err);
    }
  }
  return { h, s, $, clear, md, header, answerBlock, tip, boot };
})();
