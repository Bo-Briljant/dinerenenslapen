/* Beheeromgeving Dineren & Slapen.
   Alles wat bezoekers instuurden wordt hier als tekst getoond (nooit als HTML).
   Toegang wordt in de database afgedwongen: alleen ingelogde beheerders kunnen lezen en wijzigen. */
(function () {
  'use strict';
  if (window.top !== window.self) { document.documentElement.textContent = ''; return; }

  var DB_URL = 'https://qxexfrvrondruuheghbp.supabase.co', DB_KEY = 'sb_publishable_inV9HPO2hnCvix9QvG_k4A_YU7ZSMGn', LOC = {"piloersemaborg": "/groningen/piloersemaborg/", "prinsenhof-groningen": "/groningen/prinsenhof-groningen/", "herberg-onder-de-linden": "/groningen/herberg-onder-de-linden/", "restaurant-de-molenaar": "/groningen/restaurant-de-molenaar/", "landgoed-lauswolt": "/friesland/landgoed-lauswolt/", "de-hinde-hindeloopen": "/friesland/de-hinde-hindeloopen/", "herberg-van-smallingerland": "/friesland/herberg-van-smallingerland/", "aest-terschelling": "/friesland/aest-terschelling/", "rikus-eext": "/drenthe/rikus-eext/", "chateau-de-havixhorst": "/drenthe/chateau-de-havixhorst/", "posten-nordic-cuisine": "/drenthe/posten-nordic-cuisine/", "de-lindenhof-giethoorn": "/overijssel/de-lindenhof-giethoorn/", "de-bloemenbeek-de-lutte": "/overijssel/de-bloemenbeek-de-lutte/", "de-swarte-ruijter-holten": "/overijssel/de-swarte-ruijter-holten/", "de-librije-zwolle": "/overijssel/de-librije-zwolle/", "hotel-restaurant-t-voorhuys": "/flevoland/hotel-restaurant-t-voorhuys/", "hotel-van-saaze-kraggenburg": "/flevoland/hotel-van-saaze-kraggenburg/", "broederenklooster-zutphen": "/gelderland/broederenklooster-zutphen/", "kasteel-engelenburg": "/gelderland/kasteel-engelenburg/", "hotel-gastronomique-de-echoput": "/gelderland/hotel-gastronomique-de-echoput/", "de-nederlanden-vreeland": "/utrecht/de-nederlanden-vreeland/", "parc-broekhuizen-leersum": "/utrecht/parc-broekhuizen-leersum/", "grand-hotel-karel-v-utrecht": "/utrecht/grand-hotel-karel-v-utrecht/", "de-l-europe-amsterdam": "/noord-holland/de-l-europe-amsterdam/", "the-dylan-amsterdam": "/noord-holland/the-dylan-amsterdam/", "merlet-schoorl": "/noord-holland/merlet-schoorl/", "ml-haarlem": "/noord-holland/ml-haarlem/", "central-park-voorburg": "/zuid-holland/central-park-voorburg/", "de-watergeus-noorden": "/zuid-holland/de-watergeus-noorden/", "weeshuis-gouda": "/zuid-holland/weeshuis-gouda/", "de-kromme-watergang-hoofdplaat": "/zeeland/de-kromme-watergang-hoofdplaat/", "hof-aan-zee-dishoek": "/zeeland/hof-aan-zee-dishoek/", "inter-scaldes-kruiningen": "/zeeland/inter-scaldes-kruiningen/", "hostellerie-schuddebeurs": "/zeeland/hostellerie-schuddebeurs/", "kasteel-gemert-restaurant-gem": "/noord-brabant/kasteel-gemert-restaurant-gem/", "kazerne-eindhoven": "/noord-brabant/kazerne-eindhoven/", "kasteel-steenenburg": "/noord-brabant/kasteel-steenenburg/", "van-oys-maastricht-retreat": "/limburg/van-oys-maastricht-retreat/", "chateau-neercanne": "/limburg/chateau-neercanne/", "chateau-st-gerlach": "/limburg/chateau-st-gerlach/", "kasteeltje-hattem": "/limburg/kasteeltje-hattem/"}, SITE = 'https://dinerenenslapen.nl';
  var IDLE_MIN = 30;
  var sb = window.supabase.createClient(DB_URL, DB_KEY, {
    auth: { storage: window.sessionStorage, persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: 'implicit' }
  });

  var $ = function (id) { return document.getElementById(id); };
  var S = { reviews: [], messages: [], subscribers: [], tab: 'overzicht', rv: 'nieuw', ms: 'nieuw', mk: 'alle', sbs: 'actief', loaded: false, recovering: /type=recovery/.test(location.hash) };

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
  function safeMail(m) { return /^[^@\s<>"]+@[^@\s<>"]+\.[^@\s<>"]+$/.test(m || '') ? m : null; }
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
  function showLogin(msg, good) {
    $('app').hidden = true; $('who').hidden = true; $('login').hidden = false;
    $('box-login').hidden = S.recovering; $('box-reset').hidden = !S.recovering;
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
      S.recovering = false; $('r-pass').value = $('r-pass2').value = ''; toast('Je nieuwe wachtwoord is opgeslagen.'); start();
    });
  });
  $('logout').addEventListener('click', function () { sb.auth.signOut().then(function () { showLogin('Je bent uitgelogd.', true); }); });

  var idleT;
  function idle() { clearTimeout(idleT); idleT = setTimeout(function () { sb.auth.signOut().then(function () { showLogin('Je bent automatisch uitgelogd na ' + IDLE_MIN + ' minuten zonder activiteit.', true); }); }, IDLE_MIN * 60000); }
  ['click', 'keydown', 'scroll', 'pointermove'].forEach(function (ev) { document.addEventListener(ev, function () { if (!$('app').hidden) idle(); }, { passive: true }); });

  function start() {
    sb.auth.getSession().then(function (r) {
      var s = r.data && r.data.session;
      if (!s) { showLogin(); return; }
      if (S.recovering) { showLogin(); return; }
      sb.rpc('is_admin').then(function (a) {
        if (a.error || a.data !== true) { sb.auth.signOut(); showLogin('Dit account heeft geen toegang tot de beheeromgeving.'); return; }
        $('login').hidden = true; $('app').hidden = false; $('who').hidden = false; $('who-mail').textContent = s.user.email;
        idle(); load();
      });
    });
  }
  sb.auth.onAuthStateChange(function (ev) {
    if (ev === 'PASSWORD_RECOVERY') { S.recovering = true; showLogin(); return; }
    if (ev === 'SIGNED_IN' && !S.loaded && !S.recovering) start();
    if (ev === 'SIGNED_OUT') { S.loaded = false; S.reviews = []; S.messages = []; S.subscribers = []; }
  });

  /* ---------- gegevens ---------- */
  function load() {
    $('refresh').disabled = true;
    Promise.all([
      sb.from('reviews').select('*').order('created_at', { ascending: false }).limit(2000),
      sb.from('messages').select('*').order('created_at', { ascending: false }).limit(2000),
      sb.from('subscribers').select('*').order('created_at', { ascending: false }).limit(10000)
    ]).then(function (r) {
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
    S.reviews.forEach(function (r) { all.push({ d: r.created_at, k: 'Review', t: r.loc_name + ': ' + r.name, go: ['reviews', r.status] }); });
    S.messages.forEach(function (r) { all.push({ d: r.created_at, k: r.kind === 'tip' ? 'Tip' : 'Contact', t: r.kind === 'tip' ? (r.address_name + (r.address_place ? ', ' + r.address_place : '')) : ((r.subject || 'Bericht') + (r.name ? ' van ' + r.name : '')), go: ['berichten', r.status] }); });
    S.subscribers.forEach(function (r) { all.push({ d: r.created_at, k: 'Abonnee', t: r.email, go: ['nieuwsbrief', r.status] }); });
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
    var rows = S.reviews.filter(function (r) { return (S.rv === 'alle' || r.status === S.rv) && (!qq || (r.loc_name + ' ' + r.name + ' ' + r.body + ' ' + (r.email || '')).toLowerCase().indexOf(qq) >= 0); });
    var box = clear($('rv-list'));
    if (!rows.length) { box.appendChild(el('p', { class: 'empty', text: S.rv === 'nieuw' ? 'Er wachten geen reviews op je oordeel.' : 'Geen reviews in deze selectie.' })); return; }
    rows.forEach(function (r) {
      var url = LOC[r.loc_id], mail = safeMail(r.email), avg = ((r.score_e + r.score_s + r.score_p) / 3).toFixed(1).replace('.', ',');
      var acts = el('div', { class: 'acts' });
      if (r.status !== 'goedgekeurd') acts.appendChild(el('button', { type: 'button', class: 'btn ok', text: r.status === 'afgewezen' ? 'Toch goedkeuren' : 'Goedkeuren en plaatsen', onclick: function () { update('reviews', r, { status: 'goedgekeurd', reviewed_at: new Date().toISOString() }, 'Goedgekeurd. De review staat nu op de site.'); } }));
      if (r.status !== 'afgewezen') acts.appendChild(el('button', { type: 'button', class: 'btn no', text: r.status === 'goedgekeurd' ? 'Offline halen en afwijzen' : 'Afwijzen', onclick: function () { update('reviews', r, { status: 'afgewezen', reviewed_at: new Date().toISOString() }, 'Afgewezen. De review komt niet op de site.'); } }));
      if (r.status !== 'nieuw') acts.appendChild(el('button', { type: 'button', class: 'link', text: 'Terug naar te beoordelen', onclick: function () { update('reviews', r, { status: 'nieuw', reviewed_at: null }, 'Teruggezet.'); } }));
      if (url) acts.appendChild(el('a', { class: 'link', href: SITE + url + '#reviews', target: '_blank', rel: 'noopener noreferrer', text: 'Bekijk de pagina' }));
      acts.appendChild(el('span', { class: 'grow' }));
      acts.appendChild(confirmBtn('Verwijderen', 'link del', function () { remove('reviews', r, 'Review verwijderd.'); }));
      box.appendChild(el('article', { class: 'card s-' + r.status },
        el('div', { class: 'ch' }, el('h3', null, url ? el('a', { href: SITE + url, target: '_blank', rel: 'noopener noreferrer', text: r.loc_name }) : r.loc_name), pill(r.status)),
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
  function subRows() {
    var qq = q('sb-q');
    return S.subscribers.filter(function (r) { return (S.sbs === 'alle' || r.status === S.sbs) && (!qq || r.email.indexOf(qq) >= 0 || (r.source || '').toLowerCase().indexOf(qq) >= 0); });
  }
  function subscribers() {
    var cnt = function (s) { return S.subscribers.filter(function (r) { return s === 'alle' || r.status === s; }).length; };
    seg($('sb-seg'), [['actief', 'Actief (' + cnt('actief') + ')'], ['afgemeld', 'Afgemeld (' + cnt('afgemeld') + ')'], ['alle', 'Alles (' + cnt('alle') + ')']], S.sbs, function (v) { S.sbs = v; });
    var rows = subRows(), tb = clear($('sb-rows'));
    if (!rows.length) tb.appendChild(el('tr', null, el('td', { colspan: '6', class: 'muted', text: 'Geen abonnees in deze selectie.' })));
    rows.forEach(function (r) {
      var act = el('td');
      act.appendChild(el('button', { type: 'button', class: 'link', text: r.status === 'actief' ? 'Afmelden' : 'Weer actief', onclick: function () { update('subscribers', r, r.status === 'actief' ? { status: 'afgemeld', unsubscribed_at: new Date().toISOString() } : { status: 'actief', unsubscribed_at: null }, r.status === 'actief' ? 'Afgemeld.' : 'Weer actief.'); } }));
      act.appendChild(document.createTextNode('  '));
      act.appendChild(confirmBtn('Verwijderen', 'link del', function () { remove('subscribers', r, 'Adres verwijderd.'); }));
      tb.appendChild(el('tr', null, el('td', { text: r.email }), el('td', { text: dshort(r.created_at) }), el('td', { text: r.source || '' }), el('td', { text: r.lang === 'en' ? 'Engels' : 'Nederlands' }), el('td', null, pill(r.status)), act));
    });
    $('sb-foot').textContent = rows.length + (rows.length === 1 ? ' adres' : ' adressen') + ' in deze selectie.';
  }
  function activeInView() { return subRows().filter(function (r) { return r.status === 'actief'; }); }
  $('sb-csv').addEventListener('click', function () {
    var rows = activeInView();
    if (!rows.length) { toast('Er zijn geen actieve abonnees in deze selectie.'); return; }
    var esc = function (s) { s = String(s == null ? '' : s); if (/^[=+\-@]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
    var csv = '﻿email;ingeschreven;pagina;taal\r\n' + rows.map(function (r) { return [r.email, r.created_at.slice(0, 10), r.source, r.lang].map(esc).join(';'); }).join('\r\n');
    var url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    var a = el('a', { href: url, download: 'nieuwsbrief-abonnees-' + new Date().toISOString().slice(0, 10) + '.csv' });
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
