import pytest
from scanner import Scanner
from names import Names
from parse import Parser
from devices import Device, Devices
from network import Network
from monitors import Monitors

def test_parser_semantic_errors_devices(capsys):
    errors=['Device by this name already exists',
                'Qualifier is invalid for device type',
                'No qualifier given and device type requires one',
                'Qualifier given but one was not allowed with device type',
                'Device Type given is not a valid device type'
                ]
    for i in range(5):
        names=Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        
        
            
        file_path=r'parser_semantic_error_tests/'+str(i+1)+'.txt'
        scanner=Scanner(file_path,names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    out, err = capsys.readouterr()
    for i in range(5):
        assert  errors[i]   in out



def test_parser_semantic_errors_connections(capsys):
    errors=['ERROR : Device name does not exist\nError on line12\nA9 - G1.I2 ;',
            'ERROR : Device name does not exist\nError on line12\nA1 - G9.I2 ;',
            'ERROR : Input is already connected\nError on line12\nA1 - G1.I1 ;',
            'ERROR : Cannot connect an input to an input\nError on line12\nG3.I2 - G1.I2 ;',
            'ERROR : Port does not exist\nError on line15\nG2 - G3.I2 ;',
            'ERROR : Cannot Connect output to output\nError on line11\nA1 - G2.Q ;'
                ]
        
    for i in range(6):
        names=Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        
            
        file_path=r'parser_semantic_error_tests/'+str(i+6)+'.txt'
        scanner=Scanner(file_path,names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    out, err = capsys.readouterr()
    for i in range(6):
        assert  errors[i]   in out

def test_parser_semantic_errors_monitor(capsys):
    errors=['ERROR : Can only monitor outputs\nError on line19\nG1.I1 ;',
            'ERROR : Output already being monitored\nError on line20\nG1 ;',
            'ERROR : Device does not exist\nError on line21\nA8 ;'
            ]
        
    for i in range(3):
        names=Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        
            
        file_path=r'parser_semantic_error_tests/'+str(i+12)+'.txt'
        scanner=Scanner(file_path,names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    out, err = capsys.readouterr()
    for i in range(3):
        assert  errors[i]   in out





names=Names()
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network) 
file_path=r'parser_semantic_error_tests/'+str(12)+'.txt'
scanner=Scanner(file_path,names)
parser = Parser(names, devices, network, monitors, scanner)
parser.parse_network()

