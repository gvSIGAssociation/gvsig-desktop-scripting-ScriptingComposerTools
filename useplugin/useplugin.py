# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.tools.swing.api import Component

from javax.swing import DefaultListModel
from org.gvsig.andami import PluginsLocator

from gvsig.uselib import use_plugin

class UsePluginPanel(FormPanel, Component):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"useplugin.xml"))
    self.setPreferredSize(400,400)
    model = DefaultListModel()
    model.removeAllElements()
    plugins = PluginsLocator.getManager().getPlugins()
    orderedPlugins = list()
    for plugin in plugins:
      if plugin!=None:
        orderedPlugins.append(plugin.getPluginName())
    orderedPlugins.sort()
    self.lstPlugins.removeAll()
    for plugin in orderedPlugins:
        model.addElement(plugin)
    self.lstPlugins.setModel(model)

  def lstPlugins_change(self, *args):
    pluginName = self.lstPlugins.getSelectedValue()
    if pluginName == None:
      return
    code = "use_plugin('%s')" % pluginName
    self.txtCode.setText(code)
    self.txtCode.setSelectionStart(0)
    self.txtCode.setSelectionEnd(len(code))

  def showWindow(self, title="Use plugin"):
    winmgr = ScriptingSwingLocator.getUIManager().getWindowManager()
    dialog = winmgr.createDialog(
      self.asJComponent(),
      title,
      "Add a plugin dependency to the script framework", 
      winmgr.BUTTON_CANCEL + winmgr.BUTTON_OK
    )
    dialog.setButtonLabel(winmgr.BUTTON_OK, "Use selected plugin")
    dialog.setWindowManager(winmgr)
    dialog.show(winmgr.MODE.DIALOG)
    if dialog.getAction()==winmgr.BUTTON_OK:
      pluginName = self.lstPlugins.getSelectedValue()
      if pluginName != None:
        print "use_plugin('%s')" % pluginName
        use_plugin(pluginName)
  
def main(*args):
  panel = UsePluginPanel()
  panel.showWindow()
  
  