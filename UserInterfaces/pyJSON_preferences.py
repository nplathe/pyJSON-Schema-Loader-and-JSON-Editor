# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pyJSON_preferences.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_PrefDiag(object):
    def setupUi(self, PrefDiag):
        if not PrefDiag.objectName():
            PrefDiag.setObjectName(u"PrefDiag")
        PrefDiag.resize(400, 300)
        self.verticalLayout_2 = QVBoxLayout(PrefDiag)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.groupBox = QGroupBox(PrefDiag)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label)

        self.checkBox_verboseLog = QCheckBox(self.groupBox)
        self.checkBox_verboseLog.setObjectName(u"checkBox_verboseLog")

        self.verticalLayout_3.addWidget(self.checkBox_verboseLog)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(PrefDiag)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label_2)

        self.checkBox_ShowErrors = QCheckBox(self.groupBox_2)
        self.checkBox_ShowErrors.setObjectName(u"checkBox_ShowErrors")

        self.verticalLayout_4.addWidget(self.checkBox_ShowErrors)


        self.verticalLayout.addWidget(self.groupBox_2)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.pushButton_save = QPushButton(PrefDiag)
        self.pushButton_save.setObjectName(u"pushButton_save")

        self.horizontalLayout.addWidget(self.pushButton_save)

        self.pushButton_cancel = QPushButton(PrefDiag)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.horizontalLayout.addWidget(self.pushButton_cancel)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(PrefDiag)

        QMetaObject.connectSlotsByName(PrefDiag)
    # setupUi

    def retranslateUi(self, PrefDiag):
        PrefDiag.setWindowTitle(QCoreApplication.translate("PrefDiag", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("PrefDiag", u"Logging", None))
        self.label.setText(QCoreApplication.translate("PrefDiag", u"When this box is checked, the logs of pyJSON will be stored in a directory called \"Logs\". Otherwise, no logs will be written to the drive.", None))
        self.checkBox_verboseLog.setText(QCoreApplication.translate("PrefDiag", u"Create Log Files", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PrefDiag", u"Error Representation", None))
        self.label_2.setText(QCoreApplication.translate("PrefDiag", u"If this box is checked, structural mismatches and errors in the tabular view are shown. Otherwise, a blank description is set.", None))
        self.checkBox_ShowErrors.setText(QCoreApplication.translate("PrefDiag", u"Show Errors in Table", None))
        self.pushButton_save.setText(QCoreApplication.translate("PrefDiag", u"Save", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("PrefDiag", u"Cancel", None))
    # retranslateUi

