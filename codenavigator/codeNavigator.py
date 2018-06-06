
from gvsig import *
from gvsig.libs.formpanel import FormPanel, load_icon
from gvsig import commonsdialog

import copy
from StringIO import StringIO
from os.path import basename, dirname, join


from java.awt.event import MouseEvent
from java.awt.event import ActionListener

from javax.swing.tree import DefaultTreeCellRenderer
from javax.swing.tree import TreeModel
from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel
from javax.swing.event import ChangeListener
from javax.swing.event import TreeModelEvent
from javax.swing.tree import TreePath

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 

from codeanalizer import TYPE_ROOT
from codeanalizer import TYPE_FOLDER
from codeanalizer import TYPE_MODULE 
from codeanalizer import TYPE_CLASS 
from codeanalizer import TYPE_METHOD 
from codeanalizer import TYPE_FUNCTION 
from codeanalizer import TYPE_TEXT
from codeanalizer import TYPE_IMPORT 
from codeanalizer import CodeElement
from codeanalizer import CodeAnalyzer

class CodeNavigatorTreeModel(TreeModel):
  def __init__(self,root):
    self._root = root
    self.listeners = dict()

  def getRoot(self):
    return self._root

  def getChild(self, parent, index):
    return parent.getChildren()[index]

  def getChildCount(self, parent):
    return len(parent.getChildren())

  def isLeaf(self, node):
    return len(node.getChildren())==0

  def getIndexOfChild(self, parent, child):
    children = parent.getChildren()
    if children == None:
      return -1
    try:
      return children.index(child)
    except ValueError:
      #print "Can't find child '%s' in parent '%s'" % (child, parent)
      return -1

  def valueForPathChanged(self, path, value):
    pass

  def addTreeModelListener(self,listener) :
    self.listeners[listener] = listener

  def removeTreeModelListener(self, listener):
    del self.listeners[listener]

  def fireChanged(self):
    event = TreeModelEvent(self, TreePath(self.getRoot()))
    for listener in self.listeners.itervalues():
      listener.treeStructureChanged(event)

class NavigatorCellRenderer(DefaultTreeCellRenderer):
  def __init__(self, icon_root, icon_module, icon_class, icon_method, icon_function, icon_text, icon_import=None):
    self.icon_root = icon_root
    self.icon_module = icon_module
    self.icon_class = icon_class
    self.icon_method = icon_method
    self.icon_function = icon_function
    self.icon_text = icon_text
    if icon_import == None:
      self.icon_import = icon_function
    else:
      self.icon_import = icon_import
    
  def getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused):
    c = DefaultTreeCellRenderer.getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused)
    if isinstance(value,CodeElement):
      if value.type == TYPE_ROOT:
        icon = self.icon_root
      elif value.type == TYPE_FOLDER:
        icon = None
      elif value.type == TYPE_MODULE:
        icon = self.icon_module
      elif value.type == TYPE_CLASS:
        icon = self.icon_class
      elif value.type == TYPE_METHOD:
        icon = self.icon_method
      elif value.type == TYPE_FUNCTION:
        icon = self.icon_function
      elif value.type == TYPE_TEXT:
        icon = self.icon_text
      elif value.type == TYPE_IMPORT:
        icon = self.icon_import
      else:
        logger("Type of element %r not supported" % value.type,LOGGER_WARN)
        icon = None
      if icon!=None:
        self.setIcon(icon)
    return c
    
class CodeNavigatorDialog(FormPanel):

  def __init__(self, composer):
    FormPanel.__init__(self)
    self.root = None
    self.composer = composer
    self.editor = self.composer.getCurrentEditor()
    self.load(getResource(__file__,"codeNavigatorDialog.xml"))
    self.treeCodeNavigator.setCellRenderer( 
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
    root = CodeElement(TYPE_ROOT,"<unknown>",0,0)
    self.treeCodeNavigator.setModel(CodeNavigatorTreeModel(root))
    
    self.setPreferredSize(300,400)
    
  def txtSearch_change(self,*args):
    rootfiltered = copy.deepcopy(self.root)
    rootfiltered.retainElements(self.txtSearch.getText())
    codeNavigatorTreeModel = CodeNavigatorTreeModel(rootfiltered)
    self.treeCodeNavigator.setModel(codeNavigatorTreeModel)
    self.expandAll()
    self.treeCodeNavigator.setSelectionRow(0)
    
  def update(self):
    self.editor = self.composer.getCurrentEditor()
    if self.editor == None:
      self.treeCodeNavigator.setModel(DefaultTreeModel(DefaultMutableTreeNode()))
      return
    script = self.editor.getScript()
    fname = script.getResource(script.getId()+".py").getAbsolutePath()
    self.load_module(fname, inputFile=StringIO(self.editor.getJTextComponent().getText()))
    
  def load_module(self, fname,search=None, inputFile=None):
    analyzer = CodeAnalyzer()
    analyzer.load(fname,search=search, inputFile=inputFile)
    if search!=None:
      analyzer.removeEmptyElemens()
    self.root = analyzer.getModule()
    codeNavigatorTreeModel = CodeNavigatorTreeModel(self.root)
    self.treeCodeNavigator.setModel(codeNavigatorTreeModel)
    self.expandAll()
    self.treeCodeNavigator.setSelectionRow(0)

  def getModel(self):
    return self.treeCodeNavigator.getModel()
    
  def expandAll(self):
    row = 0
    rowCount = self.treeCodeNavigator.getRowCount()
    while row < rowCount:
      self.treeCodeNavigator.expandRow(row)
      rowCount = self.treeCodeNavigator.getRowCount()
      row += 1
      
  def btnClose_click(self,*args):
    self.hide()

  def show(self):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),"Navigator")
    self.getRootPane().setDefaultButton(self.btnGoToSource)

  def btnGoToSource_click(self,*args):
    path = self.treeCodeNavigator.getSelectionPath()
    if path == None:
      return
    element = path.getLastPathComponent()
    if element == None:
      return
    self.goToLine(element.lineno+1)
    self.hide()
    
  def goToLine(self, lineno):
    if self.editor == None:
      return
    self.editor.gotoline(lineno)
    self.editor.getJTextComponent().requestFocus()

class CodeNavigatorPanel(FormPanel,ChangeListener,ActionListener,Component):

  def __init__(self, composer, search=None):
    FormPanel.__init__(self)
    self.root = None
    self.search = search
    self.updating = False
    self.composer = composer
    self.editor = self.composer.getCurrentEditor()
    self.load(getResource(__file__,"codeNavigatorPanel.xml"))
    self.treeCodeNavigator.setCellRenderer( 
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
    root = CodeElement(TYPE_ROOT,"<unknown>",0,0)
    self.treeCodeNavigator.setModel(CodeNavigatorTreeModel(root))

    self.composer.addChangeEditorListener(self)
    self.composer.getDock().addActivateListener(self)

  def actionPerformed(self,event):
    if self.search==None:
      self.update()
        
  def stateChanged(self,event):
    if self.search == None:
      self.update()

  def requestFocus(self):
    self.treeCodeNavigator.requestFocus()
    
  def getModel(self):
    return self.treeCodeNavigator.getModel()
    
  def update(self):
    if self.updating :
      return
    self.composer.getStatusbar().message("Updading navigator...")
    try:
      self.updating = True
      self.editor = self.composer.getCurrentEditor()
      if self.editor == None:
        self.treeCodeNavigator.setModel(DefaultTreeModel(DefaultMutableTreeNode()))
        return
      script = self.editor.getScript()
      fname = script.getResource(script.getId()+".py").getAbsolutePath()
      self.load_module(fname, inputFile=StringIO(self.editor.getJTextComponent().getText()))
    finally:
      self.updating = False
      self.composer.getStatusbar().clear()
      
  def load_module(self, fname, search=None, inputFile=None):
    analyzer = CodeAnalyzer()
    analyzer.load(fname,search=search, inputFile=inputFile)
    if search!=None:
      analyzer.removeEmptyElemens()
    self.root = analyzer.getModule()
    codeNavigatorTreeModel = CodeNavigatorTreeModel(self.root)
    self.treeCodeNavigator.setModel(codeNavigatorTreeModel)
    self.expandAll()
    self.treeCodeNavigator.setSelectionRow(0)
    self.search = search
    
  def expandAll(self):
    row = 0
    rowCount = self.treeCodeNavigator.getRowCount()
    while row < rowCount:
      codeElement = self.treeCodeNavigator.getPathForRow(row).getLastPathComponent()
      if codeElement.type == TYPE_IMPORT:
        self.treeCodeNavigator.collapseRow(row)
      else:
        self.treeCodeNavigator.expandRow(row)
      rowCount = self.treeCodeNavigator.getRowCount()
      row += 1

  def treeCodeNavigator_mouseClick(self,e):
    if e.getClickCount() == 2 and e.getID() == MouseEvent.MOUSE_CLICKED and e.getButton() == MouseEvent.BUTTON1:
      path = self.treeCodeNavigator.getSelectionPath()
      if path == None:
        return
      element = path.getLastPathComponent()
      if element == None:
        return
      self.goToLine(element.lineno+1)
    
  def goToLine(self, lineno):
    if self.editor == None:
      return
    self.editor.gotoline(lineno)
    self.editor.getJTextComponent().requestFocus()
    
  
def test2():
  p = CodeNavigatorPanel(composer = ScriptingSwingLocator.getUIManager().getActiveComposer())
  p.load_module(getResource(__file__))#,search="load")
  p.showWindow("xx")
  
  
def main(*args):
  test2()
  