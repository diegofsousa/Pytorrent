from PyQt4.QtCore import *
from PyQt4.QtGui import *
from socket import *
import time, _thread as thread
from response import devolve
import time, sys


class TLL(QThread):
	'''
	Esta thread é responsável apenas pela criação de um contador regressivo para o TTL.
	'''
	def __init__ (self):
		QThread.__init__(self)

	def run(self):
		for i in range(0,5):
			self.decr()
			time.sleep(1)
		self.emit(SIGNAL("timeover()"))

	def decr(self):
		self.emit(SIGNAL("timeo()"))