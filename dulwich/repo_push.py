# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

import os

import repo_utils
reload(repo_utils)

from repo_utils import getBaseRepoPath, getSelectedFolder, warning, inputbox, message

from dulwich import porcelain


def repo_push():
  usuario=inputbox("Usuario")
  clave= inputbox("Clave")
  url =  "https://"+ usuario +":" + clave + "@github.com/jjdelcerro/ScriptingComposerTools.git"
  repopath = os.path.join(getBaseRepoPath(),"ScriptingComposerTools")
  porcelain.push(repopath, url, "master")

def main(*args):
  repo_push()
  