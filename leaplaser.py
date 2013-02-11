# Based on code from: https://github.com/j4cbo/j4cDAC/blob/master/tools/tester/talk.py
import dac
from itertools import combinations

from leapyosc import client
from leapyosc.client import (BaseLeapListener, RealPartTrackerMixin, 
                    BundledMixin, LinearScalingMixin, OSCLeapListener)

import Leap

from pointstream import PointStream
from entities.ship import Ship
from entities.particle import Particle
from entities.asteroid import Asteroid
from entities.wave import Wave


CMAX = 65535
PMAX = 32600
H_PMAX = 19348
H_PMIN = -19348
PSTEP = 200



def log(msg):
    print msg

class Shape(object):
    def __init__(self,x,y,**kwargs):
        self.pstep = int(kwargs.pop('pstep',200))
        self.x = x
        self.y = y
        self.rgb = kwargs.pop('rgb',(CMAX,0,CMAX))



class Rect(Shape):
    def __init__(self, x,y, width,height, **kwargs):
        self.width = width
        self.height = height
        super(Rect,self).__init__(x,y,**kwargs)


    def count(self, pstep=1):
        """
        Return the total number of points needed to render shape
        """
        return (self.width*2+self.height*2)/pstep


    def points(self, pstep=None):
        if not pstep:
            pstep = self.pstep


        if self.width % 2 == 0:
            left_w = self.width/2
            right_w = left_w
            #x = self.x - left_w
        else:
            left_w = (self.width-1)/2
            right_w = self.width/2
            #x = self.x - left_w
        if self.height % 2 == 0:
            top_h = self.height/2
            bottom_h = top_h
            #y = self.y - top_h
        else:
            top_h = (self.height-1)/2
            bottom_h = self.height/2
            #y = self.y - top_h

        # Draw top
        for x in xrange(self.x - left_w, self.x + right_w, pstep):
            yield (x, self.y + top_h) + self.rgb
        # Draw right
        for y in xrange(self.y - top_h, self.y + bottom_h, pstep):
            yield (self.x + right_w, y) + self.rgb
        # # Draw bottom
        for x in xrange(self.x + right_w, self.x - left_w, -pstep):
            yield (x, self.y - bottom_h) + self.rgb
        # # Draw left
        for y in xrange(self.y + bottom_h, self.y - top_h, -pstep):
            yield (self.x - left_w, y) + self.rgb





class ScenePointStream(object):
    def __init__(self, max_points=1800):
        self.shapes = []
        self.max_points = max_points
        self.point_iter = iter(self)


    def add_shape(self, shape):
        self.shapes.append(shape)

    def read(self, n):
        if len(self.shapes) > 0:
            return self._read_shapes(n)
        else:
            return [(0, 0, 0, 0, 0)] * n


    def __iter__(self):
        while True:
            # First determine # points needed to determin full resolution
            # Then use that / max points to determine resolution of shapes
            needed_points = sum([x.count() for x in self.shapes])
            pstep = (needed_points / self.max_points) or 1 # Pstep must be at least 1
            for shape in self.shapes:
                for point in shape.points(pstep):
                    yield point

    def _read_shapes(self, n):
        return [self.point_iter.next() for i in xrange(n)]




class ColorfulSquarePointStream(object):
    pmax = 32600
    pstep = 200
    cmax = 65535

    hmax = 32600
    wmax = 32600

    def produce(self):
        pmax = self.pmax
        pstep = self.pstep
        cmax = self.cmax
        wmax = self.wmax
        hmax = self.hmax
        while True:
            for x in xrange(-wmax, wmax, pstep):
                yield (x, hmax, cmax, 0, 0)
            for y in xrange(hmax, -hmax, -pstep):
                yield (wmax, y, 0, cmax, 0)
            for x in xrange(wmax, -wmax, -pstep):
                yield (x, -hmax, 0, 0, cmax)
            for y in xrange(-hmax, hmax, pstep):
                yield (-wmax, y, cmax, cmax, cmax)

    def __init__(self):
        self.stream = self.produce()

    def read(self, n):
        return [self.stream.next() for i in xrange(n)]





class NullPointStream(object):
    def read(self, n):
        return [(0, 0, 0, 0, 0)] * n



class PointExtractionMixin(object):

    def __init__(self,*args,**kwargs):
        self.x_scale = 300
        self.y_scale = 200
        super(PointExtractionMixin,self).__init__(*args,**kwargs)
        self.points = {}
        self.starter_points = {}
        self.last_seen = {}
        self.first_seen = {}
        self.frame_count = 0

        self.pt_timein = 12   # In frames
        self.pt_timeout = 5   # In frames


    def pre_extract_points(self, frame):
        pass

    def post_extract_points(self, frame):
        pass


    def new_point(self, key, point):
        pass

    def lost_point(self, key):
        pass

    def on_frame(self, controller):
        self.frame_count += 1
        super(PointExtractionMixin,self).on_frame(controller)
        frame = controller.frame()
        self.pre_extract_points(frame)
        self.extract_points(frame)
        self.post_extract_points(frame)

    def extract_points(self, frame):
        for hand in self.get_hands(frame):
            for finger in hand.fingers:
                t = finger.tip_position
                if finger.zeroed:
                    continue
                key = "%s:%s" % (hand.id, finger.id)
                #new_keys.add(key)
                if not self.first_seen.get(key):
                    self.first_seen[key] = self.frame_count
                self.starter_points[key] = self.scale_pt(t[0], t[1])
                self.last_seen[key] = self.frame_count

        # Select valid new points
        for key,frame in self.first_seen.iteritems():
            if self.frame_count - frame > self.pt_timein:
                pt = self.starter_points[key]
                if not self.points.get(key):
                    self.new_point(key, pt)
                self.points[key] = pt

        # Get rid of old points
        old_keys = []
        for key,frame in self.last_seen.iteritems():
            if self.frame_count - frame > self.pt_timeout:
                old_keys.append(key)
                
        def del_key(dct,key):
            try:
                del dct[key]
            except KeyError:
                pass

        for key in old_keys:
            del_key(self.first_seen, key)
            del_key(self.starter_points, key)
            if self.points.get(key):
                del_key(self.points, key)
                self.lost_point(key)
            del_key(self.last_seen, key)


    def build_point(self, x, y, r=CMAX, g=CMAX, b=CMAX):
        return self.scale_pt(x,y) + (r,g,b)

    def scale_pt(self, x, y):
        x = -x * self.x_scale # Scale but dont exceed max
        x = x - (x % 10)
        x = min(x, PMAX)


        y -= 200  # Because we dont have negatives in y from leap
        y = y * self.y_scale  # Scale but dont exceed max
        y = y - (y % 10)

        laser_point = self.safe_pt(x, y)
        #laser_point += (r,g,b)
        return laser_point


    def safe_pt(self, x, y):
        if x < 0:
            x = max(x, -PMAX)
        else:
            x = min(x, PMAX)

        if y < 0:
            y = max(y, H_PMIN)
        else:
            y = min(y, H_PMAX)
        return x,y


class LightningHands(PointExtractionMixin):


    def make_line(self, pt1, pt2, steps=200, rgb_start=None, rgb_end=None):

        if rgb_start is None:
            rgb_start = (CMAX, CMAX, CMAX)
        if rgb_end is None:
            rgb_end = (CMAX, CMAX, CMAX)

        xdiff = pt1[0] - pt2[0]
        ydiff = pt1[1] - pt2[1]
        rdiff = rgb_start[0] - rgb_end[0]
        gdiff = rgb_start[1] - rgb_end[1]
        bdiff = rgb_start[2] - rgb_end[2]

        line = []
        for i in xrange(0, steps, 1):
            j = float(i)/steps
            x = pt1[0] - (xdiff * j)
            y = pt1[1] - (ydiff * j)
            r = rgb_start[0] - (rdiff * j)
            g = rgb_start[1] - (gdiff * j)
            b = rgb_start[2] - (bdiff * j)
            line.append(self.build_point(x,y,r,g,b)) 
        return line


    def read(self, n):
        points = []

        pt_count = len(self.points)

        if pt_count == 0:
            return [self.build_point(0,0,r=0,g=0,b=0)] * n


        combos = [c for c in combinations(self.points.values(), 2)]
        
        if len(combos) > 0:
            i = 0
            m = n / len(combos)
            for p1,p2 in combos:
                #print p1, p2
                i += m
                points += self.make_line(p1,p2,steps=m, rgb_start=(CMAX,0,0), rgb_end=(0,0,CMAX))
            points += [self.build_point(0,0,0,0,0)] * (n - i)


        else:
            m = n / pt_count

            INSTR_MAX = 2

            for point in self.points.values():
                if m > INSTR_MAX:
                    rendered = INSTR_MAX
                    blank = m - INSTR_MAX
                else:
                    rendered = m
                    blank = 0

                to_render_pt = self.build_point(point[0], point[1])
                
                points += [to_render_pt] * rendered
                points += [self.build_point(point[0], point[1],r=0,g=0,b=0)] * blank


        return points


class Asteroids(PointExtractionMixin):

    def __init__(self, *args,**kwargs):
        self.ps = PointStream()
        self.ships = {}
        super(AsteroidInspired, self).__init__(*args,**kwargs)


    def post_extract_points(self, frame):
        if self.points:
            print self.points
        for key, point in self.points.iteritems():
            s = self.ships[key]
            s.x = point[0]
            s.y = point[1]

    def new_point(self, key, pt):
        s = Asteroid(pt[0], pt[1], r=CMAX/2, g=CMAX/4, b=CMAX/4)
        s.theta = 0.5
        self.ships[key] = s
        self.ps.objects.append(s)

    def lost_point(self, key):
        s = self.ships[key]
        del self.ships[key]
        s.destroy = True


    def read(self, n):
        return [self.safe_pt(x,y) + (r,g,b) for x,y,r,g,b in self.ps.read(n)]



class WaveStream(PointExtractionMixin):

    def __init__(self, *args,**kwargs):
        self.ps = PointStream()
        self.wave = Wave(0,0, r=CMAX/2, g=CMAX/4, b=CMAX/4)
        self.ps.objects.append(self.wave)
        super(WaveStream, self).__init__(*args,**kwargs)


    def post_extract_points(self, frame):
        # if self.points:
        #     print self.points
        # for key, point in self.points.iteritems():
        #     s = self.ships[key]
        #     s.x = point[0]
        #     s.y = point[1]
        self.wave.key_points = self.points.values()

    def new_point(self, key, pt):
        pass

    def lost_point(self, key):
        pass


    def read(self, n):
        return [self.safe_pt(x,y) + (r,g,b) for x,y,r,g,b in self.ps.read(n)]




class PointStreamingOSCLeapListener(Asteroids,
                                    RealPartTrackerMixin, 
                                    BundledMixin, 
                                    LinearScalingMixin, 
                                    OSCLeapListener):
    pass

class PointStreamingLeapListener(WaveStream,
                            RealPartTrackerMixin,
                            LinearScalingMixin,
                            BaseLeapListener):
    pass



OSC = False


def main():

    if OSC:
        hostname='169.254.74.5'
        port=6678
        listener = PointStreamingOSCLeapListener(hostname=hostname, port=port,
                    x_mm_min=-100, x_mm_max=100,
                    y_mm_min=100, y_mm_max=300)

    else:

        listener = PointStreamingLeapListener(x_mm_min=-100, x_mm_max=100,
                    y_mm_min=100, y_mm_max=300)

    controller = Leap.Controller()
    controller.add_listener(listener)
    try:

        while True:

            d = dac.DAC(dac.find_first_dac())
            try:
                d.play_stream(listener)
            except Exception as e:
                print e

    finally:
        controller.remove_listener(listener)



def max_box():
    d = dac.DAC(dac.find_first_dac())
    box = ColorfulSquarePointStream()
    box.hmax = 19348
    d.play_stream(box)


def asteroids_test():
    from entities.ship import Ship
    d = dac.DAC(dac.find_first_dac())
    box = PointStream()
    s = Ship(0, 0, CMAX/2, CMAX/2, CMAX/2)
    s.theta = 0.5
    box.objects.append(s)
    d.play_stream(box)


if __name__ == '__main__':

    #max_box()
    main()
    #asteroids_test()
