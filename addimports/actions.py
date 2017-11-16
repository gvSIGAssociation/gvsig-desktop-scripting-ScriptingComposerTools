# encoding: utf-8

import gvsig
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

import addimports
reload(addimports)

from addimports import AddImportsPanel

class FixImportsAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Fix imports...")
    self.putValue(Action.ACTION_COMMAND_KEY, "FixImports")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","fiximports.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Search import and fix its")
    self.putValue(Action.ACCELERATOR_KEY, 
      KeyStroke.getKeyStroke(
        KeyEvent.VK_I, 
        InputEvent.CTRL_DOWN_MASK + InputEvent.SHIFT_DOWN_MASK
      )
    )

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    #if composer.getDock().get("#JavadocNavigator") == None:
    #  gvsig.commonsdialog.msgbox(
    #    "You must open the javadocs in order to use this functionality",
    #    "Fix imports", 
    #    gvsig.commonsdialog.WARNING, 
    #    root=composer
    #  )
    #  return
    editor = composer.getCurrentEditor()
    if editor == None:
      return
    panel = AddImportsPanel(editor)
    panel.showWindow()
  
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = FixImportsAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action1)
  
def main(*args):
  selfRegister()
  