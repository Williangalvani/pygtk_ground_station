import cairo
from gi.repository import Gtk
from os.path import abspath, dirname, join

#http://maps.googleapis.com/maps/api/staticmap?center=#X,#Y&zoom=#Z&size=200x200&sensor=false
WHERE_AM_I = abspath(dirname(__file__))
from tileLoader import TileLoader
from gi.repository import Gdk
from math import ceil
from gi.repository import GLib

class MyApp(object):
    """Double buffer in PyGObject with cairo"""

    def __init__(self):
        # Build GUI
        self.builder = Gtk.Builder()
        self.glade_file = join(WHERE_AM_I, 'test.glade')
        self.builder.add_from_file(self.glade_file)


        # Get objects
        go = self.builder.get_object
        self.window = go('window')
        self.tileLoader = TileLoader(self.window)
        self.double_buffer = None
        self.lat = -48.519688
        self.long = -27.606899
        self.zoom = 11
        self.button = 0
        self.x,self.y = 0,0
        self.pointerX = 0
        self.pointerY = 0
        self.heigth = 0
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
        #print dir(self.window)
        self.window.resize(256,256)
        # Everything is ready
        self.window.show()
        self.updateloop()



    def updateloop(self):
        print "update"
        self.window.queue_draw()
        GLib.timeout_add_seconds(1, self.updateloop)

    def on_scroll(self,widget,event):
        #print dir(Gdk)
        #print event.get_scroll_direction()
        #if event.get_scroll_direction() == Gdk.KEY_ScrollUp:
        if event.get_scroll_direction()[1] == 0: # UP
            self.zoom+=1
            if self.zoom>20:
                self.zoom = 20

        else:
            self.zoom-=1
            if self.zoom < 1:
                self.zoom = 1
        self.window.queue_draw()

    def on_click(self,widget,event):
        self.button = event.button
        print event.button

    def on_release(self,widget,event):
        self.button = 0

    def on_move(self,widget,event):
        x, y = event.x, event.y
        dx = x-self.pointerX
        dy = y - self.pointerY
        self.pointerX, self.pointerY = x, y
        if self.button == 1:
            #self.dx+=dx
            dlat,dlong = self.tileLoader.pix_to_coord(dx,self.long,dy,self.zoom)
            self.lat -= dlat
            self.long-= dlong
            self.window.queue_draw()
        #print x,y

    def draw_tiles(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            # Create cairo context with double buffer as is DESTINATION
            span_x = self.width
            span_y = self.heigth
            tiles_x = int(ceil(span_x/256.0))
            tiles_y = int(ceil(span_y/256.0))

            cc = cairo.Context(db)
            #print tiles_x,tiles_y
            tiles = self.tileLoader.loadArea(self.long,self.lat,self.zoom,tiles_x,tiles_y)
            tile_number=0
            line_number=0

            xcenter = self.width/2 - 128
            ycenter = self.heigth/2 - 128
            offsetx,offsety = self.tileLoader.gmap_tile_xy_from_coord(self.long,self.lat,self.zoom)
            #print offsetx,offsety


            xtiles = len(tiles[0])
            ytiles = len(tiles)
            #print len(tiles),len(tiles[0])
            for line in tiles:
                for tile in line:
                    x = (tile_number - int(xtiles/2)) * 256 + xcenter
                    y = (line_number - int(ytiles/2)) * 256 + ycenter
                    finalx = x + 128 - offsetx
                    finaly = y + 128 - offsety
                    cc.set_source_surface(tile, finalx+self.dx, finaly+self.dy)
                    cc.paint()
                    tile_number += 1
                tile_number = 0
                line_number += 1



            #print tiles_x,tiles_y



            db.flush()

        else:
            print('Invalid double buffer')

    def main_quit(self, widget):
        """Quit Gtk"""
        Gtk.main_quit()

    def on_draw(self, widget, cr):

        """Throw double buffer into widget drawable"""

        if self.double_buffer is not None:
            self.draw_tiles()
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            #print dir(cr)
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
        self.double_buffer = cairo.ImageSurface(\
                cairo.FORMAT_ARGB32,
                widget.get_allocated_width(),
                widget.get_allocated_height()
            )
        self.heigth = widget.get_allocated_height()
        self.width = widget.get_allocated_width()

        # Initialize the buffer
        self.draw_tiles()

        return False

if __name__ == '__main__':
    gui = MyApp()
    Gtk.main()