# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(628, 413)
        self.btn_left = QPushButton(Form)
        self.btn_left.setObjectName(u"btn_left")
        self.btn_left.setGeometry(QRect(340, 330, 71, 61))
        self.btn_stop = QPushButton(Form)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setGeometry(QRect(200, 350, 81, 41))
        self.btn_right = QPushButton(Form)
        self.btn_right.setObjectName(u"btn_right")
        self.btn_right.setGeometry(QRect(500, 330, 71, 61))
        self.btn_go = QPushButton(Form)
        self.btn_go.setObjectName(u"btn_go")
        self.btn_go.setGeometry(QRect(420, 260, 71, 61))
        self.btn_back = QPushButton(Form)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setGeometry(QRect(420, 330, 71, 61))
        self.auto_check = QCheckBox(Form)
        self.auto_check.setObjectName(u"auto_check")
        self.auto_check.setGeometry(QRect(20, 360, 61, 22))
        font = QFont()
        font.setPointSize(13)
        font.setItalic(True)
        self.auto_check.setFont(font)
        self.list_pose = QListWidget(Form)
        self.list_pose.setObjectName(u"list_pose")
        self.list_pose.setGeometry(QRect(20, 40, 261, 151))
        self.label_pose = QLabel(Form)
        self.label_pose.setObjectName(u"label_pose")
        self.label_pose.setGeometry(QRect(20, 20, 67, 17))
        self.list_mesage = QListWidget(Form)
        self.list_mesage.setObjectName(u"list_mesage")
        self.list_mesage.setGeometry(QRect(330, 40, 261, 151))
        self.label_ = QLabel(Form)
        self.label_.setObjectName(u"label_")
        self.label_.setGeometry(QRect(330, 20, 67, 17))
        self.btn_home = QPushButton(Form)
        self.btn_home.setObjectName(u"btn_home")
        self.btn_home.setGeometry(QRect(100, 350, 81, 41))
        self.list_total_dist = QListWidget(Form)
        self.list_total_dist.setObjectName(u"list_total_dist")
        self.list_total_dist.setGeometry(QRect(20, 240, 261, 91))
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 220, 67, 17))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_left.setText(QCoreApplication.translate("Form", u"left", None))
        self.btn_stop.setText(QCoreApplication.translate("Form", u"stop", None))
        self.btn_right.setText(QCoreApplication.translate("Form", u"right", None))
        self.btn_go.setText(QCoreApplication.translate("Form", u"go", None))
        self.btn_back.setText(QCoreApplication.translate("Form", u"back", None))
        self.auto_check.setText(QCoreApplication.translate("Form", u"auto", None))
        self.label_pose.setText(QCoreApplication.translate("Form", u"Pose", None))
        self.label_.setText(QCoreApplication.translate("Form", u"Event", None))
        self.btn_home.setText(QCoreApplication.translate("Form", u"home", None))
        self.label.setText(QCoreApplication.translate("Form", u"total_dist", None))
    # retranslateUi

