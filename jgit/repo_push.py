# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

from org.eclipse.jgit.lib import ProgressMonitor

#from java.lang import Thread
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from java.lang import Runnable
from org.gvsig.tools.swing.api import Component

from repo_utils import Git, getComposer, getSelectedGit
from repo_utils import warning, message

from java.lang import Thread

class PushMonitor(ProgressMonitor, Runnable):
  def __init__(self, git, panel):
    self.__panel = panel
    self.__git = git
    self.__curtask = 0
    self.__totalTasks = 0
    
  def run(self):
    status = self.__git.push(self.__panel.getUserName(), self.__panel.getPassword(), monitor=self)
    self.__panel.pgbPushMonitor.setString("Finished: %s" % status)
    if status ==  "REJECTED_NONFASTFORWARD":
      message('The local copy needs to be updated in order to send the changes to the remote server.\nRun "pull" and fly to try.')

  def start(self, totalTasks):
    self.__totalTasks = totalTasks
    
  def beginTask(self, title, totalWork):
    self.__panel.pgbPushMonitor.setMaximum(totalWork)
    self.__panel.pgbPushMonitor.setMinimum(totalWork)
    self.__panel.pgbPushMonitor.setValue(0)
    self.__panel.pgbPushMonitor.setStringPainted(True)
    self.__panel.pgbPushMonitor.setString("%s (%s/%s)" % (title,self.__curtask,self.__totalTasks))
    
  def update(self, completed):
    self.__panel.pgbPushMonitor.setValue(completed)

  def isCancelled(self):
    return False

  def endTask(self):
    self.__panel.btnClose.setEnabled(True)
    self.__panel.btnPush.setEnabled(False)
    self.__panel.pgbPushMonitor.setMaximum(10)
    self.__panel.pgbPushMonitor.setMinimum(1)
    self.__panel.pgbPushMonitor.setValue(10)
    self.__panel.pgbPushMonitor.setStringPainted(True)
    self.__panel.pgbPushMonitor.setString("Finished")
    if self.__panel.rememberPassword():
      self.__git.setPassword(self.__panel.getPassword())
    
class PushParamsPanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_push.xml"))
    self.__monitor = PushMonitor(git, self)
    self.pgbPushMonitor.setVisible(False)
    self.setPreferredSize(400,140)
    self.txtUserName.setText(git.getUserName())
    password = git.getPassword()
    if password!=None:
      self.txtPassword.setText(password)
    self.txtPassword.requestFocusInWindow()


  def getUserName(self):
    return self.txtUserName.getText()

  def getPassword(self):
    return self.txtPassword.getText()

  def rememberPassword(self):
    return self.chkRememberPassword.isSelected()
    
  def showWindow(self, title="Git - Push"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)

  def btnPush_click(self, *args):
    self.pgbPushMonitor.setVisible(True)
    self.btnClose.setEnabled(False)
    self.btnPush.setEnabled(False)
    Thread(self.__monitor).start()
    
def repo_push(git=None):
  if git == None:
    git = getSelectedGit()
    if git == None:
      return 
  panel = PushParamsPanel(git)
  panel.showWindow()
      
def main(*args):
  repo_push()

  