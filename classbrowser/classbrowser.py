# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel, getResource, load_icon
from gvsig import commonsdialog 

import fnmatch
import copy

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 

from java.lang.reflect import Modifier
from java.lang.reflect import Field
from StringIO import StringIO
from operator import attrgetter

from addons.ScriptingComposerTools.codenavigator.codeNavigator import NavigatorCellRenderer, CodeNavigatorTreeModel
from addons.ScriptingComposerTools.codenavigator.codeNavigator import CodeElement, TYPE_TEXT, TYPE_METHOD, TYPE_CLASS

from javax.swing import Action
from org.gvsig.tools import ToolsLocator
from java.awt.event import KeyEvent
from javax.swing import KeyStroke
from java.awt.event import InputEvent
from javax.swing import AbstractAction

from java.awt.datatransfer import StringSelection
from java.awt import Toolkit

from javax.swing import JComponent

from java.awt.event import ActionListener

class Inspector(object):  
  def __init__(self,theClass):
    self.theClass = theClass
    self.imports = list()
    self.lines = self.getLines()

  def getClassName(self,aClass=None):
    if aClass == None:
      aClass = self.theClass
    try:    
      s = aClass.__name__
    except:
      s = str(aClass)
    if s.endswith(";"):
      s = s[:-1]
    try:
      name = aClass.getName()
    except:
      name = str(aClass)[7:-2]

    if name.startswith("[L"):
      name = name[2:-1]
      
    if not name in ("void", "boolean", "char","byte", "int", "long", "float", "double"):
      if not name in self.imports :
        self.imports.append(name)
    return s
      
  def fieldToString(self,f):
    s = ""
    modifiers = f.getModifiers()
    if Modifier.isPublic(modifiers):
      s += "public "
    if Modifier.isStatic(modifiers):
      s += "static "
    if Modifier.isFinal(modifiers):
      s += "final "
    s += self.getClassName(f.getType()) + " " + f.getName()
    return s

  def methodToString(self,m):
    s = ""
    modifiers = m.getModifiers()
    if Modifier.isPublic(modifiers):
      s += "public "
    if Modifier.isStatic(modifiers):
      s += "static "
    rt = m.getReturnType()
    s += self.getClassName(rt) + " " + m.getName() + "("
    for p in m.getParameterTypes():
      s += self.getClassName(p) + ", "
    if s[-2:] ==", ":
      s = s[0:-2]
    s += ")"
    return s  

  def methodToString2(self,m):
    s = ""
    modifiers = m.getModifiers()
    if Modifier.isStatic(modifiers):
      s += "static "
    rt = m.getReturnType()
    s += m.getName() + "("
    for p in m.getParameterTypes():
      s += self.getClassName(p) + ", "
    if s[-2:] ==", ":
      s = s[0:-2]
    s += "): " + self.getClassName(rt)
    return s  

  def getMethods(self):
    methods = list()
    for m in self.theClass.getMethods():
      methods.append(self.methodToString2(m))
    return methods
  
  def getLines(self):
    lines = list()
    
    staticsfields = list()
    fields = list()
  
    staticsmethods = list()
    methods = list()
  
    for f in self.theClass.getFields():
      modifiers = f.getModifiers()
      if Modifier.isStatic(modifiers):
        staticsfields.append(f)
      else:
        fields.append(f)
  
    for m in self.theClass.getMethods():
      modifiers = m.getModifiers()
      if Modifier.isStatic(modifiers):
        staticsmethods.append(m)
      else:
        methods.append(m)
    for ee in (staticsfields, fields, staticsmethods, methods):
      ee.sort(key=attrgetter('name'))
      for e in ee:
        if isinstance(e,Field):
          lines.append(self.fieldToString(e))
        else:
          lines.append(self.methodToString(e))
      lines.append("")
    self.imports.sort()
    return lines
    
  def __str__(self):
    s = StringIO()
    s.write("package ")
    s.write(self.theClass.getPackage().getName())
    s.write("\n\n")
        
    for line in self.imports:
        s.write("import ")
        s.write(line)
        s.write("\n")
    s.write("\nclass %s {\n\n" % self.theClass.getSimpleName())
    for line in self.lines:
      if line.strip() != "":
        s.write("    ")
        s.write(line)
        s.write("\n")
    s.write("\n}\n")
    ss = s.getvalue()
    s.close()
    return ss

  def toString(self):
    return str(self)

def getClassByName(fullClassName):
  try:
    fullClassName = fullClassName.strip()
    n = fullClassName.rfind(".")
    packageName = fullClassName[:n]
    className = fullClassName[n+1:]
    names = dict()
    statement = "from %s import %s" % (packageName,className)  
    #print "exec: %s" % statement
    exec statement in names
    return names[className]
  except:
    return None

class ClassBrowserDialog(FormPanel,Component):
  def __init__(self, javadocs=None ):
    FormPanel.__init__(self, getResource(__file__,"classbrowserdialog.xml"))
    self.setPreferredSize(500,400)
    self.__javadocs = javadocs
    if self.__javadocs == None :
      composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
      p = composer.getDock().get("#JavadocNavigator")
      self.__javadocs = p.getComponent().getJavadoc()
    self.treeClass.setCellRenderer( 
        NavigatorCellRenderer(
          self.load_icon((__file__,"images","references.png")),
          self.load_icon((__file__,"images","modulo.png")),
          self.load_icon((__file__,"images","clase.png")),
          self.load_icon((__file__,"images","metodo.png")),
          self.load_icon((__file__,"images","funcion1.png")),
          self.load_icon((__file__,"images","text.png")),
          self.load_icon((__file__,"images","import.png"))
      )
    )    
    self.__root = CodeElement(TYPE_CLASS,"...",0,0)
    self.treeClass.setModel(CodeNavigatorTreeModel(self.__root))

  def txtClassName_keyPressed(self, event):
    if event.getKeyCode()==27:
      self.hide()
      return
    if event.getKeyCode()==40:
      self.txtSearch.requestFocusInWindow()
      return
    if event.getKeyChar()=="\n":
      className = self.txtClassName.getText()
      theClass = getClassByName(className)
      if theClass==None:
        founds = self.doSearch(className)
        self.cboSearchs.removeAllItems()
        for className in founds:
          self.cboSearchs.addItem(className)
        self.cboSearchs.requestFocusInWindow()
      else:
        inspector = Inspector(theClass)
        self.__root = CodeElement(TYPE_CLASS,inspector.getClassName(),0,0)
        for method in inspector.getMethods():
          if method.startswith("static "):
            self.__root.addChild(CodeElement(TYPE_TEXT,method[7:],0,0))
          else:
            self.__root.addChild(CodeElement(TYPE_METHOD,method,0,0))
        self.treeClass.setModel(CodeNavigatorTreeModel(self.__root))
        self.txtSearch.requestFocusInWindow()    
        
  def txtSearch_change(self,*args):
    rootfiltered = copy.deepcopy(self.__root)
    rootfiltered.retainElements(self.txtSearch.getText())
    model = CodeNavigatorTreeModel(rootfiltered)
    self.treeClass.setModel(model)
    self.expandAll()
    self.treeClass.setSelectionRow(0)        

  def txtSearch_keyPressed(self, event):
    if event.getKeyCode()==27:
      self.hide()
      return
    if event.getKeyCode()==40:
      self.treeClass.requestFocusInWindow()
      return
    if event.getKeyCode()==38:
      self.txtClassName.requestFocusInWindow()
    
  def cboSearchs_keyPressed(self, event):
    if event.getKeyChar()=="\n":
      self.txtClassName.setText(self.cboSearchs.getSelectedItem())
      self.txtClassName.requestFocusInWindow()

  def btnCopy_click(self, *e):
    path = self.treeClass.getSelectionPath()
    if path == None:
      return
    element = path.getLastPathComponent()
    if element == None:
      return
    s = element.getName()
    n = s.find(":")
    if n>0 :
      s = s[:n]
    selection = StringSelection(s)
    clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
    clipboard.setContents(selection, selection)
    self.hide()

  def treeClass_keyPressed(self, event):
    if event.getKeyCode()==27:
      self.hide()
      return
    if event.getKeyCode()==38 and self.treeClass.isRowSelected(0):
      self.txtSearch.requestFocusInWindow()
      return
    if event.getKeyChar()=="\n":
      self.btnInsert_click()
      return
    if event.getKeyCode()==67:
      self.btnCopy_click()
      return
      
  def btnInsert_click(self,*e):
    path = self.treeClass.getSelectionPath()
    if path == None:
      return
    element = path.getLastPathComponent()
    if element == None:
      return
    s = element.getName()
    n = s.find(":")
    if n>0 :
      s = s[:n]
    selection = StringSelection(s)
    clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
    clipboard.setContents(selection, selection)
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    composer.getCurrentEditor().getJTextComponent().replaceSelection(s)
    self.hide()
    #composer.
    
  def doSearch(self, searchClass):
    founds = list()
    searchClass = searchClass.lower()
    modules = self.__javadocs.getModules()
    for module in modules:
      if module == None:
        continue
      className = "%s.%s" % (module.getPackageName(), module.getName())
      if fnmatch.fnmatch(className.lower(), "*"+searchClass+"*"):
        founds.append(className)
        if len(founds)>100:
          break
    return founds

  def expandAll(self):
    row = 0
    rowCount = self.treeClass.getRowCount()
    while row < rowCount:
      self.treeClass.expandRow(row)
      rowCount = self.treeClass.getRowCount()
      row += 1
    
  def showWindow(self, title="Class browser"):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),title)
    #self.getRootPane().setDefaultButton(self.btnClose)

class ClassBrowserPanel(FormPanel,Component):
  def __init__(self):
    FormPanel.__init__(self, getResource(__file__,"classbrowserpanel.xml"))
    
  def btnSearch_click(self, *args):
    theClass = getClassByName(self.txtClassName.getText())
    if theClass == None:
      commonsdialog.msgbox("Clase no encontrada")
      return
    inspector = Inspector(theClass)
    self.txtOutput.setText(str(inspector))
    
def testpanel():
  panel = ClassBrowserPanel()
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  composer.getDock().add("#ClassBrowser","Class browser",panel,JScriptingComposer.Dock.DOCK_BOTTOM)
  composer.getDock().select("#ClassBrowser")
  panel.asJComponent().requestFocus()

def testdialog():
  panel = ClassBrowserDialog()
  panel.showWindow()

class ClassBrowserAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Class browser...")
    self.putValue(Action.ACTION_COMMAND_KEY, "ClassBrowserDialog")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","clase.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Search java classes and show methods")
    self.putValue(Action.ACCELERATOR_KEY, 
      KeyStroke.getKeyStroke(
        KeyEvent.VK_O, 
        InputEvent.CTRL_DOWN_MASK + InputEvent.SHIFT_DOWN_MASK
      )
    )

  def actionPerformed(self,e):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    p = composer.getDock().get("#JavadocNavigator")
    if p == None:
      commonsdialog.msgbox("It is necessary that the javadocs are loaded to use this functionality." , "Java class browser", commonsdialog.WARNING, root=composer)      
      return
    panel = ClassBrowserDialog()
    panel.showWindow()
  
  def isEnabled(self):
    return True

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = ClassBrowserAction()
  manager.addComposerMenu(i18nManager.getTranslation("Edit"),action1)
  
def main(*args):
  testdialog()
