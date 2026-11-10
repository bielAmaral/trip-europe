/**
 * Horário híbrido: macro (fast-plan-table) + expandir com subblocos (walk-route + window-details.json).
 *
 * Tempos repartidos uniformemente nas paradas do tour e nos blocos de janela — estimativa, não GPS.
 */
(function () {
  "use strict";

  var TOUR_ROW_RE = /Rota a pé|Passo a passo no mapa|Tour\s+/i;
  var VAGUE_RE =
    /abrir\s+<strong>Passo a passo|trecho curto\)\s*·\s*volta|jantar\s*<\/td>|jantar rápido\s*·|jantar leve\s*·\s*$|buffer\s*\/|Manhã livre/i;

  var windowDetails = { version: 0, days: {} };
  var detailsReady = false;

  function parseTimeToMin(h, m) {
    return parseInt(h, 10) * 60 + parseInt(m, 10);
  }

  function formatHm(totalMin) {
    var t = ((totalMin % (24 * 60)) + 24 * 60) % (24 * 60);
    var hh = Math.floor(t / 60);
    var mm = t % 60;
    return (hh < 10 ? "0" : "") + hh + ":" + (mm < 10 ? "0" : "") + mm;
  }

  function parseWhenWindow(whenText) {
    var raw = (whenText || "").trim();
    var m = raw.match(/^(\d{1,2}):(\d{2})(?:\s*[–\-—]\s*(\d{1,2}):(\d{2}))?/);
    if (!m) return null;
    var startMin = parseTimeToMin(m[1], m[2]);
    var endMin = m[3] ? parseTimeToMin(m[3], m[4]) : startMin;
    var duration = endMin - startMin;
    if (duration <= 0) duration = 0;
    return { startMin: startMin, endMin: endMin, duration: duration, label: raw };
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function stopFromLi(li) {
    var strong = li.querySelector("strong");
    var title = strong ? strong.textContent.trim() : "";
    if (!title) {
      title = li.textContent.trim().split(/[—–-]/)[0].trim().slice(0, 60);
    }
    var full = li.textContent.trim();
    var tip = full;
    if (title && full.indexOf(title) === 0) {
      tip = full.slice(title.length).replace(/^[\s(—–-]+/, "").trim();
    }
    return { title: title, tip: tip };
  }

  function isTourRow(tr) {
    var cell = tr.querySelector("td:last-child");
    if (!cell) return false;
    var text = cell.textContent.trim();
    return (
      /^Tour\s+(?:<em>|<strong>)/i.test(cell.innerHTML) ||
      /^(?:Rota a pé|Passo a passo no mapa)/i.test(text)
    );
  }

  function windowSpecForRow(dayId, whenText) {
    var day = windowDetails.days[dayId];
    if (!day || !day.windows) return null;
    return day.windows[whenText && whenText.trim()] || null;
  }

  function rowNeedsExpand(tr, dayId, whenText) {
    if (isTourRow(tr)) return true;
    if (windowSpecForRow(dayId, whenText)) return true;
    var cell = tr.querySelector("td:last-child");
    if (!cell) return false;
    var txt = cell.textContent + " " + cell.innerHTML;
    return VAGUE_RE.test(txt);
  }

  function appendAnchorRow(tbody, whenCell, macroHtml, label) {
    var anchor = document.createElement("tr");
    anchor.className = "fast-plan-expand__anchor";
    anchor.innerHTML =
      '<td class="fast-plan__when">' +
      escapeHtml(whenCell ? whenCell.textContent.trim() : "—") +
      '</td><td><em class="fast-plan-expand__anchor-label">' +
      escapeHtml(label || "Janela") +
      "</em> · " +
      macroHtml +
      "</td>";
    tbody.appendChild(anchor);
  }

  function appendStopRow(tbody, atMin, offset, title, tipHtml, extraClass) {
    var tr = document.createElement("tr");
    tr.className = "fast-plan-expand__stop" + (extraClass ? " " + extraClass : "");
    tr.innerHTML =
      '<td class="fast-plan__when">' +
      escapeHtml(formatHm(atMin)) +
      '<span class="fast-plan-expand__offset">+' +
      offset +
      " min</span></td><td>" +
      title +
      (tipHtml || "") +
      "</td>";
    tbody.appendChild(tr);
  }

  function renderWalkStops(tbody, stops, window_) {
    var startMin = window_ ? window_.startMin : 10 * 60;
    var duration =
      window_ && window_.duration > 0
        ? window_.duration
        : Math.max(45, stops.length * 12);
    var step = stops.length > 1 ? Math.floor(duration / (stops.length - 1)) : 0;

    for (var i = 0; i < stops.length; i++) {
      var s = stopFromLi(stops[i]);
      var offset = i * step;
      var atMin = startMin + offset;
      var tipHtml = s.tip
        ? ' <span class="fast-plan-expand__tip">' + escapeHtml(s.tip) + "</span>"
        : "";
      appendStopRow(
        tbody,
        atMin,
        offset,
        "<strong>" + escapeHtml(s.title) + "</strong>",
        tipHtml,
        ""
      );
    }
  }

  function renderWindowBlocks(tbody, spec, window_) {
    var blocks = (spec && spec.blocks) || [];
    if (!blocks.length) return;
    var startMin = window_ ? window_.startMin : 9 * 60;
    var cursor = 0;
    for (var i = 0; i < blocks.length; i++) {
      var b = blocks[i];
      var dur = b.durMin || 15;
      var atMin = startMin + cursor;
      var est =
        b.estimate || b.kind === "transit"
          ? ' <span class="fast-plan-expand__tip">(estimativa)</span>'
          : "";
      var cut =
        b.cutFirst || b.kind === "optional"
          ? ' <span class="fast-plan-expand__tag fast-plan-expand__tag--cut">cortar primeiro</span>'
          : "";
      var kindClass = b.kind ? " fast-plan-expand__stop--" + b.kind : "";
      appendStopRow(
        tbody,
        atMin,
        cursor,
        "<span class='fast-plan-expand__block-html'>" + b.html + "</span>" + est + cut,
        "",
        kindClass.trim()
      );
      cursor += dur;
    }
    if (spec.cutFirst) {
      var foot = document.createElement("tr");
      foot.className = "fast-plan-expand__meta";
      foot.innerHTML =
        '<td class="fast-plan__when">—</td><td class="muted"><strong>Cortar primeiro:</strong> ' +
        escapeHtml(spec.cutFirst) +
        (spec.rainAlt
          ? " · <strong>Chuva:</strong> " + escapeHtml(spec.rainAlt)
          : "") +
        "</td>";
      tbody.appendChild(foot);
    }
  }

  function buildExpandedTable(dayEl, plan) {
    var table = document.createElement("table");
    table.className = "data fast-plan-table fast-plan-expand-table";
    table.innerHTML =
      "<thead><tr><th>Horário</th><th>Parada / detalhe</th></tr></thead>";
    var tbody = document.createElement("tbody");
    table.appendChild(tbody);

    var walkRoutes = dayEl.querySelectorAll(".walk-route");
    var walkIdx = 0;
    var dayId = dayEl.id;

    plan.querySelectorAll(".fast-plan-table tbody tr").forEach(function (macroTr) {
      var whenCell = macroTr.querySelector(".fast-plan__when");
      var whenKey = whenCell ? whenCell.textContent.trim() : "";
      var macroCell = macroTr.querySelector("td:last-child");
      var macroHtml = macroCell ? macroCell.innerHTML : "";
      var spec = windowSpecForRow(dayId, whenKey);
      var needsExpand = rowNeedsExpand(macroTr, dayId, whenKey);

      if (!needsExpand) {
        var clone = macroTr.cloneNode(true);
        clone.classList.add("fast-plan-expand__macro-row");
        tbody.appendChild(clone);
        return;
      }

      var label = isTourRow(macroTr) ? "Tour guiado" : "Janela detalhada";
      appendAnchorRow(tbody, whenCell, macroHtml, label);

      if (isTourRow(macroTr)) {
        var routeEl = walkRoutes[walkIdx];
        walkIdx += 1;
        var stops = routeEl
          ? routeEl.querySelectorAll(".walk-route__stops > li")
          : [];
        var window_ = whenCell ? parseWhenWindow(whenKey) : null;
        if (stops.length) {
          renderWalkStops(tbody, stops, window_);
        } else {
          var miss = document.createElement("tr");
          miss.className = "fast-plan-expand__stop";
          miss.innerHTML =
            '<td class="fast-plan__when">—</td><td class="muted">Sem paradas em <code>walk-route</code>.</td>';
          tbody.appendChild(miss);
        }
      }

      if (spec) {
        renderWindowBlocks(tbody, spec, parseWhenWindow(whenKey));
      }
    });

    return table;
  }

  function countExpandableRows(plan, dayEl) {
    var n = 0;
    var dayId = dayEl.id;
    plan.querySelectorAll(".fast-plan-table tbody tr").forEach(function (tr) {
      var when = tr.querySelector(".fast-plan__when");
      if (rowNeedsExpand(tr, dayId, when ? when.textContent.trim() : "")) n++;
    });
    return n;
  }

  function ensureScheduleLabel(plan) {
    var tableWrap = plan.querySelector(".fast-plan__table-wrap");
    if (!tableWrap) return;
    var schedLabel = plan.querySelector(".fast-plan__schedule-label");
    if (!schedLabel) {
      schedLabel = document.createElement("p");
      schedLabel.className = "fast-plan__schedule-label";
      tableWrap.insertAdjacentElement("beforebegin", schedLabel);
    }
    schedLabel.innerHTML =
      '<span class="fast-plan__schedule-title">Roteiro executável</span>' +
      '<span class="fast-plan__schedule-hint">Sequência por horário já visível; use recolher para voltar ao resumo</span>';
  }

  function setupPlan(plan, dayEl) {
    if (!plan || !dayEl) return;
    ensureScheduleLabel(plan);
    if (plan.querySelector(".fast-plan-expand")) return;

    var expandable = countExpandableRows(plan, dayEl);
    if (expandable < 1) return;

    var wrap = document.createElement("div");
    wrap.className = "fast-plan-expand";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fast-plan-expand__toggle";
    btn.setAttribute("aria-expanded", "false");
    var panelId = "fast-plan-expand-panel-" + dayEl.id;
    btn.setAttribute("aria-controls", panelId);
    btn.textContent =
      "Expandir horário completo (" + expandable + " janela" + (expandable > 1 ? "s" : "") + ")";

    var panel = document.createElement("div");
    panel.className = "fast-plan-expand__panel";
    panel.id = panelId;
    panel.hidden = false;

    function buildPanel() {
      if (panel.dataset.built) return;
      var scroll = document.createElement("div");
      scroll.className = "table-scroll fast-plan-expand__table-wrap";
      scroll.appendChild(buildExpandedTable(dayEl, plan));
      panel.appendChild(scroll);
      var note = document.createElement("p");
      note.className = "fast-plan-expand__note muted";
      note.textContent =
        "Horários nas paradas e blocos são estimativas (ordem de visita + duração da janela). Transporte: confirmar no Maps/BVG no dia.";
      panel.appendChild(note);
      panel.dataset.built = "1";
    }

    function setDetailedVisible(visible) {
      var tableWrap = plan.querySelector(".fast-plan__table-wrap");
      panel.hidden = !visible;
      if (tableWrap) tableWrap.hidden = visible;
      btn.setAttribute("aria-expanded", visible ? "true" : "false");
      btn.textContent = visible
        ? "Mostrar resumo curto"
        : "Mostrar roteiro detalhado";
    }

    buildPanel();
    setDetailedVisible(true);

    btn.addEventListener("click", function () {
      var opening = panel.hidden;
      if (opening) buildPanel();
      setDetailedVisible(opening);
    });

    wrap.appendChild(btn);
    wrap.appendChild(panel);

    var tableWrap = plan.querySelector(".fast-plan__table-wrap");
    if (tableWrap) {
      tableWrap.insertAdjacentElement("beforebegin", wrap);
    } else {
      plan.appendChild(wrap);
    }
  }

  function initAll() {
    document.querySelectorAll("details.day").forEach(function (dayEl) {
      if (!dayEl.id) return;
      var plan = document.getElementById("fast-" + dayEl.id);
      if (plan) setupPlan(plan, dayEl);
    });
  }

  function loadDetailsThenInit() {
    fetch("./data/fast-plan-window-details.json", { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("http " + r.status);
        return r.json();
      })
      .then(function (data) {
        windowDetails = data || windowDetails;
        detailsReady = true;
        initAll();
      })
      .catch(function () {
        detailsReady = true;
        initAll();
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadDetailsThenInit);
  } else {
    loadDetailsThenInit();
  }

  window.roteiroRefreshFastPlanExpand = function () {
    document.querySelectorAll(".fast-plan-expand").forEach(function (el) {
      el.remove();
    });
    loadDetailsThenInit();
  };
})();
