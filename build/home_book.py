# Homepage als opengeslagen boek. Wordt door build.py ingelezen met exec(), zodat alle helpers beschikbaar zijn.

BLUE = '#2C5A8A'
ARW_L = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M14 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARW_R = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARW_D = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

def n1(v, lang): return num(round(v * 10) / 10, lang)
def cls_txt(l): return '€€€€'[:l['pz']['cls']]
def label_line(l, lang):
    a = []
    if l['ms']: a.append(stars(l['ms'], lang))
    if l['bib']: a.append('Bib Gourmand')
    if l['gm']: a.append(gm(l['gm'], lang))
    if not a and l.get('sel'): a.append('Michelin Gids' if lang == 'nl' else 'Michelin Guide')
    if not a and l.get('other'): a.append(l['other'][0])
    return a
def thumb(l): return l.get('th') or l['img']
def prank(l): return in_prov(l['prov']).index(l) + 1

def book_map(lang):
    nl = lang == 'nl'
    paths, labels, dots = '', '', ''
    for p in PROV_ORDER:
        pn = pname(p, lang)
        paths += '<a href="%s" class="pv" data-p="%s" tabindex="-1" aria-label="%s"><path d="%s"/></a>' % (u_prov(p['id'], lang), p['id'], esc(('Hoofdstuk %s: %s' if nl else 'Chapter %s: %s') % (p['ch'], pn)), p['d'])
        labels += '<text class="lb" x="%s" y="%s" text-anchor="middle">%s</text>' % (p['lx'], p['ly'] + (16 if p['id'] == 'utrecht' else 0), esc(pn.upper()))
    for l in sorted(LOCS, key=lambda x: -RANK[x['id']]):   # beste bovenop
        r = prank(l)
        dots += ('<a href="%s" class="dt%s" tabindex="-1" data-l="%s" data-p="%s" data-x="%.1f" data-y="%.1f" aria-label="%s"><circle cx="%.1f" cy="%.1f" r="4.6"/>'
                 '<text class="dn" x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="central">%d</text></a>') % (
            u_loc(l, lang), ' best' if r == 1 else '', l['id'], l['prov'], l['x'], l['y'],
            esc('%s, %s%s' % (l['name'], l['place'], (', beste van ' + pname(PBY[l['prov']], lang)) if r == 1 and nl else (', best in ' + pname(PBY[l['prov']], lang) if r == 1 else ''))),
            l['x'], l['y'], l['x'], l['y'], r)
    return ('<div class="bmap" id="kaart"><svg viewBox="0 0 600 700" role="group" aria-label="%s"><g class="mv">%s<g class="lbs">%s</g>%s</g></svg>'
            '<div class="tip" aria-hidden="true"></div></div>') % (
        'Kaart van Nederland met de twaalf provincies en alle adressen' if nl else 'Map of the Netherlands with the twelve provinces and every address', paths, labels, dots)

def book_home_pane(lang):
    nl = lang == 'nl'
    toc = ''
    for p in PROV_ORDER:
        c = len(in_prov(p['id']))
        toc += '<a class="toc2" href="%s" data-p="%s"><span class="ch">%s</span><span class="tn">%s</span><span class="ct">%d %s</span></a>' % (
            u_prov(p['id'], lang), p['id'], p['ch'], esc(pname(p, lang)), c, ('adres' if c == 1 else 'adressen') if nl else ('address' if c == 1 else 'addresses'))
    lead = ('Wij gaan graag ergens heen om luxe te dineren en daarna te blijven slapen. In dit boek staan onze %d adressen: borgen, havezaten, kastelen en restaurants met kamers, waar je eet en slaapt onder één dak. Kies links een provincie of sla hieronder een hoofdstuk open.' % len(LOCS)) if nl else \
           ('We love travelling somewhere for a fine dinner and then staying the night. This book holds our %d addresses: manor houses, castles, country estates and restaurants with rooms, where you dine and sleep under one roof. Choose a province on the map or open a chapter below.' % len(LOCS))
    return ('<div class="pane on" data-pane="home"><div class="phd"><span class="k">%s</span><span class="k mute">%s</span></div>'
            '<div class="intro"><div class="tx"><h1>%s</h1><p>%s</p></div>%s</div>'
            '<nav class="tocg" aria-label="%s">%s</nav>'
            '<a class="pl" href="#adressen">%s %s</a></div>') % (
        'Inhoud' if nl else 'Contents', 'Editie 2026' if nl else '2026 edition',
        'Dineren en blijven slapen: de mooiste restaurants met overnachting' if nl else 'Dine and stay the night: the finest restaurants with rooms', esc(lead),
        pic(D['img']['omslag'], 'Illustratie van een gedekte tafel bij een raam met uitzicht op een landgoed' if nl else 'Illustration of a laid table by a window overlooking an estate', '150px', lazy=False, prio=True, cls='cover', widths=(480,)),
        'Inhoud' if nl else 'Contents', toc, 'Zoek op budget of op afstand van huis' if nl else 'Search by budget or distance from home', ARW_D)

def book_prov_pane(P, lang):
    nl = lang == 'nl'; pn = pname(P, lang); ls = in_prov(P['id'])
    rows = ''
    for i, l in enumerate(ls):
        rows += ('<a class="brow" href="%s" data-l="%s"><span class="th">%s<b class="rk%s">%d</b></span><span class="bd"><span class="rn">%s</span><span class="meta">%s</span><span class="tg">%s</span></span><span class="sc">%s</span></a>') % (
            u_loc(l, lang), l['id'], pic(thumb(l), '', '84px', widths=(480,)), ' best' if i == 0 else '', i + 1, esc(l['name']),
            esc(' · '.join([l['place']] + label_line(l, lang)[:1] + [eur(l['pz']['p2'], lang) + (' voor twee' if nl else ' for two')])), esc(l['tag'][lang]), n1(total(l), lang))
    if P.get('open'):
        rows += ('<div class="brow open"><span class="th"><b class="rk">%d</b></span><span class="bd"><span class="rn">%s %d</span><span class="meta">%s <a href="/zo-kiezen-wij/#tip">%s</a></span></span></div>') % (
            len(ls) + 1, 'Plek' if nl else 'Place', len(ls) + 1, 'Dit adres testen we nog.' if nl else 'We are still trying this one out.', 'Tip ons een adres' if nl else 'Suggest an address')
    return ('<div class="pane" data-pane="%s" hidden><div class="phd"><button type="button" class="back" data-home>%s%s</button><span class="k">%s %s</span></div>'
            '%s<h2 tabindex="-1">%s</h2><p class="pi">%s</p><div class="rows">%s</div>'
            '<div class="links2"><a class="pl" href="#adressen" data-scope="%s">%s %s</a><a class="pl" href="%s">%s %s</a></div></div>') % (
        P['id'], ARW_L, 'Inhoud' if nl else 'Contents', 'Hoofdstuk' if nl else 'Chapter', P['ch'],
        pic(P['plate'], ('Illustratie bij het hoofdstuk ' if nl else 'Illustration for the chapter ') + pn, '(max-width: 760px) 100vw, 560px', cls='plate', widths=(480, 960)),
        esc(pn), esc(P['intro'][lang]), rows, P['id'], 'Filter en vergelijk deze adressen' if nl else 'Filter and compare these addresses', ARW_D,
        u_prov(P['id'], lang), ('Het hele hoofdstuk ' if nl else 'The full chapter: ') + esc(pn), ARW_R)

def book(lang):
    nl = lang == 'nl'
    panes = book_home_pane(lang) + ''.join(book_prov_pane(p, lang) for p in PROV_ORDER)
    return ('<section class="bookw" id="boek" aria-label="%s"><div class="book">'
            '<div class="pg pgl"><div class="phd"><span class="k mute" id="maphead" data-home-txt="%s">%s</span><button type="button" class="back" data-home hidden>%s%s</button></div>%s'
            '<div class="pft"><div class="legend"><span><i class="lg"></i>%s</span><span><i class="lg b"></i>%s</span></div><span class="pnum" id="pgl">2</span></div></div>'
            '<div class="pg pgr">%s<div class="pnum r" id="pgr">3</div></div></div></section>') % (
        'Het boek: kaart en inhoud' if nl else 'The book: map and contents', 'Kaart van Nederland' if nl else 'Map of the Netherlands', 'Kaart van Nederland' if nl else 'Map of the Netherlands',
        ARW_L, 'Heel Nederland' if nl else 'All of the Netherlands', book_map(lang),
        'Adres in dit boek' if nl else 'Address in this book', 'Beste van de provincie' if nl else 'Best in the province', panes)

# ---------- verkenner ----------
def explorer(lang):
    nl = lang == 'nl'
    cards = ''
    for l in ORDER:
        P = PBY[l['prov']]; sc = l['sc']
        bars = ''.join('<span class="vb"><span class="vt"><span>%s</span><b data-k="%s">%s</b></span><span class="vl"><i style="width:%d%%"></i></span></span>' % (
            k, x, num(sc[x], lang), max(6, min(100, (sc[x] - 5.5) / 4.5 * 100))) for x, k in (('e', 'Eten' if nl else 'Food'), ('s', 'Slapen' if nl else 'Stay'), ('p', 'Prijs' if nl else 'Price')))
        cards += ('<a class="vcard" href="%s" data-id="%s" data-prov="%s" data-cls="%d" data-ms="%d" data-bib="%d" data-gm="%s" data-hist="%d" data-e="%s" data-s="%s" data-p="%s" data-p2="%s" data-lat="%s" data-lng="%s" data-rank="%d" data-prank="%d">'
                  '<span class="vph">%s<b class="vrk">%d</b><span class="vcl">%s</span><span class="vkm" hidden></span></span>'
                  '<span class="vbd"><span class="vty">%s</span><span class="vhd"><span><span class="cn">%s</span><span class="vwh">%s · %s</span></span><span class="vsc">%s</span></span>'
                  '<span class="vlab">%s</span><span class="vbars">%s</span><span class="vft"><span>%s</span><span class="go">%s</span></span></span></a>') % (
            u_loc(l, lang), l['id'], l['prov'], l['pz']['cls'], l['ms'], l['bib'], l['gm'] or 0, 1 if l.get('hist') else 0, sc['e'], sc['s'], sc['p'], l['pz']['p2'], l['lat'], l['lng'], RANK[l['id']], prank(l),
            pic(thumb(l), '', '(max-width: 760px) 100vw, 380px', widths=(480, 960)), RANK[l['id']], cls_txt(l),
            esc(l['type'][lang]), esc(l['name']), esc(l['place']), esc(pname(P, lang)), n1(total(l), lang),
            esc(' · '.join(label_line(l, lang)[:2])), bars, esc(p2(l, lang)), 'Bekijk adres' if nl else 'View address')
    chip = lambda txt, attrs, on=False: '<button type="button" class="fchip%s" aria-pressed="%s" %s>%s</button>' % (' on' if on else '', 'true' if on else 'false', attrs, txt)
    budget = ''.join(chip(t, 'data-f="max" data-v="%d"' % v, v == 0) for v, t in ((0, 'Alle prijzen' if nl else 'All prices'), (1, ('tot ' if nl else 'up to ') + eur(300, lang)), (2, ('tot ' if nl else 'up to ') + eur(450, lang)), (3, ('tot ' if nl else 'up to ') + eur(700, lang))))
    labs = ''.join(chip(t, 'data-f="lab" data-v="%s"' % v, v == 'all') for v, t in (('all', 'Alles' if nl else 'All'), ('ster', 'Michelinster' if nl else 'Michelin star'), ('bib', 'Bib Gourmand'), ('gm', 'Gault&amp;Millau 15+')))
    labs += chip('Kasteel, borg of landgoed' if nl else 'Castle, manor or estate', 'data-f="hist" data-v="1"')
    radius = ''.join(chip(t, 'data-f="radius" data-v="%d"' % v, v == 0) for v, t in ((0, 'Elke afstand' if nl else 'Any distance'), (50, '&lt; 50 km'), (100, '&lt; 100 km'), (150, '&lt; 150 km')))
    sorts = ''.join(chip(t, 'data-f="sort" data-v="%s"%s' % (v, ' hidden' if v == 'afstand' else ''), v == 'score') for v, t in (('score', 'Onze ranglijst' if nl else 'Our ranking'), ('afstand', 'Afstand' if nl else 'Distance'), ('prijs', 'Prijs, laag naar hoog' if nl else 'Price, low to high'), ('eten', 'Eten' if nl else 'Food'), ('slapen', 'Slapen' if nl else 'Stay')))
    sliders = ''.join('<div class="sl"><label for="w-%s">%s</label><input id="w-%s" type="range" min="0" max="100" step="5" value="%d" data-w="%s"><span class="pct">%d%%</span></div>' % (
        x, k, x, W0[x], x, round(W0[x] / (W0['e'] + W0['s'] + W0['p']) * 100)) for x, k in (('e', 'Eten' if nl else 'Food'), ('s', 'Slapen' if nl else 'Stay'), ('p', 'Prijs' if nl else 'Price')))
    return ('<section class="vk" id="adressen" aria-labelledby="vk-titel" data-lang="%s" data-n="%d"><div class="wrap vkw">'
            '<div class="vkh"><div class="stack0"><p class="k" id="vk-kick">%s</p><h2 id="vk-titel" data-all="%s">%s</h2></div><p class="vlead">%s</p></div>'
            '<div class="fbox">'
            '<div class="fc"><fieldset><legend>%s</legend><div class="chs">%s</div></fieldset><fieldset><legend>%s</legend><div class="chs">%s</div></fieldset></div>'
            '<div class="fc"><label class="lg2" for="vk-adres">%s</label><form class="vkf" id="vk-form"><input id="vk-adres" class="inp" type="text" autocomplete="postal-code" placeholder="%s"><button class="btn" type="submit">%s</button></form>'
            '<button type="button" class="lnk" id="vk-geo">%s</button><p class="fh" id="vk-help">%s</p><p class="fh err" id="vk-err" role="alert" hidden>%s</p>'
            '<div id="vk-home" hidden><p class="fh" role="status"><span id="vk-hometxt"></span> <button type="button" class="lnk" id="vk-clear">%s</button></p><div class="chs" role="group" aria-label="%s">%s</div></div></div>'
            '<div class="fc"><div class="wh"><span class="lg2">%s</span><button type="button" class="lnk" id="vk-resetw" hidden>%s</button></div>%s<p class="fh">%s</p></div>'
            '</div>'
            '<div class="vbar"><div class="chs" role="group" aria-label="%s"><span class="fh">%s</span>%s</div><div class="fh"><span role="status" id="vk-res"></span> <button type="button" class="lnk" id="vk-resetf" hidden>%s</button></div></div>'
            '<div class="vempty" id="vk-empty" hidden><p class="cn">%s</p><p>%s</p></div>'
            '<div class="vgrid" id="vk-grid">%s</div>'
            '<button type="button" class="ghostb" id="vk-more" hidden>%s</button>'
            '<p class="fh">%s</p></div></section>') % (
        lang, len(LOCS), 'Zoek, filter en vergelijk' if nl else 'Search, filter and compare', ('Alle %d adressen, op jouw manier' if nl else 'All %d addresses, your way') % len(LOCS), ('Alle %d adressen, op jouw manier' if nl else 'All %d addresses, your way') % len(LOCS),
        'Je ziet eerst onze eigen ranglijst, op basis van onze cijfers voor eten, slapen en prijs. Liever op prijs van laag naar hoog, of op afstand vanaf huis? Dat kan ook. Aan onze cijfers verandert daardoor niets.' if nl else
        'You first see our own ranking, based on our scores for food, stay and price. Would you rather sort by price, from low to high, or by distance from home? You can do that too. Our scores stay the same either way.',
        'Budget voor twee' if nl else 'Budget for two', budget, 'Erkenning en karakter' if nl else 'Awards and character', labs,
        'Afstand vanaf jouw adres' if nl else 'Distance from your address', 'Postcode of plaats' if nl else 'Postcode or town', 'Toon afstand' if nl else 'Show distance',
        'Of gebruik mijn huidige locatie' if nl else 'Or use my current location',
        'Vul je postcode of woonplaats in en zie bij elk adres hoe ver het is.' if nl else 'Enter your postcode or town to see how far away each address is.',
        'Dat adres vinden we niet. Probeer een postcode (bijvoorbeeld 9711 NR) of een plaatsnaam.' if nl else 'We could not find that address. Try a Dutch postcode (for example 9711 NR) or a town name.',
        'Wis adres' if nl else 'Clear address', 'Straal' if nl else 'Radius', radius,
        'Wat weegt voor jou het zwaarst?' if nl else 'What matters most to you?', 'Herstel' if nl else 'Reset', sliders,
        'Het cijfer in de cirkel is het gewogen gemiddelde van onze drie cijfers: eten, slapen en prijs.' if nl else 'The score in the circle is the weighted average of our three scores: food, stay and price.',
        'Sorteer op' if nl else 'Sort by', 'Sorteer op' if nl else 'Sort by', sorts, 'Wis filters' if nl else 'Clear filters',
        'Geen adressen binnen deze keuze' if nl else 'No addresses match these choices', 'Maak het budget ruimer, kies een grotere straal of haal een filter weg.' if nl else 'Raise the budget, choose a larger radius or remove a filter.',
        cards, ('Toon alle %d adressen' if nl else 'Show all %d addresses') % len(LOCS),
        'Prijzen gelden voor twee personen: diner, een nacht en ontbijt, zonder drank tenzij anders vermeld. We halen ze van de sites van de adressen zelf (oktober 2026). Afstanden zijn hemelsbreed gemeten, nauwkeurig tot op het postcodegebied. Reken voor de rijafstand op ongeveer een derde meer.' if nl else
        'Prices are for two people: dinner, one night and breakfast, without drinks unless stated otherwise. We take them from each address\'s own website (October 2026). Distances are as the crow flies and accurate to the postcode area. By road, allow roughly a third more.')

def home_sections(lang):
    nl = lang == 'nl'
    top = ''.join(('<li><a class="t5" href="%s"><span class="tr">%d</span><span class="tph">%s</span><span class="tb"><span class="cn">%s</span><span class="meta">%s · %s. %s</span></span><span class="tsc">%s</span></a></li>') % (
        u_loc(l, lang), i + 1, pic(thumb(l), '', '108px', widths=(480,)), esc(l['name']), esc(l['place']), esc(pname(PBY[l['prov']], lang)), esc(l['tag'][lang]), n1(total(l), lang)) for i, l in enumerate(ORDER[:5]))
    h = ('<section class="sec2 dark"><div class="wrap two2"><div class="stack0"><p class="k">%s</p><h2>%s</h2><p class="lead">%s</p><p><a class="btn" href="%s">%s</a></p></div><ol class="top5">%s</ol></div></section>') % (
        'De lijst' if nl else 'The list', 'De top 10 van Nederland' if nl else 'The top 10 in the Netherlands',
        'Tien adressen waar de avond aan tafel en de nacht erna samen de reis waard zijn. De volgorde is die van onze eigen cijfers voor eten, slapen en prijs.' if nl else
        'Ten addresses where the evening at the table and the night that follows are worth the journey together. The order follows our own scores for food, stay and price.',
        u_top(lang), 'Bekijk de hele top 10' if nl else 'See the full top 10', top)
    cards = ''
    for p in PROV_ORDER:
        ls = in_prov(p['id'])
        cards += ('<a class="pcard" href="%s" data-p="%s"><span class="pph">%s</span><span class="phd2"><span><span class="ch">%s</span> <span class="cn">%s</span></span><span class="meta">%d %s</span></span><span class="meta best">%s</span></a>') % (
            u_prov(p['id'], lang), p['id'], pic(p['thumb'], ('Illustratie bij het hoofdstuk ' if nl else 'Illustration for the chapter ') + pname(p, lang), '(max-width: 760px) 100vw, 280px', widths=(480,)),
            p['ch'], esc(pname(p, lang)), len(ls), 'adressen' if nl else 'addresses', esc(('Beste van de provincie: ' if nl else 'Best in the province: ') + ls[0]['name']))
    h += ('<section class="sec alt" id="provincies"><div class="wrap" style="display:grid;gap:30px"><div class="stack0"><p class="k">%s</p><h2>%s</h2></div><div class="pgrid">%s</div></div></section>') % (
        'Twaalf hoofdstukken' if nl else 'Twelve chapters', 'Dineren en slapen per provincie' if nl else 'Dine and stay by province', cards)
    stars_n = len([l for l in LOCS if l['ms']])
    keur = [('Ons boek', 'Per adres schrijven we op wat je kunt verwachten: de keuken, de kamers, het huis en wat een avond met overnachting voor twee kost.'),
            ('Zo kiezen wij', 'Je eet en je slaapt onder hetzelfde dak, en het huis heeft een eigen gezicht. Een maximum per provincie is er niet: wat erbij hoort, komt erin. Ketens laten we liggen.'),
            ('Onze cijfers', 'Bij elk adres geven we een cijfer voor eten, slapen en prijs. %d adressen hebben een Michelinster, maar bij ons tellen de nacht en de prijs net zo goed mee als het bord.' % stars_n)] if nl else \
           [('Our book', 'For every address we write down what to expect: the kitchen, the rooms, the house and what dinner with an overnight stay costs for two.'),
            ('How we choose', 'You dine and sleep under one roof, and the house has a character of its own. There is no limit per province: if a place belongs here, it goes in. We leave chains out.'),
            ('Our scores', 'Every address gets a score for food, stay and price. %d addresses hold a Michelin star, but for us the night and the price count just as much as what is on the plate.' % stars_n)]
    h += ('<section class="sec2 dark" id="keurmerken"><div class="wrap stack0"><p class="k">%s</p><h2>%s</h2><dl class="keur">%s</dl><p><a class="btn" href="/zo-kiezen-wij/">%s</a></p></div></section>') % (
        'Leeswijzer' if nl else 'Reading guide', 'Keurmerken en onze cijfers' if nl else 'Guide awards and our scores',
        ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in keur), 'Lees hoe wij kiezen en beoordelen' if nl else 'How we choose and score (in Dutch)')
    return h

HOME_JS = r""";
(function(){
var bk=document.getElementById('boek');if(!bk)return;
var svg=bk.querySelector('.bmap svg'),mv=svg.querySelector('.mv'),tip=bk.querySelector('.tip'),panes=bk.querySelectorAll('.pane'),cur=null;
var BB=%BB%,PN=%PN%,NL=document.documentElement.lang==='nl';
var dots=[].slice.call(svg.querySelectorAll('.dt')),COARSE=window.matchMedia&&matchMedia('(pointer:coarse)').matches;
function zoomOf(id){var b=BB[id],pad=30,s=Math.min(600/(b[2]-b[0]+2*pad),700/(b[3]-b[1]+2*pad),4.4);return{s:s,tx:300-s*(b[0]+b[2])/2,ty:350-s*(b[1]+b[3])/2}}
function place(z,id){
 var pos={},ids=[];
 dots.forEach(function(d){var x=+d.dataset.x,y=+d.dataset.y;pos[d.dataset.l]=[z.s*x+z.tx,z.s*y+z.ty];if(id&&d.dataset.p===id)ids.push(d.dataset.l)});
 var w=svg.getBoundingClientRect().width||500,minD=34*600/w;
 for(var it=0;it<16;it++)for(var i=0;i<ids.length;i++)for(var j=i+1;j<ids.length;j++){var a=pos[ids[i]],c=pos[ids[j]],dx=c[0]-a[0],dy=c[1]-a[1],dd=Math.sqrt(dx*dx+dy*dy);if(dd<minD){if(dd<.01){dx=1;dy=.35;dd=1.06}var p=(minD-dd)/2,ux=dx/dd,uy=dy/dd;a[0]-=ux*p;a[1]-=uy*p;c[0]+=ux*p;c[1]+=uy*p}}
 dots.forEach(function(d){var q=pos[d.dataset.l],x=(q[0]-z.tx)/z.s,y=(q[1]-z.ty)/z.s,inP=id&&d.dataset.p===id,c=d.querySelector('circle'),t=d.querySelector('text');
  c.setAttribute('cx',x.toFixed(2));c.setAttribute('cy',y.toFixed(2));t.setAttribute('x',x.toFixed(2));t.setAttribute('y',y.toFixed(2));
  c.setAttribute('r',((inP?(COARSE?17:13):(id?3:4.6))/z.s).toFixed(2));t.style.fontSize=(12.5/z.s).toFixed(2)+'px';
  d.classList.toggle('in',!!inP);d.classList.toggle('out',!!id&&!inP);d.setAttribute('tabindex',inP?'0':'-1')});
}
function open(id,push,from){
 var prev=cur;cur=id||null;var z=id?zoomOf(id):{s:1,tx:0,ty:0};
 mv.style.transform='translate('+z.tx.toFixed(2)+'px,'+z.ty.toFixed(2)+'px) scale('+z.s.toFixed(4)+')';
 bk.classList.toggle('zoomed',!!id);
 svg.querySelectorAll('.pv').forEach(function(a){a.classList.toggle('sel',a.dataset.p===id)});
 place(z,id);
 panes.forEach(function(p){var on=p.dataset.pane===(id||'home');p.hidden=!on;p.classList.toggle('on',on)});
 var mh=document.getElementById('maphead');mh.textContent=id?(NL?'Hoofdstuk ':'Chapter ')+PN[id][0]+' · '+PN[id][1]:mh.dataset.homeTxt;
 bk.querySelector('.pgl .back').hidden=!id;
 var n=id?4+(PN[id][2]-1)*14:2;document.getElementById('pgl').textContent=n;document.getElementById('pgr').textContent=n+1;
 if(push!==false)try{history.replaceState(null,'',id?'#'+id:location.pathname)}catch(e){}
 document.dispatchEvent(new CustomEvent('des:prov',{detail:id}));
 var pr=bk.querySelector('.pgr'),stacked=pr.getBoundingClientRect().left<bk.getBoundingClientRect().left+60;
 if(id&&from==='toc'&&stacked)pr.scrollIntoView({behavior:'smooth',block:'start'});
 if(from){var f=id?bk.querySelector('.pane.on h2'):(prev?bk.querySelector('.toc2[data-p="'+prev+'"]'):null);if(f)f.focus({preventScroll:from!=='toc'||!stacked})}
}
bk.addEventListener('click',function(e){
 if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button)return;
 var a=e.target.closest('[data-home]');if(a){e.preventDefault();open(null,true,'back');return}
 a=e.target.closest('.pv,.toc2');if(a){if(cur===a.dataset.p&&a.classList.contains('pv'))return;e.preventDefault();open(a.dataset.p,true,a.classList.contains('toc2')?'toc':'map');return}
});
document.querySelectorAll('.pcard').forEach(function(a){a.addEventListener('click',function(e){if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button)return;e.preventDefault();open(a.dataset.p,false);try{history.replaceState(null,'','#'+a.dataset.p)}catch(x){}bk.scrollIntoView({behavior:'smooth',block:'start'})})});
function showTip(d){var r=d.querySelector('circle').getBoundingClientRect(),b=bk.querySelector('.bmap').getBoundingClientRect();tip.textContent=d.getAttribute('aria-label').split(',')[0];tip.style.top=(r.top-b.top+r.height/2)+'px';var x=r.right-b.left+8;if(x+tip.offsetWidth>b.width-4)x=r.left-b.left-8-tip.offsetWidth;tip.style.left=Math.max(2,x)+'px';tip.classList.add('on')}
dots.forEach(function(d){d.addEventListener('mouseenter',function(){showTip(d)});d.addEventListener('focus',function(){showTip(d)});d.addEventListener('mouseleave',function(){tip.classList.remove('on')});d.addEventListener('blur',function(){tip.classList.remove('on')})});
bk.querySelectorAll('.brow[data-l]').forEach(function(r){var d=svg.querySelector('.dt[data-l="'+r.dataset.l+'"]');r.addEventListener('mouseenter',function(){d.classList.add('hot');showTip(d)});r.addEventListener('mouseleave',function(){d.classList.remove('hot');tip.classList.remove('on')})});
var h=location.hash.slice(1);if(BB[h])open(h,false);else place({s:1,tx:0,ty:0},null);
window.addEventListener('resize',function(){place(cur?zoomOf(cur):{s:1,tx:0,ty:0},cur)});
window.addEventListener('hashchange',function(){var h=location.hash.slice(1);if(BB[h]||!h)open(BB[h]?h:null,false)});
})();
(function(){
var vk=document.getElementById('adressen');if(!vk)return;
var NL=vk.dataset.lang==='nl',grid=document.getElementById('vk-grid'),cards=[].slice.call(grid.children),W0=%W0%;
var st={max:0,lab:'all',hist:false,radius:0,sort:'score',w:{e:W0.e,s:W0.s,p:W0.p},home:null,all:false,prov:null},LIM=9;
function num(v){return NL?v.toFixed(1).replace('.',','):v.toFixed(1)}
function d(c,k){return +c.dataset[k]}
function tot(c){var w=st.w,s=w.e+w.s+w.p;if(!s){w=W0;s=w.e+w.s+w.p}return(d(c,'e')*w.e+d(c,'s')*w.s+d(c,'p')*w.p)/s}
function dist(a,b,c,e){var R=6371,r=Math.PI/180,x=(c-a)*r,y=(e-b)*r,h=Math.sin(x/2)*Math.sin(x/2)+Math.cos(a*r)*Math.cos(c*r)*Math.sin(y/2)*Math.sin(y/2);return 2*R*Math.asin(Math.sqrt(h))}
function km(c){return st.home?dist(st.home.lat,st.home.lng,d(c,'lat'),d(c,'lng')):null}
function kmTxt(v){return(v<10?num(Math.round(v*10)/10):String(Math.round(v)))+' km'}
function ok(c){if(st.prov&&c.dataset.prov!==st.prov)return false;if(st.max&&d(c,'cls')>st.max)return false;if(st.lab==='ster'&&!d(c,'ms'))return false;if(st.lab==='bib'&&!d(c,'bib'))return false;if(st.lab==='gm'&&!(d(c,'gm')>=15))return false;if(st.hist&&!d(c,'hist'))return false;if(st.radius&&st.home&&km(c)>st.radius)return false;return true}
function active(){return(st.max?1:0)+(st.lab!=='all'?1:0)+(st.hist?1:0)+(st.radius&&st.home?1:0)}
function render(){
 var t={},rank={},pr={};cards.forEach(function(c){t[c.dataset.id]=tot(c)});
 var byT=cards.slice().sort(function(a,b){return t[b.dataset.id]-t[a.dataset.id]||d(a,'rank')-d(b,'rank')});byT.forEach(function(c,i){rank[c.dataset.id]=i+1;pr[c.dataset.prov]=(pr[c.dataset.prov]||0)+1;c.dataset.pr=pr[c.dataset.prov]});
 var f={score:function(a,b){return rank[a.dataset.id]-rank[b.dataset.id]},prijs:function(a,b){return d(a,'p2')-d(b,'p2')||rank[a.dataset.id]-rank[b.dataset.id]},eten:function(a,b){return d(b,'e')-d(a,'e')||rank[a.dataset.id]-rank[b.dataset.id]},slapen:function(a,b){return d(b,'s')-d(a,'s')||rank[a.dataset.id]-rank[b.dataset.id]},afstand:function(a,b){return km(a)-km(b)}}[st.sort==='afstand'&&!st.home?'score':st.sort];
 var list=cards.slice().sort(f),found=list.filter(ok),capped=!st.prov&&!st.all&&found.length>LIM;
 list.forEach(function(c){grid.appendChild(c)});
 var shown=0;list.forEach(function(c){var on=ok(c)&&(!capped||shown<LIM);if(on)shown++;c.hidden=!on;
  c.querySelector('.vsc').textContent=num(Math.round(t[c.dataset.id]*10)/10);c.querySelector('.vrk').textContent=st.prov?c.dataset.pr:rank[c.dataset.id];
  var k=c.querySelector('.vkm'),v=km(c);k.hidden=v==null;if(v!=null)k.textContent=kmTxt(v)});
 var m=found.length,n=st.prov?cards.filter(function(c){return c.dataset.prov===st.prov}).length:cards.length,act=active()>0,pn=st.prov?PROVN[st.prov]:'';
 document.getElementById('vk-titel').textContent=st.prov?(act?(NL?m+' van '+n+' adressen in '+pn:m+' of '+n+' addresses in '+pn):(NL?'De '+n+' adressen in '+pn:'The '+n+' addresses in '+pn)):(act?(NL?m+' van '+n+' adressen':m+' of '+n+' addresses'):document.getElementById('vk-titel').dataset.all);
 document.getElementById('vk-res').textContent=(NL?m+(m===1?' adres':' adressen'):m+(m===1?' address':' addresses'))+(capped?(NL?', de eerste '+LIM+' getoond':', showing the first '+LIM):'')+(st.prov?(NL?' in '+pn:' in '+pn):'');
 document.getElementById('vk-resetf').hidden=!act;
 document.getElementById('vk-empty').hidden=m>0;
 var more=document.getElementById('vk-more');more.hidden=!capped;more.textContent=NL?'Toon alle '+m+' adressen':'Show all '+m+' addresses';
 var cu=st.w.e!==W0.e||st.w.s!==W0.s||st.w.p!==W0.p;document.getElementById('vk-resetw').hidden=!cu;
 var sum=st.w.e+st.w.s+st.w.p;vk.querySelectorAll('[data-w]').forEach(function(i){i.value=st.w[i.dataset.w];i.parentNode.querySelector('.pct').textContent=(sum?Math.round(st.w[i.dataset.w]/sum*100):0)+'%'});
 vk.querySelectorAll('.fchip').forEach(function(b){var f=b.dataset.f,v=b.dataset.v,on=f==='hist'?st.hist:String(st[f])===v;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on)});
 vk.querySelector('[data-f="sort"][data-v="afstand"]').hidden=!st.home;
 document.getElementById('vk-home').hidden=!st.home;document.getElementById('vk-help').hidden=!!st.home;
 if(st.home)document.getElementById('vk-hometxt').textContent=(NL?'Hemelsbreed gemeten vanaf ':'As the crow flies from ')+st.home.label;
 document.getElementById('vk-kick').textContent=st.prov?(NL?'Hoofdstuk '+PROVCH[st.prov]+' · zoek, filter en vergelijk':'Chapter '+PROVCH[st.prov]+' · search, filter and compare'):(NL?'Zoek, filter en vergelijk':'Search, filter and compare');
}
var PROVN=%PROVN%,PROVCH=%PROVCH%;
vk.addEventListener('click',function(e){var b=e.target.closest('.fchip');if(!b)return;var f=b.dataset.f,v=b.dataset.v;
 if(f==='hist')st.hist=!st.hist;else if(f==='lab'||f==='sort')st[f]=v;else st[f]=+v;render()});
vk.querySelectorAll('[data-w]').forEach(function(i){i.addEventListener('input',function(){st.w[i.dataset.w]=+i.value;if(!st.w.e&&!st.w.s&&!st.w.p)st.w[i.dataset.w]=5;render()})});
document.getElementById('vk-resetw').onclick=function(){st.w={e:W0.e,s:W0.s,p:W0.p};render()};
document.getElementById('vk-resetf').onclick=function(){st.max=0;st.lab='all';st.hist=false;st.radius=0;render()};
document.getElementById('vk-more').onclick=function(){st.all=true;render()};
document.getElementById('vk-clear').onclick=function(){st.home=null;st.radius=0;if(st.sort==='afstand')st.sort='score';document.getElementById('vk-adres').value='';render()};
var G=null;
function loadGeo(cb){if(G)return cb();var s=document.createElement('script');s.src='/geo.js';s.onload=function(){var raw=window.DGEO||{pc:'',pl:''};G={pc:{},pl:[]};raw.pc.split(';').forEach(function(x){var a=x.split(',');if(a.length===3)G.pc[a[0]]=[(+a[1]+50000)/1000,(+a[2]+3000)/1000]});raw.pl.split(';').forEach(function(x){var a=x.split('|');if(a.length===3)G.pl.push({n:a[0],k:norm(a[0]),lat:(+a[1]+50000)/1000,lng:(+a[2]+3000)/1000})});cb()};document.head.appendChild(s)}
function norm(s){s=String(s||'').toLowerCase();if(s.normalize)s=s.normalize('NFD').replace(/[̀-ͯ]/g,'');return s.replace(/[^a-z0-9]+/g,' ').replace(/\s+/g,' ').trim()}
function nearest(lat,lng){var b=null,bd=1e9;G.pl.forEach(function(p){var x=(p.lat-lat)*(p.lat-lat)+(p.lng-lng)*(p.lng-lng)*.38;if(x<bd){bd=x;b=p}});return b}
function geocode(q){q=String(q||'').trim();if(!q)return null;var m=q.match(/(?:^|[^0-9])([1-9][0-9]{3})\s?([a-zA-Z]{2})?(?![0-9a-zA-Z])/);
 if(m&&G.pc[m[1]]){var c=G.pc[m[1]],np=nearest(c[0],c[1]);return{lat:c[0],lng:c[1],label:m[1]+(m[2]?' '+m[2].toUpperCase():'')+(np?', '+np.n:'')}}
 var k=' '+norm(q)+' ',best=null;G.pl.forEach(function(p){if(p.k.length<2)return;var i=k.lastIndexOf(' '+p.k+' ');if(i<0)return;var sc=p.k.length*10+i;if(!best||sc>best.s)best={p:p,s:sc}});
 if(!best){var last=norm(q).split(' ').pop();if(last&&last.length>=3)G.pl.forEach(function(p){if(p.k.indexOf(last)===0&&(!best||p.k.length<best.p.k.length))best={p:p,s:0}})}
 return best?{lat:best.p.lat,lng:best.p.lng,label:best.p.n}:null}
function setHome(h){st.home=h;st.sort='afstand';document.getElementById('vk-err').hidden=true;render()}
document.getElementById('vk-form').addEventListener('submit',function(e){e.preventDefault();var inp=document.getElementById('vk-adres'),q=inp.value;if(!q.trim())return;loadGeo(function(){var r=geocode(q);if(r){inp.value=r.label;setHome(r)}else{document.getElementById('vk-err').hidden=false;document.getElementById('vk-help').hidden=true;if(st.home)inp.value=st.home.label}})});
var gb=document.getElementById('vk-geo');if(!navigator.geolocation)gb.hidden=true;else gb.onclick=function(){navigator.geolocation.getCurrentPosition(function(p){var la=p.coords.latitude,lo=p.coords.longitude;loadGeo(function(){var np=nearest(la,lo);setHome({lat:la,lng:lo,label:(NL?'jouw locatie':'your location')+(np?(NL?', bij ':', near ')+np.n:'')})})},function(){document.getElementById('vk-err').hidden=false})};
document.addEventListener('des:prov',function(e){st.prov=e.detail||null;st.all=false;render()});
var h0=location.hash.slice(1);if(PROVN[h0])st.prov=h0;
document.querySelectorAll('[data-scope]').forEach(function(a){a.addEventListener('click',function(){st.prov=a.dataset.scope;render()})});
render();
})();
"""

def build_home(lang):
    nl = lang == 'nl'
    h = book(lang) + home_social(lang) + explorer(lang) + home_sections(lang)
    if nl:
        h += '<section class="sec"><div class="wrap" style="display:grid;gap:28px"><div class="stack0"><p class="k">Lijsten</p><h2>Waar heb je zin in?</h2></div><div class="minis">%s</div></div></section>' % ''.join(
            '<a class="mini" href="/%s/">%s<span><b>%s</b><span>%d adressen</span></span></a>' % (th['slug'], pic(th['locs'][0].get('th') or th['locs'][0]['img'], '', '76px', widths=(480,)), esc(th['nav']), len(th['locs'])) for th in THEMES)
        h += '<section class="sec alt"><div class="wrap" style="display:grid;gap:28px"><div class="stack0"><p class="k">Verhalen</p><h2>Over tafels, bedden en wat het kost</h2></div><div class="cards">%s</div><p><a href="/verhalen/">Alle verhalen</a></p></div></section>' % ''.join(post_card(a) for a in POSTS[:3])
    faq = ([('Wat is een restaurant met overnachting?', 'Een restaurant waar je na het diner kunt blijven slapen, op hetzelfde adres. In dit boek staan alleen adressen waar je eet en slaapt onder één dak, geen hotels waar je voor het diner een andere deur door moet.'),
            ('Wat kost een diner met overnachting?', 'Van de %d adressen in dit boek ligt de middelste prijs rond de %s voor twee, voor diner, een nacht en ontbijt, zonder drank.' % (len(LOCS), eur(sorted(l['pz']['p2'] for l in LOCS)[len(LOCS) // 2]))),
            ('Welk adres staat op nummer één?', '%s in %s, gevolgd door %s en %s.' % (ORDER[0]['name'], ORDER[0]['place'], ORDER[1]['name'], ORDER[2]['name'])),
            ('Wat betekent een blauwe stip op de kaart?', 'Een blauwe stip is per provincie het adres met ons hoogste cijfer. De rode stippen zijn de andere adressen in het boek.')] if nl else
           [('What is a restaurant with rooms?', 'A restaurant where you can stay the night after dinner, at the same address. This book only lists places where you dine and sleep under one roof.'),
            ('Which address is number one?', '%s in %s, followed by %s and %s.' % (ORDER[0]['name'], ORDER[0]['place'], ORDER[1]['name'], ORDER[2]['name'])),
            ('What does a blue dot on the map mean?', 'A blue dot marks the address with our highest score in each province. The red dots are the other addresses in the book.')])
    h += '<section class="sec white"><div class="narrow">%s</div></section>' % faq_html(faq, title='Kort gezegd' if nl else 'In short')
    js = HOME_JS.replace('%BB%', json.dumps({p['id']: p['bb'] for p in PROVS})).replace('%PN%', json.dumps({p['id']: [p['ch'], pname(p, lang), int(p['n'])] for p in PROVS}, ensure_ascii=False)) \
        .replace('%W0%', json.dumps(W0)).replace('%PROVN%', json.dumps({p['id']: pname(p, lang) for p in PROVS}, ensure_ascii=False)).replace('%PROVCH%', json.dumps({p['id']: p['ch'] for p in PROVS}))
    title = 'Restaurant met overnachting: onze %d adressen (2026)' % len(LOCS) if nl else 'Restaurants with rooms in the Netherlands (2026)'
    desc = ('Dineren en blijven slapen onder één dak: %d adressen in twaalf provincies, van borg tot sterrenrestaurant, met onze cijfers en wat je voor twee kwijt bent.' % len(LOCS)) if nl else \
           ('Dine and stay the night under one roof: %d addresses in twelve Dutch provinces, from manor house to Michelin star, with our scores and the price for two.' % len(LOCS))
    page(u_home(lang), lang, title, desc, h, 'home', {'nl': '/', 'en': '/en/'}, [ld_faq(faq), ld_itemlist(ORDER[:10], lang)], og=og_img(D['img']['omslag']), prio=1.0, extra_js=js)
