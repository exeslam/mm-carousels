"""Шаблон слайдов mm-apple: обложка с рендером за край, пункты (чат / мини-макет / цитата / график), финал-шпаргалка."""
import os, re, shutil, sys


def render(spec, c):
    e, svg, OK, N, out = c['e'], c['svg'], c['OK'], c['N'], c['out']
    ROOT, A = c['ROOT'], c['A']
    spec_path = c['spec_path']
    def top(i):
        return f'<div class="top"><span class="pill"><i class="dot"></i>{e(spec["handle"])}</span><span class="pill">{i:02d} / {N:02d}</span></div>'


    def foot(left, right):
        return f'<div class="foot"><span>{e(left)}</span><span class="next">{e(right)}</span></div>'


    S = []

    # 01 · обложка: рендер крупнее кадра, уходит за правый нижний край; стеклянная плашка поверх
    c = spec['cover']
    r = c['render']
    src_render = os.path.join(ROOT, 'releases', c.get('render_from') or spec.get('id') or os.path.splitext(os.path.basename(spec_path))[0], 'assets')
    if not os.path.exists(f'{out}/assets/cover-render.jpg') and os.path.exists(f'{src_render}/cover-render.jpg'):
        for x in ['cover-render.jpg', 'cover-render.json']: shutil.copy(f'{src_render}/{x}', f'{out}/assets/{x}')
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
        if it.get('chart'):
            ch = it['chart']; mx = max(r[1] for r in ch['rows'])
            rows = ''.join(f'<div class="bar{" hot" if k == ch.get("hot", 0) else ""}"><span class="name">{e(r[0])}</span><span class="track"><i style="width:{max(r[1] / mx * 100, 1.5):.1f}%"></i></span><span class="v">{e(r[3] if len(r) > 3 else str(r[1]))}<span class="n">{e(r[2])}</span></span></div>' for k, r in enumerate(ch['rows']))
            cards = f'<div class="t"><span class="lbl">{e(ch["title"])}</span><div class="bars">{rows}</div></div>' + (f'<div class="t blue" style="flex:none"><span class="lbl">{e(it["lbl"])}</span><div class="quote">{e(it["quote"])}</div></div>' if it.get('quote') else '')
        elif it.get('stat'):
            a, b = it['stat']
            cards = (f'<div class="row2"><div class="t blue"><span class="lbl">{e(a[1])}</span><div class="big">{e(a[0])}</div><p>{e(a[2])}</p></div>'
                     f'<div class="t"><span class="lbl">{e(b[1])}</span><div class="big">{e(b[0])}</div><p>{e(b[2])}</p></div></div>')
        elif it.get('demo') and it.get('quote'):
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

    return S
