/* CMD Resource Hub Arizona service worker. Written to ../sw.js by build55.py, which stamps
   5ae9bd4d8965 with a hash of the shipped files so every rebuild rolls out as a new cache. */
const VERSION = '5ae9bd4d8965';
const CACHE = 'az-hub-' + VERSION;
const SHELL = [
  './',
  './index.html',
  './offline.html',
  './manifest.webmanifest',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: 'reload' })))));
  // a first install has nothing to replace, so it takes over straight away; an update waits
  // for the page's "Refresh" button (it posts SKIP_WAITING)
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k.startsWith('az-hub-') && k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

/** HTML: network first, then the cached copy, then the offline page. */
async function page(request) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (err) {
    return (await cache.match(request, { ignoreSearch: true })) || (await cache.match('./offline.html'));
  }
}

/** Same-origin files: answer from cache at once and refresh it in the background. */
async function asset(event) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(event.request);
  const update = fetch(event.request).then((res) => {
    if (res.ok) cache.put(event.request, res.clone());
    return res;
  }).catch(() => undefined);
  if (hit) { event.waitUntil(update); return hit; }
  return (await update) || Response.error();
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;   // listings link out to official sites; leave those alone
  if (request.mode === 'navigate' || (request.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(page(request));
  } else {
    event.respondWith(asset(event));
  }
});
