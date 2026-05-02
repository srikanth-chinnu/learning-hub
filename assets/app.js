
(() => {
  const LS_DONE = "lh:done";
  const LS_THEME = "lh:theme";
  const LS_RECENT = "lh:recent";
  const LS_OPEN = "lh:open";
  const LS_AUTO_MARK = "lh:auto-mark";

  let manifest = null;
  let byId = new Map();   // id -> item
  let order = [];         // ordered ids
  let currentId = null;
  let scrollSpyObserver = null;
  let autoMarkTimer = null;

  // --- localStorage helpers --- //
  const lsGet = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const lsSet = (k, v) => localStorage.setItem(k, JSON.stringify(v));

  function getDone() { return new Set(lsGet(LS_DONE, [])); }
  function setDone(set) { lsSet(LS_DONE, [...set]); }
  function isDone(id) { return getDone().has(id); }
  function toggleDone(id) {
    const s = getDone();
    if (s.has(id)) s.delete(id); else s.add(id);
    setDone(s);
    return s.has(id);
  }

  function getRecent() { return lsGet(LS_RECENT, []); }
  function pushRecent(id) {
    const r = [id, ...getRecent().filter(x => x !== id)].slice(0, 5);
    lsSet(LS_RECENT, r);
  }

  function getOpenTracks() { return new Set(lsGet(LS_OPEN, ["roadmap", "dsa", "sd"])); }
  function setOpenTracks(s) { lsSet(LS_OPEN, [...s]); }

  function getAutoMark() { return !!lsGet(LS_AUTO_MARK, false); }
  function setAutoMark(v) { lsSet(LS_AUTO_MARK, !!v); }

  // --- toast notifications --- //
  function showToast(msg, kind) {
    const stack = document.getElementById("toasts");
    if (!stack) return;
    const el = document.createElement("div");
    el.className = "toast" + (kind ? " " + kind : "");
    el.textContent = msg;
    stack.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  // --- modals --- //
  function showModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add("open");
    m.setAttribute("aria-hidden", "false");
    const focusable = m.querySelector("button, input, [tabindex]");
    if (focusable) focusable.focus();
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.remove("open");
    m.setAttribute("aria-hidden", "true");
  }
  function closeAllModals() {
    document.querySelectorAll(".modal.open").forEach(m => closeModal(m.id));
  }
  function isAnyModalOpen() {
    return document.querySelector(".modal.open") !== null;
  }

  // --- theme --- //
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = t === "light" ? "🌙" : "☀️";
  }
  function toggleTheme() {
    const cur = document.documentElement.dataset.theme || "dark";
    const nxt = cur === "dark" ? "light" : "dark";
    lsSet(LS_THEME, nxt);
    applyTheme(nxt);
  }

  // --- routing --- //
  function parseHash() {
    const h = (location.hash || "").replace(/^#\/?/, "");
    if (!h) return { id: null, anchor: null };
    const [id, anchor] = h.split("#");
    return { id: id || null, anchor: anchor || null };
  }

  function navigate(id, anchor) {
    let h = "#/";
    if (id) h += id;
    if (anchor) h += "#" + anchor;
    if (location.hash !== h) {
      location.hash = h;
    } else {
      route();
    }
  }

  // --- sidebar --- //
  function buildSidebar() {
    const sb = document.getElementById("sidebar");
    sb.innerHTML = "";
    const open = getOpenTracks();
    const done = getDone();

    for (const track of manifest.tracks) {
      const trackEl = document.createElement("div");
      trackEl.className = "track";
      trackEl.dataset.trackId = track.id;
      trackEl.dataset.open = open.has(track.id) ? "true" : "false";

      const header = document.createElement("div");
      header.className = "track-header";

      const trackItems = track.groups.flatMap(g => g.items);
      const doneCount = trackItems.filter(it => done.has(it.id)).length;
      const total = trackItems.length;

      header.innerHTML = `
        <span class="chev">▶</span>
        <span>${track.icon} ${escape(track.title)}</span>
        <span class="track-progress">${doneCount}/${total}</span>
      `;
      header.addEventListener("click", () => {
        const o = getOpenTracks();
        if (trackEl.dataset.open === "true") {
          trackEl.dataset.open = "false";
          o.delete(track.id);
        } else {
          trackEl.dataset.open = "true";
          o.add(track.id);
        }
        setOpenTracks(o);
      });
      trackEl.appendChild(header);

      const body = document.createElement("div");
      body.className = "track-body";

      for (const group of track.groups) {
        if (track.groups.length > 1) {
          const gt = document.createElement("div");
          gt.className = "group-title";
          gt.textContent = group.title;
          body.appendChild(gt);

          // group progress bar
          const gDone = group.items.filter(it => done.has(it.id)).length;
          const gTotal = group.items.length;
          const gPct = gTotal ? Math.round((gDone / gTotal) * 100) : 0;
          const gBar = document.createElement("div");
          gBar.className = "group-bar";
          gBar.dataset.group = `${track.id}::${group.title}`;
          gBar.innerHTML = `<span style="width:${gPct}%"></span>`;
          body.appendChild(gBar);
        }
        for (const it of group.items) {
          const a = document.createElement("a");
          a.className = "item";
          a.href = "#/" + it.id;
          a.dataset.itemId = it.id;
          if (done.has(it.id)) a.classList.add("done");
          if (currentId === it.id) a.classList.add("active");
          const meta = it.read_min ? `<span class="item-meta">${it.read_min} min read</span>` : "";
          a.innerHTML = `<span class="check"></span><span class="title-line">${escape(it.title)}</span>${meta}`;
          body.appendChild(a);
        }
      }

      trackEl.appendChild(body);
      sb.appendChild(trackEl);
    }
  }

  function highlightSidebar() {
    document.querySelectorAll("#sidebar a.item").forEach(a => {
      a.classList.toggle("active", a.dataset.itemId === currentId);
    });
  }

  function refreshSidebarProgress() {
    const done = getDone();
    document.querySelectorAll("#sidebar a.item").forEach(a => {
      a.classList.toggle("done", done.has(a.dataset.itemId));
    });
    document.querySelectorAll("#sidebar .track").forEach(tr => {
      const id = tr.dataset.trackId;
      const track = manifest.tracks.find(t => t.id === id);
      if (!track) return;
      const trackItems = track.groups.flatMap(g => g.items);
      const dn = trackItems.filter(it => done.has(it.id)).length;
      const prog = tr.querySelector(".track-progress");
      if (prog) prog.textContent = `${dn}/${trackItems.length}`;

      // group bars
      for (const g of track.groups) {
        const sel = `[data-group="${id}::${g.title.replace(/"/g, '\\"')}"]`;
        const bar = tr.querySelector(sel + " > span");
        if (bar) {
          const gd = g.items.filter(it => done.has(it.id)).length;
          const gPct = g.items.length ? Math.round((gd / g.items.length) * 100) : 0;
          bar.style.width = gPct + "%";
        }
      }
    });
    refreshTopbarProgress();
  }

  function refreshTopbarProgress() {
    const done = getDone();
    const total = order.length;
    const dn = order.filter(id => done.has(id)).length;
    const pct = total ? Math.round((dn / total) * 100) : 0;
    const pill = document.getElementById("global-progress");
    if (pill) {
      pill.querySelector(".bar > span").style.width = pct + "%";
      pill.querySelector(".pct").textContent = `${dn}/${total} · ${pct}%`;
    }
  }

  // --- search --- //
  function filterSidebar(q) {
    q = q.trim().toLowerCase();
    const sb = document.getElementById("sidebar");
    sb.querySelectorAll(".empty-search").forEach(e => e.remove());
    let anyShown = false;
    sb.querySelectorAll(".track").forEach(tr => {
      let trackHasMatch = false;
      tr.querySelectorAll("a.item").forEach(a => {
        const t = a.textContent.toLowerCase();
        const match = !q || t.includes(q);
        a.style.display = match ? "" : "none";
        if (match) trackHasMatch = true;
      });
      tr.querySelectorAll(".group-title").forEach(g => {
        let next = g.nextElementSibling;
        let any = false;
        while (next && next.classList.contains("item")) {
          if (next.style.display !== "none") { any = true; break; }
          next = next.nextElementSibling;
        }
        g.style.display = any ? "" : "none";
      });
      tr.style.display = trackHasMatch ? "" : "none";
      if (q && trackHasMatch) tr.dataset.open = "true";
      if (trackHasMatch) anyShown = true;
    });
    if (!anyShown) {
      const e = document.createElement("div");
      e.className = "empty-search";
      e.textContent = `No matches for "${q}"`;
      sb.appendChild(e);
    }
  }

  // --- TOC right rail --- //
  function buildTOC(anchors) {
    const rail = document.getElementById("toc-rail");
    if (!anchors || anchors.length === 0) {
      rail.innerHTML = "";
      return;
    }
    const html = ['<h4>On this page</h4>'];
    for (const a of anchors) {
      html.push(`<a href="#/${currentId}#${a.id}" class="l${a.level}" data-anchor="${a.id}">${escape(a.text)}</a>`);
    }
    rail.innerHTML = html.join("");
  }

  function setupScrollSpy(anchors) {
    if (scrollSpyObserver) scrollSpyObserver.disconnect();
    if (!anchors || anchors.length === 0) return;
    const ids = new Set(anchors.map(a => a.id));
    const targets = [];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) targets.push(el);
    });
    if (targets.length === 0) return;
    scrollSpyObserver = new IntersectionObserver(entries => {
      const visible = entries
        .filter(e => e.isIntersecting)
        .sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top);
      if (visible.length === 0) return;
      const id = visible[0].target.id;
      document.querySelectorAll("#toc-rail a").forEach(a => {
        a.classList.toggle("active", a.dataset.anchor === id);
      });
    }, { rootMargin: "-80px 0px -65% 0px", threshold: 0.01 });
    targets.forEach(t => scrollSpyObserver.observe(t));
  }

  // --- breadcrumb --- //
  function buildBreadcrumb(item) {
    const bc = document.getElementById("breadcrumb");
    const track = manifest.tracks.find(t => t.groups.some(g => g.items.some(i => i.id === item.id)));
    const group = track ? track.groups.find(g => g.items.some(i => i.id === item.id)) : null;
    const parts = [`<a href="#/">🏠 Home</a>`];
    if (track) parts.push(`<span class="sep">›</span>${track.icon} ${escape(track.title)}`);
    if (group && track && track.groups.length > 1) parts.push(`<span class="sep">›</span>${escape(group.title)}`);
    parts.push(`<span class="sep">›</span>${escape(item.title)}`);
    bc.innerHTML = parts.join("");
  }

  // --- render --- //
  async function fetchFragment(src) {
    const res = await fetch(src + "?_=" + Date.now());
    if (!res.ok) throw new Error("Failed to load: " + src);
    return res.text();
  }

  async function renderItem(id, anchor) {
    const item = byId.get(id);
    const main = document.getElementById("content");
    if (!item) {
      document.title = "Not found · Learning Hub";
      main.innerHTML = `<h1>Not found</h1><p>The page <code>${escape(id)}</code> doesn't exist. <a href="#/">Go home</a>.</p>`;
      currentId = null;
      buildTOC([]);
      updateBackToTop();
      return;
    }

    currentId = id;
    document.title = item.title + " · Learning Hub";
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");

    main.innerHTML = `<div class="loading active"><div class="spinner"></div><span>Loading ${escape(item.title)}…</span></div>`;

    try {
      const html = await fetchFragment(item.src);

      const bc = document.createElement("div");
      bc.className = "breadcrumb";
      bc.id = "breadcrumb";

      const actions = makeActions(item);
      const meta = makePageMeta(item);

      const article = document.createElement("article");
      article.className = "md";
      article.innerHTML = html;

      const prevnext = buildPrevNext(item);

      main.innerHTML = "";
      main.appendChild(bc);
      main.appendChild(actions);
      if (meta) main.appendChild(meta);
      main.appendChild(article);
      main.appendChild(prevnext);

      buildBreadcrumb(item);
      buildTOC(item.anchors);
      setupScrollSpy(item.anchors);
      highlightSidebar();
      pushRecent(id);
      armAutoMark(item);

      if (anchor) {
        const el = document.getElementById(anchor);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          window.scrollTo({ top: 0 });
        }
      } else {
        window.scrollTo({ top: 0 });
      }
      updateReadingProgress();
      updateBackToTop();
    } catch (e) {
      main.innerHTML = `<h1>Error loading content</h1><p>${escape(e.message)}</p><p><a href="#/">Go home</a></p>`;
      showToast("Failed to load: " + e.message, "error");
    }
  }

  function makePageMeta(item) {
    const parts = [];
    if (item.read_min) parts.push(`<span class="read-time">${item.read_min} min read</span>`);
    if (item.words)    parts.push(`<span class="word-count">${item.words.toLocaleString()} words</span>`);
    if (parts.length === 0) return null;
    const m = document.createElement("div");
    m.className = "page-meta";
    m.innerHTML = parts.join('<span class="dot">·</span>');
    return m;
  }

  function makeActions(item) {
    const wrap = document.createElement("div");
    wrap.className = "page-actions";

    const done = isDone(item.id);
    const btn = document.createElement("button");
    btn.className = "btn " + (done ? "done" : "primary");
    btn.id = "mark-done-btn";
    btn.innerHTML = done ? "✓ Completed" : "Mark as complete";
    btn.addEventListener("click", () => {
      const now = toggleDone(item.id);
      btn.className = "btn " + (now ? "done" : "primary");
      btn.innerHTML = now ? "✓ Completed" : "Mark as complete";
      refreshSidebarProgress();
      showToast(now ? `Marked complete: ${item.title}` : `Unmarked: ${item.title}`, now ? null : "info");
    });
    wrap.appendChild(btn);

    if (item.tag) {
      const tag = document.createElement("span");
      tag.className = "tag " + escapeClass(item.tag);
      tag.textContent = item.tag;
      wrap.appendChild(tag);
    }

    const top = document.createElement("button");
    top.className = "btn";
    top.textContent = "↑ Top";
    top.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    wrap.appendChild(top);

    return wrap;
  }

  function buildPrevNext(item) {
    const wrap = document.createElement("div");
    wrap.className = "prevnext";
    const prevId = item.prev;
    const nextId = item.next;
    const prev = prevId ? byId.get(prevId) : null;
    const nxt = nextId ? byId.get(nextId) : null;
    if (prev) {
      wrap.innerHTML += `<a href="#/${prev.id}" class="prev"><div class="label">← Previous</div><div class="title">${escape(prev.title)}</div></a>`;
    } else {
      wrap.innerHTML += "<span></span>";
    }
    if (nxt) {
      wrap.innerHTML += `<a href="#/${nxt.id}" class="next"><div class="label">Next →</div><div class="title">${escape(nxt.title)}</div></a>`;
    } else {
      wrap.innerHTML += "<span></span>";
    }
    return wrap;
  }

  // --- home --- //
  function renderHome() {
    const main = document.getElementById("content");
    currentId = null;
    document.title = "Learning Hub — DSA & System Design";
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");
    buildTOC([]);
    if (scrollSpyObserver) scrollSpyObserver.disconnect();
    highlightSidebar();

    const done = getDone();
    const recent = getRecent().map(id => byId.get(id)).filter(Boolean);
    const isFirstTime = done.size === 0 && recent.length === 0;

    const trackCards = manifest.tracks.map(t => {
      const items = t.groups.flatMap(g => g.items);
      const dn = items.filter(it => done.has(it.id)).length;
      const total = items.length;
      const pct = total ? Math.round((dn / total) * 100) : 0;
      const first = items.find(it => !done.has(it.id)) || items[0];
      return `
        <div class="card">
          <h3>${t.icon} ${escape(t.title)}</h3>
          <p>${escape(t.id === "roadmap" ? "Read this first. Four-phase plan with kill switches." :
                      t.id === "dsa"     ? "77 topics across Beginner → Intermediate → Advanced → Expert + Meta." :
                                          "Tiers, 20 five-minute reads, trade-offs deep dive, books and papers.")}</p>
          <div class="progress-line"><span>${dn}/${total}</span><div class="bar"><span style="width:${pct}%"></span></div><span>${pct}%</span></div>
          <a class="go" href="#/${first ? first.id : ""}">${dn > 0 ? "Continue →" : "Start →"}</a>
        </div>`;
    }).join("");

    const continueCard = recent.length === 0 ? "" : `
      <div class="continue-card">
        <div class="ico">📖</div>
        <div class="body">
          <div class="label">Continue where you left off</div>
          <h3>${escape(recent[0].title)}</h3>
          <p class="desc">${escape(recent[0].summary || "")}</p>
        </div>
        <a class="btn primary" href="#/${recent[0].id}">Resume →</a>
      </div>
    `;

    const moreRecentHTML = recent.length <= 1 ? "" : `
      <h2>Recently viewed</h2>
      <div class="cards">
        ${recent.slice(1).map(it => `
          <div class="card recent">
            <h3>${escape(it.title)}</h3>
            <p>${escape(it.summary || "")}</p>
            <a class="go" href="#/${it.id}">Open →</a>
          </div>`).join("")}
      </div>
    `;

    const roadmap = manifest.tracks.find(t => t.id === "roadmap");
    const startId = roadmap ? roadmap.groups[0].items[0].id : (manifest.tracks[0].groups[0].items[0].id);

    const heroHTML = isFirstTime ? `
      <div class="hero welcome">
        <h1>👋 Welcome to your Learning Hub</h1>
        <p>Two tracks. One discipline. From beginner to expert in <strong>data structures &amp; problem solving</strong> and <strong>system design</strong>.</p>
        <div class="lede">
          <span>📚 ${order.length} topics</span>
          <span>⏱ 5-minute reads + deep dives</span>
          <span>⌨️ Keyboard-first</span>
          <span>📊 Progress saved locally</span>
        </div>
        <a class="cta" href="#/${startId}">Start with the Roadmap →</a>
      </div>
    ` : `
      <div class="hero">
        <h1>📚 Learning Hub</h1>
        <p>Pick a track. Mark topics complete as you go. Press <span class="kbd">?</span> for keyboard shortcuts.</p>
      </div>
    `;

    main.innerHTML = `
      ${heroHTML}
      ${continueCard}
      <h2>Tracks</h2>
      <div class="cards">${trackCards}</div>
      ${moreRecentHTML}
    `;
    updateReadingProgress();
    updateBackToTop();
  }

  // --- main route --- //
  function route() {
    const { id, anchor } = parseHash();
    if (!id) {
      renderHome();
    } else {
      renderItem(id, anchor);
    }
  }

  // --- keyboard --- //
  function setupKeys() {
    let gHeld = false;
    let gTimer = null;
    document.addEventListener("keydown", e => {
      // close modals on Esc regardless of focus target
      if (e.key === "Escape" && isAnyModalOpen()) {
        e.preventDefault();
        closeAllModals();
        return;
      }
      if (e.target.matches("input, textarea")) {
        if (e.key === "Escape") e.target.blur();
        return;
      }
      if (isAnyModalOpen()) return;
      if (e.key === "/") {
        e.preventDefault();
        document.getElementById("search-input").focus();
      } else if (e.key === "?") {
        e.preventDefault();
        showModal("help-modal");
      } else if (e.key === "j") {
        if (!currentId) return;
        const it = byId.get(currentId);
        if (it && it.next) navigate(it.next);
      } else if (e.key === "k") {
        if (!currentId) return;
        const it = byId.get(currentId);
        if (it && it.prev) navigate(it.prev);
      } else if (e.key === "m") {
        if (currentId) {
          const btn = document.getElementById("mark-done-btn");
          if (btn) btn.click();
        }
      } else if (e.key === "t") {
        toggleTheme();
      } else if (e.key === "g") {
        gHeld = true;
        clearTimeout(gTimer);
        gTimer = setTimeout(() => { gHeld = false; }, 800);
      } else if (e.key === "h" && gHeld) {
        gHeld = false;
        navigate("");
      }
    });
  }

  // --- helpers --- //
  function escape(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }
  function escapeClass(s) {
    // produce a CSS-class-safe token from a tag value
    return String(s ?? "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  }

  // --- reading progress bar --- //
  function updateReadingProgress() {
    const bar = document.querySelector(".reading-progress > span");
    if (!bar) return;
    const h = document.documentElement;
    const max = (h.scrollHeight - h.clientHeight) || 1;
    const pct = Math.min(100, Math.max(0, (h.scrollTop / max) * 100));
    bar.style.width = pct + "%";
  }

  // --- back to top button --- //
  function updateBackToTop() {
    const btn = document.getElementById("back-to-top");
    if (!btn) return;
    btn.classList.toggle("visible", window.scrollY > 400);
  }

  // --- auto-mark on scroll --- //
  function armAutoMark(item) {
    if (autoMarkTimer) {
      clearTimeout(autoMarkTimer);
      autoMarkTimer = null;
    }
    if (!getAutoMark() || !item || isDone(item.id)) return;
    // checked from main scroll listener instead of separate observer
    armAutoMark.itemId = item.id;
  }
  function checkAutoMark() {
    if (!getAutoMark()) return;
    const id = armAutoMark.itemId;
    if (!id || id !== currentId || isDone(id)) return;
    const h = document.documentElement;
    const max = (h.scrollHeight - h.clientHeight) || 1;
    const pct = (h.scrollTop / max) * 100;
    if (pct >= 90) {
      toggleDone(id);
      const btn = document.getElementById("mark-done-btn");
      if (btn) {
        btn.className = "btn done";
        btn.innerHTML = "✓ Completed";
      }
      refreshSidebarProgress();
      showToast(`Auto-marked: ${byId.get(id).title}`, "info");
      armAutoMark.itemId = null;
    }
  }

  // --- modal & button wiring --- //
  function wireModals() {
    document.querySelectorAll("[data-modal-close]").forEach(el => {
      el.addEventListener("click", () => {
        const m = el.closest(".modal");
        if (m) closeModal(m.id);
      });
    });
    const helpBtn = document.getElementById("help-btn");
    if (helpBtn) helpBtn.addEventListener("click", () => showModal("help-modal"));
    const settingsBtn = document.getElementById("settings-btn");
    if (settingsBtn) settingsBtn.addEventListener("click", openSettings);
  }
  function openSettings() {
    const cb = document.getElementById("setting-auto-mark");
    if (cb) cb.checked = getAutoMark();
    showModal("settings-modal");
  }
  function wireSettings() {
    const cb = document.getElementById("setting-auto-mark");
    if (cb) {
      cb.addEventListener("change", () => {
        setAutoMark(cb.checked);
        showToast(cb.checked ? "Auto-mark enabled" : "Auto-mark disabled", "info");
      });
    }
    const reset = document.getElementById("reset-progress-btn");
    if (reset) {
      reset.addEventListener("click", () => {
        if (!confirm("Reset all progress? This will clear completed topics, recents, and open tracks. Cannot be undone.")) return;
        try { localStorage.removeItem(LS_DONE); } catch {}
        try { localStorage.removeItem(LS_RECENT); } catch {}
        try { localStorage.removeItem(LS_OPEN); } catch {}
        try { localStorage.removeItem(LS_AUTO_MARK); } catch {}
        const cb2 = document.getElementById("setting-auto-mark");
        if (cb2) cb2.checked = false;
        buildSidebar();
        refreshSidebarProgress();
        route();
        closeModal("settings-modal");
        showToast("Progress reset", "info");
      });
    }
    const exp = document.getElementById("export-progress-btn");
    if (exp) {
      exp.addEventListener("click", () => {
        const data = {
          exportedAt: new Date().toISOString(),
          done: [...getDone()],
          recent: getRecent(),
          openTracks: [...getOpenTracks()],
          autoMark: getAutoMark()
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `learning-hub-progress-${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        showToast("Progress exported", "info");
      });
    }
  }

  // --- bootstrap --- //
  async function init() {
    applyTheme(lsGet(LS_THEME, "dark"));
    document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
    document.getElementById("sidebar-toggle").addEventListener("click", () => {
      document.body.dataset.sidebar = document.body.dataset.sidebar === "open" ? "" : "open";
    });

    const res = await fetch("manifest.json?_=" + Date.now());
    manifest = await res.json();
    byId = new Map();
    order = [];
    for (const t of manifest.tracks) {
      for (const g of t.groups) {
        for (const it of g.items) {
          byId.set(it.id, it);
          order.push(it.id);
        }
      }
    }

    buildSidebar();
    refreshSidebarProgress();

    document.getElementById("search-input").addEventListener("input", e => {
      filterSidebar(e.target.value);
    });

    window.addEventListener("hashchange", route);
    document.addEventListener("click", e => {
      const a = e.target.closest("a[href^='#/']");
      if (a && document.body.dataset.sidebar === "open") {
        document.body.dataset.sidebar = "";
      }
    });

    // sidebar backdrop click closes mobile sidebar
    const backdrop = document.getElementById("sidebar-backdrop");
    if (backdrop) backdrop.addEventListener("click", () => {
      document.body.dataset.sidebar = "";
    });

    // reading progress + back-to-top + auto-mark on scroll
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        updateReadingProgress();
        updateBackToTop();
        checkAutoMark();
        ticking = false;
      });
    }, { passive: true });

    // back-to-top button
    const btt = document.getElementById("back-to-top");
    if (btt) btt.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    wireModals();
    wireSettings();

    setupKeys();
    route();
  }

  init().catch(err => {
    document.getElementById("content").innerHTML =
      `<h1>Failed to load</h1><pre>${err.message}</pre>`;
  });
})();
