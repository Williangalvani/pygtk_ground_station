import cairo
from gi.repository import Gtk
from os.path import abspath, dirname, join

#http://maps.googleapis.com/maps/api/staticmap?center=#X,#Y&zoom=#Z&size=200x200&sensor=false
WHERE_AM_I = abspath(dirname(__file__))
from tileLoader import TileLoader

class MyApp(object):
    """Double buffer in PyGObject with cairo"""

    def __init__(self):
        # Build GUI
        self.builder = Gtk.Builder()
        self.glade_file = join(WHERE_AM_I, 'test.glade')
        self.builder.add_from_file(self.glade_file)
        self.tileLoader = TileLoader()

        # Get objects
        go = self.builder.get_object
        self.window = go('window')
        self.double_buffer = None
        self.lat = 0
        self.long = 0
        self.zoom = 7

        # Connect signals
        self.builder.connect_signals(self)

        # Everything is ready
        self.window.show()

    def draw_something(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            # Create cairo context with double buffer as is DESTINATION
            cc = cairo.Context(db)


            # Scale to device coordenates
            cc.scale(db.get_width(), db.get_height())

            # Draw a white background
            cc.set_source_rgb(1, 1, 1)

            # Draw something, in this case a matrix
            rows = 10
            columns = 10
            cell_size = 1.0 / rows
            line_width = 1.0
            line_width, notused = cc.device_to_user(line_width, 0.0)

            print dir(cc)
            for i in range(rows):
                for j in range(columns):
                    cc.rectangle(j * cell_size, i * cell_size, cell_size, cell_size)
                    cc.set_line_width(line_width)
                    cc.set_source_rgb(0, 0, 0)
                    cc.stroke()

            # Flush drawing actions
            db.flush()

        else:
            print('Invalid double buffer')

    def main_quit(self, widget):
        """Quit Gtk"""
        Gtk.main_quit()

    def on_draw(self, widget, cr):

        tile = self.tileLoader.loadImage(-27.600746,-48.520646,11)
        surface = cairo.ImageSurface (cairo.FORMAT_RGB24, 256,256)
        surface.create_from_png(tile)
        surface = cairo.ImageSurface.create_for_data (tile, cairo.FORMAT_RGB24, 256, 256)
        #ims = cairo.ImageSurface.create_from_png(tile)
        """Throw double buffer into widget drawable"""

        if self.double_buffer is not None:
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            print dir(cr)
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

        # Initialize the buffer
        self.draw_something()

        return False

if __name__ == '__main__':
    gui = MyApp()
    Gtk.main()