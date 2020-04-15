# encoding: utf-8

import gvsig

try:
  import lint
  import continuoslint
  
  def selfRegister():
    lint.selfRegister()
    continuoslint.selfRegister()
except:
  import sys
  import traceback
  ex = sys.exc_info()
  gvsig.logger("Can't load module 'lint'. %s\n%s" % (ex[1], "".join(traceback.format_exception(*ex))), gvsig.LOGGER_WARN)
  del ex
  del sys
  del traceback
  
  def selfRegister():
    pass

