# encoding: utf-8

import gvsig
from gvsig import commonsdialog
from gvsig.libs.formpanel import load_icon

from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from javax.swing import AbstractAction
from org.gvsig.tools.util import ToolsUtilLocator
from java.io import File
from java.lang import System
from javax.swing import Action
from org.gvsig.scripting import ScriptingFolder
from org.gvsig.scripting.impl import UserFolder

def getSelectedFolder():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  launcher = composer.getProjects()
  
  browser = launcher.getSelectedBrowser()
  unit = browser.getSelectedNode()

  if not isinstance(unit,ScriptingFolder):
    unit =  browser.getSelectionPath().getPathComponent(browser.getSelectionPath().getPathCount()-2)

  return unit


class FileExplorerAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Filesystem explorer")
    self.putValue(Action.ACTION_COMMAND_KEY, "FilesystemExplorer")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","fileexplorer.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Launches the system file explorer")

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    unit = getSelectedFolder()
    if unit == None:
      commonsdialog.msgbox("Select a folder in the projects tree.", "Editor", commonsdialog.IDEA, root=composer)
      return
    else:
      uri = unit.getFile().toURL().toURI()
    desktop = ToolsUtilLocator.getToolsUtilManager().createDesktopOpen()
    desktop.browse(uri)
  
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = FileExplorerAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action1)
  
def main(*args):
  selfRegister()
  
  