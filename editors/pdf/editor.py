# encoding: utf-8

import gvsig

#
# http://sventon.icesoft.org/svn/repos/repo/list/icepdf/trunk/icepdf/examples/component/?revision=HEAD&bypassEmpty=true
# http://res.icesoft.org/docs/icepdf/latest/viewer
# http://res.icesoft.org/docs/icepdf/latest/core
#

from gvsig import logger, LOGGER_WARN


from org.gvsig.scripting.swing.impl.composer.editors import ExternalFileEditor

from org.icepdf.ri.common import SwingController
from org.icepdf.ri.common import SwingViewBuilder

class PDFViewer(ExternalFileEditor):
  def __init__(self, unit):
    ExternalFileEditor.__init__(self)
    self.__controller = SwingController()
    self.__controller.setIsEmbeddedComponent(True)
    self.__pdfPanel = SwingViewBuilder(self.__controller).buildViewerPanel()
    self.addPanel("Viewer",self.__pdfPanel)
    self.set(unit)

  def set(self, unit):
    ExternalFileEditor.set(self, unit)
    self.__controller.openDocument(unit.getExternalFile().toURI().toURL())  

