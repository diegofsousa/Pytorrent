#serv_sock.py

import socket
import json
import base64

HOST = ''
PORT = 57002

MAX = 1000000000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

while True:
	c, addr = s.accept()     

	file = c.recv(MAX)     #get file name first from client
	print(file)
	j = json.loads(file.decode())

	print(file)
	#opening file first

	f = open('mas.pdf','wb')      #open that file or create one
	#l = c.recv(1024)         #get input

	f.write(base64.decodebytes(j['content'].encode()))


	f.close()

c.send('Thank you for connecting')
c.close()