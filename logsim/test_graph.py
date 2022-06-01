"""Test Graph module."""

from graph import Graph

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from gui import Gui


def init_modules():
    """Initialise useful modules."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    return names, devices, network, monitors


def test_create_boolean_from_monitor():
    """Check create_boolean_from_monitor(self, monitor_name) works."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)
    path = 'gui_test_files/gui_test1.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()

    # Test working file
    bool_exp = graph.create_boolean_from_monitor('G3')
    assert bool_exp == '((A0*A1)+(A1.A0))'
    bool_exp = graph.create_boolean_from_monitor('G1')
    assert bool_exp == '(A0*A1)'
    bool_exp = graph.create_boolean_from_monitor('A0')
    assert bool_exp == 'A0'

    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)
    path = 'gui_test_files/gui_test3.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()

    # Test file including DTYPE, should return False
    bool_exp = graph.create_boolean_from_monitor('A0')
    assert not bool_exp

    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)
    path = 'gui_test_files/gui_test5.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()

    # Test file including circular dependencies, should return False.
    bool_exp = graph.create_boolean_from_monitor('G2')
    assert not bool_exp


def test_get_sub_exp_end():
    """Check get_sub_exp_end runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.get_sub_exp_end('((A0*A1)+(A1.A0))', 4, True) == 2
    assert graph.get_sub_exp_end('((A0*A1)+(A1.A0))', 4, False) == 2
    assert graph.get_sub_exp_end('(((A0+A1).(¬A0+¬A1))+(A1.A0))', 19,
                                 True) == 9
    assert graph.get_sub_exp_end(
        '((((A0+A1)+A1).((A0+A1)+A0)).((¬A0+¬A1)+(A1.A0)))', 9, True) == 2
    assert graph.get_sub_exp_end(
        '((((A0+A1)+A1).((A0+A1)+A0)).((¬A0+¬A1)+(A1.A0)))', 22, True) == 2
    assert graph.get_sub_exp_end(
        '((((A0+A1)+A1).((A0+A1)+A0)).((¬A0+¬A1)+(A1.A0)))', 40, False) == 2
    assert graph.get_sub_exp_end(
        '((((A0+A1)+A1).((A0+A1)+A0)).(((¬A0+¬A1)+A1).((¬A0+¬A1)+A0)))', 54,
        True) == 3


def test_expand_xors():
    """Check that expand_xors runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.expand_xors()
