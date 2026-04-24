/**
 * Roteiro: lista de dias → detalhe (um ecrã) + integração com hash #day-…
 */
(function () {
  "use strict";

  var section = document.getElementById("dias");
  if (!section) return;

  var days = section.querySelectorAll("details.day");
  if (!days.length) return;

  var backBar = document.getElementById("appDiaBackBar");
  var backBtn = document.getElementById("appDiaVoltar");
  var bread = document.getElementById("appDiaBreadcrumb");
  var listHost = document.getElementById("appDiaListHost");

  function getHashId() {
    return (location.hash || "").replace(/^#/, "");
  }

  function isDayHash(id) {
    return id && id.indexOf("day-20") === 0;
  }

  function setMode(detail) {
    if (detail) {
      section.classList.remove("app-roteiro--lista");
      section.classList.add("app-roteiro--detalhe");
    } else {
      section.classList.add("app-roteiro--lista");
      section.classList.remove("app-roteiro--detalhe");
    }
  }

  function showDayById(id) {
    if (!isDayHash(id)) return;
    setMode(true);
    var target = null;
    days.forEach(function (d) {
      if (d.id === id) {
        d.classList.remove("app-dia--hidden");
        d.removeAttribute("hidden");
        d.open = true;
        target = d;
        try {
          d.scrollIntoView({ block: "start", behavior: "auto" });
        } catch (e) {}
      } else {
        d.classList.add("app-dia--hidden");
        d.open = false;
      }
    });
    if (backBar) backBar.hidden = false;
    if (bread) {
      var summ = target && target.querySelector("summary .city");
      bread.textContent = summ ? summ.textContent.replace(/\s+/g, " ").trim() : "Dia";
    }
  }

  function showList() {
    setMode(false);
    days.forEach(function (d) {
      d.classList.remove("app-dia--hidden");
      d.removeAttribute("hidden");
    });
    if (backBar) backBar.hidden = true;
    if (bread) bread.textContent = "";
  }

  function buildList() {
    if (!listHost) return;
    if (listHost.querySelector("ul.app-dia-list")) return;
    var ul = document.createElement("ul");
    ul.className = "app-dia-list";
    ul.setAttribute("role", "list");
    days.forEach(function (d) {
      if (!d.id) return;
      var sum = d.querySelector("summary");
      if (!sum) return;
      var tag = d.querySelector(".date-tag");
      var city = d.querySelector(".city");
      var li = document.createElement("li");
      li.setAttribute("role", "listitem");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "app-dia-row";
      btn.setAttribute("data-dia-id", d.id);
      btn.setAttribute("aria-label", (tag ? tag.textContent : "") + " " + (city ? city.textContent : ""));
      var dspan = document.createElement("span");
      dspan.className = "app-dia-row__date";
      dspan.textContent = tag ? tag.textContent.replace(/·.*/g, "").trim() : "";
      var mid = document.createElement("div");
      mid.className = "app-dia-row__mid";
      var t = document.createElement("div");
      t.className = "app-dia-row__title";
      t.textContent = city ? city.textContent.replace(/\s+/g, " ").trim() : sum.textContent.slice(0, 80);
      mid.appendChild(t);
      btn.appendChild(dspan);
      btn.appendChild(mid);
      btn.addEventListener("click", function () {
        try {
          history.pushState(null, "", "#" + d.id);
        } catch (e) {
          location.hash = "#" + d.id;
        }
        showDayById(d.id);
        if (window.roteiroApplyAppTab) {
          window.roteiroApplyAppTab("roteiro", { skipStore: false, hash: false, scrollTop: false });
        }
        var main = document.getElementById("appMain");
        if (main) main.scrollTo(0, 0);
        else window.scrollTo(0, 0);
      });
      li.appendChild(btn);
      ul.appendChild(li);
    });
    listHost.appendChild(ul);
    section.classList.add("app-has-dia-list");
  }

  function applyFromHash() {
    var h = getHashId();
    if (h.indexOf("!") === 0) {
      if (h === "!roteiro" || h.indexOf("!roteiro") === 0) {
        showList();
        return;
      }
    }
    if (isDayHash(h)) {
      showDayById(h);
      return;
    }
    if (section.classList.contains("app-roteiro--detalhe") && getHashId().indexOf("!") === 0) {
      return;
    }
  }

  if (backBtn) {
    backBtn.addEventListener("click", function () {
      showList();
      try {
        history.pushState(null, "", "#!roteiro");
      } catch (e) {
        location.hash = "#!roteiro";
      }
      if (window.roteiroApplyAppTab) {
        window.roteiroApplyAppTab("roteiro", { skipStore: false, hash: false, scrollTop: true });
      }
    });
  }

  buildList();
  section.classList.add("app-roteiro--lista");
  var h0 = getHashId();
  if (isDayHash(h0)) {
    showDayById(h0);
  } else {
    showList();
  }

  window.addEventListener("hashchange", function () {
    applyFromHash();
  });
})();
