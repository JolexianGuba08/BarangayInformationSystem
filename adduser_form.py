import os
import sys
import traceback

import cv2
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt
import psycopg2
from psycopg2 import Binary


class ResidentForm(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Form")
        self.setGeometry(100, 100, 600, 600)

        # Create labels
        labels = [
            QLabel("First Name:", self),
            QLabel("Middle Name:", self),
            QLabel("Last Name:", self),
            QLabel("Suffix:", self),
            QLabel("Gender:", self),
            QLabel("Civil Status:", self),
            QLabel("Citizenship:", self),
            QLabel("Date of Birth (YYYY-MM-DD):", self),
            QLabel("Religion:", self),
            QLabel("Address Line:", self),
            QLabel("Barangay:", self),
            QLabel("City:", self),
            QLabel("Region:", self),
            QLabel("Occupation:", self),
            QLabel("Mobile Number:", self),
            QLabel("Email Address:", self),
            QLabel("Place of Birth:", self)
        ]

        positions = [(50, 80), (50, 110), (50, 140), (50, 170), (50, 200),
                     (50, 230), (50, 260), (50, 290), (50, 320), (50, 350), (50, 380),
                     (50, 410), (50, 440), (50, 470), (50, 500), (50, 530), (50, 560)]

        for label, position in zip(labels, positions):
            label.move(*position)

        # Create line edits
        self.line_edits = {}
        positions = [(150, 80), (150, 110), (150, 140), (150, 170), (150, 200),
                     (150, 230), (150, 260), (150, 290), (150, 320), (150, 350), (150, 380),
                     (150, 410), (150, 440), (150, 470), (150, 500), (150, 530), (150, 560)]

        for position in positions:
            line_edit = QLineEdit(self)
            line_edit.move(*position)
            self.line_edits[position[1]] = line_edit

        # Create place of birth line edit
        self.place_of_birth_line_edit = QLineEdit(self)
        self.place_of_birth_line_edit.move(150, 560)
        self.line_edits[560] = self.place_of_birth_line_edit

        # Create buttons
        self.capture_bttn = QPushButton("Capture Image", self)
        self.capture_bttn.move(50, 600)
        self.cancel_bttn = QPushButton("Cancel", self)
        self.cancel_bttn.move(160, 600)
        self.add_resident_bttn = QPushButton("Add Resident", self)
        self.add_resident_bttn.move(270, 600)
        self.add_resident_bttn.setEnabled(False)

        # Connect button signals to slots
        self.capture_bttn.clicked.connect(self.capture_image)
        self.cancel_bttn.clicked.connect(self.cancel_capture)
        self.add_resident_bttn.clicked.connect(self.submit_form)

    def capture_image(self):
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

        # Release the VideoCapture object and close the display windows
        cap.release()
        cv2.destroyAllWindows()

    def cancel_capture(self):
        # Delete the captured image file
        if hasattr(self, "add_resident_image_file") and self.add_resident_image_file is not None:
            os.remove(self.add_resident_image_file)
            self.add_resident_image_file = None
            self.validate_resident_input()

    def validate_resident_input(self):
        input_values = [line_edit.text().strip() for line_edit in self.line_edits.values()]

        if all(input_values) and hasattr(self, "add_resident_image_file") and self.add_resident_image_file is not None:
            self.add_resident_bttn.setEnabled(True)
        else:
            self.add_resident_bttn.setEnabled(False)

    def submit_form(self):
        input_values = [line_edit.text().strip() for line_edit in self.line_edits.values()]
        # Get the current date
        resident_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
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
                image_data = bytearray(file.read())

            # Insert user information into the "RESIDENT" table
            insert_query = "INSERT INTO RESIDENT (RES_FNAME, RES_MNAME, RES_LNAME, RES_SUFFIX, RES_GENDER, " \
                           "RES_CIVILSTATUS, RES_CITIZENSHIP, RES_DOB, RES_RELIGION, RES_ADDRESSLINE, RES_BARANGAY, " \
                           "RES_CITY, RES_REGION, RES_OCCUPATION, RES_MOBILENUMBER, RES_EMAIL, RES_POB, " \
                           "RES_DATEREGISTERED, STAFF_ID, RES_ISREMOVED, RES_ISOFFICIAL, RES_PICTURE) " \
                           "VALUES (%(fname)s, %(mname)s, %(lname)s, %(suffix)s, %(gender)s, %(civilstatus)s, " \
                           "%(citizenship)s, %(dob)s, %(religion)s, %(addressline)s, %(barangay)s, %(city)s, " \
                           "%(region)s, %(occupation)s, %(mobilenumber)s, %(email)s, %(pob)s, %(date_registered)s, " \
                           "%(staff_id)s, %(isremoved)s, %(isofficial)s, %(picture)s)"

            # Create a dictionary with the input values
            resident_data = {
                'fname': input_values[0],
                'mname': input_values[1],
                'lname': input_values[2],
                'suffix': input_values[3],
                'gender': input_values[4],
                'civilstatus': input_values[5],
                'citizenship': input_values[6],
                'dob': input_values[7],
                'religion': input_values[8],
                'addressline': input_values[9],
                'barangay': input_values[10],
                'city': input_values[11],
                'region': input_values[12],
                'occupation': input_values[13],
                'mobilenumber': input_values[14],
                'email': input_values[15],
                'pob': input_values[16],
                'date_registered': resident_date,
                'staff_id': 10001,
                'isremoved': resident_isremoved,
                'isofficial': resident_isofficial,
                'picture': Binary(image_data)
            }

            # Execute the insert query
            cursor.execute(insert_query, resident_data)
            conn.commit()

            # Show success message
            QMessageBox.information(self, "Success", "User information stored in the database.")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ResidentForm()
    form.show()
    sys.exit(app.exec())
