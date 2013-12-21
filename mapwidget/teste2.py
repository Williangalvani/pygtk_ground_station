__author__ = 'Will'
#!/usr/bin/python

'''
ZetCode PyCairo tutorial

This program shows how to draw
an image on a GTK window in PyCairo.

author: Jan Bodnar
website: zetcode.com
last edited: August 2012
'''

from gi.repository import Gtk
import cairo


class Example(Gtk.Window):

    def __init__(self):
        super(Example, self).__init__()

        self.init_ui()
        self.load_image()


    def init_ui(self):

        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)

        self.set_title("Image")
        self.resize(300, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()


    def load_image(self):

        self.ims = cairo.ImageSurface.create_from_png("a.png")


    def on_draw(self, wid, cr):

        cr.set_source_surface(self.ims, 10, 10)
        cr.paint()


def main():

    app = Example()
    Gtk.main()


if __name__ == "__main__":
    main()