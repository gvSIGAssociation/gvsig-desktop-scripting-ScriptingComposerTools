# encoding: utf-8

from gvsig import *

from StringIO import StringIO
import copy
from os.path import basename

TYPE_ROOT = "root"
TYPE_FOLDER = "folder"
TYPE_MODULE = "module"
TYPE_CLASS = "class"
TYPE_METHOD = "method"
TYPE_FUNCTION = "function"
TYPE_TEXT = "text"
TYPE_IMPORT = "import"

MODE_TEXT=TYPE_TEXT
MODE_IDENTIFIER="identifier"
MODE_CLASS=TYPE_CLASS
MODE_METHOD=TYPE_METHOD
MODE_FUNCTION=TYPE_FUNCTION

class CodeElement(object):
  def __init__(self,type, name, indent, lineno,fname=None):
    self.name = name
    self.indent = indent
    self.type = type
    self.lineno = lineno
    self.elements = list()
    self.fname = fname

  def __deepcopy__(self,memo):
    theCopy = CodeElement(self.type, self.name, self.indent, self.lineno)
    theCopy.elements = copy.deepcopy(self.elements, memo)
    return theCopy
    
  def __repr__(self):
    return self.name

  def addChild(self, element):
    self.elements.append(element)
    
  def getChildren(self):
    return self.elements

  def has_children(self):
    return len(self.elements)>0

  def setName(self,name):
    self.name = name

  def getName(self):
    return self.name
    
  def removeAll(self):
    self.elements = list()
  
  def retainElements(self, search,element=None):
    if element == None:
      element = self
    toremove =list()
    search = search.lower()
    for child in element.elements:
      self.retainElements(search,child)
      if not search in child.name.lower():
         if len(child.elements)==0 :
           toremove.append(child)
    for x in toremove:
      element.elements.remove(x)    
    
class CodeAnalyzer(object):

  def __init__(self):
    self.module = CodeElement(TYPE_MODULE,"<unknown>",0,0)
    
  def getModule(self):
    return self.module
    
  def getIdentifier(self,line, pos):
    s = line[pos:].strip()
    pos = 0
    l = len(s)
    while pos<l:
      c = s[pos:pos+1]
      if not (c == "_" or c.isalnum()):
        break
      pos += 1
    return s[:pos]
      
  def load(self,fname,  search=None, inputFile=None, mode=MODE_TEXT):
    name = basename(fname)
    self.module = CodeElement(TYPE_MODULE,name,0,0,fname=fname)
    if inputFile == None:
      f = open(fname,"r")
    else:
      f = inputFile
    state = "code"
    lineno = 0
    for line in f:
      line_len = len(line)      
      pos = 0
      while pos<line_len:
        c = line[pos:pos+1]
        if c!=" ":
          indent = pos
          break
        pos += 1

      if state == "code" and search != None :
        if mode == MODE_TEXT:
          if search.lower() in self.getIdentifiers(line).lower():  
            last = self.getLastElement()
            element = CodeElement(TYPE_TEXT,"%5d: %s" % (lineno,line[pos:-1]),indent, lineno,fname=fname)
            last.elements.append(element)
        elif mode == MODE_IDENTIFIER:
          identifiers = self.getIdentifiers(line).split(" ")
          for identifier in identifiers:
            if search == identifier:
              last = self.getLastElement()
              element = CodeElement(TYPE_TEXT,"%5d: %s" % (lineno,line[pos:-1]),indent, lineno,fname=fname)
              last.elements.append(element)
              break
              
      while pos<line_len :
        if state == "triplequote":
          if line[pos:pos+3] == '"""' :
            pos +=3
            state = "code"
          else:
            pos += 1
        elif state == "code":
          if line[pos:pos+3] == '"""' :
            pos += 1
            state = "triplequote"
  
          else:
            if pos==indent and line[pos:pos+4] == 'def ':
              element = CodeElement(TYPE_FUNCTION,self.getIdentifier(line,pos+4),indent, lineno,fname=fname)
              pos += 4 + len(element.name)
              if len(self.module.elements) == 0:
                self.module.elements.append(element)
              else:
                last = self.module.elements[-1]
                if last.type == TYPE_FUNCTION:
                  if indent > last.indent:
                    last.elements.append(element)
                  else:
                    self.module.elements.append(element)
                elif last.type == TYPE_CLASS:
                  if indent > last.indent:
                    element.type = TYPE_METHOD
                    last.elements.append(element)
                  else:
                    self.module.elements.append(element)
    
            elif pos==indent and line[pos:pos+6] == 'class ':
              element = CodeElement(TYPE_CLASS, self.getIdentifier(line,pos+6), indent, lineno,fname=fname)
              pos += 6 + len(element.name)
              self.module.elements.append(element)
    
            elif pos==indent and line[pos:pos+5] == 'from ':
              element = CodeElement(TYPE_TEXT,"%5d: %s" % (lineno,line[pos:-1]),indent, lineno,fname=fname)
              pos += 6
              if len(self.module.elements) == 0:
                import_element = CodeElement(TYPE_IMPORT, "import", indent, lineno,fname=fname)
                self.module.elements.append(import_element)
              else:
                last = self.module.elements[-1]
                if last.type == TYPE_IMPORT:
                  import_element = last
                else:
                  import_element = CodeElement(TYPE_IMPORT, "import", indent, lineno,fname=fname)
                  self.module.elements.append(import_element)
              import_element.elements.append(element)
    
            elif pos==indent and line[pos:pos+7] == 'import ':
              element = CodeElement(TYPE_TEXT,"%5d: %s" % (lineno,line[pos:-1]),indent, lineno,fname=fname)
              pos += 6
              if len(self.module.elements) == 0:
                import_element = CodeElement(TYPE_IMPORT, "import", indent, lineno,fname=fname)
                self.module.elements.append(import_element)
              else:
                last = self.module.elements[-1]
                if last.type == TYPE_IMPORT:
                  import_element = last
                else:
                  import_element = CodeElement(TYPE_IMPORT, "import", indent, lineno,fname=fname)
                  self.module.elements.append(import_element)
              import_element.elements.append(element)
    
            else:
              pos += 1
        pass
      lineno += 1
      
    if inputFile == None:
      f.close()

  def getLastElement(self):
    if len(self.module.elements) == 0:
      return self.module
    last = self.module.elements[-1]
    if len(last.elements)>0:
      last = last.elements[-1]
    return last
    
  def filter(self, search, element=None, mode=MODE_TEXT):
    if element == None:
      element = self.module
    toremove =list()
    for child in element.elements:
      if child.type==mode:
        if child.getName() == search:
          child.removeAll()
        else:
          toremove.append(child)
      else:
        self.filter(search, element=child, mode=mode)
        
    for x in toremove:
      element.elements.remove(x)    
    
  def removeEmptyElemens(self, element=None):
    if element == None:
      element = self.module
    toremove =list()
    for child in element.elements:
      self.removeEmptyElemens(child)
      if len(child.elements)==0 and child.type!=TYPE_TEXT:
        toremove.append(child)
    for x in toremove:
      element.elements.remove(x)    

  def getIdentifiers(self, line):
    out = StringIO()
    STATE_TEXT = 0
    STATE_IDENTIFIER = 1
    STATE_STRING_SINGLE_QUOTE = 2
    STATE_STRING_DOUBLE_QUOTE = 3
    STATE_STRING_TRIPLE_QUOTE = 4
    
    line_len = len(line)
    pos = 0
    state = STATE_TEXT
    while pos<line_len:
      c = line[pos:pos+1]
      if state == STATE_IDENTIFIER:
        if c.isalnum() or c == "_":
          out.write(c)
        else:
          out.write(" ")
          state = STATE_TEXT
      
      if state == STATE_STRING_TRIPLE_QUOTE:
        if line[pos:pos+3] == '"""' :
          state = STATE_TEXT
          
      elif state == STATE_STRING_DOUBLE_QUOTE:
        if c == '"' :
          state = STATE_TEXT
          
      elif state == STATE_STRING_SINGLE_QUOTE:
        if c == "'" :
          state = STATE_TEXT
          
      elif state==STATE_TEXT:
        if c.isalpha() or c == "_":
          out.write(c)
          state = STATE_IDENTIFIER
          
        elif line[pos:pos+3] == '"""' :
          state = STATE_STRING_TRIPLE_QUOTE
          pos += 2
          
        elif c == '"' :
          state = STATE_STRING_DOUBLE_QUOTE
          
        elif c == "'" :
          state = STATE_STRING_SINGLE_QUOTE
          
      pos += 1
    return out.getvalue()
    
  def dump(self):
    out = StringIO()

    out.write("%s %r\n" % (self.module.type,self.module.name))
    for element in self.module.elements:
      out.write("  %s %r [lineno=%s, indent=%s]\n" % (element.type,element.name, element.lineno, element.indent))
      if len(element.elements)!=0:
        for element2 in element.elements:
          out.write("    %s %r [lineno=%s, indent=%s]\n" % (element2.type,element2.name, element2.lineno, element2.indent))
          if len(element2.elements)!=0:
            for element3 in element2.elements:
              out.write("      %s %r [lineno=%s, indent=%s]\n" % (element3.type,element3.name, element3.lineno, element3.indent))
    return out.getvalue()

def test1():
  analyzer = CodeAnalyzer()
  analyzer.load(__file__,search="CodeElement")
  analyzer.removeEmptyElemens()
  print analyzer.dump()
  