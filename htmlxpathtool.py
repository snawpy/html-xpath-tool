# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *
import requests
from lxml import etree


class Ui_Form(QWidget):
    def __init__(self):
        super(Ui_Form, self).__init__()
        self.setupUi()
        self.functions()

    def setupUi(self):
        self.setWindowTitle("Snoop Xpath Tool")
        self.resize(646, 558)
        self.main_layout = QVBoxLayout(self)

        # first row
        self.url_submit_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Fetch Url", self)
        self.url_text = QLineEdit()
        self.url_label = QLabel("Enter Url Here:", self)
        self.url_submit_layout.addWidget(self.url_label)
        self.url_submit_layout.addWidget(self.url_text)
        self.url_submit_layout.addWidget(self.fetch_button)

        # second row
        self.xpath_layout = QHBoxLayout()
        self.xpath_label = QLabel("Enter Xpath Query Here:", self)
        self.xpath_line_edit = QLineEdit()
        self.xpath_layout.addWidget(self.xpath_label)
        self.xpath_layout.addWidget(self.xpath_line_edit)

        # xpath output
        self.xpath_output = QTextBrowser()

        # add shit to the main layout
        self.main_layout.addLayout(self.url_submit_layout)
        self.main_layout.addLayout(self.xpath_layout)
        self.main_layout.addWidget(self.xpath_output)

    def functions(self):
        self.fetch_button.clicked.connect(self.fetch)
        QObject.connect(self.xpath_line_edit, SIGNAL("textChanged(QString)"),
                        self.update_result)

    def thread_instance(self):
        #    putting this here instead of the normal functions section as we
        #    can only create the instance AFTER we have gained the url and not
        #    jsut when the app is started
        self.fetch_button_instance = FetchButtonThread(self.url_text.text())

    def fetch(self):
        self.url_label.setText("Fetching Data")
        self.thread_instance()
        self.connect(self.fetch_button_instance, SIGNAL("threadDone(QString)"),
                     self.xpath_fetched, Qt.DirectConnection)
        self.xpath_output.clear()
        self.fetch_button_instance.start()

    def xpath_fetched(self, html):

        self.url_label.setText("Data Recieved")
        self.xpath_output.append("Enter xpath query above")
        self.htmlDOM = etree.HTML(html)

    def update_result(self):
        try:

            self.xpath_result = self.htmlDOM.xpath(
                self.xpath_line_edit.text())
            self.xpath_output.clear()

            #  we need to check if the result is a string or not
            #  otherwise it would print each letter
            #  on its own line if it were a string
            #  and if not we can iterate thorugh the list

            if isinstance(self.xpath_result, basestring):
                self.xpath_output.append(self.xpath_result.decode("utf-8"))
            else:
                for i in self.xpath_result:
                    self.xpath_output.append(i.decode("utf-8"))

            #  if we get unicode problems we print it with out decoding
        except UnicodeError:
            if isinstance(self.xpath_result, basestring):
                self.xpath_output.append(self.xpath_result)
            else:
                for i in self.xpath_result:
                    self.xpath_output.append(i)

        except Exception as err:
            print "There was a problem", err

    def keyPressEvent(self, event):
        try:
            if event.key() == 16777220:
                event.accept()
                self.fetch()
            else:
                event.ignore()
        except:
            pass


class FetchButtonThread(QThread):
    def __init__(self, text, parent=None):
        super(FetchButtonThread, self).__init__(parent)
        self.text = text

    def run(self):
        if "http://" not in self.text and "https://" not in self.text:
            self.text = "http://" + self.text
            print self.text
        try:
            print "working"
            response = requests.get(self.text, headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0)'
                ' Gecko/20100101 Firefox/49.0'})
            html = response.content
            self.emit(SIGNAL("threadDone(QString)"), html)

        except Exception as err:
            print err, "something went wrong reading the url"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    newAPP = Ui_Form()
    newAPP.show()
    sys.exit(app.exec_())