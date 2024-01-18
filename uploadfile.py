import sys
import traceback
from datetime import datetime

import psycopg2
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Establish a connection to the database
conn = psycopg2.connect(
    host="localhost",
    database="bis",
    user="postgres",
    password="posgre"
)

class FileUploadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('File Upload')
        self.setGeometry(100, 100, 400, 300)

        self.file_label = QLabel(self)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setGeometry(20, 20, 360, 180)

        self.upload_button = QPushButton('Upload', self)
        self.upload_button.setGeometry(150, 220, 100, 30)
        self.upload_button.clicked.connect(self.upload_file)

    def generate_filename(self,res_id, doc_type):
        filename = f"document_{res_id}.{doc_type}"
        return filename

    def upload_file(self):
        staff_id = 10001
        res_id = 10004
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter('Document Files (*.doc *.pdf *.docx);;Image Files (*.png *.jpg)')

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            doc_filedata = selected_files[0]

            doc_type = doc_filedata.split('.')[-1].lower()
            if doc_type not in ['png', 'jpg', 'jpeg', 'doc', 'docx']:
                QMessageBox.critical(self,"Invalid file format. Only PNG, JPG, and DOC files are allowed.")
                return

            try:
                # Reading the file into binary
                with open(doc_filedata, 'rb') as file:
                    file_data = file.read()

                filename = self.generate_filename(res_id,doc_type)
                timestamp = datetime.now()
                doc_datecreated = timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Data created
                doc_isremoved = 'FALSE'
                # Insert filename and file data into the database
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO document (doc_filename, doc_filedata, doc_type, doc_datecreated ,res_id ,staff_id, doc_isremoved) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (filename, file_data, doc_type, doc_datecreated, res_id, staff_id, doc_isremoved))
                    conn.commit()
                    QMessageBox.information(self, "Success","File is uploaded successfully!")
                except (Exception, psycopg2.Error) as error:
                    QMessageBox.critical(self, "Error", f"Error opening the file: {str(error)}")

                finally:
                    cursor.close()

                pixmap = QPixmap(doc_filedata)
                self.file_label.setPixmap(pixmap.scaled(360, 180, Qt.AspectRatioMode.KeepAspectRatio))

            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Error opening the file: {str(ex)}")
                traceback.print_exc()

app = QApplication(sys.argv)
window = FileUploadWindow()
window.show()
sys.exit(app.exec())

# Close the database connection
conn.close()
