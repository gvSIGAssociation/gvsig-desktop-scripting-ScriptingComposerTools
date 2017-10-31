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
  ex = sys.exc_info()[1]
  gvsig.logger("Can't load module 'lint'. " + str(ex), gvsig.LOGGER_WARN, ex)
  del ex
  del sys
  
  def selfRegister():
    pass

