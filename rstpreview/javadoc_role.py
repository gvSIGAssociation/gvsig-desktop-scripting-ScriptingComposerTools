

import os
import sys
import re
from docutils import nodes, utils
from docutils.parsers.rst import roles

from javadoc_index import javadoc_index

def iteritems(d, **kw):
  """Return an iterator over the (key, value) pairs of a dictionary."""
  return iter(getattr(d, 'iteritems')(**kw))

def load_index_from_javadocs(path_to_the_javadocs):
  index = dict()
  doc_path_web = "html"

  for (path, ficheros, archvs) in os.walk(path_to_the_javadocs):
    for a in archvs:
      if not a.endswith(".html"):
          continue
      #key
      javaclass_key = os.path.splitext(a)[0]
      if "package" in javaclass_key:
          continue
      if javaclass_key in index.keys():
          continue

      #value
      full_path = os.path.join(path, a)
      rel_path = os.path.relpath(full_path, path_to_the_javadocs)
      docs_path = os.path.join(doc_path_web, rel_path)
      index[javaclass_key] = docs_path

    return index

explicit_title_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)

def split_explicit_title(text):
    """Split role content into title and target, if given."""
    match = explicit_title_re.match(text)
    if match:
        return True, match.group(1), match.group(2)
    return False, text, text

def make_javadoc_role(base_url, title_prefix=None):
    def role(typ, rawtext, text, lineno, inliner, options={}, content=[], **args):
        text = utils.unescape(text)
        has_explicit_title, title, part = split_explicit_title(text)
        jlink = javadoc_index.get(part,"") #link in local
        full_url = os.path.join(base_url, jlink) #link in web
        if not has_explicit_title:
            if prefix is None:
                title = full_url
            else:
                title = prefix + part
        pnode = nodes.reference(title, title, internal=False, refuri=full_url)
        return [pnode], []
    return role


def selfRegister():
  BASE_URL="http://downloads.gvsig.org/download/gvsig-desktop-testing/dists/2.3.0/javadocs/"
  roles.register_canonical_role("javadoc", make_javadoc_role(BASE_URL))

def main():
  if len(sys.args)!= 1:
    print "usage: %s <path to the javadocs>" % sys.args[0]
    print "   Create the javadoc_index.py from the javadocs locateds as the argument"
    sys.exit(1)

  path_to_the_javadocs = sys.args[1]
  index = load_index_from_javadocs(path_to_the_javadocs)
  f=open("javadoc_index.py","w")
  f.write("\n\n\njavadoc_index = {\n\n")
  for k,v in index.iteritems():
    f.write("  %r : %r,\n" % (k,v))
  f.write("\n\n}\n")
  f.close()


if __name__ == "__main__" :
  main()


