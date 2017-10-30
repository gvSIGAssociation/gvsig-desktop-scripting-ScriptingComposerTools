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

from repo_utils import Git, getComposer, getSelectedFolder
from repo_utils import warning, message

from org.gvsig.scripting.swing.api import JScriptingComposer

def repo_diff(path, git=None):
  if git == None:
    folder = getSelectedFolder()
    if folder == None:
      warning("Debera seleccionar una carpeta en el arbol de proyectos para crear un nuevo repositorio local.")
      return 
    git = Git(folder.getFile())
    if not os.path.exists(git.getRepoPath()):
      warning("No existe un repositorio local asociado a la carpeta '%s'." % git.getRepoName())
      return
  out = git.diff(path)
  
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
  

def main(*args):
    pass
