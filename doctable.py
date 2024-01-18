import sys
import traceback
import psycopg2
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QMessageBox, \
    QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, pyqtSlot
import subprocess


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('User Table')
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Number of columns, including the button column
        self.table.setHorizontalHeaderLabels(['FILE NAME', 'DOCUMENT TYPE', 'DATE TIME', 'ACTION'])

        # Search box layout
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search')
        self.search_box.textChanged.connect(self.populate_table)
        search_layout.addWidget(self.search_box)

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Set the selection behavior to select entire rows
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.populate_table()

    def populate_table(self, search_text=None):
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            # Create a cursor object
            cursor = conn.cursor()

            # Fetch document records from the "DOCUMENT" table
            query = "SELECT DOC_FILENAME, DOC_TYPE, DOC_DATECREATED, DOC_FILEDATA FROM DOCUMENT"
            parameters = []
            if search_text:
                query += " WHERE DOC_FILENAME LIKE %s OR DOC_TYPE LIKE %s"
                parameters.append(f"%{search_text}%")
                parameters.append(f"%{search_text}%")

            cursor.execute(query, parameters)
            document_records = cursor.fetchall()

            # Set the number of rows in the table
            self.table.setRowCount(len(document_records))

            for row, record in enumerate(document_records):
                # Populate the table cells with data
                for col, value in enumerate(record[:3]):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 3:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, item)

                # Add the view file button
                view_file_button = QPushButton('View File')
                file_binary = record[3]
                view_file_button.clicked.connect(lambda _, binary=file_binary: self.view_file(binary))
                self.table.setCellWidget(row, 3, view_file_button)

            # Close the database connection
            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            # Handle the error
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()

        finally:
            # Close the cursor and connection
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def view_file(self, binary):
        # Save the binary data to a file
        filename = 'temp_file'
        with open(filename, 'wb') as file:
            file.write(binary)

        # Open the file with the default application
        try:
            if sys.platform == 'win32':
                subprocess.run(['start', filename], shell=True)
            else:
                subprocess.run(['xdg-open', filename])
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Unable to open the file.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table_widget = TableWidget()
    table_widget.show()
    sys.exit(app.exec())
