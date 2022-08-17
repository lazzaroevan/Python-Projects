import os
import sys
import wikipedia
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QFileDialog
from PyQt6 import QtCore, QtGui, QtWidgets

class WikipediaLinkGetter(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("wikipediaGui.ui",self)
        self.setWindowTitle("Wikipedia Link Getter")
        self.tryWikipediaSearchButton.clicked.connect(self.searchWikipedia)
        self.saveDirectoryButton.clicked.connect(self.browseFiles)

    def browseFiles(self):
        home_dir = str(os.getcwd())
        fname = QFileDialog.getExistingDirectory(self, 'Select Directory', home_dir)
        self.filePathLabel.setText(fname)
        self.filePathLabel.setToolTip(fname)

    def searchWikipedia(self):
        self.listOfLinksBox.clear()
        searchText = self.searchTerm.text()
        print(searchText)
        self.isComplete = False
        links = []
        summary = ''
        firstAttempt = True
        while not self.isComplete:
            try:
                if firstAttempt:
                    firstAttempt = False
                    page = wikipedia.page(searchText,auto_suggest=False)
                    self.isComplete = True
                else:
                    self.isComplete = True
                    self.disambigApp.exec()
                    searchText = self.disambigApp.searchText
                    page = wikipedia.page(searchText)
                if isinstance(page,wikipedia.WikipediaPage):
                    summary = page.title+': ' +page.summary
                    links = page.links
            except SystemExit:
                print("Exited")
                self.isComplete = False
                firstAttempt = True
            except wikipedia.DisambiguationError as e:
                print("DisambigError: "+ searchText)
                print(e)
                newPages = e.options
                self.disambigApp = DisambiguationPage(newPages, parent=self)
                self.isComplete = False
            except wikipedia.exceptions.WikipediaException:
                print("SearchIsBusy")
                self.isComplete = False
                firstAttempt = True
        for i in links:
            self.listOfLinksBox.addItem(i)
        self.summaryTextBox.setText(summary)

class DisambiguationPage(QDialog):
    def __init__(self, otherPages, parent = None):
        self.pagesDict = {}
        self.searchText = "Apple"
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


