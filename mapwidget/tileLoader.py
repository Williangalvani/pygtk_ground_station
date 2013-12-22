__author__ = 'Will'

from math import sin, cos, log , pi
from imageCache import ImageLoader
import cairo
import threading
from collections import deque
import time
import traceback

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args

        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


class TileLoader():
    def __init__(self,window):
        self.loader = ImageLoader()
        self.cache = {}
        self.window = window
        self.cache["loading"] = cairo.ImageSurface.create_from_png("loading.png")
        self.pendingTiles = deque()
        self.loadingTiles = set()
        self.threads = []
        self.listlock = threading.Lock()
        self.uilock = threading.Lock()
        for i in range(10):
            t = FuncThread(self.loading_thread,self.pendingTiles,self.cache,self.listlock,i)
            self.threads.append(t)
            t.start()

    def coord_to_gmap_tile(self,lat, lon, zoom):

        sin_phi = sin(lat * pi / 180)

        norm_x = lon / 180
        norm_y = (0.5 * log((1 + sin_phi) / (1 - sin_phi))) / pi

        tile_x = (2 ** zoom) * ((norm_x + 1) / 2)
        tile_y = (2 ** zoom) * ((1 - norm_y) / 2)

        return tile_x, tile_y

    def pix_to_coord(self,x, y0,y, zoom):

        sin_phi =  cos(y0 * pi / 180)
        long = 180.0/(2**zoom)*x / 128
        lat = - 180.0/(2**zoom)*y / 128 * sin_phi
        return long,lat

    def loadImage(self,x,y,z):
        x = int(x)
        y = int(y)
        z = int(z)
        return self.loader.getImage(x,y,z)

    def gmap_tile_xy(self,tile_x, tile_y):

        return (tile_x - int(tile_x)) * 256,\
               (tile_y - int(tile_y)) * 256

    def gmap_tile_xy_from_coord(self,x, y,z):
        tile_x, tile_y = self.coord_to_gmap_tile(x,y,z)
        return (tile_x - int(tile_x)) * 256,\
               (tile_y - int(tile_y)) * 256


    def loadImageSurface(self,x,y,z):
        name = str(self.coord_to_gmap_tile(x,y,z))
        if self.cache.has_key(name):
            return self.cache[name]
        else:
            tile = self.loadImage(x,y,z)
            img = cairo.ImageSurface.create_from_png(tile)
            self.cache[name] = img
        #print name
        return img

    def loadImageSurfaceFromTile(self,x,y,z):
        name = str((int(x),int(y)))
        #print name
        if self.cache.has_key(name):
                return self.cache[name]
        else:
            if (x,y,z) not in self.pendingTiles and (x,y,z) not in self.loadingTiles:
                self.pendingTiles.append((x,y,z))
            return self.cache["loading"]
        return img


    def loading_thread(self,pending,cache,lock,id):
        id = id
        while(1):
            lock.acquire()
            if len(pending)>0:
                x,y,z = pending.popleft()
                self.loadingTiles.add((x,y,z))
                lock.release()
                name = str((int(x),int(y)))
                try:
                    tile = self.loadImage(x,y,z)
                    img = cairo.ImageSurface.create_from_png(tile)
                    cache[name] = img
                    self.loadingTiles.remove((x,y,z))
                except Exception, e:
                    print "erro! " ,e,  name
                    print traceback.format_exc()

            else:
                lock.release()
            time.sleep(0.1)



    def loadArea(self,x0,y0,z0,tiles_x,tiles_y):
        x0,y0 = self.coord_to_gmap_tile(x0,y0,z0)
        tiles_array = []
        x_span = (tiles_x/2)+1
        y_span = (tiles_y/2)+1
        for y in range(-y_span,y_span+1):
            #print y
            y_list = []
            for x in range(-x_span,x_span+1):
                #print x,y
                y_list.append(self.loadImageSurfaceFromTile(x0+x,y0+y,z0))
            tiles_array.append(y_list)
        #print tiles_array
        return tiles_array


#if __name__ == '__main__':
#    x,y = coord_to_gmap_tile(-27.600746,-48.520646,11)
#    cache = ImageLoader()
#    cache.getImage(x,y,11)