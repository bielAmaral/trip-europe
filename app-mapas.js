/**
 * Paradas GPS + modo de transporte entre pontos (#mapas e plano FAST de cada dia).
 */
(function () {
  "use strict";

  var CSV_URL = "data/mapas-paradas.csv?v=33";

  var daysById = {};

  var LEG_ICONS = {
    walk: "🚶",
    metro: "🚇",
    train: "🚆",
    bus: "🚌",
    tram: "🚋",
    flight: "✈️",
    funicular: "🚡",
    taxi: "🚕",
  };

  function parseCsv(text) {
    var rows = [];
    var i = 0;
    var field = "";
    var inQuotes = false;
    var row = [];

    function pushField() {
      row.push(field);
      field = "";
    }
    function pushRow() {
      if (row.length) rows.push(row);
      row = [];
    }

    while (i < text.length) {
      var c = text[i];
      if (inQuotes) {
        if (c === '"') {
          if (text[i + 1] === '"') {
            field += '"';
            i += 2;
            continue;
          }
          inQuotes = false;
          i++;
          continue;
        }
        field += c;
        i++;
        continue;
      }
      if (c === '"') {
        inQuotes = true;
        i++;
        continue;
      }
      if (c === ",") {
        pushField();
        i++;
        continue;
      }
      if (c === "\r") {
        i++;
        continue;
      }
      if (c === "\n") {
        pushField();
        pushRow();
        i++;
        continue;
      }
      field += c;
      i++;
    }
    if (field.length || row.length) {
      pushField();
      pushRow();
    }
    return rows;
  }

  function rowsToObjects(table) {
    if (!table.length) return [];
    var headers = table[0];
    return table.slice(1).map(function (cells) {
      var o = {};
      headers.forEach(function (h, idx) {
        o[h] = cells[idx] != null ? cells[idx] : "";
      });
      return o;
    });
  }

  function groupByDay(objects) {
    var map = {};
    var order = [];
    objects.forEach(function (o) {
      var id = o.day_id;
      if (!map[id]) {
        map[id] = {
          day_id: id,
          date: o.date,
          title: o.day_title,
          route_url: o.route_day_url,
          stops: [],
        };
        order.push(id);
      }
      map[id].stops.push(o);
    });
    return order.map(function (id) {
      return map[id];
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function catClass(cat) {
    return "mapas-stop--" + (cat || "sight");
  }

  function legDetailText(leg, fromName, toName) {
    if (!leg || !leg.leg_mode) return "";
    var mode = leg.leg_mode_pt || leg.leg_mode;
    var transport = leg.leg_hint ? mode + " — " + leg.leg_hint : mode;
    if (fromName && toName) {
      return fromName + " → " + toName + ": " + transport;
    }
    if (toName) return "Até " + toName + ": " + transport;
    return transport;
  }

  function renderLeg(leg, fromStop, toStop, compact) {
    if (!leg || !leg.leg_mode) return null;

    var li = document.createElement("li");
    li.className =
      "mapas-leg mapas-leg--" + leg.leg_mode + (compact ? " mapas-leg--compact" : "");

    if (!compact) {
      var icon = document.createElement("span");
      icon.className = "mapas-leg__icon";
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = LEG_ICONS[leg.leg_mode] || "→";
      li.appendChild(icon);
    }

    var detail = document.createElement("span");
    detail.className = "mapas-leg__detail";
    if (compact) {
      var mode = leg.leg_mode_pt || leg.leg_mode;
      detail.textContent = leg.leg_hint ? mode + " · " + leg.leg_hint : mode;
    } else {
      detail.textContent = legDetailText(
        leg,
        fromStop ? fromStop.name_pt : "",
        toStop ? toStop.name_pt : ""
      );
    }
    li.appendChild(detail);

    var mapsUrl = leg.leg_maps_url || (toStop && toStop.maps_search_url);
    if (mapsUrl) {
      var dir = document.createElement("a");
      dir.className = compact ? "mapas-inline-link" : "mapas-leg__dir btn-maps";
      dir.href = mapsUrl;
      dir.target = "_blank";
      dir.rel = "noopener noreferrer";
      dir.setAttribute("aria-label", "Abrir rota no Google Maps");
      dir.textContent = "Maps";
      li.appendChild(dir);
    }

    return li;
  }

  function renderStop(s, compact) {
    var li = document.createElement("li");
    li.className =
      "mapas-stop " + catClass(s.category) + (compact ? " mapas-stop--compact" : "");

    var num = document.createElement("span");
    num.className = "mapas-stop__num";
    num.textContent = s.order;
    li.appendChild(num);

    if (!compact) {
      var badge = document.createElement("span");
      badge.className = "mapas-stop__cat";
      badge.textContent = s.category_pt || s.category;
      li.appendChild(badge);
    }

    var name = document.createElement("span");
    name.className = "mapas-stop__name";
    name.textContent = s.name_pt;
    li.appendChild(name);

    var link = document.createElement("a");
    link.className = compact ? "mapas-inline-link" : "mapas-stop__maps btn-maps";
    link.href = s.maps_search_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Abrir " + s.name_pt + " no Google Maps");
    link.textContent = "Maps";
    li.appendChild(link);

    return li;
  }

  function buildStopListOl(day, listClass) {
    var compact = listClass && listClass.indexOf("--dia") >= 0;
    var ol = document.createElement("ol");
    ol.className = listClass || "mapas-stop-list";

    var prev = null;
    day.stops.forEach(function (s) {
      if (s.leg_mode) {
        var legEl = renderLeg(s, prev, s, compact);
        if (legEl) ol.appendChild(legEl);
      }
      ol.appendChild(renderStop(s, compact));
      prev = s;
    });

    return ol;
  }

  function removeDayMapInjections(dayEl, plan) {
    if (dayEl) {
      var body = dayEl.querySelector(".body");
      if (body) {
        body.querySelectorAll(".dia-mapa-roteiro").forEach(function (n) {
          n.remove();
        });
      }
    }
    if (plan) {
      plan.querySelectorAll(
        ".fast-plan__badge--maps, .fast-plan__mapa-detail, .fast-plan__mapa-bar, .fast-plan-legs"
      ).forEach(function (n) {
        n.remove();
      });
    }
  }

  function buildFastPlanMapLink(day) {
    if (!day.route_url) return null;
    var routeA = document.createElement("a");
    routeA.className = "fast-plan__badge fast-plan__badge--maps";
    routeA.href = day.route_url;
    routeA.target = "_blank";
    routeA.rel = "noopener noreferrer";
    routeA.textContent = "Maps · rota";
    routeA.setAttribute("aria-label", "Abrir rota do dia no Google Maps");
    routeA.id = "mapa-roteiro-" + day.day_id;
    return routeA;
  }

  function buildFastPlanMapDetails(day) {
    var det = document.createElement("details");
    det.className = "transit-collapse fast-plan__mapa-detail";
    var sum = document.createElement("summary");
    sum.textContent = "Paradas no Maps (" + day.stops.length + ")";
    det.appendChild(sum);
    var inner = document.createElement("div");
    inner.className = "transit transit--nested fast-plan__mapa-detail-body";
    inner.appendChild(buildStopListOl(day, "mapas-stop-list mapas-stop-list--dia"));
    det.appendChild(inner);
    return det;
  }

  function ensureScheduleLabel(plan) {
    if (plan.querySelector(".fast-plan__schedule-label")) return;
    var tableWrap = plan.querySelector(".fast-plan__table-wrap");
    if (!tableWrap) return;
    var schedLabel = document.createElement("p");
    schedLabel.className = "fast-plan__schedule-label";
    schedLabel.textContent = "Resumo por horário";
    tableWrap.insertAdjacentElement("beforebegin", schedLabel);
  }

  function injectDayMapRoteiro(day) {
    var dayEl = document.getElementById(day.day_id);
    if (!dayEl || !day.stops.length) return;

    var plan = document.getElementById("fast-" + day.day_id);
    if (!plan) return;

    removeDayMapInjections(dayEl, plan);

    var meta = plan.querySelector(".fast-plan__meta");
    var mapLink = buildFastPlanMapLink(day);
    var details = buildFastPlanMapDetails(day);

    if (meta && mapLink) {
      meta.appendChild(mapLink);
    }

    var body = dayEl.querySelector(".body");
    var transit =
      body && body.querySelector("details.transit-collapse:not(.fast-plan__mapa-detail)");
    if (transit && transit.parentNode) {
      transit.parentNode.insertBefore(details, transit);
    } else {
      plan.appendChild(details);
    }

    ensureScheduleLabel(plan);
  }

  function renderMapasSection(days) {
    var host = document.getElementById("mapasDiasHost");
    if (!host) return;

    host.innerHTML = "";
    host.removeAttribute("aria-busy");

    var frag = document.createDocumentFragment();

    days.forEach(function (day) {
      var det = document.createElement("details");
      det.className = "mapas-day";
      det.id = "mapas-" + day.day_id;

      var sum = document.createElement("summary");
      sum.innerHTML =
        '<span class="mapas-day__date">' +
        escapeHtml(day.date) +
        '</span> <span class="mapas-day__title">' +
        escapeHtml(day.title) +
        '</span> <span class="mapas-day__count">' +
        day.stops.length +
        " paradas</span>";
      det.appendChild(sum);

      var body = document.createElement("div");
      body.className = "mapas-day__body";

      var tools = document.createElement("div");
      tools.className = "mapas-day__tools";

      if (day.route_url) {
        var routeA = document.createElement("a");
        routeA.className = "btn-maps mapas-day__route";
        routeA.href = day.route_url;
        routeA.target = "_blank";
        routeA.rel = "noopener noreferrer";
        routeA.textContent = "Abrir rota do dia no Maps";
        tools.appendChild(routeA);
      }

      var diaA = document.createElement("a");
      diaA.className = "mapas-day__link-dia";
      diaA.href = "#" + day.day_id;
      diaA.textContent = "Ver plano FAST no roteiro";
      tools.appendChild(diaA);

      body.appendChild(tools);
      body.appendChild(buildStopListOl(day));
      det.appendChild(body);
      frag.appendChild(det);
    });

    host.appendChild(frag);
  }

  function injectFastPlanLegs(days) {
    days.forEach(injectDayMapRoteiro);
  }

  function showMapasError(msg) {
    var host = document.getElementById("mapasDiasHost");
    if (host) {
      host.removeAttribute("aria-busy");
      host.innerHTML = '<p class="note mapas-error">' + escapeHtml(msg) + "</p>";
    }
    document.querySelectorAll(".fast-plan").forEach(function (plan) {
      if (plan.querySelector(".fast-plan__badge--maps")) return;
      var err = document.createElement("p");
      err.className = "fast-plan__mapa-error note";
      err.textContent = "Mapa indisponível: " + msg;
      var meta = plan.querySelector(".fast-plan__meta");
      if (meta) {
        plan.insertBefore(err, meta.nextSibling);
      } else {
        plan.insertBefore(err, plan.firstChild);
      }
    });
  }

  function onDataLoaded(days) {
    daysById = {};
    days.forEach(function (d) {
      daysById[d.day_id] = d;
    });
    renderMapasSection(days);
    injectFastPlanLegs(days);
    if (window.refreshLucide) window.refreshLucide();

    var h = (location.hash || "").replace(/^#/, "");
    if (h.indexOf("day-20") === 0 && window.roteiroRefreshDayMapRoteiro) {
      window.roteiroRefreshDayMapRoteiro(h);
    }
  }

  window.roteiroRefreshDayMapRoteiro = function (dayId) {
    var day = daysById[dayId];
    if (!day) return;
    injectDayMapRoteiro(day);
  };

  window.roteiroRefreshDayTransport = window.roteiroRefreshDayMapRoteiro;

  var host = document.getElementById("mapasDiasHost");
  if (host) host.setAttribute("aria-busy", "true");

  fetch(CSV_URL)
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.text();
    })
    .then(function (text) {
      var table = parseCsv(text);
      if (!table.length) throw new Error("CSV vazio");
      var headers = table[0];
      var objects = rowsToObjects(table);
      if (!objects.length) throw new Error("CSV sem linhas de dados");
      var hasLegCols =
        headers.indexOf("leg_mode") >= 0 && headers.indexOf("leg_maps_url") >= 0;
      var hasAnyLeg = objects.some(function (o) {
        return o.leg_mode;
      });
      if (!hasLegCols || (!hasAnyLeg && objects.length > 3)) {
        throw new Error("CSV desatualizado — corre python3 scripts/generate_mapas_csv.py");
      }
      onDataLoaded(groupByDay(objects));
    })
    .catch(function (err) {
      showMapasError("Não foi possível carregar as paradas (" + err.message + ").");
    });
})();
