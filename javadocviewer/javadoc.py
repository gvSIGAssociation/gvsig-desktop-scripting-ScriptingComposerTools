# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import getResource
from gvsig import logger,LOGGER_WARN

import re 
import urllib2

from java.net import URL
from java.io import BufferedReader
from java.io import InputStreamReader
from  org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer

class Module(object):
  def __init__(self, parent, name, url, packageName=None):
    self.__parent = parent
    self.__name = name
    self.__url = url
    self.__packageName = packageName

  def getParent(self):
    return self.__parent
    
  def getName(self):
    return self.__name

  def __repr__(self):
    return "%s  (%s)" % (self.__name, self.__packageName)

  __str__ = getName

  def getPackageName(self):
    return self.__packageName
    
  def getUrl(self):
    return self.__url
    
  def hasChildren(self):
    return False
        
class Package(object):
  def __init__(self, parent, name):
    self.__parent = parent
    self.__name = name
    self.__children = list()

  def getParent(self):
    return self.__parent

  def getName(self):
    return self.__name

  __repr__ = getName
  __str__ = getName
  
  def getChildren(self):
    return self.__children

  def hasChildren(self):
    return len(self.__children)>0

  def __len__(self):
    return len(self.__children)

  def __getitem__(self, index):
    return self.get(index)
    
  def get(self,name):
    try:
      n = int(name)
      return self.__children[n]
    except ValueError:
      pass
    for package in self.__children:
      if package.getName() == name:
        return package
    return None

  def addPackage(self, name):
    if isinstance(name,tuple) or isinstance(name,list):
      names = name
      name = names[0].strip()
      package = self.get(name)
      if not isinstance(package,Package):
        package = Package(self, name)
        self.__children.append(package)
        self.__children.sort(key=lambda module: module.getName())
      if len(names)>1:
        return package.addPackage(names[1:])
      return package   
    names = str(name).replace(".","/").split("/")
    return self.addPackage(names)

  def addModule(self,name, url, packageName=None):
    if "." in name or "/" in name:
      names = str(name).replace(".","/").split("/")
      package = self.addPackage(names[:-1])
      if names[-1] == "":
        return None
      return package.addModule(names[-1], url, packageName)
    module = Module(self, name, url, packageName)
    self.__children.append(module)
    self.__children.sort(key=lambda module: module.getName())
    return module

class JavadocSet(object):
  def __init__(self, name, url):
    self.__name = name
    self.__url = url

  def getName(self):
    return self.__name

  __repr__ = getName
  __str__ = getName
  
  def getURL(self):
    return self.__url

  def setName(self, name):
    self.__name = name

  def setURL(self, url):
    self.__url = url
    
class JavadocConfig(object):
  def __init__(self):
    self.__javadocSets = list()

  def getJavadocSets(self):
    return self.__javadocSets

  def add(self, name, url):
    if url in ("",None):
      return
    if not isinstance(url,URL):
      url = URL(str(url))
    for docset in self.__javadocSets:
      if docset.getURL() == url:
        docset.setName(name)
        return docset
      if name!=None and docset.getName().lower() == name.lower() :
        docset.setURL(url)
        return docset
    if name in ("",None):
      name = "Javadoc %02d" % len(self.__javadocSets)
    docset = JavadocSet(name,url)
    self.__javadocSets.append(docset)
    return docset

     
class Javadoc(object):
  def __init__(self, config=None, url=None, name=None):
    if config == None:
      self.__config = JavadocConfig()
    else:
      self.__config = config
    self.__nodes = Package(None,"all")
    self.__packages = list()
    self.__modules = list()
    for docset in self.__config.getJavadocSets():
      self.load(docset.getUrl(), docset.getName())
      
    if url!=None:
      self.load(url,name)

  def getConfig(self):
    return self.__config
    
  def getNodes(self):
    return self.__nodes

  def getModules(self):
    return self.__modules

  def load(self, url, docsetname=None):
    composer = ScriptingSwingLocator.getUIManager().getActiveComposer()
    if composer != None:
      composer.getStatusbar().message("Javadocs: loading javadocset...")
    try:
      if isinstance(url,URL):
        u1 = url
      else:
        u1 = URL(str(url))
      lines = 0
      u2 = URL(u1.toExternalForm()+"/allclasses-frame.html")
      try:
        allClassesFrame = u2.openConnection().getInputStream()
        allClassesFrameReader = BufferedReader(InputStreamReader(allClassesFrame))
        line = allClassesFrameReader.readLine()
      except Exception,ex:
        logger("Can't load Javadoc '%s' from '%s'" % (docsetname,u1.toExternalForm()),LOGGER_WARN,ex)
        return False
      pattern = re.compile('.*href="([^"]*)".*[>]([^<]*)[<][/]a[>].*',re.IGNORECASE)
      n = 0
      while line != None:    
        line = line.replace("<i>","").replace("</i>","")
        line = line.replace('<span class="interfaceName">',"").replace('</span>',"")
        
        match = pattern.match(line)
        if match != None:
          name = match.group(2)
          path = "/".join(match.group(1).split("/")[:-1])
          pathname = "/".join((path,name))
          url = URL(u1.toExternalForm()+"/"+match.group(1))
          packageName = str(path.replace("/",".")) 
          module = self.__nodes.addModule(pathname,url, packageName)
          self.__modules.append(module)
          if n<10 :
            print repr(packageName), repr(module)
            n+=1
        line = allClassesFrameReader.readLine()
        lines+=1
      self.__config.add(docsetname,u1)
      allClassesFrameReader.close()
      allClassesFrame.close()
      if lines < 1:
        return False
      return True
    finally:
      if composer != None:
        composer.getStatusbar().message("")

  def loadDefaultJavadocSets(self):
    for docset in self.getDefaultJavadocSets():
      self.load(docset.getURL(),docset.getName())

  def getDefaultJavadocSets(self):
    docsets = list()
    
    # Hay un bug en el component WebView de java que hace que no se carguen correctamente
    # los recursos asociados a una pagina web (css,js,png...) cuando la pagina esta en un 
    # jar/zip.
    # Para rodearlo, intentaremos cargar la documentacion de la web si hay conexion a internet
    # y si no, usaremos la copia local zipeada
    try:
      x = urllib2.urlopen("http://downloads.gvsig.org/download/gvsig-desktop-testing/dists/2.4.0/docs/javadocs/html/allclasses-frame.html",timeout=3)
      x.close()
      docsets.append( 
        JavadocSet(
          "gvSIG 2.4.0 (online)",
          "http://downloads.gvsig.org/download/gvsig-desktop-testing/dists/2.4.0/docs/javadocs/html"
        )
      )
    except:
      docsets.append( 
        JavadocSet(
          "gvSIG 2.4.0 (local)",
          "jar:file:" + getResource(__file__, "data","gvsig-2_4_0-javadocs.zip!/html")
        )
      )
    docsets.append( 
      JavadocSet(
        "Java Platform SE 8 (online)",
        "https://docs.oracle.com/javase/8/docs/api"
      )
    )
    docsets.append( 
      JavadocSet(
        "JavaFX 8 (online)",
        "http://docs.oracle.com/javase/8/javafx/api"
      )
    )
    docsets.append( 
      JavadocSet(
        "Apache Commons IO 2.5 API (online)",
        "http://commons.apache.org/proper/commons-io/javadocs/api-release"
      )
    )

    return docsets

  
def main(*args):
  url = "jar:file:" + getResource(__file__, "data","gvsig-2_4_0-javadocs.zip!/html")
  javadoc = Javadoc(url=url,name="gvSIG 2.4.0")
  print javadoc.getNodes().hasChildren()
