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
import os.path
import base64

from java.io import File

from org.eclipse.jgit.storage.file import FileRepositoryBuilder
from org.eclipse.jgit.api import Git
from org.eclipse.jgit.api.ResetCommand import ResetType

from org.gvsig.scripting import ScriptingLocator

from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider

from org.eclipse.jgit.treewalk.filter import PathFilter

from java.io import ByteArrayOutputStream

from org.eclipse.jgit.merge import ThreeWayMergeStrategy
from org.eclipse.jgit.merge import MergeStrategy
from org.eclipse.jgit.revwalk import RevWalk
from org.eclipse.jgit.treewalk import CanonicalTreeParser
from org.eclipse.jgit.lib.BranchConfig import BranchRebaseMode


def getBaseRepoPath():
  manager = ScriptingLocator.getManager()
  path = os.path.join(manager.getDataFolder("ScriptingComposerTools").getAbsolutePath(),"git")
  try:
    os.makedirs(path)
  except OSError,ex:
    pass
  #print ">>> base repo path", path
  return path

DEFAULT_BRANCH = "refs/heads/master"

def getDefaultBranch(git):
  try:
    config = git.getRepository().getConfig()
    subsections=config.getSubsections("branch")
    if subsections==None or len(subsections)==0:
      return DEFAULT_BRANCH
    for name in subsections:
      branch = config.getString("branch", name, "merge")
      if not (branch in (None,'')):
        return branch
    return DEFAULT_BRANCH
  except:
    return DEFAULT_BRANCH
    

pullStrategies = {
  "OURS"                   : MergeStrategy.OURS,
  "RECURSIVE"              : ThreeWayMergeStrategy.RECURSIVE,
  "RESOLVE"                : ThreeWayMergeStrategy.RESOLVE,
  "SIMPLE_TWO_WAY_IN_CORE" : ThreeWayMergeStrategy.SIMPLE_TWO_WAY_IN_CORE,
  "THEIRS"                 : MergeStrategy.THEIRS
}

pullRebaseModes = {
  "NONE"     : BranchRebaseMode.NONE,
  "REBASE"   : BranchRebaseMode.REBASE,
  "PRESERVE" : BranchRebaseMode.PRESERVE
}

resetModes = {
  "HARD"    : ResetType.HARD,
  "KEEP"    : ResetType.KEEP,
  "MERGE"   : ResetType.MERGE,
  "MIXED"   : ResetType.MIXED,
  "SOFT"    : ResetType.SOFT
}

class ComposerGitStatus(object):
  def __init__(self, modified, status, workingpath):
    self.__modified = modified
    self.__status = status
    self.__workingpath = unicode(workingpath)

  def __repr__(self):
    return "status(%r,%r)" % (self.__status, self.__workingpath)

  def __str__(self):
    return self.__workingpath
    
  def getStatus(self):
    return self.__status

  def getWorkingPath(self):
    return self.__workingpath

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

  def _getRevCommit(self):
    return self.__revCommit
    
  def _getAbstractTreeIterator(self, git):
    walk = RevWalk(git.getRepository())
    tree = walk.parseTree(walk.parseCommit(self.__revCommit).getTree().getId())
    treeParser = CanonicalTreeParser()
    reader = git.getRepository().newObjectReader()
    try:
        treeParser.reset(reader, tree.getId())
    finally:
        #reader.release()
        #print dir(reader)
        walk.dispose()
    return treeParser

  def __str__(self):
    return unicode(self.__revCommit)
  
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
      self.__workingpath = File(unicode(workingpath))
    if repopath == None:
      repopath = os.path.join(getBaseRepoPath(),self.getRepoName(),".git")
    self.__repopath = File(repopath)
    self.__branch = None

  def __str__(self):
    return self.__repopath.getAbsolutePath()
    
  def getWorkingPath(self):
    return unicode(self.__workingpath)
    
  def getRepoPath(self):
    return unicode(self.__repopath)

  def getRepoName(self):
    return self.__workingpath.getName()

  def getUserName(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      return config.getString("user", None, "name")
    finally:
      self._close(git)

  def getUserMail(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      return config.getString("user", None, "email")
    finally:
      self._close(git)

  def getUserId(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      return config.getString("user", None, "username")
    finally:
      self._close(git)

  def getPassword(self):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      password = config.getString("user", None, "password")
      if password in ("",None):
        return None
      return base64.decodestring(password)
    finally:
      self._close(git)

  def setPassword(self, password):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      password = base64.encodestring(password)
      if password[-1] == "\n":
        password = password[:-1]
      config.setString("user", None, "password", password )
      config.save()
    finally:
      self._close(git)

  def setUserId(self, userId):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      config.setString("user", None, "username", userId )
      config.save()
    finally:
      self._close(git)

  def setUserName(self, userName):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      config.setString("user", None, "name", userName )
      config.save()
    finally:
      self._close(git)

  def setUserMail(self, email):
    git = self._open()
    try:
      config = git.getRepository().getConfig()
      config.setString("user", None, "email", email )
      config.save()
    finally:
      self._close(git)

  def getBranch(self, git = None):
    if self.__branch != None:
      return self.__branch
    if git == None:
      git = self._open()
      try:
        self.__branch = getDefaultBranch(git)
      finally:
        self._close(git)
    else:
      self.__branch = getDefaultBranch(git)
    return self.__branch

  def setBranch(self, branch=DEFAULT_BRANCH):
    if "/" not in branch:
      branch="refs/heads/" + branch
    self.__branch = branch

  def init(self):
    git_init = Git.init()
    git_init.setDirectory(self.__workingpath)
    git_init.setGitDir(self.__repopath)
    git_init.call()
    f = open(os.path.join(self.__workingpath.getAbsolutePath(),".gitignore"), "w")
    f.write("*.class\n")
    f.write(".directory\n")
    f.close()
    
  def cloneRepository(self, remote, branch=None, monitor=None, user=None, password=None):
    git_clone = Git.cloneRepository()
    git_clone.setDirectory(self.__repopath.getParentFile())
    if branch==None:
      git_clone.setCloneAllBranches(True) 
    else:
      git_clone.setBranch(branch)
      git_clone.setBranchesToClone([branch,])
    git_clone.setNoCheckout(False)
    git_clone.setURI(remote)
    if user!=None and password!=None :
      git_clone.setCredentialsProvider(UsernamePasswordCredentialsProvider(user, password))
      
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
      #print "###git add ",files
      git_add = git.add()
      for f in files:
        git_add.addFilepattern(unicode(f))
      git_add.call()
    finally:
      self._close(git)

  def rm(self, files):
    git = self._open()
    try:
      #print "###git rm ",files
      git_rm = git.rm()
      for f in files:
        git_rm.addFilepattern(unicode(f))
      git_rm.call()
      for f in files:
        f = os.path.join(self.__workingpath.getAbsolutePath(),f)
        if os.path.exists(f):
          os.remove(f)
    finally:
      self._close(git)

  def checkout(self, files):
    git = self._open()
    try:
      git_checkout = git.checkout()
      git_checkout.setName(self.getBranch(git))
      #print "### checkout, files:", files
      if files != None and len(files)>0:
        git_checkout.addPaths(files)
      git_checkout.setCreateBranch(False)
      git_checkout.setStartPoint(self.getBranch(git))
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
      status = unicode(responses[0].getRemoteUpdate(self.getBranch(git)).getStatus())
      return status
    finally:
      self._close(git)

  def diff(self, path=None, commitOld=None, commitNew=None):
    #print "### diff, path:", repr(path)
    git = self._open()
    try:
      outputStream = ByteArrayOutputStream()
      git_diff = git.diff()
      if path!=None:
        git_diff.setPathFilter(PathFilter.create(path))
      git_diff.setOutputStream( outputStream )
      git_diff.setSourcePrefix("master:")
      git_diff.setDestinationPrefix("Working-folder:")
      if commitOld!=None:
        #print "### git diff, old", commitOld
        git_diff.setOldTree(commitOld._getAbstractTreeIterator(git))
      if commitNew!=None:
        #print "### git diff, new", commitNew
        git_diff.setNewTree(commitNew._getAbstractTreeIterator(git))
        
      diffEntries = git_diff.call()
      #print "### diff, diffEntries: ", diffEntries
      out = outputStream.toString()
      #print "### diff, out: ", out
      return out
    finally:
      self._close(git)

  def reset(self, mode="MIXED"):
    git = self._open()
    try:
      # clear the merge state
      repository = git.getRepository()
      repository.writeMergeCommitMsg(None)
      repository.writeMergeHeads(None)
      
      mode = pullStrategies.get(unicode(mode),ResetType.MIXED)
      # reset the index and work directory to HEAD
      git_reset = git.reset()
      git_reset.setMode(mode).call() 

    finally:
      self._close(git)
    
  def pull(self, branch=None, strategy="RESOLVE", monitor=None, user=None, password=None, rebase=None):
    git = self._open()
    try:
      if branch == None:
        branch= self.getBranch(git)
      strategy = pullStrategies.get(unicode(strategy),ThreeWayMergeStrategy.RESOLVE)
      rebase = pullRebaseModes.get(unicode(rebase),BranchRebaseMode.NONE)
      git_pull = git.pull()
      git_pull.setStrategy(strategy)
      git_pull.setRebase(rebase)
      if branch != "":
        git_pull.setRemoteBranchName(branch)
      if monitor!=None:
        git_pull.setProgressMonitor(monitor)
      if user!=None and password!=None :
        git_pull.setCredentialsProvider(UsernamePasswordCredentialsProvider(user, password))
      result = git_pull.call()
      rebaseResult = result.getRebaseResult()
      mergeResult = result.getMergeResult()
      print "### pull, isSuccessful:", result.isSuccessful()
      if rebaseResult!=None:
        print "### pull, rebaseResult.getStatus():", rebaseResult.getStatus()
        print "### pull, rebaseResult.getConflicts():", rebaseResult.getConflicts()
        print "### pull, rebaseResult.getFailingPaths():", rebaseResult.getFailingPaths()
      if mergeResult!=None:
        print "### pull, mergeResult.getMergeStatus():", mergeResult.getMergeStatus()
        print "### pull, mergeResult.getConflicts():", mergeResult.getConflicts()
        print "### pull, mergeResult.getFailingPaths():", mergeResult.getFailingPaths()
        print "### pull, mergeResult.getCheckoutConflicts():", mergeResult.getCheckoutConflicts()
      if result.isSuccessful():
        return "OK"
      return unicode(result)
      
    finally:
      self._close(git)

  def log(self, paths=None, maxCount=20):
    git = self._open()
    try:
      git_log = git.log()
      if paths!=None:
        for path in paths:
          if os.path.isabs(path):
            path = os.path.relpath(path, self.getWorkingPath())
          git_log.addPath(path)
      git_log.setMaxCount(maxCount)
      commits = CommitList(git_log.call())
      return commits
    finally:
      self._close(git)


  
def main(*args):
    pass
