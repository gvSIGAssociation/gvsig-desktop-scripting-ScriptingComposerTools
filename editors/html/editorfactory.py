# encoding: utf-8
"""
Este modulo registra el editor de ficheros ".properties".

Precisamos un editor especial para los ficheros properties ya que 
estos requieren de una codificacion especial de caracteres.

"""
import gvsig
from gvsig import logger, LOGGER_INFO

import os

from org.gvsig.scripting.swing.api import AbstractEditorFactory
from org.gvsig.scripting import ScriptingExternalFile
from org.gvsig.scripting.swing.api import ScriptingSwingLocator

import editor
reload(editor)
from editor import HTMLViewer

class HTMLEditorFactory(AbstractEditorFactory):
  def __init__(self):
    AbstractEditorFactory.__init__(self,"HTMLViewer","HTML Viewer")
    
  def doCreate(self, unit):
    return HTMLViewer(unit)

  def canCreate(self, unit):
    if isinstance(unit,ScriptingExternalFile):
      f = unit.getExternalFile()
      extension = os.path.splitext(f.getName())[1]
      if extension.lower() in (".htm", ".html", ".png"):
        return True
    return False

def selfRegister():
  manager = ScriptingSwingLocator.getUIManager()
  manager.registerEditor(HTMLEditorFactory())

def main(*args):
  selfRegister()
  