
(() => {
  const LS_DONE = "lh:done";
  const LS_THEME = "lh:theme";
  const LS_RECENT = "lh:recent";
  const LS_OPEN = "lh:open";

  let manifest = null;
  let byId = new Map();   // id -> item
  let order = [];         // ordered ids
  let currentId = null;
  let scrollSpyObserver = null;

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
        }
        for (const it of group.items) {
          const a = document.createElement("a");
          a.className = "item";
          a.href = "#/" + it.id;
          a.dataset.itemId = it.id;
          if (done.has(it.id)) a.classList.add("done");
          if (currentId === it.id) a.classList.add("active");
          a.innerHTML = `<span class="check"></span><span>${escape(it.title)}</span>`;
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
      main.innerHTML = `<h1>Not found</h1><p>The page <code>${escape(id)}</code> doesn't exist. <a href="#/">Go home</a>.</p>`;
      currentId = null;
      buildTOC([]);
      return;
    }

    currentId = id;
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");

    try {
      const html = await fetchFragment(item.src);

      const bc = document.createElement("div");
      bc.className = "breadcrumb";
      bc.id = "breadcrumb";

      const actions = makeActions(item);

      const article = document.createElement("article");
      article.className = "md";
      article.innerHTML = html;

      const prevnext = buildPrevNext(item);

      main.innerHTML = "";
      main.appendChild(bc);
      main.appendChild(actions);
      main.appendChild(article);
      main.appendChild(prevnext);

      buildBreadcrumb(item);
      buildTOC(item.anchors);
      setupScrollSpy(item.anchors);
      highlightSidebar();
      pushRecent(id);

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
    } catch (e) {
      main.innerHTML = `<h1>Error</h1><p>${escape(e.message)}</p>`;
    }
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
    });
    wrap.appendChild(btn);

    if (item.tag) {
      const tag = document.createElement("span");
      tag.className = "tag";
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
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");
    buildTOC([]);
    if (scrollSpyObserver) scrollSpyObserver.disconnect();
    highlightSidebar();

    const done = getDone();
    const recent = getRecent().map(id => byId.get(id)).filter(Boolean);

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

    const recentHTML = recent.length === 0 ? "" : `
      <h2>Pick up where you left off</h2>
      <div class="cards">
        ${recent.map(it => `
          <div class="card recent">
            <h3>${escape(it.title)}</h3>
            <p>${escape(it.summary || "")}</p>
            <a class="go" href="#/${it.id}">Resume →</a>
          </div>`).join("")}
      </div>
    `;

    main.innerHTML = `
      <div class="hero">
        <h1>📚 Learning Hub</h1>
        <p>Two tracks. One discipline. From beginner to expert in <strong>data structures &amp; problem solving</strong> and <strong>system design</strong>.</p>
      </div>
      <h2>Tracks</h2>
      <div class="cards">${trackCards}</div>
      ${recentHTML}
      <h2>Keyboard shortcuts</h2>
      <table class="shortcut-table">
        <tr><td><span class="kbd">/</span></td><td>focus search</td></tr>
        <tr><td><span class="kbd">j</span> / <span class="kbd">k</span></td><td>next / previous topic</td></tr>
        <tr><td><span class="kbd">m</span></td><td>mark current as complete</td></tr>
        <tr><td><span class="kbd">t</span></td><td>toggle theme</td></tr>
        <tr><td><span class="kbd">g</span> <span class="kbd">h</span></td><td>go home</td></tr>
        <tr><td><span class="kbd">Esc</span></td><td>blur search</td></tr>
      </table>
    `;
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
      if (e.target.matches("input, textarea")) {
        if (e.key === "Escape") e.target.blur();
        return;
      }
      if (e.key === "/") {
        e.preventDefault();
        document.getElementById("search-input").focus();
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

    setupKeys();
    route();
  }

  init().catch(err => {
    document.getElementById("content").innerHTML =
      `<h1>Failed to load</h1><pre>${err.message}</pre>`;
  });
})();
