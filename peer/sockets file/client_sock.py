#client_sock.py
import socket

HOST = 'localhost' #coloca o host do servidor
PORT = 57000

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect((HOST,PORT))

file = 'new_merge.pdf'

arq = open(file, 'rb')

s.send('tipo.pdf'.encode('utf-8'))

with open(file,'rb') as f:
	s.sendall(f.read())

arq.close()
s.close()