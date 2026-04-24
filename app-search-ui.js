/**
 * Abre o diálogo de pesquisa in-app: foco, fechar, clique fora, ícones.
 */
(function () {
  "use strict";

  var dlg = document.getElementById("tripSearchDialog");
  var openBtn = document.getElementById("tripSearchOpen");
  if (!dlg || !openBtn) return;

  function refreshLucide() {
    try {
      if (typeof lucide !== "undefined" && lucide.createIcons) {
        lucide.createIcons({ attrs: { "stroke-width": 1.75 } });
      }
    } catch (e) {}
  }

  openBtn.addEventListener("click", function () {
    if (typeof dlg.showModal === "function") {
      dlg.showModal();
    } else {
      dlg.setAttribute("open", "open");
    }
    var input = document.getElementById("tripSearch");
    if (input) {
      setTimeout(function () {
        try {
          input.focus();
        } catch (e1) {}
        try {
          if (input.select) input.select();
        } catch (e2) {}
      }, 0);
    }
    openBtn.setAttribute("aria-expanded", "true");
    refreshLucide();
  });

  dlg.addEventListener("close", function () {
    openBtn.setAttribute("aria-expanded", "false");
    var input = document.getElementById("tripSearch");
    if (input) {
      input.value = "";
    }
    document.body.classList.remove("has-trip-search");
    document.querySelectorAll(".search-miss").forEach(function (el) {
      el.classList.remove("search-miss");
    });
    if (typeof window.roteiroSearchMode === "function") {
      window.roteiroSearchMode(false);
    }
    try {
      openBtn.focus();
    } catch (e) {}
  });

  dlg.addEventListener("click", function (ev) {
    if (ev.target === dlg) {
      dlg.close();
    }
  });

  dlg.addEventListener("cancel", function (ev) {
    ev.preventDefault();
    dlg.close();
  });
})();
