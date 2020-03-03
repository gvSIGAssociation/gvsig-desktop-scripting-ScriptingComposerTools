# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN

from StringIO import StringIO

from org.gvsig.scripting.swing.impl.composer.editors import ExternalFileEditor

from org.gvsig.tools.swing.api import ToolsSwingLocator

class HTMLViewer(ExternalFileEditor):
  def __init__(self, unit):
    ExternalFileEditor.__init__(self)
    self.__browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
    self.addPanel("Viewer",self.__browser.asJComponent())
    self.set(unit)

  def set(self, unit):
    ExternalFileEditor.set(self, unit)
    self.__browser.location(unit.getExternalFile().toURI().toURL())
    try:
      self.getTabbedPane().setSelectedIndex(1)
    except:
      pass

