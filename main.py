__author__ = 'Will'

import gtk
import gobject
import random
from math import cos, sin,radians
from PIL import Image,ImageOps
import numpy


class BaseStation():

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("sub.glade")

        self.window = self.builder.get_object("window1")
        self.compass = self.builder.get_object("compass")
        self.horizon = self.builder.get_object("horizon")
        self.mapframe = self.builder.get_object("frame4")
        self.log = self.builder.get_object("log")
        self.log.set_editable(False)
        self.log.set_wrap_mode(gtk.WRAP_WORD)
        self.logbuffer = self.log.get_buffer()
        """@type : gtk.TextBuffer"""
        self.compass_angle = 0
        self.roll_angle=0
        self.pitch_angle=0
        self.image_names = ['compass.png', 'horizon2.png', 'battery.png'] # horizon cant be first, regular size is based on compass' size
        self.mask = Image.open('mask.png').convert('L')
        self.desired_size = None

        from mapviewer import UI
        self.mapui = UI()
        print dir(self.mapframe)
        self.mapframe.remove(self.mapframe.get_child())
        self.mapframe.add(self.mapui)

        self.images = {}
        self.loadImages()

        self.update()
        self.window.show_all()
        self.window.connect("destroy", gtk.main_quit)


        gtk.main()

    def loadImages(self):
        for name in self.image_names:
            self.images[name] = Image.open(name)
        if not self.desired_size:
            self.desired_size = self.images[self.image_names[0]].getbbox()[2:]
    def updateImages(self):
        #print dir(self.compass)
        self.compass.set_from_pixbuf(self.get_rotated_image('compass.png', self.compass_angle))
        self.horizon.set_from_pixbuf(self.get_rotated_and_shifted_horizon_image(self.roll_angle, self.pitch_angle))

    def get_rotated_image(self,image,angle):
        src_im = self.images[image]
        size = src_im.getbbox()[2:]
        dst_im = Image.new("RGBA",size, "white" )
        im = src_im.convert('RGBA')
        rot = im.rotate( angle, expand=0, )#.resize(size)
        dst_im.paste( rot, (0, 0), rot)
        dst_im.save("test.png")
        arr = numpy.array(self.apply_circular_mask(dst_im))
        return gtk.gdk.pixbuf_new_from_array(arr, gtk.gdk.COLORSPACE_RGB, 8)


    def apply_circular_mask(self,image):
        output = ImageOps.fit(image, self.mask.size, centering=(0.5, 0.5))
        output.putalpha(self.mask)
        return output

    def get_rotated_and_shifted_horizon_image(self, angle, shift):
        src_im = self.images['horizon2.png']
        size = src_im.getbbox()[2:]
        dst_im = Image.new("RGBA",size, "blue" )
        im = src_im.convert('RGBA')
        rot = im.rotate( angle, expand=0, )
        angle = radians(angle)
        dst_im.paste( rot, (int(shift*sin(angle)), int(shift*cos(angle))), rot)
        desired_height = self.desired_size[1]
        desired_width = self.desired_size[0]
        dy = desired_height/2
        dx = desired_width/2
        cx = size[0]/2
        cy = size[1]/2
        new_size = [cx-dx,cy-dy,cx+dx,cy+dy]
        dst_im = dst_im.crop(new_size)
        arr = numpy.array(self.apply_circular_mask(dst_im))
        #print dir(self.compass)
        return gtk.gdk.pixbuf_new_from_array(arr, gtk.gdk.COLORSPACE_RGB, 8)

    def log_text(self,string):
        self.logbuffer.insert(self.logbuffer.get_end_iter(),string)

    def update(self):
        self.compass_angle += 2
        self.roll_angle += random.randrange(-2,2);
        self.pitch_angle += random.randrange(-1,1)
        #print type(self.log)
        self.log_text("o haay\n")
        #print dir(self.log)
        #print self.pitch_angle,self.roll_angle


        self.updateImages()
        gobject.timeout_add(100, self.update)


BaseStation()
