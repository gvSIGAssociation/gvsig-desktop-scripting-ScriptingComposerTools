# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

import os

from javax.swing import SwingUtilities
from javax.swing import AbstractAction, Action

from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator

from addons.ScriptingComposerTools.markdown.markdownutils import isEditingMarkdown, format_text

class MarkdownInsertImageAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Insert image")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownInsertImage")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","image-add.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Insert image")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    pass


def test():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  #format_text("**","**")  
  #format_text("\n```","```\n", True)  
  
def main():
  #selfRegister()
  test()
  