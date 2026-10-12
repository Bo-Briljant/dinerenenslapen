# Meten: Google Tag Manager (GTM-5Z9K5PSH) met Google Analytics 4 (G-VD3RVJ36BM) daarin.
# Toestemmingsmodus v2: standaard staat alles uit. Pas na "Ja" in de cookiemelding
# zet Google Analytics cookies; zonder toestemming stuurt de tag alleen signalen zonder cookies.
# Advertentiecookies blijven altijd uit.
# Wordt door build.py ingelezen met exec(), na seo.py.

GTM_ID = 'GTM-5Z9K5PSH'

GTM_HEAD = ("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}"
            "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500});"
            "try{if(localStorage.getItem('des_cookies')==='ja')gtag('consent','update',{analytics_storage:'granted'})}catch(e){}</script>"
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
            "})(window,document,'script','dataLayer','%s');</script>" % GTM_ID)

GTM_BODY = ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>' % GTM_ID)

CONSENT_CSS = re.sub(r'\s*\n\s*', '', """
.ck{position:fixed;left:16px;right:16px;bottom:16px;z-index:60;max-width:560px;margin:0 auto;background:var(--g);color:#F4F0E6;border:1px solid rgba(210,173,92,.45);box-shadow:0 18px 40px rgba(0,0,0,.35);padding:18px 18px 16px;display:grid;gap:12px;font:400 15px/1.5 var(--sans)}
.ck[hidden]{display:none}
.ck p{margin:0}
.ck a{color:var(--gold)}
.ck .ckb{display:flex;gap:10px;flex-wrap:wrap}
.ck button{min-height:44px;padding:0 18px;border-radius:2px;font:600 13px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
.ck .ja{background:var(--gold);color:#10231C;border:0}
.ck .nee{background:transparent;color:#F4F0E6;border:1px solid rgba(244,240,230,.5)}
""")

def consent_html(lang):
    nl = lang == 'nl'
    return ('<div class="ck" id="ck" role="region" aria-label="%s" hidden><p>%s <a href="/privacy/">%s</a></p>'
            '<div class="ckb"><button type="button" class="ja" data-ck="ja">%s</button><button type="button" class="nee" data-ck="nee">%s</button></div></div>') % (
        'Cookies' if nl else 'Cookies',
        'We meten hoe de site gebruikt wordt, zodat we hem beter kunnen maken. Mogen we daarvoor analytische cookies gebruiken? Advertentiecookies gebruiken we nooit.' if nl else
        'We measure how the site is used so we can improve it. May we use analytics cookies for that? We never use advertising cookies.',
        'Meer over privacy' if nl else 'About privacy (in Dutch)', 'Ja, prima' if nl else 'Yes, that\'s fine', 'Liever niet' if nl else 'No thanks')

CONSENT_JS = (r""";(function(){var b=document.getElementById('ck');if(!b)return;var k='des_cookies',c=null;try{c=localStorage.getItem(k)}catch(e){}
function set(x){try{localStorage.setItem(k,x)}catch(e){}if(x==='ja')gtag('consent','update',{analytics_storage:'granted'});else gtag('consent','update',{analytics_storage:'denied'});
window.dataLayer.push({event:'cookiekeuze',cookiekeuze:x});b.hidden=true}
if(c!=='ja'&&c!=='nee')b.hidden=false;
b.addEventListener('click',function(e){var t=e.target.closest('[data-ck]');if(t)set(t.getAttribute('data-ck'))});
document.querySelectorAll('[data-ck-open]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();b.hidden=false})})})();""")

# formulieren: na een geslaagde inzending een gebeurtenis naar de dataLayer
TRACK_EVENTS = {'nieuwsbrief': 'nieuwsbrief_inschrijving', 'tip': 'tip_verzonden', 'contact': 'contact_verzonden', 'review': 'review_verzonden'}
_old = "if(r.ok||r.status===409)return done();"
_new = ("if(r.ok||r.status===409){try{window.dataLayer=window.dataLayer||[];var ev=%s[f.dataset.kind];if(ev)dataLayer.push({event:ev,formulier:f.dataset.kind,provincie:v(f,'provincie')||'',adres:f.dataset.loc||''})}catch(_){}return done()}"
        % json.dumps(TRACK_EVENTS))
assert _old in JS, 'formulier-JS is veranderd; pas analytics.py aan'
JS = JS.replace(_old, _new, 1)
CSS = CSS + CONSENT_CSS

_seo_post_prev = seo_post
def seo_post(doc):
    doc = _seo_post_prev(doc)
    if GTM_ID not in doc:
        lang = 'en' if '<html lang="en"' in doc else 'nl'
        doc = doc.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + GTM_HEAD, 1)
        doc = re.sub(r'<body>', '<body>' + GTM_BODY, doc, count=1)
        i = doc.rfind('<script>')
        doc = doc[:i] + consent_html(lang) + doc[i:]
        doc = doc.replace('</script></body></html>', CONSENT_JS + '</script></body></html>')
    return doc

def build_privacy():
    items = [('Home', '/'), ('Privacy', None)]
    h = ('<section class="sec"><div class="narrow prose stack">%s<h1 style="font-size:clamp(36px,6vw,54px)">Privacy</h1>'
         '<p>Deze site gebruikt geen advertentienetwerken en geen advertentiecookies. We meten wel hoe de site gebruikt wordt, zodat we hem beter kunnen maken.</p>'
         '<h2>Meten met Google Analytics</h2>'
         '<p>We gebruiken Google Analytics, geladen via Google Tag Manager. Daarmee zien we bijvoorbeeld hoeveel mensen een pagina bekijken, waar ze vandaan komen en hoe vaak iemand zich inschrijft voor de nieuwsbrief. '
         'Analytische cookies plaatsen we alleen als je daar in de melding onderin toestemming voor geeft. Zonder toestemming stuurt de site alleen anonieme signalen zonder cookies, waarmee je niet te herkennen bent. '
         'Google Analytics bewaart geen IP-adressen en we delen deze gegevens niet met Google voor advertenties. De gegevens worden veertien maanden bewaard.</p>'
         '<p><a href="#" data-ck-open>Je cookiekeuze wijzigen</a></p>'
         '<h2>Wat we bewaren</h2><ul>'
         '<li><strong>Nieuwsbrief.</strong> Je e-mailadres, je voorkeursprovincie, de pagina waar je je inschreef en de datum. Alleen om je de nieuwsbrief te sturen. Afmelden kan altijd.</li>'
         '<li><strong>Tips en contactberichten.</strong> Wat je invult, zodat we kunnen kijken en antwoorden.</li>'
         '<li><strong>Reviews.</strong> Je voornaam, je bezoekmaand, je cijfers en je tekst. Na goedkeuring staan je voornaam, maand, cijfers en tekst op de site. Je e-mailadres, als je het invult, komt nooit op de site.</li>'
         '<li><strong>Bescherming tegen spam.</strong> Bij elke inzending bewaren we een versleutelde code die van je IP-adres is afgeleid, zodat we massaal versturen kunnen tegenhouden. Die code wissen we na twee uur. Je IP-adres zelf bewaren we niet; onze databaseleverancier houdt IP-adressen kort bij in technische logboeken.</li></ul>'
         '<h2>Hoe lang</h2><ul><li>Berichten en tips: hooguit twee jaar.</li><li>Reviews: zolang ze op de site staan. Je e-mailadres bij een review wissen we na een jaar, afgewezen reviews na een jaar.</li><li>Nieuwsbrief: tot je je afmeldt. Na afmelden wissen we je adres binnen dertig dagen.</li><li>Bezoekgegevens in Google Analytics: veertien maanden.</li></ul>'
         '<h2>Waar het staat</h2><p>De gegevens van formulieren staan in een beveiligde database van Supabase, op servers in Frankfurt (EU). Alleen wij kunnen erbij, met een eigen inlog. Bezoekgegevens staan bij Google Analytics. We verkopen niets en geven niets door.</p>'
         '<h2>Inzien of verwijderen</h2><p>Wil je weten wat we van je hebben, of wil je dat we het verwijderen? Mail ons op <a href="mailto:%s">%s</a>. We regelen het binnen een maand.</p></div></section>') % (crumbs(items, light=True), MAIL, MAIL)
    page('/privacy/', 'nl', 'Privacy: wat we bewaren en waarom | Dineren en Slapen', 'Geen advertenties en geen advertentiecookies. Hoe we meten met Google Analytics en wat we bewaren als je je inschrijft, een tip of review stuurt.', h, '', None, [ld_crumbs(items)], prio=0.1)
