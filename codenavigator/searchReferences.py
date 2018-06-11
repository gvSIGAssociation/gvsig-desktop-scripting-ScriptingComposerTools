# encoding: utf-8

from gvsig import *
from gvsig.libs.formpanel import FormPanel

import os.path
from StringIO import StringIO
import threading

from java.awt import BorderLayout
import javax.swing.ButtonGroup

from org.gvsig.tools.visitor import Visitor

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.scripting import ScriptingLocator
from org.gvsig.scripting import ScriptingScript


import codeNavigator
reload(codeNavigator)
import codeanalizer
reload(codeanalizer)

from codeNavigator import *
from codeanalizer import *

class SearchReferencesPanel(FormPanel, Visitor):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"searchReferences.xml"))
    self.composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    self.navigator = None
    try:
      self.editor = self.composer.getDock().getSelected(JScriptingComposer.Dock.DOCK_CENTER).getComponent()
    except:
      self.editor = None
    self.initComponents()
    
  def initComponents(self):
    manager = ScriptingSwingLocator.getUIManager()
    self.browser = manager.createBrowser(manager.getManager().getUserFolder(),True)
    self.containerScriptingBrowser.setLayout(BorderLayout())
    self.containerScriptingBrowser.add(self.browser.asJComponent(), BorderLayout.CENTER)

    self.btgFindMode = javax.swing.ButtonGroup()
    self.btgFindMode.add(self.rdbFindText)
    self.btgFindMode.add(self.rdbFindIdentifier)
    self.btgFindMode.add(self.rdbFindClasses)
    self.btgFindMode.add(self.rdbFindMethods)
    self.btgFindMode.add(self.rdbFindFunctions)

    self.btgScope = javax.swing.ButtonGroup()
    self.btgScope.add(self.rdbCurrentFile)
    self.btgScope.add(self.rdbCurrentFolder)
    self.btgScope.add(self.rdbCustom)

    if self.editor == None:
      self.rdbCurrentFile.setEnabled(False)
      self.rdbCurrentFolder.setEnabled(False)
      self.rdbCustom.setSelected(True)
    else:
      self.rdbCurrentFile.setEnabled(True)
      self.rdbCurrentFolder.setEnabled(True)
      self.rdbCurrentFile.setSelected(True)
      script = self.editor.getScript()
      self.txtCurrentFile.setText("%s (%s)" % (script.getName(),self.getPath(script)))
      self.txtCurrentFolder.setText("%s (%s)" % (script.getParent().getName(),self.getPath(script.getParent())))
      try:
        s = self.editor.getJTextComponent().getSelectedText()
        self.txtSearchText.setText(s)
      except:
        pass
    self.rdbFindText.setSelected(True)

    self.setPreferredSize(540,430)

  def show(self):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),"Find references")

  def getMode(self):
    if self.rdbFindText.isSelected():
      return MODE_TEXT
    if self.rdbFindIdentifier.isSelected():
      return MODE_IDENTIFIER
    if self.rdbFindClasses.isSelected():
      return MODE_CLASS
    if self.rdbFindMethods.isSelected():
      return MODE_METHOD
    if self.rdbFindFunctions.isSelected():
      return MODE_FUNCTION
    return None

  def getSearchText(self):
    return self.txtSearchText.getText()
    
  def rdbCustom_change(self, *args):
    self.browser.setEnabled(self.rdbCustom.isSelected())

  def rdbCurrentFolder_change(self, *args):
    self.browser.setEnabled(self.rdbCustom.isSelected())
    
  def rdbCurrentFile_change(self, *args):
    self.browser.setEnabled(self.rdbCustom.isSelected())
    
  def btnFind_click(self,*args):
    if self.rdbCurrentFile.isSelected():
      unit = self.editor.getScript()
    elif self.rdbCurrentFolder.isSelected():
      unit = self.editor.getScript().getParent()
    elif self.rdbCustom.isSelected():
      unit = self.browser.getSelectedNode()
    
    if unit == None:
      return
    search = self.txtSearchText.getText()
    if search in ("",None):
      return
      
    self.navigator = CodeNavigatorPanel(self.composer, search=search)
    self.navigator.getModel().getRoot().setName("[ references of '%s' ]" % search)
    #self.searchReferences(unit)
    self.composer.getDock().add("#References","References",self.navigator,JScriptingComposer.Dock.DOCK_BOTTOM)
    self.composer.getDock().select("#References")
    self.navigator.requestFocus()
    
    threading.Thread(target=self.searchReferences, name="SearchReferences", args=(unit,)).start()
    self.hide()

  def searchReferences(self, unit):
    mode = self.getMode()
    search = self.getSearchText()
    try:
      self.composer.getStatusbar().message("Searching...")
      if isinstance(unit,ScriptingScript ):
        fname = unit.getResource(unit.getId()+".py").getAbsolutePath()
        inputFile=StringIO(self.editor.getJTextComponent().getText())
        analyzer = CodeAnalyzer()
        analyzer.load(fname,search=search, inputFile=inputFile)
        analyzer.removeEmptyElemens()
        module = analyzer.getModule()
        module.name = self.getPath(File(module.fname))
        model = self.navigator.getModel()
        model.getRoot().addChild(module)
        model.fireChanged()
      else:
        unit.accept(self)
      self.navigator.expandAll()
      self.composer.getStatusbar().clear()
        
    except Exception, ex:
      logger("Error searching references, search=%r, mode=%r, unit=%s" % (search, mode, unit), LOGGER_WARN,ex)
      
  def getPath(self,unit):
    root = ScriptingLocator.getManager().getUserFolder()
    if isinstance(unit,File):
      p1 = unit.getCanonicalPath()
    else:
      p1 = unit.getFile().getCanonicalPath()
    p2 = root.getFile().getCanonicalPath()
    if p1.startswith(p2):
      return p1[len(p2)+1:]
    return p1

  def btnCancel_click(self,*args):
    self.hide()

  def visit(self, unit):
    try:
      if not isinstance(unit,ScriptingScript ):
        return
      mode = self.getMode()
      search = self.getSearchText()
      self.composer.getStatusbar().message("Searching %s..." % unit.getName())
      fname = unit.getResource(unit.getId()+".py").getAbsolutePath()
      inputFile=StringIO(unit.getCode())
      analyzer = CodeAnalyzer()
      analyzer.load(fname,search=search, inputFile=inputFile)
      analyzer.removeEmptyElemens()
      module = analyzer.getModule()
      if module.has_children():
        module.name = self.getPath(File(module.fname))
        model = self.navigator.getModel()
        model.getRoot().addChild(module)
        model.fireChanged()
        
      
    except Exception, ex:
      logger("Error searching references, search=%r, mode=%r, unit=%s" % (search, mode, unit), LOGGER_WARN,ex)
      
def main(*args):
  panel = SearchReferencesPanel()
  panel.show()
  