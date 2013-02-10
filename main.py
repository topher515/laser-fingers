
import math
import random
import itertools
import sys
import thread
import time

from globalvals import *
from pointstream import PointStream
import dac

from entities.asteroid import Asteroid

ps = PointStream()
DRAW = ps



def dac_thread():
    global DRAW

    while True:
        try:

            d = dac.DAC(dac.find_first_dac())
            d.play_stream(ps)

        except Exception as e:

            # import sys, traceback
            # print '\n---------------------'
            # print 'Exception: %s' % e
            # print '- - - - - - - - - - -'
            # traceback.print_tb(sys.exc_info()[2])
            # print "\n"
            raise


def spawn(x,y,xVel,yVel):
    radius = random.randint(ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS)

    e = Asteroid(x, y, r=CMAX, g=CMAX, b=0, radius=radius)
    e.xVel = xVel
    e.yVel = yVel
    #e.thetaRate = random.uniform(-math.pi/100, math.pi/100)

    e.thetaRate = random.uniform(ASTEROID_SPIN_VEL_MAG_MIN,
                                ASTEROID_SPIN_VEL_MAG_MAX)
    e.thetaRate *= 1 if random.randint(0, 1) else -1

    return e


def spawn_enemy():
    x, y, xVel, yVel = (0, 0, 0, 0)
    spawnType = random.randint(0, 7)

    """
    SPAWN LOCATION -- corners and edges
    """
    if spawnType == 0:
        # TOP RIGHT
        x = MIN_X
        y = MAX_Y
        xVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 1:
        # BOTTOM RIGHT
        x = MIN_X
        y = MIN_Y
        xVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 2:
        # BOTTOM LEFT
        x = MAX_X
        y = MIN_Y
        xVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 3:
        # TOP LEFT
        x = MAX_X
        y = MAX_Y
        xVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 4:
        # TOP EDGE
        x = random.randint(MIN_X, MAX_X)
        y = MAX_Y
        xVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        xVel *= 1 if random.randint(0, 1) else -1
        yVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 5:
        # RIGHT EDGE
        x = MIN_X
        y = random.randint(MIN_Y, MAX_Y)
        xVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel *= 1 if random.randint(0, 1) else -1

    elif spawnType == 6:
        # BOTTOM EDGE
        x = random.randint(MIN_X, MAX_X)
        y = MIN_Y
        xVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        xVel *= 1 if random.randint(0, 1) else -1
        yVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)

    elif spawnType == 7:
        # LEFT EDGE
        x = MAX_X
        y = random.randint(MIN_Y, MAX_Y)
        xVel = -random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel = random.randint(ASTEROID_VEL_MAG_MIN, ASTEROID_VEL_MAG_MAX)
        yVel *= 1 if random.randint(0, 1) else -1

    e = spawn(x,y,xVel,yVel)

    return e



def run_thread():

    DRAW.objects.append(spawn(0,0,0,0))

    while True:
        for obj in DRAW.objects:
            x = obj.x
            y = obj.y
            x += obj.xVel
            y += obj.yVel
            if x < MIN_X or x > MAX_X or y < MIN_Y or y > MAX_Y :
                obj.destroy = True
                continue
            obj.x = x
            obj.y = y
            obj.theta += obj.thetaRate



def main():
	thread.start_new_thread(dac_thread, ())
	thread.start_new_thread(run_thread, ())

	while True:
	    time.sleep(20000000)



if __name__ == '__main__':
	main()