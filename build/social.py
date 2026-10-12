# Social: volgknoppen, deelknoppen, het filmpje en het blok onder het boek.
# Wordt door build.py ingelezen met exec() vlak voor main().
from urllib.parse import quote

ICONS = json.load(open(os.path.join(HERE, 'data', 'icons.json')))
ICONS['mail'] = 'M2 5h20v14H2zM2.8 5.8 12 13l9.2-7.2'
ICONS['link'] = 'M10 14a4.5 4.5 0 0 0 6.4 0l3.2-3.2a4.5 4.5 0 0 0-6.4-6.4l-1.1 1.1M14 10a4.5 4.5 0 0 0-6.4 0l-3.2 3.2a4.5 4.5 0 0 0 6.4 6.4l1.1-1.1'
ICONS['share'] = 'M12 3v12M7.5 7.5 12 3l4.5 4.5M5 12v8h14v-8'
STROKE = {'mail', 'link', 'share'}
SOCIAL = [('instagram', 'Instagram', 'https://www.instagram.com/dinerenenslapen/'), ('tiktok', 'TikTok', 'https://www.tiktok.com/@dinerenenslapen')]
VIDEO = '/media/dineren-en-slapen.mp4'; POSTER = '/media/dineren-en-slapen.jpg'

def ico(n, s=20):
    if n in STROKE:
        return '<svg viewBox="0 0 24 24" width="%d" height="%d" aria-hidden="true" focusable="false"><path d="%s" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>' % (s, s, ICONS[n])
    return '<svg viewBox="0 0 24 24" width="%d" height="%d" aria-hidden="true" focusable="false"><path d="%s" fill="currentColor"/></svg>' % (s, s, ICONS[n])

def follow_links(lang, cls='follow'):
    nl = lang == 'nl'
    return '<ul class="%s">%s</ul>' % (cls, ''.join(
        '<li><a href="%s" target="_blank" rel="noopener me" class="fl fl-%s" aria-label="%s">%s<span><b>%s</b><small>@dinerenenslapen</small></span></a></li>' % (
            u, k, ('Volg Dineren en Slapen op %s' if nl else 'Follow Dineren en Slapen on %s') % n, ico(k, 22), n) for k, n, u in SOCIAL))

def share_links(path, title, lang, img=None, cls='share'):
    nl = lang == 'nl'
    url = SITE + path; u = quote(url, safe=''); t = quote(title, safe='')
    items = [
        ('whatsapp', 'WhatsApp', 'https://wa.me/?text=' + quote(title + ' ' + url, safe='')),
        ('facebook', 'Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' + u),
        ('pinterest', 'Pinterest', 'https://pinterest.com/pin/create/button/?url=%s&description=%s%s' % (u, t, ('&media=' + quote(img, safe='')) if img else '')),
        ('linkedin', 'LinkedIn', 'https://www.linkedin.com/sharing/share-offsite/?url=' + u),
        ('x', 'X', 'https://x.com/intent/post?url=%s&text=%s' % (u, t)),
        ('mail', 'E-mail' if nl else 'Email', 'mailto:?subject=%s&body=%s' % (t, quote((('Dit leek me iets voor ons: ' if nl else 'This looks like one for us: ') + url), safe=''))),
    ]
    lab = 'Deel via %s' if nl else 'Share via %s'
    h = ''.join('<li><a href="%s" target="_blank" rel="noopener nofollow" class="sh sh-%s" aria-label="%s" title="%s">%s</a></li>' % (esc(href), k, lab % n, n, ico(k)) for k, n, href in items)
    h += '<li><button type="button" class="sh sh-copy" data-url="%s" aria-label="%s" title="%s">%s</button></li>' % (esc(url), 'Kopieer de link' if nl else 'Copy the link', 'Kopieer de link' if nl else 'Copy link', ico('link'))
    h += '<li class="sh-nat" hidden><button type="button" class="sh sh-native" data-url="%s" data-title="%s" aria-label="%s" title="%s">%s</button></li>' % (esc(url), esc(title), 'Delen' if nl else 'Share', 'Delen' if nl else 'Share', ico('share'))
    return '<ul class="%s">%s</ul><p class="sh-ok" role="status" aria-live="polite"></p>' % (cls, h)

def reel(lang, cls=''):
    nl = lang == 'nl'
    return ('<figure class="reelw %s"><div class="reel"><video muted loop playsinline preload="none" poster="%s" aria-label="%s"><source src="%s" type="video/mp4"><source src="%s" type="video/webm"></video>'
            '<button type="button" class="rplay" data-s="play" aria-label="%s"><i></i></button></div>'
            '<figcaption>%s <a href="%s" target="_blank" rel="noopener">%s</a></figcaption></figure>') % (
        cls, POSTER, 'Filmpje van Dineren en Slapen: kastelen, diners, kamers en ontbijt op bed' if nl else 'Short film by Dineren en Slapen: castles, dinners, rooms and breakfast in bed',
        VIDEO, VIDEO.replace('.mp4', '.webm'), 'Speel het filmpje af' if nl else 'Play the film',
        'Dineren en slapen in dertig seconden.' if nl else 'Dinner and a night away in thirty seconds.', SOCIAL[0][2], 'Meer filmpjes op Instagram' if nl else 'More films on Instagram')

def home_social(lang):
    nl = lang == 'nl'
    return ('<section class="sec white socb" id="volg" aria-labelledby="volg-h"><div class="wrap socg">%s'
            '<div class="socc stack"><p class="k">%s</p><h2 id="volg-h">%s</h2><p>%s</p>%s'
            '<p class="k" style="margin-top:18px">%s</p>%s</div>'
            '<div class="socn stack"><p class="k">%s</p><h2>%s</h2><p>%s</p>%s</div></div></section>') % (
        reel(lang),
        'Volg ons' if nl else 'Follow us', 'Elke week een nieuw adres in je tijdlijn' if nl else 'A new address in your feed every week',
        'Op Instagram en TikTok delen we korte filmpjes van adressen uit het boek, met wat je er voor twee kwijt bent. Volg ons, dan zie je ze als eerste.' if nl else
        'On Instagram and TikTok we share short films of addresses from the book, with what you will pay for two. Follow us and you will see them first.',
        follow_links(lang, 'follow big'),
        'Deel het boek' if nl else 'Share the book', share_links(u_home(lang), 'Dineren en Slapen: restaurants waar je ook blijft slapen' if nl else 'Dineren en Slapen: restaurants with rooms in the Netherlands', lang, SITE + POSTER),
        'Nieuwsbrief' if nl else 'Newsletter', 'Elke maand een adres om voor om te rijden' if nl else 'Every month, an address worth the drive',
        'Een nieuw adres, een arrangement dat de moeite waard is en de adressen die het net niet haalden. Kies je provincie, dan zetten we die bovenaan.' if nl else
        'A new address, a package worth booking and the places that only just missed out. Choose your province and we will put it at the top. The newsletter is in Dutch.',
        newsletter_form(lang, 'hm', head=False))

def share_strip(path, title, lang, img=None):
    nl = lang == 'nl'
    return ('<section class="sec shr" aria-label="%s"><div class="wrap shrw"><div><p class="k">%s</p>%s</div><div><p class="k">%s</p>%s</div></div></section>') % (
        'Delen en volgen' if nl else 'Share and follow', 'Deel deze pagina' if nl else 'Share this page', share_links(path, title, lang, img),
        'Volg Dineren en Slapen' if nl else 'Follow Dineren en Slapen', follow_links(lang))

SOCIAL_JS = r""";(function(){var L=document.documentElement.lang==='en'?'en':'nl',T={nl:{c:'Link gekopieerd.',f:'Kopiëren is niet gelukt. Kopieer de link uit de adresbalk.',p:'Pauzeer het filmpje',s:'Speel het filmpje af'},en:{c:'Link copied.',f:'Copying did not work. Please copy the link from the address bar.',p:'Pause the film',s:'Play the film'}}[L];
document.querySelectorAll('.sh-copy').forEach(function(b){b.addEventListener('click',function(){var ok=b.closest('ul').nextElementSibling;function say(t){if(ok){ok.textContent=t;setTimeout(function(){ok.textContent=''},3000)}}
if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(b.dataset.url).then(function(){say(T.c)},function(){say(T.f)});else say(T.f)})});
if(navigator.share)document.querySelectorAll('.sh-nat').forEach(function(li){li.hidden=false;li.querySelector('button').addEventListener('click',function(){var b=this;navigator.share({title:b.dataset.title,url:b.dataset.url}).catch(function(){})})});
document.querySelectorAll('.reel').forEach(function(r){var v=r.querySelector('video'),b=r.querySelector('.rplay'),user=false,rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function st(p){b.dataset.s=p?'pause':'play';b.setAttribute('aria-label',p?T.p:T.s)}
function tg(){user=true;if(v.paused){v.play().then(function(){st(true)}).catch(function(){})}else{v.pause();st(false)}}
b.addEventListener('click',tg);v.addEventListener('click',tg);
if(!rm&&'IntersectionObserver' in window)new IntersectionObserver(function(es){es.forEach(function(e){if(user)return;if(e.isIntersecting){v.play().then(function(){st(true)}).catch(function(){})}else if(!v.paused){v.pause();st(false)}})},{threshold:.45}).observe(v)})})();"""
JS = JS + SOCIAL_JS

SOCIAL_CSS = """
.reelw{margin:0;display:grid;gap:10px}
.socg{display:grid;grid-template-columns:minmax(220px,300px) minmax(0,1fr) minmax(0,1fr);gap:40px 52px;align-items:start}
.socg h2{font-size:clamp(28px,3.4vw,38px)}
@media (max-width:1060px){.socg{grid-template-columns:minmax(200px,280px) minmax(0,1fr)}.socn{grid-column:1 / -1}}
@media (max-width:700px){.socg{grid-template-columns:minmax(0,1fr)}.reelw{max-width:300px;margin:0 auto;width:100%}}
.reel{position:relative;aspect-ratio:9/16;border-radius:4px;overflow:hidden;background:var(--g2);box-shadow:0 24px 60px rgba(11,25,20,.28)}
.reel video{display:block;width:100%;height:100%;object-fit:cover;cursor:pointer}
.rplay{position:absolute;right:12px;bottom:12px;width:48px;height:48px;border-radius:50%;border:1px solid rgba(244,240,230,.7);background:rgba(11,25,20,.55);cursor:pointer;display:flex;align-items:center;justify-content:center}
.rplay i{display:block;width:0;height:0;border-style:solid;border-width:9px 0 9px 15px;border-color:transparent transparent transparent #F4F0E6;margin-left:4px}
.rplay[data-s=pause] i{width:14px;height:16px;border:0;border-left:4px solid #F4F0E6;border-right:4px solid #F4F0E6;margin:0}
.rplay:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.reelw figcaption{font:400 14px/1.45 var(--sans);color:var(--mute)}
ul.follow{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px}
ul.follow a{display:inline-flex;align-items:center;gap:10px;min-height:48px;padding:6px 16px 6px 12px;border:1px solid var(--line);border-radius:2px;background:#fff;color:var(--ink);text-decoration:none;font:400 14px/1.2 var(--sans)}
ul.follow a span{display:grid}ul.follow a b{font-weight:600}ul.follow a small{font-size:12.5px;color:var(--mute)}
ul.follow a:hover{border-color:var(--ink);color:var(--wine)}
ul.follow.big a{min-height:58px;padding:8px 20px 8px 14px}
ul.share{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.sh{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;padding:0}
.sh:hover{border-color:var(--ink);color:var(--wine)}
.sh:focus-visible,ul.follow a:focus-visible{outline:3px solid var(--gold2);outline-offset:2px}
.sh-ok{margin:6px 0 0;min-height:1.2em;font:400 14px var(--sans);color:var(--mute)}
.shr{padding:36px 0;background:var(--c2)}
.shrw{display:flex;flex-wrap:wrap;gap:24px 56px;justify-content:space-between;align-items:flex-start}
.shrw .k{margin-bottom:10px}
aside .sh{width:40px;height:40px}
@media (max-width:420px){.sh{width:40px;height:40px}}
footer.ft ul.follow{margin-top:18px}
footer.ft ul.follow a{background:transparent;border-color:#3A4D44;color:#E3E6DD}
footer.ft ul.follow a small{color:#A9B3A6}
footer.ft ul.follow a:hover{border-color:var(--gold);color:var(--gold)}
.socn form.sub{margin-top:4px}
"""
CSS = CSS + re.sub(r'\s*\n\s*', '', SOCIAL_CSS)
