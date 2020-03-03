# encoding: utf-8
"""
Este modulo registra el editor de ficheros ".png".
"""
import gvsig
from gvsig import logger, LOGGER_INFO

import os

from org.gvsig.scripting.swing.api import AbstractEditorFactory
from org.gvsig.scripting import ScriptingExternalFile
from org.gvsig.scripting.swing.api import ScriptingSwingLocator

import editor
reload(editor)
from editor import ImageViewer

class ImageEditorFactory(AbstractEditorFactory):
  def __init__(self):
    AbstractEditorFactory.__init__(self,"ImageViewer","Image Viewer")
    
  def doCreate(self, unit):
    return ImageViewer(unit)

  def canCreate(self, unit):
    if isinstance(unit,ScriptingExternalFile):
      f = unit.getExternalFile()
      extension = os.path.splitext(f.getName())[1]
      if extension.lower() in (".png", ".jpg", ".jpeg"):
        return True
    return False

def selfRegister():
  manager = ScriptingSwingLocator.getUIManager()
  manager.registerEditor(ImageEditorFactory())

def main(*args):
  selfRegister()
  