/* Beheeromgeving Dineren & Slapen.
   Alles wat bezoekers instuurden wordt hier als tekst getoond (nooit als HTML).
   Toegang wordt in de database afgedwongen: alleen ingelogde beheerders kunnen lezen en wijzigen. */
(function () {
  'use strict';
  if (window.top !== window.self) { document.documentElement.textContent = ''; return; }

  var DB_URL = 'https://qxexfrvrondruuheghbp.supabase.co', DB_KEY = 'sb_publishable_inV9HPO2hnCvix9QvG_k4A_YU7ZSMGn', LOC = {"piloersemaborg": {"u": "/groningen/piloersemaborg/", "n": "Piloersemaborg"}, "prinsenhof-groningen": {"u": "/groningen/prinsenhof-groningen/", "n": "Prinsenhof & Restaurant Nassau"}, "herberg-onder-de-linden": {"u": "/groningen/herberg-onder-de-linden/", "n": "Herberg Onder de Linden"}, "restaurant-de-molenaar": {"u": "/groningen/restaurant-de-molenaar/", "n": "Restaurant de Molenaar"}, "landgoed-lauswolt": {"u": "/friesland/landgoed-lauswolt/", "n": "Landgoed Lauswolt"}, "de-hinde-hindeloopen": {"u": "/friesland/de-hinde-hindeloopen/", "n": "De Hinde"}, "herberg-van-smallingerland": {"u": "/friesland/herberg-van-smallingerland/", "n": "De Herberg van Smallingerland"}, "aest-terschelling": {"u": "/friesland/aest-terschelling/", "n": "AEST"}, "rikus-eext": {"u": "/drenthe/rikus-eext/", "n": "Landhuishotel & Restaurant Rikus"}, "chateau-de-havixhorst": {"u": "/drenthe/chateau-de-havixhorst/", "n": "Château De Havixhorst"}, "posten-nordic-cuisine": {"u": "/drenthe/posten-nordic-cuisine/", "n": "POSTEN Nordic Cuisine"}, "de-lindenhof-giethoorn": {"u": "/overijssel/de-lindenhof-giethoorn/", "n": "De Lindenhof"}, "de-bloemenbeek-de-lutte": {"u": "/overijssel/de-bloemenbeek-de-lutte/", "n": "De Bloemenbeek"}, "de-swarte-ruijter-holten": {"u": "/overijssel/de-swarte-ruijter-holten/", "n": "De Swarte Ruijter"}, "de-librije-zwolle": {"u": "/overijssel/de-librije-zwolle/", "n": "De Librije & Librije's Hotel"}, "hotel-restaurant-t-voorhuys": {"u": "/flevoland/hotel-restaurant-t-voorhuys/", "n": "'t Voorhuys"}, "hotel-van-saaze-kraggenburg": {"u": "/flevoland/hotel-van-saaze-kraggenburg/", "n": "Hotel Van Saaze"}, "broederenklooster-zutphen": {"u": "/gelderland/broederenklooster-zutphen/", "n": "Broederenklooster"}, "kasteel-engelenburg": {"u": "/gelderland/kasteel-engelenburg/", "n": "Kasteel Engelenburg"}, "hotel-gastronomique-de-echoput": {"u": "/gelderland/hotel-gastronomique-de-echoput/", "n": "De Echoput"}, "de-nederlanden-vreeland": {"u": "/utrecht/de-nederlanden-vreeland/", "n": "De Nederlanden"}, "parc-broekhuizen-leersum": {"u": "/utrecht/parc-broekhuizen-leersum/", "n": "Parc Broekhuizen"}, "grand-hotel-karel-v-utrecht": {"u": "/utrecht/grand-hotel-karel-v-utrecht/", "n": "Grand Hotel Karel V"}, "de-l-europe-amsterdam": {"u": "/noord-holland/de-l-europe-amsterdam/", "n": "De L'Europe Amsterdam"}, "the-dylan-amsterdam": {"u": "/noord-holland/the-dylan-amsterdam/", "n": "The Dylan Amsterdam"}, "merlet-schoorl": {"u": "/noord-holland/merlet-schoorl/", "n": "Merlet"}, "ml-haarlem": {"u": "/noord-holland/ml-haarlem/", "n": "ML"}, "central-park-voorburg": {"u": "/zuid-holland/central-park-voorburg/", "n": "Central Park Voorburg"}, "de-watergeus-noorden": {"u": "/zuid-holland/de-watergeus-noorden/", "n": "De Watergeus"}, "weeshuis-gouda": {"u": "/zuid-holland/weeshuis-gouda/", "n": "Weeshuis Gouda"}, "de-kromme-watergang-hoofdplaat": {"u": "/zeeland/de-kromme-watergang-hoofdplaat/", "n": "De Kromme Watergang"}, "hof-aan-zee-dishoek": {"u": "/zeeland/hof-aan-zee-dishoek/", "n": "Hof aan Zee"}, "inter-scaldes-kruiningen": {"u": "/zeeland/inter-scaldes-kruiningen/", "n": "Inter Scaldes"}, "hostellerie-schuddebeurs": {"u": "/zeeland/hostellerie-schuddebeurs/", "n": "Hostellerie Schuddebeurs"}, "kasteel-gemert-restaurant-gem": {"u": "/noord-brabant/kasteel-gemert-restaurant-gem/", "n": "Kasteel Gemert & Restaurant GEM."}, "kazerne-eindhoven": {"u": "/noord-brabant/kazerne-eindhoven/", "n": "Kazerne"}, "kasteel-steenenburg": {"u": "/noord-brabant/kasteel-steenenburg/", "n": "Kasteel Steenenburg"}, "van-oys-maastricht-retreat": {"u": "/limburg/van-oys-maastricht-retreat/", "n": "Van Oys Maastricht Retreat"}, "chateau-neercanne": {"u": "/limburg/chateau-neercanne/", "n": "Château Neercanne"}, "chateau-st-gerlach": {"u": "/limburg/chateau-st-gerlach/", "n": "Château St. Gerlach"}, "kasteeltje-hattem": {"u": "/limburg/kasteeltje-hattem/", "n": "Kasteeltje Hattem"}}, SITE = 'https://dinerenenslapen.nl';
  var IDLE_MIN = 30;
  // eigen, onraadbare opslagsleutel per tabblad: andere scripts op dit domein kunnen de sessie zo niet meelezen
  var SK; try { SK = sessionStorage.getItem('dk') || 'sb-' + crypto.randomUUID(); sessionStorage.setItem('dk', SK); } catch (e) { SK = 'sb-' + crypto.randomUUID(); }
  var sb = window.supabase.createClient(DB_URL, DB_KEY, {
    auth: { storage: window.sessionStorage, storageKey: SK, persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: 'implicit' }
  });

  var $ = function (id) { return document.getElementById(id); };
  var S = { reviews: [], messages: [], subscribers: [], tab: 'overzicht', rv: 'nieuw', ms: 'nieuw', mk: 'alle', sbs: 'actief', sbp: 'alle', loaded: false, recovering: /type=recovery/.test(location.hash) };

  /* ---------- kleine hulpjes ---------- */
  function el(tag, attrs) {
    var n = document.createElement(tag), i, k;
    if (attrs) for (k in attrs) {
      var v = attrs[k];
      if (v == null || v === false) continue;
      if (k === 'text') n.textContent = v;
      else if (k === 'class') n.className = v;
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : v);
    }
    for (i = 2; i < arguments.length; i++) {
      var c = arguments[i];
      if (c == null || c === false) continue;
      if (Array.isArray(c)) c.forEach(function (x) { if (x) n.appendChild(typeof x === 'string' ? document.createTextNode(x) : x); });
      else n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return n;
  }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }
  var MND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
  function dt(s) { var d = new Date(s); return d.getDate() + ' ' + MND[d.getMonth()] + ' ' + d.getFullYear() + ', ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  function dshort(s) { var d = new Date(s), now = new Date(); return d.getDate() + ' ' + MND[d.getMonth()] + (d.getFullYear() !== now.getFullYear() ? ' ' + d.getFullYear() : ''); }
  function month(m) { if (!m) return ''; var p = m.split('-'); return MND[+p[1] - 1] + ' ' + p[0]; }
  function safeMail(m) { return /^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/.test(m || '') ? m : null; }
  function locOf(id) { return Object.prototype.hasOwnProperty.call(LOC, id) ? LOC[id] : null; }
  function toast(t) { var x = $('toast'); x.textContent = t; x.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(function () { x.hidden = true; }, 3200); }
  function fail(e) { console.error(e); toast('Dat lukte niet: ' + ((e && e.message) || 'onbekende fout') + '. Probeer het opnieuw.'); }
  function pill(s) { return el('span', { class: 'pill ' + s, text: { nieuw: 'Nieuw', goedgekeurd: 'Goedgekeurd', afgewezen: 'Afgewezen', beantwoord: 'Beantwoord', gearchiveerd: 'Gearchiveerd', actief: 'Actief', afgemeld: 'Afgemeld', tip: 'Tip', contact: 'Contact' }[s] || s }); }
  function confirmBtn(label, cls, run) {
    var b = el('button', { type: 'button', class: cls, text: label });
    b.addEventListener('click', function () {
      if (b.dataset.armed) { run(b); return; }
      b.dataset.armed = '1'; b.textContent = 'Zeker weten? Klik nog een keer';
      setTimeout(function () { delete b.dataset.armed; b.textContent = label; }, 4000);
    });
    return b;
  }

  /* ---------- inloggen ---------- */
  function box(id) { ['box-login', 'box-mfa', 'box-enroll', 'box-reset'].forEach(function (b) { $(b).hidden = b !== id; }); }
  function showLogin(msg, good) {
    $('app').hidden = true; $('who').hidden = true; $('login').hidden = false;
    box(S.recovering ? 'box-reset' : 'box-login');
    var m = $('l-msg'); m.hidden = !msg; m.textContent = msg || ''; m.className = 'msg' + (good ? ' good' : '');
  }
  $('f-login').addEventListener('submit', function (e) {
    e.preventDefault();
    var b = e.target.querySelector('button'); b.disabled = true;
    sb.auth.signInWithPassword({ email: $('l-mail').value.trim(), password: $('l-pass').value }).then(function (r) {
      b.disabled = false; $('l-pass').value = '';
      if (r.error) showLogin(/invalid/i.test(r.error.message) ? 'E-mailadres of wachtwoord klopt niet.' : r.error.message);
    });
  });
  $('l-forgot').addEventListener('click', function () {
    var m = $('l-mail').value.trim();
    if (!m) { showLogin('Vul eerst je e-mailadres in, en klik dan nog een keer op Wachtwoord vergeten.'); $('l-mail').focus(); return; }
    sb.auth.resetPasswordForEmail(m, { redirectTo: SITE + '/admin/' }).then(function () {
      showLogin('Als dit adres bij ons bekend is, staat er nu een mail klaar met een link om een nieuw wachtwoord te kiezen.', true);
    });
  });
  $('f-reset').addEventListener('submit', function (e) {
    e.preventDefault();
    var a = $('r-pass').value, b = $('r-pass2').value, m = $('r-msg');
    if (a.length < 12) { m.hidden = false; m.textContent = 'Kies minstens 12 tekens.'; return; }
    if (a !== b) { m.hidden = false; m.textContent = 'De twee wachtwoorden zijn niet hetzelfde.'; return; }
    sb.auth.updateUser({ password: a }).then(function (r) {
      if (r.error) { m.hidden = false; m.textContent = r.error.message; return; }
      S.recovering = false; $('r-pass').value = $('r-pass2').value = '';
      sb.auth.signOut({ scope: 'global' }).then(function () { showLogin('Je nieuwe wachtwoord is opgeslagen. Log nu in met je nieuwe wachtwoord.', true); });
    });
  });
  function logout() { sb.auth.signOut().then(function () { showLogin('Je bent uitgelogd.', true); }); }
  $('logout').addEventListener('click', logout);
  document.querySelectorAll('[data-logout]').forEach(function (b) { b.addEventListener('click', logout); });

  /* ---------- tweede stap: code uit een authenticator-app ---------- */
  function codeMsg(id, t) { var m = $(id); m.hidden = !t; m.textContent = t || ''; }
  function showMfa() { $('login').hidden = false; box('box-mfa'); codeMsg('m-msg'); $('m-code').value = ''; $('m-code').focus(); }
  function showEnroll() {
    $('login').hidden = false; box('box-enroll'); codeMsg('e-msg');
    sb.auth.mfa.listFactors().then(function (f) {
      var old = ((f.data && f.data.all) || []).filter(function (x) { return x.status !== 'verified'; });
      return Promise.all(old.map(function (x) { return sb.auth.mfa.unenroll({ factorId: x.id }); }));
    }).then(function () {
      return sb.auth.mfa.enroll({ factorType: 'totp', friendlyName: 'Dineren en Slapen beheer', issuer: 'Dineren & Slapen' });
    }).then(function (r) {
      if (r.error) { codeMsg('e-msg', r.error.message); return; }
      S.enroll = r.data.id; $('e-qr').src = qrSrc(r.data.totp.qr_code); $('e-secret').textContent = r.data.totp.secret; $('e-code').focus();
    });
  }
  function qrSrc(q) {
    q = String(q || '');
    if (q.indexOf('data:image/svg+xml') !== 0) return q;
    var svg = q.slice(q.indexOf(',') + 1);
    try { if (/%3C/i.test(svg)) svg = decodeURIComponent(svg); } catch (e) {}
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }
  function verify(factorId, code, msgId, btn) {
    btn.disabled = true;
    sb.auth.mfa.challengeAndVerify({ factorId: factorId, code: code }).then(function (r) {
      btn.disabled = false;
      if (r.error) { codeMsg(msgId, 'Die code klopt niet of is verlopen. Probeer de code die de app nu laat zien.'); return; }
      start();
    });
  }
  $('f-mfa').addEventListener('submit', function (e) {
    e.preventDefault();
    var code = $('m-code').value.trim(), btn = e.target.querySelector('button');
    sb.auth.mfa.listFactors().then(function (f) { var t = (f.data && f.data.totp || [])[0]; if (!t) { showEnroll(); return; } verify(t.id, code, 'm-msg', btn); });
  });
  $('f-enroll').addEventListener('submit', function (e) {
    e.preventDefault();
    if (!S.enroll) return;
    verify(S.enroll, $('e-code').value.trim(), 'e-msg', e.target.querySelector('button'));
  });

  var idleT;
  function idle() { clearTimeout(idleT); idleT = setTimeout(function () { sb.auth.signOut().then(function () { showLogin('Je bent automatisch uitgelogd na ' + IDLE_MIN + ' minuten zonder activiteit.', true); }); }, IDLE_MIN * 60000); }
  ['click', 'keydown', 'scroll', 'pointermove'].forEach(function (ev) { document.addEventListener(ev, function () { if (!$('app').hidden) idle(); }, { passive: true }); });

  function start() {
    sb.auth.getSession().then(function (r) {
      var s = r.data && r.data.session;
      if (!s) { showLogin(); return; }
      if (S.recovering) { showLogin(); return; }
      sb.auth.mfa.getAuthenticatorAssuranceLevel().then(function (l) {
        var lv = l.data || {};
        if (lv.currentLevel !== 'aal2') { if (lv.nextLevel === 'aal2') showMfa(); else showEnroll(); return; }
        admitted(s);
      });
    });
  }
  function admitted(s) {
    sb.rpc('is_admin').then(function (a) {
      if (a.error || a.data !== true) { sb.auth.signOut(); showLogin('Dit account heeft geen toegang tot de beheeromgeving.'); return; }
      $('login').hidden = true; $('app').hidden = false; $('who').hidden = false; $('who-mail').textContent = s.user.email;
      idle(); load();
    });
  }
  sb.auth.onAuthStateChange(function (ev) {
    if (ev === 'PASSWORD_RECOVERY') { S.recovering = true; showLogin(); return; }
    if (ev === 'SIGNED_IN' && !S.loaded && !S.recovering && $('box-mfa').hidden && $('box-enroll').hidden) start();
    if (ev === 'SIGNED_OUT') { S.loaded = false; S.reviews = []; S.messages = []; S.subscribers = []; }
  });

  /* ---------- gegevens: in porties van 500, zodat er nooit stil rijen wegvallen ---------- */
  function all(t) {
    var out = [];
    function pg(f) {
      return sb.from(t).select('*').order('created_at', { ascending: false }).order('id').range(f, f + 499).then(function (r) {
        if (r.error) return r;
        out = out.concat(r.data);
        return r.data.length < 500 ? { data: out } : pg(f + 500);
      });
    }
    return pg(0);
  }
  function load() {
    $('refresh').disabled = true;
    Promise.all([all('reviews'), all('messages'), all('subscribers')]).then(function (r) {
      $('refresh').disabled = false;
      var err = r.filter(function (x) { return x.error; })[0];
      if (err) { fail(err.error); return; }
      S.reviews = r[0].data; S.messages = r[1].data; S.subscribers = r[2].data; S.loaded = true;
      var d = new Date(); $('stamp').textContent = 'Bijgewerkt om ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
      render();
    }, function (e) { $('refresh').disabled = false; fail(e); });
  }
  $('refresh').addEventListener('click', load);
  setInterval(function () { if (!$('app').hidden && document.visibilityState === 'visible') load(); }, 120000);

  function update(table, row, patch, msg) {
    return sb.from(table).update(patch).eq('id', row.id).then(function (r) {
      if (r.error) return fail(r.error);
      for (var k in patch) row[k] = patch[k];
      if (msg) toast(msg); render();
    });
  }
  function remove(table, row, msg) {
    return sb.from(table).delete().eq('id', row.id).then(function (r) {
      if (r.error) return fail(r.error);
      S[table] = S[table].filter(function (x) { return x.id !== row.id; }); toast(msg); render();
    });
  }
  function noteBox(table, row) {
    var ta = el('textarea', { 'aria-label': 'Interne notitie', placeholder: 'Interne notitie, alleen voor jezelf', maxlength: '1000' });
    ta.value = row.note || '';
    var b = el('button', { type: 'button', class: 'btn ghost', text: 'Notitie opslaan', onclick: function () { update(table, row, { note: ta.value.trim() || null }, 'Notitie opgeslagen.'); } });
    return el('div', { class: 'note' }, ta, b);
  }

  /* ---------- tabs ---------- */
  document.querySelectorAll('.tab').forEach(function (t) { t.addEventListener('click', function () { go(t.dataset.tab); }); });
  function go(tab, sub) {
    S.tab = tab;
    if (sub) { if (tab === 'reviews') S.rv = sub; if (tab === 'berichten') S.ms = sub; if (tab === 'nieuwsbrief') S.sbs = sub; }
    document.querySelectorAll('.tab').forEach(function (t) { t.classList.toggle('on', t.dataset.tab === tab); t.setAttribute('aria-current', t.dataset.tab === tab ? 'page' : 'false'); });
    document.querySelectorAll('.view').forEach(function (v) { v.hidden = v.id !== 'v-' + tab; });
    render(); window.scrollTo(0, 0);
  }
  function seg(box, opts, cur, set) {
    clear(box);
    opts.forEach(function (o) { box.appendChild(el('button', { type: 'button', class: o[0] === cur ? 'on' : '', 'aria-pressed': String(o[0] === cur), text: o[1], onclick: function () { set(o[0]); render(); } })); });
  }
  function q(id) { return ($(id).value || '').trim().toLowerCase(); }
  ['rv-q', 'ms-q', 'sb-q'].forEach(function (id) { $(id).addEventListener('input', function () { render(); }); });

  function render() {
    if (!S.loaded) return;
    var nr = S.reviews.filter(function (r) { return r.status === 'nieuw'; }).length;
    var nm = S.messages.filter(function (r) { return r.status === 'nieuw'; }).length;
    var act = S.subscribers.filter(function (r) { return r.status === 'actief'; }).length;
    $('b-reviews').hidden = !nr; $('b-reviews').textContent = nr;
    $('b-berichten').hidden = !nm; $('b-berichten').textContent = nm;
    $('b-nieuwsbrief').textContent = act;
    document.title = (nr + nm ? '(' + (nr + nm) + ') ' : '') + 'Beheer | Dineren & Slapen';
    ({ overzicht: overview, reviews: reviews, berichten: messages, nieuwsbrief: subscribers })[S.tab](nr, nm, act);
  }

  /* ---------- overzicht ---------- */
  function overview(nr, nm, act) {
    var since = Date.now() - 30 * 864e5;
    var new30 = S.subscribers.filter(function (r) { return new Date(r.created_at) > since; }).length;
    var tiles = clear($('tiles'));
    [[nr, 'Reviews te beoordelen', nr ? 'Klik om ze te bekijken' : 'Alles is beoordeeld', 'reviews', 'nieuw', nr > 0],
     [nm, 'Nieuwe berichten', nm ? 'Contact en tips' : 'Geen openstaande berichten', 'berichten', 'nieuw', nm > 0],
     [act, 'Abonnees op de nieuwsbrief', 'Actief ingeschreven', 'nieuwsbrief', 'actief', false],
     [new30, 'Nieuwe abonnees', 'In de afgelopen 30 dagen', 'nieuwsbrief', 'actief', false]].forEach(function (t) {
      tiles.appendChild(el('button', { type: 'button', class: 'tile' + (t[5] ? ' alert' : ''), onclick: function () { go(t[3], t[4]); } }, el('b', { text: String(t[0]) }), el('span', { text: t[1] }), el('small', { text: t[2] })));
    });
    // abonnees per week
    var ch = clear($('chart')), weeks = [], now = new Date(); now.setHours(0, 0, 0, 0);
    var mon = new Date(now); mon.setDate(mon.getDate() - ((mon.getDay() + 6) % 7));
    for (var i = 11; i >= 0; i--) { var a = new Date(mon); a.setDate(a.getDate() - 7 * i); weeks.push({ a: a, n: 0 }); }
    S.subscribers.forEach(function (r) { var d = new Date(r.created_at); for (var j = weeks.length - 1; j >= 0; j--) if (d >= weeks[j].a) { weeks[j].n++; break; } });
    var mx = Math.max.apply(null, weeks.map(function (w) { return w.n; }).concat([1]));
    weeks.forEach(function (w) {
      var bar = el('i'); bar.style.height = Math.max(2, Math.round(w.n / mx * 120)) + 'px';
      ch.appendChild(el('div', { class: 'b', title: 'Week van ' + dshort(w.a) + ': ' + w.n }, el('em', { text: w.n ? String(w.n) : '' }), bar, el('span', { text: w.a.getDate() + ' ' + MND[w.a.getMonth()] })));
    });
    // recent
    var all = [];
    S.reviews.forEach(function (r) { var L0 = locOf(r.loc_id); all.push({ d: r.created_at, k: 'Review', t: (L0 ? L0.n : 'Onbekend adres') + ': ' + r.name, go: ['reviews', r.status] }); });
    S.messages.forEach(function (r) { all.push({ d: r.created_at, k: r.kind === 'tip' ? 'Tip' : 'Contact', t: r.kind === 'tip' ? (r.address_name + (r.address_place ? ', ' + r.address_place : '')) : ((r.subject || 'Bericht') + (r.name ? ' van ' + r.name : '')), go: ['berichten', r.status] }); });
    S.subscribers.forEach(function (r) { all.push({ d: r.created_at, k: 'Abonnee', t: r.email + (r.province ? ' (' + provName(r.province) + ')' : ''), go: ['nieuwsbrief', r.status] }); });
    all.sort(function (a, b) { return a.d < b.d ? 1 : -1; });
    var ul = clear($('recent'));
    if (!all.length) ul.appendChild(el('li', { class: 'empty', text: 'Nog niets binnengekomen. Zodra iemand een formulier op de site invult, zie je het hier.' }));
    all.slice(0, 10).forEach(function (x) { ul.appendChild(el('li', null, el('button', { type: 'button', onclick: function () { go(x.go[0], x.go[1]); } }, el('span', { class: 'd', text: x.k }), el('span', { class: 't', text: x.t }), el('span', { class: 'd', text: dshort(x.d) })))); });
  }

  /* ---------- reviews ---------- */
  function reviews() {
    var cnt = function (s) { return S.reviews.filter(function (r) { return s === 'alle' || r.status === s; }).length; };
    seg($('rv-seg'), [['nieuw', 'Te beoordelen (' + cnt('nieuw') + ')'], ['goedgekeurd', 'Goedgekeurd (' + cnt('goedgekeurd') + ')'], ['afgewezen', 'Afgewezen (' + cnt('afgewezen') + ')'], ['alle', 'Alles']], S.rv, function (v) { S.rv = v; });
    var qq = q('rv-q');
    var rows = S.reviews.filter(function (r) { return (S.rv === 'alle' || r.status === S.rv) && (!qq || ((locOf(r.loc_id) || {}).n + ' ' + r.name + ' ' + r.body + ' ' + (r.email || '')).toLowerCase().indexOf(qq) >= 0); });
    var box = clear($('rv-list'));
    if (!rows.length) { box.appendChild(el('p', { class: 'empty', text: S.rv === 'nieuw' ? 'Er wachten geen reviews op je oordeel.' : 'Geen reviews in deze selectie.' })); return; }
    rows.forEach(function (r) {
      var L0 = locOf(r.loc_id), url = L0 && L0.u, mail = safeMail(r.email), avg = ((r.score_e + r.score_s + r.score_p) / 3).toFixed(1).replace('.', ',');
      var acts = el('div', { class: 'acts' });
      if (r.status !== 'goedgekeurd') acts.appendChild(el('button', { type: 'button', class: 'btn ok', text: r.status === 'afgewezen' ? 'Toch goedkeuren' : 'Goedkeuren en plaatsen', onclick: function () { update('reviews', r, { status: 'goedgekeurd', reviewed_at: new Date().toISOString() }, 'Goedgekeurd. De review staat nu op de site.'); } }));
      if (r.status !== 'afgewezen') acts.appendChild(el('button', { type: 'button', class: 'btn no', text: r.status === 'goedgekeurd' ? 'Offline halen en afwijzen' : 'Afwijzen', onclick: function () { update('reviews', r, { status: 'afgewezen', reviewed_at: new Date().toISOString() }, 'Afgewezen. De review komt niet op de site.'); } }));
      if (r.status !== 'nieuw') acts.appendChild(el('button', { type: 'button', class: 'link', text: 'Terug naar te beoordelen', onclick: function () { update('reviews', r, { status: 'nieuw', reviewed_at: null }, 'Teruggezet.'); } }));
      if (url) acts.appendChild(el('a', { class: 'link', href: SITE + url + '#reviews', target: '_blank', rel: 'noopener noreferrer', text: 'Bekijk de pagina' }));
      acts.appendChild(el('span', { class: 'grow' }));
      acts.appendChild(confirmBtn('Verwijderen', 'link del', function () { remove('reviews', r, 'Review verwijderd.'); }));
      box.appendChild(el('article', { class: 'card s-' + r.status },
        el('div', { class: 'ch' }, el('h3', null, L0 ? el('a', { href: SITE + url, target: '_blank', rel: 'noopener noreferrer', text: L0.n }) : 'Onbekend adres'), pill(r.status)),
        L0 && L0.n !== r.loc_name ? el('p', { class: 'warn', text: 'Let op: de inzender noemde dit adres "' + r.loc_name + '". De review komt bij ' + L0.n + ' te staan.' }) : null,
        el('div', { class: 'meta' }, el('span', { text: 'Door ' + r.name }), r.visit_month ? el('span', { text: 'Bezocht in ' + month(r.visit_month) }) : null, el('span', { text: 'Ingestuurd ' + dt(r.created_at) }), r.lang === 'en' ? el('span', { text: 'Engelstalige pagina' }) : null,
          mail ? el('a', { href: 'mailto:' + mail + '?subject=' + encodeURIComponent('Je review van ' + r.loc_name), text: mail }) : el('span', { text: 'Geen e-mailadres' })),
        el('div', { class: 'scores' }, el('span', null, 'Eten', el('b', { text: String(r.score_e) })), el('span', null, 'Slapen', el('b', { text: String(r.score_s) })), el('span', null, 'Prijs', el('b', { text: String(r.score_p) })), el('span', null, 'Gemiddeld', el('b', { text: avg }))),
        el('p', { class: 'body', text: r.body }),
        noteBox('reviews', r), acts));
    });
  }

  /* ---------- berichten ---------- */
  function messages() {
    var cnt = function (s) { return S.messages.filter(function (r) { return (s === 'alle' || r.status === s) && (S.mk === 'alle' || r.kind === S.mk); }).length; };
    seg($('ms-seg'), [['nieuw', 'Nieuw (' + cnt('nieuw') + ')'], ['beantwoord', 'Beantwoord (' + cnt('beantwoord') + ')'], ['gearchiveerd', 'Archief (' + cnt('gearchiveerd') + ')'], ['alle', 'Alles']], S.ms, function (v) { S.ms = v; });
    seg($('ms-kind'), [['alle', 'Contact en tips'], ['contact', 'Contact'], ['tip', 'Tips']], S.mk, function (v) { S.mk = v; });
    var qq = q('ms-q');
    var rows = S.messages.filter(function (r) { return (S.ms === 'alle' || r.status === S.ms) && (S.mk === 'alle' || r.kind === S.mk) && (!qq || [r.name, r.email, r.subject, r.address_name, r.address_place, r.province, r.body].join(' ').toLowerCase().indexOf(qq) >= 0); });
    var box = clear($('ms-list'));
    if (!rows.length) { box.appendChild(el('p', { class: 'empty', text: S.ms === 'nieuw' ? 'Geen nieuwe berichten. Alles is bijgewerkt.' : 'Geen berichten in deze selectie.' })); return; }
    rows.forEach(function (r) {
      var mail = safeMail(r.email), tip = r.kind === 'tip';
      var title = tip ? 'Tip: ' + r.address_name + (r.address_place ? ', ' + r.address_place : '') : (r.subject || 'Bericht');
      var acts = el('div', { class: 'acts' });
      if (mail) acts.appendChild(el('a', { class: 'btn', href: 'mailto:' + mail + '?subject=' + encodeURIComponent('Re: ' + (tip ? 'je tip ' + r.address_name : (r.subject || 'je bericht')) + ' | Dineren & Slapen'), text: 'Beantwoorden per mail' }));
      if (r.status !== 'beantwoord') acts.appendChild(el('button', { type: 'button', class: 'btn ok', text: tip ? 'Afgehandeld' : 'Markeer als beantwoord', onclick: function () { update('messages', r, { status: 'beantwoord', handled_at: new Date().toISOString() }, 'Gemarkeerd als afgehandeld.'); } }));
      if (r.status !== 'gearchiveerd') acts.appendChild(el('button', { type: 'button', class: 'btn ghost', text: 'Archiveren', onclick: function () { update('messages', r, { status: 'gearchiveerd', handled_at: r.handled_at || new Date().toISOString() }, 'Gearchiveerd.'); } }));
      if (r.status !== 'nieuw') acts.appendChild(el('button', { type: 'button', class: 'link', text: 'Terug naar nieuw', onclick: function () { update('messages', r, { status: 'nieuw', handled_at: null }, 'Teruggezet naar nieuw.'); } }));
      acts.appendChild(el('span', { class: 'grow' }));
      acts.appendChild(confirmBtn('Verwijderen', 'link del', function () { remove('messages', r, 'Bericht verwijderd.'); }));
      box.appendChild(el('article', { class: 'card s-' + r.status },
        el('div', { class: 'ch' }, el('h3', { text: title }), el('span', null, pill(r.kind), ' ', pill(r.status))),
        el('div', { class: 'meta' }, r.name ? el('span', { text: 'Van ' + r.name }) : null, mail ? el('a', { href: 'mailto:' + mail, text: mail }) : el('span', { text: 'Geen e-mailadres' }), tip && r.province ? el('span', { text: r.province }) : null, el('span', { text: dt(r.created_at) }), r.page ? el('span', { text: 'Via ' + r.page }) : null),
        r.body ? el('p', { class: 'body', text: r.body }) : el('p', { class: 'muted', text: 'Geen toelichting meegestuurd.' }),
        noteBox('messages', r), acts));
    });
  }

  /* ---------- nieuwsbrief ---------- */
  var PROV = [['groningen', 'Groningen'], ['friesland', 'Friesland'], ['drenthe', 'Drenthe'], ['overijssel', 'Overijssel'], ['flevoland', 'Flevoland'], ['gelderland', 'Gelderland'],
    ['utrecht', 'Utrecht'], ['noord-holland', 'Noord-Holland'], ['zuid-holland', 'Zuid-Holland'], ['zeeland', 'Zeeland'], ['noord-brabant', 'Noord-Brabant'], ['limburg', 'Limburg'], ['geen', 'Geen voorkeur']];
  function provName(v) { for (var i = 0; i < PROV.length; i++) if (PROV[i][0] === v) return PROV[i][1]; return v ? v : 'Niet ingevuld'; }
  (function () {
    var sel = $('sb-prov');
    sel.appendChild(el('option', { value: 'alle', text: 'Alle provincies' }));
    PROV.forEach(function (p) { sel.appendChild(el('option', { value: p[0], text: p[1] })); });
    sel.appendChild(el('option', { value: 'leeg', text: 'Niet ingevuld' }));
    sel.addEventListener('change', function () { S.sbp = sel.value; render(); });
  })();
  function subRows() {
    var qq = q('sb-q');
    return S.subscribers.filter(function (r) { return (S.sbs === 'alle' || r.status === S.sbs) && (S.sbp === 'alle' || (S.sbp === 'leeg' ? !r.province : r.province === S.sbp)) && (!qq || r.email.indexOf(qq) >= 0 || (r.source || '').toLowerCase().indexOf(qq) >= 0 || provName(r.province).toLowerCase().indexOf(qq) >= 0); });
  }
  function subscribers() {
    var cnt = function (s) { return S.subscribers.filter(function (r) { return s === 'alle' || r.status === s; }).length; };
    seg($('sb-seg'), [['actief', 'Actief (' + cnt('actief') + ')'], ['afgemeld', 'Afgemeld (' + cnt('afgemeld') + ')'], ['alle', 'Alles (' + cnt('alle') + ')']], S.sbs, function (v) { S.sbs = v; });
    var rows = subRows(), tb = clear($('sb-rows'));
    if (!rows.length) tb.appendChild(el('tr', null, el('td', { colspan: '7', class: 'muted', text: 'Geen abonnees in deze selectie.' })));
    rows.forEach(function (r) {
      var act = el('td');
      act.appendChild(el('button', { type: 'button', class: 'link', text: r.status === 'actief' ? 'Afmelden' : 'Weer actief', onclick: function () { update('subscribers', r, r.status === 'actief' ? { status: 'afgemeld', unsubscribed_at: new Date().toISOString() } : { status: 'actief', unsubscribed_at: null }, r.status === 'actief' ? 'Afgemeld.' : 'Weer actief.'); } }));
      act.appendChild(document.createTextNode('  '));
      act.appendChild(confirmBtn('Verwijderen', 'link del', function () { remove('subscribers', r, 'Adres verwijderd.'); }));
      tb.appendChild(el('tr', null, el('td', { text: r.email }), el('td', { class: r.province ? '' : 'muted', text: provName(r.province) }), el('td', { text: dshort(r.created_at) }), el('td', { text: r.source || '' }), el('td', { text: r.lang === 'en' ? 'Engels' : 'Nederlands' }), el('td', null, pill(r.status)), act));
    });
    $('sb-foot').textContent = rows.length + (rows.length === 1 ? ' adres' : ' adressen') + ' in deze selectie.';
    $('sb-prov').value = S.sbp;
    // actieve abonnees per voorkeursprovincie; klik filtert de lijst
    var pc = clear($('sb-provs')), act = S.subscribers.filter(function (r) { return r.status === 'actief'; });
    var cnts = PROV.concat([['leeg', 'Niet ingevuld']]).map(function (p) { return [p[0], p[1], act.filter(function (r) { return p[0] === 'leeg' ? !r.province : r.province === p[0]; }).length]; })
      .filter(function (c) { return c[2] > 0 || c[0] !== 'leeg'; }).sort(function (a, b) { return b[2] - a[2]; });
    var mx = Math.max.apply(null, cnts.map(function (c) { return c[2]; }).concat([1]));
    cnts.forEach(function (c) {
      var bar = el('i'); bar.style.width = Math.round(c[2] / mx * 100) + '%';
      pc.appendChild(el('button', { type: 'button', class: 'pv' + (S.sbp === c[0] ? ' on' : ''), 'aria-pressed': String(S.sbp === c[0]), title: 'Toon alleen ' + c[1], onclick: function () { S.sbp = S.sbp === c[0] ? 'alle' : c[0]; render(); } },
        el('span', { text: c[1] }), el('span', { class: 'track' }, bar), el('b', { text: String(c[2]) })));
    });
  }
  function activeInView() { return subRows().filter(function (r) { return r.status === 'actief'; }); }
  $('sb-csv').addEventListener('click', function () {
    var rows = activeInView();
    if (!rows.length) { toast('Er zijn geen actieve abonnees in deze selectie.'); return; }
    var esc = function (s) { s = String(s == null ? '' : s); if (/^[=+\-@\s]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
    var csv = '﻿email;provincie;ingeschreven;pagina;taal\r\n' + rows.map(function (r) { return [r.email, provName(r.province), r.created_at.slice(0, 10), r.source, r.lang].map(esc).join(';'); }).join('\r\n');
    var url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    var a = el('a', { href: url, download: 'nieuwsbrief-abonnees-' + (S.sbp !== 'alle' ? S.sbp + '-' : '') + new Date().toISOString().slice(0, 10) + '.csv' });
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
    toast(rows.length + ' adressen gedownload.');
  });
  $('sb-copy').addEventListener('click', function () {
    var rows = activeInView();
    if (!rows.length) { toast('Er zijn geen actieve abonnees in deze selectie.'); return; }
    navigator.clipboard.writeText(rows.map(function (r) { return r.email; }).join('\n')).then(function () { toast(rows.length + ' adressen gekopieerd.'); }, function () { toast('Kopiëren lukte niet in deze browser. Gebruik de CSV.'); });
  });

  start();
})();
