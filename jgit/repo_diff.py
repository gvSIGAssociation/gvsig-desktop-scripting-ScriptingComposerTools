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

from repo_utils import Git, getComposer, getSelectedGit, getSelectedUnit
from repo_utils import warning, message

from org.gvsig.scripting.swing.api import JScriptingComposer
from org.gvsig.tools.swing.api import ToolsSwingLocator

def diffOutput2html_use_diff2html(diffout):
  import diff2html
  #         table { border:0px; border-collapse:collapse; width: 100%; font-size:0.75em; font-family: Lucida Console, monospace }
  
  html_hdr = """<!DOCTYPE html>
<html lang="en" dir="ltr"
    xmlns:dc="http://purl.org/dc/terms/">
<head>
    <meta charset="utf-8" />
    <meta name="generator" content="diff2html.py (http://git.droids-corp.org/gitweb/?p=diff2html)" />
    <!--meta name="author" content="Fill in" /-->
    <title>HTML Diff </title>
    <link rel="shortcut icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAgMAAABinRfyAAAACVBMVEXAAAAAgAD///+K/HwIAAAAJUlEQVQI12NYBQQM2IgGBQ4mCIEQW7oyK4phampkGIQAc1G1AQCRxCNbyW92oQAAAABJRU5ErkJggg==" type="image/png" />
    <meta property="dc:language" content="en" />
    <!--meta property="dc:date" content="" /-->
    <meta property="dc:modified" content="2017-11-16T03:21:59.799000+01:00" />
    <meta name="description" content="File comparison" />
    <meta property="dc:abstract" content="File comparison" />
    <style>
        table { border:0px; width: 100%; border-collapse: collapse; font-family: monospace }
        td, th { border:0px;  }
        td.line { color:#8080a0 }
        th { background: black; color: white }
        tr.diffunmodified td { background: white }
        tr.diffhunk td { background: white }
        tr.diffadded td { background: #b4ffb4 }
        tr.diffdeleted td { background: #FFCCCC }
        tr.diffchanged td { background: #a0c8ff } 
        span.diffchanged2 { background: #8fb3e5 }
        span.diffponct { color: #B08080 }
        tr.diffmisc td {}
        tr.diffseparator td {}
    </style>
</head>
<body>
"""
  html_footer = """
</body></html>
"""
  return html_hdr + diff2html.parse_from_memory(diffout, True, False) + html_footer
  #return diff2html.parse_from_memory(diffout, True, False) 

def diffOutput2html_use_pygments(diffout):
  import pygments
  from pygments.formatters.html import HtmlFormatter
  from pygments.lexers import get_lexer_by_name
  from pygments.styles import get_style_by_name
  
  html = StringIO.StringIO()
  lexer = get_lexer_by_name("Diff")
  formatter = HtmlFormatter(style='default')
  styles = formatter.get_style_defs()
  html.write("<style>\n")
  html.write(styles)
  html.write("</style>\n")
  pygments.highlight(diffout, lexer, formatter, html)
  return html.getvalue()

def diffOutput2html(diffout):
  try:
    return diffOutput2html_use_diff2html(diffout)
  except:
    pass
  try:
    return diffOutput2html_use_pygments(diffout)
  except:
    pass
  return "<pre>"+diffout+"</pre>"

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
      
  html = diffOutput2html(out)
  
  browser = ToolsSwingLocator.getToolsSwingManager().createJWebBrowser()
  browser.setContent(html,"text/html")
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
  test1()
  #repo_diff()
