# encoding: utf-8

import gvsig

from os.path import dirname, join

import javax.swing.ImageIcon
from java.io import File
from javax.swing import AbstractAction, Action

from org.gvsig.tools import ToolsLocator
from org.gvsig.app.gui.utils import FontChooser
from org.gvsig.scripting.swing.api import ScriptingSwingLocator


from org.gvsig.tools.swing.api.windowmanager import WindowManager

def load_icon(afile):
  if not isinstance(afile,File):
    afile = File(str(afile))
  return javax.swing.ImageIcon(javax.imageio.ImageIO.read(afile))

class FontChooserAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Font chooser")
    self.putValue(Action.ACTION_COMMAND_KEY, "FontChooser");
    self.putValue(Action.SMALL_ICON, load_icon(join(dirname(__file__),"fontchooser.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "Set the editor font");

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    editor = composer.getCurrentEditor()
    if editor == None:
      return
    font = editor.getJTextComponent().getFont()
    font = FontChooser.showDialog("Select font",font)
    if font != None:
      editor.getJTextComponent().setFont(font)

  def isEnabled(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer == None:
      return False
    editor = composer.getCurrentEditor()
    if editor == None:
      return False
    return True


def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = FontChooserAction()
  manager.addComposerMenu(i18nManager.getTranslation("Edit"),action)
  
def main(*args):
  selfRegister()  
  
  