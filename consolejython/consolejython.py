# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

from org.gvsig.tools.swing.api import ToolsSwingLocator
from javax.swing import JScrollPane
from javax.swing import Action
from org.gvsig.scripting.swing.api import JScriptingComposer
from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.tools.swing.api import Component
from javax.swing import AbstractAction

from java.awt import Color

class Console(Component):
  def __init__(self):
    import console.console 
    self.__console = console.console.Console(None)
    self.__component = JScrollPane(self.__console.output)
    self.__console.output.background = Color.black
    self.__console.output.foreground = Color(0xb2,0xb2,0xb2)
    self.__console.infoColor = Color(0xff,0xff,0)
    self.__console.errorColor = Color(0x18,0x18,0xb2)        
    self.__console.output.setCaretColor(Color(0xb2,0xb2,0xb2))
    self.__console.doc.remove(0, self.__console.doc.length)
    
    ToolsSwingLocator.getToolsSwingManager().setDefaultPopupMenu(self.__console.output)
    
    for line in "\n".join(console.console.Console.BANNER):
      self.__console.write(line)
    self.__console.printPrompt()
    self.__console.output.requestFocus()
        
    

  def asJComponent(self):
    return self.__component

class ConsoleJythonAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Shell python")
    self.putValue(Action.ACTION_COMMAND_KEY, "ConsoleJython");
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"consolejython.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "Show the shell python");

  def actionPerformed(self,e):
    console = Console()
    composer = e.getSource().getContext()
    composer.getDock().add("#ConsoleJython","Shell",console,JScriptingComposer.Dock.DOCK_BOTTOM)
    composer.getDock().select("#ConsoleJython")
    console.asJComponent().requestFocus()
    
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = ConsoleJythonAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action)
  
def main(*args):
  selfRegister()  
  