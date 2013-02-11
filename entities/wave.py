"""
Asteroid class
    TODO: DOC
"""

# STDLIB
import math
import random
import itertools
import sys
import thread
import time
import heapq
#import pygame

# GLOBALS 
from globalvals import *

# Base class
from entity import Entity

class Wave(Entity):

    anchored = True

    def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0, radius = 8200):
        super(Wave, self).__init__(x, y, r, g, b)
        self.drawn = False

        self.pauseFirst = True
        self.pauseLast = True

        self.theta = 0
        self.thetaRate = 0

        self.radius = radius
        self.collisionRadius = radius

        self.step = 150

        self.x_wave_scale = 400
        self.y_wave_scale = 2500

        self.key_points = []

    def produce(self):
        """
        Generate the points of the wave
        """
        r, g, b = (0, 0, 0)

        r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
        g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
        b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)


        if self.anchored:
            key_points = [(-32600, 0)] + self.key_points + [(32600, 0)]
        else:
            key_points = self.key_points

        key_points.sort(lambda a,b: cmp(a[0],b[0]))


        def make_line(pt1, pt2, steps=200):
            xdiff = pt1[0] - pt2[0]
            ydiff = pt1[1] - pt2[1]
            line = []
            for i in xrange(0, steps, 1):
                j = float(i)/steps
                x = pt1[0] - (xdiff * j)
                y = pt1[1] - (ydiff * j)
                line.append((x, y, r, g, b)) 
            return line

        def make_curvy_line(pt1, pt2, steps=200):
            xdiff = pt1[0] - pt2[0]
            ydiff = pt1[1] - pt2[1]
            line = []
            for i in xrange(0, steps, 1):
                j = float(i)/steps
                x_add = xdiff * j
                x = pt1[0] - (x_add)
                y_extra = math.sin(x/self.x_wave_scale) * self.y_wave_scale
                y_add = ydiff * j
                y = pt1[1] - (y_add + y_extra)
                line.append((x, y, r, g, b)) 
            return line            


        i = 0
        while i + 1 < len(key_points):
            p1 = key_points[i]
            p2 = key_points[i+1]

            #print "%s - %s" % (p1, p2)
            i += 1

            for p in make_curvy_line(p1, p2, self.step): # 50 is cool
                yield p


        """

        # Generate points
        ed = self.radius

        pts = []
        pts.append({0: ed, 1: ed})
        pts.append({0: -ed, 1: ed})
        pts.append({0: -ed, 1: -ed})
        pts.append({0: ed, 1: -ed})

        # Rotate points
        for p in pts:
            x = p[0]
            y = p[1]
            p[0] = x*math.cos(self.theta) - y*math.sin(self.theta)
            p[1] = y*math.cos(self.theta) + x*math.sin(self.theta)

        # Translate points
        for pt in pts:
            pt[0] += self.x
            pt[1] += self.y




        # DRAW THE SHAPE

        p = None # Save in scope

        for p in make_line(pts[0], pts[1], SQUARE_EDGE_SAMPLE_PTS):
            break
        for i in range(int(round(SQUARE_VERTEX_SAMPLE_PTS/2.0))):
            yield p
        for p in make_line(pts[0], pts[1], SQUARE_EDGE_SAMPLE_PTS):
            yield p
        for i in range(SQUARE_VERTEX_SAMPLE_PTS):
            yield p
        for p in make_line(pts[1], pts[2], SQUARE_EDGE_SAMPLE_PTS):
            yield p
        for i in range(SQUARE_VERTEX_SAMPLE_PTS):
            yield p
        for p in make_line(pts[2], pts[3], SQUARE_EDGE_SAMPLE_PTS):
            yield p
        for i in range(SQUARE_VERTEX_SAMPLE_PTS):
            yield p
        for p in make_line(pts[3], pts[0], SQUARE_EDGE_SAMPLE_PTS):
            self.lastPt = p # KEEP BOTH
            yield p
        for i in range(int(round(SQUARE_VERTEX_SAMPLE_PTS/2.0))):
            self.lastPt = p # KEEP BOTH
            yield p

        self.drawn = True

        """

