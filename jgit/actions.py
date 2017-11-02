# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

from javax.swing import Action
from org.gvsig.tools import ToolsLocator
from java.awt.event import KeyEvent
from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from javax.swing import KeyStroke
from java.awt.event import InputEvent
from javax.swing import AbstractAction

import repo_show_changes
reload(repo_show_changes)

import repo_clone
reload(repo_clone)

import repo_init
reload(repo_init)

import repo_push
reload(repo_push)

import repo_pull
reload(repo_pull)

import repo_ignore
reload(repo_ignore)

import repo_info
reload(repo_info)

import repo_show_log
reload(repo_show_log)

import repo_diff
reload(repo_diff)

class ShowChangesAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Show changes")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitShowChanges")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","show-changes.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Show changes in sources")

  def actionPerformed(self,e):
    repo_show_changes.repo_show_changes()
  
  def isEnabled(self):
    return True

class GitCloneAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Clone...")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitClone")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","git-clone.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Clone a remote repository in local")

  def actionPerformed(self,e):
    repo_clone.repo_clone()
  
  def isEnabled(self):
    return True

class GitInitAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Initialize repository...")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitInit")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","git-init.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Create a local repository for the current folder.")

  def actionPerformed(self,e):
    repo_init.repo_init()
  
  def isEnabled(self):
    return True

class GitPushAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Push...")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitPush")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","push.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Updates remote repository from local repository")

  def actionPerformed(self,e):
    repo_push.repo_push()
  
  def isEnabled(self):
    return True

class GitPullAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Pull...")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitPull")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","pull.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Incorporates changes from a remote repository into the local repository.")

  def actionPerformed(self,e):
    repo_pull.repo_pull()
  
  def isEnabled(self):
    return True

class GitIgnoreAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Edit ignore files")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitIgnore")
    #self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","gitignore.png")))
    #self.putValue(Action.SHORT_DESCRIPTION, "Edit ignore files.")

  def actionPerformed(self,e):
    repo_ignore.repo_ignore()
  
  def isEnabled(self):
    return True

class GitInfoAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Show repository information")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitInfo")
    #self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","gitinfo.png")))
    #self.putValue(Action.SHORT_DESCRIPTION, "Show repository information.")

  def actionPerformed(self,e):
    repo_info.repo_info()
  
  def isEnabled(self):
    return True

class GitLogAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Show log")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitLog")
    #self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","gitlog.png")))
    #self.putValue(Action.SHORT_DESCRIPTION, "Show log.")

  def actionPerformed(self,e):
    repo_show_log.repo_show_log()
  
  def isEnabled(self):
    return True
    
class GitDiffAction(AbstractAction):

  def __init__(self):
    AbstractAction.__init__(self,"Diff")
    self.putValue(Action.ACTION_COMMAND_KEY, "GitDiff")
    self.putValue(Action.SMALL_ICON, load_icon(getResource(__file__,"images","diff.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Show diff with head.")

  def actionPerformed(self,e):
    repo_diff.repo_diff()
  
  def isEnabled(self):
    return True
    
def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  
  gitClone = GitCloneAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitClone)

  gitInit = GitInitAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitInit)

  gitPush = GitPushAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitPush)

  gitPull = GitPullAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitPull)

  gitIgnore = GitIgnoreAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitIgnore)

  gitInfo = GitInfoAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitInfo)

  gitLog = GitLogAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitLog)

  gitDiff = GitDiffAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",gitDiff)

  showChanges = ShowChangesAction()
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Git",showChanges)
  manager.addComposerTool(showChanges)
  
def main(*args):
  selfRegister()
  