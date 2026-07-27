const VERSION = 'gymsheet-pwa-v1.0.6';
const STATIC_CACHE = `${VERSION}-static`;
const RUNTIME_CACHE = `${VERSION}-runtime`;
const APP_SHELL = [
  './', './index.html', './landing.html', './mie_schede.html', './editor_scheda.html', './converter.html',
  './converter_universale.html', './istruzioni_template.html', './manifest.json',
  './app.js', './db.js', './app.js?v=20260727-1', './db.js?v=20260727-1', './install-app.js', './pwa-register.js', './pwa-bridge.js', './offline.html', './icons/icon-192.png', './icons/icon-512.png',
  './template_scheda.xlsx'
];

const EXTERNAL_ASSETS = [
  'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(STATIC_CACHE).then(cache => Promise.allSettled([...APP_SHELL, ...EXTERNAL_ASSETS].map(asset => cache.add(asset)))));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => ![STATIC_CACHE, RUNTIME_CACHE].includes(key)).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('GymAppDB', 2);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('schede')) db.createObjectStore('schede', { keyPath: 'id' });
      if (!db.objectStoreNames.contains('fileHandles')) db.createObjectStore('fileHandles', { keyPath: 'id' });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function getStoredSheet(id) {
  const db = await openDb();
  try {
    return await new Promise((resolve, reject) => {
      const req = db.transaction('schede', 'readonly').objectStore('schede').get(id);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  } finally { db.close(); }
}

async function serveStoredSheet(url) {
  const match = url.pathname.match(/\/schede\/([^/]+)\.html$/);
  if (!match) return null;
  const record = await getStoredSheet(decodeURIComponent(match[1]));
  if (!record) return new Response('Scheda non trovata', { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  return new Response(record.htmlString, {
    status: 200,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-GymSheet-Source': 'IndexedDB'
    }
  });
}

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin === self.location.origin && /\/schede\/[^/]+\.html$/.test(url.pathname)) {
    event.respondWith(serveStoredSheet(url));
    return;
  }

  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(event.request);
        const cache = await caches.open(RUNTIME_CACHE);
        cache.put(event.request, response.clone());
        return response;
      } catch {
        return (await caches.match(event.request)) || (await caches.match('./index.html')) || (await caches.match('./offline.html'));
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    const network = fetch(event.request).then(async response => {
      if (response.ok || response.type === 'opaque') (await caches.open(RUNTIME_CACHE)).put(event.request, response.clone());
      return response;
    }).catch(() => null);
    return cached || (await network) || new Response('', { status: 504 });
  })());
});
