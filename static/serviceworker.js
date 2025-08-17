const CACHE_NAME = "timelya-cache-v1";
const urlsToCache = [
    "/",
    "/static/assets/fonts/fontawesome/css/fontawesome-all.min.css",
    "/static/assets/plugins/animation/css/animate.min.css",
    "/static/assets/css/style.css",
    "/static/assets/css/dark.css",
    "/static/assets/js/vendor-all.min.js",
    "/static/assets/plugins/bootstrap/js/bootstrap.min.js",
    "/static/assets/js/pcoded.min.js",
    "/static/assets/js/dark-mode.js",
    "/static/assets/js/datatable-all-option.js",
    "/static/assets/js/bootstrap-notify.js",
    "/static/icons/logo-dark.png",
    "/static/icons/logo-thumb.png"
    // tu peux ajouter d'autres fichiers si nécessaire
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
    );
});
