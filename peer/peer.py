from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, subprocess
from socket import *
from tracker_architecture import ClientPeer, ServerPeer, client_without_thread, ClientFilePeer, ServerFilePeer
from threading import Thread, current_thread
import random
from form_dict import AddElem
import netifaces
import time, sys
from timer_tll import TLL

from pdf_proccess import get_info, pages, pdf_splitter, merger, info_run_pages
import json

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

		self.tracker_ip_dialog = QInputDialog.getText(self, 'Informe o host do Tracker', 'Tecle enter para confirmar:')
		print(self.tracker_ip_dialog[0])
		while self.tracker_ip_dialog[0] == '':
			self.tracker_ip_dialog = QInputDialog.getText(self, 'Informe o host do Tracker', 'Tecle enter para confirmar:')
		
		self.tracker_ip = self.tracker_ip_dialog[0]

		# Inicia-se o servidor do peer como thread e seus possíveis sinais
		self.server = ServerPeer(self.ip)
		self.connect(self.server, SIGNAL("reload_list(QString)"), self.reload_list)
		self.connect(self.server, SIGNAL("download(QString)"), self.proccess_and_return_pdf_to_request)
		self.server.start()

		self.server_file = ServerFilePeer(self.ip)
		self.connect(self.server_file, SIGNAL("already_part(QString)"), self.already_part)
		#self.connect(self.server, SIGNAL("download(QString)"), self.proccess_and_return_pdf_to_request)
		self.server_file.start()

		# Initialize tab screen
		tabs = QTabWidget()


		label = QLabel("Procure pelo arquivo: ")
		self.arquivo_lineEdit = QLineEdit("")

		name_file_box = QHBoxLayout()
		name_file_box.addWidget(label)
		name_file_box.addWidget(self.arquivo_lineEdit)

		label2 = QLabel("Tracker host: ")
		self.host_lineEdit = QLineEdit("")
		self.host_lineEdit.setText(self.tracker_ip)
		self.host_lineEdit.setDisabled(True)

		tracker_host_box = QHBoxLayout()
		tracker_host_box.addWidget(label2)
		tracker_host_box.addWidget(self.host_lineEdit)


		#layout = QVBoxLayout()

		label3 = QLabel("Arquivo: ")
		self.edit_file = QLineEdit("")
		self.edit_file.setDisabled(True)

		self.btn = QPushButton("...")
		self.btn.clicked.connect(self.getfile)

		file_box = QHBoxLayout()
		file_box.addWidget(label3)
		file_box.addWidget(self.edit_file)
		file_box.addWidget(self.btn)

		self.post_btn = QPushButton("Buscar")

		informedic = QLabel("Resultado:")

		self.lista = QListWidget()

		self.lista_de_palavras = []

		for i in self.lista_de_palavras:
			item = QListWidgetItem(i)
			self.lista.addItem(item)


		vbox = QVBoxLayout()
		vbox.addWidget(informedic)
		vbox.addWidget(self.lista)


		inforlogs = QLabel("Logs:")

		self.text_logs = QTextEdit()
		#self.text_logs.setDisabled(True)

		self.info_logs = ''


		vbox1 = QVBoxLayout()
		vbox1.addWidget(inforlogs)
		vbox1.addWidget(self.text_logs)

		inforlogs_d = QLabel("Downloads:")

		self.text_logs_donwloads = QTextEdit()
		self.text_logs_donwloads.setDisabled(True)

		self.info_logs_donwloads = ''



		vbox2 = QVBoxLayout()
		vbox2.addWidget(inforlogs_d)
		vbox2.addWidget(self.text_logs_donwloads)

		hbox_text = QHBoxLayout()
		hbox_text.addLayout(vbox)
		hbox_text.addLayout(vbox1)
		hbox_text.addLayout(vbox2)

		self.post_download = QPushButton("Fazer download do arquivo selecionado!")
		

		tab1 = QWidget()
		tab1.layout = QVBoxLayout()
		tab1.layout.addLayout(tracker_host_box)
		tab1.layout.addLayout(name_file_box)
		tab1.layout.addLayout(file_box)
		tab1.layout.addWidget(self.post_btn)
		tab1.layout.addLayout(hbox_text)
		tab1.layout.addWidget(self.post_download)

		tab1.setLayout(tab1.layout)

		
		label3 = QLabel("Disponibilizar arquivo na rede: ")
		self.btn_upload = QPushButton("Adicionar arquivo")
		self.btn_upload.clicked.connect(self.get_up_file)


		up_file_box = QHBoxLayout()
		up_file_box.addWidget(label3)
		up_file_box.addWidget(self.btn_upload)



		inform_files = QLabel("Arquivos:")
		self.lista_meus_aquivos = QListWidget()
		self.lista_de_meus_arquivos = []

		for i in self.lista_de_meus_arquivos:
			item = QListWidgetItem(i)
			self.lista_meus_aquivos.addItem(item)

		self.btn_clean_all = QPushButton("Limpar tudo")

		vbox3 = QVBoxLayout()
		vbox3.addWidget(inform_files)
		vbox3.addWidget(self.lista_meus_aquivos)
		vbox3.addWidget(self.btn_clean_all)


		tab2 = QWidget()
		tab2.layout = QVBoxLayout()
		tab2.layout.addLayout(up_file_box)
		tab2.layout.addLayout(vbox3)

		tab2.setLayout(tab2.layout)



		#self.tabs.resize(300,200)
		
		# Add tabs
		tabs.addTab(tab1,"Buscar arquivos na rede")
		tabs.addTab(tab2,"Meus arquivos")
		

		vbox1 = QVBoxLayout()
		vbox1.addWidget(tabs)

		self.setLayout(vbox1)

		self.connect(self.btn_clean_all, SIGNAL("clicked()"), self.my_files_clean)
		self.connect(self.post_btn, SIGNAL("clicked()"), self.search_button)
		self.connect(self.post_download, SIGNAL("clicked()"), self.download)

		self.file_name_actual = None
		self.valid_hosts = []


		
		self.setGeometry(300,100,700,430)

	def getfile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', 
		 '/home/',"Torrent files (*.torrent)")
		self.edit_file.setText(fname)

	def get_up_file(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', 
		 '/home/',"PDF files (*.pdf)")

		can_add = True

		info_new_file = get_info(fname)

		for file in self.lista_de_meus_arquivos:
			if info_new_file['md5'] == file['md5']:
				msg = QMessageBox.information(self, "Aviso","Este arquivo ja existe na lista!", QMessageBox.Close)
				can_add = False

		if can_add == True:
			info_new_file['protocol'] = 'new'
			info_new_file['ip_from'] = self.ip
			json_prepare = json.dumps(info_new_file)
			#print(json_prepare)
			#print(type(json))

			if client_without_thread(self.tracker_ip, json_prepare) == True:
				self.lista_de_meus_arquivos.append(info_new_file)
				#print(self.lista_de_meus_arquivos)
				self.reload_my_files_by_list()
				msg = QMessageBox.information(self, "Mensagem","Obrigado por semear!\nConteudo esta disponivel no Tracker.", QMessageBox.Close)
			else:
				msg = QMessageBox.information(self, "Aviso","Ocorreu um erro ao adicionar o arquivo ao Tracker!", QMessageBox.Close)


	def reload_my_files_by_list(self):
		self.lista_meus_aquivos.clear()

		for i in self.lista_de_meus_arquivos:
			i_to_str = str("Nome: " + i['name'] + " «» Tamanho: " + str(i['size']) + " «» Numero de páginas: " + str(i['num_pages']) + " «» md5: " + str(i['md5']))
			item = QListWidgetItem(i_to_str)
			self.lista_meus_aquivos.addItem(item)
		
	def my_files_clean(self):

		json_prepare = {"protocol":"clean_my_participations",
						"ip_from":self.ip}

		json_prepare = json.dumps(json_prepare)

		if client_without_thread(self.tracker_ip, json_prepare) == True:
			self.lista_de_meus_arquivos.clear()
			#print(self.lista_de_meus_arquivos)
			self.reload_my_files_by_list()
			msg = QMessageBox.information(self, "Mensagem","Suas participacoes foram removidas do Tracker com sucesso!", QMessageBox.Close)
		else:
			msg = QMessageBox.information(self, "Aviso","Ocorreu um erro ao fazer este processamento!", QMessageBox.Close)
		
	def search_button(self):
		text = self.arquivo_lineEdit.displayText()
		upload = self.edit_file.displayText()

		key = 'all' # 'all' files, 'upload' file or 'search' files

		if text == '' and upload != '':
			key = 'upload'
		elif text != '' and upload == '':
			key = 'search'

		if key == 'all':
			json_prepare = {"protocol":"search",
							"key":key,
							"ip_from":self.ip}
		elif key == 'upload':
			json_prepare = {"protocol":"search",
							"key":key,
							"ip_from":self.ip}
		elif key == 'search':
			json_prepare = {"protocol":"search",
							"key":key,
							"ip_from":self.ip,
							"term": text}

		json_prepare = json.dumps(json_prepare)

		if client_without_thread(self.tracker_ip, json_prepare) == True:
			self.lista_de_meus_arquivos.clear()
			#print(self.lista_de_meus_arquivos)
			#self.reload_my_files_by_list()
			#msg = QMessageBox.information(self, "Mensagem","Suas participacoes foram removidas do Tracker com sucesso!", QMessageBox.Close)
		else:
			msg = QMessageBox.information(self, "Aviso","Ocorreu um erro ao fazer este processamento!", QMessageBox.Close)

	def reload_list(self, text):
		self.lista.clear()

		self.lista_de_palavras = json.loads(text)['data']

		for file in self.lista_de_palavras:
			i_to_str = str("Nome: " + file['name'] + " «» Tamanho: " + str(file['size']) + " «» Numero de páginas: " + str(file['num_pages']) + " «» md5: " + str(file['md5']))
			item = QListWidgetItem(i_to_str)
			self.lista.addItem(item)

	import subprocess

	def download(self):
		selected = self.lista.currentRow()
		item = self.lista_de_palavras[selected]

		self.info_logs +='''\nPreparando download do arquivo "{}"... Revisando seeders...\n'''.format(item['name'])

		self.file_name_actual = item
		hosts = []
		self.valid_hosts = []

		for ip in item['hosts']:
			self.info_logs += "\n"+ip+"... "
			try:
				nmap = subprocess.check_output(["nmap","-p","5000", ip]).decode()
				status = nmap.split(" ")[24]
				if status != 'open':
					self.info_logs += "Erro!"
					hosts.append([ip, None, None, None, ''])
				else:
					latency = nmap.split("(")[2].split("s")[0]
					self.info_logs += "Ok! " + " - latência: "+ latency 
					hosts.append([ip, status, float(latency), False, ''])
			except Exception as e:
				pass

		for host in hosts:
			if host[1] == None or host[1] == self.ip:
				pass
				#self.info_logs += "\n"+host[0]+"... inacessível"
			else:
				self.valid_hosts.append(host)
				#self.info_logs += "\n"+host[0]+"... " + host[1] + " " + str(host[2])

		self.valid_hosts.sort(key = sortSecond)
		if len(self.valid_hosts) != 0:
			pages_req = pages(item['num_pages'], self.valid_hosts)

			self.info_logs += "\n\nRanking de hosts:"
			for request in pages_req:
				self.info_logs += "\n"+request[0][0]+" - Páginas: " + str(request[1])

			for request in pages_req:
				dump_json = json.dumps({'protocol':'download','ip_from': self.ip, 'md5': item['md5'], 'pages': request[1]})
				#print(request[0])
				print(dump_json)
				client = ClientPeer(request[0][0], dump_json)
				client.start()
		else:
			msg = QMessageBox.information(self, "Aviso","Nenhum host esta disponível no momento!", QMessageBox.Close)



		self.reload_text_logs()

	def proccess_and_return_pdf_to_request(self, text):
		data = json.loads(text)

		final_file = None

		for file in self.lista_de_meus_arquivos:
			if data['md5'] == file['md5']:
				final_file = file

		if final_file != None:
			path_file = pdf_splitter(self.ip, final_file["url"], data["pages"], final_file["md5"])
			self.client_file = ClientFilePeer(data['ip_from'], path_file, path_file.split("/")[1])
			self.client_file.start()

	def already_part(self, text):
		data = json.loads(text)

		for host in self.valid_hosts:
			if host[0] == data['part_ip']:
				host[3] = True
				host[4] = data['file_path']

		self.info_logs_donwloads +='''DOWNLOADS "{}":\n'''.format(self.file_name_actual['name'])

		for host in self.valid_hosts:
			if host[3] == True:
				self.info_logs_donwloads += "\n"+host[0]+" - download pronto!"
			else:
				self.info_logs_donwloads += "\n"+host[0]+" - ...!"

		self.reload_text_logs_downloads()

		ready = True
		for host in self.valid_hosts:
			if host[3] == False:
				ready = False

		if ready == True:
			paths_ok = []
			for host in self.valid_hosts:
				paths_ok.append(host[4])

			path_final = merger(paths_ok, self.file_name_actual['name'])
			path_info = get_info(path_final)
			md5_n = path_info['md5']
			print(md5_n)
			print(self.file_name_actual['md5'])
			if md5_n == self.file_name_actual['md5']:
				msg = QMessageBox.information(self, self.file_name_actual['name'],"O seu download foi concluído!\n\n md5 check: Ok!\n" + md5_n + "\n", QMessageBox.Close)
				path_info['protocol'] = 'add_for_new'
				path_info['ip_from'] = self.ip
				json_prepare = json.dumps(path_info)

				if client_without_thread(self.tracker_ip, json_prepare) == True:
					self.lista_de_meus_arquivos.append(path_info)
					#print(self.lista_de_meus_arquivos)
					self.reload_my_files_by_list()
					msg = QMessageBox.information(self, "Mensagem","Obrigado por semear!\nConteudo esta disponivel no Tracker.", QMessageBox.Close)
				else:
					msg = QMessageBox.information(self, "Aviso","Ocorreu um erro ao adicionar o arquivo ao Tracker!", QMessageBox.Close)
			else:
				msg = QMessageBox.information(self, self.file_name_actual['name'],"O seu download foi concluído sem sucesso.\n\n md5 check: Erro!\n", QMessageBox.Close)

	def reload_text_logs(self):
		self.text_logs.setText(self.info_logs)

	def reload_text_logs_downloads(self):
		self.text_logs_donwloads.setText(self.info_logs_donwloads)

def sortSecond(val): 
	return val[2] 


app = QApplication(sys.argv)
dlg = index()
dlg.exec_()