import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAction, QMenu, QPushButton, QFileDialog, \
    QMessageBox
from Проект.ontology_file import MyOntology
from Проект.deap_file import myGAoptimize
from Проект.table_file import MyTable


class MainWindow(QMainWindow):

    # Override class constructor
    def __init__(self):
        # You must call the super class method
        QMainWindow.__init__(self)

        self.menu_bar = self.menuBar()
        self.newAct = QAction('Save', self)
        self.impAct = QAction('owl', self)
        self.impMenu = QMenu('Import', self)
        self.myO = MyOntology("http://test.org/bug.owl/")
        self.myT = MyTable(self.myO, self)
        self.my_window()

    # unify elements of task from row to ontology
    @staticmethod
    def cell_to_onto(new_cell, arr):
        # get domain/priority from new task
        return next(
            (_ for _ in arr if new_cell == _.name),
            None)
    @staticmethod
    def cor_url_code(text = ""):
        if "%20" in text:
            text.replace("%20","_")
        return text
    # one task from row put in array to save it
    def arr_task(self, row):
        return [self.cor_url_code(self.myT.table.item(row, 0).text()),
                self.cell_to_onto(self.myT.table.item(row, 1).text(),
                                  self.myO.inst_domain),
                self.myT.table.item(row, 2).text(),
                self.cell_to_onto(self.myT.table.item(row, 3).text(),
                                  self.myO.inst_people),
                self.myT.table.item(row, 4).text(),
                self.cell_to_onto(self.myT.table.item(row, 5).text(),
                                  self.myO.inst_priority)]

    # show message box window
    def result_Window(self, res):
        info = QMessageBox()
        info.setIcon(QMessageBox.Information)
        info.about(self, "Result Message", res)
        pass

    def my_window(self):
        # создает строку меню
        fileMenu = self.menu_bar.addMenu('File')

        self.impAct.setShortcut('Ctrl+O')
        self.impAct.setStatusTip('Open new File')
        self.impAct.triggered.connect(self.show_Dialog)
        self.impMenu.addAction(self.impAct)

        self.newAct.triggered.connect(self.all_save)
        fileMenu.addAction(self.newAct)

        fileMenu.addMenu(self.impMenu)

        button = QPushButton('AddTask', self)
        button.move(fileMenu.width(), 0)
        button.clicked.connect(self.myT.add_Row)

        button = QPushButton('Distribute', self)
        button.move(2 * button.width(), 0)
        button.clicked.connect(self.distribute)  # fillAssigner)

    # ------------ operations on menu  ------------
    def show_Dialog(self):
        fName = QFileDialog.getOpenFileName(self, "Open file", "/home",
                                            "Ontology editor (*.owl *.rdf)")[0]
        if fName == '':
            pass
        else:
            print(fName)
            # https://www.geeksforgeeks.org/python-os-path-split-method/
            split_name = os.path.split(fName)
            self.myO = MyOntology(split_name[1], "file:/" + split_name[0])
            self.myT.my_table(self.myO.inst_task)

    def all_save(self):
        try:
            self.myO.save_owl()
            self.result_Window("Successfully save to owl")
        except Exception:
            self.result_Window("Cannot save to owl. Please,try later.")

    # ------------add ROW and DISTRIBUTE------------
    def add_rez_in_table(self, row, winner):
        # add to the table
        self.myT.table.setItem(row, 3,
                               QTableWidgetItem(winner))
        print(f"Assigner in cell {row} - {self.myT.table.item(row, 3).text()}")

    # if select and enter on row
    def printResultForRow(self, fill_row, weights):
        print(f"in row {fill_row}")
        # если все истина, то записать в область допустимых
        if weights.count(3) == 0:
            res = "No one can be assigner"
        else:
            # using enumerate() + list comprehension
            # range deletion of elements
            all_win = [i for i, x in enumerate(weights) if x == 3]

            self.add_rez_in_table(fill_row, self.myO.inst_people[all_win[0]].name)

            if weights.count(3) > 1:
                res = f"more than one assigner: {len(all_win)}"
            else:
                res = f"assigner - {self.myO.inst_people[all_win[0]].name}"
            print(f"\n people for task\n\t{[self.myO.inst_people[win].name for win in all_win]}")
        print(f"task {self.myT.table.item(fill_row, 0).text()}")
        self.result_Window(res)
        pass

    # Remember new row at the ontology and array
    def save_row(self, row):
        onto_task = self.myO.update_onto(self.arr_task(row))
        self.myO.inst_task = [onto_task]

    def fillAssigner(self, last_row):
        # ---------Check selected domain or from last added row-----
        curRow = self.myT.table.currentRow()
        # выделена ли строка. Узнать через len
        selI = self.myT.table.selectionModel().selectedIndexes()
        # Check last added row when none selected row or
        # selected row already have assigner
        fill_row = last_row \
            if (len(selI) == 0 or self.myT.table.item(curRow, 3).text() is not "") else curRow
        if fill_row == -1:
            self.result_Window("Add task, please")
            pass
        weights = self.myO.weights(self.myO.item_onto(fill_row))
        self.printResultForRow(fill_row, weights)
        pass

    def optimize_tasks(self, tasks):
        # result GA optimization
        assigners = myGAoptimize(self.myO, tasks).main()
        optim_tasks = list()
        # add to table
        for i_t, t in enumerate(tasks):
            i = self.myO.inst_task.index(t)
            self.add_rez_in_table(i, self.myO.str_onto(assigners[i_t]))
            optim_tasks.append(i)
        # update onto
        self.myO.new_task.clear()
        for i in optim_tasks:
            self.save_row(i)

    def distribute(self):
        for row in self.myT.new_rows:
            self.save_row(row)
        # tasks to distribute
        noptimize_tasks = self.myO.new_task
        if len(noptimize_tasks) == 0:
            self.result_Window("All tasks have assigners. Add new tasks.")
        elif len(noptimize_tasks) == 1:
            self.fillAssigner(noptimize_tasks)
        else:
            self.optimize_tasks(noptimize_tasks)
            self.result_Window("Check result of the distribution")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
