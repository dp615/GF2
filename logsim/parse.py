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
        self.parse_completion = [False, False, False]

        self.ERROR_ID = [self.EXTRA_SEMICOLON, self.EXTRA_DEVICES, self.EXTRA_CONNECT,
            self.EXTRA_MONITOR, self.NO_NUMBER, self.NO_SEMICOLON, self.INVALID_DEVICENAME,
            self.NO_EQUALS, self.NO_END, self.INVALID_DEVICETYPE, self.INVALID_OUTPUTLABEL,
            self.NO_DOT, self.NO_DASH, self.EXPECT_DEVICES, self.EXPECT_CONNECT,
            self.EXPECT_MONITOR, self.NO_MAIN_END,self.NOT_EXPECT_END, self.INVALID_INPUTLABEL] = self.names.unique_error_codes(19)

        self.error_count = 0

    # To be completed function to display line with caret pointing to error 
    def inline_error_message(self):
        self.scanner.print_location(self.current_symbol.line,self.current_symbol.position_in_line)

    def display_error(self,error_id):
        if error_id == self.EXTRA_SEMICOLON:
            print("SYNTAX ERROR", error_id,': Extra semicolons added')
            self.inline_error_message()
            self.error_count += 1

        elif error_id == self.EXTRA_DEVICES:
            print("SYNTAX ERROR", error_id,': DEVICES already called')
            self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_CONNECT:
            print("SYNTAX ERROR", error_id,': CONNECTIONS already Called')
            self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_MONITOR:
            print("SYNTAX ERROR", error_id,': MONITOR already called')
            self.inline_error_message()
            self.error_count += 1
            self.next_symbol()
            self.next_scan_start(in_block = False)

        elif error_id == self.NO_NUMBER:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a number")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_SEMICOLON:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a semicolon here")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.INVALID_DEVICENAME:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid device name")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_EQUALS:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected an equals sign here")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_END:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected an 'END' statement")
            self.inline_error_message()

        elif error_id == self.INVALID_DEVICETYPE:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid supported device type")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.INVALID_OUTPUTLABEL:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid type of output label")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_DOT:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a dot here")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.NO_DASH:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a dash here")
            self.inline_error_message()
            self.next_scan_start()

        elif error_id == self.EXPECT_DEVICES:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'DEVICES' statement here")
            self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_CONNECT:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'CONNECTIONS' statement here")
            self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_MONITOR:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'MONITOR' statement here")
            self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.NO_MAIN_END:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'MAIN_END' statement here")
            self.inline_error_message()
            self.next_scan_start(in_block = False)

        elif error_id == self.NOT_EXPECT_END:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Unexpected 'END' statement")
            self.inline_error_message()
            self.next_symbol()
            self.next_scan_start()

        elif error_id == self.INVALID_INPUTLABEL:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Invalid input label")
            self.inline_error_message()
            self.next_scan_start()

        else:
            self.error_count += 1
            print('Unregistered error id in parser code', error_id)


    def next_symbol(self):
        self.current_symbol = self.scanner.get_symbol()

    def repeated_semicolon(self):
        error = False
        while self.current_symbol.type == self.scanner.SEMICOLON:
            self.next_symbol()
            error = True
        if error:
            #SYNTAX WARNING (extra semicolons added) IMPLEMENTED
            self.display_error(self.EXTRA_SEMICOLON)

    def next_scan_start(self, in_block = True):
        safe_start = False
        while not safe_start:
            if self.current_symbol.type == self.scanner.SEMICOLON and in_block:
                self.next_symbol()
                self.repeated_semicolon()
                safe_start = True
            elif self.current_symbol.type == self.scanner.EOF:
                safe_start = True
            elif self.current_symbol.type == self.scanner.KEYWORD:
                if self.current_symbol.id == self.scanner.END_ID and not in_block:
                    #SYNTAX ERROR (Unexpected END) IMPLEMENTED
                    self.display_error(self.NOT_EXPECT_END)
                elif not in_block:
                    if self.current_symbol.id == self.scanner.DEVICES_ID:
                        if not self.parse_completion[0]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (DEVICES ALREADY CALLED) IMPLEMENTED
                            self.display_error(self.EXTRA_DEVICES)
                    elif self.current_symbol.id == self.scanner.CONNECT_ID:
                        if not self.parse_completion[1]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (CONNECTIONS ALREADY CALLED) IMPLEMENTED
                            self.display_error(self.EXTRA_CONNECT)
                    elif self.current_symbol.id == self.scanner.MONITOR_ID:
                        if not self.parse_completion[2]:
                            safe_start = True
                        else:
                            #SYNTAX WARNING (MONITOR ALREADY CALLED) IMPLEMENTED
                            self.display_error(self.EXTRA_MONITOR)
                elif self.current_symbol.id == self.scanner.END_ID and in_block:
                    safe_start = True
                else:
                    safe_start = True
                    self.next_symbol()
            else:
                self.next_symbol()
        return

    def parse_inputlabel(self):
        if self.current_symbol.type == self.scanner.NAME:
            self.next_symbol()
        else:
            #SYNTAX WARNING (INVALID INPUTLABEL ALREADY CALLED) IMPLEMENTED
            self.display_error(self.INVALID_INPUTLABEL)

    def parse_devices(self):
        self.parse_completion[0] = True
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
                    #SYNTAX ERROR (Expected a number here) IMPLEMENTED
                    self.display_error(self.NO_NUMBER)

            if self.current_symbol.type == self.scanner.EQUALS and expect_equals:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAMES:
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.SEMICOLON:
                        self.next_symbol()
                        #Need to add ability to add a device here
                    else:
                        #SYNTAX ERROR MESSAGE (Expected a semicolon) IMPLEMENTED
                        self.display_error(self.NO_SEMICOLON)
                else:
                    #SYNTAX ERROR MESSAGE (Expected an alphanumeric string for device name) IMPLEMENTED
                    self.display_error(self.INVALID_DEVICENAME)
            elif not expect_equals:
                pass
            else:
                #SYNTAX ERROR MESSAGE (Expected equals sign here) IMPLEMENTED    
                self.display_error(self.NO_EQUALS)
                            
        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
                self.display_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Type) IMPLEMENTED
            self.display_error(self.INVALID_DEVICETYPE)
            self.parse_devices()

    def parse_connections(self):
        self.parse_completion[1] = True
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
                    # SYNTAX ERROR (Invalid output label) IMPLEMENTED
                    self.display_error(self.INVALID_OUTPUTLABEL)

            if self.current_symbol.type == self.scanner.DASH and expect_dash:
                self.next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    self.next_symbol()
                    if self.current_symbol.type == self.scanner.DOT:
                        self.next_symbol()
                        self.parse_inputlabel()
                        if self.current_symbol.type == self.scanner.SEMICOLON:
                            self.next_symbol()
                            #need to add ability to add connections
                        else:
                            # SYNTAX ERROR (Expected a semicolon here) IMPLEMENTED
                            self.display_error(self.NO_SEMICOLON)
                    else:
                        # SYNTAX ERROR (Expected a dot here) IMPLEMENTED
                        self.display_error(self.NO_DOT)
                else:
                    # SYNTAX ERROR (Invalid device name) IMPLEMENTED
                    self.display_error(self.INVALID_DEVICENAME)
            elif not expect_dash:
                pass
            else:
                # SYNTAX ERROR (Expected dash) IMPLEMENTED
                self.display_error(self.NO_DASH)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after CONNECTIONS) IMPLEMENTED
                self.display_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name) IMPLEMENTED
            self.display_error(self.INVALID_DEVICENAME)
            self.parse_connections()

    def parse_monitor(self):
        self.parse_completion[2] = True
        while self.current_symbol.type == self.scanner.NAME:
            self.next_symbol()
            expect_semicolon = True
            if self.current_symbol.type == self.scanner.DOT:
                expect_semicolon = False
                self.next_symbol()
                if (self.current_symbol.type == self.scanner.NAME 
                    and self.current_symbol.id in self.dtype_output_ids):
                    self.next_symbol()
                    expect_semicolon = True
                else:
                    # SYNTAX ERROR (Invalid output label) IMPLEMENTED
                    self.display_error(self.INVALID_OUTPUTLABEL)
            
            if self.current_symbol.type == self.scanner.SEMICOLON and expect_semicolon:
                self.next_symbol()
                #Need to implement monitoring here
            elif not expect_semicolon:
                pass
            else:
                # SYNTAX ERROR (Expected semicolon) IMPLEMENTED
                self.display_error(self.NO_SEMICOLON)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                #SYNTAX ERROR MESSAGE (Expected END after devices) IMPLEMENTED
                self.display_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name) IMPLEMENTED
            self.display_error(self.INVALID_DEVICENAME)
            self.parse_monitor()

    def parse_network(self):
        """Parse the circuit definition file."""
        self.next_symbol()
        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
            self.next_symbol()
            self.parse_devices()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED DEVICES) IMPLEMENTED
            self.display_error(self.EXPECT_DEVICES)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                self.next_symbol()
                self.parse_devices()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
            self.next_symbol()
            self.parse_connections()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED CONNECTIONS) IMPLEMENTED
            self.display_error(self.EXPECT_CONNECT)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                self.next_symbol()
                self.parse_connections()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
            self.next_symbol()
            self.parse_monitor()
        else:
            #SYNTAX ERROR MESSAGE (EXPECTED MONITORS) IMPLEMENTED
            self.display_error(self.EXPECT_MONITOR)
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                self.next_symbol()
                self.parse_monitor()

        if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MAIN_END_ID:
            self.successful_parse = True
        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (NO MAIN_END)
            self.display_error(self.NO)
        
        if self.error_count > 0:
            return False
        else:
            return True


        '''# For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True'''
