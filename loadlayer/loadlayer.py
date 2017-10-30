
import gvsig

from org.gvsig.andami import PluginsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting import ScriptingExternalFile
from org.gvsig.tools.swing.api import ToolsSwingLocator
from javax.swing import AbstractAction, Action
from java.awt.event import ActionListener
from org.gvsig.scripting.swing.api import CreateComponentListener
from org.gvsig.scripting.swing.api import JScriptingComposer

def getSelectedItem():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return None
  projects = composer.getDock().get(JScriptingComposer.DOCKED_PROJECTS).getComponent()
  if projects == None:
    return None
  browser = projects.getSelectedBrowser()
  if browser == None:
    return None
  item = browser.getSelectedNode()
  if item == None:
    return None
  if not isinstance(item,ScriptingExternalFile):
    return None
  return item

class MyCreateComponentListener(CreateComponentListener):
  def __init__(self, loadLayerAction):
    self.loadLayerAction = loadLayerAction
  
  def componentCreated(self, composer):
    #print "componentCreated", composer.__class__.__name__
    if isinstance(composer, JScriptingComposer):
      projects = composer.getDock().get(JScriptingComposer.DOCKED_PROJECTS).getComponent()
      #print "isEnabled", projects.__class__.__name__
      if projects != None:
        changeListener = MyChangeListener(self.loadLayerAction)
        projects.addDefaultActionListener(changeListener)
      
  
class MyChangeListener(ActionListener):
  def __init__(self,loadLayerAction):
    self.loadLayerAction = loadLayerAction
    
  def actionPerformed(self,e):
    unit = e.getUnit()
    #print "unit: ", unit.__class__.__name__
    if isinstance(unit,ScriptingExternalFile):
      self.loadLayerAction.setEnabled(True)
    else:
      self.loadLayerAction.setEnabled(False)

      
class LoadLayerAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Load layer")
    iconManager = ToolsSwingLocator.getIconThemeManager()
    self.putValue(Action.ACTION_COMMAND_KEY, "LoadLayer")
    self.putValue(Action.SMALL_ICON, iconManager.getCurrent().get("view-layer-add"))
    self.putValue(Action.SHORT_DESCRIPTION, "Load layer in current view")
    manager = ScriptingSwingLocator.getUIManager()
    self.createListener = MyCreateComponentListener(self)
    manager.addCreatedComponentListener(self.createListener)
    self.setEnabled(False)

  def actionPerformed(self,e):
    composer = e.getSource().getContext()
    item = getSelectedItem()
    if item == None:
      return
    f = item.getExternalFile()
    listfiles = (f,)
    actions = PluginsLocator.getActionInfoManager()
    addlayer = actions.getAction("view-layer-add")
    addlayer.execute((listfiles,))
    

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = LoadLayerAction()
  manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action)

def main(*args):
  selfRegister()
  