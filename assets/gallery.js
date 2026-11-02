/* Lightweight zoomable gallery: click/tap to open, wheel/pinch/double-tap zoom, drag to pan,
   swipe or arrow keys for prev/next, Esc to close. No dependencies.
   Markup: <div data-gallery><a href="full.jpg" data-caption="..."><img loading="lazy" ...></a>...</div> */
(function () {
  var groups = document.querySelectorAll('[data-gallery]');
  if (!groups.length) return;
  var css = '.lb{position:fixed;inset:0;z-index:9999;background:#0b0b0b;display:flex;flex-direction:column;color:#f5f5f5;font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;opacity:0;transition:opacity .2s}' +
    '.lb.on{opacity:1}.lb[hidden]{display:none}.lb-stage{position:relative;flex:1;overflow:hidden;touch-action:none;cursor:zoom-in;display:flex;align-items:center;justify-content:center}' +
    '.lb-stage.z{cursor:grab}.lb-stage.z.drag{cursor:grabbing}.lb-stage img{max-width:94vw;max-height:calc(100vh - 120px);width:auto;height:auto;user-select:none;-webkit-user-drag:none;transform-origin:center center;will-change:transform;background:#fff;box-shadow:0 20px 60px rgba(0,0,0,.5)}' +
    '.lb-btn{background:rgba(255,255,255,.08);color:#fff;border:1px solid rgba(255,255,255,.18);width:46px;height:46px;border-radius:50%;font-size:24px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:background .2s}' +
    '.lb-btn:hover,.lb-btn:focus-visible{background:rgba(255,255,255,.2);outline:none}.lb-close{position:absolute;top:16px;right:16px;z-index:2}' +
    '.lb-prev,.lb-next{position:absolute;top:50%;transform:translateY(-50%);z-index:2}.lb-prev{left:16px}.lb-next{right:16px}' +
    '.lb-bar{display:flex;align-items:center;gap:16px;padding:14px 20px;min-height:64px;border-top:1px solid rgba(255,255,255,.1)}.lb-count{opacity:.6;font-variant-numeric:tabular-nums;white-space:nowrap}' +
    '.lb-cap{flex:1;opacity:.85;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.lb-zoom{display:flex;gap:8px;margin-left:auto}.lb-zoom .lb-btn{width:38px;height:38px;font-size:20px}' +
    '@media(max-width:640px){.lb-prev,.lb-next{top:auto;bottom:80px;transform:none}.lb-stage img{max-height:calc(100vh - 150px)}.lb-cap{display:none}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var box, stage, img, capEl, countEl, items = [], idx = 0, s = 1, tx = 0, ty = 0, lastFocus;
  var pts = {}, npts = 0, drag = null, pinch = null, lastTap = 0, moved = false;

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; return e; }
  function build() {
    box = el('div', 'lb'); box.hidden = true;
    box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Image viewer');
    stage = el('div', 'lb-stage'); img = el('img'); img.alt = ''; img.draggable = false; stage.appendChild(img);
    var close = el('button', 'lb-btn lb-close', '&times;'); close.type = 'button'; close.setAttribute('aria-label', 'Close viewer');
    var prev = el('button', 'lb-btn lb-prev', '&#8249;'); prev.type = 'button'; prev.setAttribute('aria-label', 'Previous image');
    var next = el('button', 'lb-btn lb-next', '&#8250;'); next.type = 'button'; next.setAttribute('aria-label', 'Next image');
    var bar = el('div', 'lb-bar'); countEl = el('span', 'lb-count'); capEl = el('span', 'lb-cap');
    var zoom = el('span', 'lb-zoom');
    var zo = el('button', 'lb-btn', '&minus;'); zo.type = 'button'; zo.setAttribute('aria-label', 'Zoom out');
    var zi = el('button', 'lb-btn', '+'); zi.type = 'button'; zi.setAttribute('aria-label', 'Zoom in');
    zoom.appendChild(zo); zoom.appendChild(zi); bar.appendChild(countEl); bar.appendChild(capEl); bar.appendChild(zoom);
    box.appendChild(stage); box.appendChild(close); box.appendChild(prev); box.appendChild(next); box.appendChild(bar);
    document.body.appendChild(box);
    close.onclick = hide; prev.onclick = function () { go(-1); }; next.onclick = function () { go(1); };
    zi.onclick = function () { zoomAt(s * 1.6, 0, 0); }; zo.onclick = function () { zoomAt(s / 1.6, 0, 0); };
    stage.addEventListener('wheel', onWheel, { passive: false });
    stage.addEventListener('pointerdown', onDown); stage.addEventListener('pointermove', onMove);
    stage.addEventListener('pointerup', onUp); stage.addEventListener('pointercancel', onUp);
    stage.addEventListener('dblclick', function (e) { var p = rel(e); zoomAt(s > 1 ? 1 : 2.5, p.x, p.y); });
    document.addEventListener('keydown', function (e) { if (box && !box.hidden) onKey(e); });
  }
  function rel(e) { var r = stage.getBoundingClientRect(); return { x: e.clientX - r.left - r.width / 2, y: e.clientY - r.top - r.height / 2 }; }
  function clamp() {
    var mx = Math.max(0, (img.offsetWidth * s - stage.clientWidth) / 2 + 40), my = Math.max(0, (img.offsetHeight * s - stage.clientHeight) / 2 + 40);
    if (s <= 1) { tx = 0; ty = 0; } else { tx = Math.min(mx, Math.max(-mx, tx)); ty = Math.min(my, Math.max(-my, ty)); }
  }
  function apply(anim) {
    clamp(); img.style.transition = anim ? 'transform .2s ease' : 'none';
    img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
    stage.classList.toggle('z', s > 1);
  }
  function zoomAt(ns, px, py, noAnim) {
    ns = Math.min(6, Math.max(1, ns));
    tx = px - (px - tx) * (ns / s); ty = py - (py - ty) * (ns / s); s = ns; apply(!noAnim);
  }
  function reset() { s = 1; tx = 0; ty = 0; apply(false); }
  function show(i) {
    idx = (i + items.length) % items.length; var it = items[idx];
    reset(); img.src = it.href; img.alt = it.alt; capEl.textContent = it.cap;
    countEl.textContent = (idx + 1) + ' / ' + items.length;
    [1, -1].forEach(function (d) { var n = items[(idx + d + items.length) % items.length]; if (n) { var p = new Image(); p.src = n.href; } });
  }
  function go(d) { if (items.length > 1) show(idx + d); }
  function open(list, i) {
    if (!box) build(); items = list; lastFocus = document.activeElement;
    box.hidden = false; document.documentElement.style.overflow = 'hidden';
    box.querySelector('.lb-prev').hidden = box.querySelector('.lb-next').hidden = list.length < 2;
    show(i); requestAnimationFrame(function () { box.classList.add('on'); }); box.querySelector('.lb-close').focus();
  }
  function hide() {
    box.classList.remove('on'); box.hidden = true; document.documentElement.style.overflow = ''; img.removeAttribute('src');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function onKey(e) {
    var k = e.key;
    if (k === 'Escape') { e.preventDefault(); hide(); }
    else if (k === 'ArrowRight') { e.preventDefault(); go(1); }
    else if (k === 'ArrowLeft') { e.preventDefault(); go(-1); }
    else if (k === '+' || k === '=') { e.preventDefault(); zoomAt(s * 1.4, 0, 0); }
    else if (k === '-' || k === '_') { e.preventDefault(); zoomAt(s / 1.4, 0, 0); }
    else if (k === '0') { e.preventDefault(); reset(); }
    else if (k === 'Tab') {
      var f = [].slice.call(box.querySelectorAll('button:not([hidden])')); if (!f.length) return;
      var a = f.indexOf(document.activeElement);
      if (e.shiftKey && a <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && a === f.length - 1) { e.preventDefault(); f[0].focus(); }
    }
  }
  function onWheel(e) { e.preventDefault(); var p = rel(e); zoomAt(s * Math.exp(-e.deltaY * 0.0015), p.x, p.y, true); }
  function list() { var a = []; for (var k in pts) a.push(pts[k]); return a; }
  function onDown(e) {
    if (e.button && e.button !== 0) return;
    try { stage.setPointerCapture(e.pointerId); } catch (err) {} pts[e.pointerId] = { x: e.clientX, y: e.clientY }; npts++; moved = false;
    if (npts === 1) { drag = { x: e.clientX, y: e.clientY, tx: tx, ty: ty, t: Date.now() }; stage.classList.add('drag'); }
    if (npts === 2) { var p = list(); pinch = { d: dist(p), m: mid(p) }; drag = null; }
  }
  function dist(p) { return Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1; }
  function mid(p) { return rel({ clientX: (p[0].x + p[1].x) / 2, clientY: (p[0].y + p[1].y) / 2 }); }
  function onMove(e) {
    if (!pts[e.pointerId]) return; pts[e.pointerId] = { x: e.clientX, y: e.clientY };
    if (npts === 2 && pinch) {
      var p = list(), d = dist(p), m = mid(p);
      tx += m.x - pinch.m.x; ty += m.y - pinch.m.y; zoomAt(s * d / pinch.d, m.x, m.y, true);
      pinch = { d: d, m: m }; moved = true; return;
    }
    if (drag) {
      var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 6) moved = true;
      if (s > 1) { tx = drag.tx + dx; ty = drag.ty + dy; apply(false); }
      else { img.style.transition = 'none'; img.style.transform = 'translate(' + dx + 'px,0)'; }
    }
  }
  function onUp(e) {
    if (!pts[e.pointerId]) return; delete pts[e.pointerId]; npts = Math.max(0, npts - 1);
    stage.classList.remove('drag');
    if (npts === 1) { pinch = null; var r = list()[0]; drag = { x: r.x, y: r.y, tx: tx, ty: ty, t: Date.now() }; return; }
    if (npts > 0) return;
    pinch = null;
    if (drag) {
      var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (s <= 1 && Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) { go(dx < 0 ? 1 : -1); }
      else if (s <= 1) { apply(true); }
      if (!moved && e.pointerType !== 'mouse') {
        var now = Date.now();
        if (now - lastTap < 300) { var p = rel(e); zoomAt(s > 1 ? 1 : 2.5, p.x, p.y); lastTap = 0; } else lastTap = now;
      } else if (!moved && e.pointerType === 'mouse' && e.target === stage) { hide(); }
    }
    drag = null;
  }
  [].forEach.call(groups, function (g) {
    var links = [].slice.call(g.querySelectorAll('a[href]'));
    var data = links.map(function (a) { var im = a.querySelector('img'); return { href: a.getAttribute('href'), alt: im ? im.alt : '', cap: a.getAttribute('data-caption') || (im ? im.alt : '') }; });
    links.forEach(function (a, i) { a.addEventListener('click', function (e) { if (e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); open(data, i); }); });
  });
})();
