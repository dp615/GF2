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

    def next_scan_start(self):
        while not (
                self.current_symbol.type == self.scanner.SEMICOLON 
                or self.current_symbol.type == self.scanner.EOF
                or (self.current_symbol.type == self.scanner.KEYWORD
                and self.current_symbol.id == self.scanner.END_ID)
              ):
            self.next_symbol()

    def add_device(self):
        pass

    def add_connection(self):
        pass

    def add_monitor(self):
        pass

    def parse_inputlabel(self):
        self.next_symbol()

    def parse_devices(self):
        while (
                self.current_symbol.type == self.scanner.NAME 
                and (self.current_symbol.id in self.devices.device_types 
                or self.current_symbol.id in self.devices.gate_types)
            ):

            self.next_symbol()
            expect_equals = True
            if self.current_symbol.type == self.scanner.COMMA:
                expect_equals = False
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NUMBER:
                    self.next_symbol()
                    expect_equals = True
                else:
                    self.successful_parse = False
                    #SYNTAX ERROR (Expected a number here)
                    self.next_scan_start()

            if self.current_symbol.type == self.scanner.EQUALS and expect_equals:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAMES:
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.SEMICOLON:
                        self.add_device()
                        #Need to add ability to add a device here
                    else:
                        self.successful_parse = False
                        #SUNTAX ERROR MESSAGE (Expected a semicolon)
                        self.next_scan_start()
                else:
                    self.successful_parse = False
                    #SYNTAX ERROR MESSAGE (Expected an alphanumeric string for device name)
                    self.next_scan_start()
            elif not expect_equals:
                pass
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (Expected equals sign here)     
                self.next_scan_start()
                            
        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.END_ID:
            self.next_symbol()
            return
        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (Unrecognised Device Type)
            self.next_scan_start()

    def parse_connections(self):
        while self.current_symbol.type == self.scanner.NAME:
            self.next_symbol()
            expect_dash = True
            
            if self.current_symbol.type == self.scanner.DOT:
                expect_dash = False
                self.next_symbol()
                if (self.current_symbol.type == self.scanner.NAME 
                    and self.current_symbol.id in self.dtype_output_ids):
                    self.next_symbol()
                    expect_dash = True
                else:
                    self.successful_parse = False
                    self.next_scan_start()
                    # SYNTAX ERROR (Invalid output label)

            if self.current_symbol.type == self.scanner.DASH and expect_dash:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.DOT:
                        self.next_symbol()
                        self.parse_inputlabel()
                        if self.current_symbol.type == self.scanner.SEMICOLON:
                            self.add_connection()
                            #need to add ability to add connections
                        else:
                            self.successful_parse = False
                            self.next_scan_start()
                            # SYNTAX ERROR (Expected a semicolon here) 
                    else:
                        self.successful_parse = False
                        self.next_scan_start()
                        # SYNTAX ERROR (Expected a dot here)
                else:
                    self.successful_parse = False
                    self.next_scan_start()
                    # SYNTAX ERROR (Invalid device name)
            elif not expect_dash:
                pass
            else:
                self.successful_parse = False
                self.next_scan_start()
                # SYNTAX ERROR (Expected dash)

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.END_ID:
            self.next_symbol()
            return

        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name)
            self.next_scan_start()

    def parse_monitor(self):
        pass

    def parse_network(self):
        """Parse the circuit definition file."""
        if False:
            self.next_symbol()
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                self.next_symbol()
                self.parse_devices()
                if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                    self.next_symbol()
                    self.parse_connections()
                    if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                        self.next_symbol()
                        self.parse_monitor()
                    else:
                        self.successful_parse = False
                        #SYNTAX ERROR MESSAGE (NO MONITORS)
                else:
                    self.successful_parse = False
                    #SYNTAX ERROR MESSAGE (NO CONNECTIONS)
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (NO DEVICES)
            return self.successful_parse

        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
