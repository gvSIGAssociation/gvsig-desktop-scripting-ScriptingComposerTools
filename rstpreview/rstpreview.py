# encoding: utf-8

import gvsig
from gvsig import getResource

from docutils.core import publish_string
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

from  com.vladsch.flexmark.html import HtmlRenderer
from com.vladsch.flexmark.parser import Parser
from com.vladsch.flexmark.util.options import MutableDataSet

from addons.ScriptingComposerTools.javadocviewer.webbrowserpanel.browserpanel import BrowserPanel

import javadoc_role

#
# Estaria bien dar soporte a markdown para mejor integracion con GitHub
# https://github.com/vsch/flexmark-java
#

def fixurls(rest,prefix):
  def is_relative(url):
    return not bool(urlparse.urlparse(url).netloc)

  searchs=(
    "[ \\t]*[.][.][ \\t]*image::[ \\t]*(.*)", # .. image:: file1.png
    "[ \\t]*[.][.][ \\t]*[|][a-zA-Z0-9_-]*[|][ \\t]*image::[ \\t]*(.*)", # .. |xxx| image:: file1.png
    "[ \\t]*[.][.][ \\t]*figure::[ \\t]*(.*)", # .. figure:: file1.png
    "[ \\t]*[.][.][ \\t]*include::[ \\t]*(.*)", # .. include:: file1.png
    "[ \\t]*[.][.][ \\t]*_[^:]*:[ \\t]*(.*)", # .. _Python home page: file
    "`[^<]*<([^>]*)>`_" # See the `Python home page <file>`_ for info.
  )

  for search in searchs:
    out = StringIO.StringIO()
    last=0
    for x in re.finditer(search,rest):
      url = x.group(1)
      start = x.start(1)
      end = x.end(1)
      #print "url='%s', relative=%s, start=%s, end=%s" % (url,is_relative(url),start,end)
      if is_relative(url):
        out.write(rest[last:start])
        out.write(prefix)
        out.write(url)
        last=end
    out.write(rest[last:])
    rest=out.getvalue()
  return rest
  


class ReStructuredTextPreviewAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Markup preview")
    self.putValue(Action.ACTION_COMMAND_KEY, "markuppreview")
    self.putValue(Action.SMALL_ICON, self.load_icon(getResource(__file__,"rstpreview.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Markup preview (.rst, .md)")

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
    if ext in (".rst", ".md"):
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
    temp = foldersManager.getTemporaryFile("markup-preview.html")
    os.chdir(getFile().getParent())
    markuptext = editor.getJTextComponent().getText()
    if os.path.splitext(getFile().getName())[1] == ".md":
        options = MutableDataSet()
        # uncomment to set optional extensions
        #options.set(Parser.EXTENSIONS, Arrays.asList(TablesExtension.create(), StrikethroughExtension.create()));
        # uncomment to convert soft-breaks to hard breaks
        #options.set(HtmlRenderer.SOFT_BREAK, "<br />\n");
        parser = Parser.builder(options).build()
        renderer = HtmlRenderer.builder(options).build()
        document = parser.parse(markuptext)
        html = renderer.render(document)
        html = html.encode("utf-8",'replace')
    else:
      markuptext = fixurls(markuptext,os.getcwd()+"/")
      html = publish_string( source=markuptext, source_path=getFile().getName(), writer_name="html" )

    f = open(temp.getAbsolutePath(),"w")
    f.write(html)
    f.close()
    
    dockPanel = composer.getDock().get("#ReStructuredTextPreview")
    if dockPanel == None:
      browser = BrowserPanel()      
      dockPanel = composer.getDock().add("#ReStructuredTextPreview","Markup preview",browser,JScriptingComposer.Dock.DOCK_BOTTOM)
    else:
      browser = dockPanel.getComponent()    
    composer.getDock().select("#ReStructuredTextPreview")   
    browser.setPage(temp.toURI().toURL())

def selfRegister():
  javadoc_role.selfRegister()

  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = ReStructuredTextPreviewAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Show"),action)

def main():
  selfRegister()
  