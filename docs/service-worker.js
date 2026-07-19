const CACHE_PREFIX = "photography-reference";
const CACHE_NAME = "photography-reference-1784477837";
const CACHE_URLS = [
  "./",
  ".nojekyll",
  "Cards/Birds%20Perched.html",
  "Cards/Birds%20in%20Flight.html",
  "Cards/Camera%20Buttons.html",
  "Cards/Camera%20Defaults.html",
  "Cards/Camera%20Setup%20Essentials.html",
  "Cards/Fireworks.html",
  "Cards/Landscape.html",
  "Cards/People.html",
  "Cards/Wildlife.html",
  "app-assets/apple-touch-icon.png",
  "app-assets/icon-192.png",
  "app-assets/icon-512.png",
  "appendices/AF%20Cases%20%26%20Tracking%20Behavior.html",
  "appendices/Back-Button%20AF%20%26%20Custom%20Button%20Strategies.html",
  "appendices/Canon%20EOS%20R5%20Official%20Icon%20Reference.html",
  "appendices/Flash%20Photography.html",
  "appendices/Focus%20Bracketing%20%26%20In-Camera%20Depth%20Compositing.html",
  "appendices/Fv%20-%20Flexible%20Priority.html",
  "appendices/Lens%20Capabilities.html",
  "appendices/Long%20Exposure%20%26%20Night%20Photography.html",
  "appendices/R5%20Quick%20Reference.html",
  "index.html",
  "manifest.webmanifest",
  "offline.html",
  "search_index.json",
  "service-worker.js",
  "web-assets/Card%20Logos/png/Bird%20Perched.png",
  "web-assets/Card%20Logos/png/Bird%20in%20Flight.png",
  "web-assets/Card%20Logos/png/Camera%20Default.png",
  "web-assets/Card%20Logos/png/Fireworks.png",
  "web-assets/Card%20Logos/png/Landscape.png",
  "web-assets/Card%20Logos/png/People.png",
  "web-assets/Card%20Logos/png/Silver%20Logo.png",
  "web-assets/Card%20Logos/png/Wildlife.png",
  "web-assets/icons/canon_r5_official/evaluative_metering.svg",
  "web-assets/icons/canon_r5_official/eye_detection.svg",
  "web-assets/icons/canon_r5_official/face_tracking.svg",
  "web-assets/icons/canon_r5_official/high_speed_continuous_shooting.svg",
  "web-assets/icons/canon_r5_official/high_speed_continuous_shooting_plus.svg",
  "web-assets/icons/canon_r5_official/lens_af.svg",
  "web-assets/icons/canon_r5_official/lens_mf.svg",
  "web-assets/icons/canon_r5_official/low_speed_continuous_shooting.svg",
  "web-assets/icons/canon_r5_official/mode-select.svg",
  "web-assets/icons/canon_r5_official/one_point_af.svg",
  "web-assets/icons/canon_r5_official/single_shooting.svg",
  "web-assets/icons/card_icons/SVG/aperture.svg",
  "web-assets/icons/card_icons/SVG/exposure_compensation.svg",
  "web-assets/icons/card_icons/SVG/highlight_alert.svg",
  "web-assets/icons/card_icons/SVG/histogram.svg",
  "web-assets/icons/card_icons/SVG/image_quality_raw.svg",
  "web-assets/icons/card_icons/SVG/image_stabilization.svg",
  "web-assets/icons/card_icons/SVG/iso.svg",
  "web-assets/icons/card_icons/SVG/long_exposure_nr.svg",
  "web-assets/icons/card_icons/SVG/shutter.svg",
  "web-assets/icons/card_icons/SVG/subject_detection.svg",
  "web-assets/icons/card_icons/SVG/white_balance.svg"
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
