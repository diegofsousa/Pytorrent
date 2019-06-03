#client_sock.py
import socket
import base64
HOST = 'localhost' #coloca o host do servidor
PORT = 57002

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
import json

s.connect((HOST,PORT))

file = 'new_merge.pdf'
	
arq = open(file, 'rb')

prepare_arq = base64.encodebytes(arq.read())


dic = {'content':prepare_arq.decode('ascii')}

#print(json.dumps(dic))



s.send(json.dumps(dic).encode())

# with open(file,'r') as f:
# 	d = {'nome':'tipo.pdf',
# 		'conteudo':f.read().decode()}
# 	s.sendall(json.dumps(d))

arq.close()
s.close()