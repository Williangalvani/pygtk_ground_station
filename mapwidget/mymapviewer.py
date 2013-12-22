import cairo
from gi.repository import Gtk
from os.path import abspath, dirname, join

#http://maps.googleapis.com/maps/api/staticmap?center=#X,#Y&zoom=#Z&size=200x200&sensor=false
WHERE_AM_I = abspath(dirname(__file__))
from tileLoader import TileLoader
from gi.repository import Gdk
from math import ceil
from gi.repository import GLib
from datetime import datetime

class MyApp(object):
    """Double buffer in PyGObject with cairo"""

    def __init__(self):
        # Build GUI
        self.builder = Gtk.Builder()
        self.glade_file = join(WHERE_AM_I, 'test.glade')
        self.builder.add_from_file(self.glade_file)
        self.last_scroll = datetime.now()


        # Get objects
        go = self.builder.get_object
        self.window = go('window')
        self.tile_loader = TileLoader(self.window)
        self.double_buffer = None
        self.lat = -48.519688
        self.long = -27.606899
        self.zoom = 11
        self.button = 0
        self.x,self.y = 0,0
        self.pointer_x = 0
        self.pointer_y = 0
        self.height = 0
        self.width = 0
        self.dx = 0
        self.dy = 0
        # Connect signals
        self.builder.connect_signals(self)
        self.da = go("drawingarea1")

        self.window.connect("motion_notify_event", self.on_move)
        self.window.connect("button_press_event", self.on_click)
        self.window.connect("button_release_event", self.on_release)
        self.window.connect("scroll_event", self.on_scroll)
        self.window.set_events(Gdk.EventMask.EXPOSURE_MASK
                            | Gdk.EventMask.LEAVE_NOTIFY_MASK
                            | Gdk.EventMask.BUTTON_PRESS_MASK
                            | Gdk.EventMask.BUTTON_RELEASE_MASK
                            | Gdk.EventMask.POINTER_MOTION_MASK
                            | Gdk.EventMask.SCROLL_MASK
                            | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        self.window.resize(256,256)
        # Everything is ready
        self.window.show()
        self.update_loop()

    def update_loop(self):
        self.window.queue_draw()
        GLib.timeout_add_seconds(1, self.update_loop)

    def zoom_in(self):
        self.zoom+=1
        if self.zoom>20:
            self.zoom = 20

    def zoom_out(self):
        self.zoom-=1
        if self.zoom < 1:
            self.zoom = 1

    def on_scroll(self,widget,event):
        if (datetime.now() - self.last_scroll).microseconds > 100000:
            if event.get_scroll_direction()[1] == 0: # UP
                self.zoom_in()
            else:
                self.zoom_out()
            self.window.queue_draw()
            self.last_scroll = datetime.now()

    def on_click(self,widget,event):
        self.button = event.button

    def on_release(self,widget,event):
        self.button = 0

    def on_move(self,widget,event):
        x, y = event.x, event.y
        dx = x-self.pointer_x
        dy = y - self.pointer_y
        self.pointer_x, self.pointer_y = x, y
        if self.button == 1:
            dlat, dlong = self.tile_loader.dpix_to_dcoord(dx, self.long, dy, self.zoom)
            self.lat -= dlat
            self.long -= dlong
            self.window.queue_draw()


    def draw_tiles(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            span_x = self.width
            span_y = self.height
            tiles_x = int(ceil(span_x/256.0))
            tiles_y = int(ceil(span_y/256.0))

            cc = cairo.Context(db)
            tiles = self.tile_loader.load_area(self.long,self.lat,self.zoom,tiles_x,tiles_y)
            tile_number=0
            line_number=0

            x_center = self.width/2# - 128
            y_center = self.height/2# - 128
            offset_x,offset_y = self.tile_loader.gmap_tile_xy_from_coord(self.long,self.lat,self.zoom)


            xtiles = len(tiles[0])
            ytiles = len(tiles)
            #print len(tiles),len(tiles[0])
            for line in tiles:
                for tile in line:
                    x = (tile_number - int(xtiles/2)) * 256 + x_center
                    y = (line_number - int(ytiles/2)) * 256 + y_center
                    finalx = x - offset_x  #+128
                    finaly = y - offset_y  #+128
                    cc.set_source_surface(tile, finalx+self.dx, finaly+self.dy)
                    cc.paint()
                    tile_number += 1
                tile_number = 0
                line_number += 1

            db.flush()

        else:
            print('Invalid double buffer')

    def main_quit(self, widget):
        self.tile_loader.stop_threads()
        Gtk.main_quit()

    def on_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""
        if self.double_buffer is not None:
            self.draw_tiles()
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')
        return False


    def on_configure(self, widget, event, data=None):
        """Configure the double buffer based on size of the widget"""

        # Destroy previous buffer
        if self.double_buffer is not None:
            self.double_buffer.finish()
            self.double_buffer = None

        # Create a new buffer
        self.double_buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                widget.get_allocated_width(),
                                                widget.get_allocated_height())
        self.height = widget.get_allocated_height()
        self.width = widget.get_allocated_width()

        # Initialize the buffer
        self.draw_tiles()

        return False

if __name__ == '__main__':
    gui = MyApp()
    Gtk.main()