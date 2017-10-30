# encoding: utf-8

from gvsig import *
from gvsig.uselib import use_jar

import os.path

def use_jars(base,folder):
  if os.path.isfile(base):
    base = os.path.dirname(base)
  folder = os.path.join(base,folder)
  for f in os.listdir(folder):
    if f.endswith(".jar"):
      pathname = os.path.join(folder,f)
      use_jar(pathname)

use_jars(__file__,"jars")

from java.io import File

from javax.swing import SwingUtilities


# http://svnkit.com/javadoc/index.html
# http://wiki.svnkit.com/
# http://wiki.svnkit.com/Managing_A_Working_Copy
# http://svnkit.com/download.php
from org.tmatesoft.svn.core.wc import SVNClientManager
from org.tmatesoft.svn.core.wc import SVNRevision
from org.tmatesoft.svn.core import SVNDepth
from org.tmatesoft.svn.core.wc import ISVNEventHandler
from org.tmatesoft.svn.core import SVNURL

from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer

class SVN(ISVNEventHandler):
  def __init__(self):
    self.composer = ScriptingSwingLocator.getUIManager().getActiveComposer()

  def createURL(self,url):
    """Create a SVNURL from the string cointainen the url"""
    svnurl = SVNURL.parseURIEncoded(url)
    return svnurl

  def createFile(self, pathname):
    if isinstance(pathname,File):
      return pathname
    return File(pathname)

  def handleEvent(self, event, progress):
    def output():
      self.console().append("%s %s\n" % (event, progress))
    
    if SwingUtilities.isEventDispatchThread():
       output()
    else:
       SwingUtilities.invokeLater(output)
    
  def checkCancelled(self):
    pass

  def console(self):
    console = self.composer.getDock().get("#SVN")
    if console == None:
      console = ScriptingSwingLocator.getUIManager().createJScriptingConsole(False)
      self.composer.getDock().add("#SVN","SVN",console,JScriptingComposer.Dock.DOCK_BOTTOM)
    self.composer.getDock().select("#SVN")
    return console.getComponent()
        
  def checkout(self, url, folder):
    """Descarga el contenido de la URL en la carpeta indicada"""
    self.console().append("svn checkout %s %s\n" % (url, folder))
    clientManager = SVNClientManager.newInstance()
    updateClient = clientManager.getUpdateClient()
    updateClient.setEventHandler(self)
    updateClient.doCheckout(
      self.createURL(url),
      self.createFile(folder),
      SVNRevision.HEAD,
      SVNRevision.HEAD,
      SVNDepth.INFINITY,
      False
    )
    self.console().append("Checkout terminated\n")

"""
Menu "Team":

- Stat...
- Show changes...
- Diff
- ---
- Commit...
- Upate to head...
- ---
- Checkout
- Import to repository

"""
def main(*args):
  svn = SVN()
  svn.checkout("http://devel.gvsig.org/svn/gvsig-projects-pool/org.gvsig.busquedacatastral/trunk/org.gvsig.busquedacatastral","/tmp/org.gvsig.busquedacatastral")
  
  