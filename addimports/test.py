# encoding: utf-8

import gvsig

def main(*args):

  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()

  print Feature.ALL
  print composer

  model = DefaultListModel()
  print model
