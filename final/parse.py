"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

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
    parse_network(self): Parses the circuit definition file.

    Private methods
    --------------
    _copy_symbol(self): Returns a copy Symbol class instance of the
                       current symbol.

    _inline_error_message(self, symbol = None): Calls to the scanner
                        to print an error message at the appropriate
                        location by providing the error symbol.

    _display_syntax_error(self,error_id): Prints an error message for
                                    syntax and parser errors.

    _display_devices_error(self,error_id, device_name_symbol,
                        device_type_symbol, device_parameter_symbol):
                        Prints an error message for 'devices' errors.

    _display_connect_error(self, error_id, output_device_symbol,
                    output_symbol, input_device_symbol, input_symbol):
                    Prints an error message for connection errors.

    _display_monitors_error(self,error_id, monitor_symbol,
                    monitor_output_symbol): Prints an error message
                                            for 'monitors' errors.

    _next_symbol(self): Gets next symbol from scanner.

    _next_scan_start(self, in_block = True): Reaches a safe symbol to
                            resume parsing after an error occurs.

    _parse_devices(self): Parses the 'DEVICES' block of definition file.

    _parse_connections(self): Parses the 'CONNECTIONS' block of
                             definition file.

    _parse_monitor(self): Parses the 'MONITORS' block of definition file.
    """

    def __init__(
        self,
        names,
        devices,
        network,
        monitors,
        scanner,
        test=False
    ):
        """Initialise parser errors and constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.test = test

        self.current_symbol = None
        self.parse_completion = [False, False, False]

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
            self.INVALID_INPUTLABEL,
            self.INCOMPLETE_NETWORK,
            self.UNTERMINATED_COMMENT
        ] = self.names.unique_error_codes(20)

        self.error_count = 0

    def _copy_symbol(self):
        """Return a copy Symbol class instance of the current symbol."""
        symbol = Symbol()
        symbol.type = int(self.current_symbol.type)
        symbol.id = int(self.current_symbol.id)
        symbol.line = int(self.current_symbol.line)
        symbol.position_in_line = int(self.current_symbol.position_in_line)
        return symbol

    def _inline_error_message(self, symbol=None):
        """Call scanner to print an error message at the right location."""
        if not symbol:
            self.scanner.print_location(self.current_symbol)
        else:
            self.scanner.print_location(symbol)

    def _display_syntax_error(self, error_id):
        """Return error messages for syntax and parser errors."""
        self.error_count += 1
        print("Errors found so far :", self.error_count)
        advance = False  # True if _next_symbol needs to be called
        restart = True   # True if _next_scan_start needs to be called
        in_block = True  # Parameter for _next_scan_start
        if error_id == self.EXTRA_SEMICOLON:
            print("ERROR: Extra semicolons added")
            restart = False

        elif error_id == self.EXTRA_DEVICES:
            print("ERROR : DEVICES already called")
            advance = True
            in_block = False

        elif error_id == self.EXTRA_CONNECT:
            print("ERROR : CONNECTIONS already Called")
            advance = True
            in_block = False

        elif error_id == self.EXTRA_MONITOR:
            print("ERROR : MONITOR already called")
            advance = True
            in_block = False

        elif error_id == self.NO_NUMBER:
            print("ERROR : Not a number")

        elif error_id == self.NO_SEMICOLON:
            print("ERROR : Expected a semicolon here")

        elif error_id == self.INVALID_DEVICENAME:
            print("ERROR : Not a valid device name")

        elif error_id == self.NO_EQUALS:
            print("ERROR : Expected an equals sign here")

        elif error_id == self.NO_END:
            print("ERROR : Expected an 'END' statement")
            restart = False

        elif error_id == self.INVALID_DEVICETYPE:
            print("ERROR : Not a valid supported device type")

        elif error_id == self.INVALID_OUTPUTLABEL:
            print("ERROR : Not a valid type of output label")

        elif error_id == self.NO_DOT:
            print("ERROR : Expected a dot here")

        elif error_id == self.NO_DASH:
            print("ERROR : Expected a dash here")

        elif error_id == self.EXPECT_DEVICES:
            print("ERROR : Expected a 'DEVICES' statement here")
            in_block = False

        elif error_id == self.EXPECT_CONNECT:
            print("ERROR : Expected a 'CONNECTIONS' statement here")
            in_block = False

        elif error_id == self.EXPECT_MONITOR:
            print("ERROR : Expected a 'MONITOR' statement here")
            in_block = False

        elif error_id == self.NO_MAIN_END:
            print("ERROR : Expected a 'MAIN_END' statement here")
            in_block = False

        elif error_id == self.INVALID_INPUTLABEL:
            print("ERROR : Invalid input label")

        elif error_id == self.UNTERMINATED_COMMENT:
            print("ERROR : Unterminated Comment present")
            restart = False

        elif error_id == self.INCOMPLETE_NETWORK:
            print("ERROR : Not all inputs are connected")
            return  # No inline error message for incomplete network

        else:
            print('Unregistered error id in parser code', error_id)

        if not self.test:
            self._inline_error_message()
        if advance:
            self._next_symbol()
        if restart:
            self._next_scan_start(in_block=in_block)

    def _display_devices_error(
        self,
        error_id,
        device_name_symbol,
        device_type_symbol,
        device_parameter_symbol
    ):
        """Return error messages for devices errors."""
        self.error_count += 1
        print("Errors found so far :", self.error_count)
        if error_id == self.devices.DEVICE_PRESENT:
            print("ERROR : Device by this name already exists")
            self._inline_error_message(device_name_symbol)

        elif error_id == self.devices.NO_QUALIFIER:
            print("ERROR : No qualifier given and device type requires one")
            self._inline_error_message(device_type_symbol)

        elif error_id == self.devices.INVALID_QUALIFIER:
            print("ERROR : Qualifier is invalid for device type")
            self._inline_error_message(device_parameter_symbol)

        elif error_id == self.devices.QUALIFIER_PRESENT:
            print("ERROR : Qualifier not valid with device type")
            self._inline_error_message(device_parameter_symbol)

        elif error_id == self.devices.BAD_DEVICE:
            print("ERROR : Device Type given is not a valid device type")
            self._inline_error_message(device_type_symbol)

        else:
            print("ERROR : Unregistered error id in parser code", error_id)

    def _display_connect_error(
        self,
        error_id,
        output_device_symbol,
        output_symbol,
        input_device_symbol,
        input_symbol,
    ):
        """Return error messages for connection errors."""
        self.error_count += 1
        print("Errors found so far :", self.error_count)
        if error_id == self.network.DEVICE_ABSENT_ONE:
            print("ERROR : Device name does not exist")
            self._inline_error_message(output_device_symbol)

        elif error_id == self.network.DEVICE_ABSENT_TWO:
            print("ERROR : Device name does not exist")
            self._inline_error_message(input_device_symbol)

        elif error_id == self.network.INPUT_CONNECTED:
            print("ERROR : Input is already connected")
            self._inline_error_message(input_symbol)

        elif error_id == self.network.INPUT_TO_INPUT:
            print("ERROR : Cannot connect an input to an input")
            self._inline_error_message(output_symbol)

        elif error_id == self.network.PORT_ABSENT:
            print("ERROR : Port does not exist")
            self._inline_error_message(output_device_symbol)

        elif error_id == self.network.OUTPUT_TO_OUTPUT:
            print("ERROR : Cannot Connect output to output")
            self._inline_error_message(input_device_symbol)

        else:
            print("ERROR : Unregistered error id in parser code", error_id)

    def _display_monitors_error(
        self,
        error_id,
        monitor_symbol,
        monitor_output_symbol
    ):
        """Return error messages for monitor errors."""
        self.error_count += 1
        print("Errors found so far :", self.error_count)
        if error_id == self.monitors.NOT_OUTPUT:
            print("ERROR : Can only monitor outputs")
            self._inline_error_message(monitor_symbol)

        elif error_id == self.monitors.MONITOR_PRESENT:
            print("ERROR : Output already being monitored")
            self._inline_error_message(monitor_symbol)

        elif error_id == self.monitors.network.DEVICE_ABSENT:
            print("ERROR : Device does not exist")
            self._inline_error_message(monitor_symbol)

        else:
            print("Unregistered error id in parser code", error_id)
            print(self.monitors.MONITOR_PRESENT)

    def _next_symbol(self):
        """Change current symbol to next symbol from scanner."""
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.type == self.scanner.UNTERMINATED_COMMENT:
            self._display_syntax_error(self.UNTERMINATED_COMMENT)
            self.current_symbol = self.scanner.get_symbol()

    def _next_scan_start(self, in_block=True):
        """Reach a safe symbol to resume parsing after an error.

        Keyword Argument
        in_block = True if stopping symbol is mainly semicolon
                   False if stopping symbol is mainly END
        """
        while True:
            if self.current_symbol.type == self.scanner.EOF:
                return

            elif in_block:
                if self.current_symbol.type == self.scanner.SEMICOLON:
                    self._next_symbol()
                    while self.current_symbol.type == self.scanner.SEMICOLON:
                        self._display_syntax_error(self.EXTRA_SEMICOLON)
                        self._next_symbol()
                    return

                elif (
                    self.current_symbol.type == self.scanner.KEYWORD
                    and self.current_symbol.id == self.scanner.END_ID
                ):
                    return

            elif (
                not in_block
                and self.current_symbol.type == self.scanner.KEYWORD
            ):
                if self.current_symbol.id == self.scanner.DEVICES_ID:
                    if not self.parse_completion[0]:
                        return
                    else:
                        # SYNTAX ERROR (DEVICES ALREADY CALLED)
                        self._display_syntax_error(self.EXTRA_DEVICES)

                elif self.current_symbol.id == self.scanner.CONNECT_ID:
                    if not self.parse_completion[1]:
                        return
                    else:
                        # SYNTAX ERROR (CONNECTIONS ALREADY CALLED)
                        self._display_syntax_error(self.EXTRA_CONNECT)

                elif self.current_symbol.id == self.scanner.MONITOR_ID:
                    if not self.parse_completion[2]:
                        return
                    else:
                        # SYNTAX ERROR (MONITOR ALREADY CALLED)
                        self._display_syntax_error(self.EXTRA_MONITOR)

                elif self.current_symbol.id == self.scanner.MAIN_END_ID:
                    return

            self._next_symbol()

    def _parse_devices(self):
        """Parse the 'DEVICES' block of definition file."""
        self.parse_completion[0] = True
        while self.current_symbol.type == self.scanner.NAME:
            device_type_symbol = self._copy_symbol()
            device_parameter_symbol = Symbol()
            self._next_symbol()

            expect_equals = True
            if self.current_symbol.type == self.scanner.COMMA:
                expect_equals = False
                self._next_symbol()
                if self.current_symbol.type == self.scanner.NUMBER:
                    device_parameter_symbol = self._copy_symbol()
                    self._next_symbol()
                    expect_equals = True
                else:
                    self._display_syntax_error(self.NO_NUMBER)

            if (
                self.current_symbol.type == self.scanner.EQUALS
                and expect_equals
            ):
                self._next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    device_name_symbol = self._copy_symbol()
                    self._next_symbol()
                    if self.current_symbol.type == self.scanner.SEMICOLON:
                        self._next_symbol()
                        if self.error_count == 0 and not self.test:
                            error_type = self.devices.make_device(
                                    device_name_symbol.id,
                                    device_type_symbol.id,
                                    device_property=device_parameter_symbol.id
                            )
                            if error_type == self.devices.NO_ERROR:
                                pass
                            else:
                                self._display_devices_error(
                                                error_type,
                                                device_name_symbol,
                                                device_type_symbol,
                                                device_parameter_symbol
                                )
                    else:
                        self._display_syntax_error(self.NO_SEMICOLON)
                else:
                    self._display_syntax_error(self.INVALID_DEVICENAME)
            elif not expect_equals:
                pass
            else:
                self._display_syntax_error(self.NO_EQUALS)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self._next_symbol()
                return
            else:
                self._display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            self._display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self._display_syntax_error(self.EXTRA_SEMICOLON)
                self._next_symbol()
            self._parse_devices()

        else:
            self._display_syntax_error(self.INVALID_DEVICETYPE)
            self._parse_devices()

    def _parse_connections(self):
        """Parse the 'CONNECTIONS' block of definition file."""
        self.parse_completion[1] = True
        while self.current_symbol.type == self.scanner.NAME:
            output_device_symbol = self._copy_symbol()
            output_symbol = Symbol()
            self._next_symbol()

            expect_dash = True
            if self.current_symbol.type == self.scanner.DOT:
                expect_dash = False
                self._next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    output_symbol = self._copy_symbol()
                    self._next_symbol()
                    expect_dash = True
                else:
                    self._display_syntax_error(self.INVALID_OUTPUTLABEL)

            if self.current_symbol.type == self.scanner.DASH and expect_dash:
                self._next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    input_device_symbol = self._copy_symbol()
                    self._next_symbol()
                    if self.current_symbol.type == self.scanner.DOT:
                        self._next_symbol()
                        if self.current_symbol.type == self.scanner.NAME:
                            input_symbol = self._copy_symbol()
                            self._next_symbol()
                            if self.current_symbol.type == self.scanner.SEMICOLON:
                                self._next_symbol()
                                if self.error_count == 0 and not self.test:
                                    error_type = self.network.make_connection(
                                                    output_device_symbol.id,
                                                    output_symbol.id,
                                                    input_device_symbol.id,
                                                    input_symbol.id
                                    )
                                    if error_type == self.network.NO_ERROR:
                                        pass
                                    else:
                                        self._display_connect_error(
                                                    error_type,
                                                    output_device_symbol,
                                                    output_symbol,
                                                    input_device_symbol,
                                                    input_symbol
                                        )
                            else:
                                self._display_syntax_error(self.NO_SEMICOLON)
                        else:
                            self._display_syntax_error(self.INVALID_INPUTLABEL)
                    else:
                        self._display_syntax_error(self.NO_DOT)
                else:
                    self._display_syntax_error(self.INVALID_DEVICENAME)
            elif not expect_dash:
                pass
            else:
                self._display_syntax_error(self.NO_DASH)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                # Checking if all inputs are connected
                if self.error_count == 0 and not self.network.check_network():
                    self._display_syntax_error(self.INCOMPLETE_NETWORK)
                self._next_symbol()
                return
            else:
                self._display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            self._display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self._next_symbol()
            self._display_syntax_error(self.EXTRA_SEMICOLON)
            self._parse_devices()

        else:
            self._display_syntax_error(self.INVALID_DEVICENAME)
            self._parse_connections()

    def _parse_monitor(self):
        """Parse the 'MONITORS' block of definition file."""
        self.parse_completion[2] = True
        while self.current_symbol.type == self.scanner.NAME:
            monitor_symbol = self._copy_symbol()
            monitor_output_symbol = Symbol()
            self._next_symbol()

            expect_semicolon = True
            if self.current_symbol.type == self.scanner.DOT:
                expect_semicolon = False
                self._next_symbol()
                if self.current_symbol.type == self.scanner.NAME:
                    monitor_output_symbol = self._copy_symbol()
                    self._next_symbol()
                    expect_semicolon = True
                else:
                    self._display_syntax_error(self.INVALID_OUTPUTLABEL)

            if (
                self.current_symbol.type == self.scanner.SEMICOLON
                and expect_semicolon
            ):
                self._next_symbol()
                if self.error_count == 0 and not self.test:
                    error_type = self.monitors.make_monitor(
                                                monitor_symbol.id,
                                                monitor_output_symbol.id
                    )
                    if error_type == self.monitors.NO_ERROR:
                        pass
                    else:
                        self._display_monitors_error(error_type,
                                                     monitor_symbol,
                                                     monitor_output_symbol)
            elif not expect_semicolon:
                pass
            else:
                self._display_syntax_error(self.NO_SEMICOLON)

        if self.current_symbol.type == self.scanner.KEYWORD:
            if self.current_symbol.id == self.scanner.END_ID:
                self._next_symbol()
                return
            else:
                self._display_syntax_error(self.NO_END)
                return

        elif self.current_symbol.type == self.scanner.EOF:
            self._display_syntax_error(self.NO_END)
            return

        elif self.current_symbol.type == self.scanner.SEMICOLON:
            while self.current_symbol.type == self.scanner.SEMICOLON:
                self._next_symbol()
            self._display_syntax_error(self.EXTRA_SEMICOLON)
            self._parse_devices()

        else:
            self._display_syntax_error(self.INVALID_DEVICENAME)
            self._parse_monitor()

    def parse_network(self):
        """Parse the circuit definition file.

        Returns True if no errors found.
        """
        self._next_symbol()
        if(
            self.current_symbol.type == self.scanner.KEYWORD
            and self.current_symbol.id == self.scanner.DEVICES_ID
        ):
            self._next_symbol()
            self._parse_devices()
        else:
            self._display_syntax_error(self.EXPECT_DEVICES)
            if (
                self.current_symbol.type == self.scanner.KEYWORD
                and self.current_symbol.id == self.scanner.DEVICES_ID
            ):
                self._next_symbol()
                self._parse_devices()

        if (
            self.current_symbol.type == self.scanner.KEYWORD
            and self.current_symbol.id == self.scanner.CONNECT_ID
        ):
            self._next_symbol()
            self._parse_connections()
        else:
            self._display_syntax_error(self.EXPECT_CONNECT)
            if (
                self.current_symbol.type == self.scanner.KEYWORD
                and self.current_symbol.id == self.scanner.CONNECT_ID
            ):
                self._next_symbol()
                self._parse_connections()

        if (
            self.current_symbol.type == self.scanner.KEYWORD
            and self.current_symbol.id == self.scanner.MONITOR_ID
        ):
            self._next_symbol()
            self._parse_monitor()
        else:
            self._display_syntax_error(self.EXPECT_MONITOR)
            if (
                self.current_symbol.type == self.scanner.KEYWORD
                and self.current_symbol.id == self.scanner.MONITOR_ID
            ):
                self._next_symbol()
                self._parse_monitor()

        if (
            self.current_symbol.type == self.scanner.KEYWORD
            and self.current_symbol.id == self.scanner.MAIN_END_ID
        ):
            pass
        else:
            self._display_syntax_error(self.NO_MAIN_END)

        if self.error_count > 0:
            return False
        else:
            return True
