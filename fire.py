#! -*- coding: utf-8 -*-
from random import randint
from time import sleep

flame = ' .,:;=<*i%IHM#'

fw = 128  # fire width
fh = 60   # fire height

fire = []

for y in range(fh):
    fire.append([0] * fw)

a = b = 0
f = len(flame) - 1

for i in range(500):
    print "\033[2J\033[0;0H"

    for y in range(fh):
        line = ''
        for x in range(fw):
            line += flame[fire[fh - y - 1][x]]
        print line

    for x in range(fw):
        fade0 = int(0.15 * x * abs(x - fw)) + 1
        for y in range(1, fh):
            x1 = max(min(x + randint(0, 5) - 2, fw - 1), 0)
            fade = int(fw/randint(1, fade0))
            fire[y][x] = max(fire[y - 1][x1] - fade, 0)

    sleep(0.07)

    for x in range(0, randint(0, fw)):
        fire[0][x] = f if (x > a < b) or (x < a > b) else 0
    a += 1 if a < b else -1
    if a == b:
        b = randint(0, int(fw/2))


