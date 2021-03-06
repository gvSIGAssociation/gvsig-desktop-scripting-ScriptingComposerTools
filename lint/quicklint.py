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

def checkFile(pathName, code):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return
  composer.getStatusbar().message("Running quick lint to %s..." % basename(pathName))
  try:
    from pylint import lint
    reload(lint)
    from pylint.reporters import BaseReporter
    import astroid.builder
    
    code = code.strip()
    if code.startswith("# encoding:"):
      code = code.replace("# encoding:","# e n c o d i n g:",1)
    editor = composer.getCurrentEditor()
    textPanel = editor.getSyntaxtHighlightTextComponent()
        
    class MyReporter(BaseReporter):
      def __init__(self, composer):
        BaseReporter.__init__(self)
  
      def handle_message(self, msg):
        #print(msg.category, msg.msg, msg.line)
        if msg.category == "error":
          icon = icon_error
          color = Color.RED
        else:
          icon = icon_warn
          color = Color.YELLOW.darker()
        textPanel.addLineTrackingIcon("#quicklint",msg.line-1, icon, msg.msg, color)

    filename = FilePath(pathName)
    filename.source_code = code
    
    astroid.builder.MANAGER.astroid_cache.clear()
    args = list()
    args.extend(lint_options_quick)
    args.append(filename)
  
    reporter = MyReporter(composer)
    textPanel.removeTrackingIcons("#quicklint")
    #t1= time.time()
    x = lint.Run(args, reporter=reporter, exit=False)
    #print "quick-lint: ",int((time.time()-t1)*1000)
    composer.getStatusbar().clear()

  except:
    ex = sys.exc_info()[1]
    gvsig.logger(str(ex), ex=ex)
    
def main(*args):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  editor = composer.getCurrentEditor()
  
  script = editor.getScript()
  fname = script.getResource(script.getId()+".py").getAbsolutePath()
  checkFile(fname,editor.getJTextComponent().getText())


def prueba():
  aaa = bxx * 2
  c = aaa +1



  