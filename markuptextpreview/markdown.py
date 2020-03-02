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
from com.vladsch.flexmark.ext.emoji import EmojiExtension
from com.vladsch.flexmark.ext.definition import DefinitionExtension
from com.vladsch.flexmark.ext.gfm.issues import GfmIssuesExtension
from com.vladsch.flexmark.ext.gfm.strikethrough import StrikethroughExtension
from com.vladsch.flexmark.ext.gfm.tasklist import TaskListExtension
from com.vladsch.flexmark.ext.gfm.users import GfmUsersExtension
from com.vladsch.flexmark.ext.gitlab import GitLabExtension
from com.vladsch.flexmark.ext.xwiki.macros import MacroExtension
from com.vladsch.flexmark.ext.attributes import AttributesExtension
from com.vladsch.flexmark.ext.yaml.front.matter import YamlFrontMatterExtension


from com.vladsch.flexmark.ast import Image
from com.vladsch.flexmark.util.ast import VisitHandler, Visitor
from com.vladsch.flexmark.util.sequence import BasedSequenceImpl

from com.vladsch.flexmark.ext.attributes import AttributeNode
from com.vladsch.flexmark.ext.xwiki.macros import Macro
from com.vladsch.flexmark.ext.xwiki.macros import MacroClose

from com.vladsch.flexmark.util.sequence import BasedSequence
from com.vladsch.flexmark.ast import HtmlInline, Text

class ProcessNodesVisitor(Visitor):
  def __init__(self, processor, folder):
    Visitor.__init__(self)
    self.processor = processor
    self.folder = folder
    self.absolutePaths = False
    
  def hasAbsolutePaths(self):
    return self.absolutePaths

  def setFolder(self, folder):
    self.folder = folder
    #print "FOLDER: ", repr(folder)
    
  def visit(self, node):
    #print type(node)
    if isinstance(node, Macro):
      print type(node), node.isClosedTag(), unicode(node.getName())
      if node.isClosedTag():
        macroValue = self.processor.getMacroValue(unicode(node.getName()))
        if macroValue!=None:
          node.getParent().insertBefore(HtmlInline(BasedSequenceImpl.of(macroValue)))
    elif isinstance(node,Image):
      url = unicode(node.url)
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
  if folder==None:
    pathname = fname
  else:
    pathname = os.path.join(folder,fname)
  #print "LOAD  : ", repr(pathname)
  f = io.open(pathname,"r",encoding="utf-8")
  markdown = f.read()
  f.close()
  return markdown

class MarkdownProcessor(object):
  def __init__(self,markdown, pathname, options):
    self.markdown = markdown
    self.pathname = pathname
    self.options = options
    self.parser=None
    self.renderer=None
    self.processNodes=None
    self.includeHtmlMap = HashMap()
    self.macros = dict()
    self.macros["pagebreak"] = '<div style="page-break-after: always"></div>\n'

  def getMacroValue(self, name):
    return self.macros.get(name,None)
    
  def process_document(self, pathname, doc):
    #print "PROCES: ", repr(pathname)
    folder = os.path.dirname(pathname)
    self.processNodes.setFolder(folder)
    self.processNodes.visit(doc)
    
    # see if document has includes
    if doc.contains(JekyllTagExtension.TAG_LIST):
      tagList = JekyllTagExtension.TAG_LIST.get(doc)
      for tag in tagList:
        tagName = tag.getTag()
        if tagName.equals("include"):
          includeFile = tag.getParameters().toString()
          if not includeFile in ("",None):
            text = loadMDFile(folder, includeFile)            
            includeFile = os.path.join(folder, includeFile)
            tag.setParameters(BasedSequenceImpl.of(includeFile))
            if includeFile.endswith(".md") :
              includeDoc = self.parser.parse(text)
              self.process_document(includeFile, includeDoc)
              includeHtml = self.renderer.render(includeDoc)
              self.includeHtmlMap.put(includeFile, includeHtml)
              # copy any definition of reference elements from included file to our document
              self.parser.transferReferences(doc, includeDoc, None)
            else:
              self.includeHtmlMap.put(includeFile, text)
      if not self.includeHtmlMap.isEmpty():
        doc.set(JekyllTagExtension.INCLUDED_HTML, self.includeHtmlMap)
  
    
  def toHtml(self):
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
       TypographicExtension.create(),
       EmojiExtension.create(),
       DefinitionExtension.create(),
       GfmIssuesExtension.create(),
       StrikethroughExtension.create(),
       TaskListExtension.create(),
       GfmUsersExtension.create(),
       GitLabExtension.create(),
       MacroExtension.create(),
       AttributesExtension.create(),
       YamlFrontMatterExtension.create()
      ]
    )
    options.set(JekyllTagExtension.ENABLE_INLINE_TAGS, True)
    options.set(JekyllTagExtension.ENABLE_BLOCK_TAGS, True)
    options.set(JekyllTagExtension.ENABLE_RENDERING, False)
    #options.set(EmojiExtension.ROOT_IMAGE_PATH, "/img/")
    options.set(GfmIssuesExtension.GIT_HUB_ISSUES_URL_ROOT,"https://redmine.gvsig.net/redmine/issues/")
    options.set(GitLabExtension.RENDER_BLOCK_MATH,False)
    options.set(GitLabExtension.RENDER_BLOCK_MERMAID,False)
    options.set(MacroExtension.ENABLE_RENDERING,False)
  
    self.parser = Parser.builder(options).build()
    self.renderer = HtmlRenderer.builder(options).build()
    self.processNodes = ProcessNodesVisitor(self, os.path.dirname(self.pathname))
  
    doc = self.parser.parse(self.markdown)
    self.process_document(self.pathname, doc)
    html = self.renderer.render(doc);
    
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
    if self.processNodes.hasAbsolutePaths() and self.options.get("allowgui",False):
      composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
      commonsdialog.msgbox(
        "Se han utilizado rutas absolutas en alguna de las imagenes\nEs recomendable usar solo rutas relativas.", 
        "MarkupText preview", 
        commonsdialog.IDEA, 
        root=composer
      )
      
    return html

def toHtml(markdown, pathname, **kwargs):
  processor = MarkdownProcessor(markdown,pathname,kwargs)
  return processor.toHtml()
  
def selfRegister():
  pass

def test(*args):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  unit = composer.getLauncherSelectedUnit()
  if unit == None:
    composer.msgbox(
      "MarkupText preview",
      "Debera seleccionar un elemento en el arbol de proyectos."
    )
    return

  pathname = unit.getFiles()[0].getAbsolutePath()
  markdown = loadMDFile(None, pathname)
  
  html = toHtml(markdown, pathname, allowgui=True)
  
  foldersManager = ToolsLocator.getFoldersManager()
  temp_html = foldersManager.getTemporaryFile("markuptext-preview.html")
  f = open(temp_html.getAbsolutePath(),"w")
  f.write(html)
  f.close()

  dockPanel = composer.getDock().get("#MarkupTextPreview")
  if dockPanel == None:
    browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
    dockPanel = composer.getDock().add(
      "#MarkupTextPreview",
      "MarkupText preview",
      browser,JScriptingComposer.Dock.DOCK_LEFT
    )
  else:
    browser = dockPanel.getComponent()    
  composer.getDock().select("#MarkupTextPreview")   
  browser.location(temp_html.toURI().toURL())

def main(*args):
  """
  Ejemplo de insercion de una imagen muy grande que se redimensiona al
  tamaño adecuado para que quepa en la pagina (650).
![Menu de conexión al espacio de trabajo](importacion_datos_files/menu_conexion_espacio_trabajo.png){ width=650 }  

  Estaria bien tener herramientas como:
  - Insertar imagen (que seleccionamos un fichero imagen, el alt, el caption, with y height y la inserte)  
  - Editar imagen (este para nota, siempre se puede eliminar y volver a insertar)
  - Incluir fichero
  - asignar encoding
  - Que al cargar md lea el encoding

"""
  test()
  
  