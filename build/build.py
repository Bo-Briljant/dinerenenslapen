#!/usr/bin/env python3
"""Bouwt dinerenenslapen.nl als statische site in ../docs (GitHub Pages).

Alles staat als gewone HTML op een eigen URL. Geen framework, geen tracking,
alleen een paar regels JavaScript voor formulieren.
"""
import json, os, re, shutil, html, math, datetime, hashlib
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'docs')
SITE = 'https://dinerenenslapen.nl'
TODAY = datetime.date(2026, 10, 10).isoformat()
ASSETS = os.environ.get('DES_ASSETS', '/home/claude/des-assets')
BLOBS = os.path.join(HERE, 'data', 'blobs.txt')
MAIL = 'dinerenenslapen@gmail.com'
FORM_ENDPOINT = 'https://formsubmit.co/ajax/' + MAIL   # eerste inzending stuurt een activatiemail naar dit adres

D = json.load(open(os.path.join(HERE, 'data', 'data.json')))
BL = json.load(open(os.path.join(HERE, 'data', 'blog.json')))
POSTS, CATS = BL['posts'], BL['cats']
LOCS, PROVS, W0 = D['locs'], D['provs'], D['w0']
PBY = {p['id']: p for p in PROVS}
LBY = {l['id']: l for l in LOCS}
CSS = open(os.path.join(HERE, 'style.css')).read()
CSS = re.sub(r'\s*\n\s*', '', CSS)

esc = lambda s: html.escape(str(s), quote=True)

def eur(v, lang='nl'):
    whole = abs(round(v) - v) < 1e-9
    s = str(int(round(v))) if whole else '%.2f' % v
    a, _, b = s.partition('.')
    a = re.sub(r'\B(?=(\d{3})+(?!\d))', '.' if lang == 'nl' else ',', a)
    return '€ ' + a + ((',' if lang == 'nl' else '.') + b if b else '')

def num(v, lang='nl'):
    s = ('%.1f' % v)
    return s.replace('.', ',') if lang == 'nl' else s

def total(l):
    w = W0; sc = l['sc']
    return (sc['e'] * w['e'] + sc['s'] * w['s'] + sc['p'] * w['p']) / 100.0

ORDER = sorted(LOCS, key=lambda l: (-total(l), l['name']))
RANK = {l['id']: i + 1 for i, l in enumerate(ORDER)}
def in_prov(pid): return [l for l in ORDER if l['prov'] == pid]
PROV_ORDER = sorted(PROVS, key=lambda p: int(p['n']))

def pname(p, lang): return p['name'] if lang == 'nl' else p['en']
def stars(n, lang):
    if lang == 'nl': return 'Eén Michelinster' if n == 1 else '%d Michelinsterren' % n
    return 'One Michelin star' if n == 1 else '%d Michelin stars' % n
def gm(v, lang): return 'Gault&Millau ' + num(v, lang).replace(',0', '').replace('.0', '') + '/20'
def p2(l, lang): return ('ca. ' if lang == 'nl' else 'approx. ') + eur(l['pz']['p2'], lang) + (' voor twee' if lang == 'nl' else ' for two')
def lst(a, lang):
    a = list(a)
    if len(a) < 2: return ''.join(a)
    return ', '.join(a[:-1]) + (' en ' if lang == 'nl' else ' and ') + a[-1]

# ---------- URL's ----------
def u_home(lang): return '/' if lang == 'nl' else '/en/'
def u_prov(pid, lang): return ('/' if lang == 'nl' else '/en/') + pid + '/'
def u_loc(l, lang): return u_prov(l['prov'], lang) + l['id'] + '/'
def u_top(lang): return '/top-10/' if lang == 'nl' else '/en/top-10/'
def u_post(slug): return '/verhalen/' + slug + '/'

# ---------- thema's ----------
THEMES = [
    {'slug': 'sterrenrestaurants-met-overnachting', 'test': lambda l: l['ms'] > 0,
     'h1': 'Sterrenrestaurants met overnachting', 'nav': 'Sterrenrestaurants met overnachting',
     'title': 'Sterrenrestaurant met overnachting: alle {n} adressen (2026)',
     'desc': 'Eten bij een sterrenchef en daarna de trap op. Alle {n} adressen in ons boek met een Michelinster en kamers, met wat je voor twee kwijt bent.',
     'intro': 'Een sterrendiner en daarna niet meer naar huis hoeven: dat is voor ons de mooiste avond die er is. Dit zijn alle adressen in het boek waar de keuken een Michelinster heeft en je boven het restaurant blijft slapen. Van een herberg in Aduard tot De Librije, het enige driesterrenrestaurant van Nederland.'},
    {'slug': 'kastelen-en-landgoederen', 'test': lambda l: bool(re.search(r'kasteel|château|chateau|landgoed|havezate|buitenplaats', (l['type']['nl'] + ' ' + l['name']).lower())),
     'h1': 'Dineren en slapen in een kasteel of op een landgoed', 'nav': 'Kastelen en landgoederen',
     'title': 'Overnachten in een kasteel met diner: {n} adressen (2026)',
     'desc': 'Een kasteel, een havezate of een landgoed met een goede keuken en kamers. {n} adressen waar je dineert en blijft slapen, met prijs voor twee.',
     'intro': 'Een gracht, een oprijlaan, een slaapkamer met hoge ramen. Op deze adressen eet en slaap je in een kasteel, een havezate of op een landgoed, en de keuken is er net zo serieus als het pand.'},
    {'slug': 'aan-zee-en-aan-het-water', 'test': lambda l: l['id'] in {'aest-terschelling', 'hof-aan-zee-dishoek', 'merlet-schoorl', 'de-hinde-hindeloopen', 'de-watergeus-noorden', 'de-nederlanden-vreeland', 'restaurant-de-molenaar', 'de-kromme-watergang-hoofdplaat'},
     'h1': 'Dineren en slapen aan zee en aan het water', 'nav': 'Aan zee en aan het water',
     'title': 'Restaurant met overnachting aan zee of aan het water (2026)',
     'desc': 'Een eiland, de duinen, een haven of een plas: {n} adressen aan het water waar je goed eet en blijft slapen. Met wat je voor twee kwijt bent.',
     'intro': 'Na het diner nog even naar buiten, en dan ligt daar het water. Op deze adressen slaap je op een eiland, achter de duinen, aan een haven of aan een plas.'},
    {'slug': 'betaalbaar-dineren-en-slapen', 'test': lambda l: l['pz']['p2'] <= 340,
     'h1': 'Betaalbaar dineren en slapen: tot € 340 voor twee', 'nav': 'Betaalbaar, tot € 340 voor twee',
     'title': 'Betaalbaar diner met overnachting: {n} adressen tot € 340',
     'desc': 'Goed eten en mooi slapen hoeft niet duur te zijn. {n} adressen waar je voor twee tot ca. € 340 kwijt bent voor diner, een nacht en ontbijt.',
     'intro': 'Goed eten en mooi slapen hoeft niet duur te zijn. Op deze adressen ben je voor twee hooguit zo\'n € 340 kwijt voor het diner, een nacht en het ontbijt, zonder drank. Vaak in een molen, een herberg of een landhuis in het noorden en oosten.'},
]
for t in THEMES:
    t['locs'] = [l for l in ORDER if t['test'](l)]
THEMES = [t for t in THEMES if len(t['locs']) >= 5]
def themes_of(l): return [t for t in THEMES if l in t['locs']]

# ---------- verhalen: welke adressen noemt een verhaal ----------
def post_text(a):
    out = []
    for b in a['body']:
        out.append(b.get('x', '')); out += b.get('items', [])
    return ' '.join(out)
NAME_ALIASES = {}
for l in LOCS:
    al = {l['name']}
    short = re.sub(r'^(Hotel|Restaurant|Landgoed|Kasteel|Château|Chateau|Hostellerie|De Herberg van|Herberg|Grand Hotel)\s+', '', l['name'])
    short = re.split(r'\s+&\s+|,', short)[0].strip()
    if len(short) > 4: al.add(short)
    extra = {'prinsenhof-groningen': ['Prinsenhof', 'Nassau'], 'de-librije-zwolle': ['De Librije'], 'grand-hotel-karel-v-utrecht': ['Karel V'],
             'the-dylan-amsterdam': ['The Dylan'], 'de-l-europe-amsterdam': ["De L'Europe"], 'kasteel-gemert-restaurant-gem': ['Kasteel Gemert'],
             'hotel-gastronomique-de-echoput': ['De Echoput'], 'van-oys-maastricht-retreat': ['Van Oys'], 'herberg-onder-de-linden': ['Herberg Onder de Linden', 'Onder de Linden'],
             'restaurant-de-molenaar': ['De Molenaar'], 'broederenklooster-zutphen': ['Broederenklooster'], 'chateau-st-gerlach': ['Château St. Gerlach', 'St. Gerlach'],
             'rikus-eext': ['Rikus'], 'hostellerie-schuddebeurs': ['Schuddebeurs'], 'parc-broekhuizen-leersum': ['Parc Broekhuizen'], 'kasteeltje-hattem': ['Kasteeltje Hattem'],
             'chateau-de-havixhorst': ['De Havixhorst', 'Havixhorst'], 'posten-nordic-cuisine': ['POSTEN'], 'ml-haarlem': ['ML'], 'aest-terschelling': ['AEST']}
    al.update(extra.get(l['id'], []))
    NAME_ALIASES[l['id']] = sorted(al, key=len, reverse=True)
def mentions(text):
    hit = []
    for lid, al in NAME_ALIASES.items():
        for a in al:
            if re.search(r'(?<![\w])' + re.escape(a) + r'(?![\w])', text):
                hit.append(lid); break
    return hit
POST_LOCS = {a['slug']: list(dict.fromkeys(a['related'] + mentions(post_text(a)))) for a in POSTS}
def posts_of_loc(lid): return [a for a in POSTS if lid in POST_LOCS[a['slug']]]
def posts_of_prov(pid): return [a for a in POSTS if a.get('prov') == pid or any(LBY[x]['prov'] == pid for x in POST_LOCS[a['slug']] if x in LBY)]

def autolink(text, done, self_id=None):
    """Eerste vermelding van een adres in een verhaal wordt een link naar dat adres."""
    t = esc(text)
    for lid, al in NAME_ALIASES.items():
        if lid in done or lid == self_id: continue
        for a in al:
            ea = esc(a)
            m = re.search(r'(?<![\w>/])' + re.escape(ea) + r'(?![\w<])', t)
            if m and '<a ' not in t[max(0, m.start() - 200):m.start()].split('</a>')[-1]:
                t = t[:m.start()] + '<a href="%s">%s</a>' % (u_loc(LBY[lid], 'nl'), ea) + t[m.end():]
                done.add(lid); break
    # vaste begrippen naar eigen pagina's
    fixed = [('ons stuk over arrangementen', u_post('arrangement-of-los-boeken')), ('ons stuk over wat een avond uit eten met overnachting kost', u_post('wat-kost-dineren-en-slapen')),
             ('ons hoofdstuk Groningen', u_prov('groningen', 'nl')), ('top 10', u_top('nl'))]
    for phrase, url in fixed:
        if phrase in t and url not in done:
            t = t.replace(phrase, '<a href="%s">%s</a>' % (url, phrase), 1); done.add(url)
    return t

# ---------- beelden ----------
BLOB2NAME = {}
for line in open(BLOBS):
    if line.strip():
        n, i = line.split(); BLOB2NAME[i] = n
os.makedirs(OUT, exist_ok=True)
IMG_DONE = {}
def src_path(name):
    for d in ('n', 'f', ''):
        p = os.path.join(ASSETS, d, name + '.jpg')
        if os.path.exists(p): return p
    return None
def img_variants(blob, widths=(480, 960, 1600)):
    bid = blob.rsplit('/', 1)[-1] if blob else ''
    name = BLOB2NAME.get(bid)
    if not name: return None
    key = (name, widths)
    if key in IMG_DONE: return IMG_DONE[key]
    sp = src_path(name)
    if not sp: return None
    im = Image.open(sp).convert('RGB')
    W, H = im.size
    out = []
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    for w in widths:
        if w > W and out: break
        ww = min(w, W); hh = round(H * ww / W)
        fn = '%s-%d.webp' % (name, ww)
        fp = os.path.join(OUT, 'img', fn)
        if not os.path.exists(fp):
            im.resize((ww, hh), Image.LANCZOS).save(fp, 'WEBP', quality=78, method=6)
        out.append((ww, hh, '/img/' + fn))
    IMG_DONE[key] = out
    return out
def pic(blob, alt, sizes='(max-width: 760px) 100vw, 50vw', lazy=True, cls='', widths=(480, 960, 1600), prio=False):
    v = img_variants(blob, widths)
    if not v: return ''
    w, h, src = v[min(1, len(v) - 1)]
    srcset = ', '.join('%s %dw' % (s, ww) for ww, hh, s in v)
    return '<img src="%s" srcset="%s" sizes="%s" width="%d" height="%d" alt="%s"%s%s%s>' % (
        src, srcset, sizes, w, h, esc(alt), ' loading="lazy"' if lazy else '', ' fetchpriority="high"' if prio else '', ' decoding="async"' + (' class="%s"' % cls if cls else ''))
def og_img(blob):
    v = img_variants(blob)
    return SITE + v[-1][2] if v else SITE + '/og.jpg'

# ---------- teksten per provincie (poort van site.js) ----------
def prov_text(P, lang):
    nl = lang == 'nl'; pn = pname(P, lang)
    ls = in_prov(P['id'])
    starred = [l for l in ls if l['ms'] > 0]
    byp = sorted(ls, key=lambda l: l['pz']['p2'])
    sized = []
    for l in ls:
        m = re.search(r'\d+', (l['rooms'] or {}).get('nl', '') or '')
        if m: sized.append((int(m.group()), l))
    sized.sort(key=lambda x: x[0])
    top, sec = ls[0], (ls[1] if len(ls) > 1 else None)
    lo, hi = byp[0], byp[-1]
    words = (['nul', 'één', 'twee', 'drie', 'vier', 'vijf'] if nl else ['no', 'one', 'two', 'three', 'four', 'five'])
    nw = words[len(ls)] if len(ls) < 6 else str(len(ls))
    L = lambda a: lst(a, lang)
    if nl:
        intro2 = 'In %s houden we het bij %s adressen. Er is meer, maar we schrijven alleen op waar we zelf terug zouden gaan. Moeten we er één kiezen, dan wordt het %s.' % (pn, nw, top['name'])
        if starred: intro2 += ' Wie voor een ster komt, zit goed bij %s.' % L(l['name'] for l in starred)
        intro2 += ' De volgende plek is nog leeg: daar zijn we nog aan het testen.'
        faq = [('Waar kun je in %s eten en blijven slapen?' % pn, 'In ons boek staan %s adressen in %s: %s.' % (nw, pn, L('%s in %s' % (l['name'], l['place']) for l in ls))),
               ('Waar zouden jullie zelf heen gaan in %s?' % pn, '%s in %s. %s%s' % (top['name'], top['place'], top['kort']['nl'] + ' ', ('Zit dat vol, dan bellen we %s.' % sec['name']) if sec else '')),
               ('Wat kost een diner met overnachting in %s?' % pn, 'Reken voor twee op %s bij %s%s, voor het diner, een nacht en het ontbijt. De bedragen komen uit hun eigen boekingssysteem, voor een doordeweekse nacht in november 2026.' % (eur(lo['pz']['p2']), lo['name'], (' tot %s bij %s' % (eur(hi['pz']['p2']), hi['name'])) if hi is not lo else ''))]
        faq.append(('Kun je in %s bij een sterrenrestaurant blijven slapen?' % pn, ('Ja: bij %s. Je loopt na het dessert zo naar boven.' % L('%s in %s' % (l['name'], l['place']) for l in starred)) if starred else 'Nog niet bij een adres met een ster. Wel bij plekken waar we net zo graag zitten.'))
        if len(sized) > 1: faq.append(('Wat is het kleinste en het grootste adres?', 'Het kleinste is %s met %s. Het grootste is %s met %s. Klein betekent vooral: vroeg boeken.' % (sized[0][1]['name'], sized[0][1]['rooms']['nl'][0].lower() + sized[0][1]['rooms']['nl'][1:], sized[-1][1]['name'], sized[-1][1]['rooms']['nl'][0].lower() + sized[-1][1]['rooms']['nl'][1:])))
    else:
        intro2 = 'In %s we keep it to %s addresses. There are more, but we only write down the places we would go back to. If we had to pick one, it would be %s.' % (pn, nw, top['name'])
        if starred: intro2 += ' If you are coming for a star, try %s.' % L(l['name'] for l in starred)
        intro2 += ' The next place is still empty: we are still testing.'
        faq = [('Where can you dine and stay the night in %s?' % pn, 'Our book lists %s addresses in %s: %s.' % (nw, pn, L('%s in %s' % (l['name'], l['place']) for l in ls))),
               ('Where would you go yourselves in %s?' % pn, '%s in %s. %s%s' % (top['name'], top['place'], top['kort']['en'] + ' ', ('If it is full, we ring %s.' % sec['name']) if sec else '')),
               ('What does dinner with an overnight stay cost in %s?' % pn, 'For two, count on %s at %s%s, for dinner, one night and breakfast. Amounts come from their own booking systems, for a weeknight in November 2026.' % (eur(lo['pz']['p2'], 'en'), lo['name'], (' up to %s at %s' % (eur(hi['pz']['p2'], 'en'), hi['name'])) if hi is not lo else ''))]
        faq.append(('Can you stay the night at a Michelin-starred restaurant in %s?' % pn, ('Yes: at %s. After dessert you just walk upstairs.' % L('%s in %s' % (l['name'], l['place']) for l in starred)) if starred else 'Not at a starred address yet. But at places we like just as much.'))
    return intro2, faq

def price_facts(l, lang):
    nl = lang == 'nl'; z = l['pz']; out = []
    out.append(('Reken voor twee op' if nl else 'For two, count on', ('ca. ' if nl else 'approx. ') + eur(z['p2'], lang) + (': diner, een nacht en ontbijt' if nl else ': dinner, one night and breakfast') + ((', wijn inbegrepen' if nl else ', wine included') if z['allin'] else '')))
    c = z.get('calc') or {}
    if c.get('t') == 'arr': cv = 'het arrangement hieronder' if nl else 'the package below'
    elif c.get('t') == 'los':
        cv = ('kamer ' if nl else 'room ') + eur(c['room'], lang) + ((' met ontbijt' if nl else ' with breakfast') if c.get('bf') is True else '')
        if c.get('bf') is False and c.get('bfpp'): cv += (' + ontbijt ' if nl else ' + breakfast ') + eur(c['bfpp'], lang) + ' × 2'
        cv += ' + menu ' + eur(c['menu'], lang) + ' × 2'
    else: cv = 'geschat: niet alle prijzen staan op hun site' if nl else 'estimated: not all prices are on their site'
    out.append(('Zo rekenen we' if nl else 'How we get there', cv))
    if z.get('room'): out.append(('Kamer' if nl else 'Room', eur(z['room'], lang) + (' per nacht, de voordeligste kamer' if nl else ' per night, the least expensive room') + (((', met ontbijt' if nl else ', with breakfast')) if z.get('bf') is True else ((', ontbijt ' if nl else ', breakfast ') + eur(z['bfpp'], lang) + ' p.p.' if z.get('bfpp') else ''))))
    if z.get('menu'): out.append(('Menu', eur(z['menu'], lang) + ' p.p.' + ((' (%s %s%s)' % (z['crs'], 'gangen' if nl else 'courses', (', met wijn' if nl else ', with wine') if z['allin'] and c.get('t') == 'los' else '')) if z.get('crs') else '')))
    if z.get('arr') and (nl or z.get('arr1')): out.append(('Arrangement' if nl else 'Package', eur(round(z['arr'] * 2, 2), lang) + (' voor twee' if nl else ' for two') + ((': ' + z['arrd']) if nl and z.get('arrd') else '')))
    if z.get('note'): out.append(('Let op' if nl else 'Note', z['note'][lang]))
    return out

def badges(l, lang):
    b = []
    if l['ms']: b.append(('star', stars(l['ms'], lang)))
    if l['bib']: b.append(('', 'Bib Gourmand'))
    if l['gm']: b.append(('', gm(l['gm'], lang)))
    for o in l.get('other') or []: b.append(('', o))
    return b
def chips(l, lang, n=4):
    return '<div class="chips">' + ''.join('<span class="chip %s">%s</span>' % (c, esc(t)) for c, t in badges(l, lang)[:n]) + '</div>'

# ---------- layout ----------
T = {
 'nl': {'sub': 'Het boek van dineren en slapen', 'provs': 'Provincies', 'top': 'Top 10', 'blog': 'Verhalen', 'keur': 'Zo kiezen wij', 'net': 'Net niet', 'skip': 'Naar de inhoud', 'home': 'Home',
        'ourscore': 'ons cijfer', 'read': 'Lees ons verslag', 'site': 'Website', 'perprov': 'Per provincie', 'lists': 'Lijsten', 'about': 'Over dit boek', 'credits': 'Beeldverantwoording', 'privacy': 'Privacy',
        'nlText': 'Ons dagboek van avonden aan tafel en de nachten erna. Voor wie na het dessert niet meer naar huis wil.', 'nlBtn': 'Inschrijven', 'nlLabel': 'Maandelijkse nieuwsbrief', 'ph': 'naam@voorbeeld.nl', 'tip': 'Tip ons een adres'},
 'en': {'sub': 'The book of dining and sleeping', 'provs': 'Provinces', 'top': 'Top 10', 'blog': 'Stories', 'keur': 'How we choose', 'net': 'Not quite', 'skip': 'Skip to content', 'home': 'Home',
        'ourscore': 'our score', 'read': 'Read our review', 'site': 'Website', 'perprov': 'By province', 'lists': 'Lists', 'about': 'About this book', 'credits': 'Image credits', 'privacy': 'Privacy',
        'nlText': 'Our diary of evenings at the table and the nights that follow. For those who would rather not drive home after dessert.', 'nlBtn': 'Subscribe', 'nlLabel': 'Monthly newsletter (in Dutch)', 'ph': 'name@example.com', 'tip': 'Suggest an address'},
}
PAGES = []   # (path, lang, alternates, priority, lastmod)

def header(lang, active, alt):
    t = T[lang]
    def nv(href, txt, key): return '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if active == key else '', txt)
    nav = [nv(u_home(lang) + '#provincies', t['provs'], 'prov'), nv(u_top(lang), t['top'], 'top')]
    if lang == 'nl':
        nav += [nv('/verhalen/', t['blog'], 'blog'), nv('/zo-kiezen-wij/', t['keur'], 'keur'), nv('/net-niet/', t['net'], 'net')]
    alt_nl, alt_en = (alt or {}).get('nl'), (alt or {}).get('en')
    if lang == 'nl': lang_sw = '<span aria-current="true">NL</span>' + ('<a href="%s" hreflang="en" lang="en">EN</a>' % alt_en if alt_en else '')
    else: lang_sw = ('<a href="%s" hreflang="nl" lang="nl">NL</a>' % alt_nl if alt_nl else '') + '<span aria-current="true">EN</span>'
    return ('<a class="skip" href="#inhoud">%s</a><header class="top"><div class="wrap bar"><a class="brand" href="%s"><b>Dineren <i>&amp;</i> Slapen</b><small>%s</small></a>'
            '<nav class="main" aria-label="%s">%s</nav><div class="lang">%s</div></div></header>') % (t['skip'], u_home(lang), t['sub'], 'Hoofdmenu' if lang == 'nl' else 'Main menu', ''.join(nav), lang_sw)

def footer(lang):
    t = T[lang]
    provs = ''.join('<li><a href="%s">%s</a></li>' % (u_prov(p['id'], lang), ('Restaurant met overnachting ' if lang == 'nl' else '') + pname(p, lang) if False else pname(p, lang)) for p in PROV_ORDER)
    lists = '<li><a href="%s">%s</a></li>' % (u_top(lang), 'Top 10 dineren en slapen' if lang == 'nl' else 'Top 10 dine and stay')
    if lang == 'nl':
        lists += ''.join('<li><a href="/%s/">%s</a></li>' % (th['slug'], th['nav']) for th in THEMES)
        blog = ''.join('<li><a href="%s">%s</a></li>' % (u_post(a['slug']), esc(a['title']['nl'])) for a in POSTS[:4])
    about = ('<li><a href="/zo-kiezen-wij/">Zo kiezen wij en onze cijfers</a></li><li><a href="/zo-kiezen-wij/#tip">Tip ons een adres</a></li><li><a href="/net-niet/">Net niet: in de nieuwsbrief</a></li><li><a href="/verhalen/">Alle verhalen</a></li><li><a href="/beeldverantwoording/">Beeldverantwoording</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="mailto:%s">%s</a></li>' % (MAIL, MAIL)
             if lang == 'nl' else '<li><a href="/zo-kiezen-wij/">How we choose (Dutch)</a></li><li><a href="/beeldverantwoording/">Image credits</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="mailto:%s">%s</a></li>' % (MAIL, MAIL))
    cols = ('<div><p style="font:600 28px/1 var(--disp);color:var(--c);margin:0 0 12px">Dineren <i style="color:var(--gold);font-weight:500">&amp;</i> Slapen</p><p>%s</p>%s</div>'
            '<nav aria-label="%s"><h2>%s</h2><ul class="two">%s</ul></nav><nav aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>') % (
        t['nlText'], newsletter_form(lang, 'ft', compact=True), t['perprov'], t['perprov'], provs, t['lists'], t['lists'], lists)
    if lang == 'nl': cols += '<nav aria-label="Verhalen"><h2>Verhalen</h2><ul>%s</ul></nav>' % blog
    cols += '<nav aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>' % (t['about'], t['about'], about)
    return '<footer class="ft"><div class="wrap"><div class="cols">%s</div><div class="base"><span>© 2026 dinerenenslapen.nl</span><span>%s</span></div></div></footer>' % (
        cols, 'Keurmerken volgens de gidsen van 2026. Prijzen gecheckt in oktober 2026.' if lang == 'nl' else 'Labels according to the 2026 guides. Prices checked in October 2026.')

def newsletter_form(lang, idp, compact=False, dark=True):
    t = T[lang]
    return ('<div class="nlwrap"><form class="sub js-form" data-kind="nieuwsbrief" method="post" action="%s" style="margin-top:14px"><label for="%s-mail" style="font:500 13px var(--sans);width:100%%">%s</label>'
            '<input type="hidden" name="_subject" value="Nieuwsbrief: nieuwe inschrijving"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"><input id="%s-mail" class="inp" type="email" name="email" autocomplete="email" required placeholder="%s"><button class="btn%s" type="submit">%s</button></form>'
            '<p class="thanks" role="status">%s</p></div>') % (
        esc(FORM_ENDPOINT or '#'), idp, t['nlLabel'], idp, t['ph'], ' ghost' if compact else '', t['nlBtn'],
        'Dank je, je staat op de lijst. De eerste mail komt begin volgende maand.' if lang == 'nl' else 'Thank you, you are on the list. The first email arrives early next month.')

JS = ("document.querySelectorAll('.js-form').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var w=f.parentNode;"
      "if(!f.action||f.getAttribute('action')==='#'){w.classList.add('sent');return}fetch(f.action,{method:'POST',headers:{Accept:'application/json'},body:new FormData(f)}).then(function(){w.classList.add('sent')})})})")

def crumbs(items, light=False):
    li = ''.join('<li>%s</li>' % ('<a href="%s">%s</a>' % (u, esc(n)) if u else '<span aria-current="page">%s</span>' % esc(n)) for n, u in items)
    return '<nav class="crumbs%s" aria-label="Kruimelpad"><ol>%s</ol></nav>' % (' light' if light else '', li)
def ld_crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + (u or items[-1][1] or '')} for i, (n, u) in enumerate(items)]}

ORG = {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'Dineren en Slapen', 'url': SITE + '/', 'logo': SITE + '/icon-512.png'}

def page(path, lang, title, desc, body, active='', alt=None, ld=None, og=None, prio=0.6, ptype='website', noindex=False, preload_img=None, extra_js=''):
    alt = alt or {lang: path}
    links = ''
    if len(alt) > 1 or lang == 'en':
        for lg, u in alt.items(): links += '<link rel="alternate" hreflang="%s" href="%s%s">' % (lg, SITE, u)
        if 'nl' in alt: links += '<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, alt['nl'])
    graph = [ORG, {'@type': 'WebSite', '@id': SITE + '/#site', 'url': SITE + '/', 'name': 'Dineren en Slapen', 'inLanguage': 'nl-NL', 'publisher': {'@id': SITE + '/#org'}}] + (ld or [])
    ogimg = og or SITE + '/og.jpg'
    pre = '<link rel="preload" href="/fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/source-serif-4-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>'
    if preload_img: pre += preload_img
    doc = ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s%s">%s%s'
           '<meta name="robots" content="%s"><meta name="theme-color" content="#10231C">'
           '<meta property="og:type" content="%s"><meta property="og:site_name" content="Dineren en Slapen"><meta property="og:locale" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s%s"><meta property="og:image" content="%s"><meta name="twitter:card" content="summary_large_image">'
           '<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">'
           '<style>%s</style><script type="application/ld+json">%s</script></head><body>%s<main id="inhoud">%s</main>%s<script>%s</script></body></html>') % (
        lang, esc(title), esc(desc), SITE, path, links, pre, 'noindex,follow' if noindex else 'index,follow,max-image-preview:large', ptype, 'nl_NL' if lang == 'nl' else 'en_GB',
        esc(title), esc(desc), SITE, path, esc(ogimg), CSS, json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/'),
        header(lang, active, alt), body, footer(lang), JS + extra_js)
    fp = os.path.join(OUT, path.lstrip('/'), 'index.html') if path.endswith('/') else os.path.join(OUT, path.lstrip('/'))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(doc)
    if not noindex: PAGES.append((path, lang, alt, prio))
    check_meta(path, title, desc, body)

ISSUES = []
def check_meta(path, title, desc, body):
    if len(title) > 62: ISSUES.append('title > 62 (%d): %s' % (len(title), path))
    if len(desc) > 158 or len(desc) < 70: ISSUES.append('desc lengte %d: %s' % (len(desc), path))
    if body.count('<h1') != 1: ISSUES.append('h1 aantal %d: %s' % (body.count('<h1'), path))
    if '—' in body or '—' in title or '—' in desc: ISSUES.append('gedachtestreep: ' + path)

# ---------- kaart ----------
def svg_map(lang, only=None, dots=True):
    m = D['map']; parts = []
    for p in PROVS:
        if only and p['id'] != only: continue
        lab = ''
        if not only: lab = '<text class="lb" x="%s" y="%s" text-anchor="middle">%s</text>' % (p['lx'], p['ly'], esc(pname(p, lang)))
        parts.append('<a href="%s" aria-label="%s"><path class="p" d="%s"/>%s</a>' % (u_prov(p['id'], lang), esc(('Restaurant met overnachting in ' if lang == 'nl' else 'Dine and stay in ') + pname(p, lang)), p['d'], lab))
    if dots:
        for l in LOCS:
            if only and l['prov'] != only: continue
            parts.append('<a href="%s" aria-label="%s"><circle class="d%s" cx="%.1f" cy="%.1f" r="%s"/></a>' % (u_loc(l, lang), esc(l['name']), ' b' if in_prov(l['prov'])[0] is l else '', l['x'], l['y'], '6' if only else '4.5'))
    vb = '0 0 %d %d' % (m['w'], m['h'])
    if only:
        bb = json.loads(PBY[only]['bb']) if isinstance(PBY[only]['bb'], str) else PBY[only]['bb']
        pad = 14; vb = '%.1f %.1f %.1f %.1f' % (bb[0] - pad, bb[1] - pad, bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad)
    return '<div class="map"><svg viewBox="%s" role="img" aria-label="%s">%s</svg></div>' % (vb, 'Kaart' if lang == 'nl' else 'Map', ''.join(parts))

# ---------- bouwstenen ----------
def loc_card(l, lang, prio=False):
    return ('<a class="card" href="%s"><div class="ph">%s</div><div class="bd"><p class="k">%s</p><span class="cn">%s</span><span class="meta">%s · %s · %s</span><span class="tag">%s</span></div></a>') % (
        u_loc(l, lang), pic(l.get('th') or l['img'], '', '(max-width: 760px) 100vw, 380px', lazy=not prio, widths=(480, 960)), esc(l['type'][lang]), esc(l['name']), esc(l['place']), esc(pname(PBY[l['prov']], lang)), p2(l, lang), esc(l['tag'][lang]))
def mini(l, lang):
    return '<a class="mini" href="%s">%s<span><b>%s</b><span>%s · %s · %s</span></span></a>' % (u_loc(l, lang), pic(l.get('th') or l['img'], '', '76px', widths=(480,)), esc(l['name']), esc(l['place']), esc(pname(PBY[l['prov']], lang)), p2(l, lang))
def post_card(a):
    return ('<a class="card" href="%s"><div class="ph">%s</div><div class="bd"><p class="k">%s</p><span class="cn">%s</span><span style="font-size:16px;color:var(--ink2)">%s</span><span class="meta">%s · %d min lezen</span></div></a>') % (
        u_post(a['slug']), pic(D['img'].get(a['img']) or post_img(a), '', '(max-width: 760px) 100vw, 380px', widths=(480, 960)), esc(a['kicker']['nl']), esc(a['title']['nl']), esc(a['lead']['nl']), a['dateTxt']['nl'], a['min'])
def post_img(a):
    if a['img'].startswith('plaat-'):
        p = PBY.get(a['img'][6:]); return p['plate'] if p else D['img']['omslag']
    return D['img'].get(a['img'], D['img']['omslag'])
def faq_html(items, h='h2', title=None):
    out = ('<%s style="margin-bottom:18px">%s</%s>' % (h, esc(title), h)) if title else ''
    out += '<div class="faq">' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in items) + '</div>'
    return out
def ld_faq(items): return {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}
def ld_itemlist(ls, lang): return {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + u_loc(l, lang), 'name': l['name']} for i, l in enumerate(ls)]}

def nearby(l, n=3):
    def dist(a, b): return math.hypot((a['lat'] - b['lat']) * 111, (a['lng'] - b['lng']) * 111 * math.cos(math.radians(a['lat'])))
    return sorted([x for x in LOCS if x['prov'] != l['prov']], key=lambda x: dist(l, x))[:n]

# ================= pagina's =================
exec(open(os.path.join(HERE, 'home_book.py')).read())

def build_prov(P, lang):
    nl = lang == 'nl'; pn = pname(P, lang); ls = in_prov(P['id'])
    intro2, faq = prov_text(P, lang)
    v = [l['pz']['p2'] for l in ls]
    items = [(T[lang]['home'], u_home(lang)), (pn, None)]
    h = ('<section class="dark hero"><div class="wrap">%s<div class="grid" style="margin-top:22px"><div class="txt"><p class="k">%s %s</p><h1>%s</h1><p class="sub">%s</p><p class="lead">%s</p><p class="lead">%s</p></div>'
         '<figure>%s</figure></div></div></section>') % (
        crumbs(items), 'Hoofdstuk' if nl else 'Chapter', P['ch'], ('Restaurant met overnachting in ' if nl else 'Dine and stay in ') + pn,
        ('Waar wij in %s eten en blijven slapen' if nl else 'Where we dine and sleep in %s') % pn, esc(P['intro'][lang]), esc(intro2),
        pic(P['plate'], ('Illustratie van het landschap van ' if nl else 'Illustration of the landscape of ') + pn, '(max-width: 760px) 100vw, 380px', lazy=False, prio=True, cls='framed'))
    rows = ''
    for i, l in enumerate(ls):
        rows += ('<article class="row"><div class="n">%d</div><div class="in"><a class="ph" href="%s">%s</a><div style="display:grid;gap:10px;align-content:start">'
                 '<p class="k">%s</p><div class="hd"><h2><a href="%s" style="color:inherit;text-decoration:none">%s</a></h2><span class="score"><b>%s</b><small>%s</small></span></div>'
                 '<p class="meta">%s · %s</p>%s<p class="tag">%s</p><p>%s</p><p class="meta">%s</p><p class="links"><a class="btn" href="%s">%s</a></p></div></div></article>') % (
            i + 1, u_loc(l, lang), pic(l['img'], l['name'] + ', ' + l['place'], '(max-width: 760px) 100vw, 520px', lazy=i > 0, prio=i == 0), esc(l['type'][lang]), u_loc(l, lang), esc(l['name']),
            num(total(l), lang), T[lang]['ourscore'], esc(l['place']), p2(l, lang), chips(l, lang), esc(l['tag'][lang]), esc(l['kort'][lang]), esc((l['rooms'] or {}).get(lang) or ''),
            u_loc(l, lang), T[lang]['read'])
    rows += ('<article class="row"><div class="n">%d</div><div class="open"><h2 style="font-size:30px">%s %d</h2><p>%s</p><p class="links">%s</p></div></article>') % (
        len(ls) + 1, 'Plek' if nl else 'Place', len(ls) + 1, 'We zijn dit nog aan het testen.' if nl else 'We are still testing this one.',
        '<a href="/zo-kiezen-wij/#tip">Tip ons een adres in %s</a>' % pn if nl else '<a href="/zo-kiezen-wij/#tip">Suggest an address (form in Dutch)</a>')
    h += '<section class="sec"><div class="wrap split"><div style="min-width:0">%s<div style="border-top:1px solid var(--line)"></div></div><aside class="side" style="display:grid;gap:14px"><p class="k">%s</p>%s<p class="meta">%s</p></aside></div></section>' % (
        rows, ('Kaart · ' if nl else 'Map · ') + pn, svg_map(lang, only=P['id']), ('Voor twee: %s tot %s' if nl else 'For two: %s to %s') % (eur(min(v), lang), eur(max(v), lang)))
    # interne links: verhalen, thema's, buren
    extra = ''
    ps = posts_of_prov(P['id']) if nl else []
    if ps: extra += '<div class="stack"><p class="k">Verhalen</p><h2>Lees ook</h2><div class="cards">%s</div></div>' % ''.join(post_card(a) for a in ps[:3])
    ths = [th for th in THEMES if any(l in th['locs'] for l in ls)] if nl else []
    if ths: extra += '<div class="stack"><p class="k">Lijsten</p><h2>%s in onze lijsten</h2><div class="minis">%s</div></div>' % (pn, ''.join('<a class="mini" href="/%s/">%s<span><b>%s</b><span>%s</span></span></a>' % (th['slug'], pic((([l for l in ls if l in th['locs']] or th['locs'])[0]).get('th') or th['locs'][0]['img'], '', '76px', widths=(480,)), esc(th['nav']), esc(lst([l['name'] for l in ls if l in th['locs']], lang))) for th in ths))
    i = PROV_ORDER.index(P); prv, nxt = PROV_ORDER[i - 1], PROV_ORDER[(i + 1) % len(PROV_ORDER)]
    extra += '<div class="stack"><p class="k">%s</p><div class="minis">%s</div></div>' % ('Verder bladeren' if nl else 'Keep browsing', ''.join(
        '<a class="mini" href="%s">%s<span><b>%s</b><span>%s</span></span></a>' % (u_prov(q['id'], lang), pic(q['thumb'], '', '76px', widths=(480,)), esc(('Restaurant met overnachting in ' if nl else 'Dine and stay in ') + pname(q, lang)), lab) for q, lab in ((prv, 'Vorig hoofdstuk' if nl else 'Previous chapter'), (nxt, 'Volgend hoofdstuk' if nl else 'Next chapter'))))
    h += '<section class="sec alt"><div class="wrap" style="display:grid;gap:48px">%s</div></section>' % extra
    h += '<section class="sec white"><div class="narrow">%s</div></section>' % faq_html(faq, title=('Veelgestelde vragen over dineren en slapen in ' if nl else 'Questions about dining and staying in ') + pn)
    t1 = ('Restaurant met overnachting %s: onze adressen (2026)' if nl else 'Restaurants with rooms in %s (2026)') % pn
    if len(t1) > 60: t1 = ('Restaurant met overnachting %s (2026)' if nl else 'Restaurants with rooms, %s (2026)') % pn
    st = len([l for l in ls if l['ms']])
    desc = (('%d adressen in %s waar wij dineren en blijven slapen%s. Voor twee reken je op %s tot %s, met diner en ontbijt.' % (len(ls), pn, (', %d met een Michelinster' % st) if st else '', eur(min(v)), eur(max(v)))) if nl else
            ('%d places in %s where we dine and stay the night%s. For two, count on %s to %s with dinner and breakfast.' % (len(ls), pn, (', %d with a Michelin star' % st) if st else '', eur(min(v), 'en'), eur(max(v), 'en'))))
    page(u_prov(P['id'], lang), lang, t1, desc, h, 'prov', {'nl': u_prov(P['id'], 'nl'), 'en': u_prov(P['id'], 'en')},
         [ld_crumbs(items), ld_itemlist(ls, lang), ld_faq(faq), {'@type': 'CollectionPage', 'name': t1, 'url': SITE + u_prov(P['id'], lang), 'inLanguage': 'nl-NL' if nl else 'en-GB'}], og=og_img(P['plate']), prio=0.9)

def build_loc(l, lang):
    nl = lang == 'nl'; P = PBY[l['prov']]; pn = pname(P, lang)
    items = [(T[lang]['home'], u_home(lang)), (pn, u_prov(P['id'], lang)), (l['name'], None)]
    cred = ('<figcaption>%s%s</figcaption>' % ('<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (esc(l['credu']), esc(l['cred'])) if l.get('credu') else esc(l.get('cred') or ''), (' · <a href="%s" rel="license nofollow noopener" target="_blank">%s</a>' % (esc(l['licu']), esc(l['lic']))) if l.get('licu') and l.get('lic') and l['lic'] not in l['cred'] else '')) if l.get('cred') else ('<figcaption>%s</figcaption>' % ('Illustratie' if nl else 'Illustration') if l.get('ill') else '')
    host = l.get('host') or re.sub(r'^https?://(www\.)?', '', l['web']).strip('/')
    h = ('<section class="dark hero"><div class="wrap">%s<div class="grid" style="margin-top:22px"><div class="txt"><p class="k">%s</p><h1>%s</h1><p class="meta" style="color:#C9CFC4">%s · %s · %s %d</p>%s<p class="sub">%s</p>'
         '<p class="links"><a class="btn" href="%s" rel="noopener" target="_blank">%s</a><a href="#verslag">%s</a></p></div><figure style="flex:1 1 460px">%s%s</figure></div></div></section>') % (
        crumbs(items), esc(l['type'][lang]), esc(l['name']), esc(l['place']), esc(pn), ('nummer' if nl else 'number'), RANK[l['id']], chips(l, lang, 6), esc(l['tag'][lang]),
        esc(l['web']), ('Naar ' if nl else 'Visit ') + esc(host), 'Lees ons verslag' if nl else 'Read our review',
        pic(l['img'], l['name'] + ', ' + l['place'], '(max-width: 760px) 100vw, 640px', lazy=False, prio=True, cls='framed'), cred)
    paras = ''.join('<p>%s</p>' % esc(p) for p in l['rev'][lang].split('\n\n') if p.strip())
    let = ('<div class="note"><p class="k" style="margin-bottom:6px">%s</p><p>%s</p></div>' % ('Goed om te weten' if nl else 'Good to know', esc(l['let'][lang]))) if l.get('let') else ''
    facts = price_facts(l, lang)
    if l.get('rooms'): facts.append(('Kamers' if nl else 'Rooms', l['rooms'][lang]))
    if l.get('people'): facts.append(('Aan het roer' if nl else 'In charge', l['people']))
    facts.append(('Ligging' if nl else 'Location', '%s, %s' % (l['place'], pn)))
    facts.append(('Reserveren' if nl else 'Booking', ('Rechtstreeks via ' if nl else 'Directly via ') + host))
    dl = ''.join('<dt>%s</dt><dd>%s</dd>' % (esc(k), esc(v)) for k, v in facts)
    sc = l['sc']
    bars = ''.join('<div class="b"><div class="t"><span>%s</span><b>%s</b></div><div class="l"><i style="width:%d%%"></i></div><span>%s</span></div>' % (k, num(sc[x], lang), max(6, min(100, (sc[x] - 5.5) / 4.5 * 100)), d) for x, k, d in (
        ('e', 'Eten' if nl else 'Food', 'Wat er op tafel komt en hoe de avond loopt.' if nl else 'What comes to the table and how the evening goes.'),
        ('s', 'Slapen' if nl else 'Stay', 'De kamer, het bed, de rust en het ontbijt.' if nl else 'The room, the bed, the quiet and breakfast.'),
        ('p', 'Prijs' if nl else 'Price', 'Hoe hoger, hoe vriendelijker de prijs voor twee.' if nl else 'The higher, the kinder the price for two.')))
    h += ('<section class="sec" id="verslag"><div class="wrap split">'
          '<div class="stack prose" style="min-width:0;max-width:760px"><p class="k">%s</p><h2>%s</h2>%s%s'
          '<h2 style="margin-top:34px">%s</h2><dl class="facts">%s</dl><p class="meta">%s</p></div>'
          '<aside class="stack" style="min-width:0"><div style="display:flex;gap:16px;align-items:center"><span class="score" style="width:92px;height:92px"><b style="font-size:36px">%s</b><small>%s</small></span><p class="meta">%s</p></div><div class="bars" style="grid-template-columns:1fr">%s</div>%s</aside></div></section>') % (
        'Uit ons dagboek' if nl else 'From our diary', ('Dineren en slapen bij ' if nl else 'Dining and staying at ') + esc(l['name']), paras, let,
        'Prijs en praktisch' if nl else 'Price and practicalities', dl,
        'Gerekend met hun eigen site en boekingssysteem, voor een doordeweekse nacht in november 2026. Kijk voor jouw datum bij het adres zelf.' if nl else 'Worked out from their own website and booking system for a weeknight in November 2026. Check your own date with the address.',
        num(total(l), lang), T[lang]['ourscore'], (('Nummer %d van de %d adressen in Nederland, nummer %d in %s.' if nl else 'Number %d of %d addresses in the Netherlands, number %d in %s.') % (RANK[l['id']], len(LOCS), in_prov(l['prov']).index(l) + 1, pn)), bars,
        svg_map(lang, only=l['prov']))
    # interne links
    ex = ''
    sib = [x for x in in_prov(l['prov']) if x is not l]
    ex += '<div class="stack"><p class="k">%s</p><h2>%s</h2><div class="minis">%s</div><p><a href="%s">%s</a></p></div>' % (
        'Dezelfde provincie' if nl else 'Same province', ('Ook in ' if nl else 'Also in ') + esc(pn), ''.join(mini(x, lang) for x in sib), u_prov(P['id'], lang), ('Alle adressen: restaurant met overnachting in ' if nl else 'All addresses: dine and stay in ') + esc(pn))
    ex += '<div class="stack"><p class="k">%s</p><h2>%s</h2><div class="minis">%s</div></div>' % ('In de buurt' if nl else 'Nearby', 'Net over de grens van de provincie' if nl else 'Just across the provincial border', ''.join(mini(x, lang) for x in nearby(l)))
    if nl:
        ps = posts_of_loc(l['id']); ths = themes_of(l)
        if ps: ex += '<div class="stack"><p class="k">Verhalen</p><h2>%s in onze verhalen</h2><div class="cards">%s</div></div>' % (esc(l['name']), ''.join(post_card(a) for a in ps))
        if ths or RANK[l['id']] <= 10:
            li = ''.join('<li><a href="/%s/">%s</a></li>' % (th['slug'], esc(th['nav'])) for th in ths)
            if RANK[l['id']] <= 10: li = '<li><a href="/top-10/">Top 10 dineren en slapen: nummer %d</a></li>' % RANK[l['id']] + li
            ex += '<div class="stack"><p class="k">Lijsten</p><h2>Staat ook in</h2><ul style="margin:0;padding-left:20px;display:grid;gap:6px;font:500 16px var(--sans)">%s</ul></div>' % li
    h += '<section class="sec alt"><div class="wrap" style="display:grid;gap:48px">%s</div></section>' % ex
    title = ('%s, %s: diner met overnachting' if nl else '%s, %s: dine and stay') % (l['name'], l['place'])
    if len(title) > 60: title = ('%s: diner met overnachting' if nl else '%s: dine and stay') % l['name']
    if len(title) > 60: title = l['name']
    tag = l['tag'][lang].rstrip('.:')
    desc = '%s. %s%s %s.' % (tag, (stars(l['ms'], lang) + (', ' if nl else ', ')) if l['ms'] else '', ('voor twee ca. ' if nl else 'for two approx. ') + eur(l['pz']['p2'], lang) if l['ms'] else (('Voor twee ca. ' if nl else 'For two approx. ') + eur(l['pz']['p2'], lang)), 'met diner en ontbijt, ons verslag en cijfers' if nl else 'with dinner and breakfast, our review and scores')
    if len(desc) > 158: desc = '%s. %s %s.' % (tag, ('Voor twee ca. ' if nl else 'For two approx. ') + eur(l['pz']['p2'], lang), 'met diner en ontbijt' if nl else 'with dinner and breakfast')
    if len(desc) < 75: desc += ' ' + ('Ons verslag, onze cijfers en wat je kwijt bent.' if nl else 'Our review, our scores and the price.')
    biz = {'@type': ['LodgingBusiness', 'Restaurant'], '@id': SITE + u_loc(l, 'nl') + '#adres', 'name': l['name'], 'url': l['web'], 'sameAs': [l['web']],
           'image': og_img(l['img']), 'address': {'@type': 'PostalAddress', 'addressLocality': l['place'], 'addressRegion': P['name'], 'addressCountry': 'NL'},
           'geo': {'@type': 'GeoCoordinates', 'latitude': round(l['lat'], 5), 'longitude': round(l['lng'], 5)}, 'priceRange': '€' * l['pz']['cls'], 'servesCuisine': 'Fine dining' if l['ms'] else 'Modern',
           'review': {'@type': 'Review', 'author': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'datePublished': TODAY, 'inLanguage': 'nl-NL' if nl else 'en-GB',
                      'reviewRating': {'@type': 'Rating', 'ratingValue': num(total(l), 'en'), 'bestRating': '10', 'worstRating': '1'}, 'reviewBody': l['kort'][lang]}}
    if l['ms']: biz['award'] = stars(l['ms'], 'en') + ' (Michelin Guide Netherlands 2026)'
    page(u_loc(l, lang), lang, title, desc, h, 'prov', {'nl': u_loc(l, 'nl'), 'en': u_loc(l, 'en')}, [ld_crumbs(items), biz], og=og_img(l['img']), prio=0.8, ptype='article')

def build_top(lang):
    nl = lang == 'nl'; ls = ORDER[:10]
    items = [(T[lang]['home'], u_home(lang)), ('Top 10', None)]
    provs = sorted({PBY[l['prov']]['name'] if nl else PBY[l['prov']]['en'] for l in ls})
    starred = len([l for l in ls if l['ms']]); cheap = min(ls, key=lambda l: l['pz']['p2'])
    h = '<section class="dark hero"><div class="wrap">%s<div class="txt" style="margin-top:22px;max-width:820px;display:grid;gap:18px"><p class="k">%s</p><h1>%s</h1><p class="sub">%s</p><p class="lead">%s</p></div></div></section>' % (
        crumbs(items), 'De lijst · editie 2026' if nl else 'The list · 2026 edition', 'Top 10 restaurants met overnachting in Nederland' if nl else 'Top 10 restaurants with rooms in the Netherlands',
        'Tien adressen waar de avond aan tafel en de nacht in huis samen de reis waard zijn' if nl else 'Ten places where the evening at the table and the night upstairs are worth the trip together',
        ('Dit is onze eigen lijst, op volgorde van onze drie cijfers: eten, slapen en prijs. %d van de tien hebben een Michelinster, ze liggen in %d provincies, en het voordeligste adres in de lijst is %s, %s.' % (starred, len(provs), cheap['name'], p2(cheap, lang))) if nl else
        ('Our own list, in order of our three scores: food, stay and price. %d of the ten hold a Michelin star, they are spread over %d provinces, and the most affordable is %s, %s.' % (starred, len(provs), cheap['name'], p2(cheap, lang))))
    rows = ''
    for i, l in enumerate(ls):
        rows += ('<article class="row"><div class="n">%d</div><div class="in"><a class="ph" href="%s">%s</a><div style="display:grid;gap:10px;align-content:start"><p class="k">%s</p><div class="hd"><h2><a href="%s" style="color:inherit;text-decoration:none">%s</a></h2><span class="score"><b>%s</b><small>%s</small></span></div>'
                 '<p class="meta">%s · <a href="%s">%s</a> · %s</p>%s<p class="tag">%s</p><p><strong style="font:600 12px var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--gold2)">%s</strong> %s</p><p class="links"><a class="btn" href="%s">%s</a></p></div></div></article>') % (
            i + 1, u_loc(l, lang), pic(l['img'], l['name'], '(max-width: 760px) 100vw, 520px', lazy=i > 0, prio=i == 0), esc(l['type'][lang]), u_loc(l, lang), esc(l['name']), num(total(l), lang), T[lang]['ourscore'],
            esc(l['place']), u_prov(l['prov'], lang), esc(pname(PBY[l['prov']], lang)), p2(l, lang), chips(l, lang), esc(l['tag'][lang]), 'Waarom wij gaan' if nl else 'Why we go', esc(l['kort'][lang]), u_loc(l, lang), T[lang]['read'])
    h += '<section class="sec"><div class="wrap">%s<div style="border-top:1px solid var(--line)"></div><p class="meta" style="margin-top:20px">%s</p></div></section>' % (
        rows, ('Hoe we tot deze volgorde komen, lees je op <a href="/zo-kiezen-wij/">Zo kiezen wij</a>.' if nl else 'How we arrive at this order is explained on <a href="/zo-kiezen-wij/">How we choose</a> (in Dutch).'))
    t1 = 'Top 10 restaurants met overnachting in Nederland (2026)' if nl else 'Top 10 restaurants with rooms in the Netherlands (2026)'
    desc = ('Onze top 10 van adressen waar je dineert en blijft slapen, met %s op één. Met onze cijfers, de prijs voor twee en waarom wij er heen gaan.' % ls[0]['name']) if nl else \
           ('Our top 10 places to dine and stay the night in the Netherlands, with %s at number one. With our scores, the price for two and why we go.' % ls[0]['name'])
    page(u_top(lang), lang, t1, desc, h, 'top', {'nl': u_top('nl'), 'en': u_top('en')}, [ld_crumbs(items), ld_itemlist(ls, lang)], og=og_img(ls[0]['img']), prio=0.9)

def build_theme(th):
    ls = th['locs']; n = len(ls)
    items = [('Home', '/'), (th['nav'], None)]
    provs = sorted({PBY[l['prov']]['name'] for l in ls})
    v = [l['pz']['p2'] for l in ls]
    h = '<section class="dark hero"><div class="wrap">%s<div class="txt" style="margin-top:22px;max-width:820px;display:grid;gap:18px"><p class="k">Lijst</p><h1>%s</h1><p class="lead">%s</p><p class="lead">%s</p></div></div></section>' % (
        crumbs(items), esc(th['h1']), esc(th['intro']), esc('%d adressen in %d provincies. Voor twee ben je %s tot %s kwijt voor diner, een nacht en ontbijt.' % (n, len(provs), eur(min(v)), eur(max(v)))))
    rows = ''
    for i, l in enumerate(ls):
        rows += ('<article class="row"><div class="n">%d</div><div class="in"><a class="ph" href="%s">%s</a><div style="display:grid;gap:10px;align-content:start"><p class="k">%s</p><div class="hd"><h2><a href="%s" style="color:inherit;text-decoration:none">%s</a></h2><span class="score"><b>%s</b><small>ons cijfer</small></span></div>'
                 '<p class="meta">%s · <a href="%s">%s</a> · %s</p>%s<p>%s</p><p class="links"><a class="btn" href="%s">Lees ons verslag</a></p></div></div></article>') % (
            i + 1, u_loc(l, 'nl'), pic(l['img'], l['name'], '(max-width: 760px) 100vw, 520px', lazy=i > 0, prio=i == 0), esc(l['type']['nl']), u_loc(l, 'nl'), esc(l['name']), num(total(l)),
            esc(l['place']), u_prov(l['prov'], 'nl'), esc(PBY[l['prov']]['name']), p2(l, 'nl'), chips(l, 'nl'), esc(l['kort']['nl']), u_loc(l, 'nl'))
    others = ''.join('<a class="mini" href="/%s/">%s<span><b>%s</b><span>%d adressen</span></span></a>' % (o['slug'], pic(o['locs'][0].get('th') or o['locs'][0]['img'], '', '76px', widths=(480,)), esc(o['nav']), len(o['locs'])) for o in THEMES if o is not th)
    h += '<section class="sec"><div class="wrap">%s<div style="border-top:1px solid var(--line)"></div></div></section><section class="sec alt"><div class="wrap stack"><p class="k">Meer lijsten</p><div class="minis">%s<a class="mini" href="/top-10/">%s<span><b>Top 10</b><span>Onze tien favorieten</span></span></a></div></div></section>' % (rows, others, pic(ORDER[0].get('th') or ORDER[0]['img'], '', '76px', widths=(480,)))
    faq = [('Hoeveel adressen staan in deze lijst?', '%d adressen in %s.' % (n, lst(provs, 'nl'))), ('Wat kost het voor twee?', 'Van %s bij %s tot %s bij %s, voor diner, een nacht en ontbijt.' % (eur(min(v)), min(ls, key=lambda l: l['pz']['p2'])['name'], eur(max(v)), max(ls, key=lambda l: l['pz']['p2'])['name']))]
    h += '<section class="sec white"><div class="narrow">%s</div></section>' % faq_html(faq, title='Kort gezegd')
    page('/%s/' % th['slug'], 'nl', th['title'].format(n=n), th['desc'].format(n=n), h, '', None, [ld_crumbs(items), ld_itemlist(ls, 'nl'), ld_faq(faq)], og=og_img(ls[0]['img']), prio=0.8)

def build_blog_index():
    items = [('Home', '/'), ('Verhalen', None)]
    h = ('<section class="dark hero"><div class="wrap">%s<div class="txt" style="margin-top:22px;max-width:820px;display:grid;gap:18px"><p class="k">Verhalen</p><h1>Verhalen over eten, slapen en wat het kost</h1>'
         '<p class="lead">Hier schrijven we op wat niet op één adres past: wat een avond echt kost, wanneer een arrangement loont, en waar je per regio het best eet en blijft slapen.</p></div></div></section>') % crumbs(items)
    h += '<section class="sec"><div class="wrap"><div class="cards">%s</div></div></section>' % ''.join(post_card(a) for a in POSTS)
    h += ('<section class="sec alt"><div class="narrow stack"><h2>Samenwerken</h2><p>Soms schrijven we een verhaal samen met een partner, zoals een wijnhuis of een streek. Dat staat er dan bovenaan bij: In samenwerking met. Links in zo\'n verhaal zijn gemarkeerd als gesponsord. Een plek in het boek, in de top 10 of in onze cijfers kun je niet kopen.</p>'
          '<p class="links"><a href="/net-niet/">Adressen die het net niet haalden</a><a href="/zo-kiezen-wij/">Zo kiezen wij</a></p></div></section>')
    page('/verhalen/', 'nl', 'Verhalen over dineren en slapen: prijzen, tips en regio\'s', 'Wat kost een diner met overnachting, wanneer loont een arrangement en waar eet en slaap je per regio het best? Onze verhalen, met eigen cijfers.', h, 'blog', None,
         [ld_crumbs(items), {'@type': 'Blog', 'name': 'Verhalen van Dineren en Slapen', 'url': SITE + '/verhalen/', 'blogPost': [{'@type': 'BlogPosting', 'headline': a['title']['nl'], 'url': SITE + u_post(a['slug'])} for a in POSTS]}], prio=0.7)

def build_post(a):
    items = [('Home', '/'), ('Verhalen', '/verhalen/'), (a['title']['nl'], None)]
    done = set(); body = ''
    for b in a['body']:
        if b['t'] == 'h2': body += '<h2>%s</h2>' % esc(b['x'])
        elif b['t'] == 'p': body += '<p>%s</p>' % autolink(b['x'], done)
        elif b['t'] == 'note': body += '<p class="note">%s</p>' % autolink(b['x'], done)
        elif b['t'] in ('ul', 'ol'): body += '<%s>%s</%s>' % (b['t'], ''.join('<li>%s</li>' % autolink(x, done) for x in b['items']), b['t'])
    rel = [LBY[x] for x in POST_LOCS[a['slug']] if x in LBY][:6]
    nx = next((p for p in POSTS if p['slug'] == a['next']), POSTS[0])
    src = ''.join('<li><a href="%s" rel="nofollow noopener" target="_blank">%s</a></li>' % (esc(u), esc(t)) for t, u in a.get('sources', []))
    faq = [tuple(x) for x in a['faq']]
    h = ('<article><header class="dark hero"><div class="narrow" style="display:grid;gap:18px">%s<p class="k" style="margin-top:14px">%s</p><h1 style="font-size:clamp(36px,7vw,60px)">%s</h1><p class="sub" style="color:#E3E6DD">%s</p><p class="meta" style="color:#B9C2B4">Door Dineren en Slapen · <time datetime="%s">%s</time> · %d min lezen</p></div></header>'
         '<div class="sec" style="padding-top:48px"><div class="narrow prose">%s</div><div class="narrow" style="margin-top:44px;display:grid;gap:36px"><section class="stack"><p class="k">De adressen uit dit verhaal</p><div class="minis">%s</div></section>%s%s'
         '<a class="card dark" href="%s" style="padding:22px 24px;background:var(--g);color:var(--c)"><span class="k">Lees ook</span><span class="cn" style="margin-top:6px">%s</span></a></div></div></article>') % (
        crumbs(items), esc(a['kicker']['nl']), esc(a['title']['nl']), esc(a['lead']['nl']), a['date'], a['dateTxt']['nl'], a['min'], body, ''.join(mini(l, 'nl') for l in rel),
        '<section>%s</section>' % faq_html(faq, title='Kort gezegd'), ('<section class="stack"><p class="k">Bronnen</p><ul style="margin:0;padding-left:18px;font:400 14px/1.6 var(--sans)">%s</ul></section>' % src) if src else '',
        u_post(nx['slug']), esc(nx['title']['nl']))
    ld = [ld_crumbs(items), ld_faq(faq), {'@type': 'BlogPosting', 'headline': a['title']['nl'], 'description': a['metaDesc'], 'datePublished': a['date'], 'dateModified': a['date'], 'inLanguage': 'nl-NL',
          'author': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'mainEntityOfPage': SITE + u_post(a['slug']), 'image': og_img(post_img(a)),
          'about': [{'@type': 'LodgingBusiness', 'name': l['name'], 'url': SITE + u_loc(l, 'nl')} for l in rel]}]
    page(u_post(a['slug']), 'nl', a['metaTitle'], a['metaDesc'], h, 'blog', None, ld, og=og_img(post_img(a)), prio=0.7, ptype='article')

def build_keur():
    items = [('Home', '/'), ('Zo kiezen wij', None)]
    s1 = len([l for l in LOCS if l['ms'] == 1]); s2 = len([l for l in LOCS if l['ms'] == 2]); s3 = len([l for l in LOCS if l['ms'] == 3])
    bib = len([l for l in LOCS if l['bib']]); gms = len([l for l in LOCS if l['gm']]); keys = len([l for l in LOCS if l['keys']])
    cheap = min(LOCS, key=lambda l: l['pz']['p2']); dear = max(LOCS, key=lambda l: l['pz']['p2'])
    prov_opts = ''.join('<option value="%s">%s</option>' % (p['id'], p['name']) for p in PROV_ORDER)
    h = ('<section class="dark hero"><div class="wrap">%s<div class="txt" style="margin-top:22px;max-width:820px;display:grid;gap:18px"><p class="k">Leeswijzer</p><h1>Zo kiezen wij: onze regels, cijfers en keurmerken</h1>'
         '<p class="lead">Sterren, sleutels en punten komen van de gidsen. De cijfers bij elk adres komen van ons. Hier lees je wat wat is, hoe wij tot een cijfer komen en wanneer een adres in het boek komt.</p>'
         '<nav class="toc" aria-label="Op deze pagina"><a href="#wie">Wie wij zijn</a><a href="#regels">Zo kiezen wij</a><a href="#cijfers">Onze cijfers</a><a href="#keurmerken">Keurmerken</a><a href="#tip">Tip ons</a><a href="#vragen">Vragen</a></nav></div></div></section>') % crumbs(items)
    h += ('<section class="sec" id="wie"><div class="narrow prose stack"><p class="k">Wie wij zijn</p><h2>Eigenlijk is dit gewoon ons dagboek</h2>'
          '<p>Wij gaan graag uit eten. En het liefst blijven we daarna slapen, zodat niemand hoeft te rijden en de avond niet ophoudt als de rekening komt. Daar rijden we met plezier een eind voor om.</p>'
          '<p>We zijn geen inspecteurs. We zijn liefhebbers. Ergens naartoe gaan, daar luxe dineren en dan boven in een goed bed stappen: daar worden wij gelukkig van. Daarom schrijven we het op, zodat we later kunnen teruglezen waar we waren en of we er nog eens heen willen.</p>'
          '<p>Je leest hier dus een mening. De onze. Wie liever strak en modern slaapt dan in een bedstee, zal het niet altijd met ons eens zijn. Dat mag. Daarom schrijven we er steeds bij wat er te vinden is, dan kun je zelf inschatten of het iets voor jou is.</p></div></section>')
    h += ('<section class="sec alt" id="regels"><div class="narrow prose stack"><p class="k">Zo kiezen wij</p><h2>Wanneer een adres in dit boek komt</h2>'
          '<p>De regel is eenvoudig: je eet en je slaapt op hetzelfde adres. Na het dessert de trap op en klaar.</p>'
          '<p>Een hotel waar je voor het diner naar een andere deur moet, valt af. Ook als die deur ernaast zit. Hetzelfde geldt voor een restaurant met kamers een eind verderop. Het kunnen prima plekken zijn, maar ze horen niet in dit boek.</p>'
          '<p>Verder zoeken we huizen met een eigen gezicht: een borg, een havezate, een molen, een herberg waar de eigenaar zelf in de zaak staat. Ketens laten we liggen.</p>'
          '<p>En we houden het klein: per provincie hooguit vier adressen, waar minder keus is drie of twee. Daarachter staat altijd een lege plek. Daar zijn we nog aan het testen.</p>'
          '<p>Adressen die het net niet haalden, zetten we niet op de site. Die delen we alleen in de <a href="/net-niet/">nieuwsbrief</a>.</p></div></section>')
    h += ('<section class="sec" id="cijfers"><div class="narrow prose stack"><p class="k">Onze cijfers</p><h2>Zo komen onze cijfers tot stand</h2>'
          '<p>Bij elk adres staan drie cijfers, van onszelf. Eten telt bij ons iets zwaarder dan de andere twee: %d procent, slapen en prijs elk %d.</p>'
          '<ul><li><strong>Eten.</strong> De avond aan tafel: smaak, het menu, de ontvangst. Een ster helpt, maar een ster eet je niet op.</li><li><strong>Slapen.</strong> De kamer, het bed, de badkamer, de stilte, en het ontbijt de volgende ochtend.</li><li><strong>Prijs.</strong> Wat je voor de avond en de nacht samen betaalt, tegenover wat je krijgt. Een hoog cijfer betekent veel waar voor je geld, niet dat het goedkoop is.</li></ul>'
          '<p>De prijs voor twee is wat twee personen kwijt zijn voor diner, één nacht en ontbijt, zonder drank tenzij die in het menu zit. We rekenen met hun eigen boekingssysteem, voor een doordeweekse nacht in november 2026. Hoe dat uitpakt, lees je in <a href="/verhalen/wat-kost-dineren-en-slapen/">wat een avond uit eten met overnachting kost</a>.</p>'
          '<p>De prijs alleen bepaalt de plek niet. %s is met %s het voordeligste adres en staat op plek %d. %s is het duurste en staat op %d. Bekijk de <a href="/top-10/">top 10</a>.</p></div></section>') % (
        W0['e'], W0['s'], esc(cheap['name']), p2(cheap, 'nl'), RANK[cheap['id']], esc(dear['name']), RANK[dear['id']])
    labs = [('Michelinster', '%d adressen' % (s1 + s2 + s3), 'Eén ster: een keuken die een stop waard is. Twee sterren: een omweg waard. Drie: de reis zelf waard. In dit boek hebben %d adressen één ster, %d twee en %d drie.' % (s1, s2, s3)),
            ('Bib Gourmand', '%d adressen' % bib, 'Goed eten voor een redelijke prijs, volgens de Michelingids.'),
            ('Michelin Sleutel', '%d adressen' % keys, 'De hotelvariant van de ster, voor bijzondere hotels.'),
            ('Gault&Millau', '%d adressen' % gms, 'Punten op een schaal van twintig. Vanaf ongeveer veertien is het een adres om voor om te rijden.')]
    h += '<section class="sec alt" id="keurmerken"><div class="narrow stack"><p class="k">Van de gidsen</p><h2>De keurmerken, in gewone taal</h2><p class="lead">Labels van de gidsen nemen we over zoals ze zijn, volgens de edities van 2026. Wij delen ze niet uit.</p><table class="t"><thead><tr><th>Keurmerk</th><th>In dit boek</th><th>Wat het betekent</th></tr></thead><tbody>%s</tbody></table></div></section>' % ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % x for x in labs)
    h += ('<section class="sec" id="tip"><div class="narrow stack"><p class="k">Tip ons</p><h2>Ken jij een adres?</h2><p>Stuur ons je tip, met een regel erbij waarom we erheen moeten. Dan gaan we kijken. Of het daarna in het boek komt, hangt af van hoe het was.</p>'
          '<div><form class="js-form" data-kind="tip" method="post" action="%s" style="display:grid;gap:14px;font:400 15px var(--sans)">'
          '<input type="hidden" name="_subject" value="Tip: nieuw adres"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"><label>Naam van het adres<input class="inp" style="width:100%%" name="adres" required></label><label>Plaats<input class="inp" style="width:100%%" name="plaats" required></label>'
          '<label>Provincie<select class="inp" style="width:100%%" name="provincie"><option value="">Kies een provincie</option>%s</select></label>'
          '<label>Waarom moeten we erheen?<textarea class="inp" style="width:100%%;height:110px;padding:12px" name="waarom"></textarea></label>'
          '<label>Je e-mailadres (niet verplicht)<input class="inp" style="width:100%%" type="email" name="email" autocomplete="email"></label><button class="btn" type="submit" style="justify-self:start">Verstuur je tip</button></form>'
          '<p class="thanks" role="status">Dank voor je tip. We gaan kijken.</p></div><p class="meta">Liever mailen? Dat kan op <a href="mailto:dinerenenslapen@gmail.com">dinerenenslapen@gmail.com</a>.</p></div></section>') % (esc(FORM_ENDPOINT or '#'), prov_opts)
    faq = [('Tellen reviews van anderen mee in jullie cijfer?', 'Nee. Ons cijfer is van onszelf. Wat anderen schrijven, lezen we graag, maar het telt niet mee.'),
           ('Waarom staat het goedkoopste adres niet bovenaan?', 'Omdat prijs één van de drie cijfers is, en omdat het cijfer voor prijs gaat over wat je ervoor krijgt.'),
           ('Waarom staat een hotel met een goed restaurant ernaast er niet in?', 'Omdat je in dit boek eet en slaapt op hetzelfde adres. Moet je voor het diner door een andere deur, dan valt het af.'),
           ('Kun je een plek in het boek kopen?', 'Nee. Een plek in het boek, in de top 10 of in onze cijfers is niet te koop. Partnerverhalen herken je aan het label In samenwerking met.'),
           ('Hoe vaak verandert de lijst?', 'Als we ergens nog eens zijn geweest, als er een adres bijkomt of als een prijs of keurmerk verandert.')]
    h += '<section class="sec white" id="vragen"><div class="narrow">%s</div></section>' % faq_html(faq, title='Veelgestelde vragen')
    page('/zo-kiezen-wij/', 'nl', 'Zo kiezen wij: onze cijfers en de keurmerken uitgelegd', 'Hoe wij adressen kiezen, wat onze cijfers voor eten, slapen en prijs betekenen, en wat Michelinsterren, Bib Gourmand en Gault&Millau-punten zeggen.', h, 'keur', None, [ld_crumbs(items), ld_faq(faq)], prio=0.6)

def build_net():
    items = [('Home', '/'), ('Net niet', None)]
    h = ('<section class="dark hero"><div class="wrap">%s<div class="grid" style="margin-top:22px"><div class="txt"><p class="k">Net niet</p><h1>Sommige avonden halen het boek niet.</h1><p class="sub">Waar dat was en waarom, lees je alleen in je mail.</p>'
         '<p class="lead">We kijken naar meer adressen dan er in dit boek staan. Soms is de kamer prachtig en valt het eten tegen. Soms is het andersom. Die adressen zetten we niet op de site. Wie zich inschrijft, leest wel waar het was en waarom het net niet was.</p>'
         '<div class="panel">%s<p class="formnote">Eén mail per maand, gratis. Afmelden kan altijd. Je adres geven we aan niemand.</p></div></div><figure>%s</figure></div></div></section>') % (
        crumbs(items), newsletter_form('nl', 'nn').replace('class="btn"', 'class="btn"'), pic(D['img'].get('netniet'), 'Een eetzaal bij avond met kaarsen en een tafel voor twee bij het raam', '(max-width: 760px) 100vw, 380px', lazy=False, prio=True, cls='framed'))
    h += ('<section class="sec"><div class="wrap stack"><p class="k">In je mail</p><h2>Wat je elke maand krijgt</h2><div class="cards">'
          '<div class="card"><div class="bd"><span class="cn">Net niet</span><p>Waar het was en waarom het het boek niet haalde. Met naam en plaats, en met wat er wel goed was.</p></div></div>'
          '<div class="card"><div class="bd"><span class="cn">Nieuw in het boek</span><p>Komt er een adres bij, dan lees je het eerst in de mail. Pas daarna staat het op de site.</p></div></div>'
          '<div class="card"><div class="bd"><span class="cn">Nog aan het testen</span><p>Waar we binnenkort heen gaan. Ben je er al geweest? Antwoord gewoon op de mail.</p></div></div></div></div></section>')
    h += ('<section class="sec alt"><div class="narrow prose stack"><p class="k">Waarom zo</p><h2>Waarom niet gewoon op de site?</h2><p>Omdat één avond niet alles zegt. Een kok kan ziek zijn, een zaterdag te druk. Op een openbare pagina blijft zo\'n oordeel jaren staan, en dat vinden we niet eerlijk tegenover mensen die er elke dag hard voor werken.</p>'
          '<p>In de mail zeggen we wel wat we vonden. Rustig, met uitleg, zonder af te branden. Vaak is een net-niet voor een ander precies goed.</p><p>Is het later beter, dan komt het alsnog in het boek. Ook dat lees je dan eerst in je mail.</p></div></section>')
    faq = [('Hoe vaak krijg ik mail?', 'Eén keer per maand. Soms een keer extra, als iets niet kan wachten.'), ('Noemen jullie echt namen?', 'Ja, in de mail staan naam en plaats.'), ('Wat kost het?', 'Niets.'), ('Wat doen jullie met mijn e-mailadres?', 'We gebruiken het alleen voor deze mail en geven het aan niemand. Afmelden kan onderaan elke mail.')]
    h += '<section class="sec white"><div class="narrow">%s</div></section>' % faq_html(faq, title='Wat je misschien nog wilt weten')
    page('/net-niet/', 'nl', 'Net niet: de adressen die het boek niet haalden', 'Niet elke avond haalt het boek. Waar het net niet was en waarom, lees je alleen in onze maandelijkse nieuwsbrief. Gratis, afmelden met één klik.', h, 'net', None, [ld_crumbs(items), ld_faq(faq)], og=og_img(D['img'].get('netniet')), prio=0.5)

def build_credits():
    items = [('Home', '/'), ('Beeldverantwoording', None)]
    rows = ''.join('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (u_loc(l, 'nl'), esc(l['name']), ('<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (esc(l['credu']), esc(l['cred'].replace('Foto: ', '')))) if l.get('credu') else esc(l['cred']),
                   ('<a href="%s" rel="license nofollow noopener" target="_blank">%s</a>' % (esc(l['licu']), esc(l['lic']))) if l.get('licu') else esc(l.get('lic') or '')) for l in sorted(LOCS, key=lambda x: x['name']) if l.get('cred'))
    h = '<section class="sec"><div class="narrow stack">%s<h1 style="font-size:clamp(36px,6vw,54px)">Beeldverantwoording</h1><p>De tekeningen op deze site zijn voor Dineren en Slapen gemaakt. De foto\'s komen van Wikimedia Commons en worden gebruikt onder de genoemde licentie, met naamsvermelding. Ze zijn bijgesneden.</p><table class="t"><thead><tr><th>Adres</th><th>Foto</th><th>Licentie</th></tr></thead><tbody>%s</tbody></table></div></section>' % (crumbs(items, light=True), rows)
    page('/beeldverantwoording/', 'nl', 'Beeldverantwoording | Dineren en Slapen', 'Wie de foto\'s op Dineren en Slapen maakte en onder welke licentie we ze gebruiken. Alle tekeningen zijn voor deze site gemaakt.', h, '', None, [ld_crumbs(items)], prio=0.2)

def build_privacy():
    items = [('Home', '/'), ('Privacy', None)]
    h = '<section class="sec"><div class="narrow prose stack">%s<h1 style="font-size:clamp(36px,6vw,54px)">Privacy</h1><p>Deze site gebruikt geen tracking-cookies en geen advertentienetwerken. We meten alleen anoniem hoeveel pagina\'s er bekeken worden, zonder dat je te herkennen bent.</p><p>Schrijf je je in voor de nieuwsbrief of stuur je een tip, dan gebruiken we je e-mailadres alleen daarvoor. We verkopen het niet en geven het aan niemand. Afmelden kan onderaan elke mail.</p><p>Wil je weten welke gegevens we van je hebben, of wil je dat we ze verwijderen? Mail ons op <a href="mailto:dinerenenslapen@gmail.com">dinerenenslapen@gmail.com</a>.</p></div></section>' % crumbs(items, light=True)
    page('/privacy/', 'nl', 'Privacy | Dineren en Slapen', 'Geen tracking, geen advertenties. Wat we doen met je e-mailadres als je je inschrijft voor de nieuwsbrief of een tip stuurt.', h, '', None, [ld_crumbs(items)], prio=0.1)

def build_404():
    h = '<section class="sec"><div class="narrow stack"><p class="k">404</p><h1 style="font-size:clamp(36px,6vw,54px)">Deze bladzijde staat niet in het boek</h1><p>Misschien is het adres verhuisd. Begin bij de provincies of de top 10.</p><p class="links"><a class="btn" href="/">Naar de homepage</a><a href="/top-10/">Top 10</a><a href="/verhalen/">Verhalen</a></p></div></section>'
    page('/404.html', 'nl', 'Pagina niet gevonden | Dineren en Slapen', 'Deze pagina bestaat niet (meer). Begin bij de provincies, de top 10 of de verhalen van Dineren en Slapen.', h, '', None, None, noindex=True)

# ================= bestanden voor zoekmachines =================
def write_static():
    for f in os.listdir(os.path.join(HERE, 'fonts')):
        os.makedirs(os.path.join(OUT, 'fonts'), exist_ok=True); shutil.copy(os.path.join(HERE, 'fonts', f), os.path.join(OUT, 'fonts', f))
    # sitemap met hreflang
    urls = []
    for path, lang, alt, prio in PAGES:
        al = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (lg, SITE, u) for lg, u in alt.items()) if len(alt) > 1 else ''
        if len(alt) > 1 and 'nl' in alt: al += '<xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, alt['nl'])
        urls.append('<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%.1f</priority>%s</url>' % (SITE, path, TODAY, prio, al))
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)
    # llms.txt
    L = ['# Dineren en Slapen', '', '> Onafhankelijke Nederlandse gids van restaurants met overnachting: adressen waar je dineert en blijft slapen onder één dak. %d adressen in twaalf provincies, met eigen cijfers voor eten, slapen en prijs, en een prijs voor twee (diner, een nacht en ontbijt, gecheckt in hun eigen boekingssysteem voor een doordeweekse nacht in november 2026).' % len(LOCS), '',
         'Regels: eten en slapen op hetzelfde adres, geen ketens, hooguit vier adressen per provincie. Een plek in het boek is niet te koop.', '', '## Belangrijkste pagina\'s', '',
         '- [Top 10 restaurants met overnachting](%s/top-10/): onze tien favorieten, met %s op één' % (SITE, ORDER[0]['name']), '- [Zo kiezen wij](%s/zo-kiezen-wij/): regels, cijfers en keurmerken uitgelegd' % SITE, '- [Verhalen](%s/verhalen/): prijzen, arrangementen en regio\'s' % SITE, '', '## Per provincie', '']
    for p in PROV_ORDER:
        ls = in_prov(p['id']); v = [l['pz']['p2'] for l in ls]
        L.append('- [Restaurant met overnachting in %s](%s%s): %s. Voor twee %s tot %s.' % (p['name'], SITE, u_prov(p['id'], 'nl'), ', '.join(l['name'] for l in ls), eur(min(v)), eur(max(v))))
    L += ['', '## Adressen', '']
    for l in ORDER:
        L.append('- [%s, %s](%s%s): %s. %s Ons cijfer %s, %s.' % (l['name'], l['place'], SITE, u_loc(l, 'nl'), l['type']['nl'], (stars(l['ms'], 'nl') + '.') if l['ms'] else '', num(total(l)), p2(l, 'nl')))
    L += ['', '## Lijsten', ''] + ['- [%s](%s/%s/): %d adressen' % (th['nav'], SITE, th['slug'], len(th['locs'])) for th in THEMES]
    L += ['', '## Verhalen', ''] + ['- [%s](%s%s): %s' % (a['title']['nl'], SITE, u_post(a['slug']), a['metaDesc']) for a in POSTS]
    L += ['', '## Optional', '', '- [English version](%s/en/): restaurants with rooms in the Netherlands' % SITE]
    open(os.path.join(OUT, 'llms.txt'), 'w').write('\n'.join(L) + '\n')
    # beeldmerk
    open(os.path.join(OUT, 'favicon.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#10231C"/><text x="32" y="45" text-anchor="middle" font-family="Georgia,serif" font-size="40" font-style="italic" fill="#D2AD5C">&amp;</text></svg>')
    for size, name in ((32, 'favicon.ico'), (180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png')):
        im = Image.new('RGB', (size, size), '#10231C')
        from PIL import ImageDraw, ImageFont
        dr = ImageDraw.Draw(im)
        try: ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', int(size * .62))
        except Exception: ft = ImageFont.load_default()
        dr.text((size / 2, size * .52), '&', fill='#D2AD5C', font=ft, anchor='mm')
        im.save(os.path.join(OUT, name), 'ICO' if name.endswith('.ico') else 'PNG')
    json.dump({'name': 'Dineren en Slapen', 'short_name': 'Dineren & Slapen', 'start_url': '/', 'display': 'browser', 'background_color': '#F4F0E6', 'theme_color': '#10231C',
               'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, open(os.path.join(OUT, 'site.webmanifest'), 'w'))
    sp = src_path('omslag')
    if sp:
        im = Image.open(sp).convert('RGB'); W, H = im.size; t = 630 / 1200
        if H / W > t: hh = int(W * t); im = im.crop((0, (H - hh) // 2, W, (H - hh) // 2 + hh))
        im.resize((1200, 630), Image.LANCZOS).save(os.path.join(OUT, 'og.jpg'), quality=82)
    shutil.copy(os.path.join(HERE, 'data', 'geo.js'), os.path.join(OUT, 'geo.js'))
    open(os.path.join(OUT, 'CNAME'), 'w').write('dinerenenslapen.nl\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')

def main():
    keep_img = os.path.join(OUT, 'img')
    if os.path.exists(OUT):
        for f in os.listdir(OUT):
            if f != 'img': (shutil.rmtree if os.path.isdir(os.path.join(OUT, f)) else os.remove)(os.path.join(OUT, f))
    for lang in ('nl', 'en'):
        build_home(lang); build_top(lang)
        for p in PROV_ORDER: build_prov(p, lang)
        for l in LOCS: build_loc(l, lang)
    for th in THEMES: build_theme(th)
    build_blog_index()
    for a in POSTS: build_post(a)
    build_keur(); build_net(); build_credits(); build_privacy(); build_404()
    write_static()
    print('pagina\'s:', len(PAGES), '| thema\'s:', [(t['slug'], len(t['locs'])) for t in THEMES])
    for i in ISSUES: print('  !', i)

if __name__ == '__main__':
    main()
