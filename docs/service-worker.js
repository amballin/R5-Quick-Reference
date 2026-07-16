const CACHE_PREFIX = "photography-reference";
const CACHE_NAME = "photography-reference-1784207433";
const CACHE_URLS = [
  "./",
  ".nojekyll",
  "Cards/Birds%20Perched.png",
  "Cards/Birds%20in%20Flight.png",
  "Cards/Camera%20Buttons.png",
  "Cards/Camera%20Defaults.png",
  "Cards/Camera%20Setup.png",
  "Cards/Fireworks.png",
  "Cards/Landscape.png",
  "Cards/People.png",
  "Cards/Wildlife.png",
  "app-assets/apple-touch-icon.png",
  "app-assets/icon-192.png",
  "app-assets/icon-512.png",
  "appendices/AF%20Cases%20%26%20Tracking%20Behavior.html",
  "appendices/Back-Button%20AF%20%26%20Custom%20Button%20Strategies.html",
  "appendices/Canon%20EOS%20R5%20Official%20Icon%20Reference.html",
  "appendices/Custom%20Controls.html",
  "appendices/Drive%20Modes.html",
  "appendices/Electronic%20vs%20EFCS%20vs%20Mechanical%20Shutter.html",
  "appendices/Flash%20Photography.html",
  "appendices/Focus%20Bracketing%20%26%20In-Camera%20Depth%20Compositing.html",
  "appendices/Fv%20-%20Flexible%20Priority.html",
  "appendices/Image%20Stabilization.html",
  "appendices/Lens%20Capabilities.html",
  "appendices/Long%20Exposure%20%26%20Night%20Photography.html",
  "appendices/Metering%20Modes.html",
  "appendices/R5%20Quick%20Reference.html",
  "index.html",
  "manifest.webmanifest",
  "offline.html",
  "search_index.json",
  "service-worker.js"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(
        names
          .filter((name) => name.startsWith(CACHE_PREFIX + "-") && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (url.origin !== self.location.origin || request.method !== "GET") {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request, { cache: "reload" })
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match("./") || caches.match("index.html") || caches.match("offline.html")))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(request).then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      });
    })
  );
});
