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

class ResetTask(Runnable):
  def __init__(self, git, panel):
    self.__panel = panel
    self.__git = git
    
  def run(self):
    try:
      mode = str(self.__panel.getMode())
      status = self.__git.reset(mode)
      self.__panel.message("Finished")
    except Throwable, ex:
      self.endTask()
      self.__panel.message("ERROR (%s)" % str(ex))
    
    except:
      self.endTask()
      self.__panel.message("ERROR")

    finally:
      self.__panel.btnClose.setEnabled(True)

    
class ResetPanel(FormPanel,Component):
        
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_reset.xml"))
    self.__task = ResetTask(git, self)
    self.rdoMixed.setSelected(True)
    #print "Repo path: ", git.getRepoPath()
    self.txtRepositoryName.setText(git.getRepoName())
    self.txtRepositoryURL.setText(git.getRemoteURL())
    self.message("")
    self.setPreferredSize(800,340)

  def btnReset_click(self, *event):
    self.btnClose.setEnabled(False)
    self.btnReset.setEnabled(False)
    self.message("...")
    Thread(self.__task).start()  
    
  def getMode(self):
    if self.rdoHard.isSelected():
      return "HARD"
    if self.rdoKeep.isSelected():
      return "KEEP"
    if self.rdoMerge.isSelected():
      return "MERGE"
    if self.rdoMixed.isSelected():
      return "MIXED"
    return "SOFT"

  def message(self, msg):
    self.lblMsg.setText(msg)
    
  def showWindow(self, title="Git - Reset"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)

def repo_reset(git=None):
  if git == None:
    git = getSelectedGit()
    if git == None:
      return 
  panel = ResetPanel(git)
  panel.showWindow()
  
def main(*args):
  repo_reset()
  pass

