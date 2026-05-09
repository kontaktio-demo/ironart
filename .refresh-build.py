# One-shot rebuild of subpage HTML to the v2 layout.
# Reads each existing subpage, extracts <title>, meta description/keywords,
# and the inner content (between <main>...</main> minus the old header/footer).
# Writes a brand new file using the v2 template (header, page banner, footer).
#
# Run from project root:  python .refresh-build.py

import re
import glob
import os
import sys
from html import unescape

ROOT = os.path.dirname(os.path.abspath(__file__))

# ----- shared snippets -----
PL_NAV_LINKS = [
    ("index.html", "Kowalstwo"),
    ("balustrady-wewnetrzne.html", "Balustrady kute"),
    ("__SUB_WYROBY__", "Wyroby"),
    ("porecze-do-balustrad.html", "Poręcze"),
    ("meble-kute-sklep.html", "Sklep"),
    ("__SUB_PRACOWNIE__", "Pracownie"),
    ("renowacja-metaloplastyki.html", "Renowacja"),
    ("kowalstwo-lodz.html", "Kontakt"),
]
PL_SUB_WYROBY = [
    ("metaloplastyka.html", "Metaloplastyka"),
    ("balustrady-kute-wewnetrzne.html", "Balustrady kute wewnętrzne"),
    ("balustrady-zewnetrzne.html", "Balustrady zewnętrzne"),
    ("balustrady-schodowe.html", "Balustrady schodowe"),
    ("meble-kute.html", "Meble kute"),
    ("ogrodzenia-kute.html", "Ogrodzenia i bramy"),
    ("wystroj-wnetrz.html", "Wystrój wnętrz"),
    ("projekty-kute.html", "Projekty"),
]
PL_SUB_PRACOWNIE = [
    ("nasza-pracownia-lodz.html", "Pracownia Kowalska"),
    ("pracownia-jubilerska-lodz.html", "Pracownia Jubilerska"),
]

EN_NAV_LINKS = [
    ("index.html", "Blacksmithing"),
    ("internal-railings.html", "Forged Railings"),
    ("__SUB_PRODUCTS__", "Products"),
    ("handrails-for-railings.html", "Handrails"),
    ("shop.html", "Shop"),
    ("__SUB_WORKSHOP__", "Workshop"),
    ("contact.html", "Contact"),
]
EN_SUB_PRODUCTS = [
    ("metalwork.html", "Metalwork"),
    ("forged-internal-railings.html", "Forged internal railings"),
    ("exterior-railings.html", "Exterior railings"),
    ("forged-furniture.html", "Forged furniture"),
    ("forged-fences-and-gates.html", "Fences and gates"),
    ("interior-designe.html", "Interior design"),
    ("designs-and-making.html", "Designs"),
    ("artistic-blacksmithing.html", "Artistic blacksmithing"),
]
EN_SUB_WORKSHOP = [
    ("../nasza-pracownia-lodz.html", "Forge"),
    ("../pracownia-jubilerska-lodz.html", "Jeweller"),
]


def build_nav(active_slug, lang):
    if lang == "pl":
        links = PL_NAV_LINKS
    else:
        links = EN_NAV_LINKS
    out = ['<ul>']
    for href, label in links:
        if href == "__SUB_WYROBY__":
            out.append('<li class="has-sub"><span>Wyroby <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in PL_SUB_WYROBY:
                a_cls = ' class="is-active"' if sh == active_slug else ''
                out.append(f'<a href="{sh}"{a_cls}>{sl}</a>')
            out.append('</div></li>')
            continue
        if href == "__SUB_PRACOWNIE__":
            out.append('<li class="has-sub"><span>Pracownie <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in PL_SUB_PRACOWNIE:
                a_cls = ' class="is-active"' if sh == active_slug else ''
                out.append(f'<a href="{sh}"{a_cls}>{sl}</a>')
            out.append('</div></li>')
            continue
        if href == "__SUB_PRODUCTS__":
            out.append('<li class="has-sub"><span>Products <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in EN_SUB_PRODUCTS:
                a_cls = ' class="is-active"' if sh == active_slug else ''
                out.append(f'<a href="{sh}"{a_cls}>{sl}</a>')
            out.append('</div></li>')
            continue
        if href == "__SUB_WORKSHOP__":
            out.append('<li class="has-sub"><span>Workshop <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div class="submenu">')
            for sh, sl in EN_SUB_WORKSHOP:
                out.append(f'<a href="{sh}">{sl}</a>')
            out.append('</div></li>')
            continue
        a_cls = ' class="is-active"' if href == active_slug else ''
        out.append(f'<li><a href="{href}"{a_cls}>{label}</a></li>')
    out.append('</ul>')
    return '\n\t\t\t'.join(out)


# ----- template -----
def page_template(*, lang, asset_prefix, root_prefix, title, description, keywords,
                  page_h1, page_eyebrow, body_inner, active_slug, breadcrumb_html,
                  pl_index, en_index):
    nav = build_nav(active_slug, lang)
    other_lang = "EN" if lang == "pl" else "PL"
    other_href = en_index if lang == "pl" else pl_index
    cur_lang_label = "PL" if lang == "pl" else "EN"

    if lang == "pl":
        cookie_text = 'Nasza strona <strong>Kowalstwa Artystycznego</strong> korzysta z technologii cookies jedynie w celu badania statystyk odwiedzin.'
        ariaMenu = "Otwórz menu"
        ariaLogo = "Iron-Art — strona główna"
        ariaPhone = "Zadzwoń"
        ctaLabel = "+48 887 432 093"
        brandTag = "Kowalstwo Artystyczne · Łódź"
    else:
        cookie_text = 'Our <strong>Artistic Blacksmithing</strong> website uses cookies only for traffic statistics.'
        ariaMenu = "Open menu"
        ariaLogo = "Iron-Art — home"
        ariaPhone = "Call"
        ctaLabel = "+48 887 432 093"
        brandTag = "Artistic Blacksmithing · Łódź"

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0F0E0C">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<link rel="shortcut icon" href="{root_prefix}favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{asset_prefix}css/style.css">
<link rel="stylesheet" href="{asset_prefix}css/style.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-109855821-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'UA-109855821-1');
</script>
</head>
<body>

<header class="site-header">
	<div class="container header-inner">
		<a href="{pl_index}" class="brand" aria-label="{ariaLogo}">
			<img src="{asset_prefix}images/kowalstwo-artystyczne-lodz.webp" alt="Iron-Art Łódź">
			<span>
				<span class="brand-name">Iron-Art</span>
				<span class="brand-tag">{brandTag}</span>
			</span>
		</a>

		<nav class="primary-nav" aria-label="Primary">
			{nav}
		</nav>

		<div class="lang-switch desktop-only">
			<a href="{pl_index}"{' class="is-active"' if lang=='pl' else ''}>PL</a>
			<span class="sep">·</span>
			<a href="{en_index}"{' class="is-active"' if lang=='en' else ''}>EN</a>
		</div>
		<a class="header-cta" href="tel:887432093">
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
			{ctaLabel}
		</a>

		<button class="menu-toggle" aria-label="{ariaMenu}" aria-expanded="false">
			<span></span><span></span><span></span>
		</button>
	</div>
</header>

<nav class="mobile-nav" aria-label="Mobile menu">
	{nav}
	<div class="lang-switch">
		<a href="{pl_index}"{' class="is-active"' if lang=='pl' else ''}>PL</a>
		<span class="sep">·</span>
		<a href="{en_index}"{' class="is-active"' if lang=='en' else ''}>EN</a>
	</div>
</nav>

<main>

	<section class="page-banner">
		<div class="container fade-up">
			{breadcrumb_html}
			<h1>{page_h1}</h1>
		</div>
	</section>

	<div class="ornament" aria-hidden="true">
		<svg width="42" height="20" viewBox="0 0 42 20" fill="none" stroke="currentColor" stroke-width="1.2">
			<path d="M21 2 C 14 2, 12 10, 21 10 C 30 10, 28 2, 21 2 Z"/>
			<path d="M2 10 L 12 10 M 30 10 L 40 10"/>
			<circle cx="21" cy="10" r="1.6" fill="currentColor"/>
			<path d="M21 10 L 21 18 M 18 14 L 21 18 L 24 14"/>
		</svg>
	</div>

	<section class="section">
		<div class="container">
{body_inner}
		</div>
	</section>

</main>

<footer class="site-footer">
	<div class="container">
		<div class="footer-grid">
			<div>
				<div class="footer-brand">Iron-Art</div>
				<p class="footer-tagline">Kowalstwo artystyczne, metaloplastyka, meble kute, balustrady kute wewnętrzne i zewnętrzne. Łódź · Warszawa.</p>
				<div class="footer-socials">
					<a href="https://www.facebook.com/Kowalstwo-artystyczne-Iron-Art-1655904824500073/" target="_blank" rel="noopener" aria-label="Facebook">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c5.05-.5 9-4.76 9-9.95z"/></svg>
					</a>
				</div>
			</div>
			<div class="footer-col">
				<h4>Kontakt</h4>
				<p><strong>Adres pracowni</strong>ul. Beskidzka 59<br>91-611 Łódź</p>
				<p><strong>Adres biura</strong>ul. Brzezińska 38<br>92-103 Łódź</p>
				<p><strong>Telefon</strong><a href="tel:887432093">+48 887 432 093</a></p>
				<p><strong>E-mail</strong><span class="mail"></span></p>
			</div>
			<div class="footer-col">
				<h4>Pracownia</h4>
				<ul>
					<li><a href="{root_prefix}balustrady-wewnetrzne.html">Balustrady kute</a></li>
					<li><a href="{root_prefix}meble-kute.html">Meble kute</a></li>
					<li><a href="{root_prefix}metaloplastyka.html">Metaloplastyka</a></li>
					<li><a href="{root_prefix}meble-kute-sklep.html">Sklep</a></li>
					<li><a href="{root_prefix}renowacja-metaloplastyki.html">Renowacja</a></li>
					<li><a href="{root_prefix}kowalstwo-lodz.html">Kontakt</a></li>
				</ul>
			</div>
		</div>
		<div class="footer-bottom">
			<span>© Iron Art Łódź, <a href="{root_prefix}kowalstwo-artystyczne-warszawa.html">Warszawa</a> 2004–2026</span>
			<a href="https://www.blumo.pl/" target="_blank" rel="noopener">Web Design — blumo.pl</a>
		</div>
	</div>
</footer>

<a class="float-phone" href="tel:887432093" aria-label="{ariaPhone}">
	<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
</a>
<a class="float-fb" href="https://www.facebook.com/Kowalstwo-artystyczne-Iron-Art-1655904824500073/" target="_blank" rel="noopener" aria-label="Facebook">
	<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c5.05-.5 9-4.76 9-9.95z"/></svg>
</a>

<div id="cookies" class="cookies">
	<p>{cookie_text}</p>
	<a class="zamknij" href="javascript:zamknij_ciasteczko()">OK</a>
</div>

<script src="{asset_prefix}js/mail.js" defer></script>
<script src="{asset_prefix}js/ciasteczka.js" defer></script>
<script src="{asset_prefix}js/main.js" defer></script>
</body>
</html>
'''


# ---------- helpers ----------
EYEBROWS_PL = {
    "balustrady-wewnetrzne.html": "Realizacje",
    "balustrady-kute-wewnetrzne.html": "Realizacje",
    "balustrady-zewnetrzne.html": "Realizacje",
    "balustrady-schodowe.html": "Realizacje",
    "meble-kute.html": "Realizacje",
    "ogrodzenia-kute.html": "Realizacje",
    "wystroj-wnetrz.html": "Realizacje",
    "projekty-kute.html": "Realizacje",
    "metaloplastyka.html": "Realizacje",
    "porecze-do-balustrad.html": "Realizacje",
    "meble-kute-sklep.html": "Sklep",
    "renowacja-metaloplastyki.html": "Usługi",
    "nasza-pracownia-lodz.html": "Pracownia",
    "pracownia-jubilerska-lodz.html": "Pracownia",
    "kowalstwo-lodz.html": "Kontakt",
    "kowalstwo-artystyczne-warszawa.html": "Oddział",
}
EYEBROWS_EN = {
    "internal-railings.html": "Portfolio",
    "forged-internal-railings.html": "Portfolio",
    "exterior-railings.html": "Portfolio",
    "forged-furniture.html": "Portfolio",
    "forged-fences-and-gates.html": "Portfolio",
    "interior-designe.html": "Portfolio",
    "designs-and-making.html": "Portfolio",
    "metalwork.html": "Portfolio",
    "artistic-blacksmithing.html": "Craft",
    "handrails-for-railings.html": "Portfolio",
    "shop.html": "Shop",
    "contact.html": "Contact",
}


def extract(html):
    """Pull title, description, keywords, h1, content."""
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title.group(1).strip() if title else ""

    desc = re.search(r'name="description"\s+content="([^"]*)"', html)
    desc = desc.group(1) if desc else ""

    kw = re.search(r'name="keywords"\s+content="([^"]*)"', html)
    kw = kw.group(1) if kw else ""

    # First H1 (for page banner) — strip out from main content too later
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    h1 = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else ""

    # Content extraction — supports old layout (<section class="tresc">) and v2 (<article class="prose">/.gallery wrapper).
    m = re.search(r'<section class="tresc">(.*?)</section>\s*(?:</main>|<iframe[^>]*src="https://www\.google|<footer)',
                  html, re.S)
    if not m:
        # v2 layout: pull everything inside the page's main content section (after page-banner + ornament)
        m = re.search(r'<main>\s*<section class="page-banner">.*?</section>\s*(?:<div class="ornament".*?</div>\s*)?<section class="section">\s*<div class="container">\s*(.*?)\s*</div>\s*</section>\s*</main>',
                      html, re.S)
    content = m.group(1) if m else ""

    # If v2 fade-up wrapper is present, unwrap it
    content = re.sub(r'^\s*<(article|div) class="(?:prose )?fade-up[^"]*">(.*)</\1>\s*$',
                     r'\2', content, flags=re.S).strip()
    content = re.sub(r'^\s*<article class="prose fade-up">(.*)</article>\s*$',
                     r'\1', content, flags=re.S).strip()
    content = re.sub(r'^\s*<div class="fade-up">(.*)</div>\s*$',
                     r'\1', content, flags=re.S).strip()

    # Drop the first <h1>...</h1> from content (we use it as page banner)
    content = re.sub(r"<h1[^>]*>.*?</h1>", "", content, count=1, flags=re.S)
    return title, desc, kw, h1, content


def transform_content(content):
    """Convert old structures to v2 classes."""
    # Old gallery class to new
    content = content.replace('<section class="galeria">', '<div class="gallery">')
    # Closing tag for galeria — map any nested </section> immediately following figures
    # Simplest: count <section class="galeria"> openings → replace each occurrence's matching </section>.
    # We can't reliably balance with regex; instead replace every '<section class="galeria">...</section>'
    # via a non-greedy single block (galleries don't nest).
    content = re.sub(
        r'<section class="galeria">(.*?)</section>',
        lambda m: f'<div class="gallery">{m.group(1)}</div>',
        content, flags=re.S)

    # Strip fancybox class but keep links — vanilla lightbox uses .gallery a[href]
    content = re.sub(r'\bclass="fancybox"\s*', '', content)
    content = re.sub(r'\s*rel="group"', '', content)

    # Wrap top-level paragraphs/headings in .prose if not already wrapped
    return content.strip()


def crumb_html(label, root_prefix, lang):
    home = "Strona główna" if lang == "pl" else "Home"
    return (f'<nav class="crumbs" aria-label="Breadcrumb">'
            f'<a href="{root_prefix}index.html">{home}</a>'
            f'<span class="sep">›</span>'
            f'<span>{label}</span>'
            f'</nav>')


def process(filepath, lang):
    with open(filepath, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "cp1250", "latin-1"):
        try:
            html = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    title, desc, kw, h1, raw_content = extract(html)
    if not raw_content:
        print(f"SKIP {filepath}: no .tresc found")
        return

    content = transform_content(raw_content)
    name = os.path.basename(filepath)

    if lang == "pl":
        eyebrow = EYEBROWS_PL.get(name, "Iron-Art")
        asset_prefix = "assets/"
        root_prefix = ""
        pl_index = "index.html"
        en_index = "en/index.html"
    else:
        eyebrow = EYEBROWS_EN.get(name, "Iron-Art")
        asset_prefix = "../assets/"
        root_prefix = "../"
        pl_index = "../index.html"
        en_index = "index.html"

    crumb = crumb_html(h1 or title, root_prefix, lang)

    # Decide content wrapper: prose for text-heavy, plain container for galleries
    has_gallery = '<div class="gallery">' in content
    if has_gallery:
        body_inner = f'<div class="fade-up">{content}</div>'
    else:
        body_inner = f'<article class="prose fade-up">{content}</article>'

    out = page_template(
        lang=lang,
        asset_prefix=asset_prefix,
        root_prefix=root_prefix,
        title=title,
        description=desc,
        keywords=kw,
        page_h1=h1 or title,
        page_eyebrow=eyebrow,
        body_inner=body_inner,
        active_slug=name,
        breadcrumb_html=crumb,
        pl_index=pl_index,
        en_index=en_index,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK   {filepath}")


def main():
    pl_pages = [p for p in glob.glob(os.path.join(ROOT, "*.html")) if os.path.basename(p) != "index.html"]
    en_pages = [p for p in glob.glob(os.path.join(ROOT, "en", "*.html")) if os.path.basename(p) != "index.html"]
    for p in pl_pages:
        process(p, "pl")
    for p in en_pages:
        process(p, "en")
    # also rebuild en/index.html with banner-style hero (no video — keeps spec)
    en_idx = os.path.join(ROOT, "en", "index.html")
    if os.path.isfile(en_idx):
        process(en_idx, "en")


if __name__ == "__main__":
    main()
