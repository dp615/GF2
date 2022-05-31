import pytest
from scanner import Scanner
from names import Names
from parse import Parser
from devices import Device
from devices import Devices
from network import Network
from monitors import Monitors


def test_parser_semantic_errors_devices(capsys):
    errors = ['Device by this name already exists',
              'Qualifier is invalid for device type',
              'No qualifier given and device type requires one',
              'Qualifier given but one was not allowed with device type'
              , 'Device Type given is not a valid device type']
    for i in range(5):
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)

        file_path = r'parser_semantic_error_tests/' + str(i + 1) \
            + '.txt'
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    (out, err) = capsys.readouterr()
    for i in range(5):
        assert errors[i] in out


def test_parser_semantic_errors_connections(capsys):
    errors = [
        'ERROR : Device name does not exist',
        'ERROR : Device name does not exist',
        'ERROR : Input is already connected',
        'ERROR : Cannot connect an input to an input',
        'ERROR : Port does not exist',
        'ERROR : Cannot Connect output to output',
        ]

    for i in range(6):
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)

        file_path = r'parser_semantic_error_tests/' + str(i + 6) \
            + '.txt'
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    (out, err) = capsys.readouterr()
    for i in range(6):
        assert errors[i] in out


def test_parser_semantic_errors_monitor(capsys):
    errors = ['ERROR : Can only monitor outputs',
              'ERROR : Output already being monitored',
              'ERROR : Device does not exist']

    for i in range(3):
        names = Names()
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)

        file_path = r'parser_semantic_error_tests/' + str(i + 12) \
            + '.txt'
        scanner = Scanner(file_path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        parser.parse_network()
    (out, err) = capsys.readouterr()
    for i in range(3):
        assert errors[i] in out


