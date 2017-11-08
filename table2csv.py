# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView
from guitable2csv import Ui_MainWindow
import psycopg2
import psycopg2.extras
import csv

class MyFirstGuiProgram(Ui_MainWindow):
    def __init__(self, dialog):
        Ui_MainWindow.__init__(self)
        self.setupUi(dialog)

        self.pbuConectar.clicked.connect(self.ConexionBD)
        self.pbuGeneraCSV.clicked.connect(self.GeneraCSV)
        self.lstEsquema.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lstEsquema.itemSelectionChanged.connect(self.ListaTabla)

        self.pbaGeneraCSV.setValue(0)
        self.ledServidor.setText('signwall02.clz6pendayku.us-east-1.rds.amazonaws.com')
        self.ledBD.setText('dev_bd_ods')
        self.ledUsuario.setText('analisisdev')
        self.ledContrasena.setText('1dq2ZEw7PdnOGA')
        self.ledRuta.setText('c:\\temp\\')

    def ConexionBD(self):
        try:
            conn_string = "host=" + self.ledServidor.text() +\
                          " dbname=" + self.ledBD.text() +\
                          " user=" + self.ledUsuario.text() +\
                          " password=" + self.ledContrasena.text()
            global conn
            conn = psycopg2.connect(conn_string)
            print("Conexión correcta.")
        except:
            print("No se pudo conectar a la base datos.")

        self.cursorEsquema = conn.cursor()
        self.cursorEsquema.execute("select schema_name from information_schema.schemata order by 1")

        for row in self.cursorEsquema:
            try:
                print(row[0])
                self.lstEsquema.addItem(row[0])
            except:
                print('Error: '+row[0])

        self.lstEsquema.update()

    def ListaTabla(self):
        self.lstTabla.clear()
        esquema = [item.text() for item in self.lstEsquema.selectedItems()][0]
        print(esquema)
        cursorTabla = conn.cursor()
        str_execute = "select table_name from information_schema.tables where table_schema = '"+esquema+"' order by 1"
        print(str_execute)
        cursorTabla.execute(str_execute)
        print(str_execute)
        for row in cursorTabla:
            try:
                print(row[0])
                self.lstTabla.addItem(row[0])
            except:
                print('Error: '+row[0])
        self.lstTabla.update()

    def GeneraCSV(self):
        esquema = [item.text() for item in self.lstEsquema.selectedItems()][0]
        tabla = [item.text() for item in self.lstTabla.selectedItems()][0]
        print(esquema+'.'+tabla)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM '+esquema+'.'+tabla)
        totalRows=cursor.rowcount
        writer = csv.writer(open(esquema+'_'+tabla+'.csv', 'w',
                                 newline='', encoding='utf8'), delimiter='@', quotechar='"', quoting= csv.QUOTE_MINIMAL)
        log = open('eggs.log', 'w', newline='', encoding='utf8')
        numRow = 0
        numError =  0
        self.pbaGeneraCSV.setValue(0)

        for row in cursor:
            try:
                writer.writerow(row)
                numRow=numRow+1
                if totalRows > 0:
                    pctAvance=round((numRow/totalRows)*100, 0)
                    self.pbaGeneraCSV.setValue(pctAvance)
                print(numRow)
            except:
                numError = numError+1
                log.write(str(row))
                print(row)

        print("Cantidad de errores: "+str(numError))



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyFirstGuiProgram(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())