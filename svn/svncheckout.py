# encoding: utf-8

from gvsig import *
import gvsig.libs.formpanel
reload(gvsig.libs.formpanel)
from gvsig.libs.formpanel import FormPanel, load_icon

from gvsig import commonsdialog

import os.path
from javax.swing import AbstractAction,Action
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting import ScriptingLocator
from org.gvsig.tools import ToolsLocator

import svntools
reload(svntools)
from svntools import SVN

class SVNCheckout(FormPanel):
  def __init__(self):
    FormPanel.__init__(self, (__file__,"svncheckout.xml"))
    self.composer = ScriptingSwingLocator.getUIManager().getActiveComposer()


  def show(self):
    manager = ScriptingSwingLocator.getUIManager()
    manager.showWindow(self.asJComponent(),"SVN Checkout")

  def btnLocalFolder_click(self, *args):
    folder = ScriptingLocator.getManager().getUserFolder()
    f = commonsdialog.openFolderDialog("Local folder",folder.getFile(), root=self.composer)
    if f==None or len(f)<1:
      return
    f=f[0]
    self.txtLocalFolder.setText(f.getAbsolutePath())
    
    
  def btnCancel_click(self,*args):
    self.hide()

  def btnCheckout_click(self,*args):
      self.hide()
      svn = SVN()
      svn.checkout(self.txtURL.getText(), self.txtLocalFolder.getText())
      

class SVNCheckoutAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Checkout...")
    self.putValue(Action.ACTION_COMMAND_KEY, "SVNCheckout")
    self.putValue(Action.SMALL_ICON, load_icon(os.path.join(os.path.dirname(__file__),"svncheckout.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Checkout from SVN repository to local folder")
    #self.putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_R, InputEvent.CTRL_DOWN_MASK ))

  def actionPerformed(self,e):
    panel = SVNCheckout()
    panel.show()
  
  def isEnabled(self):
    return True

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action1 = SVNCheckoutAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools") + "/" + i18nManager.getTranslation("Team"), action1)
 

def main(*args):
  panel = SVNCheckout()
  panel.show()
  