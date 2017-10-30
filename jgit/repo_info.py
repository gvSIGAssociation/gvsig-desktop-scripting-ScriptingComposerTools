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


def repo_info():
  git = getSelectedGit()
  if git == None:
    return 
  panel = RepoInfoPanel(git)
  dialog = SimpleDialog(panel, WindowManager_v2.BUTTONS_OK)
  dialog.showModal()


def main(*args):
  repo_info()
