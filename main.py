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

        self.sql_command  = {}
        self.table_dict   = {}
        self.table_list   = []
        self.table_header = []
        self.table_name   = "" 

        self.sql_command["create"]    = "CREATE TABLE {} ({});"
        self.sql_command["select"]    = "SELECT {} FROM {};"
        self.sql_command["cortege"]   = "INSERT INTO {} VALUES ({});"
        self.sql_command["attribute"] = "ALTER TABLE {} ADD COLUMN {} {}"
        self.sql_command["delete"]    = "DELETE FROM {} WHERE {};"
        self.sql_command["drop"]      = "DROP TABLE IF EXISTS {};" 
        self.sql_command["sample"]    = "SELECT {} FROM {} WHERE {};"

        self.ui.action.triggered.connect(self.read_file)
        self.ui.action_3.triggered.connect(self.save_as)
        self.ui.action_4.triggered.connect(self.close_app)
        self.ui.action_5.triggered.connect(self.showDlgCreateDB)
        self.ui.action_7.triggered.connect(self.insert_attribute_db)
        self.ui.action_10.triggered.connect(self.insert_cortege_db)
        self.ui.action_11.triggered.connect(self.delete_cortege_db)
        self.ui.action_6.triggered.connect(self.delete_db)
        self.ui.action_9.triggered.connect(self.showDlgConnectionDB)
        self.ui.action_13.triggered.connect(self.showTableList) 

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
        self.conn = psycopg2.connect(dbname=self.dlg_ui.lineEdit.text(),
                                        user=self.dlg_ui.lineEdit_2.text(),
                                        password=self.dlg_ui.lineEdit_3.text(),
                                        host=self.dlg_ui.lineEdit_4.text())
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

        self.showTableList()

    def attribute_list(self):
        self.cursor.execute(self.sql_command["sample"].format("COLUMN_NAME",
                                                              "information_schema.COLUMNS",
                                                              "TABLE_NAME = '{}'".format(self.table_name)))
        for i in self.cursor:
            self.table_header.append(i[0])

    def update_table(self):
        self.ui.tableWidget.setRowCount(len(self.table_list))
        self.ui.tableWidget.setColumnCount(len(self.table_list[0]))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_header)

        row = 0
        for tup in self.table_list:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1 

    def get_table(self):
        self.cursor.execute(self.sql_command["select"].format('*', self.table_name))

        self.table_list = []
        for i in self.cursor:
            self.table_list.append(i)

        self.attribute_list()
        if self.table_list:
            self.update_table()

    def search_db(self):
        predicate = self.ui.lineEdit.text()
        self.cursor.execute(self.sql_command["sample"].format('*', self.table_name, predicate))

        self.table_list = []
        for i in self.cursor:
            self.table_list.append(i)

        self.attribute_list()
        if self.table_list:
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
            combo.addItem("TEXT")
            self.dlg_ui.tableWidget.setCellWidget(row, 1, combo)

        self.dlg.show()

    def create_db(self):
        self.dlg.close()
        data = "" 

        for i in range(self.dlg_ui.tableWidget.rowCount()):
            if self.dlg_ui.tableWidget.item(i, 0):
                data += "{} {},".format(self.dlg_ui.tableWidget.takeItem(i, 0).text(),
                                        self.dlg_ui.tableWidget.cellWidget(i, 1).currentText())

        self.table_name = self.dlg_ui.lineEdit.text() 
        self.cursor.execute(self.sql_command["create"].format(self.table_name, data[:-1]))

    def insert_attribute_db(self):
        text, ok = QInputDialog.getText(self, "Вставка","Введите атрибут: ")
        if ok and text:
            insert = sql.SQL(self.sql_command["attribute"].format(self.table_name, text))
            self.cursor.execute(insert)	

            self.table_list.append(text.split(','))
            self.update_table()

    def insert_cortege_db(self):
        text, ok = QInputDialog.getText(self, "Вставка","Введите кортеж: ")
        if ok and text:
            insert = sql.SQL(self.sql_command["cortege"].format(self.table_name, text))
            self.cursor.execute(insert)	

            self.get_table()

    def delete_cortege_db(self):
        text, ok = QInputDialog.getText(self, "Удаление","Введите кортеж: ")
        if ok and text:
            delete = sql.SQL(self.sql_command["delete"].format(self.table_name, text))
            self.cursor.execute(delete)
            self.get_table()

    def delete_db(self):
        table_name, ok = QInputDialog.getText(self, "Удаление","Название таблиц: ")
        if ok and table_name:
            self.cursor.execute(self.sql_command["drop"].format(table_name))

    def showTableList(self):
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema \
                                    NOT IN ('information_schema','pg_catalog');")
        table_names = []
        ok = False 

        for i in self.cursor:
            for j in i:
                table_names.append(j)

        if table_names:
            self.table_name, ok = QInputDialog.getItem(self, "Выберите таблицу",
                                                        "Название таблиц:", table_names, 0, False)
        if ok:
            self.get_table()

    def read_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть файл', '/home')[0]
        try:
            with open(fname, "r", newline='') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    for column, value in iter(row.items()):
                        self.table_dict.setdefault(column, []).append(value)
                for key in self.table_dict.keys():
                    self.table_list.append(self.table_dict[key])
        except IOError:
            print("I/O error")


    def save(self):
        pass
    
    def save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как...', '/home')[0]
        try:
            with open(fname, "w", newline='') as f:
                writer = csv.DictWriter(f, delimiter=';', fieldnames=list(self.table_dict))
                writer.writeheader()

                for i in range(len(self.table_list[0])): 
                    l = []
                    for j in range(len(self.table_list)):
                        l.append(self.table_list[j][i])
                    writer.writerow(dict(zip(list(self.table_dict.keys()), l)))

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
