"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

import sys


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line = None
        self.position_in_line = None


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.

    print_location(self, symbol): Prints where on the line a given symbol
                                  is with a caret.

    Private methods
    -------------
    _skip_spaces_and_comments(self): Skips white spaces and comments.

    _get_name(self): Returns the next name in the file as a string.

    _get_number(self): Returns the next number in the file as an integer.

    _advance(self): Reads the next character in the file.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try:
            self.file = open(path, "r")
            self.file.seek(0, 0)
        except FileNotFoundError:
            print('File not found: please enter a valid file path. Use "logsim.py -h" for help.')
            sys.exit()

        self.names = names

        self.symbol_type_list = [
            self.COMMA,
            self.SEMICOLON,
            self.EQUALS,
            self.DASH,
            self.KEYWORD,
            self.NUMBER,
            self.NAME,
            self.DOT,
            self.UNTERMINATED_COMMENT,
            self.EOF
        ] = range(10)

        self.keywords_list = [
            "DEVICES",
            "CONNECTIONS",
            "MONITOR",
            "MAIN_END",
            "END"
            ]

        [
            self.DEVICES_ID,
            self.CONNECT_ID,
            self.MONITOR_ID,
            self.MAIN_END_ID,
            self.END_ID,
        ] = self.names.lookup(self.keywords_list)

        self.current_character = " "
        self.position = 0
        self.line = 0
        self.position_in_line = 0
        self.last_hash_line =0
        self.last_hash_position_in_line =0

    def _skip_spaces_and_comments(self):
        """Skip white spaces and comments."""
        no_of_hashtags = 0
        while (
            (self.current_character.isspace()
            or no_of_hashtags % 2 != 0
            or self.current_character == "#" ) 
            and self.current_character!= ''
        ):
            if self.current_character == "#":
                no_of_hashtags += 1
                self.last_hash_line=self.line
                self.last_hash_position_in_line=self.position_in_line
            
                
            
            self._advance()
        if self.current_character == '' and no_of_hashtags % 2 != 0:
            return False
        return True

    def _get_name(self):
        """Return the next name in the file as a string."""
        name = ""
        while (self.current_character.isalnum() or
                self.current_character == "_"):
            name = name + self.current_character
            self._advance()
        return name

    def _get_number(self):
        """Return the next number in the file."""
        number = ""
        while self.current_character.isdigit():
            number = number + self.current_character
            self._advance()
        return int(number)

    def _advance(self):
        """Read another character in the file."""
        self.current_character = self.file.read(1)
        self.position_in_line += 1
        if self.current_character == "\n":
            self.line += 1
            self.position_in_line = -1

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        if self._skip_spaces_and_comments() == False:  
            print('here')
            symbol.type = self.UNTERMINATED_COMMENT
            symbol.position_in_line = self.last_hash_position_in_line
            symbol.line = self.last_hash_line
            self._advance()
            return symbol
        symbol.position_in_line = self.position_in_line
        symbol.line = self.line
        if self.current_character.isalpha():  
            name_string = self._get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])
        elif self.current_character.isdigit():  
            symbol.id = self._get_number()
            symbol.type = self.NUMBER
        elif self.current_character == "=":  
            symbol.type = self.EQUALS
            self._advance()
        elif self.current_character == ",":
            symbol.type = self.COMMA
            self._advance()
        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self._advance()
        elif self.current_character == "-":
            symbol.type = self.DASH
            self._advance()
        elif self.current_character == ".":
            symbol.type = self.DOT
            self._advance()
        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
        else:  # not a valid character
            self._advance()
        return symbol

    def print_location(self, symbol):
        """Print where the line a symbol is on with a caret."""
        line = symbol.line
        position_in_line = symbol.position_in_line
        self.position = self.file.tell()
        self.file.seek(0, 0)
        lines=self.file.readlines()
        if len(lines) != 0:
            if symbol.type == self.EOF:
                position_in_line -= 1
                while position_in_line >= len(lines[line]) and line!= 0:
                    line -= 1
                    position_in_line=len(lines[line])-1
                if line == 0:
                    line=None
                    position_in_line = None

            if line != None:
                print("Error on line " + str(line + 1))
                line_to_print = lines[line]
                print(line_to_print, end="")
                if line_to_print[-1] != "\n":
                    print("")
                string = ""
                for i in range(position_in_line):
                    string = string + " "
                string = string + "^"
                print(string)
        self.file.seek(self.position)
