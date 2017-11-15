# encoding: utf-8

import gvsig


from javax.swing import AbstractAction
from javax.swing import Action
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.tools import ToolsLocator

from useplugin import UsePluginPanel

class UsePluginAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Use plugin...")
    self.putValue(Action.ACTION_COMMAND_KEY, "UsePlugin");
    #self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"consolejython.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "Add plugin dependency in the editor environment");

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    panel = UsePluginPanel()
    panel.showWindow()
  
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = UsePluginAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action)
  
def main(*args):
  selfRegister()  
  