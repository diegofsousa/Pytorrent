from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, subprocess
from socket import *
from tracker_architecture import ServerTracker, ClientTracker,client_without_thread
from threading import Thread, current_thread
import random
import netifaces
import time, sys
import re
import json

class index(QDialog):
	def __init__(self, parent=None):
		super(index, self).__init__(parent)

		
		self.setWindowTitle("Tracker")

		# Selecionando a interface de rede

		item, ok = QInputDialog.getItem(self, "Interface de redes", 
		"Selecione sua interface de rede para iniciar a rede torrent:", netifaces.interfaces(), 0, False)

		# Selecionando o IP do server
		self.ip = netifaces.ifaddresses(item)[2][0]['addr']

		self.qPort = QInputDialog.getText(self, 'Informe a porta', 'IP detectado como '+self.ip+'. \nTecle enter para confirmar ou informe o seu IP correto na rede:')
		print(self.qPort[0])
		if self.qPort[0] != '':
			self.ip = self.qPort[0]

		# Inicia-se o servidor do tracker e seus possíveis sinais
		self.server = ServerTracker(self.ip)

		self.setWindowTitle("Tracker: "+ str(self.ip))
		self.connect(self.server, SIGNAL("new_file(QString)"), self.new_file)
		self.connect(self.server, SIGNAL("clean_participations_from_ip(QString)"), self.clean_participations_from_ip)
		self.connect(self.server, SIGNAL("seach_files(QString)"), self.seach_files)
		self.connect(self.server, SIGNAL("add_for_new(QString)"), self.add_for_new)
		self.server.start()

		informe = QLabel("Servidor tracker no IP "+self.ip)

		hbox = QHBoxLayout()
		hbox.addWidget(informe)

		label = QLabel("Procure por palavra: ")
		self.nome_lineEdit = QLineEdit("")
		self.search = QPushButton("Arquivos disponíveis")


		# Lista de arquivos disponíveis na rede
		self.lista_de_palavras = []
		informedic = QLabel("Arquivos disponíveis:")
		self.lista = QListWidget()

		self.itens = []

		for i in self.lista_de_palavras:
			item = QListWidgetItem(i)
			self.itens.append(item)
			self.lista.addItem(item)

		button_remove_files = QPushButton("Remover todos os arquivos")
		get_torrent_file = QPushButton("Baixar '.torrent' selecionado")

		hbox2 = QHBoxLayout()
		hbox2.addWidget(button_remove_files)
		hbox2.addWidget(get_torrent_file)


		vbox = QVBoxLayout()
		vbox.addWidget(informedic)
		vbox.addWidget(self.lista)
		vbox.addLayout(hbox2)


		vbox1 = QVBoxLayout()
		vbox1.addLayout(hbox)
		vbox1.addLayout(vbox)

		self.setLayout(vbox1)


		self.connect(self.lista, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.clique_arquivo)

		self.connect(button_remove_files, SIGNAL("clicked()"), self.remove_files)
		self.connect(get_torrent_file, SIGNAL("clicked()"), self.donwload_torrent_file)

		
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
		else:
			lista = list(filter(lambda x: re.search(search['term'], x['name'], re.IGNORECASE), self.lista_de_palavras))
			json_parametrizado = lista

		json_final = {'protocol': 'reload_list',
					  'data':json_parametrizado}

		self.client = client_without_thread(search['ip_from'], json.dumps(json_final))

	def donwload_torrent_file(self):
		selected = self.lista_de_palavras[self.lista.currentRow()]
		j_selected = json.dumps(selected)
		print(j_selected)

		try:
			arquivo = open('torrent_files/' + selected['name'].split('.')[0] + ".torrent", 'r+')
		except FileNotFoundError:
			arquivo = open('torrent_files/' + selected['name'].split('.')[0] + ".torrent", 'w+')
			arquivo.writelines(j_selected)
		arquivo.close()
		

	def new_file(self, text):

		file = json.loads(text)
		file['hosts'] = [file['ip_from'],]
		file.pop('protocol', None)

		self.lista_de_palavras.append(file)

		item = QListWidgetItem(str("Nome: " + file['name'] + " «» Tamanho: " + str(file['size']) + " «» Numero de páginas: " + str(file['num_pages']) + " «» md5: " + str(file['md5'])))
		
		self.itens.append('teste')

		self.lista.addItem(item)

	def add_for_new(self, text):

		file = json.loads(text)
		file.pop('protocol', None)

		for it in self.lista_de_palavras:
			if str(file['md5']) == str(it['md5']):
				it['hosts'].append(file['ip_from'])

		self.reload_list()

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

	def clear_list(self):
		'''
		Limpa a lista
		'''
		self.lista.clear()
		self.server.clear_list_server()


app = QApplication(sys.argv)
dlg = index()
dlg.exec_()