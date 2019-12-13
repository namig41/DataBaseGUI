#! /usr/bin/python3.6
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import sql
import sys
import csv
import random
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QTableWidgetItem, QMessageBox
from DataBaseGUI import Ui_MainWindow
import Connection
import Create
import Cortege

#https://python-scripts.com/pyqt5
#https://khashtamov.com/ru/postgresql-python-psycopg2/

class DB_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(DB_GUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sql_command  = {}
        self.table        = []
        self.table_header = []
        self.table_name   = "" 
        self.flag = True
        self.colors = [QtCore.Qt.blue, QtCore.Qt.darkMagenta, QtCore.Qt.darkRed, QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.cyan]

        self.sql_command["create"]    = "CREATE TABLE {} ({});"
        self.sql_command["select"]    = "SELECT {} FROM {};"
        self.sql_command["insert"]    = "INSERT INTO {} VALUES ({});"
        self.sql_command["delete"]    = "DELETE FROM {} WHERE {};"
        self.sql_command["drop"]      = "DROP TABLE IF EXISTS {};" 
        self.sql_command["sample"]    = "SELECT {} FROM {} WHERE {};"
        self.sql_command["copy"]      = "COPY {} FROM {!r} DELIMITER ';' ENCODING 'WIN1251' CSV HEADER";

        self.ui.action.triggered.connect(self.read_file)
        self.ui.action_3.triggered.connect(self.save_as)
        self.ui.action_4.triggered.connect(self.close_app)
        self.ui.action_5.triggered.connect(self.showDlgCreateDB)
        self.ui.action_8.triggered.connect(self.insert_file_db)
        self.ui.action_10.triggered.connect(self.showDlgCortegeAdd)
        self.ui.action_11.triggered.connect(self.delete_cortege_db)
        self.ui.action_6.triggered.connect(self.delete_db)
        self.ui.action_9.triggered.connect(self.showDlgConnectionDB)
        self.ui.pushButton.clicked.connect(self.search_db)

    def showDlgConnectionDB(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Connection.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)
        self.dlg.show()

        self.dlg_ui.buttonBox.accepted.connect(self.connect_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)
    
    def connect_db(self):
        self.dlg.close()
        try:
            self.conn = psycopg2.connect(dbname=self.dlg_ui.lineEdit.text(),
                                            user=self.dlg_ui.lineEdit_2.text(),
                                            password=self.dlg_ui.lineEdit_3.text(),
                                            host=self.dlg_ui.lineEdit_4.text())
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()

            self.cursor.execute("select table_name from information_schema.tables where table_schema \
                                        not in ('information_schema','pg_catalog');")
            self.init_comboBox()
        except:
            QMessageBox.critical(self, "Error", "Произошла ошибка входа")

    def update_table_name(self, name):
        self.table_name = name
        self.get_table()

    def attribute_list(self):
        self.cursor.execute(self.sql_command["sample"].format("COLUMN_NAME",
                                                              "information_schema.COLUMNS",
                                                              "TABLE_NAME = '{}'".format(self.table_name)))
        self.table_header = []
        for i in self.cursor:
            self.table_header.append(i[0])

    def update_table(self):
        self.attribute_list()
        self.ui.tableWidget.setRowCount(len(self.table))
        self.ui.tableWidget.setColumnCount(len(self.table_header))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_header)

        row = 0
        for tup in self.table:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1 

    def get_table(self):
        if self.table_name:
            self.cursor.execute(self.sql_command["select"].format('*', self.table_name))

            self.table = []
            for i in self.cursor:
                self.table.append(i)

            self.attribute_list()
            self.update_table()

    def search_db(self):
        search_text = self.ui.lineEdit.text()
        if search_text:
            if '=' in search_text or '>' in search_text or '<' in search_text: 
                self.cursor.execute(self.sql_command["sample"].format('*', self.table_name, search_text))
                
                self.table = []
                for i in self.cursor:
                    self.table.append(i)

                self.attribute_list()
                if self.table:
                    self.update_table()
            else:
                c = self.colors.pop()
                if search_text[-1] == '\'':
                    i = 0
                    for row in self.table:
                        j = 0
                        for item in row:
                            if search_text[:-1] in str(item):
                                self.ui.tableWidget.item(i, j).setBackground(c)
                            j += 1
                        i += 1 
                else:
                    i = 0
                    for row in self.table:
                        j = 0
                        for item in row:
                            if search_text == str(item):
                                self.ui.tableWidget.item(i, j).setBackground(c)
                            j += 1
                        i += 1 
        else:
            self.colors = [QtCore.Qt.blue, QtCore.Qt.darkMagenta, QtCore.Qt.darkRed, QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.cyan]
            self.update_table()

        
    def showDlgCreateDB(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Create.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)

        self.dlg_ui.buttonBox.accepted.connect(self.create_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(('Имя атрибута', 'Тип'))

        for row in range(self.dlg_ui.tableWidget.rowCount()):
            combo = QtWidgets.QComboBox(self.dlg)
            combo.addItem("INT")
            combo.addItem("REAL")
            combo.addItem("TEXT")
            combo.addItem("TIME")
            combo.addItem("DATE")
            self.dlg_ui.tableWidget.setCellWidget(row, 1, combo)
        self.dlg.show()

    def create_db(self):
        self.dlg.close()
        try:
            data = "" 

            for i in range(self.dlg_ui.tableWidget.rowCount()):
                if self.dlg_ui.tableWidget.item(i, 0):
                    data += "{} {},".format(self.dlg_ui.tableWidget.takeItem(i, 0).text(),
                                            self.dlg_ui.tableWidget.cellWidget(i, 1).currentText())

            self.table_name = self.dlg_ui.lineEdit.text() 
            self.cursor.execute(self.sql_command["create"].format(self.table_name, data[:-1]))
            self.table_names.append(self.table_name)
            self.update_comboBox()
        except:
            QMessageBox.critical(self, "Error", "Не удалось создать таблицу")

    def showDlgCortegeAdd(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Cortege.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)

        self.dlg_ui.tableWidget.setColumnCount(len(self.table_header))
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(self.table_header)
        self.dlg.show()

        self.dlg_ui.buttonBox.accepted.connect(self.insert_cortege_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)

    def insert_cortege_db(self):
        try:
            text = ""
            for row in range(self.dlg_ui.tableWidget.rowCount()):
                for col in range(len(self.table_header)):
                    if self.dlg_ui.tableWidget.item(row, col):
                        text += self.dlg_ui.tableWidget.item(row, col).text() + ','
                    else:
                        text += "NULL" + ','
            if text:
                insert = sql.SQL(self.sql_command["insert"].format(self.table_name, text[:-1]))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Не удалось вставить кортеж")


    def delete_cortege_db(self):
        try:
            text, ok = QInputDialog.getText(self, "Удаление", "Введите строку: ")
            if text and ok:
                insert = sql.SQL(self.sql_command["delete"].format(self.table_name, text))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Не удалось удалить кортеж")

    def insert_file_db(self):
        if True:
            insert = sql.SQL(self.sql_command["copy"].format(self.table_name, self.fname))
            self.cursor.execute(insert)
            self.update_table()
        else:
            QMessageBox.critical(self, "Error", "Не удалось скопировать данные")


    def delete_db(self):
        try:
            if self.table_names:
                self.table_name, ok = QInputDialog.getItem(self, "Выберите таблицу",
                                                            "Название таблиц:", self.table_names, 0, False)
            if ok and self.table_name:
                self.cursor.execute(self.sql_command["drop"].format(self.table_name))
                self.table_names.remove(self.table_name)
                self.update_comboBox()
        except:
            QMessageBox.critical(self, "Error", "Не удалось удалить таблицу")


    def init_comboBox(self):
        self.table_names = []
        for name in self.cursor:
            self.table_names.append(name[0])
        self.update_comboBox()
        if self.table_names:
            self.table_name = self.table_names[0]
        self.get_table()

    def update_comboBox(self):
        self.ui.comboBox.clear()
        for name in self.table_names:
            self.ui.comboBox.addItem(name)

        self.ui.comboBox.currentTextChanged.connect(self.update_table_name)

    def read_file(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Открыть файл', '/home')[0]
        try:
            with open(self.fname, "r", errors='ignore', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                self.table_header = next(reader, None)
                self.table = []
                for row in reader: 
                    self.table.append(row)
        except IOError:
            QMessageBox.critical(self, "Error", "Не удалось прочитать файл")

    def save(self):
        try:
            with open(self.fname, "w", errors='ignore', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.table_header)
                for row in self.table: 
                    writer.writerow(row)
        except IOError:
            QMessageBox.critical(self, "Error", "Не удалось сохранить файл")
    
    def save_as(self):
        self.fname = QFileDialog.getSaveFileName(self, 'Сохранить как...', '/home')[0]
        try:
            with open(self.fname, "w", errors='ignore', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.table_header)
                for row in self.table: 
                    writer.writerow(row)
        except IOError:
            QMessageBox.critical(self, "Error", "Не удалось сохранить файл")

    def close_app(self):
        self.conn.close()
        self.close()


def main():
    app = QtWidgets.QApplication([])
    application = DB_GUI()
    application.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
