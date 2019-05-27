import time, _thread as thread
from socket import *

def devolve(ip, word):
	'''
	Esta pequena thread é responsável pela devolução da resposta convincente para o peer que
	solicitou a palavra.
	Transita o significado da palavra.
	'''
	print(word)
	serverHost = ip
	serverPort = 5000

	sockobj = socket(AF_INET, SOCK_STREAM)
	sockobj.connect((serverHost, serverPort))
	word = "r^"+word
	sockobj.send(word.encode())

	data = sockobj.recv(1024)
	sockobj.close()
