const CACHE_NAME = 'venone-cache'

const urlsToCache = [
    '/',
    '/static/css/admin.css',
    '/static/css/style.css',
    '/static/js/admin.js'
]

self.addEventListener('install', function (e) {
    e.waitUntil(
        caches.open('CACHE_NAME')
            .then(function (cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request)
            .then(function (response) {
                if (response) {
                    return response
                }
                return fetch(event.request)
            })
    )

});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME
                }).map(function(cacheName) {
                    return caches.delete(cacheName)
                })
            );
        })
    )
});
