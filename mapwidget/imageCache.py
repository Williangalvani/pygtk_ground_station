__author__ = 'Will'
import urllib
from os.path import abspath, dirname, join
import os
from PIL import Image
import traceback
import time

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
        except:
            imageurl = self.address.format(lat, long, level)
            print "miss, loading image from " , imageurl
            tempfilename = filename.replace(".png","temp.png")
            tempfile = open(tempfilename,'wb')
            tempfile.write(urllib.urlopen(imageurl).read())
            tempfile.close()
            try:
                img = Image.open(tempfilename)
                new = Image.new('RGB', (256,256))
                new.paste(img,(0,0))
                newfile = open(filename,'wb')
                new.save(newfile,"PNG")

            except Exception, e:
                print "erro no Cache de disco!!", e, filename
                print traceback.format_exc()
        return filename
