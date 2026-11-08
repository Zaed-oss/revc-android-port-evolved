/* Adds the cross-origin-isolation headers that GitHub Pages cannot send,
   so SharedArrayBuffer (threads) works. Registers itself and reloads once. */
if (typeof window === 'undefined') {
  self.addEventListener('install', () => self.skipWaiting());
  self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
  self.addEventListener('fetch', (e) => {
    const r = e.request;
    if (r.cache === 'only-if-cached' && r.mode !== 'same-origin') return;
    e.respondWith(
      fetch(r).then((res) => {
        if (res.status === 0) return res;
        const h = new Headers(res.headers);
        h.set('Cross-Origin-Embedder-Policy', 'require-corp');
        h.set('Cross-Origin-Opener-Policy', 'same-origin');
        h.set('Cross-Origin-Resource-Policy', 'cross-origin');
        return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
      }).catch((err) => console.error(err))
    );
  });
} else {
  (async () => {
    if (window.crossOriginIsolated) return;
    if (!('serviceWorker' in navigator)) return;
    const reg = await navigator.serviceWorker.register(window.document.currentScript.src);
    if (reg.active && !navigator.serviceWorker.controller) { window.location.reload(); return; }
    reg.addEventListener('updatefound', () => window.location.reload());
    if (!reg.active) { navigator.serviceWorker.addEventListener('controllerchange', () => window.location.reload()); }
  })();
}
