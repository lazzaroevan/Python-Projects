import sys
import wikipedia
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QDialog
from PyQt6 import QtCore, QtGui, QtWidgets, Qt

class WikipediaLinkGetter(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("wikipediaGui.ui",self)
        self.setWindowTitle("Wikipedia Link Getter")
        self.tryWikipediaSearchButton.setAutoDefault(True)
        self.tryWikipediaSearchButton.clicked.connect(self.searchWikipedia)

    def searchWikipedia(self):
        searchTerm = self.searchTerm.text()
        pages = wikipedia.search(searchTerm)
        self.disambig = QApplication(sys.argv)
        self.disambigApp = DisambiguationPage(pages,parent = self)
        self.disambigApp.show()
        sys.exit(self.disambig.exec())
        searchText = self.disambigApp.searchText
        page = wikipedia.page(searchText)
        summary = page.summary
        links = page.links
        for i in links:
            self.listOfLinksBox.addItem(i)
        self.summaryTextBox.setText(summary)

class DisambiguationPage(QDialog):
    def __init__(self, otherPages, parent = None):
        self.pagesDict = {}
        self.searchText = ""
        self.complete = False
        super().__init__(parent)
        uic.loadUi("disambiguationPage.ui",self)
        self.select.clicked.connect(self.buttonPressed)
        for i in otherPages:
            self.pagesDict[i]=QtWidgets.QRadioButton(self.scrollAreaWidgetContents_7)
            self.pagesDict[i].setMinimumSize(QtCore.QSize(89, 20))
            self.pagesDict[i].setText(i)
            self.pagesDict[i].setObjectName(i)
            self.verticalLayout_8.addWidget(self.pagesDict[i])

    def buttonPressed(self):
        for i in self.pagesDict:
            if self.pagesDict[i].isChecked():
                self.searchText = i
                self.complete=True
                self.accept()
        self.reject()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = WikipediaLinkGetter()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Exited")


