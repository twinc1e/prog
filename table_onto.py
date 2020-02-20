# from PyQt5 import QtWidgets
from datetime import datetime

from PyQt5.QtGui import QKeyEvent
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

        self.menu_bar = self.menuBar()
        self.newAct = QAction('Save', self)
        self.impAct = QAction('owl', self)
        self.impMenu = QMenu('Import', self)

        onto_path.append("C://Users/newLenovo/Desktop/prog")
        self.bug_onto = get_ontology("http://test.org/bug.owl/").load()
        self.table = QTableWidget(self)  # Create a table
        self.new_domain = 0
        self.setMinimumSize(QSize(512, 120))  # Set sizes
        self.setWindowTitle("TasktrackerOnto")  # Set the window title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Install the central widget

        self.grid_layout = QGridLayout(self)  # Create QGridLayout
        central_widget.setLayout(self.grid_layout)  # Set this layout in central widget

        self.ontology()
        self.my_window()

    def my_window(self):
        # создает строку меню
        fileMenu = self.menu_bar.addMenu('File')

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
        return datetime.strptime(str(data), '%Y-%m-%d %H:%M:%S')
    # format onto domain
    def str_odate(self, data):
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
        start_date = self.str_odate(inst_task[i].start_doing)
        end_date = self.str_odate(inst_task[i].end_doing)
        # duration = (end_date-start_date).days
        # Format onto domain to string without name of ontology
        task = self.str_onto(inst_task[i])
        domain = self.str_onto(inst_task[i].specialize)
        assign = self.str_onto(inst_task[i].is_assigned)
        # Fill the first line
        self.table.setItem(i, 0, self.create_item_flag(task))
        self.table.setItem(i, 1, self.create_item_flag(domain))
        self.table.setItem(i, 2, self.create_item_flag(str(start_date)))
        self.table.setItem(i, 3, self.create_item_flag(assign))
        self.table.setItem(i, 4, self.create_item_flag(str(end_date)))
        # self.table.setItem(i, 5, self.create_item_flag(duration))
        pass

    def my_table(self):
        self.table.setColumnCount(5)  # Set 6 columns
        self.table.setRowCount(len(inst_task))  # and one row
        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "Domain", "Time_start", "Assigner", "Time_end"])
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

    # override keyPressEvent
    '''
    def keyPressEvent(self, e: QKeyEvent) -> None:
            if e.key() == Qt.Key_Enter:
                print("Key enter was pressed")
            elif e.key() == Qt.Key_Return:
                print("Key return was pressed")
    
    def cellchanged(self):
        try:
            if self.table.currentColumn() == 4:
                row = self.table.currentRow()
                txt_duration = (self.table.item(row, 4)-self.table.item(row, 2)).days
                self.table.item(row, 5).setText(txt_duration)
        except:
            pass
    '''

    def addRow(self):
        # Add row to the end
        self.lastRow = self.table.rowCount()
        self.table.insertRow(self.lastRow)
        # insert DATE
        now_date = str(datetime.now())
        self.table.setItem(self.lastRow, 2, self.create_item_flag(now_date[:len(now_date) - 7]))
        # insert ASSIGN - empty
        self.table.setItem(self.lastRow, 3, self.create_item_flag(""))
        '''# DURATION - empty => after enter end_time calculate one
        self.table.setItem(self.lastRow, 5, self.create_item_flag(""))
        self.table.cellChanged.connect(self.cellchanged)
        '''
        # insert combobox
        comboBox = QComboBox()
        comboBox.addItems(
            str(self.str_onto(domain))
            for domain in inst_domain)
        # comboBox.setCurrentIndex(0)
        self.table.setCellWidget(self.lastRow, 1, comboBox)
        # Add text for item. Not just widget
        self.table.setItem(self.lastRow, 1, QTableWidgetItem(comboBox.currentText()))
        # Event for combobox
        comboBox.currentIndexChanged.connect(self.selectionchange)
        # Remember new row at the ontology
        # self.save_row(self.lastRow)
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
        k_as = [0 for i in range(len(inst_people))]  # coef for
        new_domain = self.table.item(fill_row, 1)
        for i in inst_people:
            if (new_domain == d for d in i.know):
                assigner = i
                k_as[inst_people.index(i)] += 1
                print(f"who {assigner}")
        # проверка по времени тек.задачи
        n_day=[]
        for i in range(len(inst_people)):
            if k_as[i] > 0:
                # Get end date of everyone's tasks
                task_as = [inst_people[i].assigned]
                #pt - people's task ot - onto of task
                for pt in task_as:
                    end_date_task = next(
                        (ot.end_doing for ot in inst_task
                            if self.str_onto(pt) == self.str_onto(ot)),
                        None)
                    #datetime.now() - end_date_task = j.end_doing
                    start_date_cur_t = self.str_date(self.table.item(fill_row, 2).text())
                    days_date = start_date_cur_t - self.str_odate(end_date_task)
                    n_day.append(days_date.days)
                last_task = min(n_day)
                # Remember person which finished task (end_date)
                print(f' vs end date {inst_people[i]} last task {last_task}')
                if last_task >= 0:
                    k_as[i] += 1
        # Remember index from max number of array k_as
        win_as = k_as.index(max(k_as))
        # если все истина, то записать в область допустимых
        # правила вынести отдельно. Вдруг потом поменяются
        if k_as.count(max(k_as)) > 1: print("more than one assigner")
        self.table.setItem(curRow, 3, QTableWidgetItem(str(inst_people[win_as])))  # str(inst_people[0])

    def save_row(self, new_row):
        # docs send for article
        # ontology пособие характеристика. Для сложности. низк., сред., выс.

        inst_task[new_row].append(self.table.item(new_row, 0).text())
        inst_domain[new_row].append(self.table.item(new_row, 1).text())
        inst_people[new_row].append(self.table.item(new_row, 3).text())
        self.bug_onto.Task(inst_task[new_row])
        self.bug_onto.People(inst_people[new_row])
        inst_task[new_row].is_assigned.append(inst_people[new_row])

        self.bug_onto.Domain(inst_domain[new_row])
        inst_people[new_row].know.append(inst_domain[new_row])
        inst_task[new_row].specialize.append(inst_domain[new_row])

        start_date = self.bug_onto.Date(self.table.item(new_row, 2).text())
        end_date = self.bug_onto.Date(self.table.item(new_row, 4).text())
        inst_task[new_row].start_doing.append(start_date)
        inst_task[new_row].end_doing.append(end_date)
        pass

    def save_owl(self):
        self.bug_onto.save()
        # get an OWL string for a given ontology
        # print(to_owl(self.bug_onto))
        pass

    def ontology(self, fileName=None, dir=None):
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
