"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
#from scanner import Scanner
from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])

        # Gain access to Gui Class parent's variables
        self.parent = parent

        # Initialise display value variables
        self.time_steps = 10

        # Initialise store for monitors and devices
        self.monitors = monitors
        self.devices = devices

        # Set colour palette
        self.bkgd_colour = (0.3, 0.3, 0.3)
        self.line_colour = (0.9, 0.9, 0.5)
        self.text_colour = (0.9, 0.9, 0.9)

        # Initialise canvas size variable
        self.canvas_size = self.GetClientSize()

        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

        # Set background colour
        GL.glClearColor(self.bkgd_colour[0], self.bkgd_colour[1],
                        self.bkgd_colour[2], 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def render_test(self, text, time_steps=None, add_time_steps=None):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        if time_steps:
            self.time_steps = time_steps

        if add_time_steps:
            self.time_steps += add_time_steps

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(self.time_steps):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        self.canvas_size = self.GetClientSize()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        if not self.parent.values:
            self.parent.trace_names = ['N/A']
            self.parent.values = [[]]
            #raise ValueError("No parent values to display")

        display_ys = [self.canvas_size[1] - 100 - 80*j for j in range(len(self.parent.values))]
        display_x = 120

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw title
        title_text = "Monitored Signal Display"
        self.render_text(title_text, 10, self.canvas_size[1]-20, title=True)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        for j in range(len(self.parent.trace_names)):
            self.render_text(self.parent.trace_names[j], 10, display_ys[j]+5)

            # Draw a sample signal trace
            GL.glColor3f(self.line_colour[0], self.line_colour[1],
                         self.line_colour[2])  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(len(self.parent.values[0])):
                x = (i * 20) + display_x
                x_next = (i * 20) + display_x + 20
                if self.parent.values[j][i]:
                    y = display_ys[j] + 25
                else:
                    y = display_ys[j]

                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
            GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        self.canvas_size = self.GetClientSize()
        size = self.canvas_size

        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, title=False):
        """Handle text drawing operations."""
        GL.glColor3f(self.text_colour[0], self.text_colour[1],
                     self.text_colour[2])  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        if not title:
            font = GLUT.GLUT_BITMAP_HELVETICA_12
        else:
            font = GLUT.GLUT_BITMAP_HELVETICA_18

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_spin(self, event): Event handler for when the user changes the second
                           spin controller.

    on_run_button(self, event): Event handler for when the user clicks the run
                                 button.

    on_continue_button(self, event): Event handler for when the user clicks the
                                      continue button.

    run_network_and_get_values(self, time_steps): Executes the network for a
                    given number of time steps and stores the monitored
                    signals for each time step.

    on_text_box(self, event): Event handler for when the user enters text.

    on_add_monitor_button(self, event): Event handler for when the user clicks
                    the add_monitor button.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Store for monitored signals from network
        self.values = None
        self.trace_names = None
        self.time_steps = 10

        # Store inputs from logsim.py
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        # Configure the widgets
        self.text_cycles = wx.StaticText(self, wx.ID_ANY, "Cycles to run:")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")

        self.text_cont_cycles = wx.StaticText(self, wx.ID_ANY, "Continue:")
        self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "3")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        self.text_switch_control = wx.StaticText(self, wx.ID_ANY, "Toggle switch:")

        self.text_add_monitor = wx.StaticText(self, wx.ID_ANY, "Add monitored point:")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)

        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor_button)

        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer1 = wx.BoxSizer(wx.VERTICAL)
        side_sizer2 = wx.BoxSizer(wx.VERTICAL)
        side_sizer3 = wx.BoxSizer(wx.VERTICAL)
        side_sizer4 = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer1, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer2, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer3, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer4, 1, wx.ALL, 5)

        side_sizer1.Add(self.text_cycles, 1, wx.TOP, 10)
        side_sizer1.Add(self.spin, 1, wx.ALL, 5)
        side_sizer1.Add(self.run_button, 1, wx.ALL, 5)

        side_sizer2.Add(self.text_cont_cycles, 1, wx.ALL, 10)
        side_sizer2.Add(self.spin_cont, 1, wx.ALL, 5)
        side_sizer2.Add(self.continue_button, 1, wx.ALL, 5)

        side_sizer3.Add(self.text_switch_control, 1, wx.ALL, 10)

        side_sizer4.Add(self.text_add_monitor, 1, wx.ALL, 10)
        side_sizer4.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer4.Add(self.add_monitor_button, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_spin_cont(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin_cont.GetValue()
        text = "".join(["New continue spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        spin_value = self.spin.GetValue()

        self.time_steps = spin_value
        self.run_network_and_get_values(self.time_steps)

        text = "Run button pressed. (self.time_steps=%d)"%self.time_steps
        self.canvas.render(text)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        spin_cont_value = self.spin_cont.GetValue()

        self.time_steps += spin_cont_value
        self.run_network_and_get_values(self.time_steps)

        text = "Continue button pressed. (self.time_steps=%d)"%self.time_steps
        self.canvas.render(text)

    def run_network_and_get_values(self, time_steps):
        """Run the network and get the monitored signal values"""
        ## Test for now:
        self.values = [[0, 0, 0, 1, 1, 1], [1, 1, 0, 0, 1, 0]]
        self.trace_names = ['test 000111', 'test 110010']

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        spin_value = self.spin.GetValue()
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_add_monitor_button(self, event):
        """Handle the event when user clicks "add" """
        pass

path, names, devices, network, monitors = None, None, None, None, None
app = wx.App()
gui = Gui("Logic Simulator", path, names, devices, network, monitors)
gui.Show(True)
app.MainLoop()
