import pytest
from scanner import Scanner
from names import Names
from parse import Parser
from devices import Device, Devices
from network import Network
from monitors import Monitors

def test_parser_semantic_errors_devices(capsys):
    names=Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    errors=['Device by this name already exists',
            'Qualifier is invalid for device type',
            'No qualifier given and device type requires one',
            'Qualifier given but one was not allowed with device type',
            'Device Type given is not a valid device type'
            ]
    for i in range(5):
        file_path=r'parser_semantic_error_tests/'+str(i+1)+'.txt'
        scanner=Scanner(file_path,names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
        out, err = capsys.readouterr()
        assert  'Device by this name already exists'   in out