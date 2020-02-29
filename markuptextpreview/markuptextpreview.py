# encoding: utf-8

import gvsig
from gvsig import getResource

import os
import urlparse
import StringIO
import re

from java.lang import System
from java.io import File
from java.io import FileInputStream
from java.io import FileOutputStream
from java.util import Properties

from org.apache.commons.io import FileUtils
from org.gvsig.andami import PluginsLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting import ScriptingExternalFile

import javax.swing.ImageIcon
import javax.imageio.ImageIO
from javax.swing import AbstractAction, Action

from org.gvsig.tools.swing.api import ToolsSwingLocator

from addons.ScriptingComposerTools.markuptextpreview import markdown
from addons.ScriptingComposerTools.markuptextpreview import restructuredtext

class MarkupTextPreviewAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"MarkupText preview")
    self.putValue(Action.ACTION_COMMAND_KEY, "markuptextpreview")
    self.putValue(Action.SMALL_ICON, self.load_icon(getResource(__file__,"markuptextpreview.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Markup text preview (.rst, .md, .html)")

  def load_icon(self, afile):
    if not isinstance(afile,File):
      afile = File(str(afile))
    return javax.swing.ImageIcon(javax.imageio.ImageIO.read(afile))

  def isEnabled(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer == None:
      return False
    editor = composer.getCurrentEditor()
    if editor == None:
      return False
    unit = editor.getUnit()
    getFile = getattr(unit,"getExternalFile",None)
    if getFile == None:
      return False
    name, ext = os.path.splitext(getFile().getName())
    if ext in (".rst", ".md", ".htm", ".html"):
      return True
    return False
    
  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    editor = composer.getCurrentEditor()
    if editor == None:
      return
    unit = editor.getUnit()
    getFile = getattr(unit,"getExternalFile",None)
    if getFile == None:
      return 
    foldersManager = ToolsLocator.getFoldersManager()
    temp = foldersManager.getTemporaryFile("markuptext-preview.html")
    os.chdir(getFile().getParent())
    markuptext = editor.getJTextComponent().getText()
    file_ext = os.path.splitext(getFile().getName())[1].lower()
    if file_ext == ".md":
      html = markdown.toHtml(markuptext, getFile().getAbsolutePath(), allowgui=True) 
    elif file_ext == ".rst":
      html = restructuredtext.toHtml(markuptext, getFile().getAbsolutePath(), **kwargs) 
    elif file_ext in (".htm","html") :
      html = markuptext
    else:
      return

    f = open(temp.getAbsolutePath(),"w")
    f.write(html)
    f.close()
    
    dockPanel = composer.getDock().get("#MarkupTextPreview")
    if dockPanel == None:
      browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
      dockPanel = composer.getDock().add("#MarkupTextPreview","MarkupText preview",browser,JScriptingComposer.Dock.DOCK_BOTTOM)
    else:
      browser = dockPanel.getComponent()    
    composer.getDock().select("#MarkupTextPreview")   
    browser.location(temp.toURI().toURL())

def selfRegister():
  restructuredtext.selfRegister()
  markdown.selfRegister()

  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = MarkupTextPreviewAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action)

def main():
  selfRegister()
  