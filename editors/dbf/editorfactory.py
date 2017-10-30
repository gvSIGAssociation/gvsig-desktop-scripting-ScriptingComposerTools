# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_INFO

import os

from org.gvsig.scripting.swing.api import AbstractEditorFactory
from org.gvsig.scripting import ScriptingExternalFile
from org.gvsig.scripting.swing.api import ScriptingSwingLocator

import editor
reload(editor)
from editor import DBFEditor

class DbfEditorFactory(AbstractEditorFactory):
  def __init__(self):
    AbstractEditorFactory.__init__(self,"DBFEditor","Editor for dbf file contents")
    
  def doCreate(self, unit):
    return DBFEditor(unit)

  def canCreate(self, unit):
    if isinstance(unit,ScriptingExternalFile):
      f = unit.getExternalFile()
      extension = os.path.splitext(f.getName())[1]
      if extension.lower() == ".dbf":
        return True
    return False

def selfRegister():
  manager = ScriptingSwingLocator.getUIManager()
  manager.registerEditor(DbfEditorFactory())

def main(*args):
  selfRegister()
  