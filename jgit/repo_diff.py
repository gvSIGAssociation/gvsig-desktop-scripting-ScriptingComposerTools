# encoding: utf-8

import gvsig

#
# What’s the Difference? Creating Diffs with JGit
# http://www.codeaffine.com/2016/06/16/jgit-diff/
#
# JGit diff unit test
# https://gist.github.com/rherrmann/5341e735ce197f306949fc58e9aed141
#

import os
import StringIO

from addons.ScriptingComposerTools.javadocviewer.webbrowserpanel.browserpanel import BrowserPanel

import pygments
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from repo_utils import Git, getComposer, getSelectedGit, getSelectedUnit
from repo_utils import warning, message

from org.gvsig.scripting.swing.api import JScriptingComposer

def repo_diff(path=None, outdiff=None, git=None):
  if git == None:
    git = getSelectedGit()
    if git == None:
      return

  if path == None:
    unit = getSelectedUnit()
    if unit==None:
      message("Can't show diff, select a element under Git control in the project tree")
      return
    path = unit.getFiles()[0].getAbsolutePath()
    
  if os.path.isabs(path):
    path = os.path.relpath(path, git.getWorkingPath())
      
  if outdiff==None:
    out = git.diff(path)
  else:
    out = outdiff
      
  html = StringIO.StringIO()
  lexer = get_lexer_by_name("Diff")
  formatter = HtmlFormatter(style='default')
  styles = formatter.get_style_defs()
  html.write("<style>\n")
  html.write(styles)
  html.write("</style>\n")

  pygments.highlight(out, lexer, formatter, html)
  
  #print html.getvalue()

  browser = BrowserPanel()  
  browser.setContent(html.getvalue())
  composer = getComposer()
  composer.getDock().add(
    "#GitDiff."+path,
    os.path.basename(path) + " [diff]",
    browser,
    JScriptingComposer.Dock.DOCK_CENTER
  )
  composer.getDock().select("#GitDiff."+path)
  browser.asJComponent().requestFocus()
  

def test1():
  unit = getSelectedUnit()
  if unit == None:
    message("Debera seleccionar un elemento en el arbol de proyectos.")
    return
  repo_diff(unit.getFiles()[0].getAbsolutePath())

def main(*args):
  #test1()
  repo_diff()
