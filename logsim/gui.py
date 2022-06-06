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
import time

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from graph import Graph


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

    render_display(self, text): Draws the home screen.

    render(self, text): Decides which page to render and calls the relevant
                        method.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    render_help(self): Renders the help page.

    render_cnf(self): Renders the CNF page.
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
        self.oscillating = False
        self.not_connected = False

        # (home, help, cnf, logic)
        self.screen_type = (1, 0, 0, 0)

        # Set colour palette
        self.bkgd_colour = (0.1, 0.1, 0.1)
        self.line_colour = (0.9, 0.5, 0.1)
        self.text_colour = (0.8, 0.8, 0.8)
        self.axes_colour = (0.5, 0.5, 0.5)

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
        if not self.IsShownOnScreen():
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
        """Draw axis for a given signal output."""
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
        """Draw a signal output trace."""
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
        self.canvas_size = self.GetClientSize()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        if not self.parent.values:
            self.parent.trace_names = ['N/A']
            self.parent.values = [[]]

        display_ys = [self.canvas_size[1] - 100 - 80 * j for j in
                      range(len(self.parent.values))]
        display_x = 120
        signal_no = len(self.parent.trace_names)

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw title
        title_text = "Monitored Signal Display"
        self.render_text(title_text, 10, self.canvas_size[1] - 20, title=True)

        if self.not_connected:
            self.render_text('Not all inputs connected...', 10,
                             self.canvas_size[1] - 60)
        elif self.oscillating:
            self.render_text('Network Oscillating...', 10,
                             self.canvas_size[1] - 60)
        else:
            for j in range(signal_no):
                self.render_trace(display_x, display_ys[j],
                                  self.parent.values[j],
                                  self.parent.trace_names[j])
                self.render_graph_axes(display_x, display_ys[j])

        GL.glFlush()
        if self.IsShownOnScreen():
            self.SwapBuffers()

    def render(self, text):
        """Decide which screen type to render and render it."""
        if self.screen_type[1]:
            self.render_help()
        elif self.screen_type[0]:
            self.render_display(text)
        elif self.screen_type[2]:
            self.render_cnf()
        else:
            self.render_logic()

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
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.pan_x += event.GetX() - self.last_mouse_x
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation():
            self.pan_y -= event.GetWheelRotation()
            self.init = False
            text = ""

        self.pan_y = max(0, self.pan_y)
        self.pan_x = min(0, self.pan_x)
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
        """Render the help screen."""
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.SetCurrent(self.context)
        self.canvas_size = self.GetClientSize()

        if not self.help_text:
            try:
                with open('logsim/help.txt', 'r') as f:
                    self.help_text = f.readlines()
            except FileNotFoundError:
                with open('help.txt', 'r') as f:
                    self.help_text = f.readlines()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.render_text('Help Page:', 10, self.canvas_size[1] - 20, True)
        self.render_text("".join(self.help_text), 10, self.canvas_size[1] - 30)
        GL.glFlush()
        self.SwapBuffers()

    def render_cnf(self, line_gap=60):
        """Render the CNF screen."""
        self.canvas_size = self.GetClientSize()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.render_text('Conjunctive Normal Form Converter:', 10,
                         self.canvas_size[1] - 20, True)

        if len(self.parent.sig_mons) == 0:
            self.render_text('Please monitor at least one signal.', 10,
                             self.canvas_size[1] - 50)
            GL.glFlush()
            self.SwapBuffers()
            return ''

        elif self.not_connected:
            self.render_text('Not all device inputs connected.', 10,
                             self.canvas_size[1] - 50)
            GL.glFlush()
            self.SwapBuffers()
            return ''

        mon_name = self.parent.sig_mons[0]
        self.render_text(
            'Monitor to expand: ' + mon_name + '   (top monitor on '
                                               'home page)', 10,
            self.canvas_size[1] - 50)
        bool_exp = self.parent.graph.create_boolean_from_monitor(mon_name)
        if not bool_exp:
            self.render_text('Flip-Flop or circular definition in graph, try '
                             'a different logic circuit', 10,
                             self.canvas_size[1] - 50 - line_gap)
            GL.glFlush()
            self.SwapBuffers()
            return ''

        extra_lines = 0
        bool_exp_show, new_extra_lines = \
            self.parent.graph.add_new_line_breaks(bool_exp)
        self.render_text(
            bool_exp_show + '\n \t\t(boolean expression) \t\t '
            '(XOR = *,  AND = ., OR = +, NOT = ¬)', 10, self.canvas_size[1] -
            30 - line_gap - extra_lines * 20
            )
        extra_lines += new_extra_lines

        bool_exp2 = self.parent.graph.expand_xors(bool_exp)
        bool_exp2 = self.parent.graph.demorgan_push(bool_exp2)
        bool_exp_show, new_extra_lines = \
            self.parent.graph.add_new_line_breaks(bool_exp2)
        self.render_text(bool_exp_show + '\n \t\t(expand XORs to ANDs/ORs)',
                         10,
                         self.canvas_size[1] - 30 - line_gap * 2 -
                         extra_lines * 20)
        extra_lines += new_extra_lines

        bool_exp3 = self.parent.graph.distribute_ors(bool_exp2)
        bool_exp4 = self.parent.graph.clean_up_to_cnf(bool_exp3)
        bool_exp_show, new_extra_lines = \
            self.parent.graph.add_new_line_breaks(bool_exp4)
        self.render_text(
            bool_exp_show[1:-1] + '\n \t\t(distribute ORs over ANDs'
                                  ' and cleanup brackets (CNF))',
            10, self.canvas_size[1] - 30 - line_gap * 3 -
            extra_lines * 20)
        extra_lines += new_extra_lines

        bool_exp5 = self.parent.graph.in_clause_clean_up(bool_exp4)
        bool_exp_show, new_extra_lines = \
            self.parent.graph.add_new_line_breaks(bool_exp5)
        self.render_text(bool_exp_show[1:-1] + '\n \t\t(destroy trivial '
                                               'in-clause redundancy)', 10,
                         self.canvas_size[1] -
                         30 - line_gap * 4 - extra_lines * 20)
        extra_lines += new_extra_lines

        bool_exp6 = self.parent.graph.out_clause_clean_up(bool_exp5)
        bool_exp_show, new_extra_lines = \
            self.parent.graph.add_new_line_breaks(bool_exp6)
        self.render_text(bool_exp_show[1:-1] + '\n \t\t(destroy clause-level'
                                               ' redundancy)', 10,
                         self.canvas_size[1] -
                         30 - line_gap * 5 - extra_lines * 20)
        extra_lines += new_extra_lines

        GL.glFlush()
        self.SwapBuffers()

    def build_logic_file(self):
        """Build new logic description file."""
        device_ids = self.parent.devices.find_devices()
        device_print = ''

        for i in range(len(device_ids)):
            device = self.parent.devices.get_device(device_ids[i])
            dev_type = self.parent.names.names[device.device_kind]
            device_print += '\n' + dev_type
            if dev_type == 'SWITCH':
                device_print += ', ' + str(int(
                    self.parent.devices.get_switch_value(device_ids[i])))
            elif dev_type in ('AND', 'OR', 'NOR', 'NAND'):
                device_print += ', '+str(len(device.inputs))
            device_print += ' = ' + self.parent.names.names[device_ids[i]] + \
                            ';'
        device_print += '\nEND\n'

        out_string = 'DEVICES'
        out_string += device_print
        out_string += '\nCONNECTIONS\n'
        out_string += ';\n'.join(self.parent.con_names)
        out_string += ';\nEND\n\nMONITOR\n'
        out_string += ';\n'.join(self.parent.sig_mons)
        out_string += ';\nEND\n\nMAIN_END'
        return out_string

    def render_logic(self):
        """Render the new logic description file screen."""
        self.canvas_size = self.GetClientSize()

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.render_text(self.build_logic_file(), 10, self.canvas_size[1] - 20)
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
    reset_screen(self): Resets the screen to initial position and zoom.

    toolbar_handler(self, event): Handles toolbar presses.

    on_switch_choice(self, event): Handles switch choices.

    on_switch_set(self, event): Handles switch set changes.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                 button.

    on_continue_button(self, event): Event handler for when the user clicks the
                                    continue button.

    run_network_and_get_values(self): Executes the network for and stores the
                                    values and signal names.

    on_add_monitor_button(self, event): Event handler for when the user clicks
                    the add-monitor button.

    on_remove_monitor_button(self, event): Event handler for when the user
                    clicks the remove-monitor button.

    on_add_connection_button(self, event): Event handler for when the user
                    decides to add a connection.

    on_remove_connection_button(self, event): Event handler for when the user
                    decides to remove a connection.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))
        self.quit_id = 999
        self.open_id = 998
        self.help_id = 997
        self.home_id = 996
        self.cnf_id = 995
        self.logic_id = 994

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
        self.graph = Graph(self.names, self.devices, self.network,
                           self.monitors)

        self.switch_ids = self.devices.find_devices(self.devices.SWITCH)
        self.switch_names = [self.names.get_name_string(i) for i in
                             self.switch_ids]
        self.switch_values = [self.devices.get_switch_value(i) for i in
                              self.switch_ids]
        self.sig_mons, self.sig_n_mons = self.monitors.get_signal_names()

        # Setup Add/Remove connection section of the display
        self.all_input_ids, self.all_input_names = \
            self.monitors.get_input_ids_and_names()
        self.input_connected = [(self.network.get_connected_output(device_id,
                                                                   input_id)
                                 is not None) for (device_id, input_id) in
                                self.all_input_ids]

        self.con_ids, self.con_names = \
            self.monitors.get_connection_ids_and_names()
        self.con_strts = self.sig_mons[:] + self.sig_n_mons[:]
        input_number = len(self.all_input_names)
        self.con_ends = [self.all_input_names[i] for i in range(input_number)
                         if not self.input_connected[i]]

        # Toolbar setup
        toolbar = self.CreateToolBar()
        myimage = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR)
        toolbar.AddTool(self.home_id, "Home", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_FLOPPY, wx.ART_TOOLBAR)
        toolbar.AddTool(self.logic_id, "Logic Description", myimage)
        myimage = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE,
                                           wx.ART_TOOLBAR)
        toolbar.AddTool(self.cnf_id, "CNF", myimage)
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

        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")

        self.text_switch_control = wx.StaticText(self, wx.ID_ANY, "Switch On:")
        self.switch_choice = wx.ComboBox(self, wx.ID_ANY, "<SWITCH>",
                                         choices=self.switch_names)
        self.switch_choice.SetValue(self.switch_names[0])
        self.switch_set = wx.CheckBox(self, wx.ID_ANY)

        self.text_add_monitor = wx.StaticText(self, wx.ID_ANY,
                                              "Signal Monitors:")

        self.add_monitor_button = wx.Button(self, wx.ID_ANY, "Add")
        self.remove_monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.add_monitor_choice = wx.ComboBox(self, wx.ID_ANY, "<SIGNAL>",
                                              choices=self.sig_n_mons)
        self.remove_monitor_choice = wx.ComboBox(self, wx.ID_ANY, "<SIGNAL>",
                                                 choices=self.sig_mons)
        if len(self.sig_n_mons):
            self.add_monitor_choice.SetValue(self.sig_n_mons[0])
        if len(self.sig_mons):
            self.remove_monitor_choice.SetValue(self.sig_mons[0])

        self.text_connection_monitor = wx.StaticText(self, wx.ID_ANY,
                                                     "Circuit Connections:")

        self.add_connection_button = wx.Button(self, wx.ID_ANY, "Add")
        self.remove_connection_button = wx.Button(self, wx.ID_ANY, "Remove")
        self.add_connection_strt_choice = wx.ComboBox(self, wx.ID_ANY,
                                                      "<CON.STRT>",
                                                      choices=self.con_strts)
        self.add_connection_end_choice = wx.ComboBox(self, wx.ID_ANY,
                                                     "<CON.END>",
                                                     choices=self.con_ends)
        self.remove_connection_choice = wx.ComboBox(self, wx.ID_ANY,
                                                    "<CON>",
                                                    choices=self.con_names)
        if len(self.con_strts):
            self.add_connection_strt_choice.SetValue(self.con_strts[0])
        if len(self.con_ends):
            self.add_connection_end_choice.SetValue(self.con_ends[0])
        if len(self.con_names):
            self.remove_connection_choice.SetValue(self.con_names[0])

        # Bind events to widgets
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)

        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.add_monitor_button.Bind(wx.EVT_BUTTON, self.on_add_monitor_button)
        self.remove_monitor_button.Bind(wx.EVT_BUTTON,
                                        self.on_remove_monitor_button)
        self.add_connection_button.Bind(wx.EVT_BUTTON,
                                        self.on_add_connection_button)
        self.remove_connection_button.Bind(wx.EVT_BUTTON,
                                           self.on_remove_connection_button)
        self.switch_choice.Bind(wx.EVT_COMBOBOX, self.on_switch_choice)
        self.switch_set.Bind(wx.EVT_CHECKBOX, self.on_switch_set)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer7 = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text_cycles, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer3, 1, wx.ALL, 5)
        side_sizer3.Add(self.run_button, 1, wx.ALL, 5)

        side_sizer3.Add(self.continue_button, 1, wx.ALL, 5)

        side_sizer.Add(self.text_switch_control, 1, wx.ALL, 10)
        side_sizer.Add(side_sizer4, 1, wx.ALL, 5)
        side_sizer4.Add(self.switch_choice, 1, wx.ALL, 5)
        side_sizer4.Add(self.switch_set, 1, wx.ALL, 5)

        side_sizer.Add(self.text_add_monitor, 1, wx.ALL, 10)
        side_sizer.Add(side_sizer1, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer2, 1, wx.ALL, 5)

        side_sizer1.Add(self.add_monitor_choice, 1, wx.ALL, 5)
        side_sizer1.Add(self.add_monitor_button, 1, wx.ALL, 5)
        side_sizer2.Add(self.remove_monitor_choice, 1, wx.ALL, 5)
        side_sizer2.Add(self.remove_monitor_button, 1, wx.ALL, 5)

        side_sizer.Add(self.text_connection_monitor, 1, wx.ALL, 10)
        side_sizer.Add(side_sizer5, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer6, 1, wx.ALL, 5)
        side_sizer.Add(side_sizer7, 1, wx.ALL, 5)

        side_sizer5.Add(self.add_connection_strt_choice, 1, wx.ALL, 5)
        side_sizer5.Add(self.add_connection_end_choice, 1, wx.ALL, 5)
        side_sizer6.Add(self.add_connection_button, 1, wx.ALL, 5)
        side_sizer7.Add(self.remove_connection_choice, 1, wx.ALL, 5)
        side_sizer7.Add(self.remove_connection_button, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

        self.run_network_and_get_values()
        self.canvas.render('')

    def reset_screen(self):
        """Put screen back into its initial state."""
        self.canvas.pan_x = 0
        self.canvas.pan_y = 0
        self.canvas.zoom = 1
        self.canvas.init = False

    def toolbar_handler(self, event):
        """Handle toolbar presses."""
        if event.GetId() == self.quit_id:
            canc = wx.MessageBox('Are you sure you would like to quit?',
                                 'Quit?', wx.ICON_INFORMATION | wx.CANCEL)
            if canc == 4:
                self.Close(True)
        elif event.GetId() == self.open_id:
            openFileDialog = wx.FileDialog(self, "Open txt file", "", "",
                                           wildcard="TXT files (*.txt)|*.txt",
                                           style=wx.FD_OPEN +
                                                 wx.FD_FILE_MUST_EXIST)
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
            self.canvas.screen_type = (0, 1, 0, 0)
            self.canvas.render('')
        elif event.GetId() == self.home_id:
            self.reset_screen()
            self.canvas.screen_type = (1, 0, 0, 0)
            self.canvas.render('')
        elif event.GetId() == self.cnf_id:
            self.reset_screen()
            self.canvas.screen_type = (0, 0, 1, 0)
            self.canvas.render('')
        elif event.GetId() == self.logic_id:
            self.reset_screen()
            self.canvas.screen_type = (0, 0, 0, 1)
            self.canvas.render('')

    def on_switch_choice(self, event):
        """Handle the new-switch-choice event."""
        sw_name = self.switch_choice.GetValue()
        sw_val = self.switch_values[self.switch_names.index(sw_name)]
        if sw_val:
            self.switch_set.SetValue(1)
        else:
            self.switch_set.SetValue(0)

    def on_switch_set(self, event):
        """Handle the switch-set event."""
        sw_name = self.switch_choice.GetValue()
        sw_no = self.switch_names.index(sw_name)
        self.switch_values[sw_no] = [0, 1][self.switch_set.GetValue()]
        sw_id = self.names.query(sw_name)
        self.devices.set_switch(sw_id, self.switch_set.GetValue())
        self.run_network_and_get_values()
        self.canvas.render('')

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
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

        text = "Continue button pressed. (time_steps=%d)" % self.time_steps
        self.canvas.render(text)

    def run_network_and_get_values(self):
        """Run the network and get the monitored signal values."""
        self.canvas.not_connected = not self.network.check_network()
        if self.canvas.not_connected:
            return ''
        self.devices.cold_startup()
        self.monitors.reset_monitors()
        osc_here = False
        for i in range(self.time_steps):
            if not self.network.execute_network():
                self.canvas.oscillating = True
                osc_here = True
            self.monitors.record_signals()
        if not osc_here:
            self.canvas.oscillating = False
        self.values = []

        monitor_dict = self.monitors.monitors_dictionary
        for device_id, output_id in monitor_dict:
            self.values.append(monitor_dict[(device_id, output_id)])
        self.trace_names = self.monitors.get_signal_names()[0]

    def on_add_monitor_button(self, event):
        """Handle the event when user decides to add a monitor."""
        mon_choice_name = self.add_monitor_choice.GetValue()
        if '.' in mon_choice_name:
            dot_index = mon_choice_name.index('.')
            output_id = self.names.query(mon_choice_name[dot_index + 1:])
            mon_choice_name_strt = mon_choice_name[:dot_index]
        else:
            mon_choice_name_strt = mon_choice_name
            output_id = None

        if mon_choice_name not in self.sig_n_mons:
            return ''
        self.canvas.render('Add: ' + str(mon_choice_name))

        device_id = self.names.query(mon_choice_name_strt)
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
        """Handle the event when user decides to remove a monitor."""
        mon_choice_name = self.remove_monitor_choice.GetValue()
        if '.' in mon_choice_name:
            dot_index = mon_choice_name.index('.')
            output_id = self.names.query(mon_choice_name[dot_index + 1:])
            mon_choice_name_strt = mon_choice_name[:dot_index]
        else:
            mon_choice_name_strt = mon_choice_name
            output_id = None

        if mon_choice_name not in self.sig_mons:
            return ''
        self.canvas.render('Remove: ' + str(mon_choice_name))

        device_id = self.names.query(mon_choice_name_strt)
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

    def on_add_connection_button(self, event):
        """Handle the event when user wants to add a connection."""
        out_name = self.add_connection_strt_choice.GetValue()
        in_name = self.add_connection_end_choice.GetValue()
        if '.' in out_name:
            dot_index = out_name.index('.')
            out_dev_id = self.names.query(out_name[:dot_index])
            out_port_id = self.names.query(out_name[dot_index+1:])
        else:
            out_dev_id = self.names.query(out_name)
            out_port_id = None
        in_dev_id, in_port_id = self.all_input_ids[
            self.all_input_names.index(in_name)]
        self.network.make_connection(out_dev_id, out_port_id, in_dev_id,
                                     in_port_id)

        self.input_connected = [(self.network.get_connected_output(device_id,
                                                                   input_id)
                                 is not None) for (device_id, input_id) in
                                self.all_input_ids]

        self.con_ids, self.con_names = \
            self.monitors.get_connection_ids_and_names()
        self.con_strts = self.sig_mons[:] + self.sig_n_mons[:]
        input_number = len(self.all_input_names)
        self.con_ends = [self.all_input_names[i] for i in range(input_number)
                         if not self.input_connected[i]]

        self.add_connection_strt_choice.SetItems(self.con_strts)
        self.add_connection_end_choice.SetItems(self.con_ends)
        self.remove_connection_choice.SetItems(self.con_names)

        if len(self.con_strts):
            self.add_connection_strt_choice.SetValue(self.con_strts[0])
        if len(self.con_ends):
            self.add_connection_end_choice.SetValue(self.con_ends[0])
        if len(self.con_names):
            self.remove_connection_choice.SetValue(self.con_names[0])

        self.run_network_and_get_values()
        self.canvas.render('')

    def on_remove_connection_button(self, event):
        """Handle the event when the user wants to remove a connection."""

        con_name = self.remove_connection_choice.GetValue()

        con_id = self.con_ids[self.con_names.index(con_name)][1]

        self.network.delete_connection(con_id[0], con_id[1])

        self.input_connected = [(self.network.get_connected_output(device_id,
                                                                   input_id)
                                 is not None) for (device_id, input_id) in
                                self.all_input_ids]

        self.con_ids, self.con_names = \
            self.monitors.get_connection_ids_and_names()
        self.con_strts = self.sig_mons[:] + self.sig_n_mons[:]
        input_number = len(self.all_input_names)
        self.con_ends = [self.all_input_names[i] for i in range(input_number)
                         if not self.input_connected[i]]

        self.add_connection_strt_choice.SetItems(self.con_strts)
        self.add_connection_end_choice.SetItems(self.con_ends)
        self.remove_connection_choice.SetItems(self.con_names)

        if len(self.con_strts):
            self.add_connection_strt_choice.SetValue(self.con_strts[0])
        if len(self.con_ends):
            self.add_connection_end_choice.SetValue(self.con_ends[0])
        if len(self.con_names):
            self.remove_connection_choice.SetValue(self.con_names[0])

        self.run_network_and_get_values()
        self.canvas.render('')
