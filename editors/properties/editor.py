# encoding: utf-8

import gvsig
from gvsig import logger, LOGGER_WARN

from StringIO import StringIO

from org.gvsig.scripting.swing.impl.composer.editors import TextEditor

from java.util import Properties
from java.io import FileOutputStream
from java.io import FileInputStream

class PropertiesEditor(TextEditor):
  def __init__(self, unit):
    TextEditor.__init__(self, unit)

  def set(self, unit):
    self.setUnit(unit)
    self.getPropertiesPanel().set(unit)
    props = Properties()
    f = self.getUnit().getExternalFile()
    fis = FileInputStream(f)
    props.load(fis)
    fis.close()
    text = StringIO()
    names = list()
    names.extend(props.stringPropertyNames())
    names.sort()
    for name in names:
      value = props.getProperty(name)
      text.write("%s=%s\n" % (name, value))
    self.getTextEditor().setText(unit.getMimeType(),text.getvalue())
        
  def save(self):
    text = self.getTextEditor().getText()
    lines = text.split("\n")
    props = Properties()
    comments = ""
    for line in lines:
      line = line.strip()
      if line.startswith("#"):
        comments += line[1:] + " "
      else:
        if "=" in line:
          parts = line.split("=")
          props.setProperty(parts[0].strip(), parts[1].strip())
  
    f = self.getUnit().getExternalFile()
    fout=None
    try:
      fout = FileOutputStream(f)
      props.store(fout,comments)
    finally:
      if fout!=None:
        fout.close()
    self.setModified(False)
    