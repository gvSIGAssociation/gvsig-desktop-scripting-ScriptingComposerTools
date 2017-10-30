# encoding: utf-8

import gvsig

from gvsig.libs.formpanel import FormPanel

class JavadocSetPanel(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,(__file__,"javadocsetpanel.xml"))
    self.setPreferredSize(300,150)
    
  def getName(self):
    return self.txtName.getText().strip()
    
  def getURL(self):
    return self.txtURL.getText().strip()
    
def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
