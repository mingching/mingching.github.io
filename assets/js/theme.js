/* Redesign interactions: theme toggle, scroll reveal, stat counters,
   hero typing effect, news show-more. Vanilla JS, no dependencies. */
(function () {
  "use strict";

  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Theme toggle ---------- */
  var root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("van-theme", theme);
    } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#0d1117" : "#ffffff");
  }

  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }

  /* ---------- Scroll reveal (staggered) ---------- */
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window && !reduceMotion) {
    var lastTime = 0;
    var stagger = 0;
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var now = performance.now();
          /* items revealed in the same burst get a small cascading delay (capped) */
          stagger = now - lastTime < 120 ? Math.min(stagger + 60, 360) : 0;
          lastTime = now;
          entry.target.style.setProperty("--reveal-delay", stagger + "ms");
          entry.target.classList.add("revealed");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("revealed"); });
  }

  /* ---------- Count-up animation ---------- */
  function countUp(el, target) {
    if (reduceMotion || !window.requestAnimationFrame) {
      el.textContent = target;
      return;
    }
    var duration = 1100;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); /* ease-out cubic */
      el.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
    /* safety net: rAF can stall (background tab, frozen virtual time) —
       make sure the final value always lands */
    setTimeout(function () { el.textContent = target; }, duration + 400);
  }

  /* Static counters (from data-count) start when scrolled into view */
  var counters = Array.prototype.slice.call(document.querySelectorAll(".js-count"));
  if ("IntersectionObserver" in window) {
    var cio = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          countUp(entry.target, parseInt(entry.target.getAttribute("data-count"), 10) || 0);
          cio.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(function (el) {
      el.textContent = el.getAttribute("data-count") || "0";
    });
  }

  /* Live Google-Scholar stats (event fired by fetch_google_scholar_stats.html) */
  document.addEventListener("gs-stats-loaded", function (ev) {
    var data = ev.detail || {};
    var cit = document.querySelector(".stats-row .js-cit-count");
    if (cit && typeof data.citedby !== "undefined") {
      countUp(cit, parseInt(data.citedby, 10) || 0);
    }
    var hEl = document.querySelector(".js-hindex");
    var hTile = document.querySelector(".js-hindex-tile");
    if (hEl && hTile && typeof data.hindex !== "undefined") {
      hTile.removeAttribute("hidden");
      countUp(hEl, parseInt(data.hindex, 10) || 0);
    }
    renderCitationChips(data.articles || []);
    renderCitationSpark(data.graph || []);
  });

  /* ---------- Per-paper "Cited by N" chips ---------- */
  function normTitle(s) {
    return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
  }
  function renderCitationChips(articles) {
    if (!articles.length) return;
    var index = articles.map(function (a) {
      return {
        t: normTitle(a.title),
        n: a.cited_by && a.cited_by.value ? parseInt(a.cited_by.value, 10) : 0
      };
    });
    Array.prototype.forEach.call(
      document.querySelectorAll(".pub-card[data-cite-title]"),
      function (card) {
        var t = normTitle(card.getAttribute("data-cite-title"));
        if (!t) return;
        var hit = null;
        for (var i = 0; i < index.length; i++) {
          var a = index[i];
          if (!a.t) continue;
          if (a.t === t || a.t.indexOf(t.slice(0, 40)) === 0 || t.indexOf(a.t.slice(0, 40)) === 0) {
            hit = a;
            break;
          }
        }
        if (!hit || hit.n < 1) return;
        var tags = card.querySelector(".pub-card__tags");
        if (!tags) return;
        var chip = document.createElement("span");
        chip.className = "cite-chip";
        chip.innerHTML = '<i class="fas fa-chart-line" aria-hidden="true"></i> Cited by ' + hit.n;
        tags.appendChild(chip);
      }
    );
  }

  /* ---------- Citation trend sparkline (in the Total citations tile) ---------- */
  function renderCitationSpark(graph) {
    var cit = document.querySelector(".stats-row .js-cit-count");
    if (!cit || graph.length < 2) return;
    var tile = cit.closest ? cit.closest(".stat-tile") : null;
    if (!tile || tile.querySelector(".stat-tile__trend")) return;
    var pts = graph
      .slice()
      .sort(function (a, b) { return a.year - b.year; })
      .slice(-12);
    var w = Math.max(tile.clientWidth - 32, 80);
    var h = 26;
    var max = 0;
    pts.forEach(function (p) { if (p.citations > max) max = p.citations; });
    if (max < 1) return;
    var step = w / (pts.length - 1);
    var coords = pts.map(function (p, i) {
      return [i * step, h - 2 - (p.citations / max) * (h - 6)];
    });
    var line = coords.map(function (c) { return c[0].toFixed(1) + "," + c[1].toFixed(1); }).join(" ");
    var last = coords[coords.length - 1];
    var prev = coords[coords.length - 2];
    var svgns = "http://www.w3.org/2000/svg";
    var wrap = document.createElement("span");
    wrap.className = "stat-tile__trend";
    wrap.title = "Citations per year (" + pts[0].year + "–" + pts[pts.length - 1].year + ")";
    var svg = document.createElementNS(svgns, "svg");
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
    svg.setAttribute("aria-hidden", "true");
    var poly = document.createElementNS(svgns, "polyline");
    poly.setAttribute("points", line);
    poly.setAttribute("class", "spark-line");
    svg.appendChild(poly);
    var seg = document.createElementNS(svgns, "polyline");
    seg.setAttribute("points", prev[0].toFixed(1) + "," + prev[1].toFixed(1) + " " + last[0].toFixed(1) + "," + last[1].toFixed(1));
    seg.setAttribute("class", "spark-line spark-line--accent");
    svg.appendChild(seg);
    var dot = document.createElementNS(svgns, "circle");
    dot.setAttribute("cx", last[0].toFixed(1));
    dot.setAttribute("cy", last[1].toFixed(1));
    dot.setAttribute("r", "2.5");
    dot.setAttribute("class", "spark-dot");
    svg.appendChild(dot);
    wrap.appendChild(svg);
    tile.appendChild(wrap);
  }

  /* ---------- Card 3D tilt + cursor spotlight ---------- */
  var canHover =
    window.matchMedia &&
    window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (canHover && !reduceMotion) {
    Array.prototype.forEach.call(document.querySelectorAll(".pub-card"), function (card) {
      card.addEventListener("mouseenter", function () {
        card.classList.add("is-tilting");
      });
      card.addEventListener("mousemove", function (e) {
        var r = card.getBoundingClientRect();
        var x = e.clientX - r.left;
        var y = e.clientY - r.top;
        var rx = (y / r.height - 0.5) * -4;
        var ry = (x / r.width - 0.5) * 4;
        card.style.transform =
          "translateY(-4px) perspective(900px) rotateX(" + rx.toFixed(2) +
          "deg) rotateY(" + ry.toFixed(2) + "deg)";
        card.style.setProperty("--mx", x + "px");
        card.style.setProperty("--my", y + "px");
      });
      card.addEventListener("mouseleave", function () {
        card.classList.remove("is-tilting");
        card.style.transform = "";
      });
    });
  }

  /* ---------- Hero typing effect ---------- */
  var typingEl = document.getElementById("hero-typing");
  if (typingEl) {
    var roles = [];
    try {
      roles = JSON.parse(typingEl.getAttribute("data-roles")) || [];
    } catch (e) {}
    if (!roles.length) roles = ["CV / DL Researcher"];
    if (reduceMotion) {
      typingEl.textContent = roles[0];
    } else {
      var ri = 0, ci = 0, deleting = false;
      (function tick() {
        var word = roles[ri];
        typingEl.textContent = word.slice(0, ci);
        var delay;
        if (!deleting) {
          ci++;
          delay = 55 + Math.random() * 45;
          if (ci > word.length) { deleting = true; delay = 1700; }
        } else {
          ci--;
          delay = 28;
          if (ci === 0) { deleting = false; ri = (ri + 1) % roles.length; delay = 350; }
        }
        setTimeout(tick, delay);
      })();
    }
  }

  /* ---------- News show-more ---------- */
  var moreBtn = document.getElementById("news-more-btn");
  if (moreBtn) {
    moreBtn.addEventListener("click", function () {
      var extras = document.querySelectorAll("#news-timeline .timeline__item--extra");
      var opening = !moreBtn.classList.contains("is-open");
      Array.prototype.forEach.call(extras, function (el) {
        if (opening) {
          el.removeAttribute("hidden");
          el.classList.add("revealed");
        } else {
          el.setAttribute("hidden", "");
        }
      });
      moreBtn.classList.toggle("is-open", opening);
      moreBtn.childNodes[0].textContent =
        (opening ? moreBtn.getAttribute("data-less") : moreBtn.getAttribute("data-more")) + " ";
      if (!opening) {
        var section = document.getElementById("news-timeline");
        if (section) section.scrollIntoView({ block: "start", behavior: reduceMotion ? "auto" : "smooth" });
      }
    });
  }
})();
