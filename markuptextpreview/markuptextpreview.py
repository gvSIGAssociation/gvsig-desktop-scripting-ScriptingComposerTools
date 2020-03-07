# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

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
from org.gvsig.tools.util import ToolsUtilLocator

import javax.swing.ImageIcon
import javax.imageio.ImageIO
from javax.swing import AbstractAction, Action

from org.gvsig.tools.swing.api import ToolsSwingLocator

from addons.ScriptingComposerTools.markuptextpreview import markdown
from addons.ScriptingComposerTools.markuptextpreview import restructuredtext

def isMarkuptextInEditor(event=None):
  if event == None:
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  else:
    composer = event.getSource().getContext()
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

def getHTMLPreviewFile(event=None):
  if event == None:
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  else:
    composer = event.getSource().getContext()
  if composer == None:
    return None
  editor = composer.getCurrentEditor()
  if editor == None:
    return None
  unit = editor.getUnit()
  getFile = getattr(unit,"getExternalFile",None)
  if getFile == None:
    return None
  foldersManager = ToolsLocator.getFoldersManager()
  temp = foldersManager.getTemporaryFile("markuptext-preview.html")
  os.chdir(getFile().getParent())
  markuptext = editor.getJTextComponent().getText()
  file_ext = os.path.splitext(getFile().getName())[1].lower()
  if file_ext == ".md":
    html = markdown.toHtml(markuptext, getFile().getAbsolutePath(), allowgui=True) 
  elif file_ext == ".rst":
    html = restructuredtext.toHtml(markuptext, getFile().getAbsolutePath()) 
  elif file_ext in (".htm","html") :
    html = markuptext
  else:
    return None

  f = open(temp.getAbsolutePath(),"w")
  f.write(html)
  f.close()
  return temp.getAbsolutePath()

class MarkupTextPreviewAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"MarkupText preview")
    self.putValue(Action.ACTION_COMMAND_KEY, "markuptextpreview")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","markuptextpreview.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Markup text preview (.rst, .md, .html)")

  def isEnabled(self):
    return isMarkuptextInEditor()
    
  def actionPerformed(self,event):
    composer = event.getSource().getContext()
    if composer == None:
      return None
    temp = getHTMLPreviewFile(event)
    
    #
    # Molaria poder generar tambien PDF directamente desde el IDE de scripting.
    # En el siguiente enlace cuenta como hacerlo usando itext.
    # Generaria otra herramienta (Herramientas->Generar PDF) copiada de
    # esta que genere el html y lo convierta a PDF junto al fichero fuente
    # Presentandolo usando el visor de PDFs en lugar del HTML Browser.
    #
    # https://stackoverflow.com/questions/46791708/convert-html-with-images-to-pdf-using-itext
    #
        
    dockPanel = composer.getDock().get("#MarkupTextPreview")
    if dockPanel == None:
      browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
      dockPanel = composer.getDock().add("#MarkupTextPreview","MarkupText preview",browser,JScriptingComposer.Dock.DOCK_BOTTOM)
    else:
      browser = dockPanel.getComponent()    
    composer.getDock().select("#MarkupTextPreview")   
    browser.location(File(temp).toURI().toURL())

class MarkupTextPreviewInSystemBrowserAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"MarkupText preview (system browser)")
    self.putValue(Action.ACTION_COMMAND_KEY, "markuptextpreviewinsystembrowser")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","markuptextpreview-system.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Markup text preview in system browser (.rst, .md, .html)")

  def isEnabled(self):
    return isMarkuptextInEditor()
    
  def actionPerformed(self,event):
    composer = event.getSource().getContext()
    if composer == None:
      return None
    temp = getHTMLPreviewFile(event)
    desktop = ToolsUtilLocator.getToolsUtilManager().createDesktopOpen()
    desktop.browse(File(temp).toURI())


def selfRegister():
  restructuredtext.selfRegister()
  markdown.selfRegister()

  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  for action in (
      MarkupTextPreviewAction(),
      MarkupTextPreviewInSystemBrowserAction(),
    ):
    if action.getValue(Action.SMALL_ICON)!=None :
      manager.addComposerTool(action)
    manager.addComposerMenu(i18nManager.getTranslation("Show"),action)


def main():
  selfRegister()
  