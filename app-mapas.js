/**
 * Paradas GPS + modo de transporte entre pontos (#mapas e plano FAST de cada dia).
 */
(function () {
  "use strict";

  var CSV_URL = "data/mapas-paradas.csv?v=25";

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

  function legDetailText(leg) {
    if (!leg || !leg.leg_mode) return "";
    if (leg.leg_hint) {
      return (leg.leg_mode_pt || leg.leg_mode) + " — " + leg.leg_hint;
    }
    return leg.leg_mode_pt || leg.leg_mode;
  }

  function renderLeg(leg) {
    if (!leg || !leg.leg_mode) return null;

    var li = document.createElement("li");
    li.className = "mapas-leg mapas-leg--" + leg.leg_mode;

    var icon = document.createElement("span");
    icon.className = "mapas-leg__icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = LEG_ICONS[leg.leg_mode] || "→";
    li.appendChild(icon);

    var detail = document.createElement("span");
    detail.className = "mapas-leg__detail";
    detail.textContent = legDetailText(leg);
    li.appendChild(detail);

    if (leg.leg_maps_url) {
      var dir = document.createElement("a");
      dir.className = "mapas-leg__dir btn-maps";
      dir.href = leg.leg_maps_url;
      dir.target = "_blank";
      dir.rel = "noopener noreferrer";
      dir.textContent = "Abrir rota";
      li.appendChild(dir);
    }

    return li;
  }

  function renderStop(s) {
    var li = document.createElement("li");
    li.className = "mapas-stop " + catClass(s.category);

    var num = document.createElement("span");
    num.className = "mapas-stop__num";
    num.textContent = s.order;
    li.appendChild(num);

    var badge = document.createElement("span");
    badge.className = "mapas-stop__cat";
    badge.textContent = s.category_pt || s.category;
    li.appendChild(badge);

    var name = document.createElement("span");
    name.className = "mapas-stop__name";
    name.textContent = s.name_pt;
    li.appendChild(name);

    var link = document.createElement("a");
    link.className = "mapas-stop__maps";
    link.href = s.maps_search_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Abrir " + s.name_pt + " no Google Maps");
    link.textContent = "Maps";
    li.appendChild(link);

    return li;
  }

  function buildStopListOl(day, listClass) {
    var ol = document.createElement("ol");
    ol.className = listClass || "mapas-stop-list";

    day.stops.forEach(function (s) {
      if (s.leg_mode) {
        var legEl = renderLeg(s);
        if (legEl) ol.appendChild(legEl);
      }
      ol.appendChild(renderStop(s));
    });

    return ol;
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
    days.forEach(function (day) {
      var plan = document.getElementById("fast-" + day.day_id);
      if (!plan || plan.querySelector(".fast-plan-legs")) return;

      var hasLegs = day.stops.some(function (s) {
        return !!s.leg_mode;
      });
      if (!hasLegs) return;

      var wrap = document.createElement("div");
      wrap.className = "fast-plan-legs";

      var title = document.createElement("p");
      title.className = "fast-plan-legs__title";
      title.textContent = "Como ir de ponto a ponto";
      wrap.appendChild(title);

      wrap.appendChild(buildStopListOl(day, "mapas-stop-list mapas-stop-list--fast"));

      var tableWrap = plan.querySelector(".fast-plan__table-wrap");
      if (tableWrap) {
        tableWrap.insertAdjacentElement("afterend", wrap);
      } else {
        plan.appendChild(wrap);
      }
    });
  }

  function showMapasError(msg) {
    var host = document.getElementById("mapasDiasHost");
    if (!host) return;
    host.removeAttribute("aria-busy");
    host.innerHTML = '<p class="note mapas-error">' + escapeHtml(msg) + "</p>";
  }

  function onDataLoaded(days) {
    renderMapasSection(days);
    injectFastPlanLegs(days);
    if (window.refreshLucide) window.refreshLucide();
  }

  var host = document.getElementById("mapasDiasHost");
  if (host) host.setAttribute("aria-busy", "true");

  fetch(CSV_URL)
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.text();
    })
    .then(function (text) {
      var table = parseCsv(text);
      var objects = rowsToObjects(table);
      if (!objects.length) throw new Error("CSV vazio");
      if (!objects[0].leg_mode && objects[0].longitude) {
        throw new Error("CSV desatualizado — corre python3 scripts/generate_mapas_csv.py");
      }
      onDataLoaded(groupByDay(objects));
    })
    .catch(function (err) {
      showMapasError("Não foi possível carregar as paradas (" + err.message + ").");
    });
})();
