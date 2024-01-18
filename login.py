# Form implementation generated from reading ui file 'UI/login.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LogIn(object):
    def setupUi(self, LogIn):
        LogIn.setObjectName("LogIn")
        LogIn.resize(1200, 650)
        LogIn.setMinimumSize(QtCore.QSize(1200, 650))
        LogIn.setMaximumSize(QtCore.QSize(1200, 671))
        self.centralwidget = QtWidgets.QWidget(parent=LogIn)
        self.centralwidget.setMinimumSize(QtCore.QSize(1200, 650))
        self.centralwidget.setMaximumSize(QtCore.QSize(1111111, 1111111))
        self.centralwidget.setStyleSheet("#mainWidget{\n"
"background-color: black;\n"
"}\n"
"\n"
"#frameLeft{\n"
"background-color: green;\n"
"}\n"
"\n"
"#frameRight{\n"
"background-color: white;\n"
"}")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.mainWidget.setObjectName("mainWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.mainWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frameLeft = QtWidgets.QFrame(parent=self.mainWidget)
        self.frameLeft.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frameLeft.setStyleSheet("")
        self.frameLeft.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameLeft.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameLeft.setObjectName("frameLeft")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frameLeft)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(parent=self.frameLeft)
        self.label.setMaximumSize(QtCore.QSize(500, 500))
        self.label.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("UI\\../images&icon/logo_login.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout_2.addWidget(self.frameLeft)
        self.frameRight = QtWidgets.QFrame(parent=self.mainWidget)
        self.frameRight.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameRight.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameRight.setObjectName("frameRight")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameRight)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(parent=self.frameRight)
        self.frame.setStyleSheet("")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.label_2 = QtWidgets.QLabel(parent=self.frame)
        self.label_2.setGeometry(QtCore.QRect(140, 50, 341, 101))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.logInFrame = QtWidgets.QFrame(parent=self.frame)
        self.logInFrame.setGeometry(QtCore.QRect(90, 210, 451, 361))
        self.logInFrame.setMaximumSize(QtCore.QSize(451, 361))
        self.logInFrame.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.logInFrame.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.logInFrame.setStyleSheet("#logInFrame{\n"
"border: 2px solid rgb(189, 189, 189);\n"
"border-radius: 15px;\n"
"text-align: center;\n"
"}\n"
"\n"
"QLineEdit{\n"
"border-radius: 15px;\n"
"border: 2px solid rgb(189, 189, 189);\n"
"}\n"
"\n"
"\n"
"")
        self.logInFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.logInFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.logInFrame.setObjectName("logInFrame")
        self.label_3 = QtWidgets.QLabel(parent=self.logInFrame)
        self.label_3.setGeometry(QtCore.QRect(110, 30, 231, 51))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("border: none;")
        self.label_3.setObjectName("label_3")
        self.login_button = QtWidgets.QPushButton(parent=self.logInFrame)
        self.login_button.setGeometry(QtCore.QRect(150, 280, 161, 41))
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.login_button.setStyleSheet("#login_button{\n"
"border-radius: 10px;\n"
"border: none;\n"
"background-color: rgb(0, 133, 38);\n"
"font-size: 17px;\n"
"font-weight: bold;\n"
"color: white;\n"
"}\n"
"\n"
"#login_button:hover{\n"
"background-color: transparent;\n"
"border: 2px solid rgb(0, 133, 38);\n"
"color: rgb(0, 133, 38);\n"
"}\n"
"")
        self.login_button.setObjectName("login_button")
        self.username_input = QtWidgets.QLineEdit(parent=self.logInFrame)
        self.username_input.setGeometry(QtCore.QRect(90, 110, 281, 51))
        self.username_input.setStyleSheet("font-size: 16px;\n"
"padding: 13px;")
        self.username_input.setObjectName("username_input")
        self.password_input = QtWidgets.QLineEdit(parent=self.logInFrame)
        self.password_input.setGeometry(QtCore.QRect(90, 190, 281, 51))
        self.password_input.setStyleSheet("font-size: 16px;\n"
"padding: 13px;")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("password_input")
        self.verticalLayout.addWidget(self.frame)
        self.horizontalLayout_2.addWidget(self.frameRight)
        self.verticalLayout_2.addWidget(self.mainWidget)
        LogIn.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=LogIn)
        self.statusbar.setObjectName("statusbar")
        LogIn.setStatusBar(self.statusbar)

        self.retranslateUi(LogIn)
        QtCore.QMetaObject.connectSlotsByName(LogIn)

    def retranslateUi(self, LogIn):
        _translate = QtCore.QCoreApplication.translate
        LogIn.setWindowTitle(_translate("LogIn", "MainWindow"))
        self.label_2.setText(_translate("LogIn", "<html><head/><body><p align=\"center\">BARANGAY INFORMATION </p><p align=\"center\">SYSTEM</p></body></html>"))
        self.label_3.setText(_translate("LogIn", "<html><head/><body><p align=\"center\">LOGIN</p></body></html>"))
        self.login_button.setText(_translate("LogIn", "LOGIN"))
        self.username_input.setPlaceholderText(_translate("LogIn", "username"))
        self.password_input.setPlaceholderText(_translate("LogIn", "password"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LogIn = QtWidgets.QMainWindow()
    ui = Ui_LogIn()
    ui.setupUi(LogIn)
    LogIn.show()
    sys.exit(app.exec())
