import sys
import traceback

import psycopg2
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QMessageBox, \
    QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('User Table')
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Number of columns, including the button column
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Gender', 'Date Registered','Action'])

        # Set the selection behavior to select entire rows
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

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

        self.populate_table()  # Populate the table initially

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
            # Construct the query with search parameter
            query = "SELECT RES_ID, RES_FNAME || ' ' || RES_LNAME AS NAME, RES_GENDER, RES_DATEREGISTERED FROM RESIDENT"
            parameters = []
            if search_text:
                query += " WHERE RES_FNAME LIKE %s OR RES_LNAME LIKE %s"
                parameters.append(f"%{search_text}%")
                parameters.append(f"%{search_text}%")
            cursor.execute(query, parameters)
            user_records = cursor.fetchall()



            # Set the number of rows in the table
            self.table.setRowCount(len(user_records))

            for row, record in enumerate(user_records):
                # Populate the table cells with data
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 3:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, col, item)

                # Add the view profile button
                view_profile_button = QPushButton('View Profile')
                view_profile_button.clicked.connect(lambda _, user_id=record[0]: self.view_profile(user_id))
                self.table.setCellWidget(row, 4, view_profile_button)

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

    def onSelectionChanged(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            item = self.table.item(selected_row, 0)  # Selecting the id in column 0
            user_id = int(item.text())  # getting the value of that column
            self.view_profile(user_id)

    def view_profile(self, user_id):
        QMessageBox.information(self, "Success", f"View profile of user with ID: {user_id}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table_widget = TableWidget()
    table_widget.show()
    sys.exit(app.exec())
