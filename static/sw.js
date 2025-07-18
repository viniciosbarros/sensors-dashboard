const CACHE_NAME = 'sensor-dashboard-v3';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icon-1000.png',
  '/static/icon-512.png',
  '/static/icon-192.png',
  '/static/icon-1000-round.png',
  '/static/icon-512-round.png',
  '/static/icon-192-round.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
}); 