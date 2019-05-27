from PyQt4.QtCore import *
from PyQt4.QtGui import *
from socket import *
import time, _thread as thread
from response import devolve


class Serverp2p(QThread):
	def __init__ (self, meuHost):
		self.meuHost = meuHost
		QThread.__init__(self)

	def run(self):
		'''
		Configurações iniciais do servidor. Ele é uma thread por que deve funcionar sempre em background
		enquando o Cliente deste mesmo peer irá funcionar eventualmente.
		'''

		# Lista de peers que são consumidos por este. Chamamos de vizinhos
		self.neighbors = []

		# Dicionário dinâmico deste peer
		self.dicionario_dict = {}
		self.sockobj = socket(AF_INET, SOCK_STREAM)
		self.sockobj.bind((self.meuHost, 5000))
		self.sockobj.listen(5)
		print("Run, barry, run on: IP" + self.meuHost + " - Porta: " + str(5000))
		self.despacha()
		


	def busca(self, data):
		'''
		Este método é responsável por tratar as requisições.
		Existem 4 casos:
		1º Caso: O cliente procura uma palavra no servidor que deste método. Se a palavra existir,
		este método enviará a resposta para a thread contida em "response.py" encaminha-la ao IP
		que procurou o significado da palavra.
		2º Caso: Se o cliente procurar a palavra e ela não existir no dicionário do servidor deste método,
		este se encarregará de emitir um sinal para a view (views.py) para que este peer redirecione a busca
		para outro peer.
		3º Caso: Daqui em diante, ficam as requisicões originadas de response, que é quando há uma resposta
		plausível para o cliente que procurou pela palavra. Estes casos sempre são executados no peer que 
		requisitou pela palavra. Quando a palavra vem acompanhada pelo 'r' no início, significa que algum peer
		enviou o significado palavra via "response.py". Apenas emitiremos um sinal para a view com a string.
		4º Caso: Quando o últmo peer visitado não tem ramificações, ele volta o erro via "response.py" para
		o peer que requisitou a palavra.
		'''

		# 3º Caso
		if(data.split('^')[0] == 'r'):
			#print("Achou a palavra: "+data.split('^')[1])
			self.emit(SIGNAL("success(QString)"), data.split('^')[1])
		# 4º Caso
		elif(data.split('^')[0] == 'e'):
			#print("Não achamos a peca certa "+data.split('^')[1])
			self.emit(SIGNAL("fail()"))
		else:
			#print("Chegou na função de busca")
			print(data.split('^')[0])
			# 1º Caso
			try:
				significado = self.dicionario_dict[data.split('^')[0]]
				if significado:					
					thread.start_new_thread(devolve, (data.split('^')[1], significado))
			# 2º Caso
			except Exception as e:
				print('Erro de busca')
				self.emit(SIGNAL("forward(QString)"), data)				
				return 'Nada foi encontrado'

	def lidaCliente(self, conexao):
		'''
		Este método é responsável por encaminhar os pedidos do cliente para as funções decodoficando
		suas mensagens
		'''
		while True:
			data = conexao.recv(1024)
			if not data: break
			conexao.send(b'Eco=> ')
			self.busca(data.decode())

	def despacha(self):
		'''
		Este método recebe as requisições dos clientes e os encaminham cada um para uma nova thread
		'''
		while True:
			conexao, endereco = self.sockobj.accept()
			print('Server foi requisitado ', endereco)
			thread.start_new_thread(self.lidaCliente, (conexao,))

	def add_di_lista(self, palavra):
		'''
		Este método adiciona novas palavras ao dicionario sincronizando-as com a view.
		'''
		print(palavra)
		self.dicionario_dict[palavra.split(":")[0]] = palavra.split(":")[1]

	def get_list_lista(self):
		'''
		Este método retorna as palavras do dicionário.
		'''
		return self.dicionario_dict

	def clear_list_server(self):
		self.dicionario_dict.clear()

class Clientp2p(QThread):
	def __init__ (self, word, fromm, ipsearch):
		self.word = word
		self.fromm = fromm
		self.ipsearch = ipsearch
		QThread.__init__(self)

	def run(self):
		'''
		Lado cliente. Funciona como thread pois é eventualmente acionado pelo mesmo peer em que roda
		o servidor no background.
		Recebe 3 parâmetros:
		word: É a palavra que o cliente quer procurar em algum servidor vizinho.
		fromm: É o próprio IP do cliente. Quando este cliente é usado como ponte, deve levar
		a o IP do cliente que requisitou a palavra até o servidor para que este tome uma decisão
		ipsearch: É o IP (vizinho) que será buscado para talvez encontrar a palavra em seu dicionário
		'''	
		serverHost = self.ipsearch

		if self.ipsearch == '':
			# Se o ipsearch está vazio significa que este peer não tem vizinhos para redirecionar
			# a consulta. leva-se o "e" no cabeçalho para o servidor do cliente raiz emitir um sinal que
			# não encontrou a palavra.
			print("Tentando se conectar a "+ self.ipsearch)
			sockobj = socket(AF_INET, SOCK_STREAM)
			sockobj.connect((serverHost, 5000))
			wordok = 'e^'+str(self.word)

			#linha = input("Informe a mensagem a ser buscada: ")

			sockobj.send(wordok.encode())

			data = sockobj.recv(1024)
			print("Cliente recebeu: ", data)

			sockobj.close()
		else:
			# Se o ipserch existir, segue o jogo. Procuramos a palavra no próximo servidor vizinho (O que foi
			# Sorteado).
			print("Tentando enviar resposta a "+ self.ipsearch)
			sockobj = socket(AF_INET, SOCK_STREAM)
			sockobj.connect((serverHost, 5000))
			wordok = str(self.word)+'^'+str(self.fromm)

			sockobj.send(wordok.encode())
			data = sockobj.recv(1024)
			print("Cliente recebeu: ", data)
			sockobj.close()
