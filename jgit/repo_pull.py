# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

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
    
    try:
      strategy = str(self.__panel.getMergeStrategy())
      print "STRATEGY: [%s] %s" % (repr(strategy),type(strategy))
      status = self.__git.pull(self.__panel.getRemoteBranchName(), strategy, monitor=self)
      self.__panel.pgbMonitor.setString("Finished: %s" % status)
      #if status ==  "REJECTED_NONFASTFORWARD":
      #  message('The local copy needs to be updated in order to send the changes to the remote server.\nRun "pull" and fly to try.')
    
    except Throwable, ex:
      self.endTask()
      self.__panel.pgbMonitor.setString("ERROR (%s)" % str(ex))
    
    except:
      self.endTask()
      self.__panel.pgbMonitor.setString("ERROR")
    
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
    self.__panel.btnPull.setEnabled(False)
    self.__panel.pgbMonitor.setMaximum(10)
    self.__panel.pgbMonitor.setMinimum(1)
    self.__panel.pgbMonitor.setValue(10)
    self.__panel.pgbMonitor.setStringPainted(True)
    self.__panel.pgbMonitor.setString("Finished")
    
class PullPanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_pull.xml"))
    self.__monitor = PullMonitor(git, self)
    self.pgbMonitor.setVisible(False)
    self.setPreferredSize(450,130)
    #self.addEscapeKeyListener(fn)
    #self.addEnterKeyListener(fn)
    self.cboMergeStrategy.setSelectedIndex(3)

  def btnPull_click(self, *event):
    self.pgbMonitor.setVisible(True)
    self.btnClose.setEnabled(False)
    self.btnPull.setEnabled(False)
    Thread(self.__monitor).start()  
    
  def getRemoteBranchName(self):
    return self.txtRemoteBranchName.getText()

  def getMergeStrategy(self):
    return self.cboMergeStrategy.getSelectedItem()

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

