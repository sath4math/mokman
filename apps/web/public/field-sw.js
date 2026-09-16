const CACHE_NAME = "mokman-field-v1";
const APP_SHELL = ["/field", "/field-manifest.json"];

// Field Staff PWA only: registered with {scope: "/field/"} from
// app/(field)/layout.tsx, so this never touches owner/tenant/admin.
// Network-first for GETs (so online use always sees fresh data), falling
// back to the last successful response when offline. POSTs are not
// intercepted here — mutation queuing lives in lib/offline-queue.ts
// instead, since Background Sync isn't reliably available everywhere.

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch(() => {}),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request).then((cached) => cached || Response.error())),
  );
});
