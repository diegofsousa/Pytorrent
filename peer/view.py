from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, subprocess
from socket import *
from architecture import Serverp2p, Clientp2p
from threading import Thread, current_thread
import random
from form_dict import AddElem
import netifaces
import time, sys
from timer_tll import TLL

class index(QDialog):
	def __init__(self, parent=None):
		super(index, self).__init__(parent)

		
		self.setWindowTitle("Peer")

		# Selecionando o IP do server
		self.ip = netifaces.ifaddresses('wlp1s0')[2][0]['addr']
		self.qPort = QInputDialog.getText(self, 'Informe a porta', 'IP detectado como '+self.ip+'. \nTecle enter para confirmar ou informe o seu IP correto na rede:')
		print(self.qPort[0])
		if self.qPort[0] != '':
			self.ip = self.qPort[0]

		# Inicia-se o servidor do peer como thread e seus possíveis sinais
		self.server = Serverp2p(self.ip)
		self.connect(self.server, SIGNAL("success(QString)"), self.success)
		self.connect(self.server, SIGNAL("fail()"), self.fail)
		self.connect(self.server, SIGNAL("forward(QString)"), self.forward_search)
		self.server.start()


		# self.client = Clientp2p()
		# self.client.start()
		informe = QLabel("Servico rodando no IP "+self.ip)

		hbox = QHBoxLayout()
		hbox.addWidget(informe)

		label = QLabel("Procure por palavra: ")
		self.nome_lineEdit = QLineEdit("")
		self.search = QPushButton("Procurar")
		self.tll = 5
		self.label_tll = QLabel("TTL: " + str(self.tll))

		hbox1 = QHBoxLayout()
		hbox1.addWidget(label)
		hbox1.addWidget(self.nome_lineEdit)
		hbox1.addWidget(self.search)
		hbox1.addWidget(self.label_tll)

		# Dicionario de palavras para a GUI
		self.lista_de_palavras = []
		informedic = QLabel("Dicionario contido neste servico:")
		self.lista = QListWidget()
		for i in self.lista_de_palavras:
			item = QListWidgetItem("Palavra: "+i.split(':')[0]+" - Significado: "+i.split(':')[1])
			self.lista.addItem(item)

		button_add_word = QPushButton("Adicionar palavra ao dicionario")
		button_remove_all_word = QPushButton("Limpar dicionario")

		hbox2 = QHBoxLayout()
		hbox2.addWidget(button_add_word)
		hbox2.addWidget(button_remove_all_word)

		
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
		vbox.addLayout(hbox3)
		vbox.addWidget(self.inforvizinhos)

		# Lista dos peers vizinhos
		self.lista_de_vizinhos = []


		vbox1 = QVBoxLayout()
		vbox1.addLayout(hbox)
		vbox1.addLayout(hbox1)
		vbox1.addLayout(vbox)

		self.setLayout(vbox1)

		# Instância do TTL
		self.ttll = TLL()

		# Sinais para o TTL que é acionado ao fazer procura de uma palavra
		self.connect(self.ttll, SIGNAL("timeo()"), self.timer_func)
		self.connect(self.ttll, SIGNAL("timeover()"), self.time_over)

		# Sinais dos cliques na interface
		self.connect(self.search, SIGNAL("clicked()"), self.averiguar)
		self.connect(add_vizinho, SIGNAL("clicked()"), self.add_viz)
		self.connect(limpar_v, SIGNAL("clicked()"), self.limpar_vizinhos)
		self.connect(button_add_word, SIGNAL("clicked()"), self.add_word)
		self.connect(button_remove_all_word, SIGNAL("clicked()"), self.clear_list)
		self.connect(sobre, SIGNAL("clicked()"), self.about)

		
		self.setGeometry(300,100,700,430)

	def averiguar(self):
		'''
		Este método faz a procura da palavra nos peers vizinhos
		'''
		self.ttll.start()
		if len(self.lista_de_vizinhos) == 0:
			self.ttll.terminate()
			msg = QMessageBox.information(self, "Erro!",
											"Nao ha nenhum IP vizinho conectado.",
											 QMessageBox.Close)
		else:
			try:
				print(self.lista_de_vizinhos)
				sorteado = random.choice(self.lista_de_vizinhos)
				print("A rota a seguir eh: {}".format(sorteado))
				self.client = Clientp2p(self.nome_lineEdit.displayText(), self.ip, sorteado)
				self.client.start()
			except Exception as e:
				self.client = Clientp2p(self.nome_lineEdit.displayText(), self.ip, '')
				self.client.start()

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

	def success(self, significado):
		'''
		Resposta do sinal para quando algum peer envia o significado para palavra procurada
		por este peer.
		'''
		self.tll = 5
		self.label_tll.setText("TTL: "+str(self.tll))
		msg = QMessageBox.information(self, "Sucesso!",
											"Significado da palavra encontrado: "+significado,
											 QMessageBox.Close)
	def fail(self):
		'''
		Resposta do sinal para quando algum peer envia a falha ao encontrar palavra procurada
		por este peer.
		'''
		self.tll = 5
		self.label_tll.setText("TTL: "+str(self.tll))
		msg = QMessageBox.information(self, "Falha!",
											"Falha ao encontar significado da palavra:",
											 QMessageBox.Close)

	def add_word(self):
		'''
		Este método adiciona palavras para no dicionário deste peer tanto na GUI quanto no server.
		'''
		ex = AddElem(self)
		a = self.connect(ex, SIGNAL("reload(QString)"), self.reload)	
		ex.setModal(True)
		ex.show()
		#print(self.lista_de_vizinhos)

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
				self.client = Clientp2p(palavra.split('^')[0], palavra.split('^')[1], sorteado)
				self.client.start()
		except Exception as e:
			self.client = Clientp2p(self.nome_lineEdit.displayText(), self.ip, '')
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

	def open_link(self):
		QDesktopServices.openUrl(QUrl('https://github.com/diegofsousa'))

			


app = QApplication(sys.argv)
dlg = index()
dlg.exec_()