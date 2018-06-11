# encoding: utf-8

from gvsig import *
from gvsig.libs.formpanel import load_icon
from gvsig.uselib import use_libs

import time
import sys
from os.path import basename, dirname, join
import thread



from  org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from javax.swing import AbstractAction, Action

from org.gvsig.tools import ToolsLocator

# lists all messages supported by PyLint 1.1.0,
# http://pylint-messages.wikidot.com/all-codes
# https://github.com/PyCQA/pylint/blob/master/pylint/checkers/imports.py

lint_options = [
    "--reports=n",
    "--disable=bad-continuation",
    "--disable=singleton-comparison",
    "--disable=unused-argument",
    "--disable=line-too-long",
    "--disable=no-self-use",
    "--disable=redefined-builtin",
    "--disable=redefined-outer-name",
    "--disable=too-many-locals",
    "--disable=trailing-whitespace",
    "--disable=bad-indentation",
    "--disable=bad-whitespace",
    "--disable=unused-import",
    "--disable=import-error",
    "--disable=missing-docstring",
    "--disable=invalid-name",
    "--disable=unused-wildcard-import",
    "--disable=wildcard-import",
    "--disable=wrong-import-order",
    "--disable=relative-import",
    "--disable=too-few-public-methods",
    "--disable=too-many-arguments",
    "--disable=too-many-instance-attributes",
    "--disable=I0011", #I0011: Locally disabling %s
    "--disable=W0702", #W0702: No exception type(s) specified
    "--disable=C0412" #C0412: Imports from package %s are not grouped
]
def checkFile(pathName):
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return
  composer.getStatusbar().message("Running lint to %s..." % basename(pathName))
  try:
    from pylint import lint
    from pylint.reporters import BaseReporter
    import astroid.builder
    

    class MyReporter(BaseReporter):
      def __init__(self, composer):
        BaseReporter.__init__(self)
        self.problems = None
        self.composer = composer
        if self.composer != None:
          self.problems = self.composer.getProblems()
          self.problems.removeAll()
  
  
      def handle_message(self, msg):
        try:
          if self.problems != None:
            self.problems.add(msg.category.capitalize(), msg.msg, msg.module, msg.line, msg.column)
            self.composer.getDock().select(JScriptingComposer.DOCKED_PROBLEMS)
        except:
          pass    
    
    astroid.builder.MANAGER.astroid_cache.clear()
    args = list()
    args.extend(lint_options)
    args.append(pathName)
  
    reporter = MyReporter(composer)
    t1= time.time()
    x = lint.Run(args, reporter=reporter, exit=False)
    #print "lint: ",int((time.time()-t1)*1000)
    
  except:
    ex = sys.exc_info()[1]
    composer.getProblems().add("Error", "Can't execute lint", basename(pathName), 0, 0)
    composer.getDock().select(JScriptingComposer.DOCKED_PROBLEMS)
  composer.getStatusbar().clear()

class LintAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Lint")
    self.putValue(Action.ACTION_COMMAND_KEY, "Lint")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"lint.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Lint, check file syntax")
    #self.putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_O, InputEvent.CTRL_DOWN_MASK ))

  def actionPerformed(self,e=None):
    if e==None:
      composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    else:
      composer = e.getSource().getContext()
    editor = composer.getCurrentEditor()
    if editor == None:
      return
    composer.getProblems().removeAll()
    script = editor.getScript()
    fname = script.getResource(script.getId()+".py").getAbsolutePath()
    thread.start_new_thread(checkFile, (fname,))

  def isEnabled(self):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer != None:
      return composer.getDock().getSelected(JScriptingComposer.Dock.DOCK_CENTER) != None
    return False

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = LintAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools"),action)
  manager.addComposerTool(action)

def main(*args):
  action = LintAction()
  action.actionPerformed()
