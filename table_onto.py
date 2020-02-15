# from PyQt5 import QtWidgets
from datetime import datetime

from PyQt5.QtWidgets import *  # QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QSize, Qt
from owlready2 import *
from datetime import *
import re

inst_domain = []  # self.table.item(new_row,1).text()
inst_people = []  # self.table.item(new_row,3).text()
inst_task = []  # self.table.item(new_row,0).text()


class MainWindow(QMainWindow):

    # Override class constructor
    def __init__(self):
        # You must call the super class method
        QMainWindow.__init__(self)

        self.menubar = self.menuBar()
        self.newAct = QAction('Save', self)
        self.impAct = QAction('owl', self)
        self.impMenu = QMenu('Import', self)
        self.bug_onto = get_ontology("http://test.org/bug.owl").load()
        self.table = QTableWidget(self)  # Create a table
        self.new_domain = 0
        self.setMinimumSize(QSize(480, 120))  # Set sizes
        self.setWindowTitle("TasktrackerOnto")  # Set the window title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Install the central widget

        self.grid_layout = QGridLayout(self)  # Create QGridLayout
        central_widget.setLayout(self.grid_layout)  # Set this layout in central widget

        self.ontology()
        self.my_window()

    def my_window(self):
        # создает строку меню
        fileMenu = self.menubar.addMenu('File')

        self.impAct.setShortcut('Ctrl+O')
        self.impAct.setStatusTip('Open new File')
        self.impAct.triggered.connect(self.showDialog)
        self.impMenu.addAction(self.impAct)

        self.newAct.triggered.connect(self.save_owl)
        fileMenu.addAction(self.newAct)

        fileMenu.addMenu(self.impMenu)

        button = QPushButton('AddTask', self)
        button.move(fileMenu.width(), 0)
        button.clicked.connect(self.addRow)

        button = QPushButton('Distribute', self)
        button.move(2 * button.width(), 0)
        button.clicked.connect(self.fillAssigner)
        pass

    def showDialog(self):
        # fName = "issues.csv"
        fName = QFileDialog.getOpenFileName('Open file', '/home', )[0]
        print(fName)
        split_name = [str(fName).split(':')]
        self.ontology(split_name[0], split_name[1])
        '''
        with open(fName, "r") as f_obj:
            csv_reader(f_obj)
        
        f = open(fname, 'r')
        with f:
            data = f.read()
            self.textEdit.setText(data)
        '''

    # -------- Create Table ----------------------
    # format onto domain
    def str_date(self, data):
        return datetime.strptime(str(data), '[bug.%Y-%m-%dT%H:%M:%S]')

    def str_onto(self, data):
        return re.findall(r'\w+', str(data))[1]  # search().group(0)

    # Set unique cells without editing for all row
    def create_item_flag(self, text):
        tableWidgetItem = QTableWidgetItem(text)
        tableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return tableWidgetItem

    # Get text for item from ontology
    def set_item_onto(self, i):
        # Convert onto date to datetime
        start_date = self.str_date(inst_task[i].start_doing)
        # Format onto domain to string without name of ontology
        domain = self.str_onto(inst_task[i].specialize)
        assign = self.str_onto(inst_task[i].is_assigned)
        # Fill the first line
        self.table.setItem(i, 0, self.create_item_flag(str(inst_task[i])))
        self.table.setItem(i, 1, self.create_item_flag(domain))
        self.table.setItem(i, 2, self.create_item_flag(str(start_date)))
        self.table.setItem(i, 3, self.create_item_flag(assign))
        pass

    def my_table(self):
        self.table.setColumnCount(4)  # Set three columns
        self.table.setRowCount(len(inst_task))  # and one row
        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "Domain", "Time_start", "Assigner"])
        # Set all cells/items at the table
        for i in range(len(inst_task)):
            self.set_item_onto(i)
            # Do the resize of the columns by content
            self.table.resizeColumnsToContents()
            self.grid_layout.addWidget(self.table, 0, 0)  # Adding the self.table to the grid

    # ------------ OPERATION ADD ROW --------------
    # Check new index for combobox cell - domain
    def selectionchange(self, combo):
        self.new_domain = combo
        print("combo index: %i" % combo)
        pass

    def addRow(self):
        # Add row to the end
        self.lastRow = self.table.rowCount()
        self.table.insertRow(self.lastRow)
        # insert DATE
        now_date = str(datetime.now())
        self.table.setItem(self.lastRow, 2, self.create_item_flag(now_date[:len(now_date) - 7]))
        # insert ASSIGN - empty
        self.table.setItem(self.lastRow, 3, self.create_item_flag(""))
        # insert combobox
        comboBox = QComboBox()
        comboBox.addItems(
            str(domain)  # ,'[bug.%s]')
            for domain in inst_domain)
        # comboBox.setCurrentIndex(0)
        self.table.setCellWidget(self.lastRow, 1, comboBox)
        # Add text for item. Not just widget
        self.table.setItem(self.lastRow, 1, QTableWidgetItem(comboBox.currentText()))
        # Event for combobox
        comboBox.currentIndexChanged.connect(self.selectionchange)
        # Remember new row at the ontology
        self.save_row(self.lastRow)
        pass

    def fillAssigner(self):
        assigner = ""
        # ---------Check selected domain or from last added row-----
        curRow = self.table.currentRow()
        # выделена ли строка. Узнать через len
        selI = self.table.selectionModel().selectedIndexes()
        # Check last added row when none selected row or
        # selected row already have assigner
        fill_row = self.lastRow \
            if (len(selI) == 0 and self.table.item(curRow, 3) is not None) else curRow
        # Find assign to this domain. Select all of them
        k_as = [-1 for i in range(len(inst_people))]  # coef for
        new_domain = self.table.item(fill_row, 1)
        for i in inst_people:
            if (new_domain == d for d in i.know):
                assigner = i
                k_as[i] += 1
                print("who", assigner)
        # проверка по времени тек.задачи
        for i in inst_people:
            if k_as[i] > 1:
                last_task = [max(i.assigned.end_doing)]
                if self.str_date(self.table.item(fill_row, 2)) < \
                        self.str_date(last_task.end_doing):
                    k_as[i] += 1

        self.table.setItem(curRow, 3, QTableWidgetItem(assigner))  # str(inst_people[0])
        # else:

    def save_row(self, new_row):
        inst_task[new_row].append()
        self.bug_onto.Task(inst_task[new_row])
        self.bug_onto.People(inst_people[new_row])
        inst_task[new_row].is_assigned.append(inst_people[new_row])

        self.bug_onto.Domain(inst_domain[new_row])
        inst_people[new_row].know.append(inst_domain[new_row])
        inst_task[new_row].specialize.append(inst_domain[new_row])

        self.bug_onto.Date(self.table.item(new_row, 4).text())
        inst_task[new_row].start_doing.append(inst_people[new_row])
        pass

    def save_owl(self):

        self.bug_onto.save()
        # get an OWL string for a given ontology
        # print(to_owl(self.bug_onto))
        pass

    def ontology(self, fileName=None, dir=None):
        onto_path.append("C://Users/newLenovo/Desktop/prog")
        '''
        if (fileName is None):
            bug_onto = get_ontology("http://test.org/bug.owl").load()
        else:
            path = str(dir)+"//"
            onto_path.append(path)
        bug_onto = get_ontology("file:.{}".format(fileName)).load()
        '''
        for i in self.bug_onto.Domain.instances():
            inst_domain.append(i)
        for i in self.bug_onto.People.instances():
            inst_people.append(i)
        for i in self.bug_onto.Task.instances():
            inst_task.append(i)
        self.my_table()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
