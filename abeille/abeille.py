
import gvsig
from gvsig.libs.formpanel import getResource

import thread
import os.path
import subprocess
import shutil

from java.lang import System
from java.io import File
from java.io import FileInputStream
from java.io import FileOutputStream
from java.util import Properties

from org.apache.commons.io import FileUtils
from org.gvsig.andami import PluginsLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools import ToolsLocator

import javax.swing.ImageIcon
import javax.imageio.ImageIO
from javax.swing import AbstractAction, Action

def updateUserDataProperties():
  fis = None
  fos = None
  try:
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    try:
      editor = composer.getDock().getSelected(JScriptingComposer.Dock.DOCK_CENTER).getComponent()
    except:
      editor = None    
    if editor == None:
      return
    folder = editor.getUnit().getFile().getParent()
    home = os.path.expanduser("~")
    abeillehome = os.path.join(home,".abeilleforms13")
    if not os.path.isdir(abeillehome):
      os.mkdir(abeillehome)
    if not os.path.isfile(os.path.join(abeillehome,"userdata.properties")):
      shutil.copyfile(getResource(__file__,"data","userdata.properties"), abeillehome)
    lastProject = getResource(__file__,"data","abeille.jfpr")
    prop = Properties()
    fis = FileInputStream(os.path.join(abeillehome,"userdata.properties"))
    prop .load(fis)
    fis.close()
    fis = None
    prop.setProperty("jeta.filechooser.lastdirectory",folder)
    prop.setProperty("jeta.filechooser.lastdirectory.java",folder)
    prop.setProperty("jeta.filechooser.lastdirectory.form",folder)
    prop.setProperty("jeta.filechooser.lastdirectory.img",folder)
    prop.setProperty("jeta.filechooser.lastdirectoryproject",folder)
    prop.setProperty("last.project",lastProject)
    fos = FileOutputStream(os.path.join(abeillehome,"userdata.properties"))
    prop.store(fos,"")
  except:
    pass
  finally:
    if fis!=None:
      fis.close()
    if fos!=None:
      fos.close()
      
def launchAbeille():
  updateUserDataProperties()
  java = os.path.join( System.getProperties().getProperty("java.home"), "bin", "java")
  pluginsManager = PluginsLocator.getManager()
  plugin = pluginsManager.getPlugin(ScriptingExtension)
  designer = FileUtils.getFile(plugin.getPluginDirectory(),"abeille-2.1.0_M3","designer.jar")
  cmd = [java,"-jar",designer.getAbsolutePath()]
  print cmd
  subprocess.call(cmd)


class AbeilleFormDesignerAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Abeille forms designer")
    self.putValue(Action.ACTION_COMMAND_KEY, "AbeilleFormsDesigner");
    self.putValue(Action.SMALL_ICON, self.load_icon(getResource(__file__,"abeille.png")));
    self.putValue(Action.SHORT_DESCRIPTION, "Abeille forms designer");

  def load_icon(self, afile):
    if not isinstance(afile,File):
      afile = File(str(afile))
    return javax.swing.ImageIcon(javax.imageio.ImageIO.read(afile))

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    thread.start_new_thread(launchAbeille,tuple())

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = AbeilleFormDesignerAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action)

def main(*args):
  #updateUserDataProperties()
  thread.start_new_thread(launchAbeille,tuple())
