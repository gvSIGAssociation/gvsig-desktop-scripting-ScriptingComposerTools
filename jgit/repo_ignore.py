# encoding: utf-8

import gvsig

import os

from repo_utils import Git, getComposer, getSelectedFolder
from repo_utils import warning, SimpleDialog, message, inputbox, windowManager, confirm

from org.gvsig.scripting import ScriptingLocator

from java.io import File

def repo_ignore():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos.")
    return 
  git = Git(folder.getFile())
  if not os.path.exists(git.getRepoPath()):
    warning("No existe un repositorio local asociado a la carpeta '%s'." % git.getRepoName())
    return
  fname = os.path.join(git.getWorkingPath(),".gitignore")
  if not os.path.exists(fname):
    f = open(fname, "w")
    f.write("*.class\n")
    f.write(".directory\n")
    f.close()    
  composer = getComposer()
  manager = ScriptingLocator.getManager()
  unit = manager.createExternalFile(folder,".gitignore")
  composer.scriptEdit(unit)
   
def main(*args):
  repo_ignore()
  