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
        self.parse_completion = [False, False, False]

        self.WARNING_ID = [self.EXTRA_SEMICOLON, self.EXTRA_DEVICES, self.EXTRA_CONNECT,
            self.EXTRA_MONITOR] = self.names.unique_error_codes(4)

        self.ERROR_ID = [self.NO_NUMBER, self.NO_SEMICOLON, self.INVALID_DEVICENAME,
            self.NO_EQUALS, self.NO_END, self.INVALID_DEVICETYPE, self.INVALID_OUTPUTLABEL,
            self.NO_DOT, self.NO_DASH, self.EXPECT_DEVICES, self.EXPECT_CONNECT,
            self.EXPECT_MONITOR, self.EXPECT_MAIN_END] = self.names.unique_error_codes(13)

        self.error_count = 0

    # To be completed function to display line with caret pointing to error 
    def inline_error_message(error_symbol):
        pass

    def display_error(self,error_id, error_symbol):
        if error_id == self.EXTRA_SEMICOLON:
            print("SYNTAX WARNING", error_id,': Extra semicolons added')
            self.next_scan_start()

        elif error_id == self.EXTRA_DEVICES:
            print("SYNTAX WARNING", error_id,': DEVICES already called')
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_CONNECT:
            print("SYNTAX WARNING", error_id,': CONNECTIONS already Called')
            self.next_scan_start(in_block = False)

        elif error_id == self.EXTRA_MONITOR:
            print("SYNTAX WARNING", error_id,': MONITOR already called')
            self.next_scan_start(in_block = False)

        elif error_id == self.NO_NUMBER:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a number")
            self.next_scan_start()

        elif error_id == self.NO_SEMICOLON:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a semicolon here")
            self.next_scan_start()

        elif error_id == self.INVALID_DEVICENAME:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid device name")
            self.next_scan_start()

        elif error_id == self.NO_EQUALS:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected an equals sign here")
            self.next_scan_start()

        elif error_id == self.NO_END:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected an 'END' statement here")
            self.next_scan_start()

        elif error_id == self.INVALID_DEVICETYPE:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid supported device type")
            self.next_scan_start()

        elif error_id == self.INVALID_OUTPUTLABEL:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Not a valid type of output label")
            self.next_scan_start()

        elif error_id == self.NO_DOT:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a dot here")
            self.next_scan_start()

        elif error_id == self.NO_DASH:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a dash here")
            self.next_scan_start()

        elif error_id == self.EXPECT_DEVICES:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'DEVICES' statement here")
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_CONNECT:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'CONNECTIONS' statement here")
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_MONITOR:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'MONITOR' statement here")
            self.next_scan_start(in_block = False)

        elif error_id == self.EXPECT_MAIN_END:
            self.error_count += 1
            print("SYNTAX ERROR", error_id, ": Expected a 'MAIN_END' statement here")
            self.next_scan_start(in_block = False)

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
            #SYNTAX WARNING (extra semicolons added)
            pass

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
                    self.next_symbol()
                elif not in_block:
                    if self.current_symbol.id == self.scanner.DEVICES_ID:
                        if self.parse_completion[0]:
                            safe_start = True
                        else:
                            pass
                            #SYNTAX WARNING (DEVICES ALREADY CALLED)
                    elif self.current_symbol.id == self.scanner.CONNECT_ID:
                        if self.parse_completion[1]:
                            safe_start = True
                        else:
                            pass
                            #SYNTAX WARNING (CONNECTIONS ALREADY CALLED)
                    elif self.current_symbol.id == self.scanner.MONITOR_ID:
                        if not self.parse_completion[2]:
                            safe_start = True
                        else:
                            pass
                            #SYNTAX WARNING (MONITOR ALREADY CALLED)
                elif self.current_symbol.id == self.scanner.END_ID and in_block:
                    safe_start = True
                else:
                    safe_start = True
                    self.next_symbol()
            else:
                self.next_symbol()
        return

    #To be completed function to parse inputlabel
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
                        self.next_symbol()
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
                            
        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (Expected END after devices)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (Unrecognised Device Type)
            self.next_scan_start()
            self.parse_devices

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
                            self.next_symbol()
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

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (Expected END after CONNECTIONS)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name)
            self.next_scan_start()
            self.parse_connections()

    def parse_monitor(self):
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
                    self.successful_parse = False
                    self.next_scan_start()
                    # SYNTAX ERROR (Invalid output label)
            
            if self.current_symbol.type == self.scanner.SEMICOLON and expect_semicolon:
                self.next_symbol()
                #Need to implement monitoring here
            elif not expect_semicolon:
                pass
            else:
                self.successful_parse = False
                self.next_scan_start()
                # SYNTAX ERROR (Expected semicolon)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self.next_symbol()
                return
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (Expected END after devices)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            return

        else:
            self.successful_parse = False
            #SYNTAX ERROR MESSAGE (Unrecognised Device Name)
            self.next_scan_start()
            self.parse_monitor()

    def parse_network(self):
        """Parse the circuit definition file."""
        if False:
            self.next_symbol()
            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                self.next_symbol()
                self.parse_devices()
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (EXPECTED DEVICES)
                self.next_scan_start(in_block = False)
                if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.DEVICES_ID:
                    self.next_symbol()
                    self.parse_devices()
            return self.successful_parse

            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                self.next_symbol()
                self.parse_connections()
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (EXPECTED CONNECTIONS)
                self.next_scan_start(in_block = False)
                if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.CONNECT_ID:
                    self.next_symbol()
                    self.parse_connections()

            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                self.next_symbol()
                self.parse_monitor()
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (EXPECTED MONITORS)
                self.next_scan_start(in_block = False)
                if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MONITOR_ID:
                    self.next_symbol()
                    self.parse_monitor()

            if self.current_symbol.type == self.scanner.KEYWORD and self.current_symbol.id == self.scanner.MAIN_END_ID:
                self.successful_parse = True
            else:
                self.successful_parse = False
                #SYNTAX ERROR MESSAGE (NO MAIN_END)
            
            if self.error_count > 0:
                return False
            else:
                return True


        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True
