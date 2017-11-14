# encoding: utf-8

from gvsig import *

import threadlist
import lint
import codenavigator
import abeille
import javadocviewer
import editors
import fontchooser
import rstpreview
import loadlayer
import addimports
import fileexplorer
import jgit
import classbrowser
import consolejython

def main(*args):
  abeille.selfRegister()
  codenavigator.selfRegister()
  classbrowser.selfRegister()
  lint.selfRegister()
  threadlist.selfRegister()
  javadocviewer.selfRegister()
  editors.selfRegister()
  fontchooser.selfRegister()
  rstpreview.selfRegister()
  loadlayer.selfRegister()
  addimports.selfRegister()
  fileexplorer.selfRegister()
  jgit.selfRegister()
  consolejython.selfRegister()

