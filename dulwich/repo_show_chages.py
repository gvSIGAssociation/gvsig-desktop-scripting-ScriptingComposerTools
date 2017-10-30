# encoding: utf-8

import gvsig

import os

from java.lang import String
from java.util import Vector

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from javax.swing.table import DefaultTableModel, TableModel
from javax.swing.event import TableModelEvent

from repo_utils import getComposer, getBaseRepoPath, getSelectedFolder
from repo_utils import warning, SimpleDialog, message, inputbox, windowManager

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 

from dulwich import porcelain, repo

class RepoChange(object):
  def __init__(self, status, workingpath):
    self.status = status
    self.workingpath = workingpath

  def __repr__(self):
    return "RepoChange(%r,%r)" % (self.status, self.workingpath)
    
class RepoChanges(object):
  def __init__(self, repopath, workingpath):
    self.__changes = list()
    self.__repopath = repopath
    self.__workingpath = workingpath
    self.__repo = porcelain.open_repo(repopath)
    self.refresh()

  def refresh(self):
    self.__changes = list()
    status = porcelain.status(self.__repo)
    #print ">>> status:", repr(status)
    if isinstance(status, dict):
      tracked_changes = status
      unstaged_changes = list()
    else:
      tracked_changes = status[0]
      unstaged_changes = status[1]
    #print ">>> tracked_changes:", repr(tracked_changes)
    #print ">>> unstaged_changes:", repr(unstaged_changes)
    tracked = list()
    for x in self.__repo.open_index().iteritems():
      tracked.append(x[0])
    #print ">>> tracked:", repr(tracked)
    localfiles = self.getFiles(self.__workingpath)
    untracked = list()
    for f in localfiles:
      f = os.path.relpath(f,self.__repopath)
      if not f in tracked :
        untracked.append(f)
    #print ">>> untracked:", repr(untracked)
      
    for x in tracked_changes["add"]:
      self.__changes.append(RepoChange("add",x))
    for x in tracked_changes["modify"]:
      self.__changes.append(RepoChange("modify",x))
    for x in tracked_changes["delete"]:
      self.__changes.append(RepoChange("delete",x))
    for x in unstaged_changes:
      self.__changes.append(RepoChange("unstaged",x))
    for x in untracked:
      self.__changes.append(RepoChange("untracked",x))

    print "len changes: ", len(self.__changes)
    
  def __repr__(self):
    return repr(self.__changes)

  def __len__(self):
    return len(self.__changes)

  def __getitem__(self, index):
    return self.__changes[index]

  def __iter___(self):
    return self.__changes.__iter__()
    
  def stage_all(self):
    unstaged = list()
    for change in self.__changes:
      if change.status == "unstaged":
        unstaged.append(change.workingpath)
    if len(unstaged)>0:
      self.__repo.stage(unstaged)

  def add_all(self):
    untracked = list()
    for change in self.__changes:
      if change.status == "untracked":
        untracked.append(change.workingpath)
    if len(untracked)>0:
      porcelain.add(self.__repo, untracked)
    
  def perform_all(self, message):
    self.stage_all()
    self.add_all()
    porcelain.commit(self.__repo, bytes(message))
    
  def commit(self, message):
    porcelain.commit(self.__repo, bytes(message))

  def getFiles(self, path):
    paths = []
    for dirpath, dirnames, filenames in os.walk(path):
        # Skip .git and below.
        if '.git' in dirnames:
            dirnames.remove('.git')
        for filename in filenames:
          if filename.startswith("."):
            continue
          ext = os.path.splitext(filename)[1]
          if ext in (".class", ):
            continue
          f = os.path.join(dirpath, filename)
          paths.append(f)
    paths.sort()
    return paths

"""
class RepoChangesTableModel(DefaultTableModel):
  def __init__(self, changes):
    self.__changes = changes

  def addTableModelListener(self, l):
    pass
   
  def getColumnClass(self, columnIndex):
    return String

  def getColumnCount(self):
    return 2

  def getColumnName(self, columnIndex):
    if columnIndex == 0:
      return "Status"
    return "Path"

  def getRowCount(self):
    return len(self.__changes)

  def getValueAt(self, rowIndex, columnIndex):
    change = self.__changes[rowIndex]
    if columnIndex == 0:
      return change.status
    if change.workingpath.startswith('../../scripts/'):
      return change.workingpath[14:]
    return change.workingpath

  def isCellEditable(self, rowIndex, columnIndex):
    return False

  def removeTableModelListener(self, l):
    pass
    
  def setValueAt(self, aValue, rowIndex, columnIndex):
    pass

  def refresh(self):
    self.__changes.refresh()
    self.fireTableChanged(TableModelEvent(self))
      
"""


class RepoShowChangesPanel(FormPanel,Component):
  def __init__(self, repoName, changes):
    FormPanel.__init__(self,getResource(__file__,"repo_show_changes.xml"))
    self.__changes = changes
    self.lblRepoName.setText(unicode(repoName,"utf-8"))
    self.tableChanges.setModel(DefaultTableModel())
    self.updateTableModel()
    self.setPreferredSize(550,250)

  def updateTableModel(self):
    model = self.tableChanges.getModel()
    oldNumRows = model.getRowCount()
    columnIdentifiers = Vector(2)
    columnIdentifiers.add("Status")
    columnIdentifiers.add("Path")
    numRows = len(self.__changes)
    if numRows==0 :
      model.setColumnIdentifiers(columnIdentifiers)
      while model.getRowCount() > 0 :
        model.removeRow(0)
      model.fireTableDataChanged()
      self.asJComponent().setVisible(False) # ¿?
    else: 
      rows = Vector(numRows)
      for change in self.__changes:
        row = Vector(2)
        row.add(change.status)
        if change.workingpath.startswith('../../scripts/'):
          row.add(change.workingpath[14:])
        else:
          row.add(change.workingpath)
        rows.add(row)
      model.setDataVector(rows, columnIdentifiers)    
      self.tableChanges.setVisible(True)
      
    self.tableChanges.getColumnModel().getColumn(0).setPreferredWidth(100)
    self.tableChanges.getColumnModel().getColumn(1).setPreferredWidth(1000)

  def refresh(self):
    self.__changes.refresh()
    self.updateTableModel()
  
  def btnRefresh_click(self, *args):
    self.refresh()
    
  def btnAddAll_click(self, *args):
    self.__changes.add_all()
    self.refresh()
    
  def btnStageAll_click(self, *args):
    self.__changes.stage_all()
    self.refresh()
    
  def btnCommit_click(self, *args):
    msg = inputbox("Mensage")
    self.__changes.commit(msg)
    self.refresh()
    
  def btnPerformAll_click(self, *args):
    msg = inputbox("Mensage")
    self.__changes.perform_all(msg)
    self.refresh()
    
def repo_show_changes():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos para crear un nuevo repositorio local.")
    return 
  repopath = os.path.join(getBaseRepoPath(),folder.getId())
  if not os.path.exists(repopath):
    warning("No existe un repositorio local asociado a la carpeta '%s'." % folder.getId())
    return
      
  changes = RepoChanges(repopath, folder.getFile().getAbsolutePath())
  composer = getComposer()
  
  panel = RepoShowChangesPanel(folder.getName(), changes)
  composer.getDock().add("#GitChanges","Git changes",panel,JScriptingComposer.Dock.DOCK_BOTTOM)
  composer.getDock().select("#GitChanges")
  panel.asJComponent().requestFocus()
  
def main(*args):
  repo_show_changes()
