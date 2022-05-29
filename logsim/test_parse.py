import pytest
from scanner import Scanner
from names import Names
from parse import Parser
from devices import Device, Devices
from network import Network
from monitors import Monitors

def test_parser(capsys):
    names=Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    error_output =["SYNTAX ERROR: Extra semicolons added",
                "SYNTAX ERROR : DEVICES already called",
                "SYNTAX ERROR : CONNECTIONS already Called",
                "SYNTAX ERROR : MONITOR already called",
                "SYNTAX ERROR : Not a number",
                "SYNTAX ERROR : Expected a semicolon here",
                "SYNTAX ERROR : Not a valid device name",
                "SYNTAX ERROR : Expected an equals sign here",
                "SYNTAX ERROR : Expected an 'END' statement",
                "SYNTAX ERROR : Not a valid supported device type",
                "SYNTAX ERROR : Not a valid type of output label",
                "SYNTAX ERROR : Expected a dot here",
                "SYNTAX ERROR : Expected a dash here",
                "SYNTAX ERROR : Expected a 'DEVICES' statement here",
                "SYNTAX ERROR : Expected a 'CONNECTIONS' statement here",
                "SYNTAX ERROR : Expected a 'MONITOR' statement here",
                "SYNTAX ERROR : Expected a 'MAIN_END' statement here",
                "SYNTAX ERROR : Unexpected 'END' statement",
                "SYNTAX ERROR : Invalid input label"]

    for i in range (1):
        if i not in [1,2,3]:
            file_path = "".join(['parser_tests\parser_test_file',str(i+1),'.txt'])
            scanner=Scanner(file_path,names)
            parser = Parser(names, devices, network, monitors, scanner, test = True)
            parser.parse_network()
            out, err = capsys.readouterr()
            assert error_output[i] in out
