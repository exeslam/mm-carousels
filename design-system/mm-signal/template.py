"""Шаблон mm-signal (по мотивам МТС): обложка с крупным красно-глянцевым 3D за краем и пилюлями,
пункты — графитовые промо-плитки с широким заголовком, стеклянным диалогом и кнопкой-стрелкой,
графики — глянцевые капсулы и значок «%», сравнение — огромные широкие цифры на плитке, финал — белые карточки и красная кнопка.
Глянцевые объекты (щит, «%», галочка) — свои SVG; рендеры — assets/renders/mts-style (Unsplash)."""
import json, os, re, shutil

R_DIR = 'assets/renders/mts-style'


def gloss_defs(uid):
    return (f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8494"/><stop offset=".45" stop-color="#FF2B45"/><stop offset="1" stop-color="#B80019"/></linearGradient>'
            f'<radialGradient id="h{uid}" cx=".35" cy=".25" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<filter id="s{uid}" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="18" stdDeviation="16" flood-color="#B80019" flood-opacity=".35"/></filter></defs>')


def shield(uid='sh'):
    p = 'M100 12 L176 40 V98 C176 150 142 182 100 198 C58 182 24 150 24 98 V40 Z'
    return (f'<svg viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg">{gloss_defs(uid)}<g filter="url(#s{uid})"><path d="{p}" fill="url(#g{uid})"/>'
            f'<path d="{p}" fill="url(#h{uid})"/><path d="M64 104l26 26 50-54" fill="none" stroke="#fff" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/></g></svg>')


def percent(uid='pc'):
    return (f'<svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">{gloss_defs(uid)}<g filter="url(#s{uid})"><circle cx="110" cy="104" r="92" fill="url(#g{uid})"/>'
            f'<circle cx="110" cy="104" r="92" fill="url(#h{uid})"/><text x="110" y="140" text-anchor="middle" font-family="Flex" font-stretch="125%" font-weight="700" font-size="112" fill="#fff">%</text></g></svg>')


def bubble(uid='bb'):
    p = 'M40 30 H170 A30 30 0 0 1 200 60 V130 A30 30 0 0 1 170 160 H95 L55 195 V160 H40 A30 30 0 0 1 10 130 V60 A30 30 0 0 1 40 30 Z'
    return (f'<svg viewBox="0 0 210 215" xmlns="http://www.w3.org/2000/svg">{gloss_defs(uid)}<g filter="url(#s{uid})"><path d="{p}" fill="url(#g{uid})"/><path d="{p}" fill="url(#h{uid})"/>'
            f'<circle cx="65" cy="95" r="13" fill="#fff"/><circle cx="105" cy="95" r="13" fill="#fff"/><circle cx="145" cy="95" r="13" fill="#fff"/></g></svg>')


def bolt(uid='bt'):
    p = 'M120 10 L40 120 H95 L80 205 L170 85 H112 Z'
    return (f'<svg viewBox="0 0 210 215" xmlns="http://www.w3.org/2000/svg">{gloss_defs(uid)}<g filter="url(#s{uid})"><path d="{p}" fill="url(#g{uid})" stroke="#FF8494" stroke-width="3" stroke-linejoin="round"/><path d="{p}" fill="url(#h{uid})"/></g></svg>')


def tick(uid):
    return (f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{gloss_defs(uid)}<circle cx="50" cy="48" r="42" fill="url(#g{uid})"/>'
            f'<circle cx="50" cy="48" r="42" fill="url(#h{uid})"/><path d="M31 49l13 13 25-27" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def render(spec, c):
    e, svg, N, out, ROOT = c['e'], c['svg'], c['N'], c['out'], c['ROOT']
    used = c.setdefault('used_assets', [])

    def asset(name):
        src = os.path.join(ROOT, R_DIR, name + '.jpg')
        shutil.copy(src, f'{out}/assets/{name}.jpg')
        used.append(json.load(open(os.path.join(ROOT, R_DIR, name + '.json'))) | {'file': name + '.jpg'})
        return f'./assets/{name}.jpg'

    def bar(i, dark=False):
        return (f'<div class="bar"><span class="tag cap"><i></i>{e(spec["handle"])}</span><span class="tag cap">{i:02d} / {N:02d}</span></div>')

    S = []
    cv = spec['cover']
    S.append(f'''<section class="slide cover" id="slide-01">{bar(1)}
  <h1 class="h">{cv["title_html"]}</h1><p class="lead">{e(cv["sub"])}</p>
  <img class="obj" src="{asset(cv.get("signal_render", "red-layers"))}" alt="">
  <div class="btns"><span class="pbtn red cap">{e(cv.get("chip_lbl", "сохрани"))}</span><span class="pbtn white cap">листай →</span></div>
</section>''')

    for k, it in enumerate(spec['items']):
        i = k + 2
        num = f'<span class="num cap">{k + 1:02d}</span>'
        if it.get('chart'):
            ch = it['chart']; mx = max(r[1] for r in ch['rows'])
            rows = ''.join(f'<div><div class="nm">{e(r[0])}<small>{e(r[2])}</small></div><div class="row"><div class="cap-bar{" hot" if j == ch.get("hot", 0) else ""}" style="width:{max(r[1] / mx * 100, 9):.0f}%"></div>'
                           f'<div class="v{" hot" if j == ch.get("hot", 0) else ""}">{e(r[3] if len(r) > 3 else r[1])}</div></div></div>' for j, r in enumerate(ch['rows']))
            S.append(f'''<section class="slide chart-slide" id="slide-{i:02d}">{bar(i)}
  <h2 class="h">{it["h"]}</h2><p class="lead">{e(it["p"])}</p>
  <div class="badge">{percent(f"pc{i}")}</div>
  <div class="chart">{rows}</div></section>''')
            continue
        if it.get('stat'):
            a, b = it['stat']
            S.append(f'''<section class="slide stat" id="slide-{i:02d}">{bar(i)}
  <div class="tile"><img class="obj" src="{asset("glass-cube-heart")}" alt="" style="mix-blend-mode:screen;opacity:.55">
    <div class="in">{num}<h2 class="h">{it["h"]}</h2><p class="lead">{e(it["p"])}</p></div>
    <div class="a"><div class="n">{e(a[0])}</div><div class="l">{e(a[1])} · {e(a[2])}</div></div>
    <div class="b"><div class="n">{e(b[0])}</div><div class="l">{e(b[1])} · {e(b[2])}</div></div>
  </div></section>''')
            continue
        light = bool(it.get('demo'))
        if it.get('reply'):
            ctx = f'<div class="bub ctx">{e(it["ctx"])}</div>' if it.get('ctx') else ''
            inner = f'<div class="dialog">{ctx}<div class="bub me">{e(it["quote"])}</div><div class="bub">{e(it["reply"])}</div></div>'
        elif it.get('demo'):
            demo = re.sub(r'\{\{icon:([\w-]+)\}\}', lambda m: svg(m.group(1)), it['demo'])
            inner = f'<div class="demo">{demo}</div><div class="instead"><span class="cap" style="color:var(--red)">{e(it["lbl"])}</span><p>{e(it.get("quote", ""))}</p></div>'
        else:
            inner = f'<div class="dialog"><div class="bub me">{e(it["quote"])}</div></div>'
        objs = [lambda: bubble(f'bb{i}'), lambda: bolt(f'bt{i}'), lambda: shield(f'sh{i}'), lambda: percent(f'pp{i}')]
        deco = '' if light else f'<div class="gl">{objs[k % len(objs)]()}</div>'
        S.append(f'''<section class="slide item" id="slide-{i:02d}">{bar(i)}
  <div class="tile{" light" if light else ""}">
    <div class="in">{num}<h2 class="h">{it["h"]}</h2><p class="lead">{e(it["p"])}</p></div>
    {deco}{inner}<span class="arrow">→</span></div></section>''')

    f = spec['final']
    lis = ''.join(f'<div class="li">{tick(f"t{j}")}{e(x)}</div>' for j, x in enumerate(f['list']))
    S.append(f'''<section class="slide final" id="slide-{N:02d}">{bar(N)}
  <h2 class="h">{f["title_html"]}</h2>
  <div class="list">{lis}</div>
  <div class="go"><span class="cap"><small>{e(f["save_lbl"])}</small>{e(f["save"])}</span><span class="arrow">→</span></div>
</section>''')
    return S
