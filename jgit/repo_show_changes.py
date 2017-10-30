# encoding: utf-8

import gvsig

import os

from java.lang import String
from java.util import Vector

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from javax.swing.table import DefaultTableModel, TableModel
from javax.swing.event import TableModelEvent

from repo_utils import Git, getComposer, getSelectedFolder
from repo_utils import warning, SimpleDialog, message, inputbox, windowManager, confirm

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 

from org.gvsig.tools.swing.api import ToolsSwingLocator

import repo_push
reload(repo_push)

import repo_pull
reload(repo_pull)

import repo_diff
reload(repo_diff)

labels_status = {
  "missing"    : "Locally removed",  # Pending "git rm/checkout"
  "removed"    : "Locally removed",  # Pending "git commit"
  "add"        : "Locally new",      # Pending "git commit"
  "changed"    : "Locally modified", # Pending "git commit"
  "modified"   : "Locally modified", # Pending "git add/checkout"
  "untracked"  : "Locally new",      # Pending "git add"
  "conflicting": "Conflict",         # Pending ??
  "uncommitted": "Locally modified", # Pending "git commit/checkout"
}

class ShowChangesPanel(FormPanel,Component):
  def __init__(self, repoName, git):
    FormPanel.__init__(self,getResource(__file__,"repo_show_changes.xml"))
    self.btnRefreshStatus_click.setSynchronous(False)
    self.btnUpdate_click.setSynchronous(False)
    self.btnCommit_click.setSynchronous(False)
    self.btnShowLocally_click.setSynchronous(False)
    self.__git = git
    self.__last_status = None
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
      self.message("git status...")
      model = DefaultTableModel()
      columnIdentifiers = Vector(2)
      columnIdentifiers.add("Status")
      columnIdentifiers.add("Path")
      model.setColumnIdentifiers(columnIdentifiers)
      model.setRowCount(0)

      self.__last_status = self.__git.status()
      numRows = len(self.__last_status)
      if numRows>0 :
        rows = Vector(numRows)
        self.setStatusbar(0,0,numRows)
        n = 0
        for change in self.__last_status:
          self.setStatusbar(n)
          n += 1
          row = Vector(2)
          status = change.getStatus()
          row.add(labels_status.get(status,status))
          row.add(change.getWorkingPath())
          rows.add(row)
        model.setDataVector(rows, columnIdentifiers)    

      self.tableChanges.setModel(model)
      self.tableChanges.getColumnModel().getColumn(0).setPreferredWidth(150)
      self.tableChanges.getColumnModel().getColumn(1).setPreferredWidth(1000)
    finally:
      self.message()
      self.hideStatusbar()
      
  def refresh(self):
    self.updateTableModel()
  
  def btnShowBoth_click(self, *args):
    pass
    
  def btnShowLocally_click(self, *args):
    self.refresh()
    
  def btnShowRemotely_click(self, *args):
    pass
    
  def btnRefreshStatus_click(self, *args):
    self.refresh()

  def btnDiff_click(self, *args):
    selectedRows = self.tableChanges.getSelectedRows()
    if len(selectedRows)<0:
      message("Need select a row to diff with HEAD")
      return
    if len(selectedRows)>1:
      message("Need only a row selected to diff with HEAD")
      return
    change = self.__last_status[selectedRows[0]]
    repo_diff.repo_diff(change.getWorkingPath())
    
  def btnUpdate_click(self, *args):
    try:
      selectedRows = self.tableChanges.getSelectedRows()
      if len(selectedRows)<1:
        selectedRows = xrange(0,self.tableChanges.getRowCount())
        self.message("Prepare update all files (%s)..." % len(selectedRows))
      else:
        self.message("Prepare update selected files (%s)..." % len(selectedRows))

      if not confirm("Are you sure to overwrite files in the workspace?"):
        return
      filesToCheckout = list()
      self.setStatusbar(0,0,len(selectedRows))
      n = 0
      for row in selectedRows:
        self.setStatusbar(n)
        n+=1
        change = self.__last_status[row]
        status = change.getStatus()
        workingpath = change.getWorkingPath()
        if status in ("missing", "modified","uncommitted"):
          filesToCheckout.append(workingpath)
      #print "git checkout ", filesToCheckout
      #if len(filesToCheckout)>0:
      self.message("git checkout %s files..." % len(filesToCheckout))
      self.__git.checkout(filesToCheckout)
      self.refresh()
    finally:
      self.message()
      self.hideStatusbar()
      pass
    
  def btnCommit_click(self, *args):
    try:
      selectedRows = self.tableChanges.getSelectedRows()
      if len(selectedRows)<1:
        selectedRows = xrange(0,self.tableChanges.getRowCount())
        self.message("Prepare commit all files (%s)..." % len(selectedRows))
      else:
        self.message("Prepare commit selected files (%s)..." % len(selectedRows))
      msg = inputbox("Commit message")
      if msg == None:
        return
      filesToAdd = list()
      filesToRemove = list()
      self.setStatusbar(0,0,len(selectedRows))
      n = 0
      for row in selectedRows:
        self.setStatusbar(n)
        n+=1
        change = self.__last_status[row]
        status = change.getStatus()
        workingpath = change.getWorkingPath()
        if status in ("untracked", "modified"):
          filesToAdd.append(workingpath)
        if status == "missing":
          filesToRemove.append(workingpath)
      if len(filesToAdd)>0:
        self.message("git add %s files..." % len(filesToAdd))
        #print "git add ", filesToAdd
        self.__git.add(filesToAdd)
      if len(filesToRemove)>0:
        self.message("git rm %s files..." % len(filesToRemove))
        #print "git rm ", filesToRemove
        self.__git.rm(filesToRemove)
      self.message("git commit %r..." % msg)
      self.__git.commit(msg)
      self.refresh()
    finally:
      self.message()
      self.hideStatusbar()
      
  def btnPush_click(self, *args):
    repo_push.repo_push(self.__git)

  def btnPull_click(self, *args):
    repo_pull.repo_pull(self.__git)
  
def repo_show_changes():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos.")
    return 
  git = Git(folder.getFile())
  if not os.path.exists(git.getRepoPath()):
    warning("No existe un repositorio local asociado a la carpeta '%s'." % git.getRepoName())
    return
  fname = os.path.join(git.getWorkingPath(),".gitignore")
  if not os.path.exists(fname):
    f = open(fname, "w")
    f.write("*.class\n")
    f.write(".directory\n")
    f.close()    
    
  panel = ShowChangesPanel(git.getRepoName(), git)
  composer = getComposer()
  composer.getDock().add("#GitChanges","Git changes",panel,JScriptingComposer.Dock.DOCK_BOTTOM)
  composer.getDock().select("#GitChanges")
  panel.asJComponent().requestFocus()
  
def main(*args):
  repo_show_changes()
  
