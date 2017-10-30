# encoding: utf-8

import gvsig
#
# Getting Started with JGit
# http://www.codeaffine.com/2015/12/15/getting-started-with-jgit/
#
# Add this url in javadoc config tab
# http://download.eclipse.org/jgit/site/4.9.0.201710071750-r/apidocs
#

import os

from java.io import File

from org.eclipse.jgit.storage.file import FileRepositoryBuilder
from org.eclipse.jgit.api import Git

from org.gvsig.scripting import ScriptingLocator

from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider

from org.eclipse.jgit.treewalk.filter import PathFilter

from java.io import ByteArrayOutputStream

from org.eclipse.jgit.merge import ThreeWayMergeStrategy
from org.eclipse.jgit.merge import MergeStrategy

def getBaseRepoPath():
  manager = ScriptingLocator.getManager()
  path = os.path.abspath(os.path.join(manager.getRootUserFolder().getAbsolutePath(),"..","git"))
  #print ">>> base repo path", path
  return path

pullStrategies = {
  "OURS" : MergeStrategy.OURS,
  "RECURSIVE" : ThreeWayMergeStrategy.RECURSIVE,
  "RESOLVE" : ThreeWayMergeStrategy.RESOLVE,
  "SIMPLE_TWO_WAY_IN_CORE" : ThreeWayMergeStrategy.SIMPLE_TWO_WAY_IN_CORE,
  "THEIRS" : MergeStrategy.THEIRS
}

class ComposerGitStatus(object):
  def __init__(self, modified, status, workingpath):
    self.__modified = modified
    self.__status = status
    self.__workingpath = workingpath

  def __repr__(self):
    return "status(%r,%r)" % (self.__status, str(self.__workingpath))

  def __str__(self):
    return self.__workingpath
    
  def getStatus(self):
    return self.__status

  def getWorkingPath(self):
    return str(self.__workingpath)

class Changes(dict):
  def __init__(self):
    dict.__init__(self)

  def append(self, change):
    if not change.getWorkingPath() in self:
      self[change.getWorkingPath()] = change
      return

class Commit(object):
  def __init__(self, revCommit):
    self.__revCommit = revCommit

  def getId(self):
    return self.__revCommit.getId()
    
  def getMessage(self):
    return self.__revCommit.getFullMessage()

  def getShortMessage(self):
    return self.__revCommit.getShortMessage()

  def getCommiterName(self):
    return self.__revCommit.getCommitterIdent().getName()
    
  def getCommiterMail(self):
    return self.__revCommit.getCommitterIdent().getEmailAddress()
  
  def getDate(self):
    return self.__revCommit.getCommitterIdent().getWhen()

class CommitList(list):
  def __init__(self, revCommits):
    list.__init__(self)
    for revCommit in revCommits:
      self.append(Commit(revCommit))

class ComposerGit(object):
  def __init__(self, workingpath, repopath=None):
    self.__workingpath = workingpath
    if not isinstance(self.__workingpath, File):
      self.__workingpath = File(str(workingpath))
    if repopath == None:
      repopath = os.path.join(getBaseRepoPath(),self.getRepoName(),".git")
    self.__repopath = File(repopath)
    self.__branch = "refs/heads/master"

  def getWorkingPath(self):
    return str(self.__workingpath)
    
  def getRepoPath(self):
    return str(self.__repopath)

  def getRepoName(self):
    return self.__workingpath.getName()

  def getUserName(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      return config.getString("user", None, "name")
    finally:
      self._close(git)

  def getBranch(self):
    return self.__branch

  def setBranch(self, branch="refs/heads/master"):
    if "/" not in branch:
      branch="refs/heads/" + branch
    self.__branch = branch

  def init(self):
    git_init = Git.init()
    git_init.setDirectory(self.__workingpath)
    git_init.setGitDir(self.__repopath)
    f = open(os.path.join(self.__workingpath,".gitignore"), "w")
    f.write("*.class\n")
    f.write(".directory\n")
    f.close()
    
  def cloneRepository(self, remote, branch=None, monitor=None):
    git_clone = Git.cloneRepository()
    git_clone.setDirectory(self.__repopath.getParentFile())
    if branch==None:
      git_clone.setCloneAllBranches(True) 
    else:
      git_clone.setBranch(branch)
      git_clone.setBranchesToClone([branch,])
    git_clone.setNoCheckout(True)
    git_clone.setURI(remote)
    if monitor!=None:
      git_clone.setProgressMonitor(monitor)
    
    repo = git_clone.call()
    repo.close()
    
  def _open(self):
    #print ">>> open, repopath: ", self.__repopath.getAbsolutePath()
    #print ">>> open, workingpath: ", self.__workingpath.getAbsolutePath()
    builder = FileRepositoryBuilder()
    builder.setGitDir(self.__repopath)
    builder.setWorkTree(self.__workingpath)
    repo = builder.build()
    git = Git(repo)    
    return git

  def _close(self, git):
    if git == None:
      return
    repo = git.getRepository()
    git.close()
    repo.close()

  def getRemoteURL(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      remoteUrl = config.getString("remote","origin","url")
      #print "### remoteUrl", repr(remoteUrl)
      return remoteUrl
    finally:
      self._close(git)
  
  def status(self):
    git = self._open()
    try:
      status = git.status().call()
      changes = Changes()
      for f in status.getAdded():
        changes.append(ComposerGitStatus("local", "add",f))
      for f in status.getChanged():
        changes.append(ComposerGitStatus("local", "changed",f))
      for f in status.getRemoved():
        changes.append(ComposerGitStatus("local", "removed",f))
      for f in status.getMissing():
        changes.append(ComposerGitStatus("local", "missing",f))
      for f in status.getModified():
        changes.append(ComposerGitStatus("local", "modified",f))
      for f in status.getUntracked():
        changes.append(ComposerGitStatus("local", "untracked",f))
      #for f in status.getUntrackedFolders():
      #  changes.append(ComposerGitStatus("untracked",f))
      for f in status.getConflicting():
        changes.append(ComposerGitStatus("both", "conflicting",f))
      for f in status.getUncommittedChanges():
        changes.append(ComposerGitStatus("local", "uncommitted",f))
      changes = changes.values()
      changes.sort(cmp=lambda x,y: cmp(x.getWorkingPath(), y.getWorkingPath()))
      return changes
    finally:
      self._close(git)
  
  def add(self, files):
    git = self._open()
    try:
      git_add = git.add()
      for f in files:
        git_add.addFilepattern(str(f))
      git_add.call()
    finally:
      self._close(git)

  def rm(self, files):
    git = self._open()
    try:
      git_rm = git.rm()
      for f in files:
        git_rm.addFilepattern(str(f))
      git_rm.call()
    finally:
      self._close(git)

  def checkout(self, files):
    git = self._open()
    try:
      git_checkout = git.checkout()
      git_checkout.setName(self.getBranch())
      #print "### checkout, files:", files
      if files != None and len(files)>0:
        git_checkout.addPaths(files)
      git_checkout.setCreateBranch(False)
      git_checkout.setStartPoint(self.getBranch())
      #print "### checkout:", git_checkout
      git_checkout.call()
    finally:
      self._close(git)

  def commit(self, message=""):
    git = self._open()
    try:
      git.commit().setMessage(message).call()
      self._close(git)
    finally:
      self._close(git)

  def push(self, username, password, monitor=None):
    git = self._open()
    try:
      git_push = git.push()
      git_push.setCredentialsProvider(UsernamePasswordCredentialsProvider(username, password))
      if monitor!=None:
        git_push.setProgressMonitor(monitor)
      responses = git_push.call()
      status = str(responses[0].getRemoteUpdate("refs/heads/master" ).getStatus())
      return status
    finally:
      self._close(git)

  def diff(self, path):
    #print "### diff, path:", repr(path)
    git = self._open()
    try:
      outputStream = ByteArrayOutputStream()
      git_diff = git.diff()
      git_diff.setPathFilter(PathFilter.create(path))
      git_diff.setOutputStream( outputStream )
      git_diff.setSourcePrefix("master:")
      git_diff.setDestinationPrefix("Working-folder:")
      diffEntries = git_diff.call()
      #print "### diff, diffEntries: ", diffEntries
      out = outputStream.toString()
      #print "### diff, out: ", out
      return out
    finally:
      self._close(git)

  def pull(self, branch="refs/heads/master", strategy=None, monitor=None):
    git = self._open()
    try:
      strategy = pullStrategies.get(strategy,ThreeWayMergeStrategy.RESOLVE)
      git_pull = git.pull()
      git_pull.setStrategy(strategy)
      if branch != "":
        git_pull.setRemoteBranchName(branch)
      if monitor!=None:
        git_pull.setProgressMonitor(monitor)
      result = git_pull.call()
      rebaseResult = result.getRebaseResult()
      mergeResult = result.getMergeResult()
      print "### pull, isSuccessful:", result.isSuccessful()
      print "### pull, rebaseResult.getStatus():", rebaseResult.getStatus()
      print "### pull, rebaseResult.getConflicts():", rebaseResult.getConflicts()
      print "### pull, rebaseResult.getFailingPaths():", rebaseResult.getFailingPaths()
      print "### pull, mergeResult.getMergeStatus():", rebaseResult.getMergeStatus()
      print "### pull, mergeResult.getConflicts():", rebaseResult.getConflicts()
      print "### pull, mergeResult.getFailingPaths():", rebaseResult.getFailingPaths()
      print "### pull, mergeResult.getCheckoutConflicts():", rebaseResult.getCheckoutConflicts()
      if result.isSuccessful():
        return "OK"
      return str(result)
      
    finally:
      self._close(git)

  def log(self, maxCount=20):
    git = self._open()
    try:
      git_log = git.log()
      git_log.setMaxCount(maxCount)
      commits = CommitList(git_log.call())
      return commits
    finally:
      self._close(git)
  
def main(*args):
    pass
