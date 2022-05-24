"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


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
        self.line=None
        self.position=None


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
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try:
            self.file = open(path, "r")
        except cantOpenFile:
            sys.exit()

        self.names = names

        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
        self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(7)

        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR", "MAIN_END","END"]

        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
        self.END_ID] = self.names.lookup(self.keywords_list)

        self.current_character = ""
        
    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        symbol = Symbol()
        self.skip_spaces() # current character now not whitespace
        if self.current_character.isalpha(): # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
                [symbol.id] = self.names.lookup([name_string])
        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
        elif self.current_character == "=": # punctuation
            symbol.type = self.EQUALS
            self.advance()
        elif self.current_character == ",":
            symbol.type =self.COMMA
            self.advance()
        elif self.current_character == "": # end of file
            symbol.type = self.EOF
        else: # not a valid character
            self.advance()
        
        return symbol

    def skip_spaces(self):
        #skip white spaces
        while self.current_character.isspace()==True:
            self.advance()

    def get_name(self):
        name=''
        while self.current_character.isalnum()==True:
            name=name+self.current_character
            self.advance()
        self.advance()
        return name


    def get_number(self):
        number=''
        while self.current_character.isdigit()==True:
            name=name+self.current_character
            self.advance()
        return int(number)


    def advance(self):
        self.current_character=self.file.read(1)
