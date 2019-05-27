import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AddElem(QDialog):
    '''
    Esta classe é uma janela para adição de nova palavra no dicionário dinâmico da GUI.
    '''
    def __init__(self, parent=None):
        super(AddElem, self).__init__(parent)

        lblEmail = QLabel("Palavra: ")
        self.campoEmail = QLineEdit("")

        lblSenha = QLabel("Significado: ")
        self.campoSenha = QLineEdit("")

        botaoSalvar = QPushButton("Adicionar")

        camposDeEmails = QHBoxLayout()
        camposDeEmails.addWidget(lblEmail)
        camposDeEmails.addWidget(self.campoEmail)

        camposDeSenha = QHBoxLayout()
        camposDeSenha.addWidget(lblSenha)
        camposDeSenha.addWidget(self.campoSenha)

        vbox = QVBoxLayout()
        vbox.addLayout(camposDeEmails)
        vbox.addLayout(camposDeSenha)
        vbox.addWidget(botaoSalvar)


        self.connect(botaoSalvar, SIGNAL("clicked()"), self.salvar)

        self.setLayout(vbox)
        self.setWindowTitle("Adcionando palavra ao dicionario")
        self.setGeometry(500, 300, 300, 100)

    def salvar(self):
        print(self.campoEmail.displayText())
        if self.campoSenha.displayText() == "" or self.campoEmail.displayText() == "":
            msg = QMessageBox.warning(self, "Alerta",
                                     "Preencha todos os campos!", QMessageBox.Close)
        else:
            #lista.append(self.campoEmail.displayText() + ":" + self.campoSenha.displayText())
            self.emit(SIGNAL("reload(QString)"), self.campoEmail.displayText() + ":" + self.campoSenha.displayText())
            self.close()
