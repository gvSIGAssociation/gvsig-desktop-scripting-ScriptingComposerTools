# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel, getResource

import os

from javax.swing import DefaultListModel
from javax.swing import DefaultComboBoxModel 

from org.gvsig.app import ApplicationLocator 

from StringIO import StringIO

from pylint import lint
from pylint.reporters import BaseReporter
import astroid.builder

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from addons.ScriptingComposerTools.codenavigator.codeanalizer import CodeAnalyzer

lint_options = [
    "--reports=n",
    "--errors-only",
    "--ignore-imports=y",
    "--disable=all",
    "--enable=undefined-variable",
    "--enable=global-variable-undefined",
    "--disable=typecheck,classes",

    ]

class FilePath(str):
  def __init__(self, path):
    str.__init__(self,path)
    self.stream = None
    self.source_code = None

  def copy(self,s):
    new = FilePath(s)
    new.stream = self.stream
    new.source_code = self.source_code
    return new

class Suggestion(object):
  def __init__(self, simpleClassName, packageNames):
    self.__simpleClassName = simpleClassName
    self.__packageName = None
    self.__packageNames = packageNames
    self.__packageName = self.__packageNames[0]
    #print "Suggestion(%r,%r)" % (self.__simpleClassName,self.__packageNames)

  def getSimpleClassName(self):
    return self.__simpleClassName

  def getPackageName(self):
    return self.__packageName

  def getPackageNames(self):
    return self.__packageNames

  def setPackageName(self,packageName):
    self.__packageName = packageName
  
  def __repr__(self):
    if self.getPackageName() in ("", None):
      return "import %s" % self.getSimpleClassName()
    else:
      return "from %s import %s" % (self.getPackageName(), self.getSimpleClassName())

class SimpleName(object):
  def __init__(self,name, module=""):
    self.__name = name.strip()
    self.__module = module.strip()

  def __str__(self):
    if self.__module in ("",None):
      return "import %s" % self.__name
    return "from %s import %s" % (self.__module, self.__name)
  __repr__ = __str__
  
  def getName(self):
    return self.__name
    
  def getModuleName(self):
    return self.__module

class ResolveImports(object):
  def __init__(self,javadocs, message):
    self.__suggestions = dict()
    self.__javadocs = javadocs
    self.__imports = dict()
    self.__globalNames = list()
    self.__localNames = list()
    self.__msg = message
    self.loadGlobalNames()
    
  def add(self, simpleClassName):
    if self.__suggestions.has_key(simpleClassName):
      return
    packages = list()
    if self.__javadocs!=None:
      for module in self.__javadocs.getModules():
        if module == None:
          continue
        if module.getName() == simpleClassName :
          packages.append(module.getPackageName())
    for pyname in self.__globalNames:
      if pyname.getName() == simpleClassName :
        packages.append(pyname.getModuleName())
    for pyname in self.__localNames:
      if pyname.getName() == simpleClassName :
        packages.append(pyname.getModuleName())
    
    if len(packages) > 0:
      self.__suggestions[simpleClassName] = Suggestion(simpleClassName,packages)

  def getSuggestions(self):
    return self.__suggestions.values()

  def loadGlobalNames(self):
    self.__msg("Imports resolver, load global names...")
    fname = getResource(__file__, "data", "definitions.txt")
    f = open(fname,"r")
    for line in f.readlines():
      line = line.strip()
      if line.startswith("#"):
        continue
      if "," in line:
        parts = line.split(",")
        name = SimpleName(parts[0],parts[1])
      else:
        name = SimpleName(line)
      self.__globalNames.append(name)
    f.close()

  def loadLocalNames(self, pathname):
    self.__msg("Imports resolver, load local names...")
    self.__localNames = list()
    self.__loadLocalNames(pathname, self.__localNames)
    
  def __loadLocalNames(self, pathname, localNames, pkg=""):
    folder = os.path.dirname(pathname)
    if not pkg in ("",None):
      pkg = pkg + "."
    for sourcefile in os.listdir(folder):
      initfile = os.path.join(folder, sourcefile,"__init__.py")
      #print "### initfile ", repr(initfile), os.path.isfile(initfile)
      if os.path.isfile(initfile):
        self.__loadLocalNames(initfile, localNames, pkg+sourcefile)
        continue
      if sourcefile.endswith(".py"):
        self.__msg("Imports resolver, scanning '%s'..." % sourcefile)
        moduleName = os.path.splitext(sourcefile)[0]
        if pkg in ("", None):
          localNames.append(SimpleName(moduleName,""))
        else:
          localNames.append(SimpleName(pkg[:-1], moduleName))
        try:
          codeAnalyzer = CodeAnalyzer()
          codeAnalyzer.load(os.path.join(folder,sourcefile))
          for name in codeAnalyzer.getModule().getChildren():
            if name.type in ("class", "function"):
              localNames.append(SimpleName(name.getName(), pkg+moduleName))
        except:
          pass
    
  def resolve(self, pathname, code):
    self.__imports = dict()
    code = code.strip()
    if code.startswith("# encoding:"):
      code = code.replace("# encoding:","# e n c o d i n g:",1)

    class MyReporter(BaseReporter):
      def __init__(self, resolver):
        BaseReporter.__init__(self)
        self.__resolver = resolver

      def _display(self,*args):
        pass

      def handle_message(self, msg):
        if getattr(msg,"symbol",None) == 'undefined-variable':
          m = msg.msg
          if m.startswith("Undefined variable '") and m.endswith("'"):
            self.__resolver.add(m[20:-1])
        

    self.__msg("Imports resolver, cheking '%s'..." % os.path.basename(pathname))
    filename = FilePath(pathname)
    filename.source_code = code

    astroid.builder.MANAGER.astroid_cache.clear()
    args = list()
    args.extend(lint_options)
    args.append(filename)

    try:
      reporter = MyReporter(self)
      lint.Run(args, reporter=reporter, exit=False)
      self.__msg("")
    except:
      self.__msg("Imports resolver, can't check file")

class AddImportsPanel(FormPanel):
  def __init__(self, editor, suggestions=None, javadocs=None):
    FormPanel.__init__(self, getResource(__file__,"addimportspanel.xml"))
    self.__composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if suggestions == None:
      if javadocs == None :
        self.message("Imports resolver, getings javadocs...")
        p = self.__composer.getDock().get("#JavadocNavigator")
        if p != None:
          javadocs = p.getComponent().getJavadoc()
      resolver = ResolveImports(javadocs, message=self.message)
      code = editor.getJTextComponent().getText()
      fname = editor.getScript().getScriptFile().getAbsolutePath()
      resolver.loadLocalNames(fname)
      resolver.resolve(fname,code)
      suggestions = resolver.getSuggestions()
    self.setSuggestions(suggestions)
    self.__editor = editor
    self.setPreferredSize(450,250)

  def message(self, msg):
    self.__composer.getStatusbar().message(msg)
    
  def setSuggestions(self, suggestions):
    self.__suggestions = suggestions
    model = DefaultListModel()
    self.__suggestions.sort(cmp=lambda x,y:cmp(str(x).lower(),str(y).lower()))
    for suggestion in self.__suggestions:
      model.addElement(suggestion)
    self.lstSuggestions.setModel(model)
    
  def btnCancel_click(self,*args):
    self.hide()

  def btnAccept_click(self,*args):
    self.insertImports()
    self.hide()
    
  def lstSuggestions_change(self, *args):
    x = self.lstSuggestions.getSelectedValue()
    if x == None:
      return
    self.txtClass.setText(x.getSimpleClassName())
    model = DefaultComboBoxModel()    
    for package in x.getPackageNames():
      model.addElement(package)
    self.cboPackages.setModel(model)

  def cboPackages_change(self,*args):
    suggestion = self.lstSuggestions.getSelectedValue()
    if suggestion == None:
      return
    x = self.cboPackages.getSelectedItem()
    if x == None:
      return
    suggestion.setPackageName(x)
    self.setSuggestions(self.__suggestions) # refresh list

  def btnRemove_click(self,*args):
    suggestion = self.lstSuggestions.getSelectedValue()
    if suggestion == None:
      return
    n = self.__suggestions.index(suggestion)
    del self.__suggestions[n]
    self.setSuggestions(self.__suggestions) # refresh list
         
  def btnCopy_click(self,*args):
    application = ApplicationLocator.getManager()
    application.putInClipboard(self.getImports())
    
  def showWindow(self, title="Fix java imports"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)

  def getImports(self):
    x = StringIO()
    self.__suggestions.sort(cmp=lambda x,y:cmp(str(x).lower(),str(y).lower()))
    for suggestion in self.__suggestions:
      x.write(str(suggestion))
      x.write("\n")
    return x.getvalue()
      
  def insertImports(self):
    code = self.__editor.getJTextComponent().getText().split("\n")
    charcount = 0
    for line in code:
      linelen = len(line)+1
      line = line.lstrip()
      if not ( line==""
        or line.startswith("#") 
        or line.startswith("from ") 
        or line.startswith("import ")
        or line.startswith("reload(") 
        or line.startswith("use_plugin(")
        ):
        break
      charcount += linelen
    self.__editor.getJTextComponent().insert(self.getImports()+"\n",charcount)
    
        
def test():
  editor=None
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer.getDock().get("#JavadocNavigator") == None:
    print "You must open the javadocs in order to use this functionality"
    return
    
  for panel in composer.getDock():
    if panel.getId().endswith("/test.inf"):
      editor = panel.getComponent()
      break
  if editor == None:
    print "No localizado el editor de pruebas. Debera tener abierto el script 'test'"
    return

  panel = AddImportsPanel(editor)
  panel.showWindow()

def test2():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  editor = composer.getCurrentEditor()
  code = editor.getJTextComponent().getText().split("\n")
  linecount = 0
  charcount = 0
  for line in code:
    linelen = len(line)+1
    line = line.lstrip()
    print repr(line)
    if not (line=="" or line.startswith("#") or line.startswith("from ") or line.startswith("import ")):
      break
    linecount += 1
    charcount += linelen
    
  print linecount, charcount
  editor.getJTextComponent().insert(charcount)
  
def main(*args):
  test()
  pass
  