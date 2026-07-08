const CACHE_PREFIX = "photography-reference";
const CACHE_NAME = "photography-reference-1783533904";
const CACHE_URLS = [
  "./",
  "Cards/Birds%20Perched.png",
  "Cards/Birds%20in%20Flight.png",
  "Cards/Camera%20Defaults.png",
  "Cards/Camera%20Setup.png",
  "Cards/Fireworks.png",
  "Cards/Landscape.png",
  "Cards/People.png",
  "Cards/Wildlife.png",
  "appendices/Canon%20EOS%20R5%20Official%20Icon%20Reference.html",
  "appendices/Lens%20Capabilities.html",
  "appendices/R5%20Quick%20Reference.html",
  "assets/icons/canon_r5_official/af_point.svg",
  "assets/icons/canon_r5_official/af_point_adjustment.svg",
  "assets/icons/canon_r5_official/autofocus_tab.svg",
  "assets/icons/canon_r5_official/bounce_flash_photography.svg",
  "assets/icons/canon_r5_official/center_weighted_average_metering.svg",
  "assets/icons/canon_r5_official/close_non_portrait_blue_sky_included.png",
  "assets/icons/canon_r5_official/close_non_portrait_blue_sky_included_backlit.png",
  "assets/icons/canon_r5_official/close_non_portrait_bright.png",
  "assets/icons/canon_r5_official/close_non_portrait_bright_backlit.png",
  "assets/icons/canon_r5_official/close_non_portrait_dark.png",
  "assets/icons/canon_r5_official/close_non_portrait_spotlight.png",
  "assets/icons/canon_r5_official/cropping_images.svg",
  "assets/icons/canon_r5_official/evaluative_metering.svg",
  "assets/icons/canon_r5_official/expand_af_area.svg",
  "assets/icons/canon_r5_official/expand_af_area_around.svg",
  "assets/icons/canon_r5_official/eye_detection.svg",
  "assets/icons/canon_r5_official/face.svg",
  "assets/icons/canon_r5_official/face_tracking.svg",
  "assets/icons/canon_r5_official/flash_photography_without_flash_exposure_compensation.svg",
  "assets/icons/canon_r5_official/high_speed_continuous_shooting.svg",
  "assets/icons/canon_r5_official/high_speed_continuous_shooting_plus.svg",
  "assets/icons/canon_r5_official/high_speed_display.svg",
  "assets/icons/canon_r5_official/images_created_and_saved_after_performing_processing.svg",
  "assets/icons/canon_r5_official/info.svg",
  "assets/icons/canon_r5_official/jpeg.svg",
  "assets/icons/canon_r5_official/large_zone_af_horizontal.svg",
  "assets/icons/canon_r5_official/large_zone_af_vertical.svg",
  "assets/icons/canon_r5_official/lens_af.svg",
  "assets/icons/canon_r5_official/lens_is_off.svg",
  "assets/icons/canon_r5_official/lens_is_on.svg",
  "assets/icons/canon_r5_official/lens_mf.svg",
  "assets/icons/canon_r5_official/low_speed_continuous_shooting.svg",
  "assets/icons/canon_r5_official/multi_function.svg",
  "assets/icons/canon_r5_official/multi_shot_noise_reduction.svg",
  "assets/icons/canon_r5_official/multiple_exposures.svg",
  "assets/icons/canon_r5_official/nature_outdoor_scene_blue_sky_included.png",
  "assets/icons/canon_r5_official/nature_outdoor_scene_blue_sky_included_backlit.png",
  "assets/icons/canon_r5_official/nature_outdoor_scene_bright.png",
  "assets/icons/canon_r5_official/nature_outdoor_scene_bright_backlit.png",
  "assets/icons/canon_r5_official/nature_outdoor_scene_dark_tripod_used.png",
  "assets/icons/canon_r5_official/non_portrait_dark.png",
  "assets/icons/canon_r5_official/non_portrait_spotlight.png",
  "assets/icons/canon_r5_official/non_portrait_sunset.png",
  "assets/icons/canon_r5_official/non_portrait_with_motion_blue_sky_included.png",
  "assets/icons/canon_r5_official/non_portrait_with_motion_blue_sky_included_backlit.png",
  "assets/icons/canon_r5_official/non_portrait_with_motion_bright.png",
  "assets/icons/canon_r5_official/non_portrait_with_motion_bright_backlit.png",
  "assets/icons/canon_r5_official/one_point_af.svg",
  "assets/icons/canon_r5_official/partial_metering.svg",
  "assets/icons/canon_r5_official/portrait_blue_sky_included.png",
  "assets/icons/canon_r5_official/portrait_blue_sky_included_backlit.png",
  "assets/icons/canon_r5_official/portrait_bright.png",
  "assets/icons/canon_r5_official/portrait_bright_backlit.png",
  "assets/icons/canon_r5_official/portrait_dark.png",
  "assets/icons/canon_r5_official/portrait_dark_tripod_used.png",
  "assets/icons/canon_r5_official/portrait_spotlight.png",
  "assets/icons/canon_r5_official/portrait_with_motion_blue_sky_included.png",
  "assets/icons/canon_r5_official/portrait_with_motion_blue_sky_included_backlit.png",
  "assets/icons/canon_r5_official/portrait_with_motion_bright.png",
  "assets/icons/canon_r5_official/portrait_with_motion_bright_backlit.png",
  "assets/icons/canon_r5_official/quick_control.svg",
  "assets/icons/canon_r5_official/scene_intelligent_auto.svg",
  "assets/icons/canon_r5_official/scene_intelligent_auto_movies.svg",
  "assets/icons/canon_r5_official/self_timer_10_sec_remote_control.svg",
  "assets/icons/canon_r5_official/self_timer_2_sec_remote_control.svg",
  "assets/icons/canon_r5_official/set_af_point_to_center.svg",
  "assets/icons/canon_r5_official/shooting_tab.svg",
  "assets/icons/canon_r5_official/single_shooting.svg",
  "assets/icons/canon_r5_official/spot_af.svg",
  "assets/icons/canon_r5_official/spot_metering.svg",
  "assets/icons/canon_r5_official/still_photo_from_test_shots.svg",
  "assets/icons/canon_r5_official/subject_to_detect_animals.png",
  "assets/icons/canon_r5_official/subject_to_detect_none.png",
  "assets/icons/canon_r5_official/subject_to_detect_people.png",
  "assets/icons/canon_r5_official/subject_to_detect_vehicles.png",
  "assets/icons/canon_r5_official/subject_tracking_adjustment.svg",
  "assets/icons/canon_r5_official/subject_tracking_release.svg",
  "assets/icons/canon_r5_official/timer_6_sec.svg",
  "assets/icons/canon_r5_official/tracking_subject.svg",
  "assets/icons/canon_r5_official/zone_af.svg",
  "icons/apple-touch-icon.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
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
      fetch(request)
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
