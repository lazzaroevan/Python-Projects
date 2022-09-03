import sys

from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtCore,QtWidgets,QtWebEngineWidgets
from PyQt6 import uic


class WikipediaExplorerGui(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("wikipediaExplorerGui.ui",self)
        self.openWebpageButton.clicked.connect(self.openWebPage)
    def openWebPage(self):
        for i in reversed(range(self.gridLayout_2.count())):
            self.gridLayout_2.itemAt(i).widget().setParent(None)
        file = "C:\\Users\\lazza\\Desktop\\Test\\DINOSAUR\\HTML\\0.txt"
        with open(file,'r') as f:
            htmlDoc = f.read()
        self.m_output = QtWebEngineWidgets.QWebEngineView()
        path = QtCore.QFile("css/styles.css")
        self.gridLayout_2.addWidget(self.m_output)
        self.m_output.setHtml(htmlDoc)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = WikipediaExplorerGui()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Exited")
