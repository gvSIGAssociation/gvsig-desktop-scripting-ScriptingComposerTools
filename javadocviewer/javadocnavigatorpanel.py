# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import FormPanel, FormComponent, getResource
from gvsig.commonsdialog import msgbox, inputbox, confirmDialog
from gvsig.commonsdialog import QUESTION, YES_NO_CANCEL, NO

import os
import fnmatch
import xmltodic
from StringIO import StringIO
import thread

from java.awt.event import MouseEvent
from javax.swing.tree import TreeModel
from javax.swing.tree import DefaultTreeModel
from javax.swing.tree import DefaultMutableTreeNode 
from javax.swing.tree import DefaultTreeCellRenderer
from javax.swing import JMenuItem
from javax.swing import JPopupMenu
from javax.swing import JSeparator
from javax.swing.event import TreeSelectionListener
from javax.swing import DefaultListModel

from org.gvsig.tools.swing.api import Component 
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting.swing.api import JScriptingComposer

import javadoc
reload(javadoc)
from javadoc import Package, Module, Javadoc

from javadocsetpanel import JavadocSetPanel


import webbrowserpanel
reload(webbrowserpanel)
from webbrowserpanel import BrowserPanel

#-------------------------------------------
#
# Contents tab
#

class ContentsTreeModel(TreeModel):
  def __init__(self,root):
    self._root = root
    
  def getRoot(self):
    return self._root

  def getChild(self, parent, index):
    return parent[index]

  def getChildCount(self, parent):
    return len(parent)

  def isLeaf(self, node):
    return not node.hasChildren()

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
    pass

  def removeTreeModelListener(self, listener):
    pass

class ContentsTreeSelectionListener(TreeSelectionListener):
  def __init__(self, contentsPanel):
    self.__contentsPanel = contentsPanel
  
  def valueChanged(self,*args):
    treepath = self.__contentsPanel.getSelectionPath()
    if treepath == None:
      return
    item = treepath.getLastPathComponent()
    if isinstance(item,Module):
      url = item.getUrl()
      self.__contentsPanel.setPage(url)    

class ContentsCellRenderer(DefaultTreeCellRenderer):
  def __init__(self, icon_package, icon_module):
    self.icon_package = icon_package
    self.icon_module = icon_module
    
  def getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused):
    c = DefaultTreeCellRenderer.getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused)
    if isinstance(value,Package):
      icon = self.icon_package
    else:
      icon = self.icon_module
    if icon!=None:
      self.setIcon(icon)
    return c
    
class ContentsPanel(FormComponent):
  def __init__(self, navigator):
    self.__navigator = navigator
    FormComponent.__init__(self)
    self.treePackages = self.__navigator.treePackages
    self.treePackages.setModel(ContentsTreeModel(self.getJavadoc().getNodes()))
    self.treePackages.addTreeSelectionListener(ContentsTreeSelectionListener(self))
    self.treePackages.setCellRenderer( 
        ContentsCellRenderer(
          self.load_icon(getResource(__file__,"images","package.png")),
          self.load_icon(getResource(__file__,"images","clase.png"))
      )
    )
    self.autobind()

  def getJavadoc(self):
    return self.__navigator.getJavadoc()

  def getSelectionPath(self):
      return self.treePackages.getSelectionPath()

  def setPage(self, url):
    self.__navigator.setPage(url)

  def refresh(self):
    self.treePackages.setModel(ContentsTreeModel(self.getJavadoc().getNodes()))


#-------------------------------------------
#
# Contents tab
#

class ClassesPanel(FormComponent):
  def __init__(self, navigator):
    self.__navigator = navigator
    FormComponent.__init__(self)
    self.lstResults = self.__navigator.lstResults
    self.txtSearch = self.__navigator.txtSearch
    self.btnSearch = self.__navigator.btnSearch
    self.autobind()
    self.btnSearch.setIcon(self.load_icon((__file__,"images/find.png")))
    self.refresh()

  def getJavadoc(self):
    return self.__navigator.getJavadoc()

  def setPage(self,url):
    self.__navigator.setPage(url)
    
  def txtSearch_keyPressed(self,keyEvent):
    if keyEvent.getKeyChar() == "\n":
      self.doSearch()
    
  def refresh(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer != None:
      composer.getStatusbar().message("Javadocs: updating classes list...")
    try:  
      self.txtSearch.setText("")
      model = DefaultListModel()
      for module in self.getJavadoc().getModules():
        model.addElement(module)
      self.lstResults.setModel(model)
    finally:
      if composer != None:
        composer.getStatusbar().message("")
        
  def lstResults_change(self,*args):
    module = self.lstResults.getSelectedValue()
    if module != None:
      self.setPage(module.getUrl())

  def btnSearch_click(self,*args):
    self.doSearch()

  def doSearch(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer != None:
      composer.getStatusbar().message("Javadocs: Searching classes...")
    try:  
      model = DefaultListModel()
      pattern = self.txtSearch.getText().lower()
      if not ("*" in pattern or "?" in pattern):
        pattern = "*"+pattern+"*"
      for module in self.getJavadoc().getModules():
        if module!=None and fnmatch.fnmatch(module.getName().lower(), pattern):
          model.addElement(module)
      self.lstResults.setModel(model)
    finally:
      if composer != None:
        composer.getStatusbar().message("")

#-------------------------------------------
#
# Bookmarks tab
#


class Bookmarks(object):
  def __init__(self):
    self.root = DefaultMutableTreeNode(BookmarksItem("Bookmarks"))
    self.load()

  def getRoot(self):
    return self.root
    
  def save(self, fname=None):
    if fname == None:
      fname = os.path.join(os.path.dirname(__file__),"bookmarks.xml")
    buffer = StringIO()
    self.writeNode(buffer, self.root)
    xml = buffer.getvalue().encode("utf-8")
    f = open(fname,"w")
    f.write(xml)
    f.close()
    
  def writeNode(self, buffer, node, indent=0):
    item = node.getUserObject()
    if not item.isPersistent():
      return
    if item.isGroup():
      buffer.write('%s<group name="%s">\n' % ("  "*indent,item.getLabel()))
      for n in range(node.getChildCount()):
        child = node.getChildAt(n)
        self.writeNode(buffer,child,indent+1)
      buffer.write('%s</group>\n' % ("  "*indent))
    else:
      if item.getIconName() == None:
        buffer.write('%s<bookmark name="%s">%s</bookmark>\n' % ("  "*indent,item.getLabel(),item.getValue()))
      else:
        buffer.write('%s<bookmark name="%s" icon="%s">%s</bookmark>\n' % ("  "*indent,item.getLabel(),item.getIconName(),item.getValue()))

  def load(self, fname=None):
    if fname == None:
      fname = os.path.join(os.path.dirname(__file__),"bookmarks.xml")
    if os.path.exists(fname):
      fin = open(fname,"r")
      d = xmltodic.parse(fin)
      root = d["group"]
      self.root = self.loadGroup(root)

  def loadGroup(self, node, parentTreeNode=None):
    treeNode = DefaultMutableTreeNode(BookmarksItem(node["@name"]))
    if parentTreeNode!=None:
      parentTreeNode.add(treeNode)
    groups=node.get("group",None)
    if groups!=None:
      if isinstance(groups,list): 
        for child in groups:
          self.loadGroup(child, treeNode)
      else:
        self.loadGroup(groups,treeNode)

    bookmarks=node.get("bookmark",None)
    if bookmarks!=None:
      if isinstance(bookmarks,list):
        for child in bookmarks:
          self.loadBookmark(child, treeNode)
      else:
        self.loadBookmark(bookmarks, treeNode)
    return treeNode
            
  def loadBookmark(self, node, parentTreeNode):
    treeNode = DefaultMutableTreeNode(BookmarksItem(node["@name"],node["#text"], node.get("@icon",None)))
    if parentTreeNode!=None:
      parentTreeNode.add(treeNode)
      

class BookmarksItem(object):
  def __init__(self,name, value=None, icon=None, persistent=True):
    self._name = name
    self._value = value
    self._iconName = icon
    self._persistent = persistent
    if self._iconName != None:
        iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
        self._icon = iconTheme.get(self._iconName)
    else:
      self._icon = None

  def __repr__(self):
    return self._name

  def getLabel(self):
    return self._name

  def getIcon(self):
    return self._icon
    
  def getIconName(self):
    return self._iconName
    
  def getValue(self):
    return self._value

  def setLabel(self,label):
    self._name = label
    
  def isGroup(self):
    return self._value == None

  def isPersistent(self):
    return self._persistent

class BookmarksCellRenderer(DefaultTreeCellRenderer):
  def __init__(self, icon_folder, icon_layer):
    self._icon_folder = icon_folder
    self._icon_layer = icon_layer
    
  def getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused):
    c = DefaultTreeCellRenderer.getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused)
    icon = value.getUserObject().getIcon()
    if icon == None:
      if value.getUserObject().isGroup():
        icon = self._icon_folder
      else:
        icon = self._icon_layer
    self.setIcon(icon)
    return c

class BookmarksPanel(FormComponent):
  def __init__(self, navigator):
    self.__navigator = navigator
    FormComponent.__init__(self)
    self.bookmarks = None
    self.treeBookmarks = self.__navigator.treeBookmarks
    self.mnuCreateNewGroup = JMenuItem("Create group")
    self.mnuAddCurrentDocument = JMenuItem("Add current document")
    self.mnuAddExternalDocument = JMenuItem("Add external document")
    self.mnuViewDocument = JMenuItem("View document")
    self.mnuRename = JMenuItem("Rename")
    self.mnuRemove = JMenuItem("Remove")
    self.mnuProperties = JMenuItem("Properties")
    self.initComponents()
    self.autobind()

  def initComponents(self):
    self.bookmarks = Bookmarks()
    self.treeBookmarks.setCellRenderer( 
      BookmarksCellRenderer(
        self.load_icon(os.path.join(os.path.dirname(__file__),"images","folder.png")),
        self.load_icon(os.path.join(os.path.dirname(__file__),"images","bookmark.png")),
      )
    )
    self.treeBookmarks.setModel(DefaultTreeModel(self.bookmarks.getRoot()))
    
  def getJavadoc(self):
    return self.__navigator.getJavadoc()

  def setPage(self,url):
    self.__navigator.setPage(url)

  def getPage(self):
    return self.__navigator.getPage()
    
  def getPageTitle(self):
    return self.__navigator.getPageTitle()
    
  def getCurrentNode(self):
    path = self.treeBookmarks.getSelectionPath()
    if path == None:
      self.treeBookmarks.setSelectionRow(0)
      path = self.treeBookmarks.getSelectionPath()
    if path == None:
      return None
    element = path.getLastPathComponent()
    return element

  def addItem(self, node, item):
    newnode = DefaultMutableTreeNode(item)
    node.add(newnode)
    self.refresh(node)
    self.bookmarks.save()

  def refresh(self, node=None):
    if node == None:
      node = self.bookmarks.getRoot()
    model = self.treeBookmarks.getModel()
    model.reload(node)
    self.treeBookmarks.expandPath(self.treeBookmarks.getSelectionPath())
    
  def treeBookmarks_mouseClick(self,e):
    if e.isPopupTrigger():
      node = self.getCurrentNode()
      if node == None:
        return
      menu = JPopupMenu()
      if node.getUserObject().isGroup():
        menu.add(self.mnuCreateNewGroup)
        menu.add(self.mnuAddCurrentDocument)
        menu.add(self.mnuAddExternalDocument)
        menu.add(JSeparator())
        menu.add(self.mnuRename)
        menu.add(JSeparator())
        menu.add(self.mnuRemove)
      else:
        menu.add(self.mnuRename)
        menu.add(JSeparator())
        menu.add(self.mnuRemove)
        menu.add(JSeparator())
        menu.add(self.mnuProperties)
      menu.show(e.getComponent(), e.getX(), e.getY())
    elif e.getClickCount() == 2 and e.getID() == MouseEvent.MOUSE_CLICKED and e.getButton() == MouseEvent.BUTTON1:
      self.mnuViewDocument_click(None)
      
  def mnuCreateNewGroup_click(self,*args):
    node = self.getCurrentNode()
    if node == None:
      return
    folderName = inputbox("Group name","Bookmarks")
    if folderName in (None,""):
      return
    self.addItem(node, BookmarksItem(folderName))
 
  def mnuAddCurrentDocument_click(self,*args):
    url = self.getPage()
    name = self.getPageTitle() #os.path.basename(os.path.splitext(url.toString())[0])
    node = self.getCurrentNode()
    self.addDocument(name, url, node)

  def mnuAddExternalDocument_click(self,*args):
    url = inputbox("URL:", "Bookmarks - add external document", QUESTION)
    if url in ("",None):
      return
    name = os.path.basename(url)
    name = inputbox("Name:", "Bookmarks - add external document", QUESTION, name)
    if name in ("",None):
      return
    node = self.getCurrentNode()
    self.addDocument(name, url, node)

  def addDocument(self, name, url, node=None, persistent=True):
    if node == None:
      node = self.bookmarks.getRoot()
    self.addItem(node, BookmarksItem(name,url,persistent=persistent))
    
  def mnuViewDocument_click(self,*args):
    node = self.getCurrentNode()
    if node == None:
      return
    url = node.getUserObject().getValue()
    if url != None:
      self.setPage(url)

  def mnuRename_click(self,*args):
    node = self.getCurrentNode()
    if node == None:
      return
    item = node.getUserObject()
    s = inputbox("New name:", "Bookmarks - rename", QUESTION, item.getLabel())
    if s in ("",None):
      return
    item.setLabel(s)
    self.refresh(node)
    self.bookmarks.save()

  def mnuRemove_click(self,*args):
    node = self.getCurrentNode()
    if node == None:
      return
    item = node.getUserObject()
    if confirmDialog("Remove '%s' from the bookmarks ?" % item.getLabel(), "Bookmarks - remove", YES_NO_CANCEL, QUESTION) == NO:
      return
    parent = node.   getParent()
    node.removeFromParent()
    self.refresh(parent)
    self.bookmarks.save()

    
#-------------------------------------------
#
# Config tab
#

class ConfigPanel(FormComponent):
  def __init__(self, navigator):
    self.__navigator = navigator
    FormComponent.__init__(self)
    self.lstJavadocSets = self.__navigator.lstJavadocSets
    self.btnAddDocset = self.__navigator.btnAddDocset
    self.btnEditDocSet = self.__navigator.btnEditDocSet
    self.btnRemoveDocSet = self.__navigator.btnRemoveDocSet
    self.cboShowInArea = self.__navigator.cboShowInArea
    self.autobind()
    self.refresh()
    
  def getJavadoc(self):
    return self.__navigator.getJavadoc()
    
  def refresh(self):
    model = self.lstJavadocSets.getModel()
    model.clear()
    for docset in self.getJavadoc().getConfig().getJavadocSets():
      model.addElement(docset)

  def getShowLocation(self):
   n = self.cboShowInArea.getSelectedIndex()
   if n == 0:
     return JScriptingComposer.Dock.DOCK_CENTER
   return JScriptingComposer.Dock.DOCK_BOTTOM
   
  def btnAddDocset_click(self,*args):
    winmgr = ScriptingSwingLocator.getUIManager().getWindowManager()
    javadocSetPanel = JavadocSetPanel()    
    dialog = winmgr.createDialog(
      javadocSetPanel.asJComponent(),
      "Javadoc set",
      None, 
      winmgr.BUTTON_CANCEL + winmgr.BUTTON_OK
    )
    dialog.setWindowManager(winmgr)
    dialog.show(winmgr.MODE.DIALOG)
    if dialog.getAction()==winmgr.BUTTON_OK:
      name = javadocSetPanel.getName()
      url = javadocSetPanel.getURL()
      if url == "" or name == "":
        msgbox("URL and name can't be a empty string")
        return
      if not self.getJavadoc().load(url,name):
        msgbox("No se que ha pasado")
        return
      self.__navigator.refresh()
    
    
#-------------------------------------------
#
# Javadoc navigator panel
#

class JavadocNavigatorPanel(FormPanel, Component):
  def __init__(self,javadoc):
    FormPanel.__init__(self,(__file__,"javadocnavigatorpanel.xml"))
    self.__javadoc = javadoc
    self.__browser = None 
    self.initComponents()

  def initComponents(self):
    self.__contents = ContentsPanel(self)
    self.__classes = ClassesPanel(self)
    self.__bookmarks = BookmarksPanel(self)
    self.__config = ConfigPanel(self)

  def getBookmarksPanel(self):
    return self.__bookmarks
    
  def setPage(self,url):  
    if self.__browser == None:
      self.__browser = BrowserPanel()
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer.getDock().get("#JavadocBrowser")==None:
      location = self.__config.getShowLocation()
      composer.getDock().add("#JavadocBrowser","Javadoc browser",self.__browser,location)
      composer.getDock().select("#JavadocBrowser")    
    self.__browser.setPage(url)

  def getPage(self):
    if self.__browser == None:
      return None
    return self.__browser.getPage()

  def getPageTitle(self):
    if self.__browser == None:
      return None
    return self.__browser.getTitle()
      
  def getJavadoc(self):
    return self.__javadoc

  def refresh(self):
    self.__contents.refresh()
    self.__classes.refresh()
    self.__bookmarks.refresh()
    self.__config.refresh()

  def __loadJavadocSet(self, name, url):
    self.getJavadoc().load(url,name)
    self.refresh()
    
  def loadJavadocSet(self,name, url):
    thread.start_new_thread(self.__loadJavadocSet,(name,url))
    
  def showWindow(self,title="Help viewer"):
    windowManager = ScriptingSwingLocator.getUIManager()
    windowManager.showWindow(self,title)



def main(*args):
  javadoc = Javadoc()
  navigator = JavadocNavigatorPanel(javadoc)
  navigator.getBookmarksPanel().addDocument(
    "gvSIG Scripting developers guide", 
    "jar:file:" + getResource(__file__, "data","scripting-developers-guide.zip!/html/index.html"), 
    persistent=False
  )
  for docset in javadoc.getDefaultJavadocSets():
    navigator.loadJavadocSet(docset.getName(), docset.getURL())
  
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  composer.getDock().add("#JavadocNavigator","Javadoc",navigator,JScriptingComposer.Dock.DOCK_LEFT)
  composer.getDock().select("#JavadocNavigator")
  
