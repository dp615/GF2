"""Test the Gui and MyGlCanvas modules."""
import pytest

import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from gui import Gui
from graph import Graph


def init_modules():
    """Initialise useful modules."""
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    return names, devices, network, monitors


def test1():
    """TEST 1: open typical logic description file and produce all pages."""
    names, devices, network, monitors = init_modules()
    path = 'gui_test_files/gui_test1.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    if parser.parse_network():
        app = wx.App()
        import builtins


        builtins._ = wx.GetTranslation

        locale = wx.Locale()

        locale.Init(wx.LANGUAGE_DEFAULT)

        locale.AddCatalogLookupPathPrefix('./locale')

        locale.AddCatalog('gui')
        gui = Gui("Logic Simulator Test 1", path, names, devices, network,
                  monitors)
        gui.Show(True)
        app.MainLoop()


def test2():
    """TEST 2: open logic circuit description including CLOCK."""
    names, devices, network, monitors = init_modules()
    path = 'gui_test_files/gui_test2.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    if parser.parse_network():
        app = wx.App()
        gui = Gui("Logic Simulator Test 2", path, names, devices, network,
                  monitors)
        gui.Show(True)
        app.MainLoop()


def test3():
    """TEST 3: open logic circuit description including DTYPE flip-flops."""
    names, devices, network, monitors = init_modules()
    path = 'gui_test_files/gui_test3.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    if parser.parse_network():
        app = wx.App()
        gui = Gui("Logic Simulator Test 3", path, names, devices, network,
                  monitors)
        gui.Show(True)
        app.MainLoop()


def test4():
    """TEST 4: open "large" logic description and display useful CNF."""
    names, devices, network, monitors = init_modules()
    path = 'gui_test_files/gui_test4.txt'
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    if parser.parse_network():
        app = wx.App()
        gui = Gui("Logic Simulator Test 4", path, names, devices, network,
                  monitors)
        gui.Show(True)
        app.MainLoop()
