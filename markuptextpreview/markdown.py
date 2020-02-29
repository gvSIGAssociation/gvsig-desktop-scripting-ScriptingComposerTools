# encoding: utf-8

import gvsig

from gvsig import commonsdialog

import os
import os.path
import io

from gvsig import getResource
from java.util import HashMap
from java.io import FileOutputStream

from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer

from com.vladsch.flexmark.html import HtmlRenderer
from com.vladsch.flexmark.parser import Parser
from com.vladsch.flexmark.util.data import MutableDataSet
from com.vladsch.flexmark.ext.autolink import AutolinkExtension
from com.vladsch.flexmark.ext.jekyll.tag import JekyllTag
from com.vladsch.flexmark.ext.jekyll.tag import JekyllTagExtension
from com.vladsch.flexmark.ext.jekyll.front.matter import JekyllFrontMatterExtension
from com.vladsch.flexmark.ext.macros import MacrosExtension
from com.vladsch.flexmark.ext.tables import TablesExtension
from com.vladsch.flexmark.ext.admonition import AdmonitionExtension
from com.vladsch.flexmark.ext.footnotes import FootnoteExtension
from com.vladsch.flexmark.ext.toc import TocExtension
from com.vladsch.flexmark.ext.typographic import TypographicExtension
from com.vladsch.flexmark.pdf.converter import PdfConverterExtension

from com.vladsch.flexmark.ast import Image
from com.vladsch.flexmark.util.ast import VisitHandler, Visitor
from com.vladsch.flexmark.util.sequence import BasedSequenceImpl

class ImageProcessVisitor(Visitor):
  def __init__(self, folder):
    Visitor.__init__(self)
    self.folder = folder
    self.absolutePaths = False
    
  def hasAbsolutePaths(self):
    return self.absolutePaths

  def setFolder(self, folder):
    self.folder = folder
    
  def visit(self, node):
    if isinstance(node,Image):
      url = str(node.url)
      if url.startswith("/") :
        self.absolutePaths = True
      url_abs = os.path.join(self.folder, url)
      node.setUrl(BasedSequenceImpl.of(url_abs))
    self.visitChildren(node)

  def visitChildren(self, parent):
    node = parent.getFirstChild()
    while node != None:
      next = node.getNext()
      self.visit(node)
      node = next

def loadMDFile(folder, fname):
  f = io.open(os.path.join(folder,fname),"r",encoding="utf-8")
  markdown = f.read()
  f.close()
  return markdown
  
def toHtml(markdown, mdpathname, **kwargs):

  folder = os.path.dirname(mdpathname)
  
  included = HashMap()

  options = MutableDataSet()
  options.set(Parser.EXTENSIONS, [
     AutolinkExtension.create(), 
     JekyllTagExtension.create(),
     JekyllFrontMatterExtension.create(),
     MacrosExtension.create(),
     TablesExtension.create(),
     AdmonitionExtension.create(),
     FootnoteExtension.create(),
     TocExtension.create(),
     TypographicExtension.create()
    ]
  )
  options.set(JekyllTagExtension.ENABLE_INLINE_TAGS, True)
  options.set(JekyllTagExtension.ENABLE_BLOCK_TAGS, True)
  options.set(JekyllTagExtension.ENABLE_RENDERING, False)

  # change soft break to hard break
  #options.set(HtmlRenderer.SOFT_BREAK, "<br/>")

  parser = Parser.builder(options).build()
  renderer = HtmlRenderer.builder(options).build()

  document = parser.parse(markdown)
  
  imageProcess = ImageProcessVisitor(folder)
  imageProcess.visit(document)
  
  # see if document has includes
  doc = document;
  if doc.contains(JekyllTagExtension.TAG_LIST):
    tagList = JekyllTagExtension.TAG_LIST.get(doc)
    includeHtmlMap = HashMap()
    for tag in tagList:
      tagName = tag.getTag()
      if tagName.equals("include"):
        includeFile = tag.getParameters().toString()
        if not includeFile in ("",None):
          if includeFile in("page-break","pagebreak"):
            text = '<div style="page-break-after: always"></div>\n'
          else:
            text = loadMDFile(folder, includeFile)
            imageProcess.setFolder(os.path.dirname(os.path.join(folder, includeFile)))
          if includeFile.endswith(".md") :
            includeDoc = parser.parse(text)
            imageProcess.visit(includeDoc)
            includeHtml = renderer.render(includeDoc)
            includeHtmlMap.put(includeFile, includeHtml)
  
            # copy any definition of reference elements from included file to our document
            parser.transferReferences(doc, includeDoc, None)
          else:
            includeHtmlMap.put(includeFile, text)
        
    if not includeHtmlMap.isEmpty():
      doc.set(JekyllTagExtension.INCLUDED_HTML, includeHtmlMap)

  html = renderer.render(document);
  
  html = html.encode("utf-8",'replace')
  html = """<!DOCTYPE html>
<html>
<head>
<meta charset=\"UTF-8\">
<style>
img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  page-break-before: auto; /* 'always,' 'avoid,' 'left,' 'inherit,' or 'right' */
  page-break-after: auto; /* 'always,' 'avoid,' 'left,' 'inherit,' or 'right' */
  page-break-inside: avoid; /* or 'auto' */
}
</style>
</head>
<body>
""" + html + """
</body>
</html>"""
  if imageProcess.hasAbsolutePaths() and kwargs.get("allowgui",False):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    commonsdialog.msgbox(
      "Se han utilizado rutas absolutas en alguna de las imagenes\nEs recomendable usar solo rutas relativas.", 
      "MarkupText preview", 
      commonsdialog.IDEA, 
      root=composer
    )
    
  return html

def selfRegister():
  pass

def getSelectedUnit():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  launcher = composer.getProjects()
  browser = launcher.getSelectedBrowser()
  unit = browser.getSelectedNode()
  return unit
  
def test(*args):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  #unit = composer.getLauncherSelectedUnit()
  unit = getSelectedUnit()
  if unit == None:
    #composer.msgbox("Debera seleccionar un elemento en el arbol de proyectos.", "MarkupText preview")
    commonsdialog.msgbox("Debera seleccionar un elemento en el arbol de proyectos.", "MarkupText preview", commonsdialog.IDEA, root=composer)
    return
  
  pathname = unit.getFiles()[0].getAbsolutePath()
  f = io.open(pathname,"r",encoding="utf-8")
  markdown = f.read()
  f.close()
  
  html = toHtml(markdown, pathname, allowgui=True)
  
  foldersManager = ToolsLocator.getFoldersManager()
  temp_html = foldersManager.getTemporaryFile("preview-md.html")
  f = open(temp_html.getAbsolutePath(),"w")
  f.write(html)
  f.close()

  dockPanel = composer.getDock().get("#MarkupTextPreview")
  if dockPanel == None:
    browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
    dockPanel = composer.getDock().add("#MarkupTextPreview","MarkupText preview",browser,JScriptingComposer.Dock.DOCK_LEFT)
  else:
    browser = dockPanel.getComponent()    
  composer.getDock().select("#MarkupTextPreview")   
  browser.location(temp_html.toURI().toURL())

def main(*args):
  test()
  
  