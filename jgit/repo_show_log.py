# encoding: utf-8

import gvsig

import os

from java.lang import String
from java.util import Vector

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from javax.swing.table import DefaultTableModel, TableModel
from javax.swing.event import TableModelEvent

from repo_utils import Git, getComposer, getSelectedGit
from repo_utils import warning, SimpleDialog, message, inputbox, windowManager, confirm

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 

from org.gvsig.tools.swing.api import ToolsSwingLocator

from java.text import SimpleDateFormat

class ShowLogPanel(FormPanel,Component):
  def __init__(self, repoName, git):
    FormPanel.__init__(self,getResource(__file__,"repo_show_log.xml"))
    self.__git = git
    self.__commits = None
    self.lblRepoName.setText(unicode(repoName,"utf-8"))
    self.updateTableModel()
    self.setPreferredSize(550,250)
    self.pgbProgress.setVisible(False)
    self.message()

  def message(self, msg=None):
    if msg == None:
      msg = ""
    self.lblMessage.setText(msg)
    if msg == "":
      self.imgBusy.setVisible(False)
    else:
      self.imgBusy.setVisible(True)

  def setStatusbar(self, value, minvalue=None, maxvalue=None):
    if minvalue!=None:
      self.pgbProgress.setMinimum(minvalue)
      self.pgbProgress.setVisible(True)
    if maxvalue!=None:
      self.pgbProgress.setMaximum(maxvalue)
    self.pgbProgress.setValue(value)

  def hideStatusbar(self):
    self.pgbProgress.setVisible(False)
    
  def updateTableModel(self):
    try:
      self.message("git log...")
      model = DefaultTableModel()
      columnIdentifiers = Vector(2)
      columnIdentifiers.add("id")
      columnIdentifiers.add("Date")
      columnIdentifiers.add("User name")
      columnIdentifiers.add("Message")
      model.setColumnIdentifiers(columnIdentifiers)
      model.setRowCount(0)

      self.__commits = self.__git.log()
      numRows = len(self.__commits)
      if numRows>0 :
        rows = Vector(numRows)
        self.setStatusbar(0,0,numRows)
        n = 0
        for commit in self.__commits:
          self.setStatusbar(n)
          n += 1
          row = Vector(4)
          row.add(commit.getId())
          row.add(SimpleDateFormat("yy/MM/dd HH:mm").format(commit.getDate()))
          row.add(commit.getCommiterName())
          row.add(commit.getShortMessage())
          rows.add(row)
        model.setDataVector(rows, columnIdentifiers)    

      self.tableChanges.setModel(model)
      self.tableChanges.getColumnModel().getColumn(0).setPreferredWidth(100)
      self.tableChanges.getColumnModel().getColumn(1).setPreferredWidth(150)
      self.tableChanges.getColumnModel().getColumn(2).setPreferredWidth(120)
      self.tableChanges.getColumnModel().getColumn(3).setPreferredWidth(1000)
    finally:
      self.message()
      self.hideStatusbar()
      
  def refresh(self):
    self.updateTableModel()
  
def repo_show_log():
  git = getSelectedGit()
  if git == None:
    return

  panel = ShowLogPanel(git.getRepoName(), git)
  composer = getComposer()
  composer.getDock().add("#GitLog","Git Log",panel,JScriptingComposer.Dock.DOCK_BOTTOM)
  composer.getDock().select("#GitLog")
  panel.asJComponent().requestFocus()
  
def main(*args):
  repo_show_log()
  
