# encoding: utf-8


import properties.editorfactory
import dbf.editorfactory
import html.editorfactory
import pdf.editorfactory

def selfRegister():
  properties.editorfactory.selfRegister()
  dbf.editorfactory.selfRegister()
  html.editorfactory.selfRegister()
  pdf.editorfactory.selfRegister()
  