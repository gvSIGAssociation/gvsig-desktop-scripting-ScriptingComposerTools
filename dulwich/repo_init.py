# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
reload(repo_utils)

from repo_utils import getBaseRepoPath, getSelectedFolder, warning, SimpleDialog, message

from dulwich.config import ConfigFile
from dulwich import porcelain

class RepoInitPanel(FormPanel):
  def __init__(self, repoName, repoPath):
    FormPanel.__init__(self,getResource(__file__,"repo_init.xml"))
    self.txtRepoName.setText(repoName)
    self.txtRepoPath.setText(repoPath)
    self.txtUserName.setText(os.getlogin())
    self.txtUserMail.setText(os.getlogin())

  def getUserName(self):
    return self.txtUserName.getText()
    
  def getUserMail(self):
    return self.txtUserMail.getText()
    
    
def repo_init():
  folder = getSelectedFolder()
  if folder == None:
    warning("Debera seleccionar una carpeta en el arbol de proyectos para crear un nuevo repositorio local.")
    return 
  repopath = os.path.join(getBaseRepoPath(),folder.getId())
  
  if os.path.exists(repopath):
    warning("Ya existe el repositorio local asociado a la carpeta '%s'." % folder.getId())
    return 

  panel = RepoInitPanel(folder.getId(),repopath )
  dialog = SimpleDialog(panel)
  dialog.showModal()
  if dialog.isOk():
    repo = porcelain.init(repopath)

    configpath = os.path.join(repopath,".git","config")
    config = ConfigFile.from_path(configpath)
    config.set("user","name",bytes(panel.getUserName()))
    config.set("user","email",bytes(panel.getUserMail()))
    config.write_to_path(configpath)

    message("Repositorio local creado")


def main(*args):
  repo_init()
