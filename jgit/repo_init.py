# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
reload(repo_utils)
from repo_utils import Git, getSelectedFolder, warning, SimpleDialog, message

class RepoInitPanel(FormPanel):
  def __init__(self, repoName, repoPath, workingPath):
    FormPanel.__init__(self,getResource(__file__,"repo_init.xml"))
    self.txtRepoName.setText(repoName)
    self.txtRepoPath.setText(repoPath)
    self.txtWorkingPath.setText(workingPath)


def repo_init():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos para crear un nuevo repositorio local.")
    return 
  git = Git(folder.getFile())
  if os.path.exists(git.getRepoPath()):
    warning("Ya existe el repositorio local asociado a la carpeta '%s'." % git.getRepoName())
    return 

  panel = RepoInitPanel(git.getRepoName(),git.getRepoPath(), git.getWorkingPath() )
  dialog = SimpleDialog(panel)
  dialog.showModal()
  if dialog.isOk():
    git.init()
    message("Repositorio local creado")

def main(*args):
  repo_init()
  