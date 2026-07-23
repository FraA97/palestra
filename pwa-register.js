(() => {
  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
    window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js', { scope: './' }).catch(error => console.warn('PWA non registrata', error)));
  }
  if (navigator.storage?.persist) navigator.storage.persist().catch(() => false);
})();
