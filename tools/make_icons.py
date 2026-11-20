"""Generate Pendo's white line icons (tinted at runtime by Kivy's Image `color`).

Run:  python3 tools/make_icons.py   ->  assets/icons/*.png  (96x96, transparent)
"""
import math
import os
from PIL import Image, ImageDraw

S = 8            # supersampling factor
N = 96           # output size
W = 7 * S        # stroke width at supersampled scale
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'icons')
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def canvas():
    im = Image.new('RGBA', (N * S, N * S), CLEAR)
    return im, ImageDraw.Draw(im)


def p(*pts):
    return [(x * S, y * S) for x, y in pts]


def line(d, pts, w=W):
    d.line(pts, fill=WHITE, width=w, joint='curve')
    r = w // 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE)


def rrect(d, box, r, outline=True, fill=False, w=W):
    x0, y0, x1, y1 = [v * S for v in box]
    if fill:
        d.rounded_rectangle([x0, y0, x1, y1], r * S, fill=WHITE)
    else:
        d.rounded_rectangle([x0, y0, x1, y1], r * S, outline=WHITE, width=w)


def circle(d, cx, cy, r, fill=False, w=W):
    box = [(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S]
    if fill:
        d.ellipse(box, fill=WHITE)
    else:
        d.ellipse(box, outline=WHITE, width=w)


def save(im, name):
    im.resize((N, N), Image.LANCZOS).save(os.path.join(OUT, name + '.png'), optimize=True)


def home():
    im, d = canvas()
    line(d, p((18, 46), (48, 20), (78, 46)))
    line(d, p((26, 40), (26, 74), (40, 74), (40, 54), (56, 54), (56, 74), (70, 74), (70, 40)))
    save(im, 'home')


def tick():
    im, d = canvas()
    line(d, p((24, 50), (42, 68), (74, 30)))
    save(im, 'tick')


def ring():
    im, d = canvas()
    circle(d, 48, 48, 30)
    save(im, 'ring')


def check_circle():
    im, d = canvas()
    circle(d, 48, 48, 34, fill=True)
    d.line(p((33, 49), (44, 60), (64, 36)), fill=CLEAR, width=W, joint='curve')
    for x, y in ((33, 49), (64, 36)):
        r = W // 2
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=CLEAR)
    save(im, 'check_circle')


def calendar():
    im, d = canvas()
    rrect(d, (16, 22, 80, 78), 10)
    line(d, p((16, 40), (80, 40)))
    line(d, p((34, 14), (34, 28)))
    line(d, p((62, 14), (62, 28)))
    circle(d, 36, 56, 4, fill=True)
    circle(d, 60, 56, 4, fill=True)
    save(im, 'calendar')


def wallet():
    im, d = canvas()
    rrect(d, (14, 26, 82, 74), 10)
    line(d, p((14, 40), (82, 40)))
    circle(d, 64, 57, 4.5, fill=True)
    save(im, 'wallet')


def grid():
    im, d = canvas()
    for x, y in ((18, 18), (54, 18), (18, 54), (54, 54)):
        rrect(d, (x, y, x + 24, y + 24), 7)
    save(im, 'grid')


def listicon():
    im, d = canvas()
    for y in (28, 48, 68):
        circle(d, 22, y, 4.5, fill=True)
        line(d, p((38, y), (76, y)))
    save(im, 'list')


def doc():
    im, d = canvas()
    line(d, p((26, 14), (56, 14), (74, 32), (74, 82), (26, 82), (26, 14)))
    line(d, p((56, 14), (56, 32), (74, 32)))
    line(d, p((38, 52), (62, 52)))
    line(d, p((38, 66), (62, 66)))
    save(im, 'doc')


def target():
    im, d = canvas()
    circle(d, 48, 48, 32)
    circle(d, 48, 48, 17)
    circle(d, 48, 48, 4.5, fill=True)
    save(im, 'target')


def user():
    im, d = canvas()
    circle(d, 48, 34, 14)
    d.arc([18 * S, 54 * S, 78 * S, 114 * S], 180, 360, fill=WHITE, width=W)
    save(im, 'user')


def plus():
    im, d = canvas()
    line(d, p((48, 22), (48, 74)))
    line(d, p((22, 48), (74, 48)))
    save(im, 'plus')


def chevron_right():
    im, d = canvas()
    line(d, p((36, 22), (62, 48), (36, 74)))
    save(im, 'chevron_right')


def chevron_left():
    im, d = canvas()
    line(d, p((60, 22), (34, 48), (60, 74)))
    save(im, 'chevron_left')


def trash():
    im, d = canvas()
    line(d, p((20, 28), (76, 28)))
    line(d, p((38, 28), (38, 18), (58, 18), (58, 28)))
    line(d, p((28, 28), (31, 78), (65, 78), (68, 28)))
    line(d, p((43, 42), (43, 66)))
    line(d, p((53, 42), (53, 66)))
    save(im, 'trash')


def pencil():
    im, d = canvas()
    line(d, p((22, 74), (28, 54), (62, 20), (76, 34), (42, 68), (22, 74)))
    line(d, p((54, 28), (68, 42)))
    save(im, 'pencil')


def star():
    im, d = canvas()
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = 34 if i % 2 == 0 else 15
        pts.append((48 + r * math.cos(ang), 50 + r * math.sin(ang)))
    pts.append(pts[0])
    line(d, p(*pts), w=6 * S)
    save(im, 'star')


def wifi():
    im, d = canvas()
    for r in (14, 28, 42):
        d.arc([(48 - r) * S, (70 - r) * S, (48 + r) * S, (70 + r) * S], 225, 315, fill=WHITE, width=W)
    circle(d, 48, 70, 4.5, fill=True)
    save(im, 'wifi')


def inbox():
    im, d = canvas()
    line(d, p((16, 56), (28, 24), (68, 24), (80, 56), (80, 72), (16, 72), (16, 56)))
    line(d, p((16, 56), (36, 56), (40, 64), (56, 64), (60, 56), (80, 56)))
    save(im, 'inbox')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for fn in (home, tick, ring, check_circle, calendar, wallet, grid, listicon, doc, target, user,
               plus, chevron_right, chevron_left, trash, pencil, star, wifi, inbox):
        fn()
    print('icons written to', os.path.abspath(OUT))
