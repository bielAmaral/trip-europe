const CACHE = "roteiro-pwa-v11";
const PRECACHE = [
  "./",
  "./index.html",
  "./app-shell.js",
  "./app.css",
  "./app-views.js",
  "./app-search-ui.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];
const LUCIDE = "https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js";

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      try {
        await cache.addAll(PRECACHE);
      } catch (e) {
        console.warn("sw precache", e);
      }
      try {
        const res = await fetch(LUCIDE, { mode: "cors", cache: "reload" });
        if (res && res.ok) {
          await cache.put(LUCIDE, res.clone());
        }
      } catch (e) {
        /* icon pack offline só após 1.ª visita com rede */
      }
    })()
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  if (event.request.url.startsWith("chrome-extension://")) return;

  if (event.request.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          const res = await fetch(event.request);
          if (res && res.status === 200) {
            const c = await caches.open(CACHE);
            await c.put(event.request, res.clone());
          }
          return res;
        } catch {
          return (
            (await caches.match(event.request)) || (await caches.match("./index.html")) || (await caches.match("index.html"))
          );
        }
      })()
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((res) => {
          if (!res || res.status !== 200) return res;
          const t = res.type;
          if (t !== "basic" && t !== "cors") return res;
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(event.request, copy));
          return res;
        })
        .catch(() => caches.match("./index.html"));
    })
  );
});
