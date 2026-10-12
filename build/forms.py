# Formulieren en opslag: nieuwsbrief, tips, contact en reviews gaan naar de eigen database (Supabase, EU).
# Wordt door build.py ingelezen met exec() vlak voor main(), zodat het de standaardversies vervangt.

_cfg = os.path.join(HERE, 'data', 'supabase.json')
DB = json.load(open(_cfg)) if os.path.exists(_cfg) else {'url': '', 'key': ''}

FORM_MSG = {
    'nl': {'fail': 'Het versturen is niet gelukt. Probeer het zo nog eens, of mail ons op %s.' % MAIL, 'many': 'Je hebt net al een paar keer iets gestuurd. Probeer het over een uur nog eens.', 'prov': 'Kies nog even je provincie, of kies Geen voorkeur.', 'mail': 'Vul een geldig e-mailadres in.', 'req': 'Vul de verplichte velden in.'},
    'en': {'fail': 'Something went wrong while sending. Please try again in a moment, or email us at %s.' % MAIL, 'many': 'You have already sent us a few messages just now. Please try again in an hour.', 'prov': 'Please choose a province, or choose No preference.', 'mail': 'Please enter a valid email address.', 'req': 'Please fill in the required fields.'},
}

JS = (r"""(function(){var DB=%s,MSG=%s,L=document.documentElement.lang==='en'?'en':'nl',t0=Date.now();
function hd(){var h={apikey:DB.key,'Content-Type':'application/json',Prefer:'return=minimal'};if(DB.key.indexOf('eyJ')===0)h.Authorization='Bearer '+DB.key;return h}
function v(f,n){var e=f.elements[n];if(!e)return'';if(e.type==='checkbox')return e.checked;return String(e.value||'').trim()}
function nn(x){return x===''?null:x}
var MAP={
nieuwsbrief:function(f){return['subscribers',{email:v(f,'email'),province:nn(v(f,'provincie')),source:location.pathname,lang:L}]},
tip:function(f){return['messages',{kind:'tip',address_name:v(f,'adres'),address_place:nn(v(f,'plaats')),province:nn(v(f,'provincie')),body:nn(v(f,'waarom')),email:nn(v(f,'email')),page:location.pathname}]},
contact:function(f){return['messages',{kind:'contact',name:nn(v(f,'naam')),email:v(f,'email'),subject:nn(v(f,'onderwerp')),body:v(f,'bericht'),page:location.pathname}]},
review:function(f){return['reviews',{loc_id:f.dataset.loc,loc_name:f.dataset.name,name:v(f,'naam'),email:nn(v(f,'email')),visit_month:nn(v(f,'wanneer')),score_e:+v(f,'eten'),score_s:+v(f,'slapen'),score_p:+v(f,'prijs'),body:v(f,'tekst'),visited:v(f,'bezocht')===true,lang:L}]}};
document.querySelectorAll('.js-form').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();
var w=f.closest('.fwrap')||f.parentNode,er=w.querySelector('.ferr'),b=f.querySelector('[type=submit]');
function done(){w.classList.add('sent');var t=w.querySelector('.thanks');if(t){t.setAttribute('tabindex','-1');t.focus()}}
if(v(f,'website')){done();return}
if(f.checkValidity&&!f.checkValidity()){var bad=f.querySelector(':invalid');if(er){er.hidden=false;er.textContent=bad&&bad.tagName==='SELECT'?MSG[L].prov:(bad&&bad.type==='email'?MSG[L].mail:MSG[L].req)}if(bad)bad.focus();return}
if(!DB.url){if(er){er.hidden=false;er.textContent=MSG[L].fail}return}
var m=MAP[f.dataset.kind](f);b.disabled=true;if(er)er.hidden=true;
fetch(DB.url+'/rest/v1/'+m[0],{method:'POST',headers:hd(),body:JSON.stringify(m[1])}).then(function(r){
if(r.ok||r.status===409)return done();return r.json().catch(function(){return{}}).then(function(j){throw j})}).catch(function(x){b.disabled=false;
if(er){er.hidden=false;er.textContent=(x&&x.message&&/Te veel/.test(x.message))?MSG[L].many:MSG[L].fail}})})});
document.querySelectorAll('.js-reviews').forEach(function(box){if(!DB.url)return;
fetch(DB.url+'/rest/v1/rpc/approved_reviews',{method:'POST',headers:hd(),body:JSON.stringify({p_loc:box.dataset.loc})}).then(function(r){return r.ok?r.json():[]}).then(function(a){
if(!a||!a.length)return;var list=box.querySelector('.rvlist'),sum=0;box.querySelector('.rvempty').hidden=true;
var M=L==='en'?['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']:['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
var K=L==='en'?['Food','Stay','Price','Visited']:['Eten','Slapen','Prijs','Bezocht'];
function n1(x){x=Math.round(x*10)/10;return L==='en'?x.toFixed(1):x.toFixed(1).replace('.',',')}
a.forEach(function(r){sum+=(r.score_e+r.score_s+r.score_p)/3;var ar=document.createElement('article');ar.className='rv';
var hd2=document.createElement('div');hd2.className='rvh';var nm=document.createElement('b');nm.textContent=r.name;hd2.appendChild(nm);
if(r.visit_month){var mo=document.createElement('span');var p=r.visit_month.split('-');mo.textContent=K[3]+' '+M[+p[1]-1]+' '+p[0];hd2.appendChild(mo)}
var sc=document.createElement('div');sc.className='rvs';sc.textContent=K[0]+' '+r.score_e+' · '+K[1]+' '+r.score_s+' · '+K[2]+' '+r.score_p;
var tx=document.createElement('p');tx.textContent=r.body;ar.appendChild(hd2);ar.appendChild(sc);ar.appendChild(tx);list.appendChild(ar)});
var c=box.querySelector('.rvcount');c.hidden=false;c.textContent=(L==='en'?a.length+(a.length===1?' review from readers, average ':' reviews from readers, average '):a.length+(a.length===1?' review van lezers, gemiddeld ':' reviews van lezers, gemiddeld '))+n1(sum/a.length)}).catch(function(){})})})();""")
JS = JS % (json.dumps({'url': DB['url'], 'key': DB['key']}), json.dumps(FORM_MSG, ensure_ascii=False))

HONEY = '<div class="hp" aria-hidden="true"><label>Laat dit veld leeg<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>'

def ferr(): return '<p class="ferr" role="alert" hidden></p>'

def prov_select(lang, idp, dark=False):
    nl = lang == 'nl'
    opts = ''.join('<option value="%s" data-nb>%s</option>' % (p['id'], esc(pname(p, lang))) for p in sorted(PROVS, key=lambda p: pname(p, lang)))
    return ('<label for="%s-prov" class="nbl">%s</label><select id="%s-prov" class="inp nbp" name="provincie" required>'
            '<option value="">%s</option>%s<option value="geen" data-nb>%s</option></select>') % (
        idp, 'In welke provincie ga je het liefst dineren en slapen?' if nl else 'Which province would you most like to dine and stay in?', idp,
        'Kies je provincie' if nl else 'Choose a province', opts, 'Geen voorkeur, heel Nederland' if nl else 'No preference, anywhere in the country')

def newsletter_form(lang, idp, compact=False, dark=True, head=True):
    t = T[lang]
    return ('<div class="nlwrap fwrap"><form class="sub js-form" data-kind="nieuwsbrief" action="#" style="margin-top:14px" novalidate="novalidate">%s%s'
            '<label for="%s-mail" class="nbl">%s</label>'
            '%s<input id="%s-mail" class="inp" type="email" name="email" autocomplete="email" required maxlength="200" placeholder="%s"><button class="btn%s" type="submit">%s</button></form>%s'
            '<p class="thanks" role="status">%s</p></div>') % (
        ('<p class="nbh">%s</p>' % t['nlLabel']) if head else '', prov_select(lang, idp), idp, 'Je e-mailadres' if lang == 'nl' else 'Your email address', HONEY, idp, t['ph'], ' ghost' if compact else '', t['nlBtn'], ferr(),
        'Dank je, je staat op de lijst. De eerste mail komt begin volgende maand, met de adressen in jouw provincie bovenaan.' if lang == 'nl' else 'Thank you, you are on the list. The first email will arrive early next month, with the addresses in your province at the top.')

def nb_preselect(doc, path):
    seg = [x for x in path.split('/') if x]
    if seg and seg[0] == 'en': seg = seg[1:]
    if seg and seg[0] in {p['id'] for p in PROVS}:
        doc = doc.replace('<option value="%s" data-nb>' % seg[0], '<option value="%s" data-nb selected>' % seg[0])
    return doc

def reviews_section(l, lang):
    nl = lang == 'nl'
    months = [('', 'Kies een maand' if nl else 'Choose a month')]
    MN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december'] if nl else \
         ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    y, m = 2026, 10
    for _ in range(24):
        months.append(('%d-%02d' % (y, m), '%s %d' % (MN[m - 1], y)))
        m -= 1
        if m == 0: m, y = 12, y - 1
    opts = ''.join('<option value="%s">%s</option>' % (a, b) for a, b in months)
    rng = lambda n, k: ('<div class="rr"><label for="rv-%s">%s</label><input id="rv-%s" type="range" name="%s" min="1" max="10" step="1" value="8" oninput="this.nextElementSibling.textContent=this.value"><output>8</output></div>') % (n, k, n, n)
    return ('<section class="sec white" id="reviews"><div class="wrap split"><div class="stack js-reviews" data-loc="%s" style="min-width:0">'
            '<p class="k">%s</p><h2>%s</h2><p class="meta rvcount" hidden></p><p class="rvempty">%s</p><div class="rvlist"></div></div>'
            '<aside class="fwrap rvform"><details%s><summary class="btn ghost2">%s</summary>'
            '<form class="js-form rvf" data-kind="review" data-loc="%s" data-name="%s" action="#">%s'
            '<label>%s<input class="inp" name="naam" required minlength="2" maxlength="60" autocomplete="given-name"></label>'
            '<label>%s<select class="inp" name="wanneer">%s</select></label>'
            '<fieldset class="rrs"><legend>%s</legend>%s%s%s</fieldset>'
            '<label>%s<textarea class="inp" name="tekst" required minlength="40" maxlength="3000" rows="6"></textarea><span class="fh">%s</span></label>'
            '<label>%s<input class="inp" type="email" name="email" maxlength="200" autocomplete="email"><span class="fh">%s</span></label>'
            '<label class="chk"><input type="checkbox" name="bezocht" required> %s</label>'
            '<button class="btn" type="submit">%s</button><p class="fh">%s</p></form>%s'
            '<p class="thanks" role="status">%s</p></details></aside></div></section>') % (
        l['id'], 'Reviews van lezers' if nl else 'Reviews from readers', ('Ben jij bij %s geweest?' if nl else 'Have you been to %s?') % esc(l['name']),
        ('Er staan nog geen reviews van lezers bij dit adres. Ben je er geweest? Dan lezen we graag hoe het was. Jouw review komt naast ons eigen cijfer te staan en telt daarin niet mee.' if nl else
         'There are no reader reviews for this address yet. Have you been? We would love to hear how it was. Your review will appear next to our own score and does not count towards it.'),
        '', 'Schrijf een review' if nl else 'Write a review', l['id'], esc(l['name']), HONEY,
        'Je voornaam (die zetten we bij je review)' if nl else 'Your first name (shown with your review)', 'Wanneer was je er?' if nl else 'When did you go?', opts,
        'Jouw cijfers, van 1 tot 10' if nl else 'Your scores, from 1 to 10', rng('eten', 'Eten' if nl else 'Food'), rng('slapen', 'Slapen' if nl else 'Stay'), rng('prijs', 'Prijs' if nl else 'Price'),
        'Wat maakte het bijzonder?' if nl else 'What made it special?', 'Minstens een paar zinnen.' if nl else 'At least a few sentences.',
        'Je e-mailadres (niet verplicht)' if nl else 'Your email address (optional)', 'Alleen voor als we een vraag hebben. Het komt nooit op de site.' if nl else 'Only in case we have a question. It never appears on the site.',
        'Ik heb hier zelf gegeten of geslapen' if nl else 'I have dined or stayed here myself',
        'Review versturen' if nl else 'Send review',
        'We lezen elke review voordat hij online komt.' if nl else 'We read every review before it goes online.', ferr(),
        ('Dank je. We lezen je review en zetten hem daarna bij %s.' if nl else 'Thank you. We will read your review and then add it to the page for %s.') % esc(l['name'].rstrip('.')))

def build_contact():
    items = [('Home', '/'), ('Contact', None)]
    subj = ''.join('<option>%s</option>' % s for s in ('Een vraag', 'Samenwerken', 'Een fout op de site', 'Iets anders'))
    h = ('<section class="sec"><div class="narrow stack">%s<p class="k">Contact</p><h1 style="font-size:clamp(36px,6vw,54px)">Schrijf ons</h1>'
         '<p class="lead">Een vraag over een adres, een fout die je zag of een idee om samen te werken? Laat het weten. We lezen alles en antwoorden meestal binnen een paar dagen.</p>'
         '<div class="fwrap"><form class="js-form" data-kind="contact" action="#" style="display:grid;gap:14px;font:400 15px var(--sans)">%s'
         '<label>Je naam<input class="inp" style="width:100%%" name="naam" maxlength="80" autocomplete="name"></label>'
         '<label>Je e-mailadres<input class="inp" style="width:100%%" type="email" name="email" required maxlength="200" autocomplete="email"></label>'
         '<label>Waar gaat het over?<select class="inp" style="width:100%%" name="onderwerp">%s</select></label>'
         '<label>Je bericht<textarea class="inp" style="width:100%%;height:160px;padding:12px" name="bericht" required minlength="5" maxlength="5000"></textarea></label>'
         '<button class="btn" type="submit" style="justify-self:start">Verstuur je bericht</button><p class="formnote">We gebruiken je gegevens alleen om je te antwoorden. Lees de <a href="/privacy/">privacyverklaring</a>.</p></form>%s'
         '<p class="thanks" role="status">Dank je, je bericht is binnen. We antwoorden meestal binnen een paar dagen.</p></div>'
         '<p class="meta">Een adres tippen? Dat kan via <a href="/zo-kiezen-wij/#tip">het tipformulier</a>. Liever mailen? <a href="mailto:%s">%s</a>.</p></div></section>') % (crumbs(items, light=True), HONEY, subj, ferr(), MAIL, MAIL)
    page('/contact/', 'nl', 'Contact: een vraag, tip of fout melden | Dineren en Slapen', 'Een vraag over een adres, een fout op de site of samenwerken? Stuur Dineren en Slapen een bericht. We antwoorden meestal binnen een paar dagen.', h, '', None, [ld_crumbs(items), {'@type': 'ContactPage', 'url': SITE + '/contact/', 'name': 'Contact'}], prio=0.3)

def build_privacy():
    items = [('Home', '/'), ('Privacy', None)]
    h = ('<section class="sec"><div class="narrow prose stack">%s<h1 style="font-size:clamp(36px,6vw,54px)">Privacy</h1>'
         '<p>Deze site gebruikt geen tracking-cookies, geen advertentienetwerken en geen analysediensten.</p>'
         '<h2>Wat we bewaren</h2><ul>'
         '<li><strong>Nieuwsbrief.</strong> Je e-mailadres, je voorkeursprovincie, de pagina waar je je inschreef en de datum. Alleen om je de nieuwsbrief te sturen. Afmelden kan altijd.</li>'
         '<li><strong>Tips en contactberichten.</strong> Wat je invult, zodat we je tip kunnen bekijken en je kunnen antwoorden.</li>'
         '<li><strong>Reviews.</strong> Je voornaam, je bezoekmaand, je cijfers en je tekst. Na goedkeuring staan je voornaam, maand, cijfers en tekst op de site. Je e-mailadres komt nooit op de site, ook niet als je het invult.</li>'
         '<li><strong>Bescherming tegen spam.</strong> Bij elke inzending bewaren we een versleutelde code die van je IP-adres is afgeleid, zodat we massale inzendingen kunnen tegenhouden. Die code wissen we na twee uur. Je IP-adres zelf bewaren we niet. Onze databaseleverancier houdt IP-adressen wel kort bij in technische logboeken.</li></ul>'
         '<h2>Hoe lang</h2><ul><li>Berichten en tips: hooguit twee jaar.</li><li>Reviews: zolang ze op de site staan. Je e-mailadres bij een review en afgewezen reviews wissen we na een jaar.</li><li>Nieuwsbrief: tot je je afmeldt. Na afmelden wissen we je adres binnen dertig dagen.</li></ul>'
         '<h2>Waar het staat</h2><p>De gegevens staan in een beveiligde database van Supabase, op servers in Frankfurt (EU). Alleen wij kunnen erbij, met een eigen inlog. We verkopen niets en geven niets door.</p>'
         '<h2>Inzien of verwijderen</h2><p>Wil je weten wat we van je hebben, of wil je dat we het verwijderen? Mail ons op <a href="mailto:%s">%s</a>. We regelen het binnen een maand.</p></div></section>') % (crumbs(items, light=True), MAIL, MAIL)
    page('/privacy/', 'nl', 'Privacy: wat we bewaren en waarom | Dineren en Slapen', 'Geen tracking en geen advertenties. Wat we bewaren als je je inschrijft, een tip of review stuurt of contact opneemt, en waar dat staat.', h, '', None, [ld_crumbs(items)], prio=0.1)

def write_admin():
    src = os.path.join(HERE, 'admin'); dst = os.path.join(OUT, 'admin')
    os.makedirs(dst, exist_ok=True)
    host = re.sub(r'^https?://', '', DB['url']).rstrip('/') or 'example.supabase.co'
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if f.endswith(('.html', '.js', '.css')):
            s = open(p, encoding='utf-8').read().replace('__DB_URL__', DB['url']).replace('__DB_KEY__', DB['key']).replace('__DB_HOST__', host).replace('__LOC_URLS__', json.dumps({l['id']: {'u': u_loc(l, 'nl'), 'n': l['name']} for l in LOCS}, ensure_ascii=False))
            open(os.path.join(dst, f), 'w', encoding='utf-8').write(s)
        else:
            shutil.copy(p, os.path.join(dst, f))

def gallery_section(l, lang):
    if not l.get('gallery'): return ''
    nl = lang == 'nl'; figs = ''
    for i, (name, cnl, cen) in enumerate(l['gallery']):
        v = img_variants('own:' + name)
        if not v: continue
        cap = cnl if nl else cen
        figs += '<figure><a href="%s" target="_blank" rel="noopener">%s</a><figcaption>%s</figcaption></figure>' % (v[-1][2], pic('own:' + name, cap, '(max-width: 760px) 50vw, 300px', widths=(480, 960)), esc(cap))
    return ('<section class="sec" id="fotos"><div class="wrap stack"><p class="k">%s</p><h2>%s</h2><div class="gal">%s</div><p class="meta">%s</p></div></section>') % (
        'Onze foto\'s' if nl else 'Our photos', ('Zo was het bij %s' if nl else 'How it was at %s') % esc(l['name']), figs,
        'Foto\'s die we zelf maakten tijdens onze bezoeken. Klik op een foto voor een grotere versie.' if nl else 'Photos we took ourselves on our visits. Click a photo to see a larger version.')
