# encoding: utf-8


import properties
import dbf
import html
import pdf

def selfRegister():
  properties.selfRegister()
  dbf.selfRegister()
  html.selfRegister()
  pdf.selfRegister()
  