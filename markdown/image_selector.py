# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

import sys

from java.io import File
from java.awt import Dimension
from java.awt import BorderLayout
from java.awt import Image
from javax.swing import JFileChooser
from javax.swing import JLabel
from javax.swing.filechooser import FileFilter
from javax.swing.filechooser import FileView
from javax.swing import JPanel
from javax.swing import ImageIcon
from javax.swing import SwingUtilities
from javax.imageio import ImageIO

from java.beans import PropertyChangeListener

from org.apache.commons.io import FilenameUtils

from org.gvsig.scripting.swing.api import ScriptingSwingLocator
from org.gvsig.scripting.swing.api import JScriptingComposer

class ImageFileFilter(FileFilter):
  def accept(self, f):
    return f.isDirectory() or FilenameUtils.isExtension(
        f.getName().lower(), 
        ("png","jpeg","jpg")
    )

  def getDescription(self):
    return "Image files (png/jpeg)"

def scaleImage(image, w,h):
  width = image.getWidth(None)
  height = image.getHeight(None)
  ratio = 1.0   
  if width >= height:
    ratio = float(w-5) / width
    width = w-5
    height = int(height * ratio)
  else:
    ratio = float(h) / height
    height = h
    width = int(width * ratio)
  image = image.getScaledInstance(width, height, Image.SCALE_DEFAULT)
  return image

class ImagePreviewPanel(JPanel,PropertyChangeListener):
  def __init__(self):
    JPanel.__init__(self)
    self.image_icon = load_icon((__file__,"images","image-32x32.png"))
    self.setLayout(BorderLayout())
    self.label = JLabel()
    self.add(self.label,BorderLayout.CENTER)
    self.setPreferredSize(Dimension(250, -1))
    
  def propertyChange(self, e):
    propertyName = e.getPropertyName()  
    if propertyName==JFileChooser.SELECTED_FILE_CHANGED_PROPERTY:
      f = e.getNewValue()
      if f == None:
          return
      if FilenameUtils.isExtension(f.getName().lower(),("png","jpeg","jpg")):
        try:
          image = ImageIO.read(f)
          w = image.getWidth()
          h = image.getHeight()
          if w<1500 and h<1500 :
            image = scaleImage(image,250,250)
            self.label.setIcon(ImageIcon(image))
          else:
            self.label.setIcon(self.image_icon)
        except:
          #ex = sys.exc_info()[1]
          #print "Oh!! ha petado", str(ex)
          self.label.setIcon(None)
      else:
        self.label.setIcon(None)

    
class ImageFileView(FileView):
  def __init__(self):
    FileView.__init__(self)
    self.folder_icon = load_icon((__file__,"images","folder-32x32.png"))
    self.image_icon = load_icon((__file__,"images","image-32x32.png"))

  def getName(self,f):
    return FilenameUtils.getBaseName(f.getName())

  def getTypeDescription(self, f):
    if f.isDirectory():
      return "Folder"
    fname = f.getName().lower()
    if FilenameUtils.isExtension(fname, ("jpeg","jpg")):
      return "A JPEG Compressed Image File"
    if FilenameUtils.isExtension(fname,"png"):
      return "A PNG Image File"
    return None

  def getIcon(self, f):
    if f.isDirectory():
      return self.folder_icon
    fname = f.getName().lower()
    if FilenameUtils.isExtension(fname, ("png","jpeg","jpg")):
      try:
        img = ImageIO.read(f)
        w = img.getWidth()
        h = img.getHeight()
        if w<1500 and h<1500 :
          img = scaleImage(img, 32,32)
          return ImageIcon(img)
        else:
          return self.image_icon
      except:
        ex = sys.exc_info()[1]
        print "Oh!! ha petado", str(ex)
        self.image = None
    return None
    
def select_image(folder=None):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer == None:
      return 
    
    jfc = JFileChooser()
    
    preview = ImagePreviewPanel()
    jfc.setAccessory(preview)
    jfc.addPropertyChangeListener(preview)

    if folder == None:
      pass
    elif isinstance(folder,File):
      jfc.setSelectedFile(folder)
    else:
      jfc.setSelectedFile(File(str(folder)))
      
    jfc.setDialogType(JFileChooser.OPEN_DIALOG)
    jfc.setMultiSelectionEnabled(False)
    jfc.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES)
    jfc.setFileView(ImageFileView())
    jfc.setFileFilter(ImageFileFilter())
    jfc.setPreferredSize(Dimension(750,500))
    if jfc.showOpenDialog(composer.asJComponent()) != JFileChooser.APPROVE_OPTION:
        return None
    f = jfc.getSelectedFile()
    return f.getAbsolutePath()
    


def test():
  print repr(select_image(None))
  
def main():
  #selfRegister()
  test()
  