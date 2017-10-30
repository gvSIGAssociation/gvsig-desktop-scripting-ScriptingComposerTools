# encoding: utf-8

import gvsig
import gvsig.libs.formpanel
reload(gvsig.libs.formpanel)
from gvsig.libs.formpanel import FormPanel, getResource, load_icon
from gvsig.uselib import use_jars

from time import sleep

from org.gvsig.tools.swing.api import Component 

from java.lang import Throwable

import java.lang.Runnable
from java.awt import BorderLayout
from javax.swing import JEditorPane
from javax.swing import JScrollPane
from javax.swing.event import HyperlinkEvent
from javax.swing.event import HyperlinkListener

from org.gvsig.scripting.swing.api import ScriptingSwingLocator




class DefaultHyperlinkHandler(HyperlinkListener):
  def __init__(self, browser):
    self.__browser = browser

  def hyperlinkUpdate(self, hyperlinkEvent):
    if hyperlinkEvent.getEventType() == HyperlinkEvent.EventType.ACTIVATED :
      self.__browser.setPage(str(hyperlinkEvent.getURL()))

class BrowserPanel(FormPanel,Component):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"browserpanel.xml"))
    self.__browser = None
    self.initComponents()

  def __initCSSBox(self):
    from org.fit.cssbox.swingbox import BrowserPane
    from org.fit.cssbox.swingbox.util import DefaultHyperlinkHandler
    self.__browser = BrowserPane()
    self.__browser.addHyperlinkListener(DefaultHyperlinkHandler())
    self.containerBrowser.add(JScrollPane(self.__browser),BorderLayout.CENTER)

  def __initJEditorPane(self):
    self.__browser = JEditorPane()
    self.__browser.setEditable(False)
    self.__browser.addHyperlinkListener(DefaultHyperlinkHandler(self))
    self.containerBrowser.add(JScrollPane(self.__browser),BorderLayout.CENTER)

  def __initJFXBrowser(self):
    from javafx.embed.swing import JFXPanel
    import javafx.beans.value.ChangeListener
    import javafx.event.EventHandler
    
    
    class Runnable(java.lang.Runnable):
      def __init__(self,fn, *args):
        self.__fn = fn
        self.__args = args
    
      def run(self):
        self.__fn(*self.__args)
    
      def __call__(self):
        self.__fn(*self.__args)
        
    class MyEventHandler(javafx.event.EventHandler):
      def __init__(self, jfxbrowser):
        self.jfxbrowser = jfxbrowser

      def handle(self,event):
        #print "handle: ", repr(event.getEventType()), repr(event.getData())
        if event.getEventType() == event.STATUS_CHANGED:
          s = event.getData()
          if s==None:
            self.jfxbrowser.status.setText("")
          else:
            self.jfxbrowser.status.setText(s)
        
    class MyChangeListener(javafx.beans.value.ChangeListener):
      def __init__(self, jfxbrowser):
        self.jfxbrowser = jfxbrowser

      def changed(self, ov, oldState, newState):
        if newState == newState.SUCCEEDED:
          self.jfxbrowser.location.setText(self.jfxbrowser.engine.getLocation())
          
    class JFXBrowser(JFXPanel):
      def __init__(self, status, location):
        from javafx.application import Platform
        self.status = status
        self.location = location
        self.view = None
        self.engine = None
        self.scene = None
        self.__runLater = Platform.runLater

        self.__runLater(Runnable(self.__createScene))
        Platform.setImplicitExit(False)
        #sleep(1)

      def __createScene(self):
        from javafx.scene.web import WebView
        from javafx.scene import Scene
    
        self.view = WebView()
        self.engine = self.view.getEngine()
        self.engine.setOnStatusChanged(MyEventHandler(self))
        self.engine.getLoadWorker().stateProperty().addListener(MyChangeListener(self))
        self.engine.setJavaScriptEnabled(True)
        self.scene = Scene(self.view)
        self.setScene(self.scene)

      def __load(self, url):
        #print url.__class__.__name__, repr(str(url))   
        self.engine.load(str(url))
        self.revalidate()

      def __loadContent(self, content, contentType="text/html"):
        self.engine.loadContent(str(content),contentType)
        self.revalidate()
      
      def __goHistory(self, index):
        self.engine.getHistory().go(index)

      def call(self,method, *args):
        self.__runLater(Runnable(method,*args))
        
      def setPage(self,url):
        self.call(self.__load,url)
        
      def setContent(self,content, contentType="text/html"):
        self.call(self.__loadContent,content, contentType)
        
      def getPage(self):
        return self.engine.getLocation()

      def goPrevious(self):
        self.call(self.__goHistory,-1)

      def goNext(self):
        self.call(self.__goHistory,1)

      def getTitle(self):
        return self.engine.getTitle()

      def __executeScript(self, js):
        return self.engine.executeScript(js);

      def __find(self,text, backwards=False):
        #if text in (None,""):
        #  self.engine.executeScript('window.stopFinding()');
        #else:
        self.engine.executeScript('window.find("%s",false,%s,true)' % (text,str(backwards).lower()));
        
      def find(self,text, backwards=False):
        try:
          self.call(self.__find,text,backwards);
        except Throwable, ex:
          print "find, a petao", ex
        
    self.__browser = JFXBrowser(self.lblStatus, self.txtURL)
    self.containerBrowser.add(self.__browser,BorderLayout.CENTER)
    
  def initComponents(self):
    self.containerBrowser.setLayout(BorderLayout())

    try:
      self.__initJFXBrowser()
    except:
      try:
        print "try to use CSSBox as WebBrowser"
        self.__initCSSBox()
      except:
        print "Using JEditorPane as WebBrowser"
        self.__initJEditorPane()

    self.btnPrevious.setIcon(load_icon(getResource(__file__,"images","arrow_left.png")))
    self.btnNext.setIcon(load_icon(getResource(__file__,"images","arrow_right.png")))
    self.btnRefresh.setIcon(load_icon(getResource(__file__,"images","arrow_refresh.png")))
    self.btnConfig.setIcon(load_icon(getResource(__file__,"images","add.png")))
    self.btnSearchPrevious.setIcon(load_icon(getResource(__file__,"images","arrow_up.png")))
    self.btnSearchNext.setIcon(load_icon(getResource(__file__,"images","arrow_down.png")))
    self.imgSearch.setIcon(load_icon(getResource(__file__,"images","search.png")))
    self.setPreferredSize(600,500)

  def txtURL_keyPressed(self,keyEvent):
    if keyEvent.getKeyChar() == "\n":
      self.setPage(self.txtURL.getText())

  def btnSearchPrevious_click(self,*args):
    jtext = self.txtSearch
    self.__browser.find(jtext.getText(),True)

  def btnSearchNext_click(self,*args):
    jtext = self.txtSearch
    self.__browser.find(jtext.getText())

  def txtSearch_keyPressed(self,event):
    jtext = self.txtSearch
    if event.getKeyChar() == "\x1b" : # ESC
      jtext.setText("")
      self.__browser.find("")
      return
    if event.getKeyChar() == "\n" :
      self.__browser.find(jtext.getText())
      return
       
  def setPage(self,url):
    self.txtURL.setText(str(url))
    self.__browser.setPage(url)

  def getPage(self):
    return self.__browser.getPage()

  def setContent(self,content, contentType="text/html"):
    return self.__browser.setContent(content, contentType)
    
  def btnPrevious_click(self,*args):
    self.__browser.goPrevious()

  def btnNext_click(self,*args):
    self.__browser.goNext()

  def getTitle(self):
    return self.__browser.getTitle()
    
  def showWindow(self,title="Browser",scriptEditor=True):
    if scriptEditor:
      windowManager = ScriptingSwingLocator.getUIManager()
      windowManager.showWindow(self.asJComponent(),title)
    else:
      FormPanel.showWindow(self,title)
      
def main(*args):
  browser = BrowserPanel()
  browser.showWindow("Browser", scriptEditor=False)
  url = "jar:file:" + getResource(__file__, "..","data","gvsig-2_3_0-javadocs.zip!/html/overview-summary.html")
  url = "jar:file:" + getResource(__file__, "..", "data","scripting-developers-guide.zip!/html/index.html")
  url = "http://downloads.gvsig.org/download/web/es/build/html/gvsigsearch_all.html"
  browser.setPage(url)
  