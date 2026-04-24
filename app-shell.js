/**
 * Shell tipo app (tabs, painéis, hash). Depende de body.has-app-ui e [data-app-panel].
 * Pesquisa: MutationObserver em body.classList (has-trip-search) para mostrar todos os painéis.
 */
(function () {
  "use strict";

  var TABS = { inicio: 1, roteiro: 1, mapa: 1, mais: 1 };
  var KEY = "roteiro-app-tab-v1";
  var _tab = "inicio";
  var _searchPeek = false;

  function scrollAppToTop() {
    var m = document.getElementById("appMain");
    if (m) m.scrollTo(0, 0);
    else {
      try {
        window.scrollTo(0, 0);
      } catch (e) {}
    }
  }

  function getPanels() {
    return document.querySelectorAll("[data-app-panel]");
  }

  function whichTabForSectionId(id) {
    if (!id) return null;
    if (id === "resumo" || id === "inicio-hero" || id === "indice-toc") return "inicio";
    if (id === "dias" || id === "indice-dias" || id.indexOf("day-") === 0) return "roteiro";
    if (id === "mapa" || id === "cidades" || (id && id.indexOf("city-") === 0)) return "mapa";
    if (id === "cambio" || id === "mais-hub") return "mais";
    if (
      id === "horarios-bilhetes" ||
      id === "voos" ||
      id === "hoteis" ||
      id === "emergencia" ||
      id === "compras" ||
      id === "checklist" ||
      (id && id.indexOf("compras-") === 0)
    )
      return "mais";
    return null;
  }

  function nudgeRevealIn(root) {
    if (!root) return;
    if (root.querySelectorAll) {
      root.querySelectorAll(".reveal:not(.is-visible)").forEach(function (el) {
        el.classList.add("is-visible", "reveal-motion-done");
      });
    }
  }

  function showPanelsForTab(t) {
    getPanels().forEach(function (p) {
      var show = p.getAttribute("data-app-panel") === t;
      if (show) {
        p.removeAttribute("hidden");
        p.setAttribute("aria-hidden", "false");
        nudgeRevealIn(p);
      } else {
        p.setAttribute("hidden", "");
        p.setAttribute("aria-hidden", "true");
      }
    });
  }

  function setTabUI(t) {
    document.querySelectorAll(".app-tab").forEach(function (btn) {
      var on = btn.getAttribute("data-app-tab") === t;
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  window.roteiroApplyAppTab = function (t, opts) {
    opts = opts || {};
    if (!TABS.hasOwnProperty(t)) t = "inicio";
    if (_searchPeek) return;
    _tab = t;
    document.body.setAttribute("data-app-tab", t);
    setTabUI(t);
    if (!opts.skipStore) {
      try {
        localStorage.setItem(KEY, t);
      } catch (e) {}
    }
    showPanelsForTab(t);
    if (opts.hash !== false) {
      try {
        history.replaceState(null, "", "#!" + t);
      } catch (e) {
        try {
          location.replace("#!" + t);
        } catch (e2) {}
      }
    }
    if (opts.scrollTop) {
      scrollAppToTop();
    }
  };

  function onSearchPeek(on) {
    if (on) {
      if (_searchPeek) return;
      _searchPeek = true;
      document.body.classList.add("app-search-peek");
      getPanels().forEach(function (p) {
        p.removeAttribute("hidden");
        p.setAttribute("aria-hidden", "false");
      });
    } else {
      if (!_searchPeek) return;
      _searchPeek = false;
      document.body.classList.remove("app-search-peek");
      showPanelsForTab(_tab);
      setTabUI(_tab);
    }
  }

  window.roteiroSearchMode = onSearchPeek;

  function tryPulse(id) {
    if (!id || id.indexOf("!") === 0) return;
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.remove("target-pulse");
    void el.offsetWidth;
    el.classList.add("target-pulse");
    if (el.classList && (el.classList.contains("day") || el.classList.contains("city-block"))) {
      el.open = true;
    }
    if (el.scrollIntoView) {
      el.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "start"
      });
    }
    setTimeout(function () {
      el.classList.remove("target-pulse");
    }, 1400);
  }

  function clearAppSearch() {
    document.body.classList.remove("has-trip-search");
    document.querySelectorAll(".search-miss").forEach(function (el) {
      el.classList.remove("search-miss");
    });
    var se = document.getElementById("tripSearch");
    if (se) se.value = "";
    onSearchPeek(false);
  }

  function routeFromHash() {
    var h = (location.hash || "").replace(/^#/, "");
    if (h.indexOf("!") === 0) {
      var t = h.slice(1);
      if (TABS.hasOwnProperty(t)) {
        if (!_searchPeek) {
          clearAppSearch();
          _tab = t;
          document.body.setAttribute("data-app-tab", t);
          setTabUI(t);
          showPanelsForTab(t);
        }
        if (!_searchPeek) {
          scrollAppToTop();
        }
        return;
      }
    }
    if (h && h.indexOf("!") !== 0) {
      var tab = whichTabForSectionId(h);
      if (tab) {
        _tab = tab;
        document.body.setAttribute("data-app-tab", tab);
        setTabUI(tab);
        if (!_searchPeek) {
          showPanelsForTab(tab);
        }
        setTimeout(function () {
          tryPulse(h);
        }, 40);
        return;
      }
    }
    if (!_searchPeek) {
      showPanelsForTab(_tab);
    }
  }

  function readStoredTab() {
    try {
      var s = localStorage.getItem(KEY);
      if (s === "financas") {
        try {
          localStorage.setItem(KEY, "mais");
        } catch (e2) {}
        return "mais";
      }
      if (s && TABS.hasOwnProperty(s)) return s;
    } catch (e) {}
    return "inicio";
  }

  if (!document.body.classList.contains("has-app-ui")) return;

  document.querySelectorAll(".app-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var t = btn.getAttribute("data-app-tab");
      if (!t) return;
      onSearchPeek(false);
      if (document.body.classList.contains("has-trip-search")) {
        document.body.classList.remove("has-trip-search");
        document.querySelectorAll(".search-miss").forEach(function (el) {
          el.classList.remove("search-miss");
        });
        var se = document.getElementById("tripSearch");
        if (se) se.value = "";
      }
      window.roteiroApplyAppTab(t, { skipStore: false, hash: true, scrollTop: true });
    });
  });

  var mSearch = new MutationObserver(function () {
    var on = document.body.classList.contains("has-trip-search");
    var se = document.getElementById("tripSearch");
    var q = se && (se.value || "").trim();
    if (on && q) {
      onSearchPeek(true);
    } else {
      onSearchPeek(false);
    }
  });
  mSearch.observe(document.body, { attributes: true, attributeFilter: ["class"] });

  var h0 = (location.hash || "").replace(/^#/, "");
  if (h0.indexOf("!") === 0) {
    var tn = h0.slice(1);
    if (TABS.hasOwnProperty(tn)) {
      _tab = tn;
    } else {
      _tab = readStoredTab();
    }
  } else if (h0) {
    var t2 = whichTabForSectionId(h0);
    if (t2) _tab = t2;
    else _tab = readStoredTab();
  } else {
    _tab = readStoredTab();
  }

  document.body.setAttribute("data-app-tab", _tab);
  setTabUI(_tab);
  if (document.body.classList.contains("has-trip-search") && (document.getElementById("tripSearch") && document.getElementById("tripSearch").value || "").trim()) {
    onSearchPeek(true);
  } else {
    showPanelsForTab(_tab);
  }

  if (!location.hash) {
    try {
      history.replaceState(null, "", "#!" + _tab);
    } catch (e) {
      location.hash = "#!" + _tab;
    }
  }

  window.addEventListener("hashchange", function () {
    /* Durante peek de pesquisa (correspondências em toda a página) não trocar tab pelo hash, para não "perder" o contexto. Com input vazio, routeFromHash corre sempre. */
    if (document.body.classList.contains("app-search-peek") && (document.getElementById("tripSearch") && (document.getElementById("tripSearch").value || "").trim()) ) {
      return;
    }
    routeFromHash();
  });
  if (h0) {
    setTimeout(function () {
      routeFromHash();
    }, 0);
  }

  function refreshTabIcons() {
    try {
      if (typeof lucide !== "undefined" && lucide.createIcons) {
        lucide.createIcons({ attrs: { "stroke-width": 1.75 } });
      }
    } catch (e) {}
  }
  refreshTabIcons();
})();
