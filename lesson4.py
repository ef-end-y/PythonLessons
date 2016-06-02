# -*- coding: utf-8 -*-
from PIL import Image
import re

scr_x = 800  # Ширина картинки
scr_y = scr_x  # Высота картинки


class Screen(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.img = Image.new('RGB', (width, height), 'black')
        self.canvas = self.img.load()
        self.z_buffer = [[0] * width for i in range(height)]

    def point(self, *coords):
        return Point(self, *coords)

    @staticmethod
    def triangle(coords):
        a, b, c = sorted(coords, key=lambda p: p.y)
        p1 = a.copy()
        p2 = a.copy()
        height_ac = c.y - a.y
        height_ab = (b.y - a.y) or 1
        height_bc = (c.y - b.y) or 1
        delta_x1 = float(b.x - a.x) / height_ab
        delta_x2 = float(c.x - a.x) / height_ac
        delta_z1 = float(b.z - a.z) / height_ab
        delta_z2 = float(c.z - a.z) / height_ac
        for y in (b.y, c.y):
            while p1.y < y:
                if p1.x > p2.x:
                    p3 = p2.copy()
                    p4 = p1
                else:
                    p3 = p1.copy()
                    p4 = p2
                delta_z3 = float(p4.z - p3.z) / ((p4.x - p3.x) or 1)
                while p3.x < p4.x:
                    p3.show(tuple([int(p3.z * 128)] * 3))
                    p3.x += 1
                    p3.z += delta_z3
                p1.y += 1
                p2.y += 1
                p1.x += delta_x1
                p1.z += delta_z1
                p2.x += delta_x2
                p2.z += delta_z2
            delta_x1 = float(c.x - b.x) / height_bc
            delta_z1 = float(c.z - b.z) / height_bc
            p1 = b.copy()


class Point(object):
    def __init__(self, screen, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.screen = screen

    def show(self, color=None):
        screen = self.screen
        x = int(self.x)
        y = int(self.y)
        if self.z <= screen.z_buffer[x][y]:
            return
        screen.z_buffer[x][y] = self.z
        screen.canvas[x, screen.height-y] = color or (255, 255, 255)

    def copy(self):
        return Point(self.screen, self.x, self.y, self.z)


def show_face():
    half_scr_x = int(scr_x/2)
    half_scr_y = int(scr_y/2)
    f = open('face.obj', 'r')
    lines = f.read()
    points = []
    screen = Screen(scr_x, scr_y)
    for line in lines.split('\n'):
        try:
            v, x, y, z = re.split('\s+', line)
        except ValueError:
            continue
        if v == 'v':
            x = int((float(x) + 1) * half_scr_x)
            y = int((float(y) + 1) * half_scr_y)
            z = float(z) + 1
            points.append(screen.point(x, y, z))
        if v == 'f':
            screen.triangle([points[int(i.split('/')[0])-1] for i in (x, y, z)])
    screen.img.show()

show_face()
