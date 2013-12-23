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

    def get_image(self, lat, long, level):
        got_image = False
        lat = int(lat)
        long = int(long)
        level = int(level)
        level_dir = join(cachedir, str(level))
        ensure_dir(level_dir)
        filename = join(level_dir, "{0}-{1}.png".format(lat, long))
        try:
            image = open(filename)
            image.close()
            got_image = True
        except Exception , e:
            #print e
            pass

        if not got_image:
            image_url = self.address.format(lat, long, level)
            print "miss, loading image from " , image_url
            temp_file_name = filename.replace(".png","temp.png")
            temp_file = open(temp_file_name,'wb')
            temp_file.write(urllib.urlopen(image_url).read())
            temp_file.close()
            try:
                img = Image.open(temp_file_name)
                new = Image.new('RGB', (256,256))
                new.paste(img,(0,0))
                new_file = open(filename,'wb')
                new.save(new_file,"PNG")

            except Exception, e:
                print "erro no Cache de disco!!", e, filename
                os.remove(temp_file_name)
                os.remove(filename)
                print traceback.format_exc()
        return filename
