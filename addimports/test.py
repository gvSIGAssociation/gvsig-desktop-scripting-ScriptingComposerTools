# encoding: utf-8

import gvsig

def main(*args):

  composer = ScriptingSwingLocator.getUIManager().getActiveComposer()

  print Feature.ALL
  print composer

  model = DefaultListModel()
  print model

  x = getResource(__file__,"test.png")

  fname = os.path.join("hola", "adios")

  icon = load_icon("test")

  shutil.rmtree("xx")

  xx = StringIO()

  xx = currentLayer()

  msgbox("Hola")

  logger("Hola")

  x = SimpleName("hola")
  
  xx= File("Hola")
  
  