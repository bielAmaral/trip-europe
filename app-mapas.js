/**
 * Paradas GPS + modo de transporte entre pontos (#mapas e plano FAST de cada dia).
 */
(function () {
  "use strict";

  var CSV_URL = "data/mapas-paradas.csv?v=38";

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

  var CAT_DO_FALLBACK = {
    airport: "Aeroporto: imigração, bagagem e seguir para o transporte do dia.",
    hotel: "Hotel: check-in ou check-out, deixar mala, banho rápido se precisar.",
    transport: "Deslocação — confira horário no bilhete / app Omio.",
    sight: "Passear e fotos; detalhe no plano por horário acima.",
    food: "Comer ou comprar algo para o kit / jantar.",
    night: "Bar ou zona de noite — 1 drink e dormir se amanhã tiver trem cedo.",
    tour: "Tour / visita — gorjeta em cash se for gratuito.",
  };

  function extractFastPlanContext(plan) {
    if (!plan) return { mode: "", rows: [], feet: [] };
    var modeEl = plan.querySelector(".fast-plan__mode");
    var rows = [];
    plan.querySelectorAll(".fast-plan-table tbody tr").forEach(function (tr) {
      var when = tr.querySelector(".fast-plan__when");
      var cells = tr.querySelectorAll("td");
      var whatCell = cells.length > 1 ? cells[cells.length - 1] : null;
      if (when && whatCell) {
        rows.push({
          when: when.textContent.trim(),
          what: whatCell.textContent.trim(),
        });
      }
    });
    var feet = [];
    plan.querySelectorAll(".fast-plan__foot").forEach(function (p) {
      feet.push(p.textContent.trim());
    });
    return {
      mode: modeEl ? modeEl.textContent.trim() : "",
      rows: rows,
      feet: feet,
    };
  }

  function stopKeywords(namePt) {
    var base = String(namePt || "")
      .split("(")[0]
      .split("—")[0]
      .trim()
      .toLowerCase();
    var parts = base.split(/[\s,/·]+/).filter(function (w) {
      return w.length > 3;
    });
    return [base].concat(parts);
  }

  function normalizePlaceKey(s) {
    return String(s || "")
      .toLowerCase()
      .replace(/\([^)]*\)/g, "")
      .split(/[+·/—–-]/)[0]
      .replace(/\s+/g, " ")
      .trim();
  }

  function parseWalkStopsFromDay(dayId) {
    var dayEl = document.getElementById(dayId);
    if (!dayEl) return [];
    var out = [];
    dayEl.querySelectorAll(".walk-route .walk-route__stops > li").forEach(function (li) {
      var strong = li.querySelector("strong");
      var title = strong ? strong.textContent.trim() : "";
      if (!title) return;
      var full = li.textContent.trim();
      var tip = full;
      if (full.indexOf(title) === 0) {
        tip = full.slice(title.length).replace(/^[\s(—–-]+/, "").trim();
        if (tip.charAt(0) === "(") {
          var close = tip.indexOf(")");
          if (close >= 0) tip = tip.slice(close + 1).replace(/^[\s—–-]+/, "").trim();
        }
      }
      out.push({ title: title, tip: tip });
    });
    return out;
  }

  function findStopForWalkTitle(title, stops) {
    var key = normalizePlaceKey(title);
    if (!key) return null;
    var best = null;
    var bestScore = 0;
    stops.forEach(function (s) {
      if (s.category === "transport" || s.category === "hotel" || s.category === "airport") {
        return;
      }
      var nk = normalizePlaceKey(s.name_pt);
      if (!nk) return;
      var score = 0;
      if (nk === key) score = 100;
      else if (nk.indexOf(key) >= 0 || key.indexOf(nk) >= 0) score = 60;
      else {
        var parts = key.split(/\s+/).filter(function (w) {
          return w.length >= 4;
        });
        parts.forEach(function (w) {
          if (nk.indexOf(w) >= 0) score += 15;
        });
      }
      if (score > bestScore) {
        bestScore = score;
        best = s;
      }
    });
    return bestScore >= 30 ? best : null;
  }

  function mapsSearchForWalkTitle(title) {
    return (
      "https://www.google.com/maps/search/?api=1&query=" +
      encodeURIComponent(title)
    );
  }

  function matchStopActivity(stop, fastRows, walkTip) {
    if (walkTip) return walkTip;
    if (stop.do_here_pt) return stop.do_here_pt;
    var keys = stopKeywords(stop.name_pt);
    var i;
    for (i = 0; i < fastRows.length; i++) {
      var whatLow = fastRows[i].what.toLowerCase();
      var j;
      for (j = 0; j < keys.length; j++) {
        if (keys[j].length >= 4 && whatLow.indexOf(keys[j]) >= 0) {
          return fastRows[i].when + " — " + fastRows[i].what;
        }
      }
    }
    if (stop.category === "transport" && stop.leg_hint) {
      return "Ir para " + stop.name_pt + ": " + stop.leg_hint;
    }
    return CAT_DO_FALLBACK[stop.category] || "";
  }

  function buildMapasDayIntro(fastCtx) {
    var wrap = document.createElement("div");
    wrap.className = "mapas-day-intro";

    if (fastCtx.mode) {
      var obj = document.createElement("p");
      obj.className = "mapas-day-intro__objective";
      obj.innerHTML =
        "<strong>Hoje:</strong> " + escapeHtml(fastCtx.mode);
      wrap.appendChild(obj);
    }

    if (fastCtx.rows.length) {
      var title = document.createElement("p");
      title.className = "mapas-day-intro__label";
      title.textContent = "Plano por horário (resumo)";
      wrap.appendChild(title);

      var ol = document.createElement("ol");
      ol.className = "mapas-day-intro__schedule";
      fastCtx.rows.forEach(function (r) {
        var li = document.createElement("li");
        li.innerHTML =
          "<span class=\"mapas-day-intro__when\">" +
          escapeHtml(r.when) +
          "</span> " +
          escapeHtml(r.what);
        ol.appendChild(li);
      });
      wrap.appendChild(ol);
    }

    if (fastCtx.feet.length) {
      var feet = document.createElement("ul");
      feet.className = "mapas-day-intro__feet";
      fastCtx.feet.forEach(function (t) {
        var li = document.createElement("li");
        li.textContent = t;
        feet.appendChild(li);
      });
      wrap.appendChild(feet);
    }

    return wrap;
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

  function renderStop(s, compact, activityText) {
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

    if (activityText) {
      var doHere = document.createElement("span");
      doHere.className = "mapas-stop__do";
      doHere.textContent = activityText;
      li.appendChild(doHere);
    }

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

  function renderWalkOnlyStop(index, walkItem, matchedStop, compact) {
    var li = document.createElement("li");
    li.className =
      "mapas-stop mapas-stop--sight mapas-stop--walk" +
      (compact ? " mapas-stop--compact" : "");

    var num = document.createElement("span");
    num.className = "mapas-stop__num";
    num.textContent = index;
    li.appendChild(num);

    if (!compact) {
      var badge = document.createElement("span");
      badge.className = "mapas-stop__cat";
      badge.textContent = "Rota a pé";
      li.appendChild(badge);
    }

    var name = document.createElement("span");
    name.className = "mapas-stop__name";
    name.textContent = walkItem.title;
    li.appendChild(name);

    if (walkItem.tip) {
      var doHere = document.createElement("span");
      doHere.className = "mapas-stop__do";
      doHere.textContent = walkItem.tip;
      li.appendChild(doHere);
    }

    var url =
      (matchedStop && matchedStop.maps_search_url) ||
      mapsSearchForWalkTitle(walkItem.title);
    var link = document.createElement("a");
    link.className = compact ? "mapas-inline-link" : "mapas-stop__maps btn-maps";
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Abrir " + walkItem.title + " no Google Maps");
    link.textContent = "Maps";
    li.appendChild(link);

    return li;
  }

  function buildWalkTipsIndex(walkItems, dayStops) {
    var byStopKey = {};
    var unmatched = [];
    walkItems.forEach(function (w) {
      var stop = findStopForWalkTitle(w.title, dayStops);
      if (stop) {
        byStopKey[stop.order + ":" + stop.name_pt] = w.tip;
      } else {
        unmatched.push(w);
      }
    });
    return { byStopKey: byStopKey, unmatched: unmatched };
  }

  function buildStopListOl(day, listClass, fastRows) {
    var compact = listClass && listClass.indexOf("--dia") >= 0;
    var ol = document.createElement("ol");
    ol.className = listClass || "mapas-stop-list";

    var walkItems = parseWalkStopsFromDay(day.day_id);
    var walkIdx = buildWalkTipsIndex(walkItems, day.stops);

    if (compact && walkItems.length) {
      var walkLabel = document.createDocumentFragment();
      var head = document.createElement("li");
      head.className = "mapas-walk-section-head";
      head.textContent = "Rota a pé — ordem e curiosidade";
      ol.appendChild(head);

      walkItems.forEach(function (w, i) {
        var matched = findStopForWalkTitle(w.title, day.stops);
        ol.appendChild(renderWalkOnlyStop(i + 1, w, matched, compact));
      });

      if (day.stops.some(function (s) {
        return s.category === "transport" || s.category === "hotel" || s.category === "airport";
      })) {
        var sep = document.createElement("li");
        sep.className = "mapas-walk-section-head mapas-walk-section-head--rest";
        sep.textContent = "Restante do dia (transporte, hotel, extras)";
        ol.appendChild(sep);
      }
    }

    var prev = null;
    day.stops.forEach(function (s) {
      if (s.leg_mode) {
        var legEl = renderLeg(s, prev, s, compact);
        if (legEl) ol.appendChild(legEl);
      }
      var stopKey = s.order + ":" + s.name_pt;
      var walkTip = walkIdx.byStopKey[stopKey] || "";
      var activity = compact
        ? matchStopActivity(s, fastRows || [], walkTip)
        : walkTip || "";
      if (compact && walkItems.length && walkTip && s.category === "sight") {
        /* já listado na secção rota a pé — evita duplicar parada */
        prev = s;
        return;
      }
      ol.appendChild(renderStop(s, compact, activity));
      prev = s;
    });

    return ol;
  }

  function removeDayMapInjections(dayEl, plan) {
    if (dayEl) {
      var body = dayEl.querySelector(".body");
      if (body) {
        body.querySelectorAll(".dia-mapa-roteiro, .fast-plan__mapa-detail").forEach(
          function (n) {
            n.remove();
          }
        );
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

  function buildFastPlanMapDetails(day, plan) {
    var fastCtx = extractFastPlanContext(plan);
    var det = document.createElement("details");
    det.className = "transit-collapse fast-plan__mapa-detail";
    det.id = "mapa-paradas-" + day.day_id;
    var sum = document.createElement("summary");
    sum.textContent =
      "Passo a passo no mapa — o que fazer em cada lugar (" +
      day.stops.length +
      ")";
    det.appendChild(sum);
    var inner = document.createElement("div");
    inner.className = "transit transit--nested fast-plan__mapa-detail-body";
    inner.appendChild(buildMapasDayIntro(fastCtx));
    var stepsLabel = document.createElement("p");
    stepsLabel.className = "mapas-day-intro__label mapas-day-intro__label--steps";
    stepsLabel.textContent =
      parseWalkStopsFromDay(day.day_id).length
        ? "Passo a passo — rota a pé + deslocações do dia"
        : "Ordem das paradas (como chegar entre elas)";
    inner.appendChild(stepsLabel);
    inner.appendChild(
      buildStopListOl(day, "mapas-stop-list mapas-stop-list--dia", fastCtx.rows)
    );
    det.appendChild(inner);
    return det;
  }

  function ensureScheduleLabel(plan) {
    if (plan.querySelector(".fast-plan__schedule-label")) return;
    var tableWrap = plan.querySelector(".fast-plan__table-wrap");
    if (!tableWrap) return;
    var schedLabel = document.createElement("p");
    schedLabel.className = "fast-plan__schedule-label";
    schedLabel.textContent = "Plano do dia — comece por aqui (horários)";
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
    var details = buildFastPlanMapDetails(day, plan);

    if (meta && mapLink) {
      meta.appendChild(mapLink);
    }

    ensureScheduleLabel(plan);

    var foot = plan.querySelector(".fast-plan__foot");
    if (foot && foot.parentNode) {
      foot.parentNode.insertBefore(details, foot);
    } else {
      var tableWrap = plan.querySelector(".fast-plan__table-wrap");
      if (tableWrap && tableWrap.nextSibling) {
        tableWrap.parentNode.insertBefore(details, tableWrap.nextSibling);
      } else {
        plan.appendChild(details);
      }
    }
  }

  function renderMapasSection(days) {
    var host = document.getElementById("mapasDiasHost");
    if (!host) return;

    host.innerHTML = "";
    host.removeAttribute("aria-busy");

    var ul = document.createElement("ul");
    ul.className = "mapas-index-list";

    days.forEach(function (day) {
      var li = document.createElement("li");
      li.className = "mapas-index-list__item";

      var diaA = document.createElement("a");
      diaA.className = "mapas-index-list__dia";
      diaA.href = "#" + day.day_id;
      diaA.textContent = day.date + " — " + day.title + " (" + day.stops.length + " paradas)";
      li.appendChild(diaA);

      if (day.route_url) {
        var routeA = document.createElement("a");
        routeA.className = "mapas-index-list__maps btn-maps";
        routeA.href = day.route_url;
        routeA.target = "_blank";
        routeA.rel = "noopener noreferrer";
        routeA.textContent = "Rota Maps";
        li.appendChild(routeA);
      }

      ul.appendChild(li);
    });

    host.appendChild(ul);
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
