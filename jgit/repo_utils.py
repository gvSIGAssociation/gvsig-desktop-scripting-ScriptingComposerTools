# encoding: utf-8

import gvsig
from gvsig import commonsdialog

import os

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting import ScriptingLocator
from org.gvsig.scripting import ScriptingFolder
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.scripting.impl import UserFolder

import composergit
reload(composergit)
from composergit import ComposerGit as Git

from java.io import File

windowManager = ToolsSwingLocator.getWindowManager()

def getComposer():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  return composer
  
def getSelectedFolder():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  launcher = composer.getProjects()
  browser = launcher.getSelectedBrowser()
  unit = browser.getSelectedNode()
  if not isinstance(unit,ScriptingFolder):
    return None
  if isinstance(unit,UserFolder):
    return None
  return unit

def getSelectedUnit():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  launcher = composer.getProjects()
  browser = launcher.getSelectedBrowser()
  unit = browser.getSelectedNode()
  return unit

def getSelectedGit():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  launcher = composer.getProjects()
  browser = launcher.getSelectedBrowser()
  folder = browser.getSelectionPath()
  selected = folder.getLastPathComponent()
  while folder !=None:
    unit = folder.getLastPathComponent()
    #print "### unit", repr(unit)
    if not isinstance(unit,ScriptingFolder):
      folder = folder.getParentPath()
      continue
    git = Git(unit.getFile())
    if os.path.exists(git.getRepoPath()):
      fname = os.path.join(git.getWorkingPath(),".gitignore")
      if not os.path.exists(fname):
        f = open(fname, "w")
        f.write("*.class\n")
        f.write(".directory\n")
        f.close()     
      return git
    folder = folder.getParentPath()
  warning("The '"+selected.getUserPath()+"' file is not under the Git control.\nYou must select a element under Git control in the project tree.")
  return None

def getSelectedGit_old():
  folder = getSelectedFolder()
  if folder == None:
    warning("You must select a folder in the project tree.")
    return None
  git = Git(folder.getFile())
  if not os.path.exists(git.getRepoPath()):
    warning("There is no local repository associated with folder '%s'." % git.getRepoName())
    return None
  fname = os.path.join(git.getWorkingPath(),".gitignore")
  if not os.path.exists(fname):
    f = open(fname, "w")
    f.write("*.class\n")
    f.write(".directory\n")
    f.close()    
  return git
  
def warning(msg):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  commonsdialog.msgbox(msg, "Git", commonsdialog.WARNING, root=composer)

def message(msg):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  commonsdialog.msgbox(msg, "Git", commonsdialog.IDEA, root=composer)
  
def confirm(msg):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  n = commonsdialog.confirmDialog(msg, "Git", messageType=commonsdialog.QUESTION, root=composer)
  if n == commonsdialog.YES:
    return True
  return False
  
def inputbox(prompt):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  resp = commonsdialog.inputbox(
    prompt,
    "Git", 
    commonsdialog.QUESTION,
    root=composer
  )
  return resp

class SimpleDialog(object):
  def __init__(self, panel, buttons = windowManager.BUTTONS_OK_CANCEL):
    self.__panel = panel
    self.__dialog = windowManager.createDialog(
      panel.asJComponent(),
      "Git",
      None,
      buttons
    )
    
  def isOk(self):
    return self.__dialog.getAction()==windowManager.BUTTON_OK
  
  def showModal(self):
    self.__dialog.show(windowManager.MODE.DIALOG)

def main(*args):
    #print getUserPath(getSelectedUnit())
    print getSelectedGit()
