# -*- coding: utf-8 -*-
import random
from PIL import Image
import re

scr_x = 800  # Ширина картинки
scr_y = scr_x  # Высота картинки
img = Image.new('RGB', (scr_x, scr_y), 'black')  # Создадим картинку с черным цветом фона
canvas = img.load()  # Через эту переменную у нас есть доступ к пикселям картинки


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def show(self, color=None):
        canvas[self.x, scr_y-self.y] = color or (255, 255, 255)

    def copy(self):
        return Point(self.x, self.y)


def zero_div(a, b):
    return float(a)/b if b else 0


def triangle(coords, color):
    a, b, c = sorted(coords, key=lambda p: p.y)
    p1 = a.copy()
    p2 = a.copy()
    delta_p1 = zero_div((b.x - a.x), (b.y - a.y))
    delta_p2 = zero_div((c.x - a.x), (c.y - a.y))
    for y in (b.y, c.y):
        while p1.y < y:
            if p1.x > p2.x:
                p3 = p2.copy()
                x = p1.x
            else:
                p3 = p1.copy()
                x = p2.x
            while p3.x < x:
                p3.show(color)
                p3.x += 1
            p1.y += 1
            p2.y += 1
            p1.x += delta_p1
            p2.x += delta_p2
        delta_p1 = zero_div((c.x - b.x), (c.y - b.y))

half_scr_x = int(scr_x / 2)
half_scr_y = int(scr_y / 2)
f = open('face.obj', 'r')
lines = f.read()
points = []
for line in lines.split('\n'):
    try:
        v, x, y, z = re.split('\s+', line)
    except:
        continue
    if v == 'v':
        x = int((float(x) + 1) * half_scr_x)
        y = int((float(y) + 1) * half_scr_y)
        points.append(Point(x, y))
    if v == 'f':
        color = tuple([random.randint(0, 255)] * 3)
        triangle([points[int(i.split('/')[0])-1] for i in (x, y, z)], color)

img.show()

