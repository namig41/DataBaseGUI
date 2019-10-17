import psycopg2
from psycopg2 import sql
import sys
import csv
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QTableWidgetItem
from DataBaseGUI import Ui_MainWindow
import Connection
import Create

#https://python-scripts.com/pyqt5
#https://khashtamov.com/ru/postgresql-python-psycopg2/

class DB_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(DB_GUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.data_base_dict = {}
        self.data_base_list = []
        self.table_name = "" 

        self.ui.action.triggered.connect(self.read_file)
        self.ui.action_3.triggered.connect(self.save_as)
        self.ui.action_4.triggered.connect(self.close_app)
        self.ui.action_5.triggered.connect(self.create_db)
        self.ui.action_7.triggered.connect(self.insert_db)
        self.ui.action_8.triggered.connect(self.delete_db)
        self.ui.action_9.triggered.connect(self.showDlgConnection)

    def showDlgConnection(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Connection.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)
        self.dlg.show()

        self.dlg_ui.buttonBox.accepted.connect(self.connect_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)
    
    def connect_db(self):
        self.dlg.close()
        self.conn = psycopg2.connect(dbname=self.dlg_ui.lineEdit.text(),
                                        user=self.dlg_ui.lineEdit_2.text(),
                                        password=self.dlg_ui.lineEdit_3.text(),
                                        host=self.dlg_ui.lineEdit_4.text())
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','pg_catalog');")
        table = []
        for i in self.cursor:
            for k in i:
                table.append(k)

        if table:
            self.table_name, ok = QInputDialog.getItem(self, "Выберите таблицу", "Название таблиц:", table, 0, False)
            if ok:
                self.cursor.execute("SELECT * FROM {};".format(self.table_name))
                for i in self.cursor:
                    self.data_base_list.append(i)
                self.update_table()

    def update_table(self):
        self.ui.tableWidget.setRowCount(len(self.data_base_list))
        self.ui.tableWidget.setColumnCount(len(self.data_base_list[0]))
        row = 0
        for tup in self.data_base_list:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1 

    def create_db(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Create.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(('Имя атрибута', 'Тип'))

        row = 0
        for _ in range(10):
 
            combo = QtWidgets.QComboBox()
            combo.addItem("INT")
            combo.addItem("TEXT")
 
            self.dlg_ui.tableWidget.setCellWidget(row, 1, combo)
            row += 1

        self.dlg.show()

    def insert_db(self):
        text, ok = QInputDialog.getText(self, "Вставка","Введите строку: ")
        if ok and text:
            insert = sql.SQL("INSERT INTO %s VALUES (%s)" % (self.table_name, text))
            self.cursor.execute(insert)

    def delete_db(self):
        table_name, ok = QInputDialog.getText(self, "Удаление","Название таблиц: ")
        if ok and table_name:
            self.cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))

    def read_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть файл', '/home')[0]
        try:
            with open(fname, "r", newline='') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    for column, value in iter(row.items()):
                        self.data_base_dict.setdefault(column, []).append(value)
        except IOError:
            print("I/O error")


    def save(self):
        pass
    
    def save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как...', '/home')[0]
        print(self.data_base_dict.values())
        try:
            with open(fname, "w", newline='') as f:
                writer = csv.DictWriter(f, delimiter=';', fieldnames=list(self.data_base_dict))
                writer.writeheader()
                for keys, data in self.data_base_dict.items():
                    print(keys, data)
        except IOError:
            print("I/O error")

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