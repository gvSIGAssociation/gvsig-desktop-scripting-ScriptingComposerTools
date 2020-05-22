# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os
import sys

from org.gvsig.tools.swing.api import Component

from repo_utils import Git, getComposer, getSelectedGit
from repo_utils import warning

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.eclipse.jgit.lib import ProgressMonitor
from java.lang import Runnable

from java.lang import Thread

from java.lang import Throwable

class PullMonitor(ProgressMonitor, Runnable):
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
      status = git.pull(
        panel.getRemoteBranchName(), 
        panel.getMergeStrategy(), 
        monitor=self, 
        user=panel.getUserId(), 
        password=panel.getPassword(), 
        rebase=panel.getRebase()
      )
      if panel.getUserId()!=None:
        git.setUserId(panel.getUserId())
      if panel.rememberPassword() and panel.getPassword()!=None:
        git.setPassword(panel.getPassword())
      progressbar.setString("Finished: %s" % status)
    
    except Throwable, ex:
      ex = sys.exc_info()[1]
      gvsig.logger("Can't load module 'jgit'. " + str(ex), gvsig.LOGGER_WARN, ex)
      self.endTask()
      progressbar.setString("ERROR (%s)" % str(ex))
    
    except:
      ex = sys.exc_info()[1]
      gvsig.logger("Can't load module 'jgit'. " + str(ex), gvsig.LOGGER_WARN, ex)
      self.endTask()
      progressbar.setString("ERROR")
    
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
    panel.btnPull.setEnabled(False)
    progressbar.setMaximum(10)
    progressbar.setMinimum(1)
    progressbar.setValue(10)
    progressbar.setStringPainted(True)
    progressbar.setString("Finished")

class PullPanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_pull.xml"))
    self.__monitor = PullMonitor(git, self)
    self.pgbMonitor.setVisible(False)
    self.setPreferredSize(450,195)
    #self.addEscapeKeyListener(fn)
    #self.addEnterKeyListener(fn)
    self.txtUser.setText(git.getUserId())
    password = git.getPassword()
    if password!=None :
      self.txtPassword.setText(password)
    self.cboMergeStrategy.setSelectedIndex(3)

  def btnPull_click(self, *event):
    self.pgbMonitor.setVisible(True)
    self.btnClose.setEnabled(False)
    self.btnPull.setEnabled(False)
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
  
  def getRemoteBranchName(self):
    return self.txtRemoteBranchName.getText()

  def getMergeStrategy(self):
    return str(self.cboMergeStrategy.getSelectedItem())

  def getRebase(self):
    return str(self.cboRebase.getSelectedItem())

  def showWindow(self, title="Git - Pull"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)

def repo_pull(git=None):
  if git == None:
    git = getSelectedGit()
    if git == None:
      return 
  panel = PullPanel(git)
  panel.showWindow()
  
def main(*args):
  repo_pull()
  pass

