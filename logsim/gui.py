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
import os

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
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

    render_graph_axes(self, x, y): Draws graph axes.

    render_trace(self, x, y, values, name): Draws signal output.

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

        # Initialise store for help_text, monitors and devices
        self.monitors = monitors
        self.devices = devices
        self.help_text = []
        self.help_screen = False

        # Set colour palette
        self.bkgd_colour = (0.3, 0.3, 0.3)
        self.line_colour = (0.9, 0.9, 0.5)
        self.text_colour = (0.9, 0.9, 0.9)
        self.axes_colour = (0.9, 0.9, 0.9)

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

    def render_graph_axes(self, x, y):
        """Draw axis for a given signal output"""

        time_step_no = len(self.parent.values[0])
        GL.glColor3f(self.axes_colour[0], self.axes_colour[1],
                     self.axes_colour[2])  # signal trace is blue

        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(x - 4, y + 29)
        GL.glVertex2f(x - 4, y - 4)
        GL.glVertex2f(x + 4 + (time_step_no * 20), y - 4)
        GL.glEnd()
        GL.glFlush()

        for i in range(time_step_no + 1):
            self.render_text(str(i), x - 4 + (20 * i), y - 16)

        self.render_text('0', x - 14, y - 6)
        self.render_text('1', x - 14, y + 19)

    def render_trace(self, x, y, values, name):
        """Draw a signal output trace"""

        self.render_text(name, 10, y + 5)
        GL.glColor3f(self.line_colour[0], self.line_colour[1],
                     self.line_colour[2])

        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(values)):
            x0 = (i * 20) + x
            x1 = (i * 20) + x + 20
            if values[i]:
                y0 = y + 25
            else:
                y0 = y

            GL.glVertex2f(x0, y0)
            GL.glVertex2f(x1, y0)
        GL.glEnd()
        GL.glFlush()

    def render_display(self, text):
        """Handle all drawing operations."""
        #self.SetCurrent(self.context)
        self.canvas_size = self.GetClientSize()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        if not self.parent.values:
            self.parent.trace_names = ['N/A']
            self.parent.values = [[]]

        display_ys = [self.canvas_size[1] - 100 - 80 * j for j in range(len(self.parent.values))]
        display_x = 120
        signal_no = len(self.parent.trace_names)

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw title
        title_text = "Monitored Signal Display"
        self.render_text(title_text, 10, self.canvas_size[1] - 20, title=True)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        for j in range(signal_no):
            self.render_trace(display_x, display_ys[j], self.parent.values[j],
                              self.parent.trace_names[j])
            self.render_graph_axes(display_x, display_ys[j])

        GL.glFlush()
        self.SwapBuffers()

    def render(self, text):
        if self.help_screen:
            self.render_help()
        else:
            self.render_display(text)

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

    def render_help(self):
        """Render the help screen"""

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.SetCurrent(self.context)
        self.canvas_size = self.GetClientSize()

        if not self.help_text:
            with open('logsim/help.txt', 'r') as f:
                self.help_text = f.readlines()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.render_text("".join(self.help_text), 10, self.canvas_size[1] - 20)
        GL.glFlush()
        self.SwapBuffers()


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
        self.quit_id = 999
        self.open_id = 998
        self.help_id = 997
        self.home_id = 996

        """
        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)
        """

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Store for monitored signals from network
        self.values = None
        self.trace_names = None
        self.time_steps = 8

        # Store inputs from logsim.py
        self.title = title
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors

        self.switch_ids = self.devices.find_devices(self.devices.SWITCH)
        self.switch_names = [self.names.get_name_string(i) for i in self.switch_ids]
        self.switch_values = [self.devices.get_switch_value(i) for i in self.switch_ids]
        self.sig_mons, self.sig_n_mons = self.monitors.get_signal_names()

        # Toolbar setup
        toolbar = self.CreateToolBar()
        myimage = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR)
        toolbar.AddTool(self.home_id, "Home", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddTool(self.open_id, "Open file", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_TOOLBAR)
        toolbar.AddTool(self.help_id, "Help", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        toolbar.AddTool(self.quit_id, "Exit", myimage)
        toolbar.Bind(wx.EVT_TOOL, self.toolbar_handler)
        toolbar.Realize()
        self.ToolBar = toolbar

        # Configure the widgets
        self.text_cycles = wx.StaticText(self, wx.ID_ANY, "Cycles to run:")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")

        #self.text_cont_cycles = wx.StaticText(self, wx.ID_ANY, "Continue:")
        #self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "3")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        self.text_switch_control = wx.StaticText(self, wx.ID_ANY, "Switch On:")
        #self.text_switch_set = wx.StaticText(self, wx.ID_ANY, "On?:")
        self.switch_choice = wx.ComboBox(self, wx.ID_ANY, "<SWITCH>", choices=self.switch_names)
        self.switch_choice.SetValue(self.switch_names[0])
        self.switch_set = wx.CheckBox(self, wx.ID_ANY)

        self.text_add_monitor = wx.StaticText(self, wx.ID_ANY, "Signal Monitors:")
        #self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
        #                            style=wx.TE_PROCESS_ENTER)
        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")
        self.remove_monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.add_monitor_choice = wx.ComboBox(self, wx.ID_ANY, "<SIGNAL>", choices=self.sig_n_mons)
        self.remove_monitor_choice = wx.ComboBox(self, wx.ID_ANY, "<SIGNAL>", choices=self.sig_mons)
        self.add_monitor_choice.SetValue(self.sig_n_mons[0])
        self.remove_monitor_choice.SetValue(self.sig_mons[0])

        # Bind events to widgets
        #self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        #self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)

        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor_button)
        self.remove_monitor_button.Bind(wx.EVT_BUTTON, self.on_remove_monitor_button)
        self.switch_choice.Bind(wx.EVT_COMBOBOX, self.on_switch_choice)
        self.switch_set.Bind(wx.EVT_CHECKBOX, self.on_switch_set)

        #self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text_cycles, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer3, 1, wx.ALL, 5)
        side_sizer3.Add(self.run_button, 1, wx.ALL, 5)

        #side_sizer.Add(self.text_cont_cycles, 1, wx.ALL, 10)
        #side_sizer.Add(self.spin_cont, 1, wx.ALL, 5)
        side_sizer3.Add(self.continue_button, 1, wx.ALL, 5)

        side_sizer.Add(self.text_switch_control, 1, wx.ALL, 10)
        side_sizer.Add(side_sizer4, 1, wx.ALL, 5)
        side_sizer4.Add(self.switch_choice, 1, wx.ALL, 5)
        #side_sizer4.Add(self.text_switch_set, 1, wx.ALL, 5)
        side_sizer4.Add(self.switch_set, 1, wx.ALL, 5)

        side_sizer.Add(self.text_add_monitor, 1, wx.ALL, 10)
        side_sizer.Add(side_sizer1, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer2, 1, wx.ALL, 5)
        #side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer1.Add(self.add_monitor_choice, 1, wx.ALL, 5)
        side_sizer1.Add(self.add_monitor_button, 1, wx.ALL, 5)
        side_sizer2.Add(self.remove_monitor_choice, 1, wx.ALL, 5)
        side_sizer2.Add(self.remove_monitor_button, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

        self.run_network_and_get_values()
        self.canvas.render('')

    def reset_screen(self):
        """Put screen back into its initial state"""
        self.canvas.pan_x = 0
        self.canvas.pan_y = 0
        self.canvas.zoom = 1
        self.canvas.init = False

    def toolbar_handler(self, event):
        """Handles toolbar presses"""
        if event.GetId() == self.quit_id:
            canc = wx.MessageBox('Are you sure you would like to quit?', 'Quit?', wx.ICON_INFORMATION | wx.CANCEL)
            if canc == 4:
                self.Close(True)
        elif event.GetId() == self.open_id:
            openFileDialog = wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt",
                                           style=wx.FD_OPEN + wx.FD_FILE_MUST_EXIST)
            self.reset_screen()
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                print("The user cancelled")
                return  # the user changed idea...
            new_path = openFileDialog.GetPath()
            print("File chosen=", new_path)

            self.Close(True)
            names = Names()
            devices = Devices(names)
            network = Network(names, devices)
            monitors = Monitors(names, devices, network)
            scanner = Scanner(new_path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                gui = Gui("Logic Simulator", new_path, names, devices, network,
                          monitors)
                gui.Show(True)

        elif event.GetId() == self.help_id:
            self.reset_screen()
            self.canvas.help_screen = not self.canvas.help_screen
            self.canvas.render('')
        elif event.GetId() == self.home_id:
            self.reset_screen()
            self.canvas.help_screen = False
            self.canvas.render('')

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            print('menu quit')
            #self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_switch_choice(self, event):
        sw_name = self.switch_choice.GetValue()
        sw_val = self.switch_values[self.switch_names.index(sw_name)]
        if sw_val:
            self.switch_set.SetValue(1)
        else:
            self.switch_set.SetValue(0)

    def on_switch_set(self, event):
        sw_name = self.switch_choice.GetValue()
        sw_no = self.switch_names.index(sw_name)
        self.switch_values[sw_no] = [0, 1][self.switch_set.GetValue()]
        sw_id = self.names.query(sw_name)
        self.devices.set_switch(sw_id, self.switch_set.GetValue())  # SET ACTUAL SWITCH
        self.run_network_and_get_values()
        self.canvas.render('')

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
        self.run_network_and_get_values()

        text = "Run button pressed. (self.time_steps=%d)" % self.time_steps
        self.canvas.render(text)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        spin_cont_value = self.spin.GetValue()

        self.time_steps += spin_cont_value
        self.run_network_and_get_values()

        text = "Continue button pressed. (self.time_steps=%d)" % self.time_steps
        self.canvas.render(text)

    def run_network_and_get_values_test(self, time_steps):
        """Run the network and get the monitored signal values"""
        ## Test for now:
        self.values = [[0, 0, 0, 1, 1, 1], [1, 1, 0, 0, 1, 0]]
        self.trace_names = ['test 000111', 'test 110010']

    def run_network_and_get_values(self):
        """Run the network and get the monitored signal values"""

        # Add return False / True (deal with faulty execution)
        self.devices.cold_startup()
        self.monitors.reset_monitors()
        for i in range(self.time_steps):
            if not self.network.execute_network():
                break
            self.monitors.record_signals()
        self.values = []

        monitor_dict = self.monitors.monitors_dictionary
        for device_id, output_id in monitor_dict:
            self.values.append(monitor_dict[(device_id, output_id)])
        self.trace_names = self.monitors.get_signal_names()[0]

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        spin_value = self.spin.GetValue()
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_add_monitor_button(self, event):
        """Handle the event when user clicks "add" """
        mon_choice_name = self.add_monitor_choice.GetValue()
        if mon_choice_name not in self.sig_n_mons:
            return ''
        self.canvas.render('Add: '+str(mon_choice_name))

        device_id = self.names.query(mon_choice_name)
        output_id = None
        self.monitors.make_monitor(device_id, output_id)
        self.run_network_and_get_values()

        self.sig_n_mons.remove(mon_choice_name)
        self.sig_mons.append(mon_choice_name)
        self.add_monitor_choice.SetItems(self.sig_n_mons)
        self.remove_monitor_choice.SetItems(self.sig_mons)
        if self.sig_n_mons:
            self.add_monitor_choice.SetValue(self.sig_n_mons[0])
        if self.sig_mons:
            self.remove_monitor_choice.SetValue(self.sig_mons[0])
        self.canvas.render('')

    def on_remove_monitor_button(self, event):
        """Handle the event when user clicks "add" """
        mon_choice_name = self.remove_monitor_choice.GetValue()
        if mon_choice_name not in self.sig_mons:
            return ''
        self.canvas.render('Remove: '+str(mon_choice_name))

        device_id = self.names.query(mon_choice_name)
        output_id = None
        self.monitors.remove_monitor(device_id, output_id)
        self.run_network_and_get_values()

        self.sig_n_mons.append(mon_choice_name)
        self.sig_mons.remove(mon_choice_name)

        self.add_monitor_choice.SetItems(self.sig_n_mons)
        self.remove_monitor_choice.SetItems(self.sig_mons)
        if self.sig_n_mons:
            self.add_monitor_choice.SetValue(self.sig_n_mons[0])
        if self.sig_mons:
            self.remove_monitor_choice.SetValue(self.sig_mons[0])
        self.canvas.render('')



"""
path = None
names = Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)

#scanner = Scanner(path, names)
#parser = Parser(names, devices, network, monitors, scanner)

app = wx.App()
gui = Gui("Logic Simulator", path, names, devices, network, monitors)
gui.Show(True)
app.MainLoop()
"""