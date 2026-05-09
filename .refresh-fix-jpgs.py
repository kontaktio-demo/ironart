import os, glob

# 1) find bad jpgs
bad = []
for f in glob.glob('assets/images/**/*.jpg', recursive=True):
    if os.path.getsize(f) == 14326:
        bad.append(f.replace(os.sep, '/'))
print(f'Bad JPGs found: {len(bad)}')

# 2) classify
fixable = {}
hopeless = []
for jpg in bad:
    webp = jpg[:-4] + '.webp'
    if os.path.exists(webp) and os.path.getsize(webp) > 1000:
        fixable[jpg] = webp
    else:
        hopeless.append(jpg)
print(f'Replaceable with webp: {len(fixable)}')
print(f'No webp sibling: {len(hopeless)}')

# 3) rewrite HTML
html_files = glob.glob('*.html')
total_fixes = 0
for hf in html_files:
    with open(hf, 'r', encoding='utf-8') as f: txt = f.read()
    new = txt
    for jpg, webp in fixable.items():
        new = new.replace(jpg, webp)
    if new != txt:
        with open(hf, 'w', encoding='utf-8') as f: f.write(new)
        total_fixes += 1
print(f'HTML files updated: {total_fixes}')

# 4) delete the bad jpgs that were replaced
for jpg in fixable:
    try: os.remove(jpg)
    except OSError: pass

# 5) check which hopeless ones still appear in HTML
all_html = '\n'.join(open(h, encoding='utf-8').read() for h in html_files)
still_referenced = [j for j in hopeless if os.path.basename(j) in all_html]
print(f'Hopeless JPGs still in HTML: {len(still_referenced)}')
with open('.broken-jpgs.txt', 'w', encoding='utf-8') as f:
    for j in still_referenced:
        f.write(j + '\n')
