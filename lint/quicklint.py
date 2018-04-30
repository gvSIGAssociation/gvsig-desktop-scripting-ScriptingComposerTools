# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import load_icon
from gvsig.uselib import use_libs

import time
import sys
from os.path import basename, dirname, join
import thread

from  org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from javax.swing import AbstractAction, Action
from java.awt import Color

from java.lang import Runnable
from javax.swing import SwingUtilities

lint_options_quick = [
    "--reports=n",
    "--errors-only",
    "--ignore-imports=y",
    "--disable=all",
    "--enable=undefined-variable",
    "--enable=used-before-assignment",
    "--enable=cell-var-from-loop",
    "--enable=global-variable-undefined",
    "--enable=undefined-loop-variable",
    "--enable=not-in-loop",
    "--enable=function-redefined",
    "--enable=return-outside-function",
    "--enable=return-arg-in-generator",
    "--enable=unreachable",
    "--enable=bad-super-call", 
    "--enable=not-an-iterable",
    "--enable=not-a-mapping",
    "--enable=mixed-indentation",
    "--enable=mixed-line-endings",
    "--enable=no-value-for-parameter",
    "--enable=access-member-before-definition",
    "--enable=no-self-argument",
    "--enable=unbalanced-tuple-unpacking",
    "--disable=typecheck,classes",
    
    ]

def prueba():
  a = bxx * 2
  c = bxz +1

class FilePath(str):
  def __init__(self, path):
    str.__init__(self,path)
    self.stream = None
    self.source_code = None
    
  def copy(self,s):
    new = FilePath(s)
    new.stream = self.stream
    new.source_code = self.source_code
    return new

icon_error = load_icon((__file__,"trackicon_error.png"))
icon_warn = load_icon((__file__,"trackicon_warn.png"))

class AddLineTrackingIcon(Runnable):
  def __init__(self, textPanel, iconsGroup, line, icon, msg, color):
    self.textPanel = textPanel
    self.iconsGroup = iconsGroup
    self.line = line
    self.icon = icon
    self.msg = msg
    self.color = color

  def run(self):
    self.textPanel.addLineTrackingIcon(
      self.iconsGroup, 
      self.line, 
      self.icon, 
      self.msg, 
      self.color
    )

  def call(self):
    if SwingUtilities.isEventDispatchThread():
      self.run()
    else:
      SwingUtilities.invokeLater(self)



def checkFile(pathName, code, background=False):

  def check(pathName, code, textPanel):
    from pylint import lint
    reload(lint)
    from pylint.reporters import BaseReporter
    import astroid.builder
  
    code = code.strip()
    if code.startswith("# encoding:"):
      code = code.replace("# encoding:","# e n c o d i n g:",1)
        
    class MyReporter(BaseReporter):
      def __init__(self):
        BaseReporter.__init__(self)
  
      def handle_message(self, msg):
        #print(msg.category, msg.msg, msg.line)
        if msg.category == "error":
          icon = icon_error
          color = Color.RED
        else:
          icon = icon_warn
          color = Color.YELLOW.darker()
        AddLineTrackingIcon(textPanel, "#quicklint",msg.line-1, icon, msg.msg, color).call()
  
    filename = FilePath(pathName)
    filename.source_code = code
    
    astroid.builder.MANAGER.astroid_cache.clear()
    args = list()
    args.extend(lint_options_quick)
    args.append(filename)
  
    reporter = MyReporter()
    #t1= time.time()
    x = lint.Run(args, reporter=reporter, exit=False)
    #print "quick-lint: ",int((time.time()-t1)*1000)
    composer.getStatusbar().clear()

  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return
  composer.getStatusbar().message("Running quick lint to %s..." % basename(pathName))
  try:
    #use_libs(join(dirname(__file__),"libs"),isglobal=True)
    editor = composer.getCurrentEditor()
    textPanel = editor.getSyntaxtHighlightTextComponent()
    textPanel.removeTrackingIcons("#quicklint")

    if background:
      thread.start_new_thread(check,(pathName, code, textPanel))
    else:
      check(pathName, code, textPanel)

  except Exception, ex:
    gvsig.logger(str(ex))
    
def main(*args):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  editor = composer.getCurrentEditor()
  
  script = editor.getScript()
  fname = script.getResource(script.getId()+".py").getAbsolutePath()
  checkFile(fname,editor.getJTextComponent().getText())


def prueba():
  aaa = bxx * 2
  c = aaa +1



  