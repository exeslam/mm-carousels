"""Шаблон mm-expressive: композиции Material 3 Expressive.
Обложка — цветовое поле + гигантское «печенье» с числом за краем + наклейка-взрыв + FAB.
Пункт — номер в «клевере», заголовок, телефон с интерфейсом уходит за нижний край, карточка-вывод.
График — столбики-пилюли со стрелкой и значением в капсуле + наклейка. Сравнение — два числа в формах.
Финал — паттерн контуров компонентов, список M3, Extended FAB."""
import re

THEMES = ['th-light', 'th-dark', 'th-salmon']


def render(spec, c):
    e, svg, N = c['e'], c['svg'], c['N']
    icon = lambda n: svg(n)
    S = []

    def chips(i):
        return f'<div class="chips"><span class="chip"><i></i>{e(spec["handle"])}</span><span class="chip">{i:02d} / {N:02d}</span></div>'

    cv = spec['cover']
    big = cv.get('big') or str(len(spec['items']))
    S.append(f'''<section class="slide cover th-lav" id="slide-01">{chips(1)}
  <h1 class="display">{cv["title_html"]}</h1>
  <p class="sub">{e(cv["sub"])}</p>
  <div class="blob2"></div><div class="blob"></div>
  <div class="bignum">{e(big)}</div><div class="biglbl">{e(cv.get("big_lbl", ""))}</div>
  <div class="burst"><span>{e(cv.get("chip", ""))}</span></div>
  <div class="fab">{icon("arrow_forward")}листай</div>
</section>''')

    k_theme = 0
    for k, it in enumerate(spec['items']):
        i = k + 2
        th = THEMES[k % len(THEMES)]
        head = f'<div class="wrap"><div class="idx">{it.get("n", k + 1)}</div><h2 class="headline">{it["h"]}</h2><p class="support">{e(it["p"])}</p></div>'
        if it.get('chart'):
            ch = it['chart']; mx = max(r[1] for r in ch['rows'])
            rows = ''
            for j, r in enumerate(ch['rows']):
                w = 520 + (r[1] / mx) * 360
                rows += (f'<div class="row"><div class="bar c{j % 4}" style="width:{w:.0f}px"><span class="nm">{e(r[0])}<small>{e(r[2])}</small></span>'
                         f'<span class="val">{e(r[3] if len(r) > 3 else r[1])}</span></div><span class="tip tipc{j % 4}"></span></div>')
            body = (f'<div class="wrap"><h2 class="headline">{it["h"]}</h2><p class="support">{e(it["p"])}</p></div>'
                    f'<div class="burst"><span>{e(it.get("sticker", ""))}</span></div>'
                    f'<div class="chart"><div class="title">{e(ch["title"])}</div>{rows}</div>')
            S.append(f'<section class="slide item chart-slide th-dark" id="slide-{i:02d}">{chips(i)}{body}</section>')
            continue
        if it.get('stat'):
            a, b = it['stat']
            body = (f'<div class="wrap"><h2 class="headline">{it["h"]}</h2><p class="support">{e(it["p"])}</p></div>'
                    f'<div class="duo"><div class="a"><div class="n">{e(a[0])}</div><div class="l">{e(a[1])}</div></div>'
                    f'<div class="bb"><div class="n">{e(b[0])}</div><div class="l">{e(b[1])}</div></div>'
                    f'<div class="note">{e(a[2])}</div></div>')
            S.append(f'<section class="slide item th-salmon" id="slide-{i:02d}">{chips(i)}{body}</section>')
            continue
        # телефон: чат или мини-макет
        if it.get('reply'):
            ctx = f'<div class="b ctx">{e(it["ctx"])}</div>' if it.get('ctx') else ''
            screen = f'<div class="thread">{ctx}<div class="b me">{e(it["quote"])}</div><div class="b ai">{e(it["reply"])}</div></div>'
            say = ''
        elif it.get('demo'):
            demo = re.sub(r'\{\{icon:([\w-]+)\}\}', lambda m: icon(m.group(1)), it['demo'])
            screen = f'<div class="demo">{demo}</div>'
            say = f'<div class="say"><span class="label">{e(it["lbl"])}</span><p>{e(it.get("quote") or it.get("cap", ""))}</p></div>'
        else:
            screen = f'<div class="thread"><div class="b me">{e(it["quote"])}</div></div>'
            say = f'<div class="say"><span class="label">{e(it["lbl"])}</span><p>{e(it["quote"])}</p></div>'
        phone = (f'<div class="phone"><div class="screen"><div class="sbar"><span>9:30</span><span><i></i><i></i></span></div>'
                 f'<div class="appbar"><span class="av"></span>{e(it.get("app", "Чат"))}</div>{screen}</div></div>')
        S.append(f'<section class="slide item {th}" id="slide-{i:02d}">{chips(i)}{head}{phone}{say}</section>')

    f = spec['final']
    lis = ''.join(f'<div class="li"><span class="ic">{icon("check_circle")}</span>{e(x)}</div>' for x in f['list'])
    S.append(f'''<section class="slide final th-deep" id="slide-{N:02d}">{chips(N)}
  <div class="wrap"><h2 class="headline">{f["title_html"]}</h2></div>
  <div class="list">{lis}</div>
  <div class="fab">{icon("download")}<span><small>{e(f["save_lbl"])}</small>{e(f["save"])}</span></div>
  <div class="foot">{e(spec["handle"])}</div>
</section>''')
    return S
