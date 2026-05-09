"""Iron-Art subpage builder.
Reads each subpage, extracts title/description/keywords/h1/content,
splits the content into h2-driven segments and renders the v2 template
(header, page banner, alternating sections with gallery / prose, footer).
Produces clean URLs (no .html) and full SEO meta (OG, Twitter, JSON-LD).
"""

import re
import glob
import os
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://ironart.vercel.app"

NAV_LINKS = [
    ("index.html", "Kowalstwo"),
    ("balustrady-wewnetrzne.html", "Balustrady kute"),
    ("__SUB_WYROBY__", "Wyroby"),
    ("porecze-do-balustrad.html", "Poręcze"),
    ("meble-kute-sklep.html", "Sklep"),
    ("__SUB_PRACOWNIE__", "Pracownie"),
    ("renowacja-metaloplastyki.html", "Renowacja"),
    ("kowalstwo-lodz.html", "Kontakt"),
]
SUB_WYROBY = [
    ("metaloplastyka.html", "Metaloplastyka"),
    ("balustrady-kute-wewnetrzne.html", "Balustrady kute wewnętrzne"),
    ("balustrady-zewnetrzne.html", "Balustrady zewnętrzne"),
    ("balustrady-schodowe.html", "Balustrady schodowe"),
    ("meble-kute.html", "Meble kute"),
    ("ogrodzenia-kute.html", "Ogrodzenia i bramy"),
    ("wystroj-wnetrz.html", "Wystrój wnętrz"),
    ("projekty-kute.html", "Projekty"),
]
SUB_PRACOWNIE = [
    ("nasza-pracownia-lodz.html", "Pracownia Kowalska"),
    ("pracownia-jubilerska-lodz.html", "Pracownia Jubilerska"),
]


def clean_href(href):
    if href.startswith(('http', 'mailto:', 'tel:')):
        return href
    h = href[:-5] if href.endswith('.html') else href
    if h == 'index': return '/'
    return h


def build_nav(active_slug):
    out = ['<ul>']
    for href, label in NAV_LINKS:
        if href == "__SUB_WYROBY__":
            out.append('<li class="has-sub"><span>Wyroby <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in SUB_WYROBY:
                cls = ' class="is-active"' if sh == active_slug else ''
                out.append(f'<a href="{clean_href(sh)}"{cls}>{sl}</a>')
            out.append('</div></li>')
            continue
        if href == "__SUB_PRACOWNIE__":
            out.append('<li class="has-sub"><span>Pracownie <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in SUB_PRACOWNIE:
                cls = ' class="is-active"' if sh == active_slug else ''
                out.append(f'<a href="{clean_href(sh)}"{cls}>{sl}</a>')
            out.append('</div></li>')
            continue
        cls = ' class="is-active"' if href == active_slug else ''
        out.append(f'<li><a href="{clean_href(href)}"{cls}>{label}</a></li>')
    out.append('</ul>')
    return '\n\t\t\t'.join(out)


def extract(html):
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title.group(1).strip() if title else ""
    desc = re.search(r'name="description"\s+content="([^"]*)"', html)
    desc = desc.group(1) if desc else ""
    kw = re.search(r'name="keywords"\s+content="([^"]*)"', html)
    kw = kw.group(1) if kw else ""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    h1 = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else ""

    m = re.search(r'<section class="tresc">(.*?)</section>\s*(?:</main>|<iframe[^>]*src="https://www\.google|<footer)',
                  html, re.S)
    if not m:
        m = re.search(
            r'<main>\s*<section class="page-banner">.*?</section>\s*'
            r'(?:<div class="ornament".*?</div>\s*)?'
            r'(.*?)\s*</main>',
            html, re.S)
    content = m.group(1) if m else ""

    content = re.sub(r"<h1[^>]*>.*?</h1>", "", content, count=1, flags=re.S)
    return title, desc, kw, h1, content


def normalise_punctuation(text):
    """Replace AI-typical typography with plain ASCII variants."""
    repl = {
        "–": "-", "—": "-",
        "…": "...",
        "“": '"', "”": '"',
        "„": '"', "‚": "'",
        "‘": "'", "’": "'",
        " ": " ",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text


def fix_inner_html(content):
    content = re.sub(r'<section class="galeria">(.*?)</section>',
                     lambda m: f'<div class="gallery">{m.group(1)}</div>',
                     content, flags=re.S)
    content = re.sub(r'\bclass="fancybox"\s*', '', content)
    content = re.sub(r'\s*rel="group"', '', content)

    def split_inner(m):
        inner = m.group(1)
        chunks = re.split(r'(<h2[^>]*>.*?</h2>|<h3[^>]*>.*?</h3>|<p[^>]*>.*?</p>)', inner, flags=re.S)
        out = []
        figs = []
        def flush():
            if figs:
                out.append('<div class="gallery">' + ''.join(figs) + '</div>')
                figs.clear()
        for c in chunks:
            if not c.strip():
                continue
            if re.match(r'<(h2|h3|p)\b', c, flags=re.S):
                flush()
                out.append('</div>' if False else '')
                out.append(c)
            else:
                figs.append(c)
        flush()
        return ''.join(out)

    content = re.sub(r'<div class="gallery">(.*?)</div>(?=\s*(?:<h2|<h3|<p|<div|$))',
                     split_inner, content, flags=re.S)

    content = re.sub(r'<figure(?![^>]*\bclass=)', '<figure class="fade-up"', content)
    content = re.sub(r'<figure([^>]*\bclass=")(?![^"]*fade-up)([^"]*)"',
                     r'<figure\1\2 fade-up"', content)
    content = re.sub(r'<img(?![^>]*\bloading=)', '<img loading="lazy" decoding="async"', content)
    content = re.sub(r'href="([a-z][a-z0-9\-]*)\.html(["#])', r'href="\1\2', content)
    content = re.sub(r'href="/([a-z][a-z0-9\-]*)\.html(["#])', r'href="/\1\2', content)
    content = re.sub(r'</?br\s*/?>', '<br>', content)
    return content.strip()


def split_into_segments(content):
    """Split content on <h2> boundaries. Each segment gets its own intro + gallery."""
    parts = re.split(r'(<h2[^>]*>.*?</h2>)', content, flags=re.S)
    segments = []
    cur = {"heading": "", "intro": "", "gallery": ""}

    def take_galleries(chunk):
        gals = re.findall(r'<div class="gallery[^"]*">.*?</div>', chunk, flags=re.S)
        for g in gals:
            chunk = chunk.replace(g, '\n', 1)
        return chunk, gals

    for chunk in parts:
        if re.match(r'<h2', chunk, flags=re.S):
            if cur["heading"] or cur["intro"] or cur["gallery"]:
                segments.append(cur)
            heading = re.sub(r'</?h2[^>]*>', '', chunk).strip()
            cur = {"heading": heading, "intro": "", "gallery": ""}
        else:
            chunk, gals = take_galleries(chunk)
            chunk = chunk.strip()
            if chunk:
                cur["intro"] = (cur["intro"] + '\n' + chunk).strip() if cur["intro"] else chunk
            for g in gals:
                cur["gallery"] = (cur["gallery"] + '\n' + g).strip() if cur["gallery"] else g

    if cur["heading"] or cur["intro"] or cur["gallery"]:
        segments.append(cur)

    cleaned = []
    for s in segments:
        s["intro"] = re.sub(r'(<p>\s*</p>\s*)+', '', s["intro"]).strip()
        s["gallery"] = re.sub(r'<div class="gallery[^"]*">\s*</div>', '', s["gallery"]).strip()
        if s["heading"] or s["intro"] or s["gallery"]:
            cleaned.append(s)
    return cleaned


def strip_broken_figures(gallery_html, broken_set):
    """Remove <figure> blocks whose href or src points to a broken image."""
    def keep(m):
        block = m.group(0)
        for bad in broken_set:
            if bad in block:
                return ''
        return block
    return re.sub(r'<figure[^>]*>.*?</figure>', keep, gallery_html, flags=re.S)


def render_segments(segments, broken_set):
    sections = []
    for i, seg in enumerate(segments):
        bg = ' section--alt' if i % 2 == 0 else ''
        head = ''
        if seg["heading"]:
            head = f'<h2 class="section-title">{seg["heading"]}</h2>'
        intro = ''
        if seg["intro"]:
            intro = f'<div class="section-lead">{seg["intro"]}</div>'
        gallery = ''
        if seg["gallery"]:
            gh = strip_broken_figures(seg["gallery"], broken_set)
            gh = re.sub(r'<div class="gallery[^"]*">', '<div class="gallery stagger">', gh)
            gallery = f'<div class="fade-up">{gh}</div>'
        if not head and not intro and not gallery:
            continue
        inner = '\n'.join(x for x in [head, intro, gallery] if x)
        sections.append(
            f'\t<section class="section{bg}">\n'
            f'\t\t<div class="container">\n'
            f'\t\t\t<div class="fade-up section-block">\n{inner}\n\t\t\t</div>\n'
            f'\t\t</div>\n'
            f'\t</section>'
        )
    return '\n\n'.join(sections)


HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0E0C09">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Iron-Art Łódź">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/images/balustrada-iron-art.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{site}/assets/images/balustrada-iron-art.webp">
<link rel="shortcut icon" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/style.css">{extra_css}
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-109855821-1"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'UA-109855821-1');
</script>
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>"""


HEADER_NAV = """<header class="site-header">
\t<div class="container header-inner">
\t\t<a href="/" class="brand" aria-label="Iron-Art - strona glowna">
\t\t\t<img src="assets/images/kowalstwo-artystyczne-lodz.webp" alt="Iron-Art - Kowalstwo Artystyczne Lodz">
\t\t\t<span class="brand-tag">Kowalstwo Artystyczne <em>&middot;</em> Jubilerstwo <em>&middot;</em> Lodz</span>
\t\t</a>
\t\t<nav class="primary-nav" aria-label="Glowna nawigacja">
\t\t\t{nav}
\t\t</nav>
\t\t<a class="header-cta" href="tel:887432093">
\t\t\t<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
\t\t\t+48 887 432 093
\t\t</a>
\t\t<button class="menu-toggle" aria-label="Otworz menu" aria-expanded="false">
\t\t\t<span></span><span></span><span></span>
\t\t</button>
\t</div>
</header>
<nav class="mobile-nav" aria-label="Menu mobilne">
\t{nav}
</nav>"""


FOOTER = """<footer class="site-footer">
\t<div class="container">
\t\t<div class="footer-grid">
\t\t\t<div>
\t\t\t\t<img class="footer-logo" src="assets/images/kowalstwo-artystyczne-lodz.webp" alt="Iron-Art">
\t\t\t\t<p class="footer-tagline">Kowalstwo artystyczne, metaloplastyka, meble kute, balustrady kute wewnetrzne i zewnetrzne. Lodz.</p>
\t\t\t\t<div class="footer-socials">
\t\t\t\t\t<a href="https://www.facebook.com/Kowalstwo-artystyczne-Iron-Art-1655904824500073/" target="_blank" rel="noopener" aria-label="Facebook">
\t\t\t\t\t\t<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c5.05-.5 9-4.76 9-9.95z"/></svg>
\t\t\t\t\t</a>
\t\t\t\t</div>
\t\t\t</div>
\t\t\t<div class="footer-col">
\t\t\t\t<h4>Kontakt</h4>
\t\t\t\t<p><strong>Adres</strong>ul. Brzezinska 38<br>92-103 Lodz</p>
\t\t\t\t<p><strong>Telefon</strong><a href="tel:887432093">+48 887 432 093</a></p>
\t\t\t\t<p><strong>E-mail</strong><span class="mail"></span></p>
\t\t\t</div>
\t\t\t<div class="footer-col">
\t\t\t\t<h4>Pracownia</h4>
\t\t\t\t<ul>
\t\t\t\t\t<li><a href="balustrady-wewnetrzne">Balustrady kute</a></li>
\t\t\t\t\t<li><a href="meble-kute">Meble kute</a></li>
\t\t\t\t\t<li><a href="metaloplastyka">Metaloplastyka</a></li>
\t\t\t\t\t<li><a href="meble-kute-sklep">Sklep</a></li>
\t\t\t\t\t<li><a href="renowacja-metaloplastyki">Renowacja</a></li>
\t\t\t\t\t<li><a href="kowalstwo-lodz">Kontakt</a></li>
\t\t\t\t</ul>
\t\t\t</div>
\t\t</div>
\t\t<div class="footer-bottom">
\t\t\t<span>(c) Iron Art Lodz 2004-2026</span>
\t\t\t<a href="https://kontaktio.pl/" target="_blank" rel="noopener">Zrobione przez Kontaktio</a>
\t\t</div>
\t</div>
</footer>
<div id="cookies" class="cookies">
\t<p>Strona Kowalstwa Artystycznego korzysta z plikow cookies w celu badania statystyk odwiedzin.</p>
\t<a class="zamknij" href="javascript:zamknij_ciasteczko()">OK</a>
</div>
<script src="assets/js/mail.js" defer></script>
<script src="assets/js/ciasteczka.js" defer></script>
<script src="assets/js/main.js" defer></script>
</body>
</html>"""


def find_broken_images():
    broken = set()
    for f in glob.glob('assets/images/**/*.jpg', recursive=True):
        if os.path.getsize(f) == 14326:
            broken.add(os.path.basename(f))
    return broken


def build_ld_json(name, url, description):
    return (
        '{\n'
        '\t"@context":"https://schema.org",\n'
        '\t"@type":"LocalBusiness",\n'
        '\t"name":"Iron-Art - Kowalstwo Artystyczne Lodz",\n'
        '\t"image":"' + SITE + '/assets/images/balustrada-iron-art.webp",\n'
        '\t"url":"' + url + '",\n'
        '\t"telephone":"+48 887 432 093",\n'
        '\t"address":{\n'
        '\t\t"@type":"PostalAddress",\n'
        '\t\t"streetAddress":"ul. Brzezinska 38",\n'
        '\t\t"postalCode":"92-103",\n'
        '\t\t"addressLocality":"Lodz",\n'
        '\t\t"addressCountry":"PL"\n'
        '\t},\n'
        '\t"geo":{\n'
        '\t\t"@type":"GeoCoordinates",\n'
        '\t\t"latitude":51.796924,\n'
        '\t\t"longitude":19.514735\n'
        '\t},\n'
        '\t"openingHoursSpecification":[\n'
        '\t\t{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"08:00","closes":"16:00"},\n'
        '\t\t{"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"08:00","closes":"13:00"}\n'
        '\t]\n'
        '}'
    )


def render_page(filename, html, broken):
    title, desc, kw, h1, raw_content = extract(html)
    if not raw_content:
        print(f"SKIP {filename}: no content")
        return False

    content = fix_inner_html(raw_content)
    content = normalise_punctuation(content)

    title = normalise_punctuation(title)
    desc = normalise_punctuation(desc)
    h1 = normalise_punctuation(h1)

    segments = split_into_segments(content)

    name = filename
    canonical = f"{SITE}/{name[:-5] if name.endswith('.html') else name}"
    if name == 'index.html':
        canonical = SITE + '/'

    extra_css = ''
    if name == 'kowalstwo-lodz.html':
        extra_css = '\n<link rel="stylesheet" href="assets/css/kontakt.css">\n<link rel="stylesheet" href="assets/css/formularz.css">'
    elif name == 'meble-kute-sklep.html':
        extra_css = '\n<link rel="stylesheet" href="assets/css/meble-kute-sklep.css">'

    head = HEAD_TEMPLATE.format(
        title=escape(title, quote=True),
        description=escape(desc, quote=True),
        keywords=escape(kw, quote=True),
        canonical=canonical,
        site=SITE,
        extra_css=extra_css,
        ld_json=build_ld_json(title, canonical, desc),
    )

    nav = build_nav(name)
    header_html = HEADER_NAV.format(nav=nav)

    crumb = (
        '<nav class="crumbs" aria-label="Breadcrumb">'
        '<a href="/">Strona glowna</a>'
        '<span class="sep">/</span>'
        f'<span>{escape(h1 or title)}</span>'
        '</nav>'
    )

    page_banner = (
        '\t<section class="page-banner">\n'
        '\t\t<div class="container fade-up">\n'
        f'\t\t\t{crumb}\n'
        f'\t\t\t<h1>{escape(h1 or title)}</h1>\n'
        '\t\t</div>\n'
        '\t</section>'
    )

    sections_html = render_segments(segments, broken)

    out = (
        head + '\n' +
        header_html + '\n' +
        '<main>\n' +
        page_banner + '\n\n' +
        sections_html + '\n' +
        '</main>\n' +
        FOOTER
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(out)
    return True


def main():
    os.chdir(ROOT)
    broken = find_broken_images()
    print(f"Broken image basenames in inventory: {len(broken)}")

    import subprocess
    pages = sorted(p for p in glob.glob('*.html') if p != 'index.html')
    ok = 0
    for p in pages:
        if p == 'kowalstwo-lodz.html':
            continue
        # Pull the original baseline content from the e62f4fe commit
        try:
            blob = subprocess.run(
                ['git', 'show', f'e62f4fe:{p}'],
                capture_output=True, check=True
            ).stdout
            html = blob.decode('utf-8', errors='replace')
        except subprocess.CalledProcessError:
            print(f"SKIP {p}: not in baseline")
            continue
        if render_page(p, html, broken):
            ok += 1
            print(f"OK   {p}")
    print(f"\nProcessed: {ok}/{len(pages)-1}")


if __name__ == "__main__":
    main()
