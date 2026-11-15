#!/usr/bin/env python3
"""Генерирует заготовки фонов в блочном стиле (backgrounds/*.jpg + backgrounds.json).
Это запасные картинки: замените их своими скриншотами / артами с теми же именами или добавьте новые файлы
и впишите их имена в backgrounds/backgrounds.json. Запуск:  python3 tools/make_backgrounds.py   (нужен Pillow)"""
import json, os, random
from PIL import Image, ImageDraw

W, H, U = 1280, 720, 16            # размер картинки и «размер блока» в пикселях
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backgrounds')
os.makedirs(OUT, exist_ok=True)


def lerp(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(stops):
    """stops: [(позиция 0..1, '#rrggbb'), ...] - вертикальный градиент"""
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]; p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                d.line([(0, y), (W, y)], fill=lerp(hexc(c0), hexc(c1), (t - p0) / (p1 - p0 or 1)))
                break
    return img


def block(d, x, y, w, h, color): d.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def clouds(img, rnd, color, count, ymin, ymax, alpha=235):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = color + (alpha,)
    for _ in range(count):
        cx, cy = rnd.randrange(-4, W // U) * U, rnd.randrange(ymin // U, ymax // U) * U
        for row in range(rnd.randint(1, 2)):
            n = rnd.randint(4, 9)
            ox = rnd.randint(0, 2) * U
            block(d, cx + ox, cy + row * U * 2, n * U, U * 2, c)
        if rnd.random() < 0.6:
            block(d, cx + U * 2, cy - U * 2, rnd.randint(2, 4) * U, U * 2, c)
    img.paste(layer, (0, 0), layer)


def hills(img, rnd, base_y, amp, color, step=2, top=None, rough=1):
    """ступенчатый силуэт холмов; top - цвет верхнего ряда блоков (трава / снег)"""
    d = ImageDraw.Draw(img)
    cols = W // (U * step) + 2
    h = rnd.randint(2, 4)
    for i in range(cols):
        h = max(0, min(amp, h + rnd.choice([-1, 0, 0, 1][:2 + rough * 2])))
        x, y = i * U * step, base_y - h * U
        block(d, x, y, U * step, H - y, color)
        if top: block(d, x, y, U * step, U, top)


def stars(img, rnd, count, ymax, bright=(255, 255, 255)):
    d = ImageDraw.Draw(img)
    for _ in range(count):
        x, y = rnd.randrange(0, W // 4) * 4, rnd.randrange(0, ymax // 4) * 4
        s = rnd.choice([4, 4, 4, 8])
        v = rnd.uniform(0.35, 1)
        block(d, x, y, s, s, tuple(int(c * v) for c in bright))


def square_sun(img, cx, cy, size, core, halo, rings=3):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(rings, 0, -1):
        r = size // 2 + i * U * 2
        block(d, cx - r, cy - r, r * 2, r * 2, halo + (28,))
    block(d, cx - size // 2, cy - size // 2, size, size, core + (255,))
    img.paste(layer, (0, 0), layer)


def save(img, name):
    img.convert('RGB').save(os.path.join(OUT, name + '.jpg'), quality=88, optimize=True)


def day():
    r = random.Random(11)
    img = gradient([(0, '#4f8df5'), (0.55, '#8fc0ff'), (1, '#cfe6ff')])
    square_sun(img, 1020, 150, 96, hexc('#fff6b0'), hexc('#fff1a0'))
    clouds(img, r, (255, 255, 255), 9, 40, 300)
    hills(img, r, 560, 9, hexc('#5f9a4f'), 3, hexc('#7cc062'))
    hills(img, r, 660, 7, hexc('#46823a'), 2, hexc('#62a84a'))
    save(img, 'day')


def sunset():
    r = random.Random(22)
    img = gradient([(0, '#241552'), (0.35, '#7a2f7e'), (0.62, '#e0617a'), (0.82, '#ff9a5a'), (1, '#ffd08a')])
    square_sun(img, 640, 520, 128, hexc('#ffe9a8'), hexc('#ffb36b'), 4)
    clouds(img, r, (255, 170, 150), 8, 90, 380, 170)
    hills(img, r, 600, 9, hexc('#4a2250'), 3)
    hills(img, r, 680, 6, hexc('#2a1238'), 2)
    save(img, 'sunset')


def night():
    r = random.Random(33)
    img = gradient([(0, '#04061a'), (0.6, '#101a42'), (1, '#1d2b5e')])
    stars(img, r, 260, 520)
    d = ImageDraw.Draw(img)
    block(d, 960, 90, 112, 112, hexc('#e9edff'))
    for (dx, dy, s) in [(16, 16, 32), (64, 48, 32), (32, 64, 16), (72, 16, 16)]:
        block(d, 960 + dx, 90 + dy, s, s, hexc('#c4cbe8'))
    clouds(img, r, (60, 75, 130), 6, 120, 360, 120)
    hills(img, r, 580, 9, hexc('#0c1430'), 3)
    hills(img, r, 670, 7, hexc('#070b1d'), 2)
    save(img, 'night')


def tree(d, x, y, h, trunk, leaf, snow):
    """ель: ствол + h ярусов, нижний ярус самый широкий"""
    block(d, x, y - U, U, U, trunk)
    for i in range(h):
        w = (h - i) * 2 + 1
        ty = y - U - (i + 1) * U * 2
        left = x - (w // 2) * U
        block(d, left, ty, w * U, U * 2, leaf)
        block(d, left, ty, w * U, U // 2, snow)


def snow():
    r = random.Random(44)
    img = gradient([(0, '#a9cdf2'), (0.6, '#d9ebfb'), (1, '#f4faff')])
    clouds(img, r, (255, 255, 255), 8, 40, 260, 215)
    hills(img, r, 540, 8, hexc('#e4eef9'), 3, hexc('#ffffff'))
    hills(img, r, 650, 6, hexc('#cfe0f0'), 2, hexc('#f8fcff'))
    d = ImageDraw.Draw(img)
    for _ in range(9):
        tree(d, r.randrange(2, W // U - 2) * U, 640 + r.randrange(0, 4) * U, r.randint(2, 4), hexc('#5a3d27'), hexc('#2f5f4a'), hexc('#f5fbff'))
    for _ in range(140):
        block(d, r.randrange(0, W // 4) * 4, r.randrange(0, H // 4) * 4, 4, 4, (255, 255, 255))
    save(img, 'snow')


def nether():
    r = random.Random(55)
    img = gradient([(0, '#1a0303'), (0.55, '#5c1008'), (0.85, '#b8380f'), (1, '#ff7a1a')])
    d = ImageDraw.Draw(img)
    # потолок со сталактитами
    x = 0
    while x < W:
        block(d, x, 0, U * 2, U * r.randint(2, 7), hexc('#3a0a0a'))
        block(d, x, 0, U * 2, U, hexc('#2a0606'))
        x += U * 2
    hills(img, r, 560, 8, hexc('#4a1212'), 3, hexc('#6a1c1a'))
    hills(img, r, 640, 6, hexc('#2e0a0a'), 2, hexc('#451212'))
    # лава
    block(d, 0, 664, W, H - 664, hexc('#ff7d1c'))
    for _ in range(60):
        block(d, r.randrange(0, W // U) * U, 664 + r.randrange(0, 3) * U, U * r.randint(1, 3), U, hexc('#ffb347'))
    for _ in range(90):
        block(d, r.randrange(0, W // 4) * 4, r.randrange(120, 640 // 4) * 4, 4, 4, hexc('#ff9a3a'))
    save(img, 'nether')


def end():
    r = random.Random(66)
    img = gradient([(0, '#060312'), (0.6, '#150b2e'), (1, '#2a1650')])
    stars(img, r, 220, H, (230, 215, 255))
    d = ImageDraw.Draw(img)
    # башни из обсидиана
    for px, ph in [(140, 11), (330, 8), (900, 12), (1090, 9)]:
        block(d, px, 640 - ph * U * 2, U * 2, ph * U * 2, hexc('#120c1c'))
        block(d, px - U // 2, 640 - ph * U * 2 - U, U * 3, U, hexc('#b04ad8'))
    # остров из эндерняка: плоская верхушка, неровное «брюхо»
    block(d, 160, 640, 960, U, hexc('#dcdca0'))
    cx0, y = 160, 640 + U
    layers = [(960, '#cfcf92'), (864, '#b9b97c'), (736, '#a0a068'), (576, '#86864f'), (400, '#6e6e3d'), (224, '#58582f')]
    for w, col in layers:
        block(d, 640 - w // 2, y, w, U * 2, hexc(col))
        y += U * 2
    img2 = img
    save(img2, 'end')


if __name__ == '__main__':
    for fn in (day, sunset, night, snow, nether, end):
        fn()
    json.dump(['day.jpg', 'sunset.jpg', 'night.jpg', 'snow.jpg', 'nether.jpg', 'end.jpg'],
              open(os.path.join(OUT, 'backgrounds.json'), 'w'), indent=2)
    print('ok ->', os.path.abspath(OUT))
