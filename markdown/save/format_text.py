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

class MarkdownFormatTextBoldAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Bold")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatTextBold")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-bold.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Bold")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_text("**","**")  

class MarkdownFormatTextItalicAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Italic")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatTextItalic")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-italic.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Italic")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_text("*","*")  

class MarkdownFormatTextUnderlineAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Underline")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatTextUnderline")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-underline.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Underline")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_text("__","__")  

class MarkdownFormatTextCodeAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Code")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatTextCode")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-code.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Code")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_text("\n```","```\n", block=True)  

def selfRegister():
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  action = MarkdownFormatTextBoldAction()
  #manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Markdown",action)

  action = MarkdownFormatTextItalicAction()
  #manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Markdown",action)

  action = MarkdownFormatTextUnderlineAction()
  #manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Markdown",action)

  action = MarkdownFormatTextCodeAction()
  #manager.addComposerTool(action)
  manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Markdown",action)


def test():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  #format_text("**","**")  
  #format_text("\n```","```\n", True)  

def main():
  #selfRegister()
  test()
  