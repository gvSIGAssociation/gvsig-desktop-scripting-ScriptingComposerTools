# encoding: utf-8


import properties
import dbf
import html
import pdf
import png

def selfRegister():
  properties.selfRegister()
  dbf.selfRegister()
  html.selfRegister()
  pdf.selfRegister()
  png.selfRegister()
  