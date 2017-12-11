# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
reload(repo_utils)
from repo_utils import Git, getSelectedFolder, warning, inputbox, message

import sys

from java.lang import Thread
from java.lang import Runnable
from java.lang import Throwable
from org.gvsig.tools.swing.api import Component
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.eclipse.jgit.lib import ProgressMonitor

class CloneMonitor(ProgressMonitor, Runnable):
  def __init__(self, git, panel):
    self.__panel = panel
    self.__git = git
    self.__curtask = 0
    self.__totalTasks = 0
    
  def run(self):
    
    try:
      self.__git.cloneRepository(
        self.__panel.getRepositoryURL(), 
        monitor=self, 
        userName=self.__panel.getUserName(), 
        userMail=self.__panel.getUserMail(), 
        userId=self.__panel.getUserId()
      )
      self.__panel.btnClose.setEnabled(True)
      self.__panel.btnCloneRepository.setEnabled(False)
      self.__panel.pgbMonitor.setMaximum(10)
      self.__panel.pgbMonitor.setMinimum(1)
      self.__panel.pgbMonitor.setValue(10)
      self.__panel.pgbMonitor.setStringPainted(True)
      self.__panel.pgbMonitor.setString("Finished")
    
    except Throwable, ex:
      self.endTask()
      self.__panel.pgbMonitor.setString("ERROR (%s)" % str(ex))

    except :
      self.endTask()
      self.__panel.pgbMonitor.setString("ERROR (%s)" % ( sys.exc_info()[1]))
    
  def start(self, totalTasks):
    self.__totalTasks = totalTasks
    
  def beginTask(self, title, totalWork):
    self.__panel.pgbMonitor.setMaximum(totalWork)
    self.__panel.pgbMonitor.setMinimum(totalWork)
    self.__panel.pgbMonitor.setValue(0)
    self.__panel.pgbMonitor.setStringPainted(True)
    self.__panel.pgbMonitor.setString("%s (%s/%s)" % (title,self.__curtask,self.__totalTasks))
    
  def update(self, completed):
    self.__panel.pgbMonitor.setValue(completed)

  def isCancelled(self):
    return False

  def endTask(self):
    self.__panel.btnClose.setEnabled(True)
    self.__panel.btnCloneRepository.setEnabled(False)
    self.__panel.pgbMonitor.setMaximum(10)
    self.__panel.pgbMonitor.setMinimum(1)
    self.__panel.pgbMonitor.setValue(10)
    self.__panel.pgbMonitor.setStringPainted(True)
    self.__panel.pgbMonitor.setString("Finished")
    
class ClonePanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_clone.xml"))
    self.__monitor = CloneMonitor(git, self)
    self.pgbMonitor.setVisible(False)
    self.setPreferredSize(450,120)

  def btnCloneRepository_click(self, *event):
    self.pgbMonitor.setVisible(True)
    self.btnClose.setEnabled(False)
    self.btnCloneRepository.setEnabled(False)
    Thread(self.__monitor).start()  
    
  def getRemoteBranchName(self):
    return self.txtRemoteBranchName.getText()

  def getUserName(self):
    return self.txtUserName.getText()

  def getUserMail(self):
    return self.txtUserMail.getText()

  def getUserId(self):
    return self.txtUserId.getText()

  def getRepositoryURL(self):
    return self.txtURL.getText()

  def showWindow(self, title="Git - Clone"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)


def repo_clone():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos para asociar el nuevo repositorio a ella.")
    return 
  git = Git(folder.getFile())
  if os.path.exists(git.getRepoPath()):
    warning("Ya existe el repositorio local asociado a la carpeta '%s'." % git.getRepoName())
    return 
  panel = ClonePanel(git)
  panel.showWindow()

def main(*args):
  repo_clone()
