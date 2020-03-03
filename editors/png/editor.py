# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from StringIO import StringIO

from java.awt import BorderLayout

from org.gvsig.scripting.swing.impl.composer.editors import ExternalFileEditor
from org.gvsig.tools.util import ToolsUtilLocator
from org.gvsig.tools.swing.api import Component
from org.gvsig.tools.swing.api import ToolsSwingLocator


class ImageViewer(ExternalFileEditor):
  def __init__(self, unit):
    ExternalFileEditor.__init__(self)
    self.__imageViewer = ToolsUtilLocator.getImageViewerManager().createImageViewer()
    self.addPanel("Viewer",self.__imageViewer.asJComponent())
    self.__additionalPanel = AddtionalPanel()
    self.getAdditionalPanel().setLayout(BorderLayout())
    self.getAdditionalPanel().add(self.__additionalPanel.asJComponent(), BorderLayout.CENTER)
    self.set(unit)

  def set(self, unit):
    ExternalFileEditor.set(self, unit)
    self.__imageViewer.setImage(unit.getExternalFile())
    self.getTabbedPane().setSelectedIndex(1)
    try:
      image = ToolsSwingLocator.getToolsSwingManager().createSimpleImage(unit.getExternalFile())
      self.__additionalPanel.txtWidth.setText(str(image.getWidth()))
      self.__additionalPanel.txtHeight.setText(str(image.getHeight()))
    except:
      self.__additionalPanel.txtWidth.setText("???")
      self.__additionalPanel.txtHeight.setText("???")

class AddtionalPanel(FormPanel,Component):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"addtionalPanel.xml"))        
  