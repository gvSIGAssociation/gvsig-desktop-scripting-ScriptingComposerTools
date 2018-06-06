# encoding: utf-8

from gvsig import *

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting.swing.api import JScriptingComposer
from org.gvsig.scripting.swing.api import CreateComponentListener

from javax.swing import Timer
from javax.swing.event import ChangeListener
from java.awt.event import ActionListener

from time import time, sleep
from threading import Thread

from quicklint import checkFile

class ContinuosLint(Thread):
  def __init__(self, composer):
    Thread.__init__(self,name="ContinuosLint")
    self.composer = composer
    self.processing = False

  def run(self):
    from gvsig.libs.formpanel import ActionListenerAdapter, ChangeListenerAdapter

    self.timer = Timer(3000, ActionListenerAdapter(self.timerActivated))
    self.timer.setRepeats(False)
    editorChangedListener = ChangeListenerAdapter(self.editorChanged)
    dockSelectedListener = ActionListenerAdapter(self.dockSelected)
    self.composer.addChangeEditorListener(editorChangedListener)
    self.composer.getDock().addActivateListener(dockSelectedListener)
    try:
      while True:
        sleep(10)
    except KeyboardInterrupt as ex:
      pass 
    self.composer.removeChangeEditorListener(editorChangedListener)
    self.composer.getDock().removeActivateListener(dockSelectedListener)
    print "Exit continuos lint"

  def timerActivated(self, *args):
    #print "[%d] timerActivated: %s" % (time(),args)
    self.timer.stop()
    self.update()
    
  def editorChanged(self,*args):
    #print "[%d] editorChanged: %s" % (time(),args)
    self.timer.restart()
        
  def dockSelected(self,*args): 
    #print "[%d] dockSelected: %s" % (time(),args)
    self.timer.restart()

  def update(self):
    #print "Lint start."
    if self.processing:
      return
    try:
      self.processing = True
      self.composer.getStatusbar().message("Checking syntax...")
      editor = self.composer.getCurrentEditor()
      script = self.composer.getCurrentScript()
      if editor != None and script != None:
        fname = script.getResource(script.getId()+".py").getAbsolutePath()
        checkFile(fname,editor.getJTextComponent().getText())
    finally:
      self.composer.getStatusbar().clear()
      self.processing = False
    
class ContinuosLintInstaller(CreateComponentListener):
  def __init__(self):
    pass

  def componentCreated(self, component):
    if isinstance(component, JScriptingComposer):
      x = ContinuosLint(component)
      x.start() 

def selfRegister():
  manager = ScriptingSwingLocator.getUIManager()
  manager.addCreatedComponentListener(ContinuosLintInstaller())
  

def main(*args):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  x = ContinuosLint(composer)
  x.start() 
