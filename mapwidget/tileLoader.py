__author__ = 'Will'

from math import sin, cos, log , pi
from imageCache import ImageLoader


class TileLoader():
    def __init__(self):
        self.loader = ImageLoader()

    def coord_to_gmap_tile(self,lat, lon, zoom):

        sin_phi = sin(lat * pi / 180)

        norm_x = lon / 180
        norm_y = (0.5 * log((1 + sin_phi) / (1 - sin_phi))) / pi

        tile_x = (2 ** zoom) * ((norm_x + 1) / 2)
        tile_y = (2 ** zoom) * ((1 - norm_y) / 2)

        return int(tile_x), int(tile_y)

    def loadImage(self,x,y,z):
        x,y = self.coord_to_gmap_tile(x,y,z)
        return self.loader.getImage(x,y,z)

    def gmap_tile_xy(self,tile_x, tile_y):
        return (tile_x - int(tile_x)) * 256,\
               (tile_y - int(tile_y)) * 256



#if __name__ == '__main__':
#    x,y = coord_to_gmap_tile(-27.600746,-48.520646,11)
#    cache = ImageLoader()
#    cache.getImage(x,y,11)