# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

from org.gvsig.tools.swing.api import ToolsSwingLocator
from javax.swing import Action
from org.gvsig.scripting.swing.api import JScriptingComposer
from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.tools.swing.api import Component
from javax.swing import AbstractAction
from org.gvsig.expressionevaluator.swing import ExpressionEvaluatorSwingLocator
from org.gvsig.expressionevaluator.swing import JTextComponentProxy

class JTextComponentOfEditor(JTextComponentProxy):
  def getJTextComponent(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    editor = composer.getCurrentEditor()
    jtext = editor.getJTextComponent()
    return jtext

class CosaAssistantAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Cosa assistant")
    self.putValue(Action.ACTION_COMMAND_KEY, "CosaAssistant");
    #self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"assistant.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "Show the Cosa assistant");

  def actionPerformed(self,e=None):
    if e!=None:
      composer = e.getSource().getContext()
    else:
      composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    assistant = ExpressionEvaluatorSwingLocator.getManager().createJExpressionBuilderAssistant(JTextComponentOfEditor())
    assistant.setAutomaticExpressionCheckerEnabled(False)
    composer.getDock().add("#CosaAssistant","Cosa assistant",assistant,JScriptingComposer.Dock.DOCK_BOTTOM)
    composer.getDock().select("#CosaAssistant")
    assistant.asJComponent().requestFocus()
    
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = CosaAssistantAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action)
  
def main(*args):
  #selfRegister()  
  action = CosaAssistantAction()
  action.actionPerformed()
  
