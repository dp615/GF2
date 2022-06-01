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
    """Check create_boolean_from_monitor(...) runs correctly."""
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
    """Check get_sub_exp_end(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.get_sub_exp_end('((A*B)+(B.A))', 5, True) == 1
    assert graph.get_sub_exp_end('(((A+B).(¬A+¬B))+(B.A))', 19, True) == 1
    assert graph.get_sub_exp_end(
        '((((A+B)+B).((A+B)+A)).((¬A+¬B)+(B.A)))', 21, True) == 9
    assert graph.get_sub_exp_end(
        '((((A+B)+B).((A+B)+A)).((¬A+¬B)+(B.A)))', 23, False) == 7


def test_expand_xors():
    """Check that expand_xors(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.expand_xors('(A*B)') == '((A+B).(¬A+¬B))'
    assert graph.expand_xors('((A*B)+(C.A))') == '(((A+B).(¬A+¬B))+(C.A))'


def test_distribute_ors():
    """Check that distribute_ors(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.distribute_ors('((AA.BB)+B)') == '((AA+B).(BB+B))'
    assert graph.distribute_ors('(ABCD+(AA.BB))') == '((ABCD+AA).(ABCD+BB))'
    assert graph.distribute_ors('((A+(B.C))+D)') == '(((A+B)+D).((A+C)+D))'


def test_clean_up_to_cnf():
    """Check that clean_up_to_cnf(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.clean_up_to_cnf('(((()))))))') == '(())'
    assert graph.clean_up_to_cnf('(((((A+B)+C)+D)+E))') == '((A+B+C+D+E))'
    assert graph.clean_up_to_cnf('(A+B).(C+D)') == '(A+B).(C+D)'


def test_get_clauses():
    """Check that get_clauses(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.get_clauses('((clause1).(clause2))') == ['clause1', 'clause2']
    assert graph.get_clauses('((A+B+C).(D+E+F).(G+H+I))') == ['A+B+C', 'D+E+F',
                                                              'G+H+I']
    assert graph.get_clauses('((A).(B).(C).(D).(E))') == ['A', 'B', 'C', 'D',
                                                          'E']


def test_get_literal_adc():
    """Check that get_literal_adc(...) runs correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.get_literals_adc('A+¬B') == (['A', 'B'], [0, 1])
    assert graph.get_literals_adc('A+A+A') == (['A'], [0])
    assert graph.get_literals_adc('A+A+¬A') == (['1'], [0])


def test_in_clause_clean_up():
    """Check that in_clause_clean_up(...) works correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.in_clause_clean_up('((A+B+C).(D+E+F))') == '((A+B+C).' \
        '(D+E+F))'
    assert graph.in_clause_clean_up('((A+A+A).(A+B+¬A))') == '((A).(1))'
    assert graph.in_clause_clean_up('((B).(A).(B+¬A))') == '((B).(A).(B+¬A))'


def test_out_clause_clean_up():
    """Check that out_clause_clean_up(...) works correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.out_clause_clean_up('((A).(B).(C))') == '((A).(B).(C))'
    assert graph.out_clause_clean_up('((A).(A).(C))') == '((A).(C))'
    assert graph.out_clause_clean_up('((A).(¬A).(ABC))') == '((A).(¬A).(ABC))'


def test_add_new_line_breaks():
    """Check that add_new_line_breaks(...) works correctly."""
    names, devices, network, monitors = init_modules()
    graph = Graph(names, devices, network, monitors)

    assert graph.add_new_line_breaks('('*80) == ((70 * '(') + '\n\t' +
                                                 ('(' * 10), 1)
    assert graph.add_new_line_breaks('('*(71*17))[1] == 17
    assert graph.add_new_line_breaks('1'*1000+'(000)')[0] == ('1' * 1000) + \
        '\n\t' + '(000)'


test_create_boolean_from_monitor()
test_get_sub_exp_end()
test_expand_xors()
test_distribute_ors()
test_clean_up_to_cnf()
test_get_clauses()
test_get_literal_adc()
test_in_clause_clean_up()
test_out_clause_clean_up()
test_add_new_line_breaks()
