
import gvsig
from gvsig import getResource

from docutils.core import publish_string
import os
import urlparse
import StringIO
import re

import javadoc_role

def fixurls(rest,prefix):
  def is_relative(url):
    return not bool(urlparse.urlparse(url).netloc)

  searchs=(
    "[ \\t]*[.][.][ \\t]*image::[ \\t]*(.*)", # .. image:: file1.png
    "[ \\t]*[.][.][ \\t]*[|][a-zA-Z0-9_-]*[|][ \\t]*image::[ \\t]*(.*)", # .. |xxx| image:: file1.png
    "[ \\t]*[.][.][ \\t]*figure::[ \\t]*(.*)", # .. figure:: file1.png
    "[ \\t]*[.][.][ \\t]*include::[ \\t]*(.*)", # .. include:: file1.png
    "[ \\t]*[.][.][ \\t]*_[^:]*:[ \\t]*(.*)", # .. _Python home page: file
    "`[^<]*<([^>]*)>`_" # See the `Python home page <file>`_ for info.
  )

  for search in searchs:
    out = StringIO.StringIO()
    last=0
    for x in re.finditer(search,rest):
      url = x.group(1)
      start = x.start(1)
      end = x.end(1)
      #print "url='%s', relative=%s, start=%s, end=%s" % (url,is_relative(url),start,end)
      if is_relative(url):
        out.write(rest[last:start])
        out.write(prefix)
        out.write(url)
        last=end
    out.write(rest[last:])
    rest=out.getvalue()
  return rest  

def toHtml(markuptext, pathname, **kwargs):
  markuptext = fixurls(markuptext,os.path.dirname(pathname)+"/")
  html = publish_string( source=markuptext, source_path=os.path.basename(pathname), writer_name="html" )
  return html

def selfRegister():
  javadoc_role.selfRegister()

def main():
  pass
  