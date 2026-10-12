# SEO-aanvullingen: deelafbeeldingen als JPG, organisatiegegevens, kopregel en metatags.
# Wordt door build.py ingelezen met exec() vlak voor main().

def og_img(blob):
    """Deelafbeelding van 1200 x 630 als JPG: WhatsApp, LinkedIn en Facebook tonen die altijd."""
    bid = blob.rsplit('/', 1)[-1] if blob else ''
    name = bid[4:] if bid.startswith('own:') else BLOB2NAME.get(bid)
    sp = src_path(name) if name else None
    if not sp:
        # bronbeeld niet beschikbaar: gebruik de eerder gebouwde deelafbeelding
        if name and os.path.exists(os.path.join(OUT, 'img', 'og', '%s.jpg' % name)): return SITE + '/img/og/%s.jpg' % name
        return SITE + '/og.jpg'
    os.makedirs(os.path.join(OUT, 'img', 'og'), exist_ok=True)
    fn = '%s.jpg' % name; fp = os.path.join(OUT, 'img', 'og', fn)
    if not os.path.exists(fp):
        im = Image.open(sp).convert('RGB'); W, H = im.size; r = 1200 / 630
        if W / H > r: nw = round(H * r); im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
        else: nh = round(W / r); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
        im.resize((1200, 630), Image.LANCZOS).save(fp, 'JPEG', quality=82, optimize=True, progressive=True)
    return SITE + '/img/og/' + fn

ORG.update({
    'logo': {'@type': 'ImageObject', 'url': SITE + '/icon-512.png', 'width': 512, 'height': 512},
    'email': MAIL,
    'description': 'Onafhankelijke gids van restaurants met overnachting in Nederland: adressen waar je dineert en blijft slapen onder één dak, met eigen cijfers en de prijs voor twee.',
    'sameAs': [u for _, _, u in SOCIAL],
})

def seo_post(doc):
    m = re.search(r'<meta property="og:image" content="([^"]+)">', doc)
    t = re.search(r'<meta property="og:title" content="([^"]*)">', doc)
    if m and m.group(1).endswith('.jpg'):
        extra = '<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        if t: extra += '<meta property="og:image:alt" content="%s">' % t.group(1)
        doc = doc.replace(m.group(0), m.group(0) + extra, 1)
    return doc

CSS = CSS + re.sub(r'\s*\n\s*', '', """
.hero h1 .h1s{display:block;margin-top:10px;font:400 clamp(16px,1.9vw,19px)/1.35 var(--sans);letter-spacing:.01em;color:#C9CFC4}
.hero h1 .h1s::first-letter{text-transform:uppercase}
""")
