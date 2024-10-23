# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN

from StringIO import StringIO

from org.gvsig.scripting.swing.impl.composer.editors import TextEditor

from org.gvsig.tools.swing.api import ToolsSwingLocator

class HTMLViewer(TextEditor):
  def __init__(self, unit):
    self.__browser = None
    TextEditor.__init__(self, unit)
    self.__browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
    self.addPanel("Viewer",self.__browser.asJComponent())
    self.set(unit)

  def set(self, unit):
    TextEditor.set(self, unit)
    if self.__browser == None:
      return
    self.__browser.location(unit.getExternalFile().toURI().toURL())
    try:
      self.getTabbedPane().setSelectedIndex(2)
    except:
      pass

