# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN

from StringIO import StringIO

from org.gvsig.scripting.swing.impl.composer.editors import ExternalFileEditor

from addons.ScriptingComposerTools.javadocviewer.webbrowserpanel.browserpanel import BrowserPanel

class HTMLViewer(ExternalFileEditor):
  def __init__(self, unit):
    ExternalFileEditor.__init__(self)
    self.__browser = BrowserPanel()      
    self.addPanel("Viewer",self.__browser.asJComponent())
    self.set(unit)

  def set(self, unit):
    ExternalFileEditor.set(self, unit)
    self.__browser.setPage(unit.getExternalFile().toURI().toURL())

