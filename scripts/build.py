"""Собирает карусель из спеки: specs/<id>.json → releases/<id>/source.html (+ стили, шрифты, ассеты).

    python3 scripts/build.py specs/mm-5-phrases-chatgpt.json

Рендер PNG после сборки: node scripts/render.mjs releases/<id>
Формат спеки — в README.md, раздел «Спека карусели».
"""
import html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'assets')
spec_path = sys.argv[1]
spec = json.load(open(spec_path))
rid = spec.get('id') or os.path.splitext(os.path.basename(spec_path))[0]
out = os.path.join(ROOT, 'releases', rid)
os.makedirs(out + '/assets/fonts', exist_ok=True)
e = html.escape


def svg(name):
    return re.sub(r' width="24" height="24"', '', open(f'{A}/icons/tabler/{name}.svg').read())


OK = f'<span class="ok">{svg("circle-check-filled")}</span>'
N = 2 + len(spec['items'])


def top(i):
    return f'<div class="top"><span class="pill"><i class="dot"></i>{e(spec["handle"])}</span><span class="pill">{i:02d} / {N:02d}</span></div>'


def foot(left, right):
    return f'<div class="foot"><span>{e(left)}</span><span class="next">{e(right)}</span></div>'


S = []

# 01 · обложка: рендер крупнее кадра, уходит за правый нижний край; стеклянная плашка поверх
c = spec['cover']
r = c['render']
if not os.path.exists(f'{out}/assets/cover-render.jpg'):
    sys.exit(f'нет {out}/assets/cover-render.jpg — положи рендер и cover-render.json (источник, автор, лицензия)')
S.append(f'''<section class="slide cover has-render" id="slide-01">{top(1)}
  <div class="head"><h1>{c["title_html"]}</h1><p>{e(c["sub"])}</p></div>
  <img class="cover-render" src="./assets/cover-render.jpg" alt="" style="width:{r["w"]}px;left:{r["left"]}px;top:{r["top"]}px">
  <div class="t chip"><span class="lbl">{e(c["chip_lbl"])}</span><h3>{e(c["chip"])}</h3></div>
  {foot(c.get("foot", ""), "листай →")}</section>''')

# 02…N-1 · пункты: чат, мини-макет «было / вместо», UI-шаг или цитата
for k, it in enumerate(spec['items']):
    i = k + 2
    if it.get('demo'):
        it['demo'] = re.sub(r'\{\{icon:([\w-]+)\}\}', lambda m: svg(m.group(1)), it['demo'])
    for a in it.get('assets', []):
        shutil.copy(f'{A}/3d/{a}', out + '/assets/' + a.replace('/', '-'))
    if it.get('demo') and it.get('quote'):
        cards = (f'<div class="row2"><div class="t demo-card"><span class="lbl">{e(it.get("bad_lbl", "было"))}</span><div class="demo">{it["demo"]}</div></div>'
                 f'<div class="t blue"><span class="lbl">{e(it["lbl"])}</span><div class="quote">{e(it["quote"])}</div></div></div>')
    elif it.get('demo'):
        cards = (f'<div class="t demo-card"><span class="lbl">{e(it["lbl"])}</span><div class="demo">{it["demo"]}</div>'
                 + (f'<p class="demo-cap">{e(it["cap"])}</p>' if it.get('cap') else '') + '</div>')
    elif it.get('reply'):
        ctx = f'<div class="msg me ctx">{e(it["ctx"])}</div>' if it.get('ctx') else ''
        cards = (f'<div class="t chat"><span class="lbl">{e(it.get("chat_lbl", "пример"))}</span>{ctx}'
                 f'<div class="msg me">{e(it["quote"])}</div><div class="msg ai">{e(it["reply"])}</div></div>')
    elif it.get('bad'):
        cards = (f'<div class="row2"><div class="t"><span class="lbl">{e(it.get("bad_lbl", "было"))}</span><div class="bad">{e(it["bad"])}</div></div>'
                 f'<div class="t blue"><span class="lbl">{e(it["lbl"])}</span><div class="quote">{e(it["quote"])}</div></div></div>')
    else:
        cards = f'<div class="t"><span class="lbl">{e(it["lbl"])}</span><div class="quote">{e(it["quote"])}</div></div>'
    nxt = 'дальше →' if k < len(spec['items']) - 1 else 'итог →'
    S.append(f'''<section class="slide item" id="slide-{i:02d}">{top(i)}
  <div class="idx">{it.get("n", k + 1)}</div>
  <div class="head"><h1>{it["h"]}</h1><p>{e(it["p"])}</p></div>
  <div class="stack">{cards}</div>
  {foot(it.get("foot", spec["title"]), nxt)}</section>''')

# N · финал: шпаргалка на всю высоту + «сохрани»
f = spec['final']
lis = ''.join(f'<div class="t li">{OK}<b>{e(x)}</b></div>' for x in f['list'])
S.append(f'''<section class="slide final" id="slide-{N:02d}">{top(N)}
  <div class="head"><h1>{f["title_html"]}</h1></div>
  <div class="list">{lis}<div class="t blue save"><span class="lbl">{e(f["save_lbl"])}</span><h3>{e(f["save"])}</h3></div></div>
  {foot(spec.get("tagline", "строим контент-машину в открытую"), spec["handle"])}</section>''')

open(out + '/source.html', 'w').write(
    '<!doctype html>\n<html lang="ru">\n<head><meta charset="utf-8"><link rel="stylesheet" href="./mm-apple.css"></head>\n<body>\n'
    + '\n\n'.join(S) + '\n<script src="./liquid.js"></script>\n</body>\n</html>\n')
for x in ['mm-apple.css', 'liquid.js']:
    shutil.copy(f'{ROOT}/design-system/{x}', out)
shutil.copy(f'{A}/fonts/Inter/inter-cyrillic-wght-normal.woff2', out + '/assets/fonts/Inter-Cyrillic.woff2')
shutil.copy(f'{A}/fonts/Inter/inter-latin-wght-normal.woff2', out + '/assets/fonts/Inter-Latin.woff2')
labels = ['обложка'] + [re.sub('<[^>]+>', '', it.get('label', it['h']))[:28] for it in spec['items']] + ['итог']
json.dump({'id': rid, 'title': spec['title'], 'account': spec['handle'], 'status': spec.get('status', 'awaiting-review'),
           'cover': json.load(open(out + '/assets/cover-render.json')), 'icons': 'Tabler (MIT)', 'font': 'Inter (OFL)',
           'slides': [{'id': f'{i + 1:02d}', 'label': l} for i, l in enumerate(labels)]},
          open(out + '/meta.json', 'w'), ensure_ascii=False, indent=2)
if spec.get('caption'):
    open(out + '/caption.txt', 'w').write(spec['caption'] + '\n')
print(f'{rid}: {N} slides → releases/{rid}/source.html')
