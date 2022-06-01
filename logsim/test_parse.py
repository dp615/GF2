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
    error_output =["ERROR: Extra semicolons added",
                "ERROR : DEVICES already called",
                "ERROR : CONNECTIONS already Called",
                "ERROR : MONITOR already called",
                "ERROR : Not a number",
                "ERROR : Expected a semicolon here",
                "ERROR : Not a valid device name",
                "ERROR : Expected an equals sign here",
                "ERROR : Expected an 'END' statement",
                "ERROR : Not a valid supported device type",
                "ERROR : Not a valid type of output label",
                "ERROR : Expected a dot here",
                "ERROR : Expected a dash here",
                "ERROR : Expected a 'CONNECTIONS' statement here",
                "ERROR : Expected a 'MONITOR' statement here",
                "ERROR : Expected a 'MAIN_END' statement here",
                "ERROR : Unexpected 'END' statement",
                "ERROR : Invalid input label"]

    for i in range (1):
        if i not in [1,2,3]:
            file_path = "".join(['parser_tests\parser_test_file',str(i+1),'.txt'])
            scanner=Scanner(file_path,names)
            parser = Parser(names, devices, network, monitors, scanner, test = True)
            parser.parse_network()
            out, err = capsys.readouterr()
            assert error_output[i] in out
