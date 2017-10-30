
from gvsig import *

from jarray import array
from os.path import dirname, join

import javax.swing.ImageIcon
import javax.swing.Timer

from java.io import File
from java.lang import Thread
from javax.swing import DefaultListModel
from javax.swing import AbstractAction, Action
from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools.swing.api import Component 
from org.gvsig.tools import ToolsLocator

#import gvsig.libs.formpanel
#reload(gvsig.libs.formpanel)
from gvsig.libs.formpanel import FormPanel

class ListThreadsItem:

  def __init__(self, thread):
    self.thread = thread

  def __repr__(self):
    return "%s - %s" % (self.thread.getName(),self.thread.getId())

  def getThread(self):
    return self.thread

class ThreadList(FormPanel, Component):
  def __init__(self):
    #self.timerAutorefresh = javax.swing.Timer(5000,None)
    self.load(File(join(dirname(__file__),"threadlist.xml")))
    self.setPreferredSize(400,400)
    self.refresh()
    #self.timerAutorefresh.start()

  def refresh(self):
    currentGroup = Thread.currentThread().getThreadGroup()
    n = currentGroup.activeCount()
    threadList = array( [None]*n, Thread)

    currentGroup.enumerate(threadList)
    self.lstThreads.removeAll()
    items = list()
    for t in threadList:
      items.append(ListThreadsItem(t))
    items.sort()

    model = DefaultListModel()
    for item in items:
      model.addElement(item)
    self.lstThreads.setModel(model)

  #def timerAutorefresh_perform(self,*args):
  #  self.refresh()

  def btnRefresh_click(self,*args):
    self.refresh()

  #def btnClose_click(self, *args):
  #  self.hide()

  def btnKill_click(self, *args):
    item = self.lstThreads.getSelectedValue()
    if item == None:
      return
    print "interrupt %s %s" % (item.getThread().getId(),item.getThread().getName())
    item.getThread().interrupt()


def load_icon(afile):
  if not isinstance(afile,File):
    afile = File(str(afile))
  return javax.swing.ImageIcon(javax.imageio.ImageIO.read(afile))

class ThreadListAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Thread list")
    self.putValue(Action.ACTION_COMMAND_KEY, "ThreadList");
    self.putValue(Action.SMALL_ICON, load_icon(join(dirname(__file__),"threadlist.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "List running threads");

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    p = ThreadList()
    composer.getDock().add("#Threadlist","Threadlist",p,JScriptingComposer.Dock.DOCK_LEFT)
    composer.getDock().select("#Threadlist")

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = ThreadListAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action)
  
def test(*args):
  p = ThreadList()
  manager = ScriptingSwingLocator.getUIManager()
  manager.showWindow(p.asJComponent(),"Thread list")

def main(*args):
  pass