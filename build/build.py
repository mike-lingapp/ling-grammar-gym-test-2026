"""Assemble the Ling Wrapped 2026 prototype into one self-contained HTML file.
Run from the build folder: python3 build.py  -> ../ling-wrapped-prototype.html
"""
import base64, json, mimetypes, os, re
from motion_css import convert

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'dist', 'ling-wrapped-prototype.html')   # Claude artifact (no document skeleton)
OUT_SITE = os.path.join(HERE, '..', 'ling-wrapped-2026', 'index.html')  # GitHub Pages page
RIVS = {'bg': 'lingwrapped-bg-anim.riv', 'start': 'lingwrapped-start-complete-anim.riv', 'logocards': 'lingwrapped-logo-cards-anim.riv'}

def read(p):
    return open(os.path.join(HERE, p), encoding='utf-8').read()

# ---------- shared components ----------
LOGO_SYMBOL = [  # (inset, file) - same percentages for md and sm logo
    ('37.77% 72.68% 45.36% 4.6%', 0), ('38.18% 4.26% 44.95% 73.03%', 1),
    ('35.64% 12.15% 22.1% 12.56%', 2), ('21.29% 12.3% 42.37% 12.83%', 3),
    ('41.48% 20.32% 27.94% 20.73%', 4), ('32.1% 49.69% 46.07% 20.96%', 5),
    ('32.1% 20.55% 46.07% 50.1%', 6), ('1% 10% 68.16% 1.39%', 7),
    ('49.73% 42.99% 48.24% 43.87%', 8)]
LOGO_FILES = {
    'md': ['9e3b6', '31a3a', 'b96f1', 'f74ef', 'cb1a7', 'a8fa5', '101c7', 'bafb8', '16b67', '5441c'],
    'sm': ['29a8e', '4214e', '7163d', 'edd51', '775c6', 'a55bb', '6de4d', 'd8fb8', 'f083c', '506e4'],
}

def logo(size):
    f = LOGO_FILES[size]
    sym = ''.join(f'<div style="position:absolute;inset:{ins}"><img class="f" src="assets/common/logo-{size}/{f[i]}.svg"></div>' for ins, i in LOGO_SYMBOL)
    typ = f'<div style="position:absolute;inset:24.22% 1.38% 2.21% 1.52%"><img class="f" src="assets/common/logo-{size}/{f[9]}.svg"></div>'
    if size == 'md':
        return (f'<div style="position:relative;width:136px;height:59px"><div style="position:absolute;left:0;top:0;width:42px;height:59px;overflow:hidden">{sym}</div>'
                f'<div style="position:absolute;left:52.51px;top:0;width:82px;height:59px">{typ}</div></div>')
    return (f'<div style="position:relative;width:84px;height:36px"><div style="position:absolute;inset:0 69% -1.61% 0;overflow:hidden">{sym}</div>'
            f'<div style="position:absolute;inset:0 0.72% -1.61% 38.76%">{typ}</div></div>')

STATUS = '''<div class="status"><span class="time">9:41</span>
<div style="position:absolute;right:64.4px;top:16.6px;width:17.1px;height:10.7px"><img class="f" src="assets/common/00a6e.svg"></div>
<div style="position:absolute;right:44px;top:16.4px;width:15.4px;height:11.057px"><img class="f" src="assets/common/a8d46.svg"></div>
<div style="position:absolute;right:14.5px;top:16.16px;width:24.5px;height:11.5px"><img class="f" src="assets/common/28990.svg"></div>
<div style="position:absolute;right:19px;top:18.08px;width:18px;height:7.667px;border-radius:1.6px;background:#fff"></div></div>'''

HOLE = '<img class="hole" src="assets/common/hole.svg" alt="">'

def card(label, value, bottom):
    return f'''<div class="card"><div class="card-row top">{HOLE}<p class="card-label">{label}</p>{HOLE}</div>
<div class="card-num"><p>{value}</p></div>
<div class="card-row bot">{HOLE}<p class="card-bottom">{bottom}</p>{HOLE}</div></div>'''

def topnav(shadow):
    return f'''<div class="topnav"><div class="progress">{''.join('<div class="seg"><i></i></div>' for _ in range(6))}</div>
<div class="navrow"><div class="pill" style="box-shadow:0 8px 24px 0 {shadow}">{logo('sm')}</div>
<button class="iconbtn js-close" aria-label="Close"><span><img src="assets/common/close.svg" alt=""></span></button></div></div>'''

def buttons(primary, secondary=None, primary_cls='js-share', secondary_cls='js-next'):
    b = f'<button class="btn btn-brand {primary_cls}">{primary}</button>'
    if secondary:
        b += f'<button class="btn btn-white {secondary_cls}">{secondary}</button>'
    return f'<div class="bottom">{b}<div class="home"><i></i></div></div>'

def frag_parts(key):
    html = read(f'slides/{key}.html')
    i = html.find('<div class="illus"')
    return html[:i].strip(), html[i:].strip()

# ---------- slides ----------
SLIDES = json.load(open(os.path.join(HERE, 'slides.json')))

def build_slide(s):
    key = s['key']
    bg, illus = frag_parts(key)
    if s.get('rive'):  # Rive background replaces the Figma-exported animated layer
        vm = f' data-vm="{s["vm"]}"' if s.get('vm') else ''
        bg = (f'<div class="bg-layer" style="position:absolute;left:50%;top:0;width:1120px;height:844px;transform:translateX(-50%);overflow:hidden;background:{s.get("bgcolor", "#011133")}">'
              f'<canvas class="rive" data-riv="{s["rive"]}"{vm} style="position:absolute;inset:0;width:1120px;height:844px"></canvas></div>')
    if key == 'start':
        inner = f'''{bg}<div class="screen">{STATUS}
<button class="iconbtn js-close" aria-label="Close" style="top:48px;z-index:5"><span><img src="assets/common/close.svg" alt=""></span></button>
<div class="body"><div style="padding-top:24px;display:flex;justify-content:center"><div class="pill pill-md">{logo('md')}</div></div></div>
{buttons('Start', 'Share', primary_cls='js-start', secondary_cls='js-share')}</div>'''
    elif s.get('custom'):
        inner = f'''{bg}<div class="screen">{STATUS}
<div class="body"><div class="content">{topnav(s['shadow'])}{illus}</div></div>
{buttons(*s['buttons'], primary_cls='js-share', secondary_cls='js-finish')}</div>'''
    else:
        inner = f'''{bg}<div class="screen">{STATUS}
<div class="body center"><div class="content">{topnav(s['shadow'])}
<div class="cardContainer"><div class="illus-wrap">{illus}</div>{card(*s['card'])}</div></div></div>
{buttons('Share', 'Next')}</div>'''
    return f'<section class="slide slide-{key}" data-key="{key}">{inner}</section>'

def motion_styles():
    css = []
    for s in SLIDES:
        p = os.path.join(HERE, f"motion-{s['key']}.json")
        if os.path.exists(p) and not s.get('rive') and s['key'] != 'summary':
            css.append(convert(p, s['key']))
    p = os.path.join(HERE, 'motion-floaticon.json')
    if os.path.exists(p):
        css.append(convert(p, 'floaticon', '.floaticon'))
    return '\n'.join(css)

def strip_motion_inline_transform(html):
    # data-m elements get their transform from the motion CSS; an inline transform would win over it.
    def fix(m):
        tag = m.group(0)
        return re.sub(r'(style="[^"]*?)(?<![-\w])transform:[^;"]*;?', r'\1', tag)
    return re.sub(r'<div[^>]*\bdata-m="[^"]*"[^>]*>', fix, html)

def inline_assets(html):
    cache = {}
    def rep(m):
        path = m.group(2)
        if path not in cache:
            full = os.path.join(HERE, path)
            mime = mimetypes.guess_type(full)[0] or 'application/octet-stream'
            if path.endswith('.svg'): mime = 'image/svg+xml'
            cache[path] = f'data:{mime};base64,' + base64.b64encode(open(full, 'rb').read()).decode()
        return m.group(1) + cache[path]
    return re.sub(r'(src=["\']|url\(|["\'])(assets/[^"\')]+)', rep, html)

def main():
    entry = json.load(open(os.path.join(HERE, 'slides/entry.json')))
    share_screen = read('slides/share-screen.html') if os.path.exists(os.path.join(HERE, 'slides/share-screen.html')) else ''
    floaticon = read('slides/floaticon.html') if os.path.exists(os.path.join(HERE, 'slides/floaticon.html')) else ''
    slides_html = '\n'.join(build_slide(s) for s in SLIDES)
    tpl = read('template.html')
    shares = {s['key']: s.get('share') for s in SLIDES}
    page = (tpl.replace('/*MOTION*/', motion_styles())
               .replace('<!--SLIDES-->', slides_html)
               .replace('<!--SHARE-->', share_screen)
               .replace('<!--FLOATICON-->', floaticon)
               .replace('/*ENTRY*/', json.dumps(entry))
               .replace('/*SHARES*/', json.dumps(shares))
               .replace('/*RIVS*/', json.dumps({k: base64.b64encode(open(os.path.join(HERE, 'assets/rive', f), 'rb').read()).decode() for k, f in RIVS.items()}))
               .replace('<!--SHAREIMGS-->', ''.join(f'<img data-k="{k}" src="assets/share/{v}" alt="">' for k, v in shares.items() if v and os.path.exists(os.path.join(HERE, 'assets/share', v)))))
    page = strip_motion_inline_transform(page)
    page = inline_assets(page)
    # GitHub Pages version: full document.
    head_end = page.index('</head>')
    site = page[:head_end].replace('<head>', '<head>\n<meta name="robots" content="noindex">') + page[head_end:]
    os.makedirs(os.path.dirname(OUT_SITE), exist_ok=True)
    open(OUT_SITE, 'w', encoding='utf-8').write(site)
    import shutil
    for d in (os.path.dirname(OUT_SITE), os.path.dirname(OUT)):
        os.makedirs(d, exist_ok=True)
        shutil.copyfile(os.path.join(HERE, 'assets/rive/rive.wasm'), os.path.join(d, 'rive.wasm'))
    # Artifact skeleton supplies doctype/html/head/body; keep the page content only.
    for tag in ['<!doctype html>', '<html lang="en">', '<head>', '</head>', '<body>', '</body>', '</html>',
                '<meta charset="utf-8">', '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">']:
        page = page.replace(tag, '')
    page = page.strip()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(page)
    missing = re.findall(r'src="assets/[^"]+"', page)
    print('wrote', OUT, f'{len(page)/1e6:.2f} MB', 'unresolved:', missing[:5])

if __name__ == '__main__':
    main()
