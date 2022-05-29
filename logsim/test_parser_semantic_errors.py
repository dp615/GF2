import pytest
from scanner import Scanner
from names import Names
from parse import Parser
from devices import Device, Devices
from network import Network
from monitors import Monitors

def test_parser_semantic_errors_devices():
    names=Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    file_path = r'parser_semantic_error_tests/DEVICE_PRESENT.txt'
    scanner=Scanner(file_path,names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()
    out, err = capfd.readouterr()
    assert out == "Device by this name already exists\nError on line3\nSWITCH, 1 = A0;"