# encoding: utf-8

import gvsig
from gvsig import commonsdialog

import os

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting import ScriptingLocator
from org.gvsig.scripting import ScriptingFolder
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.scripting.impl import UserFolder

windowManager = ToolsSwingLocator.getWindowManager()


def getBaseRepoPath():
  manager = ScriptingLocator.getManager()
  path = os.path.abspath(os.path.join(manager.getRootUserFolder().getAbsolutePath(),"..","git"))
  #print ">>> base repo path", path
  return path

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

def warning(msg):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  commonsdialog.msgbox(msg, "Git", commonsdialog.WARNING, root=composer)

def message(msg):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  commonsdialog.msgbox(msg, "Git", commonsdialog.IDEA, root=composer)

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
    pass
