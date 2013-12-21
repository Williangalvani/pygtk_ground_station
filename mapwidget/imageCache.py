__author__ = 'Will'
import urllib
from os.path import abspath, dirname, join
import os

WHERE_AM_I = abspath(dirname(__file__))

cachedir = join(WHERE_AM_I, "cache")

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)



class ImageLoader(object):
    def __init__(self):
        self.address = "http://mt0.google.com/vt/lyrs=y&hl=en&x={0}&s=&y={1}&z={2}"

    def getImage(self, lat, long, level):
        leveldir = join(cachedir, str(level))
        ensure_dir(leveldir)
        filename = join(leveldir, "{0}-{1}.png".format(lat, long))
        try:
             image = open(filename)
             image.close()
             #print image

        except:
            imageurl = self.address.format(lat, long, level)
            print "loading image from " , imageurl
            urllib.urlretrieve(imageurl, filename)

            #output = open(join(leveldir,"{0}-{1}.png".format(lat,long)),'wb')
            #output.write(image.read())
            #output.close()
            #print image
        image = open(filename)
        return image

#ImageLoader().getImage(0,0,0)
