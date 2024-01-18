import sys
import psycopg2
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from docxtpl import DocxTemplate
from datetime import datetime
import os


class GenerateCertificate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Information")
        self.setGeometry(100, 100, 700, 400)

        # Create user ID label and input
        self.user_id_label = QLabel("User ID:", self)
        self.user_id_label.move(50, 50)
        self.user_id_input = QLineEdit(self)
        self.user_id_input.move(150, 50)

        # Create buttons
        self.get_info_button = QPushButton("Get Information", self)
        self.get_info_button.move(150, 100)
        self.get_info_button.clicked.connect(self.get_user_info)
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.move(250, 100)
        self.clear_button.clicked.connect(self.clear_form)

        # Create labels to display user information
        self.labels = [
            QLabel("First Name:", self),
            QLabel("Last Name:", self),
            QLabel("Suffix:", self),
            QLabel("Gender:", self),
            QLabel("Date of Birth:", self),
            QLabel("Street:", self),
            QLabel("Contact Number:", self),
            QLabel("Email Address:", self)
        ]

        positions = [(50, 150), (50, 180), (50, 210), (50, 240), (50, 270), (200, 150), (200, 180), (200, 210)]

        for label, position in zip(self.labels, positions):
            label.move(*position)

        # Create buttons for barangay clearance, certificate of indigency, and certificate of residency
        self.brgy_clearance_button = QPushButton("Barangay Clearance", self)
        self.brgy_clearance_button.move(50, 320)
        self.brgy_clearance_button.setEnabled(False)
        self.brgy_clearance_button.clicked.connect(self.generate_brgy_clearance)

        self.certificate_indigency_button = QPushButton("Certificate of Indigency", self)
        self.certificate_indigency_button.move(180, 320)
        self.certificate_indigency_button.setEnabled(False)
        self.certificate_indigency_button.clicked.connect(self.generate_certificate_indigency)

        self.certificate_residency_button = QPushButton("Certificate of Residency", self)
        self.certificate_residency_button.move(320, 320)
        self.certificate_residency_button.setEnabled(False)
        self.certificate_residency_button.clicked.connect(self.generate_certificate_residency)

    def get_user_info(self, user_id):
        user_id = user_id



        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host="localhost",
                database="bis",
                user="postgres",
                password="posgre"
            )

            # Create a cursor object
            cursor = conn.cursor()

            # Fetch user information from the database using the User ID
            select_query = "SELECT RES_FNAME, RES_MNAME, RES_LNAME, RES_SUFFIX, RES_GENDER, " \
                           "RES_DOB, RES_ADDRESSLINE, RES_EMAIL, RES_CIVILSTATUS, RES_ID " \
                           "FROM resident " \
                           "WHERE RES_ID = %s"

            cursor.execute(select_query, (user_id,))
            user_info = cursor.fetchall()

            if user_info:
                # Calculate the age based on the date of birth and the current date
                dob = user_info[5]
                current_date = datetime.now().date()
                age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

                # Display user information
                for label, value in zip(self.labels, user_info):
                    label.setText(f"{label.text().split(':')[0]}: {str(value)}")

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
                # Clear the labels and disable the buttons
                self.clear_form()
                QMessageBox.warning(self, "Error", "User ID not found in the database.")

            conn.commit()

        except (Exception, psycopg2.Error) as error:
            QMessageBox.critical(self, "Error", f"Error accessing database: {error}")

        finally:
            # Close the database connection
            if conn:
                conn.close()
                print("Database connection closed.")

    def clear_form(self):
        # Clear the labels
        for label in self.labels:
            label.setText(label.text().split(':')[0] + ":")

        # Clear the User ID input
        self.user_id_input.clear()

        # Disable the buttons for generating certificates
        self.brgy_clearance_button.setEnabled(False)
        self.certificate_indigency_button.setEnabled(False)
        self.certificate_residency_button.setEnabled(False)


    def generate_brgy_clearance(self):
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
        transaction_id = "10001"  # as if of the transaction ID
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
            cert_filename = filename
            cert_filedata = filedata
            cert_type = ".docx"
            cert_datecreated = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            cert_query = "INSERT INTO certificates (cert_filename, cert_filedata, cert_type, cert_datecreated) " \
                         "VALUES (%s, %s, %s, %s)"
            cert_values = (cert_filename, cert_filedata, cert_type, cert_datecreated)
            cursor.execute(cert_query, cert_values)
            conn.commit()
            QMessageBox.information(self, "Barangay Clearance",
                                    "Success")

            # Close the database connection
            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Barangay Clearance: {str(e)}")

    def generate_certificate_indigency(self):
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
        resident_id =  self.user_info["ID"]
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
            QMessageBox.information(self, "Certificate of Indigency", "Certificate of Indigency generated successfully.")

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
            cert_filename = filename
            cert_filedata = filedata
            cert_type = ".docx"
            cert_datecreated = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            cert_query = "INSERT INTO certificates (cert_filename, cert_filedata, cert_type, cert_datecreated) " \
                         "VALUES (%s, %s, %s, %s)"
            cert_values = (cert_filename, cert_filedata, cert_type, cert_datecreated)
            cursor.execute(cert_query, cert_values)

            conn.commit()
            QMessageBox.information(self, "Certificate of Indigency",
                                    "Success")
            # Close the database connection
            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Barangay Clearance: {str(e)}")

    def generate_certificate_residency(self):
        # Implement logic for generating certificate of residency
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

            # Read the file data
            with open(filename, 'rb') as file:
                filedata = file.read()

            conn = psycopg2.connect(
                database="brgy_users",
                user="postgres",
                password="posgre",
                host="localhost",
                port="5432"
            )

            cursor = conn.cursor()
            # Insert cert data into the database
            cert_filename = filename
            cert_filedata = filedata
            cert_type = ".docx"
            cert_datecreated = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            cert_query = "INSERT INTO certificate (cert_filename, cert_filedata, cert_type, cert_datecreated) " \
                         "VALUES (%s, %s, %s, %s)"
            cert_values = (cert_filename, cert_filedata, cert_type, cert_datecreated)
            cursor.execute(cert_query, cert_values)

            conn.commit()
            QMessageBox.information(self, "Certificate of Residency",
                                    "Success")
            # Close the database connection
            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Certificate of Residency: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GenerateCertificate()
    window.show()
    sys.exit(app.exec())
