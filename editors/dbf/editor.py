# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN
from gvsig import openStore

from javax.swing import JPanel

from org.gvsig.scripting.swing.impl.composer.editors import ExternalFileEditor
from org.gvsig.fmap.dal.swing import DALSwingLocator
from java.awt import BorderLayout
from javax.swing import JTabbedPane

class DBFEditor(ExternalFileEditor):
  def __init__(self, unit):
    ExternalFileEditor.__init__(self)
    self.__formpanel = None
    self.__tablepanel = None
    self.__initComponents()
    self.set(unit)

  def __initComponents(self):
    self.__tablepanel = JPanel()
    self.__tablepanel.setLayout(BorderLayout())
    self.__formpanel = JPanel()
    self.__formpanel.setLayout(BorderLayout())
    self.addPanel("Form", self.__formpanel)
    self.addPanel("Table", self.__tablepanel)
    
  def save(self):
    if self.__store.isEditing():
      self.__store.finishEditing()

  def isModified(self):
    return self.__store.isEditing()
    
  def fetch(self, unit):
    pass
   
  def set(self, unit):
    ExternalFileEditor.set(self, unit)
    try:
      uimanager = DALSwingLocator.getSwingManager()
      self.__store = openStore("DBF",DbfFile=self.getUnit().getExternalFile())
  
      tableModel = uimanager.createFeatureTableModel(self.__store, None)
      self.__table = uimanager.createJFeatureTable(tableModel)
      form = uimanager.createJFeaturesForm(self.__store)
      self.__formpanel.removeAll()
      self.__formpanel.add(form.asJComponent(),BorderLayout.CENTER)
      self.__tablepanel.removeAll()
      self.__tablepanel.add(self.__table.asJComponent(),BorderLayout.CENTER)
      try:
        self.getTabbedPane().setSelectedIndex(1)
      except:
        pass
    except Exception, ex:
      logger("Can't set unit.",LOGGER_WARN,ex)
    
