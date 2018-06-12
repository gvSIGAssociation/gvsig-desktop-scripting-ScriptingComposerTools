# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
reload(repo_utils)
from repo_utils import Git, getSelectedGit, warning, SimpleDialog, message

from org.gvsig.tools.swing.api.windowmanager import WindowManager_v2

class RepoInfoPanel(FormPanel):
  def __init__(self, git):
    FormPanel.__init__(self,getResource(__file__,"repo_info.xml"))
    self.txtRepoName.setText(git.getRepoName())
    self.txtRepoPath.setText(git.getRepoPath())
    self.txtWorkingPath.setText(git.getWorkingPath())
    self.txtRemoteURL.setText(git.getRemoteURL())
    self.txtUserName.setText(git.getUserName())    
    self.txtUserId.setText(git.getUserId())
    self.txtUserMail.setText(git.getUserMail())

  def getUserName(self):
    return self.txtUserName.getText()
    
  def getUserId(self):
    return self.txtUserId.getText()
    
  def getUserMail(self):
    return self.txtUserMail.getText()
    
def repo_info():
  git = getSelectedGit()
  if git == None:
    return 
  panel = RepoInfoPanel(git)
  dialog = SimpleDialog(panel, WindowManager_v2.BUTTONS_OK_CANCEL)
  dialog.showModal()
  if dialog.isOk():
    git.setUserName(panel.getUserName())
    git.setUserId(panel.getUserId())
    git.setUserMail(panel.getUserMail())


def main(*args):
  repo_info()
