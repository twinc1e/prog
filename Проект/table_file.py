from datetime import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QComboBox


class MyTable:
    def __init__(self, my_onto, parent):
        self.my_onto = my_onto
        self.table = QTableWidget(parent)  # Create a table
        self.new_rows = []
        self.dom_combotxt = None
        self.prior_combotxt = None
        self.table.setMinimumSize(QSize(750, 120))  # Set sizes
        self.table.setWindowTitle("TasktrackerOnto")  # Set the window title
        central_widget = QWidget(parent)  # Create a central widget
        parent.setCentralWidget(central_widget)  # Install the central widget

        self.grid_layout = QGridLayout(parent)  # Create QGridLayout
        central_widget.setLayout(self.grid_layout)  # Set this layout in central widget
        self.my_table(my_onto.inst_task)

    # Get text for item from ontology
    def set_item_onto(self, i, task):
        # Fill the first line
        self.table.setItem(i, 0, self.create_item_flag(task[0]))
        self.table.setItem(i, 1, self.create_item_flag(task[1]))
        self.table.setItem(i, 2, self.create_item_flag(task[2]))
        self.table.setItem(i, 3, self.create_item_flag(task[3]))
        self.table.setItem(i, 4, self.create_item_flag(task[4]))
        self.table.setItem(i, 5, self.create_item_flag(task[5]))
        # self.table.setItem(i, 6, self.create_item_flag(priority))
        # self.table.setItem(i, 5, self.create_item_flag(duration))
        pass

    # -------- Create Table ----------------------
    def my_table(self, tasks):
        self.table.setSortingEnabled(True)
        self.table.setColumnCount(6)  # Set 6 columns
        self.table.setRowCount(len(tasks))  # and one row
        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "Domain", "Time_start", "Assigner", "Time_end", "Priority"])
        # Set all cells/items at the table
        for i in range(len(tasks)):
            self.set_item_onto(i, self.my_onto.item_onto(i))
            # Do the resize of the columns by content
            self.table.resizeColumnsToContents()
            self.grid_layout.addWidget(self.table, 0, 0)  # Adding the self.table to the grid

    # ------------ OPERATION ADD ROW --------------
    # Check new text for combobox cell - domain
    def add_Row(self):
        # Add row to the end
        lastRow = self.table.rowCount()
        self.table.insertRow(lastRow)
        self.table.scrollToBottom()  # (0, self.table.height())
        # insert task
        self.table.setItem(lastRow, 0, QTableWidgetItem("New task"))
        # insert DATE
        now_date = str(datetime.now())
        future_date = str(datetime.now() + timedelta(days=3))
        self.table.setItem(lastRow, 2, self.create_item_flag(now_date[:len(now_date) - 7]))
        self.table.setItem(lastRow, 4, QTableWidgetItem(future_date[:len(now_date) - 7]))
        # insert ASSIGN - empty
        self.table.setItem(lastRow, 3, self.create_item_flag(""))
        '''# DURATION - empty => after enter end_time calculate one
        self.table.setItem(lastRow, 5, self.create_item_flag(""))
        self.table.cellChanged.connect(self.cellchanged)
        '''
        self.combo_domain(lastRow)
        self.combo_priority(lastRow)

        self.new_rows.append(lastRow)

    # ------------ OPERATION ADD ROW --------------
    # Check new text for combobox cell - domain
    def dselectionchange(self, combotext):
        self.dom_combotxt = combotext
        print("combo txt: %s" % combotext)
        # Add text for item. Not just widget
        self.table.setItem(self.table.currentRow(), 1, QTableWidgetItem(self.dom_combotxt))
        pass

    # Check new text for combobox cell - priority
    def pselectionchange(self, combotext):
        self.prior_combotxt = combotext
        print("combo txt: %s" % combotext)
        # Add text for item. Not just widget
        self.table.setItem(self.table.currentRow(), 5, QTableWidgetItem(self.prior_combotxt))
        pass

    def combo_domain(self, row):
        # insert combobox
        comboBox = QComboBox()
        comboBox.addItems(
            str(self.my_onto.str_onto(domain))
            for domain in self.my_onto.inst_domain)
        # comboBox.setCurrentIndex(0)
        self.table.setCellWidget(row, 1, comboBox)
        self.dom_combotxt = comboBox.currentText()
        # Event for combobox
        comboBox.currentTextChanged.connect(self.dselectionchange)
        # Add text for item. Not just widget
        self.table.setItem(row, 1, QTableWidgetItem(self.dom_combotxt))

    def combo_priority(self, row):
        # insert combobox for priority
        p_comboBox = QComboBox()
        p_comboBox.addItems(
            str(self.my_onto.str_onto(priority))
            for priority in self.my_onto.inst_priority)
        # comboBox.setCurrentIndex(0)
        self.table.setCellWidget(row, 5, p_comboBox)
        self.prior_combotxt = p_comboBox.currentText()
        # Event for combobox
        p_comboBox.currentTextChanged.connect(self.pselectionchange)
        # Add text for item. Not just widget
        self.table.setItem(row, 5, QTableWidgetItem(self.prior_combotxt))

    # Set unique cells without editing for all row
    @staticmethod
    def create_item_flag(text):
        tableWidgetItem = QTableWidgetItem(text)
        tableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return tableWidgetItem
