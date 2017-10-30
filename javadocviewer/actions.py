# encoding: utf-8

from gvsig import *
from gvsig.libs.formpanel import load_icon, getResource

from os.path import join, dirname

from javax.swing import AbstractAction, Action

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 
from org.gvsig.tools import ToolsLocator

from javadoc import Javadoc
from javadocnavigatorpanel import JavadocNavigatorPanel

class JavadocPanelAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Java docs")
    self.putValue(Action.ACTION_COMMAND_KEY, "JavadocNavigator")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","javadoc.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Java docs navigator")

  def actionPerformed(self,e):
    javadoc = Javadoc()
    navigator = JavadocNavigatorPanel(javadoc)
    navigator.getBookmarksPanel().addDocument(
      "gvSIG Scripting developers guide", 
      "jar:file:" + getResource(__file__, "data","scripting-developers-guide.zip!/html/index.html"), 
      persistent=False
    )
    for docset in javadoc.getDefaultJavadocSets():
      navigator.loadJavadocSet(docset.getName(), docset.getURL())

    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    composer.getDock().add("#JavadocNavigator","Javadoc",navigator,JScriptingComposer.Dock.DOCK_LEFT)
    composer.getDock().select("#JavadocNavigator")    
  
  def isEnabled(self):
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = JavadocPanelAction()
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action1)
  
def main(*args):
  selfRegister()
  