# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
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
    
    panel = self.__panel
    progressbar = panel.pgbMonitor
    git = self.__git
    try:
      git.cloneRepository(panel.getRepositoryURL(), monitor=self, user=panel.getUserId(), password=panel.getPassword())
      git.setUserMail(panel.getUserMail())     
      if panel.getUserId()!=None:
        git.setUserId(panel.getUserId())
      if panel.rememberPassword() and panel.getPassword()!=None:
        git.setPassword(panel.getPassword())
      panel.btnClose.setEnabled(True)
      panel.btnCloneRepository.setEnabled(False)
      progressbar.setMaximum(10)
      progressbar.setMinimum(1)
      progressbar.setValue(10)
      progressbar.setStringPainted(True)
      progressbar.setString("Finished")
    
    except Throwable, ex:
      ex = sys.exc_info()[1]
      gvsig.logger("Can't load module 'jgit'. " + str(ex), gvsig.LOGGER_WARN, ex)
      self.endTask()
      progressbar.setString("ERROR (%s)" % str(ex))

    except :
      ex = sys.exc_info()[1]
      gvsig.logger("Can't load module 'jgit'. " + str(ex), gvsig.LOGGER_WARN, ex)
      self.endTask()
      progressbar.setString("ERROR (%s)" % ( sys.exc_info()[1]))
    
  def start(self, totalTasks):
    self.__totalTasks = totalTasks
    
  def beginTask(self, title, totalWork):
    progressbar = self.__panel.pgbMonitor
    progressbar.setMaximum(totalWork)
    progressbar.setMinimum(totalWork)
    progressbar.setValue(0)
    progressbar.setStringPainted(True)
    progressbar.setString("%s (%s/%s)" % (title,self.__curtask,self.__totalTasks))
    
  def update(self, completed):
    progressbar = self.__panel.pgbMonitor
    progressbar.setValue(completed)

  def isCancelled(self):
    return False

  def endTask(self):
    panel = self.__panel
    progressbar = panel.pgbMonitor
    
    panel.btnClose.setEnabled(True)
    panel.btnCloneRepository.setEnabled(False)
    progressbar.setMaximum(10)
    progressbar.setMinimum(1)
    progressbar.setValue(10)
    progressbar.setStringPainted(True)
    progressbar.setString("Finished")
    
class ClonePanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_clone.xml"))
    self.__monitor = CloneMonitor(git, self)
    self.pgbMonitor.setVisible(False)
    self.setPreferredSize(450,200)
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    toolsSwingManager.addClearButton(self.txtUser)
    toolsSwingManager.setDefaultPopupMenu(self.txtUser)
    toolsSwingManager.addClearButton(self.txtPassword)
    toolsSwingManager.setDefaultPopupMenu(self.txtPassword)
    toolsSwingManager.addClearButton(self.txtUserMail)
    toolsSwingManager.setDefaultPopupMenu(self.txtUserMail)
    toolsSwingManager.addClearButton(self.txtURL)
    toolsSwingManager.setDefaultPopupMenu(self.txtURL)


  def btnCloneRepository_click(self, *event):
    self.pgbMonitor.setVisible(True)
    self.btnClose.setEnabled(False)
    self.btnCloneRepository.setEnabled(False)
    Thread(self.__monitor).start()  

  def getUserId(self):
    userId = self.txtUser.getText().strip()
    if userId == "":
      return None
    return userId

  def getPassword(self):
    password = self.txtPassword.getText().strip()
    if password == "":
      return None
    return password

  def rememberPassword(self):
    return self.chkRememberPassword.isSelected()
  
  def getUserMail(self):
    userMail = self.txtUserMail.getText().strip()
    if userMail == "":
      return None
    return userMail
    
  def getRemoteBranchName(self):
    return self.txtRemoteBranchName.getText()

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
