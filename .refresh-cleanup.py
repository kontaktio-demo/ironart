"""Final cleanup: strip HTML comments, normalise punctuation, collapse blank lines."""
import re, glob, os

REPL = {
    "–": "-", "—": "-",
    "…": "...",
    "“": '"', "”": '"',
    "„": '"', "‚": "'",
    "‘": "'", "’": "'",
    " ": " ",
}

def normalise(text):
    for k, v in REPL.items():
        text = text.replace(k, v)
    return text

def clean_html(path):
    with open(path, 'rb') as f: raw = f.read()
    for enc in ('utf-8', 'cp1250', 'latin-1'):
        try: html = raw.decode(enc); break
        except UnicodeDecodeError: continue

    # strip HTML comments (preserve IE conditionals if any)
    html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.S)
    # strip orphan blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    # normalise punctuation
    html = normalise(html)
    # tidy trailing whitespace on lines
    html = re.sub(r'[ \t]+\n', '\n', html)

    with open(path, 'w', encoding='utf-8') as f: f.write(html)

def clean_css(path):
    with open(path, 'r', encoding='utf-8') as f: css = f.read()
    # strip /* ... */ comments but keep file-header (first one if it spans multiple lines and looks like header)
    css = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css)
    css = re.sub(r'\n{3,}', '\n\n', css)
    with open(path, 'w', encoding='utf-8') as f: f.write(css)

def clean_js(path):
    with open(path, 'r', encoding='utf-8') as f: js = f.read()
    # strip single-line // comments at line start (but keep code after //)
    js = re.sub(r'^\s*//.*$', '', js, flags=re.M)
    js = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', js)
    js = re.sub(r'\n{3,}', '\n\n', js)
    with open(path, 'w', encoding='utf-8') as f: f.write(js)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for p in glob.glob('*.html'):
        clean_html(p)
    for p in glob.glob('assets/css/*.css'):
        clean_css(p)
    for p in glob.glob('assets/js/*.js'):
        clean_js(p)
    print('cleanup done')
