# -*- coding: utf-8 -*-
import copy
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
        return TexturePoint(self, *coords)

    @staticmethod
    def triangle(coords, texture):
        a, b, c = sorted(coords, key=lambda p: p.y)
        p1, p2 = a.copy(), a.copy()
        height = c.y - a.y
        delta_x2 = float(c.x - a.x) / height
        deltas = lambda i, j, divider: [float(i.z-j.z)/divider, float(i.u-j.u)/divider, float(i.v-j.v)/divider]
        delta_z2, delta_u2, delta_v2 = deltas(c, a, height)
        for p in (b, c):
            height = (p.y - p1.y) or 1
            delta_x1 = float(p.x - p1.x) / height
            delta_z1, delta_u1, delta_v1 = deltas(p, p1, height)
            while p1.y < p.y:
                p3, p4 = (p2.copy(), p1) if p1.x > p2.x else (p1.copy(), p2)
                delta_z3, delta_u3, delta_v3 = deltas(p4, p3, (p4.x - p3.x) or 1)
                while p3.x < p4.x:
                    p3.show(texture[p3.u, p3.v])
                    p3.add(x=1, z=delta_z3, u=delta_u3, v=delta_v3)
                p1.add(x=delta_x1, y=1, z=delta_z1, u=delta_u1, v=delta_v1)
                p2.add(x=delta_x2, y=1, z=delta_z2, u=delta_u2, v=delta_v2)
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
        if self.z <= screen.z_buffer[y][x]:
            return
        screen.z_buffer[y][x] = self.z
        screen.canvas[x, screen.height-y] = color or (255, 255, 255)

    def copy(self):
        return copy.copy(self)


class TexturePoint(Point):
    def __init__(self, screen, x, y, z, u, v):
        super(TexturePoint, self).__init__(screen, x, y, z)
        self.u = u
        self.v = v

    def add(self, x=0, y=0, z=0, u=0, v=0):
        self.x += x
        self.y += y
        self.z += z
        self.u += u
        self.v += v


def show_face():
    half_scr_x = int(scr_x/2)
    half_scr_y = int(scr_y/2)
    texture_img = Image.open('african_head_diffuse.tga')
    texture = texture_img.load()
    f = open('face.obj', 'r')
    lines = f.read()
    points = []
    textures = []
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
            points.append((x, y, z))
        if v == 'vt':
            u = float(x) * texture_img.width
            v = (1 - float(y)) * texture_img.height
            textures.append((u, v))
        if v == 'f':
            indexes = [[int(j)-1 for j in i.split('/')] for i in (x, y, z)]
            tr_points = []
            for i in range(3):
                params = points[indexes[i][0]] + textures[indexes[i][1]]
                tr_points.append(screen.point(*params))
            screen.triangle(tr_points, texture)
    screen.img.show()

show_face()
