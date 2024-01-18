import os
import subprocess
import sys
import traceback

from datetime import datetime, date
import cv2
import psycopg2
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QComboBox, QTableWidget, QPushButton, \
    QTableWidgetItem, QFileDialog, QLabel
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTime, QDate, QTimer, Qt, QFileInfo
from docxtpl import DocxTemplate
from psycopg2 import Binary

def widget_function(frame):
    widget.addWidget(frame)
    widget.setCurrentIndex(widget.currentIndex() + 1)


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
staffDict = {

}

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi("ui/login.ui", self)
        loginbtn = self.login_button
        loginbtn.clicked.connect(self.login)

        closebutton = self.close_button
        closebutton.clicked.connect(self.close_app)

    def close_app(self):
        widget.close()
    def login(self):
        # Getting user input
        username_input = self.username_input.text()
        password_input = self.password_input.text()

        try:
            # Perform basic validation
            if not username_input:
                QMessageBox.critical(self.centralwidget, "Required", "Username is required")
                return
            if not password_input:
                QMessageBox.critical(self.centralwidget, "Required", "Password is required")
                return

            # Establish a connection to the PostgreSQL database
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )

            # Validating email, checking if user exists
            cursor = conn.cursor()
            cursor.execute("SELECT STAFF_ID, STAFF_USERNAME, STAFF_PASSWORD, STAFF_ISADMIN, STAFF_FNAME, STAFF_LNAME "
                           "FROM STAFF WHERE STAFF_USERNAME = %s",(username_input,))


            user = cursor.fetchone()

            if user is None:
                QMessageBox.critical(self.centralwidget, "Invalid", "Staff doesn't exist")
                return

            user_data = {
                'STAFF_ID': user[0],
                'STAFF_USERNAME': user[1],
                'STAFF_PASSWORD': user[2],
                'STAFF_ISADMIN': user[3],
                'STAFF_FNAME' : user[4],
                'STAFF_LNAME' : user [5]
            }
            staffid = user_data["STAFF_ID"]
            global staffDict
            staffDict = user_data

            password =  user_data["STAFF_PASSWORD"]
            is_admin =  user_data["STAFF_ISADMIN"]
            # Validate the password
            if password == password_input:
                if is_admin:
                    QMessageBox.information(self.centralwidget, "Success", "Welcome Admin")
                    import admin
                    admin.widget_function(admin.AdminCreateAccountWindow())
                    admin.widget.show()
                    widget.close()
                else:
                    QMessageBox.information(self.centralwidget, "Success", "Welcome User")
                    insert_history(None,"Staff Login",staffid)
                    self.go_homepage()

                    # Add more fields and store them in session, redirect to another page after
            else:
                QMessageBox.critical(self.centralwidget, "Invalid", "Invalid Password")

        except Exception as e:
            # Print or log the exception information
            print("An error occurred during login:")
            traceback.print_exc()
            QMessageBox.critical(self.centralwidget, "Error", "An error occurred during login")

    def go_homepage(self):
        homepage = HomepageWindow()
        homepage.display_staffinfo()
        widget_function(homepage)


class LogoutWindow(QMainWindow):
    def __init__(self):
        super(LogoutWindow, self).__init__()
        loadUi("ui/resident_logout.ui", self)
        homepagebtn = self.homepage_button
        residentbtn = self.resident_button
        officialbtn = self.official_button
        yesbtn = self.yes_button
        cancelbtn = self.cancel_button

        homepagebtn.clicked.connect(self.go_homepage)
        residentbtn.clicked.connect(self.go_resident)
        officialbtn.clicked.connect(self.go_official)
        yesbtn.clicked.connect(self.yes)
        cancelbtn.clicked.connect(self.cancel)
        self.display_staffinfo()

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

    def go_homepage(self):
        login = LoginWindow()
        login.go_homepage()

    def go_resident(self):
        homepage = HomepageWindow()
        homepage.go_resident()

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def yes(self):
        login = LoginWindow()
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        insert_history(None, "Staff Logout", staff_id)
        widget_function(login)

    def cancel(self):
        homepage = HomepageWindow()
        widget_function(homepage)

class HomepageWindow(QMainWindow):
    def __init__(self):
        super(HomepageWindow, self).__init__()
        loadUi("ui/resident_homepage.ui", self)


        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000) # Updating every second
        self.updated_datatime()

        staffusername = self.staff_username
        staffimage = self.staff_image
        headerdate = self.header_date
        headertime = self.header_time
        remindertbl = self.reminder_table
        eventtbl = self.event_table

        singledisplay = self.single_display
        marrieddisplay = self.married_display
        widoweddisplay = self.widowed_display
        divorceddisplay = self.divorced_display
        maledisplay = self.male_display
        femaledisplay = self.female_display
        employeddisplay = self.employed_display
        unemployeddisplay = self.unemployed_display
        populationdisplay = self.population_display

        residentbtn = self.resident_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button
        self.populate_reminder_table()
        self.populate_event_table()
        residentbtn.clicked.connect(self.go_resident)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        self.display_query_results()
        self.display_staffinfo()


    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

    def display_query_results(self):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()

            # EMPLOYED
            employed_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_OCCUPATION NOT IN ('Student', 'None', 'N/A') AND RES_ISREMOVED = 'False'
            """
            cursor.execute(employed_query)
            employed_count = cursor.fetchone()[0]
            self.employed_display.setText(str(employed_count))

            # UNEMPLOYED
            unemployed_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_OCCUPATION IN ('Student','None', 'N/A') AND RES_ISREMOVED = 'False'
            """
            cursor.execute(unemployed_query)
            unemployed_count = cursor.fetchone()[0]
            self.unemployed_display.setText(str(unemployed_count))

            # SINGLE
            single_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_CIVILSTATUS = 'Single' AND RES_ISREMOVED = 'False'
            """
            cursor.execute(single_query)
            single_count = cursor.fetchone()[0]
            self.single_display.setText(str(single_count))

            # MARRIED
            married_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_CIVILSTATUS = 'Married' AND RES_ISREMOVED = 'False'
            """
            cursor.execute(married_query)
            married_count = cursor.fetchone()[0]
            self.married_display.setText(str(married_count))

            # WIDOWED
            widowed_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_CIVILSTATUS = 'Widowed' AND RES_ISREMOVED = 'False'
            """
            cursor.execute(widowed_query)
            widowed_count = cursor.fetchone()[0]
            self.widowed_display.setText(str(widowed_count))

            # DIVORSED
            divorsed_query = """
                          SELECT COUNT(*) FROM RESIDENT
                          WHERE RES_CIVILSTATUS = 'Divorced' AND RES_ISREMOVED = 'False'
                      """
            cursor.execute(divorsed_query)
            divorse_count = cursor.fetchone()[0]
            self.divorced_display.setText(str(divorse_count))

            # MALE
            male_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_GENDER = 'Male' AND RES_ISREMOVED = 'False'
            """
            cursor.execute(male_query)
            male_count = cursor.fetchone()[0]
            self.male_display.setText(str(male_count))

            # FEMALE
            female_query = """
                SELECT COUNT(*) FROM RESIDENT
                WHERE RES_GENDER = 'Female' AND RES_ISREMOVED = 'False'
            """
            cursor.execute(female_query)
            female_count = cursor.fetchone()[0]
            self.female_display.setText(str(female_count))

            # POPULATION
            population_query = """
                SELECT COUNT(*) FROM RESIDENT WHERE RES_ISREMOVED = 'False'
            """
            cursor.execute(population_query)
            population_count = cursor.fetchone()[0]
            self.population_display.setText(str(population_count))

            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)


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
                  ORDER BY NOTE_ID DESC
              """

            cursor.execute(query)
            reminder_descriptions = cursor.fetchall()

            self.reminder_table.setRowCount(len(reminder_descriptions))
            self.reminder_table.setShowGrid(False)  # Remove cell lines
            font = self.reminder_table.font()
            font.setPointSize(16)  # Adjust the font size as desired
            self.reminder_table.setFont(font)

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
                  ORDER BY NOTE_ID DESC
              """

            cursor.execute(query)
            event_descriptions = cursor.fetchall()

            self.event_table.setRowCount(len(event_descriptions))
            self.event_table.setShowGrid(False)  # Remove cell lines
            font = self.event_table.font()
            font.setPointSize(16)  # Adjust the font size as desired
            self.event_table.setFont(font)

            for row, description in enumerate(event_descriptions):
                item = QTableWidgetItem(str(description[0]))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.event_table.setItem(row, 0, item)
            cursor.close()
            conn.close()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

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

    def go_resident(self):
        resident = ResidentWindow()
        widget_function(resident)



    def go_official(self):
        official = ResidentOfficialWindow()
        widget_function(official)

    def go_logout(self):
        logout = LogoutWindow()
        widget_function(logout)

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

class ResidentWindow(QMainWindow):
    def __init__(self):
        super(ResidentWindow, self).__init__()
        loadUi("ui/resident_resident.ui", self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()

        staffusername = self.staff_username
        staffimage = self.staff_image
        headerdate = self.header_date
        headertime = self.header_time
        self.userid = ""
        cancelbtn = self.cancel_button
        self.search_resident.textChanged.connect(self.populate_table)
        self.resident_table.setColumnCount(4)
        self.resident_table.setHorizontalHeaderLabels(['ID', 'Name', 'Gender', 'Action'])
        self.resident_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.resident_table.cellDoubleClicked.connect(self.onCellDoubleClicked)

        self.display_staffinfo()
        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button
        addresidentbtn = self.add_resident_button
        self.update_resident_button.setEnabled(False)

        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        addresidentbtn.clicked.connect(self.add_resident)
        self.update_resident_button.clicked.connect(self.update_resident)
        cancelbtn.clicked.connect(self.cancelClicked)
        self.populate_table()
        self.display_staffinfo()

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

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
            query = "SELECT RES_ID, RES_FNAME || ' ' || RES_LNAME AS NAME, RES_GENDER, RES_DATEREGISTERED FROM RESIDENT WHERE RES_ISREMOVED = 'False' "
            parameters = []
            if search_text:
                query += " AND RES_FNAME ILIKE %s OR RES_LNAME ILIKE %s"
                parameters.append(f"%{search_text}%")
                parameters.append(f"%{search_text}%")
            query += "ORDER BY res_id desc"
            cursor.execute(query, parameters)
            user_records = cursor.fetchall()



            # Set the number of rows in the table
            self.resident_table.setRowCount(len(user_records))

            for row, record in enumerate(user_records):
                # Populate the table cells with data
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 3:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.resident_table.setItem(row, col, item)

                # Add the view profile button
                view_profile_button = QPushButton('View Profile')
                view_profile_button.clicked.connect(lambda _, user_id=record[0]: self.view_profile(user_id))
                self.resident_table.setCellWidget(row, 3, view_profile_button)

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
            item = self.resident_table.item(row, column)
            user_id = int(item.text())
            self.userid = user_id
            self.update_resident_button.setEnabled(True)
            QMessageBox.information(self, "Message", f"Update resident profile resident id: {user_id}?")

    def view_profile(self, user_id):
        QMessageBox.information(self, "Success", f"View resident profile of resident id: {user_id}")
        resident_view_resident = ResidentViewResident()
        resident_view_resident.get_residentinfo(user_id)
        # resident_view_resident.display_residentinfo()
        widget_function(resident_view_resident)

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)


    def go_homepage(self):
        homepage = HomepageWindow()
        widget_function(homepage)

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        homepage = HomepageWindow()
        homepage.go_logout()

    def add_resident(self):

        resident_add = ResidentAddWindow()
        widget_function(resident_add)

    def update_resident(self):
        resident_update = ResidentUpdateWindow(self.userid)
        resident_update.load_resident_info()
        widget_function(resident_update)

class ResidentViewResident(QMainWindow):
    def __init__(self):
        super(ResidentViewResident, self).__init__()
        loadUi("ui/resident_view_resident.ui", self)

        self.userinfo = {}
        self.staff_username
        self.residentid = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        residentbtn = self.resident_button
        staffimage = self.staff_image
        headerdate = self.header_date
        headertime = self.header_time
        self.resident_name
        self.resident_picture
        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button

        documentsbtn = self.documents_button
        documentrequestbtn = self.document_request_button
        self.display_staffinfo()

        residentbtn.clicked.connect(self.go_resident)
        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        documentsbtn.clicked.connect(self.document)
        documentrequestbtn.clicked.connect(self.document_request)

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

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

    def go_resident(self):
        resident = ResidentWindow()
        widget_function(resident)

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

    def go_homepage(self):
        homepage = HomepageWindow()
        widget_function(homepage)

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        homepage = HomepageWindow()
        homepage.go_logout()

    def document_request(self):
        resident_document_request = ResidentDocumentRequest(self.residentid)
        resident_document_request.get_user_info()
        widget_function(resident_document_request)

    def document(self):
        resident_view_available_document = ResidentViewDocumentAvailable(self.residentid)
        widget_function(resident_view_available_document)

class ResidentDocumentRequest(QMainWindow):
    def __init__(self ,residentid):
        super(ResidentDocumentRequest, self) .__init__()
        loadUi("ui/resident_document_request.ui", self)

        global staffDict
        self.staff_id = staffDict["STAFF_ID"]
        self.resident_id = residentid
        self.user_info = {}


        staffusername = self.staff_username
        staffimage = self.staff_image
        self.barangay_certificate_button.clicked.connect(self.generate_brgy_clearance)
        self.barangay_indigency_button.clicked.connect(self.generate_certificate_indigency)
        self.certificate_of_residency_button.clicked.connect(self.generate_certificate_residency)
        backbtn = self.back_button

        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button

        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        backbtn.clicked.connect(self.back)
        self.display_staffinfo()

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

    def get_user_info(self):
        user_id = self.resident_id
        current_date = date.today()
        print("get user info")
        print(user_id)
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                database="bis",
                user="postgres",
                password="posgre",
                host="localhost",
                port="5432"
            )
            # Create a cursor object
            cursor = conn.cursor()

            # Fetch user information from the database using the User ID
            select_query = "SELECT res_fname, res_mname, res_lname, res_suffix, res_gender, " \
                           "res_dob, res_addressline, res_email, res_civilstatus, res_id " \
                           "FROM resident " \
                           "WHERE res_id = %s"

            cursor.execute(select_query, (user_id,))
            user_info = cursor.fetchone()

            if user_info:
                dob = user_info[5]
                age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
                self.user_info = {
                    "First Name": user_info[0],
                    "Middle Name": user_info[1],
                    "Last Name": user_info[2],
                    "Suffix": user_info[3],
                    "Age": age,
                    "Gender": user_info[4],
                    "Date of Birth": user_info[5],
                    "Street": user_info[6],
                    "Email Address": user_info[7],
                    "Civil Status": user_info[8],
                    "ID": user_info[9]
                }

            else:
                QMessageBox.warning(self, "Error", "User ID not found in the database.")

            conn.commit()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.critical(self, "Error", f"Error accessing database: {error}")

        finally:
            # Close the database connection
            if conn:
                conn.close()
                print("Database connection closed.")

    def generate_brgy_clearance(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText("Do you want to generate Certificate of Indigency?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        button_clicked = message_box.exec()

        if button_clicked == QMessageBox.StandardButton.Yes:
            # Implement logic for generating barangay clearance
            QMessageBox.information(self, "Barangay Clearance", "Generating Barangay Clearance...")
            # Need to implement getting the file template from the database
            doc = DocxTemplate("BARANGAY_CLEARANCE.docx")
            resident_firstname = self.user_info["First Name"]
            resident_middlename = self.user_info["Middle Name"]
            resident_lastname = self.user_info["Last Name"]
            resident_age = self.user_info["Age"]
            resident_civilstat = self.user_info["Civil Status"]
            resident_day = datetime.today().day
            resident_month = datetime.today().month
            resident_year = datetime.today().year
            transaction_id = "10001"
            resident_date = datetime.today().strftime("%d %b, %Y")
            resident_id = self.user_info["ID"]
            context = {
                'RES_NAME': resident_firstname + " " + resident_middlename + " " + resident_lastname,
                'RES_AGE': resident_age,
                'RES_CIVILSTATUS': resident_civilstat,
                'DAY': resident_day,
                'MONTH': resident_month,
                'YEAR': resident_year,
                'TRANS_ID': transaction_id,
                'DATE': resident_date
            }

            try:
                filename = f"{resident_lastname}_{resident_id}_BarangayClearance.docx"
                doc.render(context)
                doc.save(filename)
                QMessageBox.information(self, "Barangay Clearance", "Barangay Clearance generated successfully.")
                # Open the generated file for printing
                os.startfile(filename)
                is_printed = self.check_file_print_status(filename)

                if is_printed:
                    QMessageBox.information(self, "Barangay Clearance", "Barangay Clearance added to the transaction.")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()

                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False

                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id, cert_id)" \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id,10047)
                    insert_history(self.resident_id, "Barangay Clearance Released",self.staff_id)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()

                else:
                    QMessageBox.information(self, "Barangay Clearance", "Barangay Clearance added to the transaction.")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()

                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False
                    # cert id
                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id, cert_id) " \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    # insert into history
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id,10047)
                    insert_history(self.resident_id, "Barangay Clearance Released", self.staff_id)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate Barangay Clearance: {str(e)}")
        else:
            pass


    def generate_certificate_indigency(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText("Do you want to generate Certificate of Indigency?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        button_clicked = message_box.exec()

        if button_clicked == QMessageBox.StandardButton.Yes:
            # Implement logic for generating certificate of indigency
            QMessageBox.information(self, "Certificate of Indigency", "Generating Certificate of Indigency...")
            doc = DocxTemplate("CERTIFICATE_OF_INDIGENCY.docx")

            resident_firstname = self.user_info["First Name"]
            resident_middlename = self.user_info["Middle Name"]
            resident_lastname = self.user_info["Last Name"]
            resident_age = self.user_info["Age"]
            resident_civilstat = self.user_info["Civil Status"]
            resident_nationality = "Filipino"
            resident_day = datetime.today().day
            resident_month = datetime.today().month
            resident_year = datetime.today().year
            transaction_id = "10001"
            resident_date = datetime.today().strftime("%d %b, %Y")
            resident_id = self.user_info["ID"]
            context = {
                'RES_NAME': resident_firstname + " " + resident_middlename + " " + resident_lastname,
                'RES_AGE': resident_age,
                'RES_CIVILSTATUS': resident_civilstat,
                'RES_NATIONALITY': resident_nationality,
                'DAY': resident_day,
                'MONTH': resident_month,
                'YEAR': resident_year,
                'TRANS_ID': transaction_id,
                'DATE': resident_date
            }

            try:
                filename = f"{resident_lastname}_{resident_id}_CertofIndigency.docx"
                doc.render(context)
                doc.save(filename)
                QMessageBox.information(self, "Certificate of Indigency",
                                        "Certificate of Indigency generated successfully.")
                os.startfile(filename)
                is_printed = self.check_file_print_status(filename)

                if is_printed:
                    QMessageBox.information(self, "Certificate of Indigency", "Certificate of Indigency added to the transaction.")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()
                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False

                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id, cert_id) " \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    insert_history(self.resident_id, "Certificate of Indigency Released", self.staff_id)
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id,10048)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()

                else:
                    QMessageBox.information(self, "Certificate of Indigency", "Certificate of Indigency added to the transaction.")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()

                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False

                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id, cert_id) " \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    insert_history(self.resident_id, "Certificate of Indigency Released", self.staff_id)
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id, 10048)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate Certificate of Indigency: {str(e)}")
        else:
            pass

    def generate_certificate_residency(self):
        # Implement logic for generating certificate of residency

        message_box = QMessageBox()
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setText("Do you want to generate Certificate of Residency?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        button_clicked = message_box.exec()

        if button_clicked == QMessageBox.StandardButton.Yes:

            QMessageBox.information(self, "Certificate of Residency", "Generating Certificate of Residency...")
            doc = DocxTemplate("CERTIFICATE_OF_RESIDENCY.docx")

            resident_firstname = self.user_info["First Name"]
            resident_middlename = self.user_info["Middle Name"]
            resident_lastname = self.user_info["Last Name"]
            resident_age = self.user_info["Age"]
            resident_civilstat = self.user_info["Civil Status"]
            resident_nationality = "Filipino"
            resident_day = datetime.today().day
            resident_month = datetime.today().month
            resident_year = datetime.today().year
            transaction_id = "10001"
            resident_date = datetime.today().strftime("%d %b, %Y")
            resident_id = self.user_info["ID"]

            context = {
                'RES_NAME': resident_firstname + " " + resident_middlename + " " + resident_lastname,
                'RES_AGE': resident_age,
                'RES_CIVILSTATUS': resident_civilstat,
                'RES_NATIONALITY': resident_nationality,
                'DAY': resident_day,
                'MONTH': resident_month,
                'YEAR': resident_year,
                'TRANS_ID': transaction_id,
                'DATE': resident_date
            }

            try:
                filename = f"{resident_lastname}_{resident_id}_CertofResidency.docx"
                doc.render(context)
                doc.save(filename)
                QMessageBox.information(self, "Certificate of Residency",
                                        "Certificate of Residency generated successfully.")
                is_printed = self.check_file_print_status(filename)
                os.startfile(filename)

                if is_printed:
                    QMessageBox.information(self, "Certificate of Residency ", "Certificate of Residency  added to the transaction.")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()

                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False
                    insert_history(self.resident_id, "Certificate of Residency Released", self.staff_id)
                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id, cert_id) " \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id, 10052)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()

                else:
                    QMessageBox.information(self, "Certificate of Residency", "Please check if the document is printed")
                    # Read the file data
                    with open(filename, 'rb') as file:
                        filedata = file.read()

                    conn = psycopg2.connect(
                        database="bis",
                        user="postgres",
                        password="posgre",
                        host="localhost",
                        port="5432"
                    )

                    cursor = conn.cursor()
                    # Insert cert data into the database
                    trans_filename = filename
                    trans_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trans_isremoved = False
                    insert_history(self.resident_id, "Certificate of Residency Released", self.staff_id)
                    cert_query = "INSERT INTO transaction (trans_description, trans_daterequested, trans_isremoved, res_id, staff_id,cert_id) " \
                                 "VALUES (%s, %s, %s, %s, %s, %s)"
                    cert_values = (trans_filename, trans_datecreated, trans_isremoved, self.resident_id, self.staff_id, 10052)
                    cursor.execute(cert_query, cert_values)
                    conn.commit()
                    # Close the database connection
                    cursor.close()
                    conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate Certificate of Residency: {str(e)}")
        else:
            pass


    def check_file_print_status(self, filename):
        # Execute a command to check the print status of the file
        try:
            result = subprocess.run(["powershell", "-Command",
                                     f"(Get-Printer -Name 'Microsoft Print to PDF').Jobs | Where-Object {{ $_.Document -eq '{filename}' }} | Select-Object -First 1"],
                                    capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                # File has been printed
                return True
            else:
                # File has not been printed
                return False
        except subprocess.TimeoutExpired:
            # Command execution timed out
            return False
        except Exception:
            # Error occurred while checking print status
            return False

    def go_homepage(self):
        homepage = HomepageWindow()
        widget_function(homepage)

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        homepage = HomepageWindow()
        homepage.go_logout()

    def back(self):
        resident_view_resident = ResidentViewResident()
        resident_view_resident.get_residentinfo(self.resident_id)
        widget_function(resident_view_resident)

class ResidentViewDocumentAvailable(QMainWindow):
    def __init__(self,resident_id):
        super(ResidentViewDocumentAvailable, self).__init__()
        loadUi("ui/resident_view_document_available.ui", self)
        self.residentid = resident_id
        self.binary_data = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.updated_datatime)
        self.timer.start(1000)  # Updating every second
        self.updated_datatime()
        staffusername = self.staff_username
        staffimage = self.staff_image
        headerdate = self.header_date
        headertime = self.header_time

        self.search_document.textChanged.connect(self.populate_table)
        self.file_label = QLabel(self)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setGeometry(20, 20, 360, 180)

        self.document_table.setColumnCount(4)  # Number of columns, including the button column
        self.document_table.setHorizontalHeaderLabels(['FILE NAME', 'DOCUMENT TYPE', 'DATE TIME', 'ACTION'])
        self.document_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.document_table.cellDoubleClicked.connect(self.onCellClicked)
        self.populate_table()
        cancelbtn = self.cancel_button
        self.add_document_button.clicked.connect(self.upload_file)
        self.delete_button.clicked.connect(self.update_document)
        self.delete_button.setEnabled(False)
        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button

        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        self.display_staffinfo()

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)


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

    def upload_file(self):
        staff_id = staffDict["STAFF_ID"]
        res_id = self.residentid

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter('Document Files (*.doc *.pdf *.docx);;Image Files (*.png *.jpg)')

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            doc_filedata = selected_files[0]
            file_info = QFileInfo(doc_filedata)
            doc_filename = file_info.fileName()

            doc_type = doc_filedata.split('.')[-1].lower()
            if doc_type not in ['png', 'jpg', 'jpeg', 'doc', 'docx', 'pdf']:
                QMessageBox.information(self, "Error",
                                        "Invalid file format. Only PNG, JPG, DOC, and PDF files are allowed.")
                return

            try:
                # Reading the file into binary
                with open(doc_filedata, 'rb') as file:
                    file_data = file.read()

                filename = doc_filename
                doc_datecreated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data created
                doc_isremoved = 'FALSE'

                # Insert filename and file data into the database
                conn = psycopg2.connect(
                    host="localhost",
                    database="bis",
                    user="postgres",
                    password="posgre"
                )
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO document (doc_filename, doc_filedata, doc_type, doc_datecreated, res_id, staff_id, doc_isremoved) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (filename, file_data, doc_type, doc_datecreated, res_id, staff_id, doc_isremoved))
                    insert_history(res_id, "Uploaded Document", staff_id)
                    conn.commit()
                    QMessageBox.information(self, "Success", "File is uploaded successfully!")
                    resident_view_available_document = ResidentViewDocumentAvailable(self.residentid)
                    widget_function(resident_view_available_document)
                except (Exception, psycopg2.Error) as error:
                    QMessageBox.critical(self, "Error", f"Error opening the file: {str(error)}")
                finally:
                    cursor.close()
                    conn.close()

                pixmap = QPixmap(doc_filedata)
                self.file_label.setPixmap(pixmap.scaled(360, 180, Qt.AspectRatioMode.KeepAspectRatio))

            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Error opening the file: {str(ex)}")
                traceback.print_exc()

    def populate_table(self, search_text=None):
        res_id = self.residentid
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
            query = "SELECT DOC_FILENAME, DOC_TYPE, DOC_DATECREATED, DOC_FILEDATA FROM DOCUMENT WHERE RES_ID = %s AND DOC_ISREMOVED = %s"
            parameters = [res_id,False]
            if search_text:
                query += " AND (DOC_FILENAME LIKE %s OR DOC_TYPE LIKE %s)"
                parameters.append(f"%{search_text}%")
                parameters.append(f"%{search_text}%")

            cursor.execute(query, parameters)
            document_records = cursor.fetchall()

            # Set the number of rows in the table
            self.document_table.setRowCount(len(document_records))

            for row, record in enumerate(document_records):
                # Populate the table cells with data
                for col, value in enumerate(record[:3]):
                    item = QTableWidgetItem(str(value))

                    # Disable editing for non-button columns
                    if col != 3:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.document_table.setItem(row, col, item)

                # Add the view file button
                view_file_button = QPushButton('View File')
                file_binary = record[3]
                view_file_button.clicked.connect(lambda _, binary=file_binary: self.view_file(binary))
                self.document_table.setCellWidget(row, 3, view_file_button)


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
        if column == 3:  # Assuming the action column is column 3
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
                self.delete_button.setEnabled(True)
                QMessageBox.information(self, "Message", f"You select {file_name}")


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

                    # Update document data in the "DOCUMENT" table
                    query = "UPDATE DOCUMENT SET DOC_ISREMOVED = %s WHERE DOC_FILEDATA = %s"
                    global staffDict
                    staff_id = staffDict["STAFF_ID"]
                    insert_history(self.residentid, "Removed Document", staff_id)
                    parameters = (True, self.binary_data)

                    cursor.execute(query, parameters)
                    conn.commit()

                    cursor.close()
                    conn.close()

                    QMessageBox.information(self, "Message", "Document has been deleted successfully")


                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL:", error)
                    traceback.print_exc()

            else:
                pass

        else:
            QMessageBox.warning(self, "Warning", "Please choose a row before updating the document.")
        resident_view_available_document = ResidentViewDocumentAvailable(self.residentid)
        widget_function(resident_view_available_document)

    def go_homepage(self):
        homepage = HomepageWindow()
        widget_function(homepage)

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        homepage = HomepageWindow()
        homepage.go_logout()

class ResidentAddWindow(QMainWindow):
    def __init__(self):
        super(ResidentAddWindow, self).__init__()
        loadUi("ui/resident_add_resident.ui", self)
        self.staff_info = {}
        self.staff_username
        self.staff_image
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
            'barangay_input': self.barangay_input if self.barangay_input.text() != '' else self.barangay_input.setText('Pajo'),
            'city_input': self.city_input if self.city_input.text() != '' else self.city_input.setText('Lapu lapu City'),
            'region_input': self.region_input if self.region_input.text() != '' else self.region_input.setText('VII'),
            'occupation_input': self.occupation_input,
            'contact_number_input': self.contact_number_input,
            'email_address_input': self.email_address_input,
            'place_of_birth_input': self.place_of_birth_input
        }

        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button
        backbtn = self.back_button
        addpicturebtn = self.add_picture_button
        saveresidentbtn = self.save_resident_button

        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        backbtn.clicked.connect(self.back)
        addpicturebtn.clicked.connect(self.capture_image)
        saveresidentbtn.clicked.connect(self.validate_resident_input)
        self.display_staffinfo()

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

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

    def validate_resident_input(self):
        line_edit_values = [line_edit.text().strip() for line_edit in self.line_edits.values() if
                            isinstance(line_edit, QLineEdit)]
        combo_box_values = [combo_box.currentText() for combo_box in self.line_edits.values() if
                            isinstance(combo_box, QComboBox)]
        firstname_input_value = self.line_edits['firstname_input'].text().strip()
        lastname_input_value = self.line_edits['lastname_input'].text().strip()
        middlename_input_value = self.line_edits['middlename_input'].text().strip()
        bday_input_value = self.line_edits['bday_input']
        gender_input_value = self.gender_input.currentText()

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

        if not hasattr(self, "add_resident_image_file") or self.add_resident_image_file is None:
            QMessageBox.warning(self, "Invalid Input", "Please upload a picture.")
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
        default_gender = ["Male","Female"]
        default_civil_status = ["Single", "Married", "Widowed", "Divorced"]
        selected_gender = self.gender_input.currentText()
        selected_civil_status = self.civil_status_input.currentText()


        if selected_gender not in default_gender or selected_civil_status not in default_civil_status:
            QMessageBox.warning(self, "Invalid Input", "Please select a value from the dropdown menus.")
            return

        check_ifExist = self.check_resident_exists(firstname_input_value, lastname_input_value,middlename_input_value,
                                   gender_input_value,calendar_value)
        if check_ifExist:
            QMessageBox.warning(self, "Invalid Input", "Resident already exists with the provided details.")
            self.display_resident_full_name(firstname_input_value, middlename_input_value, lastname_input_value)
            return



        # All validations passed
        QMessageBox.information(self, "Message", "Saving Resident's Information.....")

        self.submit_form()

    def check_resident_exists(self, first_name, last_name, middle_name, gender,calendar_value):
        conn = psycopg2.connect(
            host="localhost",
            database="bis",
            user="postgres",
            password="posgre"
        )

        cursor = conn.cursor()
        query = "SELECT * FROM RESIDENT WHERE RES_FNAME = %s AND RES_LNAME = %s AND RES_MNAME = %s AND RES_GENDER = %s AND RES_DOB = %s"
        values = (first_name, last_name, middle_name, gender, calendar_value)

        cursor.execute(query, values)
        resident_data = cursor.fetchone()

        return bool(resident_data)

    def display_resident_full_name(self,first_name, middle_name, last_name):
        full_name = f"{first_name} {middle_name} {last_name}"
        message_box = QMessageBox()
        message_box.setWindowTitle("Resident's Full Name")
        message_box.setText(f"The resident's full name is: {full_name}")
        message_box.exec()

    def submit_form(self):
        firstname_input_value = self.line_edits['firstname_input'].text().strip()
        lastname_input_value = self.line_edits['lastname_input'].text().strip()
        middlename_input_value = self.line_edits['middlename_input'].text().strip()
        suffix_input_value = self.line_edits['suffix_input'].text().strip()
        gender_input_value = self.gender_input.currentText()
        citizenship_input_value = self.line_edits['citizenship_input'].text().strip()
        civil_status_input_value = self.civil_status_input.currentText()
        bday_input_value = self.bday_input.date().toString("yyyy-MM-dd")
        religion_input_value = self.line_edits['religion_input'].text().strip()
        addressline_input_value = self.line_edits['addressline_input'].text().strip()
        barangay_input_value = self.barangay_input.text()
        city_input_value = self.city_input.text()
        region_input_value = self.region_input.text()
        occupation_input_value = self.line_edits['occupation_input'].text().strip()
        contact_number_input_value = self.line_edits['contact_number_input'].text().strip()
        email_address_input_value = self.line_edits['email_address_input'].text().strip()
        place_of_birth_input_value = self.line_edits['place_of_birth_input'].text().strip()

        global staffDict
        staff_id = staffDict["STAFF_ID"]
        resident_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        resident_isremoved = False
        resident_isofficial = False

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

            # Read the image file as binary data
            with open(self.add_resident_image_file, "rb") as file:
                image_data = file.read()

            # Insert user information into the "RESIDENT" table
            insert_query = "INSERT INTO RESIDENT (RES_FNAME, RES_MNAME, RES_LNAME, RES_SUFFIX, RES_GENDER, " \
                           "RES_CIVILSTATUS, RES_CITIZENSHIP, RES_DOB, RES_RELIGION, RES_ADDRESSLINE, RES_BARANGAY, " \
                           "RES_CITY, RES_REGION, RES_OCCUPATION, RES_MOBILENUMBER, RES_EMAIL, RES_POB, " \
                           "RES_DATEREGISTERED, STAFF_ID, RES_ISREMOVED, RES_ISOFFICIAL, RES_PICTURE) " \
                           "VALUES (%(fname)s, %(mname)s, %(lname)s, %(suffix)s, %(gender)s, %(civilstatus)s, " \
                           "%(citizenship)s, %(dob)s, %(religion)s, %(addressline)s, %(barangay)s, %(city)s, " \
                           "%(region)s, %(occupation)s, %(mobilenumber)s, %(email)s, %(pob)s, %(date_registered)s, " \
                           "%(staff_id)s, %(isremoved)s, %(isofficial)s, %(picture)s)"

            resident_data = {
                'fname': firstname_input_value,
                'lname': lastname_input_value,
                'mname': middlename_input_value,
                'suffix': suffix_input_value,
                'gender': gender_input_value,
                'citizenship': citizenship_input_value,
                'civilstatus': civil_status_input_value,
                'dob': bday_input_value,
                'religion': religion_input_value,
                'addressline': addressline_input_value,
                'barangay': barangay_input_value,
                'city': city_input_value,
                'region': region_input_value,
                'occupation': occupation_input_value,
                'mobilenumber': contact_number_input_value,
                'email': email_address_input_value,
                'pob': place_of_birth_input_value,
                'date_registered': resident_date,
                'staff_id': staff_id,
                'isremoved': resident_isremoved,
                'isofficial': resident_isofficial,
                'picture': Binary(image_data)
            }

            # Execute the insert query
            cursor.execute(insert_query, resident_data)
            conn.commit()

            # Get the newly inserted resident's ID
            cursor.execute("SELECT LASTVAL()")
            new_resident_id = cursor.fetchone()[0]

            # Show success message
            QMessageBox.information(self, "Success", "User information stored in the database.")
            insert_history(new_resident_id, "Added Resident", staff_id)
            self.go_resident()


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

    def go_homepage(self):
        resident = ResidentWindow()
        resident.go_homepage()

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        resident = ResidentWindow()
        resident.go_logout()


    def back(self):
        homepage = HomepageWindow()
        homepage.go_resident()

    def go_resident(self):
        resident = ResidentWindow()
        widget_function(resident)

class ResidentUpdateWindow(QMainWindow):
    def __init__(self,residentid):
        super(ResidentUpdateWindow, self).__init__()
        loadUi("ui/resident_update_resident.ui", self)
        self.resident_id = residentid
        self.staff_username
        self.staff_image
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

        staffusername = self.staff_username
        staffimage = self.staff_image

        homepagebtn = self.homepage_button
        officialbtn = self.official_button
        logoutbtn = self.logout_button
        backbtn = self.back_button
        addbtn = self.add_button
        savechangesbtn = self.save_changes_button

        homepagebtn.clicked.connect(self.go_homepage)
        officialbtn.clicked.connect(self.go_official)
        logoutbtn.clicked.connect(self.go_logout)
        backbtn.clicked.connect(self.back)
        addbtn.clicked.connect(self.capture_image)
        savechangesbtn.clicked.connect(self.validate_resident_input)
        self.display_staffinfo()

    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

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
            global staffDict
            staff_id = staffDict["STAFF_ID"]
            insert_history(self.resident_id, "Updated Resident", staff_id)
            resident = ResidentWindow()
            widget_function(resident)


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

    def go_homepage(self):
        resident = ResidentWindow()
        resident.go_homepage()

    def go_official(self):
        homepage = HomepageWindow()
        homepage.go_official()

    def go_logout(self):
        resident = ResidentWindow()
        resident.go_logout()

    def add(self): # image
        resident_add = ResidentAddWindow()
        resident_add.add()

    def back(self):
        resident_add = ResidentAddWindow()
        resident_add.back()

class ResidentOfficialWindow(QMainWindow):
    def __init__(self):
        super(ResidentOfficialWindow, self).__init__()
        loadUi("ui/resident_official.ui", self)

        self.staffusername = self.staff_username

        self.officials = [
            ("Captain", self.captain_img, self.captain_display),
            ("Secretary", self.secretary_img, self.secretary_display),
            ("Treasurer", self.treasurer_img, self.treasurer_display)
        ] + [(f"Councilor {i + 1}", getattr(self, f"councilor_img{i + 1}"),
              getattr(self, f"councilor_display_{i + 1}")) for i in range(8)]

        self.homepage_button.clicked.connect(self.go_homepage)
        self.resident_button.clicked.connect(self.go_resident)
        self.logout_button.clicked.connect(self.go_logout)

        self.display_staffinfo()
        self.load_officials_info()

    def load_officials_info(self):
        for official_title, img_label, display_label in self.officials:
            self.set_official_image_and_name(img_label, display_label, official_title)

    def set_official_image_and_name(self, image_label, name_label, official_title):
        image_data = self.get_official_image(official_title)
        if image_data:
            image = QImage.fromData(image_data)
            pixmap = QPixmap.fromImage(image)
            image_label.setPixmap(pixmap)

        official_name = self.get_official_name(official_title)
        if official_name:
            name_label.setText(official_name)
            font = QFont(name_label.font())
            font.setPointSize(15)  # Adjust the size as desired
            name_label.setFont(font)

    def get_official_image(self, official_title):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()
            select_query = """
                SELECT res_picture
                FROM resident
                INNER JOIN official ON resident.res_id = official.res_id
                WHERE official.off_title = %s AND res_isofficial = 'true' AND official.off_isremoved = 'false'
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


    def display_staffinfo(self):
        global staffDict
        staff_id = staffDict["STAFF_ID"]
        staff_lname = staffDict["STAFF_LNAME"]
        staff_fname = staffDict["STAFF_FNAME"]
        self.staff_username.setText(staff_fname + " " + staff_lname)

    def get_official_name(self, official_title):
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )
            cursor = conn.cursor()
            select_query = """
                SELECT res_fname || ' ' || res_lname
                FROM resident
                INNER JOIN official ON resident.res_id = official.res_id
                WHERE official.off_title = %s AND res_isofficial = 'true' AND official.off_isremoved = 'false'
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

    def go_homepage(self):
        resident = ResidentWindow()
        resident.go_homepage()

    def go_resident(self):
        homepage = HomepageWindow()
        homepage.go_resident()

    def go_logout(self):
        homepage = HomepageWindow()
        homepage.go_logout()


app = QApplication(sys.argv)
login = LoginWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.showFullScreen()
widget.show()
app.exec()