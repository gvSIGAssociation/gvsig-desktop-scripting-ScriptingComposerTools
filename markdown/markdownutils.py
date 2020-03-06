# encoding: utf-8

import gvsig
from gvsig import commonsdialog

import os
import os.path

from javax.swing import SwingUtilities

from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.tools import ToolsLocator
from org.gvsig.scripting import ScriptingExternalFile


def getCurrentFile():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return None
  editor = composer.getCurrentEditor()
  if editor == None:
    return None
  unit = editor.getUnit()
  getFile = getattr(unit,"getExternalFile",None)
  if getFile == None:
    return None
  f = getFile()
  if f == None:
    return None
  return f.getAbsolutePath()

def isEditingMarkdown():
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return False
  editor = composer.getCurrentEditor()
  if editor == None:
    return False
  unit = editor.getUnit()
  getFile = getattr(unit,"getExternalFile",None)
  if getFile == None:
    return False
  name, ext = os.path.splitext(getFile().getName())
  if ext == ".md":
    return True
  return False

def getJTextComponent(event=None):
  if event == None:
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  else:
    composer = event.getSource().getContext()
  if composer == None:
    return
  editor = composer.getCurrentEditor()
  if editor == None:
    return None
  textComponent = editor.getJTextComponent()
  return textComponent
  
def format_title(num_title):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  sel_start = comp.getSelectionStart()

  BUFSIZE = 1000
  n = BUFSIZE
  if sel_start - n < 0:
    n = sel_start
  s = doc.getText(sel_start-n,n)
  sel_start = sel_start - (n - s.rfind("\n")) + 1

  n = 100
  if sel_start + n > doc.getLength():
    n = doc.getLength() - sel_start - 1
  s = doc.getText(sel_start,n)
  if s.startswith("#"):
    n = s.find(" ")
    if n>=0 :
      doc.remove(sel_start,n)
      s = s.replace("#","")
      if len(s)>0:
        doc.insertString(sel_start,s.lstrip(),None)
  doc.insertString(sel_start,("#"*num_title)+" ",None)
  comp.setSelectionStart(sel_start)
  comp.setSelectionEnd(sel_start)
  comp.requestFocusInWindow()
   
  
def insert_text_block(text):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  sel_start = comp.getSelectionStart()

  BUFSIZE = 1000
  n = BUFSIZE
  if sel_start - n < 0:
    n = sel_start
  s = doc.getText(sel_start-n,n)
  sel_start = sel_start - (n - s.rfind("\n")) + 1

  doc.insertString(sel_start,text+"\n",None)
  comp.setSelectionStart(sel_start)
  comp.setSelectionEnd(sel_start)
  comp.requestFocusInWindow()
   
  
def insert_text(text):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  sel_start = comp.getSelectionStart()
  doc.insertString(sel_start,text,None)
  comp.setSelectionStart(sel_start)
  comp.setSelectionEnd(sel_start)
  comp.requestFocusInWindow()
   
  
def format_text(pre, post, block=False):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  sel_end = comp.getSelectionEnd()
  sel_start = comp.getSelectionStart()
  if block:
    BUFSIZE = 1000
    n = BUFSIZE
    if sel_start - n < 0:
      n = sel_start
    s = doc.getText(sel_start-n,n)
    sel_start = sel_start - (n - s.rfind("\n"))
    n = BUFSIZE
    if sel_end + n > doc.getLength():
      n = doc.getLength() - sel_end - 1
    s = doc.getText(sel_end,n)
    sel_end =sel_end + s.find("\n") + 1
  doc.insertString(sel_start,pre,None)
  doc.insertString(sel_end+len(pre),post,None)
  comp.setSelectionStart(sel_end+len(pre))
  comp.setSelectionEnd(sel_end+len(pre))
  comp.requestFocusInWindow()

def getCanonicalPath(path):
  path = os.path.normcase(path)
  path = os.path.normpath(path)
  path = os.path.realpath(path)
  return path

def insert_image(currentfolder, imagePath, text="Alt text"):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  
  currentfolder = getCanonicalPath(currentfolder)
  imagePath = getCanonicalPath(imagePath)
  imagePath = os.path.relpath(imagePath, currentfolder)
  
  html = "![%s](%s)" % (text, imagePath)
  sel_start = comp.getSelectionStart()
  doc.insertString(sel_start,html,None)
  comp.setSelectionStart(sel_start)
  comp.setSelectionEnd(sel_start + len(html))


def insert_include(currentfolder, pathname, tagname="include"):
  comp = getJTextComponent()
  if comp == None:
    return
  doc = comp.getDocument()
  if doc == None:
    return
  
  currentfolder = getCanonicalPath(currentfolder)
  pathname = getCanonicalPath(pathname)
  pathname = os.path.relpath(pathname, currentfolder)
  
  html = "{%% %s %s %%}\n" % (tagname,pathname)

  sel_start = comp.getSelectionStart()

  BUFSIZE = 1000
  n = BUFSIZE
  if sel_start - n < 0:
    n = sel_start
  s = doc.getText(sel_start-n,n)
  sel_start = sel_start - (n - s.rfind("\n")) + 1
  
  doc.insertString(sel_start,html,None)
  comp.setSelectionStart(sel_start)
  comp.setSelectionEnd(sel_start + len(html))


def test_insert_image():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  from addons.ScriptingComposerTools.markdown import image_selector 
  reload(image_selector)
  
  f = getCurrentFile()
  if f == None:
    return
  img = image_selector.select_image(f)
  if img == None:
    return
  insert_image(os.path.dirname(f), img)

def test_bold():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  format_text("**","**")

def test_title():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  format_title(3)

def test_include():
  if not SwingUtilities.isEventDispatchThread():
    SwingUtilities.invokeLater(main)
    return
  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
  if composer == None:
    return
  folder = os.path.dirname(getCurrentFile())
  f = commonsdialog.openFileDialog("Select file to include",folder, composer.asJComponent())
  if f==None or len(f)==0:
    return
  insert_include(folder, f[0])


def main(**args):
  #test_insert_image()
  #test_title()
  test_include()