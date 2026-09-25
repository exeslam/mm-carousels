"""Шаблон mm-reels: карусель в языке наших рилсов (MM/reels/_kit, DESIGN.md).

Обложка: капс-хук с синей плашкой на слове + герой: мемоджи / 3D-стикер / фото (cover.visual).
Пункты (items[].kind):
  card   запрет/правило: иконка, пилюля, почему, что делать, пример «так пишут / так лучше»
  step   шаг: номер, заголовок, пояснение, 3D-стикер
  chat   переписка: ctx (серый справа), me (синий), ai (серый слева)
  ba     было / стало: два текста
  quiz   правда или миф: утверждение, штамп вердикта, пояснение
  msg    сообщение с пометками: {фраза} подсвечивается, ярлыки ниже
  list   группа пунктов с иконками
  shot   скрин сайта в окне браузера
  meme   свои мем-форматы: expect (ожидание/реальность на мемоджи), vs (я / нейросеть), photo (фото + подпись)
Финал: чек-лист, карточка Telegram-канала, кодовое слово.
Любому пункту можно дать sticker: "fluent/fire" (id из общей библиотеки lib/manifest.json).
Слова в [скобках] получают синюю плашку, как в субтитрах рилсов."""
import json, math, os, re, shutil

CHANNEL = {'name': 'ИИшница', 'handle': '@iishnitsa_nazavtrak'}
VERDICT = {'правда': 'green', 'миф': 'red', 'ну почти': 'orange'}


def render(spec, c):
    e, svg, N, out, ROOT = c['e'], c['svg'], c['N'], c['out'], c['ROOT']
    used = c.setdefault('used_assets', [])
    LIB = os.path.join(ROOT, 'lib')
    man = {a['id']: a for a in json.load(open(os.path.join(LIB, 'manifest.json')))['assets']}

    def lib(aid):
        """id из lib/manifest.json (memoji/think, fluent/fire, photo/…, render/…, screen/…) → путь в выпуске."""
        if aid.startswith('screen/'):
            a = {'id': aid, 'file': f'screens/{aid[7:]}.jpg', 'license': 'скрин сайта, номинативно'}
        else:
            a = man[aid]
        dst = 'assets/lib/' + a['file'].replace('/', '-')
        os.makedirs(f'{out}/assets/lib', exist_ok=True)
        shutil.copy(os.path.join(LIB, a['file']), f'{out}/{dst}')
        if not any(u.get('id') == aid for u in used if isinstance(u, dict)):
            used.append({k: a[k] for k in ('id', 'file', 'license', 'source', 'author') if k in a})
        return './' + dst

    def mj(name):
        return lib('memoji/' + name)

    def subs(text, cls='subs'):
        words = []
        for part in re.split(r'(\[[^\]]+\])', text):
            if part.startswith('['):
                words.append(f'<span class="hl">{e(part[1:-1])}</span>')
                continue
            for w in part.split():
                if words and re.fullmatch(r'[.,!?:;]+', w):
                    words[-1] = f'<span class="nw">{words[-1]}<span class="pn">{e(w)}</span></span>'
                else:
                    words.append(f'<span>{e(w)}</span>')
        return f'<div class="{cls}">{"".join(words)}</div>'

    def pills(i):
        return f'<div class="pills"><span class="pill lgk"><i></i>{e(spec["handle"])}</span><span class="pill lgk">{i:02d} / {N:02d}</span></div>'

    host = spec.get('host', {})
    plate = (f'<div class="plate lgk"><div class="ava"><img src="{mj(host.get("avatar", "laptop"))}" alt=""></div>'
             f'<div class="pt"><b>{e(host.get("title", spec["title"]))}</b><span>{e(host.get("sub", ""))}</span></div></div>')

    S = []
    # ── обложка ──
    cv = spec['cover']
    vis = cv.get('visual', {'kind': 'memoji', 'id': cv.get('memoji', 'think')})
    hero = ''
    if cv.get('ring'):
        orbit = ''
        for k, name in enumerate(cv['ring']):
            a = -math.pi / 2 + 2 * math.pi * k / len(cv['ring'])
            x, y = 355 + 230 * math.cos(a) - 52, 905 + 230 * math.sin(a) - 52
            orbit += f'<span class="sym{" red" if k % 3 == 1 else ""}" style="left:{x:.0f}px;top:{y:.0f}px">{svg(name)}</span>'
        hero += (f'<div class="orbit">{orbit}</div><div class="med"><div class="disc lgk" style="border-radius:50%"></div>'
                 f'<div class="ring"></div>{svg(cv.get("medal", "lock"))}</div>')
    if vis['kind'] == 'memoji':
        hero += f'<img class="mj" src="{mj(vis["id"])}" alt="">'
    elif vis['kind'] == 'sticker':
        hero += f'<img class="hero-st" src="{lib(vis["id"])}" alt="">'
        if vis.get('memoji'):
            hero += f'<img class="mj small" src="{mj(vis["memoji"])}" alt="">'
    elif vis['kind'] == 'photo':
        hero += (f'<div class="hero-ph"><img src="{lib(vis["id"])}" alt="" style="object-position:{vis.get("pos", "50% 50%")}"></div>')
        if vis.get('memoji'):
            hero += f'<img class="mj small" src="{mj(vis["memoji"])}" alt="">'
    S.append(f'''<section class="slide cover cv-{vis["kind"]}" id="slide-01">{pills(1)}
  {subs(cv["hook"])}
  {hero}
  <div class="note lgk">{svg("arrow-right")}{e(cv.get("note", "листай"))}</div>
</section>''')

    # ── пункты ──
    total = len(spec['items'])
    for k, it in enumerate(spec['items']):
        i = k + 2
        kind = it.get('kind', 'card')
        same = [x for x in spec['items'] if x.get('kind', 'card') == kind]
        pos, of = same.index(it) + 1, len(same)
        react = f'<img class="react" src="{mj(it["react"])}" alt="">' if it.get('react') else ''
        sticker = f'<img class="stk" src="{lib(it["sticker"])}" alt="">' if it.get('sticker') else ''
        body = ''
        if kind == 'card':
            body = (f'<div class="card glass"><span class="ban{" ok" if it.get("ban_ok") else ""}">{svg("check" if it.get("ban_ok") else "x")}{e(it.get("ban", "нельзя"))}</span>'
                    f'<div class="hd"><span class="sym{" red" if it.get("red") else ""}">{svg(it["icon"])}</span>'
                    f'<div>{f'<div class="n">{pos} из {of}</div>' if of > 1 else ''}<h2>{e(it["title"])}</h2></div></div>'
                    f'<p class="why">{e(it["why"])}</p>'
                    + (f'<div class="do">{svg("circle-check-filled")}<span>{e(it["do"])}</span></div>' if it.get('do') else '') + '</div>')
            if it.get('bad'):
                body += (f'<div class="ex glass"><span class="exl">{e(it.get("bad_lbl", "так пишут"))}</span><div class="msg bad">{e(it["bad"])}</div>'
                         f'<span class="exl good">{e(it.get("good_lbl", "так лучше"))}</span><div class="msg good">{e(it["good"])}</div></div>')
        elif kind == 'step':
            body = (f'<div class="card glass step"><div class="hd"><span class="sym big">{it.get("n", k + 1)}</span>'
                    f'<div>{"<div class=n>шаг " + str(it.get("n", pos)) + " из " + str(of) + "</div>" if of > 1 else ""}<h2>{e(it["title"])}</h2></div></div>'
                    f'<p class="why">{e(it["why"])}</p>'
                    + (f'<div class="prompt"><span class="exl good">{e(it.get("prompt_lbl", "напиши"))}</span><p>{e(it["prompt"])}</p></div>' if it.get('prompt') else '')
                    + '</div>')
        elif kind == 'chat':
            rows = ''
            for who, text in it['msgs']:
                rows += f'<div class="msg {who}">{e(text)}</div>'
            body = (f'<div class="card glass chat"><div class="app"><span class="sym">{svg(it.get("app_icon", "message-circle"))}</span>'
                    f'<b>{e(it.get("app", "Чат с нейросетью"))}</b><span class="lbl">{e(it.get("lbl", ""))}</span></div>{rows}</div>')
        elif kind == 'ba':
            body = (f'<div class="bawrap"><div class="ba glass"><span class="exl">{e(it.get("before_lbl", "было"))}</span><p class="bef">{e(it["before"])}</p></div>'
                    f'<div class="arrowdown">{svg("arrow-down")}</div>'
                    f'<div class="ba glass good"><span class="exl good">{e(it.get("after_lbl", "стало"))}</span><p class="aft">{e(it["after"])}</p></div></div>')
        elif kind == 'quiz':
            v = it['verdict']
            body = (f'<div class="card glass quiz"><div class="n">фраза {pos} из {of}</div><h2 class="stmt">{e(it["statement"])}</h2>'
                    f'<span class="stamp {VERDICT.get(v.lower(), "orange")}">{e(v)}</span><p class="why">{e(it["why"])}</p></div>')
        elif kind == 'msg':
            n = [0]

            def mark(m):
                n[0] += 1
                return f'<mark>{e(m.group(1))}<sup>{n[0]}</sup></mark>'
            txt = re.sub(r'\{([^}]+)\}', mark, e(it['text']).replace('&#x27;', "'"))
            labels = ''.join(f'<span class="tagm"><sup>{j + 1}</sup>{e(l)}</span>' for j, l in enumerate(it.get('labels', [])))
            body = (f'<div class="card glass msgcard"><div class="app"><span class="sym">{svg("mail")}</span><b>{e(it.get("to", "Клиенту"))}</b>'
                    f'<span class="lbl">{e(it.get("lbl", "черновик"))}</span></div><p class="mtext">{txt}</p><div class="tags">{labels}</div></div>')
        elif kind == 'list':
            rows = ''.join(f'<div class="li"><span class="sym{" red" if it.get("red") else ""}">{svg(r[0])}</span><span>{e(r[1])}</span></div>' for r in it['rows'])
            body = f'<div class="card glass listcard"><div class="n">{e(it.get("group", ""))}</div><h2>{e(it["title"])}</h2>{rows}</div>'
        elif kind == 'shot':
            body = (f'<div class="browser glass"><div class="bbar"><i></i><i></i><i></i><span>{e(it["domain"])}</span></div>'
                    f'<img src="{lib(it["shot"])}" alt=""></div>'
                    + (f'<span class="badge">{e(it["badge"])}</span>' if it.get('badge') else '')
                    + f'<div class="shotcap glass"><b>{e(it["title"])}</b><span>{e(it["why"])}</span></div>')
        elif kind == 'term':
            rows = ''
            for kind_, text in it['lines']:
                if kind_ == 'cmd':
                    rows += f'<div class="tl cmd"><b>&gt;</b>{e(text)}</div>'
                elif kind_ == 'bar':
                    lbl, pct = text
                    rows += f'<div class="tl bar"><span>{e(lbl)}</span><i><u style="width:{pct}%"></u></i><em>{pct}%</em></div>'
                else:
                    rows += f'<div class="tl {kind_}">{e(text)}</div>'
            body = (f'<div class="term"><div class="tbar"><i></i><i></i><i></i><span>{e(it.get("tname", "claude"))}</span></div>{rows}</div>'
                    + (f'<div class="tnote glass"><b>{e(it["title"])}</b><span>{e(it["why"])}</span></div>' if it.get('title') else ''))
        elif kind == 'price':
            logo = f'<img class="plogo" src="{lib(it["logo"])}" alt="">' if it.get('logo') else ''
            rows = ''.join(f'<div class="pr{" hot" if r[3:] and r[3] else ""}"><div><b>{e(r[0])}</b><span>{e(r[2])}</span></div><em>{e(r[1])}</em></div>' for r in it['rows'])
            body = (f'<div class="card glass pricecard"><div class="app">{logo}<b>{e(it["title"])}</b><span class="lbl">{e(it.get("lbl", "в месяц"))}</span></div>{rows}'
                    + (f'<p class="pnote">{e(it["note"])}</p>' if it.get('note') else '') + '</div>')
        elif kind == 'tool':
            chips = ''.join(f'<span class="chip">{e(x)}</span>' for x in it.get('where', []))
            body = (f'<div class="card glass toolcard"><div class="thd"><img class="tlogo" src="{lib(it["logo"])}" alt=""><div><div class="n">{e(it.get("lbl", ""))}</div><h2>{e(it["title"])}</h2></div></div>'
                    f'<p class="why">{e(it["why"])}</p><div class="exl good">где работает</div><div class="chips">{chips}</div>'
                    f'<div class="do">{svg("coin")}<span>{e(it["pay"])}</span></div></div>')
        elif kind == 'meme':
            f_ = it['format']
            if f_ == 'expect':
                body = (f'<div class="meme2"><div class="mp glass"><span class="exl good">{e(it.get("l_lbl", "ожидание"))}</span><img src="{mj(it.get("l_mj", "wink"))}" alt=""><p>{e(it["left"])}</p></div>'
                        f'<div class="mp glass"><span class="exl">{e(it.get("r_lbl", "реальность"))}</span><img src="{mj(it.get("r_mj", "oops"))}" alt=""><p>{e(it["right"])}</p></div></div>')
            elif f_ == 'vs':
                body = (f'<div class="meme2 vs"><div class="mp glass"><span class="exl">{e(it.get("l_lbl", "я"))}</span><img src="{mj(it.get("l_mj", "laptop"))}" alt=""><p>{e(it["left"])}</p></div>'
                        f'<div class="mp glass"><span class="exl good">{e(it.get("r_lbl", "нейросеть"))}</span><img src="{lib(it.get("r_img", "fluent/robot"))}" alt=""><p>{e(it["right"])}</p></div></div>')
            else:
                body = (f'<div class="memeph glass"><div class="cap">{e(it["top"])}</div><img src="{lib(it["photo"])}" alt="" style="object-position:{it.get("pos", "50% 40%")}"></div>')
        S.append(f'''<section class="slide item k-{kind}{" has-react" if react else ""}" id="slide-{i:02d}">{pills(i)}
  {plate}{body}{sticker}{subs(it["say"])}{react}
</section>''')

    # ── финал ──
    f = spec['final']
    ch = f.get('channel', CHANNEL)
    lis = ''.join(f'<div class="li"><span class="sym{" red" if f.get("red") else ""}">{svg(x[0])}</span>{e(x[1])}</div>' for x in f['list'])
    S.append(f'''<section class="slide final n{len(f["list"])}" id="slide-{N:02d}">{pills(N)}
  <div class="list glass">{"<div class='lt'>" + e(f["title"]) + "</div>" if f.get("title") else ""}{lis}</div>
  <div class="tg glass"><div class="ava"><img src="{mj(f.get("avatar", "wink"))}" alt=""></div>
    <div><h2>{e(ch["name"])}</h2><div class="handle">{e(ch["handle"])}</div>
    <div class="sub">{svg("brand-telegram")}Подписаться</div><div class="hint">ссылка в шапке профиля</div></div></div>
  <div class="kw lgk">{svg("message-circle")}Напиши в комментариях <b>{e(f.get("keyword", "ИИШНИЦА"))}</b></div>
  {subs(f["say"])}
</section>''')
    return S
