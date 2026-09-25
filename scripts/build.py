"""Собирает карусель из спеки: specs/<id>.json → releases/<id>/source.html (+ стили, шрифты, ассеты).

    python3 scripts/build.py specs/mm-5-phrases-chatgpt.json

Другая дизайн-система: python3 scripts/build.py specs/<id>.json <design>  → releases/<id>--<design>
Рендер PNG после сборки: node scripts/render.mjs releases/<id>
Формат спеки — в README.md, раздел «Спека карусели».
"""
import html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'assets')
spec_path = sys.argv[1]
spec = json.load(open(spec_path))
design = (sys.argv[2] if len(sys.argv) > 2 else None) or spec.get('design', 'mm-apple')
DS = os.path.join(ROOT, 'design-system', design)
system = json.load(open(os.path.join(DS, 'system.json')))
rid = spec.get('id') or os.path.splitext(os.path.basename(spec_path))[0]
if design != spec.get('design', 'mm-apple'):
    rid = f'{rid}--{design}'          # та же спека в другой системе — отдельный выпуск для сравнения
out = os.path.join(ROOT, 'releases', rid)
os.makedirs(out + '/assets/fonts', exist_ok=True)
e = html.escape


ICON_SET = system.get('icons', 'tabler')


def svg(name):
    if '/' in name:
        s_, name = name.split('/', 1)
    else:
        s_ = ICON_SET
        name = system.get('icon_map', {}).get(name, name)
    return re.sub(r' (width|height)="[^"]*"', '', open(f'{A}/icons/{s_}/{name}.svg').read(), count=2)


OK = f'<span class="ok">{svg(system.get("check_icon", "tabler/circle-check-filled"))}</span>'
N = 2 + len(spec['items'])


import importlib.util
ctx = dict(e=e, svg=svg, OK=OK, N=N, out=out, ROOT=ROOT, A=A, spec_path=spec_path, system=system)
tspec = importlib.util.spec_from_file_location('tpl', os.path.join(DS, 'template.py'))
tpl = importlib.util.module_from_spec(tspec); tspec.loader.exec_module(tpl)
S = tpl.render(spec, ctx)

open(out + '/source.html', 'w').write(
    f'<!doctype html>\n<html lang="ru">\n<head><meta charset="utf-8"><link rel="stylesheet" href="./{system["css"]}"></head>\n<body class="ds-{design}">\n'
    + '\n\n'.join(S) + '\n' + ''.join(f'<script src="./{x}"></script>\n' for x in system.get('scripts', [])) + '</body>\n</html>\n')
for x in [system['css']] + system.get('scripts', []):
    shutil.copy(f'{DS}/{x}', out)
for src, dst in system['fonts']:
    shutil.copy(os.path.join(ROOT, src), out + '/assets/fonts/' + dst)
labels = ['обложка'] + [re.sub('<[^>]+>', '', it.get('label') or it.get('h') or it.get('title') or it.get('statement') or re.sub(r'[\[\]]', '', it.get('say', '')))[:28] for it in spec['items']] + ['итог']
json.dump({'id': rid, 'design': design, 'title': spec['title'], 'account': spec['handle'], 'status': spec.get('status', 'awaiting-review'),
           'cover': (json.load(open(out + '/assets/cover-render.json')) if os.path.exists(out + '/assets/cover-render.json') else None), 'assets': ctx.get('used_assets', []), 'icons': system.get('icons_label', 'Tabler (MIT)'), 'font': system.get('font_label', 'Inter (OFL)'),
           'slides': [{'id': f'{i + 1:02d}', 'label': l} for i, l in enumerate(labels)]},
          open(out + '/meta.json', 'w'), ensure_ascii=False, indent=2)
if spec.get('caption'):
    open(out + '/caption.txt', 'w').write(spec['caption'] + '\n')
print(f'{rid}: {N} slides → releases/{rid}/source.html')
