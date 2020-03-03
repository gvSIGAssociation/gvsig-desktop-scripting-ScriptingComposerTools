# encoding: utf-8

import gvsig

from gvsig import commonsdialog

import os
import os.path
import io
import StringIO

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
from com.vladsch.flexmark.ast import HtmlInline, Text, FencedCodeBlock

def format_code(langname, code):
  import pygments
  from pygments.formatters.html import HtmlFormatter
  from pygments.lexers import get_lexer_by_name
  from pygments.styles import get_style_by_name
  
  html = StringIO.StringIO()
  lexer = get_lexer_by_name(langname)
  formatter = HtmlFormatter(style='default')
  #styles = formatter.get_style_defs()
  #html.write("<style>\n")
  #html.write(styles)
  #html.write("</style>\n")
  pygments.highlight(code, lexer, formatter, html)
  return html.getvalue()

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
    if isinstance(node, FencedCodeBlock):
      try:
        code = StringIO.StringIO()
        for l in node.getContentLines():
          code.write(unicode(l))
        html = format_code(unicode(node.getInfo()), code.getvalue())
        node.insertBefore(HtmlInline(BasedSequenceImpl.of(html)))
        node.unlink()
      except:
        pass
      
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

/* pygments styles */
.hll { background-color: #ffffcc }
.c { color: #408080; font-style: italic } /* Comment */
.err { border: 1px solid #FF0000 } /* Error */
.k { color: #008000; font-weight: bold } /* Keyword */
.o { color: #666666 } /* Operator */
.ch { color: #408080; font-style: italic } /* Comment.Hashbang */
.cm { color: #408080; font-style: italic } /* Comment.Multiline */
.cp { color: #BC7A00 } /* Comment.Preproc */
.cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
.c1 { color: #408080; font-style: italic } /* Comment.Single */
.cs { color: #408080; font-style: italic } /* Comment.Special */
.gd { color: #A00000 } /* Generic.Deleted */
.ge { font-style: italic } /* Generic.Emph */
.gr { color: #FF0000 } /* Generic.Error */
.gh { color: #000080; font-weight: bold } /* Generic.Heading */
.gi { color: #00A000 } /* Generic.Inserted */
.go { color: #888888 } /* Generic.Output */
.gp { color: #000080; font-weight: bold } /* Generic.Prompt */
.gs { font-weight: bold } /* Generic.Strong */
.gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.gt { color: #0044DD } /* Generic.Traceback */
.kc { color: #008000; font-weight: bold } /* Keyword.Constant */
.kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
.kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
.kp { color: #008000 } /* Keyword.Pseudo */
.kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
.kt { color: #B00040 } /* Keyword.Type */
.m { color: #666666 } /* Literal.Number */
.s { color: #BA2121 } /* Literal.String */
.na { color: #7D9029 } /* Name.Attribute */
.nb { color: #008000 } /* Name.Builtin */
.nc { color: #0000FF; font-weight: bold } /* Name.Class */
.no { color: #880000 } /* Name.Constant */
.nd { color: #AA22FF } /* Name.Decorator */
.ni { color: #999999; font-weight: bold } /* Name.Entity */
.ne { color: #D2413A; font-weight: bold } /* Name.Exception */
.nf { color: #0000FF } /* Name.Function */
.nl { color: #A0A000 } /* Name.Label */
.nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
.nt { color: #008000; font-weight: bold } /* Name.Tag */
.nv { color: #19177C } /* Name.Variable */
.ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
.w { color: #bbbbbb } /* Text.Whitespace */
.mb { color: #666666 } /* Literal.Number.Bin */
.mf { color: #666666 } /* Literal.Number.Float */
.mh { color: #666666 } /* Literal.Number.Hex */
.mi { color: #666666 } /* Literal.Number.Integer */
.mo { color: #666666 } /* Literal.Number.Oct */
.sa { color: #BA2121 } /* Literal.String.Affix */
.sb { color: #BA2121 } /* Literal.String.Backtick */
.sc { color: #BA2121 } /* Literal.String.Char */
.dl { color: #BA2121 } /* Literal.String.Delimiter */
.sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
.s2 { color: #BA2121 } /* Literal.String.Double */
.se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
.sh { color: #BA2121 } /* Literal.String.Heredoc */
.si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
.sx { color: #008000 } /* Literal.String.Other */
.sr { color: #BB6688 } /* Literal.String.Regex */
.s1 { color: #BA2121 } /* Literal.String.Single */
.ss { color: #19177C } /* Literal.String.Symbol */
.bp { color: #008000 } /* Name.Builtin.Pseudo */
.fm { color: #0000FF } /* Name.Function.Magic */
.vc { color: #19177C } /* Name.Variable.Class */
.vg { color: #19177C } /* Name.Variable.Global */
.vi { color: #19177C } /* Name.Variable.Instance */
.vm { color: #19177C } /* Name.Variable.Magic */
.il { color: #666666 } /* Literal.Number.Integer.Long */
.highlight {background-color: #f1f1f1 }
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
  
  