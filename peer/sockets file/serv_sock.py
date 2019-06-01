#serv_sock.py

import socket

HOST = ''
PORT = 57000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

while True:
	c, addr = s.accept()     

	file = c.recv(1024)     #get file name first from client
	#opening file first

	f = open(file,'wb')      #open that file or create one
	l = c.recv(1024)         #get input
	while (l):
		f.write(l)            #save input to file
		l = c.recv(1024)      #get again until done

	f.close()

c.send('Thank you for connecting')
c.close()