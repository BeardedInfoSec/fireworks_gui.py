import sys
import random
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt

class FireworkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Firework Sequencer')
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QGridLayout()
        self.layout.addLayout(self.form_layout)

        self.name_label = QLabel('Name:')
        self.form_layout.addWidget(self.name_label, 0, 0)
        self.name_input = QLineEdit()
        self.form_layout.addWidget(self.name_input, 0, 1)

        self.runtime_label = QLabel('Run Time (s):')
        self.form_layout.addWidget(self.runtime_label, 0, 2)
        self.runtime_input = QLineEdit()
        self.form_layout.addWidget(self.runtime_input, 0, 3)

        self.type_label = QLabel('Type:')
        self.form_layout.addWidget(self.type_label, 0, 4)
        self.type_input = QComboBox()
        self.type_input.addItems(['Main Event', 'Grand Finale'])
        self.form_layout.addWidget(self.type_input, 0, 5)

        self.add_button = QPushButton('Add Firework')
        self.add_button.clicked.connect(self.add_firework)
        self.form_layout.addWidget(self.add_button, 1, 1, 1, 2)

        self.remove_button = QPushButton('Remove Firework')
        self.remove_button.clicked.connect(self.remove_firework)
        self.form_layout.addWidget(self.remove_button, 1, 3, 1, 2)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'Run Time', 'Type', 'Sequence Number'])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Auto expand the "Sequence Number" column
        self.table.setColumnWidth(0, 200)  # Set the "Name" column width
        self.layout.addWidget(self.table)

        self.randomize_button = QPushButton('Randomize Main Event Order')
        self.randomize_button.clicked.connect(self.randomize_main_event)
        self.layout.addWidget(self.randomize_button)

        self.total_main_label = QLabel('Total Main Event Time: 0:00')
        self.layout.addWidget(self.total_main_label)

        self.total_grand_label = QLabel('Total Grand Finale Time: 0:00')
        self.layout.addWidget(self.total_grand_label)

        self.total_run_time_label = QLabel('Total Run Time: 0:00')
        self.layout.addWidget(self.total_run_time_label)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.load_show_button = QPushButton('Load Show')
        self.load_show_button.clicked.connect(self.load_show)
        self.button_layout.addWidget(self.load_show_button)

        self.save_button = QPushButton('Save Show')
        self.save_button.clicked.connect(self.save_show)
        self.button_layout.addWidget(self.save_button)

        self.total_main_time = 0
        self.total_grand_time = 0
        self.current_sequence_number = 1

    def load_show(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Load Show', '', 'JSON Files (*.json)')
        if file_name:
            with open(file_name, 'r') as file:
                data = json.load(file)
                self.new_show()
                for item in data['fireworks']:
                    self.add_firework_to_table(item['name'], item['runtime'], item['type'], item['sequence'])
                self.total_main_time = data['total_main_time']
                self.total_grand_time = data['total_grand_time']
                self.current_sequence_number = len(data['fireworks']) + 1
                self.total_main_label.setText(f'Total Main Event Time: {self.format_time(self.total_main_time)}')
                self.total_grand_label.setText(f'Total Grand Finale Time: {self.format_time(self.total_grand_time)}')
                self.update_total_run_time()

    def save_show(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Show', '', 'JSON Files (*.json)')
        if file_name:
            fireworks = []
            for row in range(self.table.rowCount()):
                name = self.table.item(row, 0).text()
                runtime = float(self.table.item(row, 1).text().split(':')[0]) * 60 + float(self.table.item(row, 1).text().split(':')[1])
                f_type = self.table.item(row, 2).text()
                sequence = int(self.table.item(row, 3).text())
                fireworks.append({'name': name, 'runtime': runtime, 'type': f_type, 'sequence': sequence})
            data = {
                'fireworks': fireworks,
                'total_main_time': self.total_main_time,
                'total_grand_time': self.total_grand_time
            }
            with open(file_name, 'w') as file:
                json.dump(data, file, indent=4)

    def new_show(self):
        self.table.setRowCount(0)
        self.total_main_time = 0
        self.total_grand_time = 0
        self.current_sequence_number = 1
        self.total_main_label.setText('Total Main Event Time: 0:00')
        self.total_grand_label.setText('Total Grand Finale Time: 0:00')
        self.total_run_time_label.setText('Total Run Time: 0:00')

    def add_firework(self):
        name = self.name_input.text()
        runtime = self.runtime_input.text()
        f_type = self.type_input.currentText()

        if not name or not runtime:
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields.')
            return

        try:
            runtime = float(runtime)
        except ValueError:
            QMessageBox.warning(self, 'Input Error', 'Run Time must be a number.')
            return

        self.add_firework_to_table(name, runtime, f_type, self.current_sequence_number)

        if f_type == 'Main Event':
            self.total_main_time += runtime
            self.total_main_label.setText(f'Total Main Event Time: {self.format_time(self.total_main_time)}')
        else:
            self.total_grand_time += runtime
            self.total_grand_label.setText(f'Total Grand Finale Time: {self.format_time(self.total_grand_time)}')

        self.update_total_run_time()

        self.current_sequence_number += 1

        self.name_input.clear()
        self.runtime_input.clear()

    def add_firework_to_table(self, name, runtime, f_type, sequence):
        current_rows = self.table.rowCount()
        self.table.insertRow(current_rows)
        self.table.setItem(current_rows, 0, QTableWidgetItem(name))
        self.table.setItem(current_rows, 1, QTableWidgetItem(self.format_time(runtime)))
        self.table.setItem(current_rows, 2, QTableWidgetItem(f_type))
        self.table.setItem(current_rows, 3, QTableWidgetItem(str(sequence)))

    def remove_firework(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            runtime = self.table.item(selected_row, 1).text().split(':')
            runtime = float(runtime[0]) * 60 + float(runtime[1])
            f_type = self.table.item(selected_row, 2).text()

            if f_type == 'Main Event':
                self.total_main_time -= runtime
                self.total_main_label.setText(f'Total Main Event Time: {self.format_time(self.total_main_time)}')
            else:
                self.total_grand_time -= runtime
                self.total_grand_label.setText(f'Total Grand Finale Time: {self.format_time(self.total_grand_time)}')

            self.table.removeRow(selected_row)
            self.update_total_run_time()
        else:
            QMessageBox.warning(self, 'Selection Error', 'Please select a firework to remove.')

    def randomize_main_event(self):
        main_event_rows = [row for row in range(self.table.rowCount()) if self.table.item(row, 2).text() == 'Main Event']
        random.shuffle(main_event_rows)

        all_rows = []
        for sequence, row in enumerate(main_event_rows, start=1):
            row_data = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
            row_data[3] = str(sequence)  # Update sequence number
            all_rows.append(row_data)

        grand_finale_rows = [row for row in range(self.table.rowCount()) if self.table.item(row, 2).text() == 'Grand Finale']
        for row in grand_finale_rows:
            row_data = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
            all_rows.append(row_data)

        self.table.setRowCount(0)
        for row_data in all_rows:
            current_rows = self.table.rowCount()
            self.table.insertRow(current_rows)
            for col, item in enumerate(row_data):
                self.table.setItem(current_rows, col, QTableWidgetItem(item))

    def update_total_run_time(self):
        total_run_time = self.total_main_time + self.total_grand_time
        self.total_run_time_label.setText(f'Total Run Time: {self.format_time(total_run_time)}')

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f'{minutes}:{seconds:02}'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FireworkApp()
    ex.show()
    sys.exit(app.exec_())
