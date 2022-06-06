import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import time

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from graph import Graph


import wx

class Translation(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(220, 100))

        panel = wx.Panel(self, -1)

        mylocale = wx.Locale()
        mylocale.AddCatalogLookupPathPrefix('.')
        print(mylocale.AddCatalog('tester'))
        #wx.Translations.SetLanguage=wx.LANGUAGE_SPANISH
        _ = wx.GetTranslation
        
        wx.StaticText(panel, -1, _("hello"), (10, 10))
        #wx.StaticText(panel, -1, wx.GetTranslation('hello'), (10, 10))
        print(_("hello"))
        self.Centre()
        self.Show(True)

app = wx.App()
Translation(None, -1, 'Translation')
app.MainLoop()
