"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.current_symbol = None
        self.successful_parse = True

    def next_symbol(self):
        self.current_symbol = self.scanner.get_symbol()

    def parse_devices(self):
        pass

    def parse_connections(self):
        pass

    def parse_monitor(self):
        pass

    def parse_network(self):
        """Parse the circuit definition file."""
        if False:
            self.next_symbol()
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                self.parse_devices()
                self.next_symbol()
                if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                    self.parse_connections()
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                        self.parse_monitor()
                        self.next_symbol()
                    else:
                        self.successful_parse = False
                        #SYNTAX ERROR MESSAGE
                else:
                    self.successful_parse = False
                    #SYNTAX ERROR MESSAGE
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE
            return self.successful_parse

        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
