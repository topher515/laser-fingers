from Tkinter import *
import SocketServer
import threading
from walldriver import PANEL_NUM

import time



MAX_REFRESH_RATE = 15


WALL_Y_MAX = 32600
WALL_Y_MIN = -32600
WALL_X_MAX = 32600
WALL_X_MIN = -32600


class DACSimulator(object):


    def __init__(self,host="localhost",port=7778):

        # Setup TCP server
        self.host = host
        self.port = port
        self.server = self.WallTCPServer((self.host,self.port), self.WallTCPHandler, sim=self)
        #super(WallServer,self).__init__()
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        # Setup GUI
        self.master = Tk()
        self.w = Canvas(self.master, width=800, height=800)
        self.w.pack()


        panel_w = 98
        panel_h = 98

        self.panels = {}
        self.channels = {}

        y = 1
        for row in WALL_LAYOUT:
            x = 1
            for panel_num in row:

                i = self.w.create_rectangle(x, y, x+panel_w, y+panel_h, fill='#000')

                if panel_num is not None:

                    j = self.w.create_text(x+10,y+10,text="%s" % panel_num,fill="#FFF")

                    p = WallSimulator.Panel(canvas=self.w, rect=i, panel_num=panel_num)

                    self.panels[panel_num] = p

                    j = (panel_num-1)*3+1
                    self.channels[j] = p.r
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)
                    j = (panel_num-1)*3+2
                    self.channels[j] = p.g
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)
                    j = (panel_num-1)*3+3
                    self.channels[j] = p.b
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)

                x += panel_w+2

            y += panel_h+2  

        print "Built Wall GUI..."
        #print "Channels..."
        #print self.channels
        #print "Panels..."
        #print self.panels


    def start(self):    
        print "Starting server at %s:%s..." % (self.host,self.port)
        self.server_thread.start()
        print "Starting GUI..."
        mainloop()
        print "Stopping server..."
        self.server.shutdown()


    class WallTCPServer(SocketServer.TCPServer):
        def __init__(self,*args,**kwargs):
            self.wait_time = 1/float(MAX_REFRESH_RATE)
            self.sim = kwargs.pop('sim')
            self.last_time = time.time()
            super(WallTCPServer,self).__init__(self,*args,**kwargs)


    class WallTCPHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if time.time() - self.server.last_time < self.server.wait_time:
                return
            self.server.last_time = time.time()

            lines = self.rfile.readlines()
            for ch,val in [line.strip().split(' ') for line in lines]:
                self.server.wall.channels[int(ch)].value = int(val)


def main():
    w = DACSimulator()
    w.start()

if __name__ == '__main__':
    main()





class WallSimulator(object):

    class Channel(object):
        def __init__(self,panel,channel_num):
            self._value = 0
            self.panel = panel
            self.channel_num = channel_num

        def _set_val(self,val):
            if self._value != val:
                self._value =val
                self.panel.canvas.master.event_generate('<<Channel-Update-%s>>' % self.channel_num)
        def _get_val(self):
            return self._value
        value = property(fget=_get_val,fset=_set_val)


    class Panel(object):
        def __init__(self,canvas,rect,panel_num):
            self.canvas = canvas
            self.rect = rect
            self.r = WallSimulator.Channel(self,(panel_num-1)*3+1)
            self.g = WallSimulator.Channel(self,(panel_num-1)*3+2)
            self.b = WallSimulator.Channel(self,(panel_num-1)*3+3)

        def _update(self,foo):
            self.canvas.itemconfig(self.rect,fill='#%0.2X%0.2X%0.2X' % (self.r.value,self.g.value,self.b.value))





    def __init__(self,host="localhost",port=7778):

        # Setup TCP server
        self.host = host
        self.port = port
        self.server = WallSimulator.WallTCPServer((self.host,self.port), WallSimulator.WallTCPHandler, wall=self)
        #super(WallServer,self).__init__()
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        # Setup GUI
        self.master = Tk()
        self.w = Canvas(self.master, width=1000, height=400)
        self.w.pack()


        panel_w = 98
        panel_h = 98

        self.panels = {}
        self.channels = {}

        y = 1
        for row in WALL_LAYOUT:
            x = 1
            for panel_num in row:

                i = self.w.create_rectangle(x, y, x+panel_w, y+panel_h, fill='#000')

                if panel_num is not None:

                    j = self.w.create_text(x+10,y+10,text="%s" % panel_num,fill="#FFF")

                    p = WallSimulator.Panel(canvas=self.w, rect=i, panel_num=panel_num)

                    self.panels[panel_num] = p

                    j = (panel_num-1)*3+1
                    self.channels[j] = p.r
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)
                    j = (panel_num-1)*3+2
                    self.channels[j] = p.g
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)
                    j = (panel_num-1)*3+3
                    self.channels[j] = p.b
                    self.master.bind('<<Channel-Update-%s>>' % j, p._update)

                x += panel_w+2

            y += panel_h+2  

        print "Built Wall GUI..."
        #print "Channels..."
        #print self.channels
        #print "Panels..."
        #print self.panels


    def start(self):    
        print "Starting server at %s:%s..." % (self.host,self.port)
        self.server_thread.start()
        print "Starting GUI..."
        mainloop()
        print "Stopping server..."
        self.server.shutdown()


    class WallTCPServer(SocketServer.TCPServer):
        def __init__(self,*args,**kwargs):
            self.wait_time = 1/float(MAX_REFRESH_RATE)
            self.wall = kwargs.pop('wall')
            self.last_time = time.time()
            SocketServer.TCPServer.__init__(self,*args,**kwargs)


    class WallTCPHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if time.time() - self.server.last_time < self.server.wait_time:
                return
            self.server.last_time = time.time()

            lines = self.rfile.readlines()
            for ch,val in [line.strip().split(' ') for line in lines]:
                self.server.wall.channels[int(ch)].value = int(val)


def main():
    w = WallSimulator()
    w.start()

if __name__ == '__main__':
    main()