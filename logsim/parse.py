"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

# Tasks to be done 
# Repeated semicolons to give just on error message
# Implement devices, connections, monitors, network
# Fix next_scan_start
from scanner import Symbol


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
    copy_symbol(self): Returns a copy Symbol class instance of the current symbol

    inline_error_message(self, symbol = None): 

    display_syntax_error(self,error_id): 

    display_devices_error(self,error_id, device_name_symbol, device_type_symbol, device_parameter_symbol): 

    display_connect_error(self, error_id, output_device_symbol, output_symbol, input_device_symbol, input_symbol): 

    display_monitors_error(self,error_id, monitor_symbol, monitor_output_symbol): 

    next_symbol(self): 

    next_scan_start(self, in_block = True): 

    parse_devices(self): Parses the 'DEVICES' block of definition file

    parse_connections(self): Parses the 'CONNECTIONS' block of definition file

    parse_monitor(self): Parses the 'MONITORS' block of definition file

    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner, test = False):
        """Initialise parser errors and constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.current_symbol = None
        self.parse_completion = [False, False, False]
        self.test = test

        # Error codes are for all syntax errors as well as the error for an incomplete network
        self.ERROR_ID = [
            self.EXTRA_SEMICOLON, 
            self.EXTRA_DEVICES, 
            self.EXTRA_CONNECT,
            self.EXTRA_MONITOR, 
            self.NO_NUMBER, 
            self.NO_SEMICOLON, 
            self.INVALID_DEVICENAME,
            self.NO_EQUALS, 
            self.NO_END, 
            self.INVALID_DEVICETYPE, 
            self.INVALID_OUTPUTLABEL,
            self.NO_DOT, 
            self.NO_DASH, 
            self.EXPECT_DEVICES, 
            self.EXPECT_CONNECT,
            self.EXPECT_MONITOR, 
            self.NO_MAIN_END,
            self.NOT_EXPECT_END, 
            self.INVALID_INPUTLABEL,
            self.INCOMPLETE_NETWORK
        ] = self.names.unique_error_codes(20)

        self.error_count = 0

    def copy_symbol(self):
        """Returns a copy Symbol class instance of the current symbol"""
        symbol = Symbol()
        symbol.type = int(self.current_symbol.type)
        symbol.id = int(self.current_symbol.id)
        symbol.line = int(self.current_symbol.line)
        symbol.position_in_line = int(self.current_symbol.position_in_line)
        return symbol

    def inline_error_message(self, symbol = None):
        """Calls to the scanner to print an error message at the right location"""
        if not symbol:
            self.scanner.print_location(self.current_symbol)
        else:
            self.scanner.print_location(symbol)

    def display_syntax_error(self,error_id):
        """Handles all error messaging for all parser errors"""
        print("Errors found so far :", self.error_count + 1)
        if error_id == self.EXTRA_SEMICOLON:
            print("ERROR: Extra semicolons added")
            if not self.test:
                self.inline_error_message()
            self.error_count += 1

        elif error_id == self.EXTRA_DEVICES:
            print("ERROR : DEVICES already called")
            if not self.test:
                self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_CONNECT:
            print("ERROR : CONNECTIONS already Called")
            if not self.test:
                self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_MONITOR:
            print("ERROR : MONITOR already called")
            if not self.test:
                self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.NO_NUMBER:
            self.error_count += 1
            print("ERROR : Not a number")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_SEMICOLON:
            self.error_count += 1
            print("ERROR : Expected a semicolon here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.INVALID_DEVICENAME:
            self.error_count += 1
            print("ERROR : Not a valid device name")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_EQUALS:
            self.error_count += 1
            print("ERROR : Expected an equals sign here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_END:
            self.error_count += 1
            print("ERROR : Expected an 'END' statement")
            if not self.test:
                self.inline_error_message()

        elif error_id == self.INVALID_DEVICETYPE:
            self.error_count += 1
            print("ERROR : Not a valid supported device type")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.INVALID_OUTPUTLABEL:
            self.error_count += 1
            print("ERROR : Not a valid type of output label")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_DOT:
            self.error_count += 1
            print("ERROR : Expected a dot here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_DASH:
            self.error_count += 1
            print("ERROR : Expected a dash here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.EXPECT_DEVICES:
            self.error_count += 1
            print("ERROR : Expected a 'DEVICES' statement here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_CONNECT:
            self.error_count += 1
            print("ERROR : Expected a 'CONNECTIONS' statement here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_MONITOR:
            self.error_count += 1
            print("ERROR : Expected a 'MONITOR' statement here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.NO_MAIN_END:
            self.error_count += 1
            print("ERROR : Expected a 'MAIN_END' statement here")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.NOT_EXPECT_END:
            self.error_count += 1
            print("ERROR : Unexpected 'END' statement")
            if not self.test:
                self.inline_error_message()
            self.next_symbol()
            self.next_scan_start()

        elif error_id == self.INVALID_INPUTLABEL:
            self.error_count += 1
            print("ERROR : Invalid input label")
            if not self.test:
                self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.INCOMPLETE_NETWORK:
            self.error_count += 1
            print("ERROR : Not all inputs are connected")

        else:
            self.error_count += 1
            print('Unregistered error id in parser code', error_id)

    def display_devices_error(
        self,
        error_id,
        device_name_symbol,
        device_type_symbol,
        device_parameter_symbol
    ):
        """Return error messages for devices errors."""
        print("Errors found so far :", self.error_count + 1)
        if error_id == self.devices.DEVICE_PRESENT:
            print("ERROR : Device by this name already exists")
            self.inline_error_message(device_name_symbol)
            self.error_count += 1

        elif error_id == self.devices.NO_QUALIFIER:
            print("ERROR : No qualifier given and device type requires one")
            self.inline_error_message(device_type_symbol)
            self.error_count += 1

        elif error_id == self.devices.INVALID_QUALIFIER:
            print("ERROR : Qualifier is invalid for device type")
            self.inline_error_message(device_parameter_symbol)
            self.error_count += 1

        elif error_id == self.devices.QUALIFIER_PRESENT:
            print("ERROR : Qualifier not valid with device type")
            self.inline_error_message(device_parameter_symbol)
            self.error_count += 1

        elif error_id == self.devices.BAD_DEVICE:
            print("ERROR : Device Type given is not a valid device type")
            self.inline_error_message(device_type_symbol)
            self.error_count += 1

        else:
            self.error_count += 1
            print("ERROR : Unregistered error id in parser code", error_id)

    def display_connect_error(
        self,
        error_id,
        output_device_symbol,
        output_symbol,
        input_device_symbol,
        input_symbol,
    ):
        """ Return error messages for connection errors."""
        print("Errors found so far :", self.error_count + 1)
        if error_id == self.network.DEVICE_ABSENT_ONE:
            print("ERROR : Device name does not exist")
            self.inline_error_message(output_device_symbol)
            self.error_count += 1

        elif error_id == self.network.DEVICE_ABSENT_TWO:
            print("ERROR : Device name does not exist")
            self.inline_error_message(input_device_symbol)
            self.error_count += 1

        elif error_id == self.network.INPUT_CONNECTED:
            print("ERROR : Input is already connected")
            self.inline_error_message(input_symbol)
            self.error_count += 1

        elif error_id == self.network.INPUT_TO_INPUT:
            print("ERROR : Cannot connect an input to an input")
            self.inline_error_message(output_symbol)
            self.error_count += 1

        elif error_id == self.network.PORT_ABSENT:
            print("ERROR : Port does not exist")
            self.inline_error_message(output_device_symbol)
            self.error_count += 1

        elif error_id == self.network.OUTPUT_TO_OUTPUT:
            print("ERROR : Cannot Connect output to output")
            self.inline_error_message(input_device_symbol)
            self.error_count += 1

        else:
            self.error_count += 1
            print("ERROR : Unregistered error id in parser code", error_id)

    def display_monitors_error(
        self,
        error_id,
        monitor_symbol,
        monitor_output_symbol
        ):
        """Return error messages for monitor errors."""
        print("Errors found so far :", self.error_count + 1)
        if error_id == self.monitors.NOT_OUTPUT:
            print("ERROR : Can only monitor outputs")
            self.inline_error_message(monitor_symbol)
            self.error_count += 1

        elif error_id == self.monitors.MONITOR_PRESENT:
            print("ERROR : Output already being monitored")
            self.inline_error_message(monitor_symbol)
            self.error_count += 1

        elif error_id == self.monitors.network.DEVICE_ABSENT:
            print("ERROR : Device does not exist")
            self.inline_error_message(monitor_symbol)
            self.error_count += 1

        else:
            self.error_count += 1
            print("Unregistered error id in parser code", error_id)
            print(self.monitors.MONITOR_PRESENT)

    def next_symbol(self):
        """Changes current symbol to next symbol from scanner"""
        self.current_symbol = self.scanner.get_symbol()

    def next_scan_start(self, in_block = True):
        """Reaches a safe symbol to resume parsing after an error
        
        Keyword Argument
        in_block = True if stopping symbol is mainly semicolon
                   False if stopping symbol is mainly END
        """
        safe_start = False
        while not safe_start:
            if self.current_symbol.type == self.scanner.SEMICOLON and in_block:
                self.next_symbol()
                while self.current_symbol.type == self.scanner.SEMICOLON:
                    #SYNTAX WARNING (extra semicolons added) IMPLEMENTED
                    self.display_syntax_error(self.EXTRA_SEMICOLON)
                    self.next_symbol()
                safe_start = True
            elif self.current_symbol.type == self.scanner.EOF:
                safe_start = True
            elif self.current_symbol.type == self.scanner.KEYWORD:
                if self.current_symbol.id == self.scanner.END_ID and not in_block:
                    #SYNTAX ERROR (Unexpected END) IMPLEMENTED
                    self.display_syntax_error(self.NOT_EXPECT_END)
                elif not in_block:
                    if self.current_symbol.id == self.scanner.DEVICES_ID:
                        if not self.parse_completion[0]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (DEVICES ALREADY CALLED) IMPLEMENTED
                            self.display_syntax_error(self.EXTRA_DEVICES)
                    elif self.current_symbol.id == self.scanner.CONNECT_ID:
                        if not self.parse_completion[1]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (CONNECTIONS ALREADY CALLED) IMPLEMENTED
                            self.display_syntax_error(self.EXTRA_CONNECT)
                    elif self.current_symbol.id == self.scanner.MONITOR_ID:
                        if not self.parse_completion[2]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (MONITOR ALREADY CALLED) IMPLEMENTED
                            self.display_syntax_error(self.EXTRA_MONITOR)
                elif self.current_symbol.id == self.scanner.END_ID and in_block:
                    safe_start = True
                else:
                    safe_start = True
                    self.next_symbol()
            else:
                self.next_symbol()
        return

    def parse_devices(self):
        """Parses the 'DEVICES' block of definition file"""
        self.parse_completion[0] = True
        while self.current_symbol.type == self.scanner.NAME:
            ###
            device_type_symbol = self.copy_symbol()
            device_parameter_symbol = Symbol()
            ###
            self.next_symbol()
            expect_equals = True
            if self.current_symbol.type == self.scanner.COMMA:
                expect_equals = False
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NUMBER:
                    ##
                    device_parameter_symbol = self.copy_symbol()
                    ##
                    self.next_symbol()
                    expect_equals = True
                else:
                    #SYNTAX ERROR (Expected a number here) IMPLEMENTED
                    self.display_syntax_error(self.NO_NUMBER)

            if self.current_symbol.type == self.scanner.EQUALS and expect_equals:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    ##
                    device_name_symbol = self.copy_symbol()
                    ##
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.SEMICOLON:
                        self.next_symbol()
                        #
                        if self.error_count == 0 and not self.test:
                            error_type = self.devices.make_device(device_name_symbol.id, 
                                                                device_type_symbol.id, 
                                                                device_property=device_parameter_symbol.id)
                            if error_type == self.devices.NO_ERROR:
                                pass
                            else:
                                '''SEMANTIC ERROR to be implemented'''
                                self.display_devices_error(error_type, 
                                                           device_name_symbol, 
                                                           device_type_symbol, 
                                                           device_parameter_symbol)
                        ##
                    else:
                        #SYNTAX ERROR MESSAGE (Expected a semicolon) IMPLEMENTED
                        self.display_syntax_error(self.NO_SEMICOLON)
                else:
                    #SYNTAX ERROR MESSAGE (Expected an alphanumeric string for device name) IMPLEMENTED
                    self.display_syntax_error(self.INVALID_DEVICENAME)
            elif not expect_equals:
                pass
            else:
                #SYNTAX ERROR MESSAGE (Expected equals sign here) IMPLEMENTED    
                self.display_syntax_error(self.NO_EQUALS)
                            
        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
                self.display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
            self.display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            #SYNTAX ERROR MESSAGE (EXTRA SEMICOLONS) IMPLEMENTED
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self.display_syntax_error(self.EXTRA_SEMICOLON)
                self.next_symbol()
            self.parse_devices()

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Type) IMPLEMENTED
            self.display_syntax_error(self.INVALID_DEVICETYPE)
            self.parse_devices()

    def parse_connections(self):
        """Parses the 'CONNECTIONS' block of definition file"""
        self.parse_completion[1] = True
        while self.current_symbol.type == self.scanner.NAME:
            ##
            output_device_symbol = self.copy_symbol()
            output_symbol = Symbol()
            ##
            self.next_symbol()
            expect_dash = True
            if self.current_symbol.type == self.scanner.DOT:
                expect_dash = False
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    ##
                    output_symbol = self.copy_symbol()
                    ##
                    self.next_symbol()
                    expect_dash = True
                else:
                    # SYNTAX ERROR (Invalid output label) IMPLEMENTED
                    self.display_syntax_error(self.INVALID_OUTPUTLABEL)

            #print(expect_dash, self.current_symbol.type, self.scanner.DASH)
            if self.current_symbol.type == self.scanner.DASH and expect_dash:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    ##
                    input_device_symbol = self.copy_symbol()
                    ##
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.DOT:
                        self.next_symbol()
                        if self.current_symbol.type == self.scanner.NAME:
                            ##
                            input_symbol = self.copy_symbol()
                            ##
                            self.next_symbol()
                            if self.current_symbol.type == self.scanner.SEMICOLON:
                                self.next_symbol()
                                ##
                                if self.error_count == 0 and not self.test:
                                    error_type = self.network.make_connection(output_device_symbol.id, 
                                                                            output_symbol.id, 
                                                                            input_device_symbol.id,
                                                                            input_symbol.id)
                                    if error_type == self.network.NO_ERROR:
                                        pass
                                    else:
                                        '''SEMANTIC ERROR to be implemented'''
                                        self.display_connect_error(error_type, 
                                                                   output_device_symbol, 
                                                                   output_symbol, 
                                                                   input_device_symbol, 
                                                                   input_symbol)
                                ##
                            else:
                                # SYNTAX ERROR (Expected a semicolon here) IMPLEMENTED
                                self.display_syntax_error(self.NO_SEMICOLON)
                        else:
                            #SYNTAX WARNING (INVALID INPUTLABEL ALREADY CALLED) IMPLEMENTED
                            self.display_syntax_error(self.INVALID_INPUTLABEL)
                    else:
                        # SYNTAX ERROR (Expected a dot here) IMPLEMENTED
                        self.display_syntax_error(self.NO_DOT)
                else:
                    # SYNTAX ERROR (Invalid device name) IMPLEMENTED
                    self.display_syntax_error(self.INVALID_DEVICENAME)
            elif not expect_dash:
                pass
            else:
                # SYNTAX ERROR (Expected dash) IMPLEMENTED
                self.display_syntax_error(self.NO_DASH)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                ## Checking if all inputs are connected
                if not self.network.check_network():
                    self.display_syntax_error(self.INCOMPLETE_NETWORK)
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after CONNECTIONS) IMPLEMENTED
                self.display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
            self.display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            #SYNTAX ERROR MESSAGE (EXTRA SEMICOLONS) IMPLEMENTED
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self.next_symbol()
            self.display_syntax_error(self.EXTRA_SEMICOLON)
            self.parse_devices()

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name) IMPLEMENTED
            self.display_syntax_error(self.INVALID_DEVICENAME)
            self.parse_connections()

    def parse_monitor(self):
        """Parses the 'MONITORS' block of definition file"""
        self.parse_completion[2] = True
        while self.current_symbol.type == self.scanner.NAME:
            monitor_symbol = self.copy_symbol()
            monitor_output_symbol = Symbol()
            self.next_symbol()
            expect_semicolon = True
            if self.current_symbol.type == self.scanner.DOT:
                expect_semicolon = False
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    ##
                    monitor_output_symbol = self.copy_symbol()
                    ##
                    self.next_symbol()
                    expect_semicolon = True
                else:
                    # SYNTAX ERROR (Invalid output label) IMPLEMENTED
                    self.display_syntax_error(self.INVALID_OUTPUTLABEL)
            
            if self.current_symbol.type == self.scanner.SEMICOLON and expect_semicolon:
                self.next_symbol()
                ##
                if self.error_count == 0 and not self.test:
                    error_type = self.monitors.make_monitor(monitor_symbol.id, monitor_output_symbol.id)
                    if error_type == self.monitors.NO_ERROR:
                        pass
                    else:
                        self.display_monitors_error(error_type, 
                                                    monitor_symbol, 
                                                    monitor_output_symbol)
                ##
            elif not expect_semicolon:
                pass
            else:
                # SYNTAX ERROR (Expected semicolon) IMPLEMENTED
                self.display_syntax_error(self.NO_SEMICOLON)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
                self.display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
            self.display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            #SYNTAX ERROR MESSAGE (EXTRA SEMICOLONS) IMPLEMENTED
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self.next_symbol()
            self.display_syntax_error(self.EXTRA_SEMICOLON)
            self.parse_devices()

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name) IMPLEMENTED
            self.display_syntax_error(self.INVALID_DEVICENAME)
            self.parse_monitor()

    def parse_network(self):
        """Parse the circuit definition file.
        
        Returns True if no errors found."""
        self.next_symbol()
        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
            self.next_symbol()
            self.parse_devices()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED DEVICES) IMPLEMENTED
            self.display_syntax_error(self.EXPECT_DEVICES)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                self.next_symbol()
                self.parse_devices()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
            self.next_symbol()
            self.parse_connections()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED CONNECTIONS) IMPLEMENTED
            self.display_syntax_error(self.EXPECT_CONNECT)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                self.next_symbol()
                self.parse_connections()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
            self.next_symbol()
            self.parse_monitor()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED MONITORS) IMPLEMENTED
            self.display_syntax_error(self.EXPECT_MONITOR)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                self.next_symbol()
                self.parse_monitor()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MAIN_END_ID:
            self.successful_parse = True
        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (NO MAIN_END)
            self.display_syntax_error(self.NO_MAIN_END)
        
        if self.error_count > 0:
            return False
        else:
            return True


        '''# For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True'''

