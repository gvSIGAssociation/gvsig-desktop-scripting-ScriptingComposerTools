# encoding: utf-8

from gvsig import *

from addons.ScriptingComposerTools import threadlist
from addons.ScriptingComposerTools import codenavigator
from addons.ScriptingComposerTools import abeille
from addons.ScriptingComposerTools import javadocviewer
from addons.ScriptingComposerTools import editors
from addons.ScriptingComposerTools import fontchooser
from addons.ScriptingComposerTools import rstpreview
from addons.ScriptingComposerTools import loadlayer
from addons.ScriptingComposerTools import fileexplorer
from addons.ScriptingComposerTools import jgit
from addons.ScriptingComposerTools import classbrowser
from addons.ScriptingComposerTools import consolejython
from addons.ScriptingComposerTools import useplugin

def main(*args):
  script.registerDataFolder("ScriptingComposerTools")

  abeille.selfRegister()
  codenavigator.selfRegister()
  classbrowser.selfRegister()
  threadlist.selfRegister()
  javadocviewer.selfRegister()
  editors.selfRegister()
  fontchooser.selfRegister()
  rstpreview.selfRegister()
  loadlayer.selfRegister()
  fileexplorer.selfRegister()
  jgit.selfRegister()
  consolejython.selfRegister()
  useplugin.selfRegister()
