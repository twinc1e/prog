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
inst_priority = []
inst_role = []  # unuseful


class MainWindow(QMainWindow):

    # Override class constructor
    def __init__(self):
        # You must call the super class method
        QMainWindow.__init__(self)

        self.menu_bar = self.menuBar()
        self.newAct = QAction('Save', self)
        self.impAct = QAction('owl', self)
        self.impMenu = QMenu('Import', self)
        dirname = os.path.dirname(__file__)
        onto_path.append(dirname)  # ("C://Users/newLenovo/Desktop/prog")
        self.bug_onto = get_ontology("http://test.org/bug.owl/").load()

        '''
        for i in self.bug_onto.Priority.instances():
            self.inst_prior = {i.is_same_as: i}
        for i in self.bug_onto.Role.instances():
            self.inst_role = {i.is_same_as: i}
        '''
        self.table = QTableWidget(self)  # Create a table
        self.dom_combotxt = None
        self.prior_combotxt = None
        self.setMinimumSize(QSize(750, 120))  # Set sizes
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
        return datetime.strptime(str(data), '%Y-%m-%d %H:%M:%S')  # %Y-%m-%dT%H:%M:%S

    # format onto domain
    def str_odate(self, data):
        try:
            odate = datetime.strptime(str(data), 'bug.%d.%m.%YT%H-%M-%S')
        except ValueError:
            odate = datetime.strptime(str(data), '[bug.%d.%m.%YT%H-%M-%S]')

        return odate

    # get nice string from onto without onto class
    def str_onto(self, data):
        try:  # r - подавляют экранирование строки ("Сырые" строки)
            ostr = re.split(r'\.', str(data), maxsplit=1)[1]  # search.group(0)  # findall([^.]+$)[0]
        except IndexError or AttributeError:
            ostr = str(data)
        return ostr

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
        priority = self.str_onto(inst_task[i].have_priority)

        # Fill the first line
        self.table.setItem(i, 0, self.create_item_flag(task))
        self.table.setItem(i, 1, self.create_item_flag(domain))
        self.table.setItem(i, 2, self.create_item_flag(str(start_date)))
        self.table.setItem(i, 3, self.create_item_flag(assign))
        self.table.setItem(i, 4, self.create_item_flag(str(end_date)))
        self.table.setItem(i, 5, self.create_item_flag(priority))
        # self.table.setItem(i, 6, self.create_item_flag(priority))
        # self.table.setItem(i, 5, self.create_item_flag(duration))
        pass

    def my_table(self):
        self.table.setColumnCount(6)  # Set 6 columns
        self.table.setRowCount(len(inst_task))  # and one row
        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "Domain", "Time_start", "Assigner", "Time_end", "Priority"])
        # Set all cells/items at the table
        for i in range(len(inst_task)):
            self.set_item_onto(i)
            # Do the resize of the columns by content
            self.table.resizeColumnsToContents()
            self.grid_layout.addWidget(self.table, 0, 0)  # Adding the self.table to the grid
        self.lastRow = -1

    # ------------ OPERATION ADD ROW --------------
    # Check new text for combobox cell - domain
    def dselectionchange(self, combotext):
        self.dom_combotxt = combotext
        print("combo txt: %s" % combotext)
        # Add text for item. Not just widget
        self.table.setItem(self.table.currentRow(), 1, QTableWidgetItem(self.dom_combotxt))
        pass

    # ------------ OPERATION ADD ROW --------------
    # Check new text for combobox cell - domain
    def pselectionchange(self, combotext):
        self.prior_combotxt = combotext
        print("combo txt: %s" % combotext)
        # Add text for item. Not just widget
        self.table.setItem(self.table.currentRow(), 5, QTableWidgetItem(self.prior_combotxt))
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
    # I want to set messagebox
    '''
    def mousePressEvent(self, *args, **kwargs):
        self.ao.own_signal.emit()
        self.close()
    def set_params(self,res,event):
        self.ao = self.AddRow
        self.ao.own_signal.connect(self.on_clicked)
        self.setGeometry(200,200)
        self.setWindowTitle("Result Message")
        self.text()
        self.show()
        '''

    def resultWindow(self, res):
        info = QMessageBox()
        info.setIcon(QMessageBox.Information)
        info.about(self, "Result Message", res)
        pass

    def addRow(self):
        # Add row to the end
        self.lastRow = self.table.rowCount()
        self.table.insertRow(self.lastRow)
        self.table.scrollToBottom()  # (0, self.table.height())
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
        self.dom_combotxt = comboBox.currentText()
        # Event for combobox
        comboBox.currentTextChanged.connect(self.dselectionchange)
        # Add text for item. Not just widget
        self.table.setItem(self.lastRow, 1, QTableWidgetItem(self.dom_combotxt))

        # insert combobox for priority
        p_comboBox = QComboBox()
        p_comboBox.addItems(
            str(self.str_onto(priority))
            for priority in inst_priority)
        # comboBox.setCurrentIndex(0)
        self.table.setCellWidget(self.lastRow, 5, p_comboBox)
        self.prior_combotxt = p_comboBox.currentText()
        # Event for combobox
        p_comboBox.currentTextChanged.connect(self.pselectionchange)
        # Add text for item. Not just widget
        self.table.setItem(self.lastRow, 5, QTableWidgetItem(self.prior_combotxt))

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
            if (len(selI) == 0 or self.table.item(curRow, 3) is not None) else curRow
        if fill_row == -1:
            self.resultWindow("Add task, please")
            return
        # ----------------------------------------------------------------
        # create coefficient which match task to people - searching assigner
        k_as = [0 for i in range(len(inst_people))]
        # get domain from new task
        new_domain = self.table.item(fill_row, 1)
        domain = next(
            (d for d in inst_domain if new_domain.text() == d.name),
            None)
        # get name of priority from new task
        new_prior = self.table.item(fill_row, 5)
        # get element from ontology which match name with cell from table
        priority = next(
            (p for p in inst_priority if new_prior.text() == p.name),
            None)
        n_day = []
        for i in inst_people:
            print(f"person {i}")
            # -------- Find assign to this domain. Select all of them
            for d in i.know:
                if domain == d:
                    k_as[inst_people.index(i)] += 1
                    print(f"who have domain")
            # if k_as[i] > 0:  #just for people which match with needed domain
            # -------- Check by priority-----
            for r in priority.related_to:
                if i.is_role_of[0] == r:
                    k_as[inst_people.index(i)] += 1
                    print(f"who have qualification")
            # ------------Check by date-----------------
            # determine date of last task of i_people
            if len(i.assigned) != 0:
                for pt in i.assigned:  # pt - people's task
                    # for ot in inst_task:#ot - from all tasks
                    end_date_task = pt.end_doing  # if self.str_onto(pt) == self.str_onto(ot) else 0)
                    # is the i_people free? how much time?
                    # datetime.now() - end_date_task = j.end_doing
                    start_date_cur_t = self.str_date(self.table.item(fill_row, 2).text())
                    days_date = start_date_cur_t - self.str_odate(end_date_task)
                    n_day.append(days_date.days)
                    print(f"how much days {n_day}")
                last_task = min(n_day)
                n_day.clear()
            # Remember person which finished task (end_date)
            print(f'v--- have free day {last_task}')
            if last_task >= 0 or len(i.assigned) == 0:
                k_as[inst_people.index(i)] += 1
                print(f"who is free")

            print(f"coef = {k_as[inst_people.index(i)]}")

        # Remember index from max number of array k_as
        win_as = k_as.index(max(k_as))
        # если все истина, то записать в область допустимых
        all_win_as = k_as.count(max(k_as))
        if all_win_as > 1:
            res = f"more than one assigner {all_win_as}"
            print(res)  # +str(inst_people[index_with_max_coef].name)
        elif all_win_as == 0:
            res = "No one can be assigner"
        else:
            res = f"assigner - {inst_people[win_as]}"
        self.table.setItem(fill_row, 3, QTableWidgetItem(str(inst_people[win_as].name)))  # str(inst_people[0])
        self.resultWindow(res)

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

    def min_role(self, priority):
        role = inst_role[0]  # junior
        min_rol = 5
        for i in priority.related_to:
            if i.is_same_as < min_rol:
                role = i
                min_rol = i.is_same_as
        return role

    def max_prior(self, priors):
        max_pr = 0
        prior = inst_priority[3]  # urgent
        for i in priors:
            if i.is_same_as > max_pr:
                prior = i
                max_pr = i.is_same_as
        return prior

    # set roles for people
    def role_of_pers(self, pers):
        # pers doesn't have tasks
        if len(pers.assigned) == 0:
            print(pers, 0)
            return inst_role[0]
        # all priorities's tasks by pers
        pr_task_i = [who.have_priority for who in pers.assigned]
        if len(pers.assigned) > 1:
            print(pers, pr_task_i, len(pers.assigned))
        # who has higher weight of priority
        pr_i = self.max_prior(pr_task_i)
        # who has less weight of role
        role = self.min_role(pr_i)
        print(pers,' is ',role, ' role')
        return role

    def ontology(self, fileName=None, dir=None):
        '''
        if (fileName is None):
            bug_onto = get_ontology("http://test.org/bug.owl").load()
        else:
            path = str(dir)+"//"
            onto_path.append(path)
        bug_onto = get_ontology("file:.{}".format(fileName)).load()
        '''
        for i in self.bug_onto.Task.instances():
            inst_task.append(i)
        for i in self.bug_onto.Domain.instances():
            inst_domain.append(i)
        for i in self.bug_onto.Priority.instances():
            inst_priority.append(i)
        for i in self.bug_onto.Role.instances():
            inst_role.append(i)
        # отсортируем список ролей по уровням, а не по алфавиту.
        # В д.случае лидера в конец.
        # остальные правильно построены
        # inst_role.insert(len(inst_role), inst_role.pop(1))
        # Junior, Middle, Senior, Lead

        for i in self.bug_onto.People.instances():
            i.is_role_of.append(self.role_of_pers(i))
            inst_people.append(i)

        self.my_table()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
