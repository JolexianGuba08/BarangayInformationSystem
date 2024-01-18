import subprocess
from datetime import datetime, date
import sys
import traceback

from datetime import datetime, timedelta

import cv2
import psycopg2
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTime, QDate, QTimer, Qt, QFileInfo
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QPushButton, QTableWidgetItem, \
    QComboBox, QLineEdit, QLabel, QFileDialog, QInputDialog, QTabWidget, QAbstractButton
from PyQt6.uic import loadUi
from pyexpat import model

from main import HomepageWindow


def widget_function(frame):
    widget.addWidget(frame)
    widget.setCurrentIndex(widget.currentIndex() + 1)

adminId = 10095

def insert_history(res_id, description, staff_id):
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="bis",
        user="postgres",
        password="posgre"
    )

    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Get the current timestamp
        current_time = datetime.now()

        # Insert a new record into the HISTORY table
        insert_query = "INSERT INTO HISTORY (RES_ID, HIST_DESCRIPTION, HIST_DATE, STAFF_ID) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (res_id, description, current_time, staff_id))

        # Commit the transaction
        conn.commit()

        print("Record inserted successfully into HISTORY table.")

    except (Exception, psycopg2.Error) as error:
        # Handle the error
        print("Error while connecting to PostgreSQL or inserting into HISTORY table:", error)

    finally:
        # Close the cursor and connection
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

class AdminCreateAccountWindow(QMainWindow):
    def __init__(self):
        super(AdminCreateAccountWindow, self).__init__()
        loadUi("ui_admin/admin_create_account.ui", self)
        adminpicture = self.admin_picture
        adminname = self.admin_name

        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button
        residentsbutton.clicked.connect(self.go_resident)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)

        self.view_staff_button.clicked.connect(self.view_staff)

        headerdate = self.header_date
        headertime = self.header_time

        firstnameinput = self.firstname_input
        lastnameinput = self.lastname_input
        usernameinput = self.username_input
        passwordinput = self.password_input
        confirmpasswordinput = self.confirm_password_input
        self.logout_button.clicked.connect(self.go_logout)
        self.line_edits = {
            'firstname_input': self.firstname_input,
            'lastname_input': self.lastname_input,
            'username_input': self.username_input,
            'password_input': self.password_input,
            'confirm_password_input': self.confirm_password_input
        }

        self.create_account_btn.clicked.connect(self.validate_resident_input)



    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def validate_resident_input(self):
        line_edit_values = [line_edit.text().strip() for line_edit in self.line_edits.values()]



        # Check if all values are non-empty
        if not all(line_edit_values):
            QMessageBox.warning(self, "Invalid Input", "Please fill in all the required fields.")
            return

        username = self.username_input
        if self.checkusername(username) == True:
            QMessageBox.warning(self, "Invalid Input", "This username is already exist. ")
            return

        password = self.line_edits.get("password_input")
        conf_password = self.line_edits.get("confirm_password_input")
        if password.text() != conf_password.text():
            QMessageBox.warning(self, "Invalid Input", "Password and confirmation do not match")
            return

        # All validations passed
        QMessageBox.information(self, "Message", "Saving Staff's Information.....")
        QTimer.singleShot(1000, self.submit_form)

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

    def checkusername(self,username):
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )

        try:
            # Create a cursor object
            cursor = conn.cursor()

            # Retrieve the existing resident information based on the resident ID
            select_query = "SELECT * FROM STAFF WHERE STAFF_USERNAME = %(username)s"
            cursor.execute(select_query, {'username': username.text()})
            resident_data = cursor.fetchone()

            if resident_data:
                return True
            else:
                return False
        except (Exception, psycopg2.Error) as error:
            # Handle the error
            print("Error while connecting to PostgreSQL:", error)

        finally:
            # Close the cursor and connection
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def submit_form(self):
        firstname_input = self.line_edits['firstname_input'].text().strip()
        lastname_input = self.line_edits['lastname_input'].text().strip()
        username_input = self.line_edits['username_input'].text().strip()
        password_input = self.line_edits['password_input'].text().strip()


        datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        staff_isadmin = False
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            # Create a cursor object
            cursor = conn.cursor()

            insert_query = "INSERT INTO STAFF (STAFF_USERNAME, STAFF_PASSWORD, STAFF_FNAME, STAFF_LNAME, STAFF_DATECREATED, " \
                           "STAFF_ISADMIN) VALUES (%(username)s, %(password)s, %(fname)s, %(lname)s, %(datecreated)s, %(isadmin)s)"

            resident_data = {
                'username': username_input,
                'password': password_input,
                'fname': firstname_input,
                'lname': lastname_input,
                'datecreated': datecreated,
                'isadmin': staff_isadmin,

            }

            # Execute the insert query
            cursor.execute(insert_query, resident_data)
            conn.commit()

            # Show success message
            QMessageBox.information(self, "Success", "Staff's information successfully saved!")
            #insert history
            admin_create_account = AdminCreateAccountWindow()
            widget_function(admin_create_account)

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


    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.adminname.setText(staff_fname + " " + staff_lname)


    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_documents(self):
        admin_documents = AdminDocumentsWindow()
        widget_function(admin_documents)

    def go_officials(self):
        admin_officials = AdminOfficialsWindow()
        widget_function(admin_officials)

    def go_transaction(self):
        activity_log = AdminActivityLogWindow()
        widget_function(activity_log)

    def go_notes(self):
        admin_notes = AdminNotesWindow()
        widget_function(admin_notes)

    def view_staff(self):
        admin_view_staff = AdminViewStaffWindow()
        widget_function(admin_view_staff)

class AdminViewStaffWindow(QMainWindow):
    def __init__(self):
        super(AdminViewStaffWindow, self).__init__()
        loadUi("ui_admin/admin_view_staff.ui", self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        adminpicture = self.admin_picture
        adminname = self.admin_name
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        headerdate = self.header_date
        headertime = self.header_time
        searchstaff = self.search_staff
        cancelbutton = self.cancel_button
        stafftable = self.staff_table
        backbutton = self.back_button
        self.search_staff.textChanged.connect(self.populate_table)
        self.staff_table.setColumnCount(4)  # Number of columns, including the button column
        self.staff_table.setHorizontalHeaderLabels(['STAFF ID', 'STAFF USERNAME', 'STAFF NAME', 'DATE CREATED'])
        self.staff_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.staff_table.cellDoubleClicked.connect(self.onCellDoubleClicked)
        self.populate_table()
        backbutton.clicked.connect(self.back)
        self.logout_button.clicked.connect(self.go_logout)
        self.cancel_button.clicked.connect(self.cancelClicked)

    def cancelClicked(self):
        self.search_staff.setText("")

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

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
            query = "SELECT STAFF_ID, STAFF_USERNAME , STAFF_FNAME || ' ' || STAFF_LNAME AS NAME, STAFF_DATECREATED FROM STAFF WHERE STAFF_ISADMIN = 'False'"
            parameters = []

            if search_text:
                query += " AND STAFF_FNAME ILIKE %s OR STAFF_LNAME ILIKE %s OR (STAFF_FNAME || ' ' || STAFF_LNAME) ILIKE %s OR CAST(STAFF_ID AS TEXT) ILIKE %s ORDER BY STAFF_ID DESC"
                parameters.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])

            cursor.execute(query, parameters)
            user_records = cursor.fetchall()

            # Set the number of rows in the table
            self.staff_table.setRowCount(len(user_records))

            for row, record in enumerate(user_records):
                # Populate the table cells with data
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 4:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.staff_table.setItem(row, col, item)
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

    def onCellDoubleClicked(self, row, column):
        if column == 0:  # Check if the ID column was double-clicked
            item = self.staff_table.item(row, column)
            user_id = int(item.text())
            self.userid = user_id
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Icon.Question)
            message_box.setText(f"Delete Staff id: {user_id}?")
            message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            message_box.setDefaultButton(QMessageBox.StandardButton.No)
            button_clicked = message_box.exec()

            if button_clicked == QMessageBox.StandardButton.Yes:
                # Perform the update operation
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="bis",
                        user="postgres",
                        password="posgre"
                    )
                    cursor = conn.cursor()

                    # Update document data in the "DOCUMENT" table
                    query = "DELETE FROM staff WHERE staff_id = %s"
                    parameters = (user_id,)

                    cursor.execute(query, parameters)
                    conn.commit()

                    cursor.close()
                    conn.close()

                    QMessageBox.information(self, "Message", "Staff has been deleted successfully")
                    self.populate_table()

                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL:", error)
                    traceback.print_exc()

            else:
                pass

    def back(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

class AdminResidentWindow(QMainWindow):
    def __init__(self):
        super(AdminResidentWindow, self).__init__()
        loadUi("ui_admin/admin_residents.ui", self)

        self.userid = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        adminpicture = self.admin_picture
        adminname = self.admin_name

        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button


        self.cancel_button.clicked.connect(self.cancelClicked)
        self.search_resident.textChanged.connect(self.populate_table)
        self.resident_table.setColumnCount(5)
        self.resident_table.setHorizontalHeaderLabels(['ID','Name', 'Gender', 'Date Registered', 'Action'])
        self.resident_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.resident_table.cellDoubleClicked.connect(self.onCellDoubleClicked)

       
        self.update_button.clicked.connect(self.update_resident)
        self.update_button.setEnabled(False)
        createaccountbutton.clicked.connect(self.go_create_account)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)
        self.populate_table()

        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def delete_selected_row(self):
        selected_row = self.resident_table.currentRow()
        if selected_row >= 0:
            # Get the resident ID from the selected row
            item = self.resident_table.item(selected_row, 0)
            resident_id = int(item.text())
            message_box = QMessageBox()
            message_box.setWindowTitle("Confirmation")
            message_box.setIcon(QMessageBox.Icon.Question)
            message_box.setText(f"Do you want to delete this resident ?{resident_id}")
            message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            message_box.setDefaultButton(QMessageBox.StandardButton.No)
            button_clicked = message_box.exec()


            if button_clicked == QMessageBox.StandardButton.Yes:
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
                    # Construct the query to delete the resident
                    query = "UPDATE RESIDENT SET RES_ISREMOVED = %s WHERE RES_ID = %s"
                    cursor.execute(query, (True,resident_id,))
                    conn.commit()
                    # Show a success message
                    QMessageBox.information(self, "Success", f"Resident ID: {resident_id} has been deleted.")
                    insert_history(resident_id, "Deleted Resident", adminId)
                    # Refresh the table
                    self.populate_table()

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
        else:
            pass
            QMessageBox.warning(self, "No Row Selected", "Please select a row to delete.")

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

    def cancelClicked(self):
        self.search_resident.setText("")

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
            query = "SELECT RES_ID, RES_FNAME || ' ' || RES_LNAME AS NAME, RES_GENDER, RES_DATEREGISTERED FROM RESIDENT WHERE RES_ISREMOVED = 'False'"
            parameters = []

            if search_text:
                query += " AND RES_FNAME ILIKE %s OR RES_LNAME ILIKE %s OR (RES_FNAME || ' ' || RES_LNAME) ILIKE %s OR CAST(RES_ID AS TEXT) ILIKE %s"
                parameters.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            query += "ORDER BY res_id DESC"
            cursor.execute(query, parameters)
            user_records = cursor.fetchall()

            # Set the number of rows in the table
            self.resident_table.setRowCount(len(user_records))

            for row, record in enumerate(user_records):
                # Populate the table cells with data
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 4:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.resident_table.setItem(row, col, item)

                # Add the view profile button
                view_profile_button = QPushButton('View Profile')
                view_profile_button.clicked.connect(lambda _, user_id=record[0]: self.view_profile(user_id))
                self.resident_table.setCellWidget(row, 4, view_profile_button)

            # Close the database connection
            cursor.close()
            conn.close()
            self.delete_button.clicked.connect(self.delete_selected_row)

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

    def onCellDoubleClicked(self, row, column):
        if column == 0:  # Check if the ID column was double-clicked
            item = self.resident_table.item(row, column)
            user_id = int(item.text())
            self.userid = user_id
            self.update_button.setEnabled(True)
            QMessageBox.information(self, "Message", f"Update resident profile resident id: {user_id}?")

    def view_profile(self, user_id):
        QMessageBox.information(self, "Success", f"View resident profile of resident id: {user_id}")
        resident_view_resident = AdminViewResidentWindow()
        resident_view_resident.get_residentinfo(user_id)
        widget_function(resident_view_resident)


    def cancelClicked(self):
        self.search_resident.setText("")

    def go_create_account(self):
        create_account = AdminCreateAccountWindow()
        widget_function(create_account)

    def go_documents(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_documents()

    def go_officials(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_officials()

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

    def update_resident(self):
        admin_update_resident = AdminUpdateResidentWindow(self.userid)
        admin_update_resident.load_resident_info()
        widget_function(admin_update_resident)

class AdminUpdateResidentWindow(QMainWindow):
    def __init__(self,residentid):
        super(AdminUpdateResidentWindow, self).__init__()
        loadUi("ui_admin/admin_update_resident.ui", self)
        self.resident_id = residentid
        adminpicture = self.admin_picture
        adminname = self.admin_name
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        self.line_edits = {
            'firstname_input': self.firstname_input,
            'lastname_input': self.lastname_input,
            'middlename_input': self.middlename_input,
            'suffix_input': self.suffix_input,
            'gender_input': self.gender_input.currentText(),
            'citizenship_input': self.citizenship_input,
            'civil_status_input': self.civil_status_input.currentText(),
            'bday_input': self.bday_input.date().toString("yyyy-MM-dd"),
            'religion_input': self.religion_input,
            'addressline_input': self.addressline_input,
            'barangay_input': self.barangay_input,
            'city_input': self.city_input,
            'region_input': self.region_input,
            'occupation_input': self.occupation_input,
            'contact_number_input': self.contact_number_input,
            'email_address_input': self.email_address_input,
            'place_of_birth_input': self.place_of_birth_input
        }

        backbtn = self.back_button
        self.save_resident_button.clicked.connect(self.save_changes)
        createaccountbutton.clicked.connect(self.go_create_account)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)
        backbtn.clicked.connect(self.back)
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def capture_image(self):
        try:
            # Create a VideoCapture object to read from the webcam
            cap = cv2.VideoCapture(0)

            # Check if the webcam is opened successfully
            if not cap.isOpened():
                print("Unable to access the webcam.")
                return

            # Create a window for displaying the live video feed
            cv2.namedWindow("Live Feed")

            while True:
                # Read a frame from the webcam
                ret, frame = cap.read()

                # Display the frame in the "Live Feed" window
                cv2.imshow("Live Feed", frame)

                # Check for key press to capture the face
                if cv2.waitKey(1) == ord(' '):
                    # Save the captured frame as an image file
                    self.add_resident_image_file = "captured_face.jpg"
                    cv2.imwrite(self.add_resident_image_file, frame)
                    self.validate_resident_input()
                    break

                # Check for key press to exit capturing
                if cv2.waitKey(1) == ord('q'):
                    break

        except Exception as e:
            # Handle the error
            print("Error capturing image:", e)
            traceback.print_exc()

        finally:
            # Release the VideoCapture object and close the display windows
            cap.release()
            cv2.destroyAllWindows()

    def load_resident_info(self):
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )

        try:
            # Create a cursor object
            cursor = conn.cursor()

            # Retrieve the existing resident information based on the resident ID
            select_query = f"SELECT * FROM RESIDENT WHERE res_id = {self.resident_id}"
            cursor.execute(select_query)
            resident_data = cursor.fetchone()

            if resident_data:
                # Set the placeholders for the line fields
                self.firstname_input.setText(resident_data[1])
                self.lastname_input.setText(resident_data[2])
                self.middlename_input.setText(resident_data[3])
                self.suffix_input.setText(resident_data[4])
                self.citizenship_input.setText(resident_data[8])
                self.religion_input.setText(resident_data[11])
                self.addressline_input.setText(resident_data[12])
                self.barangay_input.setText(resident_data[13])
                self.city_input.setText(resident_data[14])
                self.region_input.setText(resident_data[15])
                self.occupation_input.setText(resident_data[16])
                self.contact_number_input.setText(resident_data[17])
                self.email_address_input.setText(resident_data[18])
                self.place_of_birth_input.setText(resident_data[10])
                dob = resident_data[9]
                if dob:
                    dob_date = QDate(dob.year, dob.month, dob.day)
                    self.bday_input.setDate(dob_date)

                # Set the placeholder for gender dropdown
                gender_index = self.gender_input.findText(resident_data[6])
                if gender_index != -1:
                    self.gender_input.setCurrentIndex(gender_index)

                # Set the placeholder for civil status dropdown
                civil_status_index = self.civil_status_input.findText(resident_data[7])
                if civil_status_index != -1:
                    self.civil_status_input.setCurrentIndex(civil_status_index)

                # Set the rest of the placeholders for line fields


            else:
                # Handle the case when resident data is not found
                QMessageBox.warning(self, "Invalid Resident", "Resident data not found.")
                self.close()

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

    def save_changes(self):
        # Get the user's input
        firstname = self.firstname_input.text()
        lastname = self.lastname_input.text()
        middlename = self.middlename_input.text()
        suffix = self.suffix_input.text()
        citizenship = self.citizenship_input.text()
        religion = self.religion_input.text()
        addressline = self.addressline_input.text()
        barangay = self.barangay_input.text()
        city = self.city_input.text()
        region = self.region_input.text()
        occupation = self.occupation_input.text()
        contact_number = self.contact_number_input.text()
        email_address = self.email_address_input.text()
        place_of_birth = self.place_of_birth_input.text()
        gender = self.gender_input.currentText()
        civil_status = self.civil_status_input.currentText()
        dob = self.bday_input.date().toPyDate()

        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )

        try:
            # Create a cursor object
            cursor = conn.cursor()

            # Update the resident information in the database based on the resident ID

            update_query = """
            UPDATE RESIDENT SET
            res_fname = %s,
            res_lname = %s,
            res_mname = %s,
            res_suffix = %s,
            res_citizenship = %s,
            res_religion = %s,
            res_addressline = %s,
            res_barangay = %s,
            res_city = %s,
            res_region = %s,
            res_occupation = %s,
            res_mobilenumber = %s,
            res_email = %s,
            res_pob = %s,
            res_gender = %s,
            res_civilstatus = %s,
            res_dob = %s,
            res_dateupdated = CURRENT_TIMESTAMP
            WHERE res_id = %s

            """
            cursor.execute(update_query, (
                firstname, lastname, middlename, suffix, citizenship, religion,
                addressline, barangay, city, region, occupation, contact_number,
                email_address, place_of_birth, gender, civil_status, dob, self.resident_id
            ))

            # Commit the changes to the database
            conn.commit()

            QMessageBox.information(self, "Success", "Resident information updated successfully.")
            insert_history(self.resident_id, "Updated Resident", adminId)
            self.go_resident()



        except (Exception, psycopg2.Error) as error:
            # Handle the errors
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()
            QMessageBox.warning(self, "Error", "An error occurred while updating resident information.")

        finally:
            # Close the cursor and connection
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def validate_resident_input(self):
        line_edit_values = [line_edit.text().strip() for line_edit in self.line_edits.values() if
                            isinstance(line_edit, QLineEdit)]
        combo_box_values = [combo_box.currentText() for combo_box in self.line_edits.values() if
                            isinstance(combo_box, QComboBox)]

        email_address = self.email_address_input.text().strip()
        calendar_value = self.bday_input.date().toString("yyyy-MM-dd")  # Corrected code

        input_values = line_edit_values + combo_box_values + [email_address, calendar_value]

        # Additional validation for mobile number and middle name
        mobile_number = self.contact_number_input.text().strip()
        middle_name = self.middlename_input.text().strip()

        # Check if all values are non-empty
        if not all(input_values):
            QMessageBox.warning(self, "Invalid Input", "Please fill in all the required fields.")
            return

        # Check if mobile number contains only numbers
        if not mobile_number.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Mobile number should contain numbers only.")
            return

        # Check if middle name contains only a single word
        if len(middle_name.split()) != 1:
            QMessageBox.warning(self, "Invalid Input", "Middle name should contain a single word.")
            return

        # Check if the selected values are the default values in the dropdown menus
        default_gender = ["Male", "Female"]
        default_civil_status = ["Single", "Married", "Widowed", "Divorced"]
        selected_gender = self.gender_input.currentText()
        selected_civil_status = self.civil_status_input.currentText()

        if selected_gender not in default_gender or selected_civil_status not in default_civil_status:
            QMessageBox.warning(self, "Invalid Input", "Please select a value from the dropdown menus.")
            return

        # All validations passed
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText("Do you want to save changes?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        button_clicked = message_box.exec()

        if button_clicked == QMessageBox.StandardButton.Yes:
            self.save_changes()
        else:
            pass
    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_documents(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_documents()

    def go_officials(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_officials()

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

    def back(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_resident()

class AdminDocumentsWindow(QMainWindow):
    def __init__(self):
        super(AdminDocumentsWindow, self).__init__()
        loadUi("ui_admin/admin_documents.ui", self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        adminpicture = self.admin_picture
        adminname = self.admin_name
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button
        headerdate = self.header_date
        headertime = self.header_time
        self.file_label = QLabel(self)
        self.search_document.textChanged.connect(self.populate_table)

        self.file_label.setGeometry(20, 20, 360, 180)
        self.document_table.setColumnCount(6)  # Number of columns, including the button column
        self.document_table.setHorizontalHeaderLabels(['FILE NAME', 'DOCUMENT TYPE', 'DATE TIME','RESIDENT NAME','STAFF USERNAME', 'ACTION'])
        self.document_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.document_table.cellDoubleClicked.connect(self.onCellClicked)
        self.populate_table()



        createaccountbutton.clicked.connect(self.go_create_account)
        residentsbutton.clicked.connect(self.go_resident)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def generate_filename(self, res_id, doc_type):
        filename = f"document_{res_id}.{doc_type}"
        return filename

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

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
            query = """
                SELECT d.DOC_FILENAME, d.DOC_TYPE, d.DOC_DATECREATED, r.RES_FNAME || ' ' || r.RES_LNAME AS RESIDENT_NAME, s.STAFF_USERNAME,d.DOC_FILEDATA
                FROM DOCUMENT d
                JOIN RESIDENT r ON d.RES_ID = r.RES_ID
                JOIN STAFF s ON d.STAFF_ID = s.STAFF_ID
                WHERE d.DOC_ISREMOVED = %s
                
            """
            parameters = [False]
            if search_text:
                query += " AND (d.DOC_FILENAME ILIKE %s OR d.DOC_TYPE ILIKE %s)"
                parameters.append(f"%{search_text}%")
                parameters.append(f"%{search_text}%")
            query += " ORDER BY DOC_ID DESC"
            cursor.execute(query, parameters)
            document_records = cursor.fetchall()

            # Set the number of rows in the table
            self.document_table.setRowCount(len(document_records))

            for row, record in enumerate(document_records):
                # Populate the table cells with data
                for col, value in enumerate(record[:5]):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 5:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.document_table.setItem(row, col, item)

                # Add the view file button
                view_file_button = QPushButton('View File')
                file_binary = record[5]
                view_file_button.clicked.connect(lambda _, binary=file_binary: self.view_file(binary))
                self.document_table.setCellWidget(row, 5, view_file_button)


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

    def onCellClicked(self, row, column):
        if column == 5:  # Assuming the action column is column 3
            view_file_button = self.document_table.cellWidget(row, column)
            if view_file_button is not None:
                binary_item = view_file_button.property("binary_data")
                if binary_item is not None:
                    self.binary_data = binary_item
                    self.update_document_button.setEnabled(True)

        elif column == 0:  # Assuming the ID column is column 0
            item = self.document_table.item(row, column)
            file_name = item.text()
            # Retrieve the binary data associated with the file name
            binary_data = self.retrieve_binary_data(file_name)
            if binary_data is not None:
                self.binary_data = binary_data
                QMessageBox.information(self, "Message", f"You select {file_name}")
                self.update_document()

    def retrieve_binary_data(self, file_name):
        # Connect to the database and retrieve the binary data for the given file name
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DOC_FILEDATA FROM DOCUMENT WHERE DOC_FILENAME = %s", (file_name,))
            record = cursor.fetchone()
            if record:
                binary_data = record[0]
                return binary_data
            else:
                QMessageBox.warning(self, "Warning", "Binary data not found for the selected file.")
                return None
        except (Exception, psycopg2.Error) as error:
            QMessageBox.critical(self, "Error", f"Error retrieving binary data: {str(error)}")
            traceback.print_exc()
            return None
        finally:
            cursor.close()
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

    def update_document(self):
        # Check if a row is selected and binary data is available
        if self.binary_data is not None:
            # Display a confirmation message box
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Icon.Question)
            message_box.setText("Are you sure you want to delete the document?")
            message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            message_box.setDefaultButton(QMessageBox.StandardButton.No)
            button_clicked = message_box.exec()

            if button_clicked == QMessageBox.StandardButton.Yes:
                # Perform the update operation
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="bis",
                        user="postgres",
                        password="posgre"
                    )
                    cursor = conn.cursor()

                    # Retrieve the resident ID associated with the document
                    query = "SELECT RES_ID FROM DOCUMENT WHERE DOC_FILEDATA = %s"
                    cursor.execute(query, (self.binary_data,))
                    resident_id = cursor.fetchone()[0]

                    # Update document data in the "DOCUMENT" table
                    query = "UPDATE DOCUMENT SET DOC_ISREMOVED = %s WHERE DOC_FILEDATA = %s"
                    insert_history(resident_id, "Removed Document", adminId)
                    parameters = (True, self.binary_data)

                    cursor.execute(query, parameters)
                    conn.commit()

                    cursor.close()
                    conn.close()

                    QMessageBox.information(self, "Message", "Document has been deleted successfully")
                    create_account = AdminCreateAccountWindow()
                    create_account.go_documents()

                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL:", error)
                    traceback.print_exc()

            else:
                pass

        else:
            QMessageBox.warning(self, "Warning", "Please choose a row before updating the document.")
        # REDIRECT TO SOMETHING


    def go_create_account(self):
        admin_create_account = AdminCreateAccountWindow()
        widget_function(admin_create_account)

    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_officials(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_officials()

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

class AdminOfficialsWindow(QMainWindow):
    def __init__(self):
        super(AdminOfficialsWindow, self).__init__()
        loadUi("ui_admin/admin_officials.ui", self)

        self.admin_picture = self.admin_picture
        self.admin_name = self.admin_name

        self.create_account_button = self.create_account_button
        self.residents_button = self.residents_button
        self.documents_button = self.documents_button
        self.officials_button = self.officials_button
        self.transactions_button = self.transactions_button
        self.notes_button = self.notes_button
        self.logout_button = self.logout_button

        def create_callback(official_title):
            return lambda: self.select_official(official_title)

        officials = [("Captain", self.captain_img, self.captain_display, self.add_captain_button),
                     ("Secretary", self.secretary_img, self.secretary_display, self.add_secretary_button),
                     ("Treasurer", self.treasurer_img, self.treasurer_display, self.add_treasurer_button)] + \
                    [(f"Councilor {i + 1}", getattr(self, f"councilor_img{i + 1}"),
                      getattr(self, f"councilor_display_{i + 1}"), getattr(self, f"add_councilor_button{i + 1}")) for i
                     in range(8)]

        for official_title, img_label, display_label, add_button in officials:
            self.set_official_image_and_name(img_label, display_label, official_title)
            add_button.clicked.connect(create_callback(official_title))
        self.create_account_button.clicked.connect(self.go_create_account)
        self.residents_button.clicked.connect(self.go_resident)
        self.documents_button.clicked.connect(self.go_documents)
        self.transactions_button.clicked.connect(self.go_transaction)
        self.notes_button.clicked.connect(self.go_notes)
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def set_official_image_and_name(self, image_label, name_label, official_title):
        image_data = self.get_official_image(official_title)
        if image_data:
            image = QImage.fromData(image_data)
            pixmap = QPixmap.fromImage(image)
            image_label.setPixmap(pixmap)

        official_name = self.get_official_name(official_title)
        if official_name:
            name_label.setText(official_name)

    def get_official_image(self, official_title):
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            select_query = """
                SELECT res_picture
                FROM resident
                INNER JOIN official ON resident.res_id = official.res_id
                WHERE official.off_title = %s and res_isofficial = 'true' and official.off_isremoved = 'false'
            """
            cursor.execute(select_query, (official_title,))
            result = cursor.fetchone()
            if result:
                image_data = result[0]
                return image_data
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return None

    def get_official_name(self, official_title):
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            select_query = """
                SELECT res_fname || ' ' || res_lname
                FROM resident
                INNER JOIN official ON resident.res_id = official.res_id
                WHERE official.off_title = %s and res_isofficial = 'true' and official.off_isremoved = 'false'
            """
            cursor.execute(select_query, (official_title,))
            result = cursor.fetchone()
            if result:
                return result[0]
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return None

    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_resident(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_resident()

    def go_documents(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_documents()

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

    def select_official(self,title):
        select_official = AdminSelectOfficialsWindow(title)
        widget_function(select_official)

class AdminSelectOfficialsWindow(QMainWindow):
    def __init__(self, official_title):
        super(AdminSelectOfficialsWindow, self).__init__()
        loadUi("ui_admin/admin_select_officials.ui", self)
        self.official_tittle = official_title
        print(self.official_tittle)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()

        adminpicture = self.admin_picture
        adminname = self.admin_name
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        headerdate = self.header_date
        headertime = self.header_time
        searchresident = self.search_resident
        cancelbutton = self.cancel_button
        residenttable = self.resident_table
        self.search_resident.textChanged.connect(self.populate_table)
        self.resident_table.setColumnCount(4)
        self.resident_table.setHorizontalHeaderLabels(['ID', 'Name', 'Gender', 'Action'])
        backbutton = self.back_button
        self.populate_table()

        createaccountbutton.clicked.connect(self.go_create_account)
        residentsbutton.clicked.connect(self.go_resident)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)
        backbutton.clicked.connect(self.back)
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def cancelClicked(self):
        self.search_resident.setText("")

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
            query = """
                            SELECT DISTINCT RESIDENT.RES_ID, RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME AS NAME, RESIDENT.RES_GENDER 
                            FROM RESIDENT WHERE RES_ISREMOVED = %s 

                        """

            parameters = [False]
            if search_text:
                query += " AND (RESIDENT.RES_FNAME ILIKE %s OR RESIDENT.RES_LNAME ILIKE %s OR (RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME) ILIKE %s OR CAST(RESIDENT.RES_ID AS TEXT) I" \
                         "ILIKE %s)"
                parameters.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])

            query += " ORDER BY RESIDENT.RES_ID DESC"
            cursor.execute(query, parameters)
            user_records = cursor.fetchall()

            # Set the number of rows in the table
            self.resident_table.setRowCount(len(user_records))

            current_official_id = self.get_current_official_id()  # Get the ID of the current official
            current_official_index = None

            for row, record in enumerate(user_records):
                # Populate the table cells with data
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 3:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.resident_table.setItem(row, col, item)

                # Add the select button
                select_button = QPushButton()
                user_id = record[0]
                is_official = self.check_official_status(user_id, self.official_tittle)
                if is_official:
                    select_button.setText('Deselect')
                    current_official_index = row
                else:
                    select_button.setText('Select')

                select_button.clicked.connect(lambda _, user_id=user_id: self.select_official(user_id))
                self.resident_table.setCellWidget(row, 3, select_button)

                # Disable the button if it's not the current official
                if current_official_id and user_id != current_official_id:
                    select_button.setEnabled(False)

            for row in range(self.resident_table.rowCount()):
                item = self.resident_table.cellWidget(row, 0)  # Get the widget in the desired column
                if row == current_official_index:
                    item.setStyleSheet("background-color: green;")  # Set the desired background color
                else:
                    item.setStyleSheet("")  # Reset the background color for other rows

            # Move the selected row to the top
            if current_official_index is not None:
                self.resident_table.insertRow(0)
                for col in range(self.resident_table.columnCount()):
                    item = self.resident_table.takeItem(current_official_index + 1, col)
                    self.resident_table.setItem(0, col, item)

                # Remove the original row after moving
                self.resident_table.removeRow(current_official_index + 1)

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


    def get_current_official_id(self):
        # Connect to the database and get the ID of the current official for the specific official title
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            query = """
                SELECT res_id
                FROM official
                WHERE off_title = %s AND off_isremoved = %s
            """
            cursor.execute(query, (self.official_tittle, False))
            row = cursor.fetchone()
            if row:
                return row[0]  # Return the ID if the current official exists
            else:
                return None  # Return None if the current official does not exist
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
            return None
        finally:
            if conn is not None:
                conn.close()

    def select_official(self, user_id):
        title = self.official_tittle
        is_official = self.check_official_status(user_id, title)

        if is_official:
            self.deselect_official(user_id)
            QMessageBox.information(self, "Success", "Official deselected successfully.")
            self.populate_table()  # Refresh the table
        else:
            # Deselect the current official for the specific title
            self.deselect_current_official(title)
            # Select the new official
            official = self.check_current_official(user_id)
            if not official:
                self.insert_official(user_id)
                QMessageBox.information(self, "Success", f"User selected as {title}.")
                self.populate_table()  # Refresh the table
            else:
                res_tittle = self.get_resident_title(user_id)
                QMessageBox.information(self, "Error Message", f"Unable, Resident {user_id} is already an {res_tittle}.")

    def get_resident_title(self,resident_id):
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
            query = """
                SELECT off_title
                FROM official
                WHERE res_id = %s and off_isremoved = %s 
            """
            cursor.execute(query, (resident_id,False))
            row = cursor.fetchone()
            if row:
                return row[0]  # Return the title if it exists
            else:
                return None  # Return None if the resident is not an official
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
        finally:
            # Close the cursor and connection
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def check_current_official(self, user_id):
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*)
                FROM Resident
                WHERE res_id = %s AND res_isofficial = %s
            """
            cursor.execute(query, (user_id,True))
            row = cursor.fetchone()
            count = row[0]
            return count > 0
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return False

    def check_official_status(self, user_id, official_title):
        # Connect to the database and check the is_admin status
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM official WHERE res_id = %s AND off_title = %s AND off_isremoved = %s"
            cursor.execute(query, (user_id, official_title,False))
            row = cursor.fetchone()
            is_official = row[0]
            if is_official > 0:
                return True
            else:
                return False
            cursor.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
        finally:
            if conn is not None:
                conn.close()

    def deselect_official(self, user_id):
        offtitle = self.official_tittle
        current_time = datetime.now()
        # Calculate the end term date by adding 3 years
        end_term = current_time + timedelta(days=365 * 3)
        is_removed = True
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            update_query = """
                UPDATE official
                SET off_isremoved = true
                WHERE off_title = %s AND res_id = %s
            """
            cursor.execute(update_query, (offtitle, user_id))

            update_query = """
                UPDATE resident
                SET res_isofficial = false
                WHERE res_id = %s
            """
            cursor.execute(update_query, (user_id,))

            select_query = """
                SELECT CONCAT(res_fname, ' ', res_lname)
                FROM resident
                WHERE res_id = %s
            """
            cursor.execute(select_query, (user_id,))
            name = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", f"{name}'s official status has been removed")

            # Update the button text to "Select" in the table
            self.update_button_text(user_id, "Select")

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()

        finally:
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def update_button_text(self, user_id, text):
        for row in range(self.resident_table.rowCount()):
            item = self.resident_table.item(row, 0)
            if item and int(item.text()) == user_id:
                button = self.resident_table.cellWidget(row, 3)
                if button:
                    button.setText(text)
                    break

    def deselect_current_official(self, title):
        # Connect to the database and deselect the current official of the given title
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            query = """
                UPDATE official
                SET off_isremoved = true
                WHERE off_title = %s
            """
            cursor.execute(query, (title,))
            conn.commit()
            cursor.close()
            conn.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()
        finally:
            if conn is not None:
                conn.close()

    def insert_official(self, user_id):
        offtitle = self.official_tittle
        current_time = datetime.now()
        # Calculate the end term date by adding 3 years
        end_term = current_time + timedelta(days=365 * 3)
        is_removed = False
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO official (off_title, off_startterm, off_endterm, off_isremoved, res_id, staff_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (offtitle, current_time, end_term, is_removed, user_id, adminId))

            update_query = """
                UPDATE resident
                SET res_isofficial = true
                WHERE res_id = %s
            """
            cursor.execute(update_query, (user_id,))

            select_query = """
                SELECT CONCAT(res_fname, ' ', res_lname)
                FROM resident
                WHERE res_id = %s
            """
            cursor.execute(select_query, (user_id,))
            name = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", f"{name} successfully set as {offtitle}.")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()

        finally:
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)



    def go_create_account(self):
        create_account = AdminCreateAccountWindow()
        widget_function(create_account)

    def go_resident(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_resident()

    def go_documents(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_documents()

    def go_officials(self):
        select_official = AdminSelectOfficialsWindow()
        widget_function(select_official)

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

    def back(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_officials()

class AdminActivityLogWindow(QMainWindow):
    def __init__(self):
        super(AdminActivityLogWindow, self).__init__()
        loadUi("ui_admin/admin_activity_log.ui", self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        adminpicture = self.admin_picture
        adminname = self.admin_name
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        headerdate = self.header_date
        headertime = self.header_time
        self.search_document.textChanged.connect(self.populate_table)
        self.cancel_button.clicked.connect(self.cancelClicked)
        documenttable = self.document_table
        self.document_table.setColumnCount(4)  # Number of columns, including the button column
        self.document_table.setHorizontalHeaderLabels(
            ['RESIDENT NAME', 'DESCRIPTION', 'DATE TIME', 'STAFF USERNAME'])
        createaccountbutton.clicked.connect(self.go_create_account)
        residentsbutton.clicked.connect(self.go_resident)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        notesbutton.clicked.connect(self.go_notes)
        self.select_type.currentTextChanged.connect(self.populate_table)

        self.populate_table()
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def cancelClicked(self):
        self.search_document.setText("")
        self.select_type.setCurrentIndex(-1)


    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_documents(self):
        admin_documents = AdminDocumentsWindow()
        widget_function(admin_documents)

    def go_officials(self):
        admin_officials = AdminOfficialsWindow()
        widget_function(admin_officials)

    def go_notes(self):
        admin_notes = AdminNotesWindow()
        widget_function(admin_notes)

    def populate_table(self, search_text=None):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()

            query = """
                SELECT RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME, HISTORY.HIST_DESCRIPTION,
                       HISTORY.HIST_DATE, STAFF.STAFF_USERNAME
                FROM HISTORY
                LEFT JOIN RESIDENT ON HISTORY.RES_ID = RESIDENT.RES_ID
                LEFT JOIN STAFF ON HISTORY.STAFF_ID = STAFF.STAFF_ID
                WHERE 1=1
            """
            parameters = []


            # Get the selected history type from the dropdown
            selected_type = self.select_type.currentText()
            print(selected_type)

            if selected_type and selected_type != "All":
                if selected_type == "Logged":
                    query += " AND HISTORY.HIST_DESCRIPTION IN ('Staff Login', 'Staff Logout')"  # Use 'WHERE' for filtering
                else:
                    query += " AND HISTORY.HIST_DESCRIPTION = %s"
                    parameters.append(selected_type)
                # Add search filter if search text is provided
                if search_text is not None:
                    query += " OR (RESIDENT.RES_FNAME ILIKE %s OR RESIDENT.RES_LNAME ILIKE %s OR (RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME) ILIKE %s)"
                    parameters.extend([f"%{search_text}%", f"%{search_text}%", search_text])
                else:
                    query += " AND (RESIDENT.RES_FNAME ILIKE %s OR RESIDENT.RES_LNAME ILIKE %s OR (RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME) ILIKE %s) AND HISTORY.HIST_DESCRIPTION = %s "
                    parameters.extend([f"%{search_text}%", f"%{search_text}%", search_text])


            elif search_text is not None and selected_type != "All":
                query += " AND (RESIDENT.RES_FNAME ILIKE %s OR RESIDENT.RES_LNAME ILIKE %s OR (RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME) ILIKE %s)"
                parameters.extend([f"%{search_text}%", f"%{search_text}%", search_text])


            elif search_text and selected_type and selected_type != "All":
                query += " AND (RESIDENT.RES_FNAME ILIKE %s OR RESIDENT.RES_LNAME ILIKE %s OR (RESIDENT.RES_FNAME || ' ' || RESIDENT.RES_LNAME) ILIKE %s) AND HISTORY.HIST_DESCRIPTION = %s"
                parameters.extend([f"%{search_text}%", f"%{search_text}%", search_text],selected_type)

            # Add ordering by date in descending order
            query += " ORDER BY HISTORY.HIST_DATE DESC"
            cursor.execute(query, parameters)
            history_records = cursor.fetchall()

            self.document_table.setRowCount(len(history_records))

            for row, record in enumerate(history_records):
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Format the date column if it is in the third position (index 2)
                    if col == 2:
                        date = value.strftime("%Y-%m-%d %H:%M:%S")  # Format the date string
                        item.setText(date)

                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.document_table.setItem(row, col, item)

            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

class AdminNotesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui_admin/admin_notes.ui", self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datetime)
        self.timer.start(1000)  # Updating every second
        self.updated_datetime()


        self.create_account_button.clicked.connect(self.go_create_account)
        self.residents_button.clicked.connect(self.go_resident)
        self.documents_button.clicked.connect(self.go_documents)
        self.officials_button.clicked.connect(self.go_officials)
        self.transactions_button.clicked.connect(self.go_transaction)

        self.add_reminder.clicked.connect(self.addreminder)
        self.add_event.clicked.connect(self.addevent)
        self.reminder_table.itemDoubleClicked.connect(self.choose_action_reminder)
        self.event_table.itemDoubleClicked.connect(self.choose_action_event)
        self.populate_reminder_table()
        self.populate_event_table()
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def updated_datetime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

    def addreminder(self):
        reminder_text = self.edit_reminder.text()
        note_type = "Reminder"
        if reminder_text:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    database="bis",
                    user="postgres",
                    password="posgre"
                )
                cursor = conn.cursor()

                query = "INSERT INTO NOTE (NOTE_DESCRIPTION, NOTE_TYPE, NOTE_DATECREATED, NOTE_DATEUPDATED, NOTE_ISREMOVED, STAFF_ID) VALUES (%s, %s, NOW(), NOW(), False, %s)"
                values = (reminder_text, note_type, adminId)  # Replace adminId with the actual staff ID value

                cursor.execute(query, values)
                conn.commit()

                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Reminder note is saved")
                self.populate_reminder_table()
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL:", error)
        else:
            QMessageBox.information(self, "Error", "Please add a note")

    def addevent(self):
        event_text = self.edit_event.text()
        note_type = "Event"
        if event_text:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    database="bis",
                    user="postgres",
                    password="posgre"
                )
                cursor = conn.cursor()

                query = "INSERT INTO NOTE (NOTE_DESCRIPTION, NOTE_TYPE, NOTE_DATECREATED, NOTE_DATEUPDATED, NOTE_ISREMOVED, STAFF_ID) VALUES (%s, %s, NOW(), NOW(), False, %s)"
                values = (event_text, note_type, adminId)  # Replace adminId with the actual staff ID value

                cursor.execute(query, values)
                conn.commit()

                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Event note is saved")
                self.populate_event_table()
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL:", error)
        else:
            QMessageBox.information(self, "Error", "Please add an event")

    def populate_reminder_table(self):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()

            query = """
                  SELECT NOTE_DESCRIPTION
                  FROM NOTE WHERE NOTE_TYPE = 'Reminder' AND NOTE_ISREMOVED = false
                  ORDER BY NOTE_DATECREATED DESC
              """

            cursor.execute(query)
            reminder_descriptions = cursor.fetchall()

            self.reminder_table.setRowCount(len(reminder_descriptions))

            for row, description in enumerate(reminder_descriptions):
                item = QTableWidgetItem(str(description[0]))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.reminder_table.setItem(row, 0, item)
            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
    def populate_event_table(self):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()

            query = """
                  SELECT NOTE_DESCRIPTION
                  FROM NOTE WHERE NOTE_TYPE = 'Event' AND NOTE_ISREMOVED = false
                  ORDER BY NOTE_DATECREATED DESC
              """

            cursor.execute(query)
            event_descriptions = cursor.fetchall()

            self.event_table.setRowCount(len(event_descriptions))

            for row, description in enumerate(event_descriptions):
                item = QTableWidgetItem(str(description[0]))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.event_table.setItem(row, 0, item)
            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

    def choose_action_reminder(self, item):
        if item is None:
            # Handle the case when item is None
            print("Error: item is None")
            return
        row = item.row()
        table_name = "Reminder"

        message_box = QMessageBox()
        message_box.setWindowTitle("Choose an action")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText(f"Do you want to delete or update the selected {table_name.lower()} note?")

        delete_button = QPushButton("Delete")
        update_button = QPushButton("Update")

        message_box.addButton(delete_button, QMessageBox.ButtonRole.YesRole)
        message_box.addButton(update_button, QMessageBox.ButtonRole.NoRole)

        message_box.setDefaultButton(delete_button)
        button_clicked = message_box.exec()

        if button_clicked == 0:  # Delete button is clicked
            self.delete_cell(row, table_name)
        elif button_clicked == 1:  # Update button is clicked
            self.on_reminder_message_changed(item)
        else:
            pass




    def choose_action_event(self, item):
        if item is None:
            # Handle the case when item is None
            print("Error: item is None")
            return
        row = item.row()
        table_name = "Event"

        message_box = QMessageBox()
        message_box.setWindowTitle("Choose an action")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText(f"Do you want to delete or update the selected {table_name.lower()} note?")

        delete_button = QPushButton("Delete")
        update_button = QPushButton("Update")

        message_box.addButton(delete_button, QMessageBox.ButtonRole.YesRole)
        message_box.addButton(update_button, QMessageBox.ButtonRole.NoRole)

        message_box.setDefaultButton(delete_button)
        button_clicked = message_box.exec()

        if button_clicked == 0:  # Delete button is clicked
            self.delete_cell(row, table_name)
        elif button_clicked == 1:  # Update button is clicked
            self.on_event_message_changed(item)
        else:
            pass



    def delete_cell(self, row, table_name):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()
            if table_name == 'Reminder':
                current_table = self.reminder_table
                description = current_table.item(row, 0).text()
            else:
                current_table = self.event_table
                description = current_table.item(row, 0).text()

            query = "UPDATE NOTE SET NOTE_ISREMOVED = %s WHERE NOTE_DESCRIPTION = %s AND NOTE_TYPE = %s "
            values = (True,description, table_name)

            cursor.execute(query, values)
            conn.commit()

            cursor.close()
            conn.close()

            current_table.removeRow(row)

            QMessageBox.information(self, "Success", f"{table_name} note has been deleted")

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

    def on_reminder_message_changed(self, item):
        # Retrieve the row and column of the changed item
        row = item.row()
        column = item.column()
        table_name = "Reminder"
        # Perform actions based on the changed item
        if column == 0:
            # Get the current message in the clicked cell
            current_message = item.text()

            # Prompt the user to enter a new message
            new_message, ok = QInputDialog.getText(self, "Update Message", "Enter new message:", text=current_message)

            if ok and new_message:
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="bis",
                        user="postgres",
                        password="posgre"
                    )
                    cursor = conn.cursor()

                    # Get the current time
                    current_time = datetime.now()


                    # Update the message and current date in the database
                    query = "UPDATE NOTE SET NOTE_DESCRIPTION = %s, NOTE_DATEUPDATED = %s WHERE NOTE_DESCRIPTION = %s AND NOTE_TYPE = %s"
                    values = (new_message, current_time, current_message, table_name)

                    cursor.execute(query, values)
                    conn.commit()

                    cursor.close()
                    conn.close()
                    self.populate_reminder_table()
                    QMessageBox.information(self, "Success", "Message updated")
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL:", error)
                    QMessageBox.warning(self, "Error", "Failed to update message. Please try again.")
            else:
                return

    def on_event_message_changed(self, item):
        # Retrieve the row and column of the changed item
        row = item.row()
        column = item.column()
        table_name = "Event"
        # Perform actions based on the changed item
        if column == 0:
            # Get the current message in the clicked cell
            current_message = item.text()

            # Prompt the user to enter a new message
            new_message, ok = QInputDialog.getText(self, "Update Message", "Enter new message:", text=current_message)

            if ok and new_message:
                try:
                    conn = psycopg2.connect(
                        host="localhost",
                        database="bis",
                        user="postgres",
                        password="posgre"
                    )
                    cursor = conn.cursor()

                    # Get the current time
                    current_time = datetime.now()

                    # Update the message and current date in the database
                    query = "UPDATE NOTE SET NOTE_DESCRIPTION = %s, NOTE_DATEUPDATED = %s WHERE NOTE_DESCRIPTION = %s AND NOTE_TYPE = %s"
                    values = (new_message, current_time, current_message, table_name)

                    cursor.execute(query, values)
                    conn.commit()

                    cursor.close()
                    conn.close()
                    self.populate_event_table()
                    QMessageBox.information(self, "Success", "Message updated")
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL:", error)
                    QMessageBox.warning(self, "Error", "Failed to update message. Please try again.")
            else:
                return



    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_documents(self):
        admin_documents = AdminDocumentsWindow()
        widget_function(admin_documents)

    def go_officials(self):
        admin_officials = AdminOfficialsWindow()
        widget_function(admin_officials)

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

class AdminViewResidentWindow(QMainWindow):
    def __init__(self):
        super(AdminViewResidentWindow, self).__init__()
        loadUi("ui_admin/admin_view_resident.ui", self)

        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        createaccountbutton.clicked.connect(self.go_create_account)
        residentsbutton.clicked.connect(self.go_resident)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)
        self.userinfo = {}
        self.residentid = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        self.resident_name
        self.resident_picture
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def updated_datatime(self):
        # Get the current time
        current_time = QTime.currentTime()
        # Format the time as per your requirement
        time_text = current_time.toString("hh:mm:ss")
        # Update the UI elements with the new time
        self.header_time.setText(time_text)
        # Update the date
        current_date = QDate.currentDate()
        date_text = current_date.toString("yyyy-MM-dd")
        self.header_date.setText(date_text)

    def get_residentinfo(self, resident_id):
        self.residentid = resident_id
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )
        try:
            cursor = conn.cursor()
            query = "SELECT RES_ID, RES_FNAME, RES_MNAME, RES_LNAME, RES_SUFFIX, RES_GENDER, RES_CIVILSTATUS, RES_DOB, RES_POB, RES_CITIZENSHIP, " \
                    "RES_ADDRESSLINE, RES_BARANGAY, RES_CITY, RES_MOBILENUMBER, RES_EMAIL, RES_PICTURE FROM RESIDENT WHERE RES_ID = %s"

            cursor.execute(query, (resident_id,))
            user_record = cursor.fetchone()

            if user_record:
                result_dict = {
                    'res_id': user_record[0],
                    'res_fname': user_record[1],
                    'res_mname': user_record[2],
                    'res_lname': user_record[3],
                    'res_suffix': user_record[4],
                    'res_gender': user_record[5],
                    'res_civilstatus': user_record[6],
                    'res_dob': user_record[7],
                    'res_pob': user_record[8],
                    'res_citizenship': user_record[9],
                    'res_addressline': user_record[10],
                    'res_barangay': user_record[11],
                    'res_city': user_record[12],
                    'res_mobilenumber': user_record[13],
                    'res_email': user_record[14],
                    'res_picture': user_record[15]
                }

                self.userinfo = result_dict
                self.display_residentinfo()
                self.display_resident_picture(result_dict['res_picture'])

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)
            traceback.print_exc()

        finally:
            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    def display_residentinfo(self):
        userinfo = self.userinfo
        residentname = userinfo["res_fname"] + " " + userinfo["res_mname"] + " " + userinfo["res_lname"]
        address = userinfo["res_addressline"] + " " + userinfo["res_barangay"] + " " + userinfo["res_city"]
        # Set the text of the display labels

        self.resident_name.setText(residentname)

        # Increase font size
        font = QFont(self.resident_name.font())
        font.setPointSize(23)
        font.bold()
        self.resident_name.setFont(font)

        self.resident_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.firstname_display.setText(userinfo["res_fname"])
        self.lastname_display.setText(userinfo["res_lname"])
        self.middlename_display.setText(userinfo["res_mname"])
        self.suffix_display.setText(userinfo["res_suffix"])
        self.gender_display.setText(userinfo["res_gender"])
        self.citizenship_display.setText(userinfo["res_citizenship"])
        self.civil_status_display.setText(userinfo["res_civilstatus"])
        self.birthdate_display.setText(userinfo["res_dob"].strftime("%Y-%m-%d"))
        self.place_of_birth_display.setText(userinfo["res_pob"])
        self.address_display.setText(address)
        self.mobile_display.setText(userinfo["res_mobilenumber"])
        self.email_display.setText(userinfo["res_email"])

    def display_resident_picture(self, picture_data):
        pixmap = QPixmap()
        pixmap.loadFromData(picture_data)
        self.resident_picture.setPixmap(pixmap)

    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_documents(self):
        admin_documents = AdminDocumentsWindow()
        widget_function(admin_documents)

    def go_officials(self):
        admin_officials = AdminOfficialsWindow()
        widget_function(admin_officials)

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        admin_notes = AdminNotesWindow()
        widget_function(admin_notes)


class AdminLogoutWindow(QMainWindow):
    def __init__(self):
        super(AdminLogoutWindow, self).__init__()
        loadUi("ui_admin/admin_logout.ui", self)
        adminpicture = self.admin_picture
        adminname = self.admin_name
        createaccountbutton = self.create_account_button
        residentsbutton = self.residents_button
        documentsbutton = self.documents_button
        officialsbutton = self.officials_button
        transactionsbutton = self.transactions_button
        notesbutton = self.notes_button
        logoutbutton = self.logout_button

        createaccountbutton.clicked.connect(self.go_create_account)
        residentsbutton.clicked.connect(self.go_resident)
        documentsbutton.clicked.connect(self.go_documents)
        officialsbutton.clicked.connect(self.go_officials)
        transactionsbutton.clicked.connect(self.go_transaction)
        notesbutton.clicked.connect(self.go_notes)

        yesbtn = self.yes_button
        cancelbtn = self.cancel_button

        yesbtn.clicked.connect(self.yes)
        cancelbtn.clicked.connect(self.cancel)
        self.logout_button.clicked.connect(self.go_logout)

    def go_logout(self):
        admin_logout = AdminLogoutWindow()
        widget_function(admin_logout)

    def go_create_account(self):
        admin_resident = AdminResidentWindow()
        admin_resident.go_create_account()

    def go_resident(self):
        admin_resident = AdminResidentWindow()
        widget_function(admin_resident)

    def go_documents(self):
        admin_documents = AdminDocumentsWindow()
        widget_function(admin_documents)

    def go_officials(self):
        admin_officials = AdminOfficialsWindow()
        widget_function(admin_officials)

    def go_transaction(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_transaction()

    def go_notes(self):
        create_account = AdminCreateAccountWindow()
        create_account.go_notes()

    def yes(self):
        import main
        main.widget_function(main.LoginWindow())
        main.widget.show()
        widget.close()

    def cancel(self):
        createaccount = AdminCreateAccountWindow()
        widget_function(createaccount)




app = QApplication(sys.argv)
admin_create_account = AdminCreateAccountWindow()
widget = QtWidgets.QStackedWidget()
widget_function(admin_create_account)
widget.showFullScreen()
widget.show()
app.exec()