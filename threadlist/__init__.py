# encoding: utf-8

import gvsig

try:
  from threadlist import selfRegister
except:
  import sys
  ex = sys.exc_info()[1]
  gvsig.logger("Can't load module 'threadlist'. " + str(ex), gvsig.LOGGER_WARN, ex)
  del ex
  del sys
  
  def selfRegister():
    pass

