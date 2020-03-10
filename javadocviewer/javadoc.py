# encoding: utf-8

import gvsig
from gvsig.libs.formpanel import getResource
from gvsig import logger,LOGGER_WARN

import sys
import os
import re 
import urllib2
import fnmatch
import ConfigParser
import hashlib

from java.net import URL
from java.io import BufferedReader
from java.io import InputStreamReader
from  org.gvsig.scripting.swing.api import ScriptingSwingLocator, JScriptingComposer
from org.gvsig.scripting import ScriptingLocator

def getJavadocUserFolder(*subfolders):
  manager = ScriptingLocator.getManager()
  folder = os.path.join(manager.getDataFolder("ScriptingComposerTools").getAbsolutePath(),"javadoc",*subfolders)
  try:
    os.makedirs(folder)
  except:
    pass
  return folder
    
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

  def __contains(self, moduleOrPackage):
    for child in self.__children:
      if child.getName() == moduleOrPackage.getName():
        if child.__class__ == moduleOrPackage.__class__:
          return child, True
    return moduleOrPackage, False
    
  def addPackage(self, name):
    if isinstance(name,tuple) or isinstance(name,list):
      names = name
      name = names[0].strip()
      package = self.get(name)
      if not isinstance(package,Package):
        package = Package(self, name)
        package, contains = self.__contains(package)
        if not contains:
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
    module, contains = self.__contains(module)
    if not contains:
      self.__children.append(module)
      self.__children.sort(key=lambda module: module.getName())
    return module

class JavadocSet(object):
  def __init__(self, name, url, enabled=True):
    self.__name = name
    self.__url = url
    self.__enabled = enabled

  def getName(self):
    return self.__name

  def toString(self):
    return self.__name
  
  def __str__(self):
    return self.__name

  def __repr__(self):
    #return "JavadocSet('%s','%s',%s)" % (self.__name, self.__url, self.__enabled)
    return self.__name
    
  def isEnabled(self):
    return self.__enabled

  def setEnabled(self, enabled):
    self.__enabled = enabled
    
  def getURL(self):
    return self.__url

  def setName(self, name):
    self.__name = name

  def setURL(self, url):
    self.__url = url

  def save(self, pathname=None):
    if pathname == None:
      fname = self.__getValidFileName(self.getName())
      pathname = os.path.join(getJavadocUserFolder("sets"), fname)  
    config = ConfigParser.ConfigParser()
    config.add_section('javadocset')
    config.set("javadocset","name", self.__name)
    config.set("javadocset","url", self.__url)
    config.set("javadocset","enabled", str(self.__enabled).lower())
    with open(pathname, 'wb') as configfile:
      config.write(configfile)

  def remove(self, pathname=None):
    if pathname == None:
      fname = self.__getValidFileName(self.getName())
      pathname = os.path.join(getJavadocUserFolder("sets"), fname)  
    if os.path.exists(pathname):
      os.remove(pathname)
      
  def __getValidFileName(self, name):
    fname = [ c for c in name if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" ]
    fname =  "".join(fname) + "-" + hashlib.md5(name).hexdigest() + ".javadoc"
    return fname

    
class JavadocConfig(object):
  def __init__(self):
    self.__javadocSets = list()

  def contains(self, docset):
    for x in self.__javadocSets:
      if x.getName() == docset.getName():
        return True
    return False
    
  def getJavadocSets(self):
    return self.__javadocSets

  def add(self, javadocSet):
    for docset in self.__javadocSets:
      if docset.getURL() == javadocSet.getURL():
        docset.setName(javadocSet.getName())
        docset.setEnabled(javadocSet.isEnabled())
        return docset
      if docset.getName().lower() == javadocSet.getName().lower() :
        docset.setURL(javadocSet.getURL())
        docset.setEnabled(javadocSet.isEnabled())
        return docset
    self.__javadocSets.append(javadocSet)
    return javadocSet

     
class Javadoc(object):
  def __init__(self, config=None, javadocSet=None):
    if config == None:
      self.__config = JavadocConfig()
    else:
      self.__config = config
    self.__nodes = Package(None,"all")
    self.__packages = list()
    self.__modules = list()
    if javadocSet!=None:
      self.load(javadocSet)

  def clear(self):
    self.__nodes = Package(None,"all")
    self.__packages = list()
    self.__modules = list()
    self.__config = JavadocConfig()
    
  def getConfig(self):
    return self.__config
    
  def getNodes(self):
    return self.__nodes

  def getModules(self):
    return self.__modules

  def load(self, javadocSet):
    status = True
    if javadocSet.isEnabled():
      if isinstance(javadocSet.getURL(),URL):
        u1 = javadocSet.getUrl()
      else:
        u1 = URL(str(javadocSet.getURL()))
      lines = 0
      u2 = URL(u1.toExternalForm()+"/allclasses-frame.html")
      logger("Loading javadoc set %s (%s)..." % (javadocSet.getName(),u1.toExternalForm()))
      try:
        allClassesFrame = u2.openConnection().getInputStream()
        allClassesFrameReader = BufferedReader(InputStreamReader(allClassesFrame))
        line = allClassesFrameReader.readLine()
      except Exception,ex:
        logger("Can't load (1) Javadoc '%s' from '%s'" % (javadocSet.getName(),u1.toExternalForm()),LOGGER_WARN,ex)
        return False
      except:
        ex = sys.exc_info()[1]
        logger("Can't load (2) Javadoc '%s' from '%s'" % (javadocSet.getName(),u1.toExternalForm()),LOGGER_WARN,ex)
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
            #print repr(packageName), repr(module)
            n+=1
        line = allClassesFrameReader.readLine()
        lines+=1
      
      allClassesFrameReader.close()
      allClassesFrame.close()
      if lines < 1:
        status = False
    
    self.__config.add(javadocSet)
    return status

  def loadJavadocSets(self):
    for docset in self.getJavadocSets():
      self.load(docset)

  def getJavadocSets(self):
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
        "Java Platform SE 8",
        "https://docs.oracle.com/javase/8/docs/api"
      )
    )
    folder = getJavadocUserFolder("sets")
    files = [os.path.join(folder,f) for f in os.listdir(folder) if fnmatch.fnmatch(f, "*.javadoc")]
    folder = getResource(__file__, "data", "javadocsets")
    files.extend([os.path.join(folder,f) for f in os.listdir(folder) if fnmatch.fnmatch(f, "*.javadoc")])
    for f in files:
      configfile = ConfigParser.ConfigParser()
      #print "javadoc: ", f
      configfile.read(f)
      set = JavadocSet(
        configfile.get("javadocset","name"),
        configfile.get("javadocset","url"),
        configfile.getboolean("javadocset","enabled")
      )
      alreadyLoaded = False
      for x in docsets:
        if x.getName() == set.getName():
          alreadyLoaded = True
          break
      if not alreadyLoaded:
        docsets.append(set)
    docsets.sort(cmp=lambda x,y: cmp(x.getName(),y.getName()))
    return docsets

  
def main(*args):
  url = "jar:file:" + getResource(__file__, "data","gvsig-2_4_0-javadocs.zip!/html")
  javadoc = Javadoc(javadocSet=JavadocSet("gvSIG 2.4.0", url))
  print javadoc.getNodes().hasChildren()
