"""
Player's bullets
    TODO: DOC
"""

# STDLIB
import math
import random
import itertools
import sys
import thread
import time
#import pygame

# GLOBALS 
from globalvals import *

# Base class
from entity import Entity

class Bullet(Entity):
    def __init__(self, x = 0, y = 0, r = CMAX, g = CMAX, b = CMAX,
                rgb=(CMAX, CMAX, CMAX),
                shotAngle=0, length=BULLET_LENGTH):

        super(Bullet, self).__init__(x, y, rgb[0], rgb[1], rgb[2])
        self.drawn = False

        self.pauseFirst = True
        self.pauseLast = True

        self.length = length
        self.shotAngle = shotAngle
        self.theta = shotAngle

        # Override blanking
        self.doBlanking = BULLET_DO_BLANKING

    def produce(self):
        """
        Generate the points of the circle.
        """
        r, g, b = (0, 0, 0)

        pts = []
        pts.append({'x': 0, 'y': 0})
        pts.append({'x': self.length*math.cos(self.shotAngle),
                    'y': self.length*math.sin(self.shotAngle)})

        """
        # Rotate points
        for p in pts:
            x = p['x']
            y = p['y']
            p['x'] = x*math.cos(self.theta) - y*math.sin(self.theta)
            p['y'] = y*math.cos(self.theta) + x*math.sin(self.theta)
        """

        # Translate points
        for pt in pts:
            pt['x'] += self.x
            pt['y'] += self.y

        r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
        g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
        b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)

        def make_line(pt1, pt2, steps=200):
            xdiff = pt1['x'] - pt2['x']
            ydiff = pt1['y'] - pt2['y']
            line = []
            for i in xrange(0, steps, 1):
                j = float(i)/steps
                x = pt1['x'] - (xdiff * j)
                y = pt1['y'] - (ydiff * j)
                line.append((x, y, r, g, b)) # XXX FIX COLORS
            return line

        for p in make_line(pts[0], pts[1], BULLET_EDGE_SAMPLE_PTS):
            self.lastPt = p # XXX super important
            yield p

        self.drawn = True


