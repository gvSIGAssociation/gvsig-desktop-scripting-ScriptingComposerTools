# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon
from gvsig import commonsdialog

import os

from javax.swing import SwingUtilities
from javax.swing import AbstractAction, Action

from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting.swing.api import ScriptingSwingLocator

from addons.ScriptingComposerTools.markdown.image_selector import select_image
from addons.ScriptingComposerTools.markdown.markdownutils import isEditingMarkdown
from addons.ScriptingComposerTools.markdown.markdownutils import format_text
from addons.ScriptingComposerTools.markdown.markdownutils import format_title
from addons.ScriptingComposerTools.markdown.markdownutils import getCurrentFile
from addons.ScriptingComposerTools.markdown.markdownutils import insert_image
from addons.ScriptingComposerTools.markdown.markdownutils import insert_include
from addons.ScriptingComposerTools.markdown.markdownutils import insert_text_block
from addons.ScriptingComposerTools.markdown.markdownutils import insert_text

class MarkdownFormatTitleAction(AbstractAction):
  def __init__(self, num_title):
    AbstractAction.__init__(self,"Title %d" % num_title)
    self.num_title = num_title
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatTitle%d" % num_title)
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-h%d.png" % num_title)))
    self.putValue(Action.SHORT_DESCRIPTION, "Title %d" % num_title)

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_title(self.num_title)  

class MarkdownFormatTextAction(AbstractAction):
  def __init__(self, name, pre, post, block=False):
    AbstractAction.__init__(self,name)
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownFormatText%s" % name)
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-%s.png" % name.lower())))
    self.putValue(Action.SHORT_DESCRIPTION, name)
    self._name = name
    self._pre = pre
    self._post = post
    self._block = block

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    format_text(self._pre, self._post, self._block)  

class MarkdownIncludeAction(AbstractAction):
  def __init__(self, tagName="Include"):
    AbstractAction.__init__(self,tagName.replace("_"," "))
    self.putValue(Action.ACTION_COMMAND_KEY, "Markdown%s" % tagName.replace(" ",""))
    #self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","format-text-%s.png" % name.lower())))
    self.putValue(Action.SHORT_DESCRIPTION, tagName.replace("_"," "))
    self._tagName = tagName

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer == None:
      return
    folder = os.path.dirname(getCurrentFile())
    f = commonsdialog.openFileDialog("Select file to include",folder, composer.asJComponent())
    if f==None or len(f)==0:
      return
    insert_include(folder, f[0], self._tagName)

class MarkdownInsertImageAction(AbstractAction):
  def __init__(self):
    AbstractAction.__init__(self,"Insert image")
    self.putValue(Action.ACTION_COMMAND_KEY, "MarkdownInsertImage")
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","image-add.png")))
    self.putValue(Action.SHORT_DESCRIPTION, "Insert image")

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    f = getCurrentFile()
    if f == None:
      return
    img = select_image(f)
    if img == None:
      return
    insert_image(os.path.dirname(f), img)

class MarkdownInsertTextBlockAction(AbstractAction):
  def __init__(self, name, text):
    AbstractAction.__init__(self,name.replace("_"," "))
    self.putValue(Action.ACTION_COMMAND_KEY, "Markdown%s" % name.replace(" ",""))
    self.putValue(Action.SMALL_ICON, load_icon((__file__,"images","%s.png" % name.lower().replace("_","-"))))
    self.putValue(Action.SHORT_DESCRIPTION, name.replace("_"," "))
    self._text = text

  def isEnabled(self):
    return isEditingMarkdown()
    
  def actionPerformed(self,e):
    insert_text_block(self._text)

def selfRegister():
  add_in_toolbar = True
  
  i18nManager = ToolsLocator.getI18nManager()
  manager = ScriptingSwingLocator.getUIManager()
  for action in (
      MarkdownFormatTextAction("Bold","**","**"),
      MarkdownFormatTextAction("Italic", "*", "*"),
      MarkdownFormatTextAction("Underline", "__", "__"),
      MarkdownFormatTextAction("Code", "\n```","```\n", block=True),
      MarkdownInsertImageAction(),
      MarkdownFormatTitleAction(1),
      MarkdownFormatTitleAction(2),
      MarkdownFormatTitleAction(3),
      MarkdownFormatTitleAction(4),
      MarkdownFormatTitleAction(5),
      MarkdownFormatTitleAction(6),
      MarkdownIncludeAction("Include"),
      MarkdownIncludeAction("Include_relative"),
      MarkdownInsertTextBlockAction("Insert_pagebreak","{{pagebreak /}}"),
    ):
    print repr(action.getValue(Action.NAME)), repr(action.getValue(Action.SMALL_ICON))
    if add_in_toolbar and action.getValue(Action.SMALL_ICON)!=None :
      manager.addComposerTool(action)
    manager.addComposerMenu(i18nManager.getTranslation("Tools")+"/Markdown",action)

def main():
  selfRegister()
  