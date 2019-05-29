from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, subprocess
from socket import *
from tracker_architecture import ServerTracker, ClientTracker,client_without_thread
from threading import Thread, current_thread
import random
from form_dict import AddElem
import netifaces
import time, sys
from timer_tll import TLL

import re

import json

class index(QDialog):
	def __init__(self, parent=None):
		super(index, self).__init__(parent)

		
		self.setWindowTitle("Tracker")

		# Selecionando o IP do server
		self.ip = netifaces.ifaddresses('eth0')[2][0]['addr']
		self.qPort = QInputDialog.getText(self, 'Informe a porta', 'IP detectado como '+self.ip+'. \nTecle enter para confirmar ou informe o seu IP correto na rede:')
		print(self.qPort[0])
		if self.qPort[0] != '':
			self.ip = self.qPort[0]

		# Inicia-se o servidor do peer como thread e seus possíveis sinais
		self.server = ServerTracker(self.ip)

		self.setWindowTitle("Tracker: "+ str(self.ip))

		self.connect(self.server, SIGNAL("new_file(QString)"), self.new_file)
		self.connect(self.server, SIGNAL("clean_participations_from_ip(QString)"), self.clean_participations_from_ip)
		self.connect(self.server, SIGNAL("seach_files(QString)"), self.seach_files)
		self.server.start()


		# self.client = Clientp2p()
		# self.client.start()
		informe = QLabel("Servidor tracker no IP "+self.ip)

		hbox = QHBoxLayout()
		hbox.addWidget(informe)

		label = QLabel("Procure por palavra: ")
		self.nome_lineEdit = QLineEdit("")
		self.search = QPushButton("Arquivos disponíveis")
		self.tll = 5
		self.label_tll = QLabel("TTL: " + str(self.tll))

		#hbox1 = QHBoxLayout()
		#hbox1.addWidget(label)
		#hbox1.addWidget(self.nome_lineEdit)
		#hbox1.addWidget(self.search)
		#hbox1.addWidget(self.label_tll)

		# Dicionario de palavras para a GUI
		self.lista_de_palavras = []
		informedic = QLabel("Arquivos disponíveis:")
		self.lista = QListWidget()

		self.itens = []

		for i in self.lista_de_palavras:
			item = QListWidgetItem(i)
			self.itens.append(item)
			self.lista.addItem(item)

		button_remove_files = QPushButton("Remover todos os arquivos")
		button_remove_all_word = QPushButton("Limpar dicionario")

		hbox2 = QHBoxLayout()
		hbox2.addWidget(button_remove_files)
		#hbox2.addWidget(button_remove_all_word)

		
		self.inforvizinhos = QLabel("Vizinhos proximos: " + str(self.lista_de_palavras))
		add_vizinho = QPushButton("Adicionar vizinho")
		limpar_v = QPushButton("Limpar vizinhos")
		sobre = QPushButton("Sobre")

		hbox3 = QHBoxLayout()
		hbox3.addWidget(add_vizinho)
		hbox3.addWidget(limpar_v)
		hbox3.addWidget(sobre)

		vbox = QVBoxLayout()
		vbox.addWidget(informedic)
		vbox.addWidget(self.lista)
		vbox.addLayout(hbox2)
		#vbox.addLayout(hbox3)
		#vbox.addWidget(self.inforvizinhos)

		# Lista dos peers vizinhos
		self.lista_de_vizinhos = []


		vbox1 = QVBoxLayout()
		vbox1.addLayout(hbox)
		#vbox1.addLayout(hbox1)
		vbox1.addLayout(vbox)

		self.setLayout(vbox1)

		# Instância do TTL
		self.ttll = TLL()

		# Sinais para o TTL que é acionado ao fazer procura de uma palavra
		self.connect(self.ttll, SIGNAL("timeo()"), self.timer_func)
		self.connect(self.ttll, SIGNAL("timeover()"), self.time_over)

		self.connect(self.lista, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.clique_arquivo)

		self.connect(button_remove_files, SIGNAL("clicked()"), self.remove_files)

		
		self.setGeometry(300,100,700,430)

	def clique_arquivo(self, item):
		print_this = '''
			\nNome do arquivo: {},
			\nTamanho: {},
			\nCaminho completo: {},
			\nNúmero de páginas: {},
			\nPalavras em cada página: {},
			\nCriador: {},
			\nSeeds: {},
			\nmd5 correspondente: {}.
		'''.format(self.lista_de_palavras[self.lista.currentRow()]['name'],
				   str(self.lista_de_palavras[self.lista.currentRow()]['size']),
				   self.lista_de_palavras[self.lista.currentRow()]['url'],
				   str(self.lista_de_palavras[self.lista.currentRow()]['num_pages']),
				   str(self.lista_de_palavras[self.lista.currentRow()]['count_words_by_pages']),
				   str(self.lista_de_palavras[self.lista.currentRow()]['ip_from']),
				   str(self.lista_de_palavras[self.lista.currentRow()]['hosts']),
				   str(self.lista_de_palavras[self.lista.currentRow()]['md5']))
		msg = QMessageBox.information(self, "Detalhes", print_this, QMessageBox.Close)

	def seach_files(self, text):
		'''
		Este método faz a procura da palavra nos peers vizinhos
		'''
		search = json.loads(text)

		if search['key'] == 'all':
			json_parametrizado = self.lista_de_palavras
		elif search['key'] == 'search':
			lista = list(filter(lambda x: re.search(search['term'], x['name'], re.IGNORECASE), self.lista_de_palavras))
			json_parametrizado = lista
		else:
			json_parametrizado = self.lista_de_palavras

		json_final = {'protocol': 'reload_list',
					  'data':json_parametrizado}

		self.client = client_without_thread(search['ip_from'], json.dumps(json_final))
		

	def add_viz(self):
		'''
		Este método adiciona IP's vizinhos tanto na GUI quanto na variável do server
		'''
		add = QInputDialog.getText(self, 'Adicionando IP vizinho', 'Adicione um IP valido:',QLineEdit.Normal ,self.ip.replace(self.ip.split('.')[-1], ''))

		if add[0] == '':
			msg = QMessageBox.information(self, "Alerta",
											"Informe um IP valido",
											 QMessageBox.Close)
		else:
			self.lista_de_vizinhos.append(add[0])
			self.inforvizinhos.setText("Vizinhos proximos: " + str(self.lista_de_vizinhos))

	def limpar_vizinhos(self):
		'''
		Este método serve para limpar os vizinhos.
		'''
		self.lista_de_vizinhos.clear()
		self.inforvizinhos.setText("Vizinhos proximos: " + str(self.lista_de_vizinhos))

	def new_file(self, text):

		file = json.loads(text)
		file['hosts'] = [file['ip_from'],]
		file.pop('protocol', None)

		self.lista_de_palavras.append(file)

		item = QListWidgetItem(str("Nome: " + file['name'] + " «» Tamanho: " + str(file['size']) + " «» Numero de páginas: " + str(file['num_pages']) + " «» md5: " + str(file['md5'])))
		
		self.itens.append('teste')

		self.lista.addItem(item)

	def clean_participations_from_ip(self, text):
		file = json.loads(text)
		for item in self.lista_de_palavras:
			if len(item['hosts']) == 1 and item['hosts'][0] == file['ip_from']:
				self.lista_de_palavras.remove(item)

			elif item['ip_from'] == file['ip_from'] and len(item['hosts']) > 1:
				item['ip_from'] = ''
				item['hosts'].remove(file['ip_from'])
			else:
				for ip in item['hosts']:
					if ip == file['ip_from']:
						item['hosts'].remove(ip)

		self.reload_list()

	def reload_list(self):
		self.lista.clear()

		for file in self.lista_de_palavras:
			i_to_str = str("Nome: " + file['name'] + " «» Tamanho: " + str(file['size']) + " «» Numero de páginas: " + str(file['num_pages']) + " «» md5: " + str(file['md5']))
			item = QListWidgetItem(i_to_str)
			self.lista.addItem(item)

	def remove_files(self):
		self.lista_de_palavras.clear()
		self.lista.clear()

	def reload(self, palavra):
		'''
		Método auxiliar para "add_word"
		'''
		self.lista_de_palavras.append(palavra)
		item = QListWidgetItem("Palavra: "+palavra.split(':')[0]+" - Significado: "+palavra.split(':')[1])
		self.lista.addItem(item)
		self.server.add_di_lista(palavra)
		print("Listando ...")
		print(self.server.get_list_lista())

	def clear_list(self):
		'''
		Limpa a lista
		'''
		self.lista.clear()
		self.server.clear_list_server()


	def timer_func(self):
		'''
		Ao receber um sinal, decrementa o contador na GUI
		'''
		print("TTL expirando em: "+str(self.tll))
		self.tll -= 1
		self.label_tll.setText("TTL: "+str(self.tll))

	def time_over(self):
		'''
		Ao receber um sinal, informa ao usuário que o TTL acabou.
		'''
		self.tll = 5
		self.label_tll.setText("TTL: "+str(self.tll))
		msg = QMessageBox.information(self, "Falha!",
											"Tempo de espera por mensagem acabou.",
											 QMessageBox.Close)
		self.client.terminate()

	def forward_search(self, palavra):
		'''
		Ao receber sinal, repassa a consulta para algum vizinho próximo. 
		'''
		try:
			if self.tll != 0:
				sorteado = random.choice(self.lista_de_vizinhos)
				print("A rota a seguir eh: {}".format(sorteado))
				self.client = ClientTracker(palavra.split('^')[0], palavra.split('^')[1], sorteado)
				self.client.start()
		except Exception as e:
			self.client = ClientTracker(self.nome_lineEdit.displayText(), self.ip, '')
			self.client.start()

	def about(self):
		'''
		Este método dá os créditos ao desenvolvedor da aplicação
		'''
		msg = QMessageBox.information(self, "Sobre",
											"Desenvolvedor: Diego Fernando\n"+
											"https://github.com/diegofsousa/",
											 'Página do desenvolvedor')
		self.open_link()


			


app = QApplication(sys.argv)
dlg = index()
dlg.exec_()