/**
 * Utilitários globais: ícones, scroll, mapa intercidades, pesquisa, tema, reveal.
 * (Sem cursor custom / magnetic — inativos no PWA.)
 */
(function () {
  "use strict";

  function labelDataTables() {
    document.querySelectorAll("table.data").forEach(function (table) {
      var headers = Array.prototype.map.call(table.querySelectorAll("thead th"), function (th) {
        return th.textContent.replace(/\s+/g, " ").trim();
      });
      if (!headers.length) return;
      table.querySelectorAll("tbody tr").forEach(function (tr) {
        tr.querySelectorAll("td").forEach(function (td, i) {
          if (headers[i]) td.setAttribute("data-label", headers[i]);
        });
      });
    });
  }

  window.refreshLucide = function refreshLucide() {
    var ok = false;
    try {
      if (typeof lucide !== "undefined" && lucide.createIcons) {
        lucide.createIcons({ attrs: { "stroke-width": 1.75 } });
        ok = true;
      }
    } catch (e1) {}
    if (ok) return;
    var m = {
      layers: "\u2261",
      plane: "\u2708",
      sun: "\u2600",
      moon: "\u263d",
      wallet: "\u20AC",
      "arrow-up": "\u2191",
      wine: "\ud83c\udf77",
      compass: "\ud83e\udded",
      home: "\u2302",
      calendar: "\u2637",
      map: "\u29C9",
      list: "\u2630",
      search: "\u2315",
    };
    m["minimize-2"] = "\u2014";
    document.querySelectorAll("i[data-lucide]").forEach(function (el) {
      if (el.querySelector("svg")) return;
      var n = el.getAttribute("data-lucide");
      el.textContent = m[n] || "\u2022";
      el.classList.add("lucide-ico--fallback");
    });
  };

  function showStorageWarning() {
    var el = document.getElementById("appStorageToast");
    if (!el) return;
    el.removeAttribute("hidden");
    el.setAttribute("aria-hidden", "false");
    if (window.__roteiroStorageT) clearTimeout(window.__roteiroStorageT);
    window.__roteiroStorageT = setTimeout(function () {
      el.setAttribute("hidden", "");
      el.setAttribute("aria-hidden", "true");
    }, 5200);
  }

  function parseRevealStaggerMs(el) {
    var raw = getComputedStyle(el).getPropertyValue("--reveal-stagger").trim();
    var n = parseFloat(raw);
    return isNaN(n) ? 0 : n;
  }

  function runSpringReveal(el) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.classList.add("reveal-motion-done");
      return;
    }
    var y = 52;
    var vy = 0;
    var stiffness = 350;
    var damping = 20;
    var last = performance.now();
    function tick(now) {
      var dt = Math.min(0.045, (now - last) / 1000);
      last = now;
      var ay = -stiffness * y - damping * vy;
      vy += ay * dt;
      y += vy * dt;
      el.style.transform = "translate3d(0," + y.toFixed(3) + "px,0) scale(0.985)";
      if (Math.abs(y) < 0.085 && Math.abs(vy) < 0.42) {
        el.style.transform = "";
        el.classList.add("reveal-motion-done");
        return;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  var __appM = document.getElementById("appMain");

  function __getScrollPort() {
    if (!__appM) return document.scrollingElement || document.documentElement;
    var cs = getComputedStyle(__appM);
    if (cs.overflowY === "visible") return document.scrollingElement || document.documentElement;
    if (__appM.scrollHeight > __appM.clientHeight + 2) return __appM;
    return document.scrollingElement || document.documentElement;
  }

  function __getScrollY() {
    var p = __getScrollPort();
    return p && p === __appM ? p.scrollTop : window.scrollY || document.documentElement.scrollTop;
  }

  function __setScrollTopInstant(y) {
    var p = __getScrollPort();
    if (p === __appM && __appM) p.scrollTop = y;
    else window.scrollTo(0, y);
  }

  function scrollToElementHighSpeedDecel(targetEl, done) {
    if (!targetEl) {
      if (done) done();
      return;
    }
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      targetEl.scrollIntoView({ behavior: "auto", block: "start" });
      if (done) done();
      return;
    }
    var OFFSET = 76;
    var start = __getScrollY();
    var end;
    var port = __getScrollPort();
    if (port === __appM && __appM) {
      var re = __appM.getBoundingClientRect();
      var te = targetEl.getBoundingClientRect();
      end = start + (te.top - re.top) - OFFSET;
    } else {
      var rect = targetEl.getBoundingClientRect();
      end = rect.top + start - OFFSET;
    }
    var dist = end - start;
    if (Math.abs(dist) < 3) {
      if (done) done();
      return;
    }
    var dur = Math.min(1550, Math.max(480, Math.pow(Math.abs(dist), 0.72) * 1.35));
    var t0 = performance.now();
    function easeOutQuint(t) {
      return 1 - Math.pow(1 - t, 5);
    }
    function step(now) {
      var t = Math.min(1, (now - t0) / dur);
      var p = easeOutQuint(t);
      __setScrollTopInstant(start + dist * p);
      if (t < 1) requestAnimationFrame(step);
      else if (done) done();
    }
    requestAnimationFrame(step);
  }

  window.scrollToElementHighSpeedDecel = scrollToElementHighSpeedDecel;

  function pulseDetailsEl(el) {
    if (!el) return;
    var ok = el.classList.contains("day") || el.classList.contains("city-block");
    if (!ok) return;
    el.classList.remove("target-pulse");
    void el.offsetWidth;
    el.classList.add("target-pulse");
    if (el.classList.contains("day") || el.classList.contains("city-block")) el.open = true;
    setTimeout(function () {
      el.classList.remove("target-pulse");
    }, 1400);
  }

  labelDataTables();
  window.refreshLucide();

  document.addEventListener(
    "click",
    function (ev) {
      if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) return;
      var a = ev.target.closest('a[href^="#day-"]');
      if (!a) return;
      var id = (a.getAttribute("href") || "").replace(/^#/, "");
      if (!id) return;
      var day = document.getElementById(id);
      if (!day || !day.classList.contains("day")) return;
      ev.preventDefault();
      day.open = true;
      try {
        if (history.pushState) history.pushState(null, "", "#" + id);
        else location.hash = "#" + id;
      } catch (eHash) {
        location.hash = "#" + id;
      }
      if (typeof window.roteiroApplyAppTab === "function") {
        window.roteiroApplyAppTab("roteiro", { skipStore: false, hash: false, scrollTop: false });
      }
      scrollToElementHighSpeedDecel(day, function () {
        pulseDetailsEl(day);
      });
    },
    true
  );

  (function initMapCityPanel() {
    var MAP_CITIES = {
      muc: {
        title: "Munique",
        code: "MUC",
        dates: "19–22 nov · 3 noites",
        hotel: "B&B Hotel München-Hbf",
        station: "München Hbf; ZOB para FlixBus (Füssen / Salzburgo)",
        poi: [
          "Centro: Marienplatz, Viktualienmarkt, Englischer Garten",
          "21 nov: Neuschwanstein (FlixBus ZOB 08:30–19:25 ou RE+Füssen)",
          "Seg.: FlixBus para Salzburgo (22 nov ~13:45 do ZOB)",
        ],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=B%26B%20Hotel%20M%C3%BCnchen-Hbf%20Arnulfstra%C3%9Fe%2030%20M%C3%BCnchen",
        copyAddr: "B&B Hotel München-Hbf, Arnulfstraße 30, 80335 München, Germany",
        anchor: "#city-muc",
      },
      szg: {
        title: "Salzburgo",
        code: "SZG",
        dates: "22–24 nov · 2 noites",
        hotel: "Atel Hotel Lasserhof",
        station: "Salzburg Hbf",
        poi: [
          "Altstadt, Festung Hohensalzburg, rio Salzach",
          "Chegada típica FlixBus P+R Süd (~15:45) no 22 nov",
          "Seg.: ÖBB ICE 10:00 → Wien Hbf (24 nov)",
        ],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=Atel%20Hotel%20Lasserhof%20Lasserstra%C3%9Fe%2047%20Salzburg",
        copyAddr: "Atel Hotel Lasserhof, Lasserstraße 47, 5020 Salzburg, Austria",
        anchor: "#city-szg",
      },
      vie: {
        title: "Viena",
        code: "VIE",
        dates: "24–26 nov · 2 noites",
        hotel: "Hotel Zipser (Josefstadt, perto Rathaus / U2)",
        station: "Wien Hbf",
        poi: [
          "Prater, Naschmarkt, Donaukanal; Schönbrunn (jardins), Stephansdom (exterior), Ring",
          "Seg.: FlixBus VIB ~12:35 → Bratislava Most SNP (26 nov)",
        ],
        mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hotel%20Zipser%20Lange%20Gasse%2049%20Wien",
        copyAddr: "Hotel Zipser, Lange Gasse 49, 1080 Wien, Austria",
        anchor: "#city-vie",
      },
      bts: {
        title: "Bratislava",
        code: "BTS",
        dates: "26–27 nov · 1 noite",
        hotel: "Danubia Gate Hotel",
        station: "Most SNP (FlixBus Omio) ou hl.st. — confira o bilhete",
        poi: ["Castelo, Staré Mesto", "Seg.: FlixBus Mlynské Nivy ~10:50 → Budapeste Kelenföld (27 nov)"],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=Danubia%20Gate%20Hotel%20Dunajsk%C3%A1%2026%20Bratislava",
        copyAddr: "Danubia Gate Hotel, Dunajská 26, 811 01 Bratislava, Slovakia",
        anchor: "#city-bts",
      },
      bud: {
        title: "Budapeste",
        code: "BUD",
        dates: "27–30 nov · 3 noites",
        hotel: "Medos Hotel",
        station: "Chegada típica Kelenföld (FlixBus); voo 30 nov 15:40 BUD → BER",
        poi: [
          "Parlamento, margens, basílica, Ponte das Correntes, Buda ao pôr do sol",
          "Dia do voo: folga para centro → BUD (ex. 100E)",
        ],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=Medos%20Hotel%20R%C3%A1k%C3%B3czi%20%C3%BAt%2040%20Budapest",
        copyAddr: "Medos Hotel, Rákóczi út 40, 1072 Budapest, Hungary",
        anchor: "#city-bud",
      },
      ber: {
        title: "Berlim",
        code: "BER",
        dates: "30 nov–3 dez · 3 noites",
        hotel: "Premier Inn Berlin Alexanderplatz",
        station: "Chegada voo BER 30 nov; saída FlixBus Südkreuz ~10:20 (3 dez) ou EC do Hbf",
        poi: [
          "Brandenburg, Memorial, Unter den Linden, East Side Gallery, Mitte",
          "Noite de chegada: REWE / bairro da estação",
        ],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=Premier%20Inn%20Berlin%20Alexanderplatz%20Otto-Braun-Stra%C3%9Fe%2069",
        copyAddr: "Premier Inn Berlin Alexanderplatz, Otto-Braun-Straße 69, 10178 Berlin, Germany",
        anchor: "#city-ber",
      },
      prg: {
        title: "Praga",
        code: "PRG",
        dates: "3–5 dez · 2 noites",
        hotel: "Alton (Legerova · metro I.P. Pavlova)",
        station: "ÚAN Florenc (FlixBus) ou hl.n. (EC); PRG só para voo",
        poi: [
          "Staroměstské náměstí, Karlův most, castelo (vistas), Malá Strana",
          "Seg.: voo PRG → CRL (5 dez 12:30) Ryanair FR 69; Flibco → Midi",
        ],
        mapsUrl: "https://www.google.com/maps/search/?api=1&query=Alton%20Hotel%20Legerova%2022%20Praha",
        copyAddr: "Alton Hotel, Legerova 1581/22, 120 00 Praha 2, Czechia",
        anchor: "#city-prg",
      },
      bru: {
        title: "Bruxelas",
        code: "BRU",
        dates: "5–7 dez · 2 noites",
        hotel: "Hotel des Colonies Brussels by Mercure (Rogier)",
        station: "Rogier / Bruxelles-Nord; chegada 5 dez via CRL (Flibco → Midi); voo 7 dez BRU",
        poi: [
          "Grand Place (5 dez); 6 dez descanso + prep voo em Bruxelas",
          "Seg.: voo BRU → Brasil (7 dez)",
        ],
        mapsUrl:
          "https://www.google.com/maps/search/?api=1&query=Hotel%20des%20Colonies%20Brussels%20Rue%20des%20Croisades%206",
        copyAddr: "Hotel des Colonies Brussels by Mercure, Rue des Croisades 6, 1210 Saint-Josse-ten-Noode, Belgium",
        anchor: "#city-bru",
      },
    };

    var panel = document.getElementById("mapCityPanel");
    var hint = document.getElementById("mapCityPanelHint");
    var body = document.getElementById("mapCityPanelBody");
    var titleEl = document.getElementById("mapCityPanelTitle");
    var codeEl = document.getElementById("mapCityPanelCode");
    var datesEl = document.getElementById("mapCityPanelDates");
    var hotelEl = document.getElementById("mapCityPanelHotel");
    var stationEl = document.getElementById("mapCityPanelStation");
    var poiUl = document.getElementById("mapCityPanelPoi");
    var mapsA = document.getElementById("mapCityPanelMaps");
    var copyBtn = document.getElementById("mapCityPanelCopy");
    var fichaA = document.getElementById("mapCityPanelFicha");
    if (!panel || !hint || !body || !titleEl || !poiUl || !mapsA || !copyBtn || !fichaA) return;

    function scrollPanelIntoView() {
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      try {
        panel.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" });
      } catch (e) {
        panel.scrollIntoView();
      }
    }

    function selectMapCity(key) {
      var d = MAP_CITIES[key];
      if (!d) return;
      document.querySelectorAll(".map-node.is-selected").forEach(function (g) {
        g.classList.remove("is-selected");
      });
      var node = document.querySelector('.map-node[data-city="' + key + '"]');
      if (node) node.classList.add("is-selected");
      panel.classList.add("has-selection");
      hint.hidden = true;
      body.hidden = false;
      titleEl.textContent = d.title;
      codeEl.textContent = d.code;
      datesEl.textContent = d.dates;
      hotelEl.textContent = d.hotel;
      stationEl.textContent = d.station;
      poiUl.innerHTML = "";
      d.poi.forEach(function (t) {
        var li = document.createElement("li");
        li.textContent = t;
        poiUl.appendChild(li);
      });
      mapsA.href = d.mapsUrl;
      copyBtn.setAttribute("data-copy", d.copyAddr);
      copyBtn.textContent = copyBtn.getAttribute("data-label") || "Copiar morada";
      copyBtn.classList.remove("is-done");
      fichaA.href = "#hoteis";
    }

    document.querySelectorAll(".map-node").forEach(function (g) {
      var key = g.getAttribute("data-city");
      if (!key || !MAP_CITIES[key]) return;
      function activate() {
        selectMapCity(key);
        scrollPanelIntoView();
      }
      g.addEventListener("click", activate);
      g.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          activate();
        }
      });
    });
  })();

  var LS_OPEN = "roteiro-open-state-v1";
  var days = document.querySelectorAll("details.day");
  var cities = document.querySelectorAll("details.city-block");
  var allDetails = document.querySelectorAll("details.day, details.city-block");

  function persistOpens() {
    var o = {};
    allDetails.forEach(function (el) {
      if (el.id) o[el.id] = !!el.open;
    });
    try {
      localStorage.setItem(LS_OPEN, JSON.stringify(o));
    } catch (e) {
      showStorageWarning();
    }
  }

  try {
    var saved = JSON.parse(localStorage.getItem(LS_OPEN) || "{}");
    if (saved && typeof saved === "object") {
      allDetails.forEach(function (el) {
        if (el.id && Object.prototype.hasOwnProperty.call(saved, el.id)) {
          el.open = !!saved[el.id];
        }
      });
    }
  } catch (e2) {}

  days.forEach(function (d) {
    d.addEventListener("toggle", persistOpens);
  });
  cities.forEach(function (c) {
    c.addEventListener("toggle", persistOpens);
  });

  function pad2(n) {
    return n < 10 ? "0" + n : String(n);
  }

  var now = new Date();
  var todayIso = now.getFullYear() + "-" + pad2(now.getMonth() + 1) + "-" + pad2(now.getDate());
  document.querySelectorAll("details.day[data-trip-date]").forEach(function (d) {
    if (d.getAttribute("data-trip-date") !== todayIso) return;
    d.classList.add("is-trip-today");
    var summ = d.querySelector("summary");
    if (summ && !summ.querySelector(".badge-hoje")) {
      var b = document.createElement("span");
      b.className = "badge-hoje";
      b.textContent = "Hoje";
      summ.appendChild(b);
    }
  });

  var searchEl = document.getElementById("tripSearch");
  var searchTimer = null;

  function clearSearchClasses() {
    document.body.classList.remove("has-trip-search");
    document.querySelectorAll(".search-miss").forEach(function (el) {
      el.classList.remove("search-miss");
    });
  }

  function runSearch() {
    var q = (searchEl.value || "").trim().toLowerCase();
    document.querySelectorAll(".search-miss").forEach(function (el) {
      el.classList.remove("search-miss");
    });
    if (!q) {
      clearSearchClasses();
      return;
    }
    document.body.classList.add("has-trip-search");
    document.querySelectorAll("details.day").forEach(function (d) {
      if (!d.textContent.toLowerCase().includes(q)) d.classList.add("search-miss");
    });
    document.querySelectorAll("section.block").forEach(function (sec) {
      if (sec.id === "dias") {
        var anyDay = false;
        sec.querySelectorAll("details.day").forEach(function (d) {
          if (!d.classList.contains("search-miss")) anyDay = true;
        });
        var h2 = sec.querySelector("h2");
        var lede = sec.querySelector(".lede");
        var headMatch =
          (h2 && h2.textContent.toLowerCase().includes(q)) ||
          (lede && lede.textContent.toLowerCase().includes(q));
        if (!anyDay && !headMatch) sec.classList.add("search-miss");
      } else if (!sec.textContent.toLowerCase().includes(q)) {
        sec.classList.add("search-miss");
      }
    });
    document.querySelectorAll("nav.toc li").forEach(function (li) {
      var a = li.querySelector('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute("href").slice(1);
      var t = document.getElementById(id);
      if (t && t.classList.contains("search-miss")) li.classList.add("search-miss");
    });
  }

  if (searchEl) {
    searchEl.addEventListener("input", function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(runSearch, 140);
    });
    searchEl.addEventListener("search", function () {
      if (!searchEl.value) clearSearchClasses();
    });
  }

  document.body.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".btn-copy");
    if (!btn) return;
    var text = btn.getAttribute("data-copy");
    if (!text) return;
    var label = btn.getAttribute("data-label") || "Copiar morada";
    function revert() {
      btn.classList.remove("is-done");
      btn.textContent = label;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        btn.classList.add("is-done");
        btn.textContent = "Copiado!";
        setTimeout(revert, 2200);
      });
    }
  });

  var root = document.documentElement;
  var themeKey = "roteiro-theme-v1";
  var themeStored = null;
  try {
    themeStored = localStorage.getItem(themeKey);
  } catch (e0) {}
  if (themeStored === "dark") root.setAttribute("data-theme", "dark");

  var themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark";
      if (dark) {
        root.removeAttribute("data-theme");
        try {
          localStorage.setItem(themeKey, "light");
        } catch (e) {}
      } else {
        root.setAttribute("data-theme", "dark");
        try {
          localStorage.setItem(themeKey, "dark");
        } catch (e) {}
      }
      window.refreshLucide();
    });
  }

  var scrollProgressEl = document.getElementById("scrollProgress");
  function updateScrollProgress() {
    if (!scrollProgressEl) return;
    var p = __getScrollPort();
    if (!p) return;
    var sh = p.scrollHeight - p.clientHeight;
    var st = p === __appM ? p.scrollTop : window.scrollY || document.documentElement.scrollTop;
    var pct = sh <= 0 ? 0 : Math.min(100, Math.max(0, (st / sh) * 100));
    scrollProgressEl.style.width = pct + "%";
    scrollProgressEl.setAttribute("aria-valuenow", String(Math.round(pct)));
  }

  var fab = document.getElementById("fabTop");
  var onScroll = function () {
    if (fab) fab.classList.toggle("is-visible", __getScrollY() > 420);
    updateScrollProgress();
  };
  if (__appM) __appM.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", updateScrollProgress, { passive: true });
  onScroll();

  if (fab) {
    fab.addEventListener("click", function () {
      var b = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
      var port = __getScrollPort();
      if (port === __appM && __appM) {
        __appM.scrollTo({ top: 0, behavior: b });
      } else {
        window.scrollTo({ top: 0, behavior: b });
      }
    });
  }

  document.querySelectorAll("details.day, details.city-block, section.block").forEach(function (el) {
    el.classList.add("reveal");
  });
  var revealEls = document.querySelectorAll(".reveal");
  revealEls.forEach(function (el, i) {
    el.style.setProperty("--reveal-stagger", Math.min(i, 48) * 28 + "ms");
  });
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) {
    revealEls.forEach(function (el) {
      el.classList.add("is-visible", "reveal-motion-done");
    });
  } else {
    var revealRoot = null;
    var appMainEl = document.getElementById("appMain");
    if (appMainEl) {
      var oy = getComputedStyle(appMainEl).overflowY;
      if (oy === "auto" || oy === "scroll" || oy === "overlay") {
        revealRoot = appMainEl;
      }
    }
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var el = e.target;
          obs.unobserve(el);
          el.classList.add("is-visible");
          var delay = parseRevealStaggerMs(el);
          setTimeout(function () {
            runSpringReveal(el);
          }, delay);
        });
      },
      { threshold: 0.06, rootMargin: "100px 0px -28px 0px", root: revealRoot }
    );
    revealEls.forEach(function (el) {
      obs.observe(el);
    });
    document.addEventListener("roteiro:panels-shown", function () {
      if (typeof window.roteiroNudgeRevealIn === "function") {
        document.querySelectorAll("[data-app-panel]:not([hidden])").forEach(function (p) {
          window.roteiroNudgeRevealIn(p);
        });
      }
    });
  }

  (function initHojeDestaque() {
    var box = document.getElementById("hojeDestaque");
    var line = document.getElementById("hojeDestaqueLine");
    var btn = document.getElementById("hojeDestaqueBtn");
    if (!box || !line || !btn) return;
    var day = document.querySelector('details.day[data-trip-date="' + todayIso + '"]');
    if (!day) return;
    box.removeAttribute("hidden");
    var city = day.querySelector(".city");
    var label = city ? city.textContent.replace(/\s+/g, " ").trim() : "Dia de hoje";
    line.textContent = label;
    btn.addEventListener("click", function () {
      if (typeof window.roteiroApplyAppTab === "function") {
        window.roteiroApplyAppTab("roteiro", { skipStore: false, hash: true, scrollTop: false });
      }
      day.open = true;
      scrollToElementHighSpeedDecel(day);
    });
  })();
})();
