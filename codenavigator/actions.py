# encoding: utf-8

from gvsig import *
from gvsig.libs.formpanel import load_icon

from os.path import join, dirname

from javax.swing import AbstractAction, Action
from javax.swing import KeyStroke
from java.awt.event import KeyEvent
from java.awt.event import ActionListener
from java.awt.event import InputEvent

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 
from org.gvsig.tools import ToolsLocator

from codeNavigator import CodeNavigatorDialog, CodeNavigatorPanel
from searchReferences import SearchReferencesPanel


class CodeNavigatorDialogAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Code navigator")
    self.putValue(Action.ACTION_COMMAND_KEY, "CodeNavigator")
    self.putValue(Action.SMALL_ICON, load_icon(join(dirname(__file__),"images","codeNavigator.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Code navigator")
    self.putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_O, InputEvent.CTRL_DOWN_MASK ))

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    editor = composer.getCurrentEditor()
    if editor == None:
      return
    p = CodeNavigatorDialog(composer)
    p.update()
    p.show()

  def isEnabled(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer != None:
      return composer.getDock().getSelected(JScriptingComposer.Dock.DOCK_CENTER) != None
    return False

class CodeNavigatorPanelAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Code navigator")
    self.putValue(Action.ACTION_COMMAND_KEY, "CodeNavigatorPanel")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","codeNavigator.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Code navigator panel")

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    navigator = CodeNavigatorPanel(composer)
    navigator.update()
    composer.getDock().add("#Navigator","Navigator",navigator,JScriptingComposer.Dock.DOCK_LEFT)
    composer.getDock().select("#Navigator")

class CodeNavigatorReferencesAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Search references")
    self.putValue(Action.ACTION_COMMAND_KEY, "CodeNavigatorReferences")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","references.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Search references")
    self.putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_R, InputEvent.CTRL_DOWN_MASK ))

  def actionPerformed(self,e):
    panel = SearchReferencesPanel()
    panel.show()
  
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = CodeNavigatorDialogAction()
  manager.addComposerMenu(i18nManager.getTranslation("Edit"),action1)
  action2 = CodeNavigatorPanelAction()
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action2)
  action3 = CodeNavigatorReferencesAction()
  manager.addComposerMenu(i18nManager.getTranslation("Edit"),action3)
  
