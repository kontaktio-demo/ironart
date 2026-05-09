import os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
files = glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'en', '*.html'))
for path in files:
    with open(path, 'rb') as f: raw = f.read()
    for enc in ('utf-8','cp1250','latin-1'):
        try:
            html = raw.decode(enc); break
        except UnicodeDecodeError:
            continue
    is_en = os.sep + 'en' + os.sep in path
    new = html
    if is_en:
        new = new.replace('href="index"', 'href="/en/"')
        new = new.replace('href="../index"', 'href="/"')
        new = new.replace('href="index.html"', 'href="/en/"')
        new = new.replace('href="../index.html"', 'href="/"')
    else:
        new = new.replace('href="index"', 'href="/"')
        new = new.replace('href="en/index"', 'href="/en/"')
        new = new.replace('href="index.html"', 'href="/"')
        new = new.replace('href="en/index.html"', 'href="/en/"')
    # also strip any remaining bare ".html"
    if new != html:
        with open(path, 'w', encoding='utf-8') as f: f.write(new)
print('home links normalised:', len(files), 'files')
