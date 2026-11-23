// Install-as-app support. The service worker is registered only when the hub is served over
// HTTPS (the published site); opening index.html from disk or in a sandboxed viewer skips it.
(function () {
  if (!('serviceWorker' in navigator) || location.protocol !== 'https:') return;
  var accepted = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (accepted) { accepted = false; location.reload(); }
  });
  function offer(worker) {
    if (document.getElementById('pwaup')) return;
    var box = document.createElement('div');
    box.id = 'pwaup'; box.className = 'pwaup glass'; box.setAttribute('role', 'status');
    var msg = document.createElement('span'); msg.textContent = 'A new version of the hub is available.';
    var go = document.createElement('button'); go.type = 'button'; go.className = 'btn'; go.textContent = 'Refresh';
    var later = document.createElement('button'); later.type = 'button'; later.className = 'btn'; later.textContent = 'Later';
    go.addEventListener('click', function () { accepted = true; go.disabled = true; worker.postMessage({ type: 'SKIP_WAITING' }); });
    later.addEventListener('click', function () { box.remove(); });
    box.append(msg, go, later);
    document.body.appendChild(box);
  }
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').then(function (reg) {
      if (reg.waiting && navigator.serviceWorker.controller) offer(reg.waiting);
      reg.addEventListener('updatefound', function () {
        var w = reg.installing;
        if (w) w.addEventListener('statechange', function () {
          if (w.state === 'installed' && navigator.serviceWorker.controller) offer(w);
        });
      });
      // check for a new version when the app comes back to the foreground
      document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible') reg.update().catch(function () {}); });
    }).catch(function () { /* no offline support in this browser; the hub still works */ });
  });
})();
