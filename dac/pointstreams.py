import dac
from dac import Point


class Shape(object):
    def __init__(self,x,y,**kwargs):
        self.pstep = int(kwargs.pop('pstep',200))
        self.x = x
        self.y = y
        self.rgb = kwargs.pop('rgb',(255,255,255))



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
        # Draw bottom
        for x in xrange(self.x + right_w, self.x - left_w, -pstep):
            yield (x, self.y + top_h) + self.rgb
        # Draw left
        for y in xrange(self.y + bottom_h, self.y - top_h, -pstep):
            yield (self.x + right_w, y) + self.rgb





class ScenePointStream(object):
    def __init__(self, max_points=1800):
        self.shapes = []
        self.max_points = max_points

    def add_shape(self, shape):
        self.shapes.append(shape)

    def __iter__(self):
        while True:
            # First determine # points needed to determin full resolution
            # Then use that / max points to determine resolution of shapes
            needed_points = sum([x.count() for x in self.shapes])
            pstep = (needed_points / self.max_points) or 1 # Pstep must be at least 1
            for shape in self.shapes:
                for point in shape.points(pstep):
                    yield Point(point)





class ColorfulSquarePointStream(object):
    def __iter__(self):
        pmax = 32600
        pstep = 200
        cmax = 65535
        while True:
            for x in xrange(-pmax, pmax, pstep):
                yield Point(x, pmax, cmax, 0, 0)
            for y in xrange(pmax, -pmax, -pstep):
                yield Point(pmax, y, 0, cmax, 0)
            for x in xrange(pmax, -pmax, -pstep):
                yield Point(x, -pmax, 0, 0, cmax)
            for y in xrange(-pmax, pmax, pstep):
                yield Point(-pmax, y, cmax, cmax, cmax)


class NullPointStream(object):
    def read(self, n):
        while True:
            yield Point(0, 0, 0, 0, 0)

#dac.find_dac()

d = dac.DAC(dac.find_first_dac())

d.play_stream(ColorfulSquarePointStream())