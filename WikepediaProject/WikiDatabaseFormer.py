import os
import shutil
import sys
import requests
import wikipedia
from wikipedia import exceptions
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QAbstractItemView
from PyQt6 import QtCore, QtWidgets
import webbrowser

class WikipediaLinkGetter(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("guis/wikipediaGui.ui",self)
        self.setWindowTitle("Wikipedia Link Getter")
        self.tryWikipediaSearchButton.clicked.connect(self.searchWikipedia)
        self.saveDirectoryButton.clicked.connect(self.browseFiles)
        self.saveFilesButton.clicked.connect(self.saveDatabase)
        self.listOfLinksBox.itemDoubleClicked.connect(self.openBrowser)
        self.listOfLinksBox.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.startPage = None
        self.setStyleSheet("font-size: 10pt")
        self.disambigLinks = []

    def browseFiles(self):
        home_dir = str(os.getcwd())
        fname = QFileDialog.getExistingDirectory(self, 'Select Directory', home_dir)
        self.filePathLabel.setText(fname)
        self.filePathLabel.setToolTip(fname)
        self.saveFilesButton.setEnabled(True)

    def saveDatabase(self):
        numLinks = len(self.links)
        print(numLinks)
        self.progressBar.setRange(0, numLinks)
        self.thread = TaskThread(self.filePathLabel.text() + '/' +self.searchTerm.text().upper(),self.picturesCheck.isChecked(),self.listOfLinksBox,self.startPage,self.disambigLinks)
        self.thread.moveToThread(self.thread)
        self.thread.started.connect(self.thread.run)
        self.thread.progress.connect(self.progressBarUp)
        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.littleProgress.connect(self.littleProgress)
        self.thread.saveProgress.connect(self.saveFileProgress)

        self.thread.start()

    def littleProgress(self,tuple):
        link = tuple[2]
        link.setText(link.text() + ':')
        name = link.text().split(':')[0] + ': Sublinks: ' + str(tuple[0]) + '/' + str(tuple[1])
        link.setText(name)

    def progressBarUp(self,num):
        self.progressTracker.setText(str(int(self.progressTracker.text().split('/')[0])+1) + '/' + str(len(self.links)))
        brush = QBrush()
        brush.setColor(QColor.fromRgb(0, 255, 0))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.listOfLinksBox.item(self.progressBar.value()).setBackground(brush)
        self.progressBar.setValue(num + int(self.progressBar.value()))

    def saveFileProgress(self,tuple):
        link = tuple[2]
        link.setText(link.text() + ':')
        name = link.text().split(':')[0] + ': Saving links: ' + str(tuple[0]) + '/' + str(tuple[1])
        link.setText(name)

    def searchWikipedia(self):
        self.listOfLinksBox.clear()
        searchText = self.searchTerm.text()
        self.isComplete = False
        self.links = []
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
                    self.searchTerm.setText(searchText)
                    page = wikipedia.page(searchText,auto_suggest=False)
                if isinstance(page,wikipedia.WikipediaPage):
                    summary = page.title +': ' +page.summary
                    self.links = page.links
                    self.startPage = page
            except SystemExit:
                print("Exited")
                self.isComplete = False
                firstAttempt = True
            except wikipedia.DisambiguationError as e:
                print("Disambiguation Error: "+ searchText)
                print(e)
                newPages = e.options
                self.disambigApp = DisambiguationPage(newPages, parent=self)
                self.isComplete = False
            except wikipedia.exceptions.WikipediaException:
                print("Spelling Error?")
                newPages = wikipedia.search(wikipedia.suggest(searchText))
                self.disambigApp = DisambiguationPage(newPages, parent=self)
                self.isComplete = False
        for i in self.links:
            self.listOfLinksBox.addItem(i)
        self.summaryTextBox.setText(summary)
        self.saveDirectoryButton.setEnabled(True)
        self.progressTracker.setText(str(0) + '/' + str(len(self.links)))

    def openBrowser(self,qlistItem):
        url = 'https://en.wikipedia.org/wiki/'
        url = url + qlistItem.text()
        webbrowser.open(url)

class DisambiguationPage(QDialog):
    def __init__(self, otherPages, parent = None):
        self.pagesDict = {}
        self.searchText = "Apple"
        self.complete = False
        super().__init__(parent)
        uic.loadUi("guis/disambiguationPage.ui",self)
        self.select.clicked.connect(self.buttonPressed)
        for i in otherPages:
            self.pagesDict[i] = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_7)
            self.pagesDict[i].setMinimumSize(QtCore.QSize(89, 20))
            self.pagesDict[i].setText(i)
            self.pagesDict[i].setObjectName(i)
            self.verticalLayout_8.addWidget(self.pagesDict[i])

    def buttonPressed(self):
        for i in self.pagesDict:
            if self.pagesDict[i].isChecked():
                self.searchText = i
                self.complete = True
                self.accept()
        self.reject()

class TaskThread(QtCore.QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    littleProgress = pyqtSignal(tuple)
    saveProgress = pyqtSignal(tuple)

    def __init__(self,filePath,imageCheck,linkBox,startPage,disambigList):
        QtCore.QThread.__init__(self,parent=None)
        self.links = []
        self.filePath = filePath
        self.picturesCheck = imageCheck
        self.linksBox = linkBox
        self.startPage = startPage
        self.disambigList =  disambigList
        self.disambig = False

    def downloadPage(self,directoryPath,wikiPage,uuid):
        forPathUse = str(uuid)
        summaryPath = directoryPath + "/summary"
        imagesPath = directoryPath + "/images"
        fullPagePath = directoryPath + "/fullPage"
        htmlPath = directoryPath + "/HTML"
        linksPath = directoryPath + "/links"
        if not os.path.exists(summaryPath):
            os.mkdir(summaryPath)
        if not os.path.exists(htmlPath):
            os.mkdir(htmlPath)
        if not os.path.exists(imagesPath):
            os.mkdir(imagesPath)
        if not os.path.exists(fullPagePath):
            os.mkdir(fullPagePath)
        if not os.path.exists(linksPath):
            os.mkdir(linksPath)
        self.imgTypes = ['bmp', 'jpeg', 'tiff', 'tif', '.gif', 'png', 'jpg']
        summary = wikiPage.summary
        fullPage = wikiPage.content
        htmlDoc = wikiPage.html()
        tempSummaryPath = summaryPath + '/' + forPathUse + '.txt'
        tempFullPagePath = fullPagePath + '/' + forPathUse + '.txt'
        tempHTMLPath = htmlPath + '/' + forPathUse + '.txt'
        tempLinksPath = linksPath + '/' +forPathUse + '.txt'
        with open(tempSummaryPath, 'w', encoding="utf-8") as f:
            f.write((summary))
            f.close()
        with open(tempLinksPath, 'w', encoding="utf-8") as f:
            for link in wikiPage.links:
                f.write((link))
            f.close()
        with open(tempHTMLPath, 'w', encoding="utf-8") as f:
            f.write((htmlDoc))
            f.close()
        with open(tempFullPagePath, 'w', encoding="utf-8") as f:
            f.write((fullPage))
            f.close()
        ## image checkbox check
        if (self.picturesCheck):
            try:
                images = wikiPage.images
                tempImagesPath = imagesPath + '/' + forPathUse
                imgFolder = imagesPath + '/' + forPathUse
                if not os.path.exists(imgFolder):
                    os.mkdir(imgFolder)
                    imgCount = 0
                    imgDirectoryManagerFile = imgFolder + '/' + forPathUse + '.txt'
                    with open(imgDirectoryManagerFile, 'w') as g:
                        for a in images:
                            if isinstance(a, str):
                                if ('Red_Pencil_Icon.png' and 'Double-dagger-14-plain.png' not in a):
                                    fileName = a.split('/')[-1]
                                    if fileName.split('.')[-1] in self.imgTypes:
                                        headers = {
                                            'User-Agent': 'EvanCategoryWikiBot/2.0 (boomandot@gmail.com; coolbot@example.org)'}
                                        try:
                                            with open(tempImagesPath + '/' + str(imgCount) + '.' +
                                                      fileName.split('.')[-1], 'wb') as f:
                                                r = requests.get(a, stream=True, headers=headers)
                                                r.raw.decode_content = True
                                                if (r.status_code == 200):
                                                    shutil.copyfileobj(r.raw, f)
                                                    g.write(a + '\n')
                                                    imgCount += 1
                                            f.close()
                                        except OSError as e:
                                            print(e)
                    g.close()
            except KeyError as e:
                print(e)

    def run(self):
        directoryPath = self.filePath
        if not os.path.exists(directoryPath):
            os.mkdir(directoryPath)
        progressLink = []
        uuidMaker = 1
        uuidFile = directoryPath + '/uuidDirectory' + '.txt'
        if (os.path.exists(uuidFile)):
            os.remove(uuidFile)
        with open(uuidFile, 'a', encoding="utf-8") as uuidMakerFile:
            title = self.startPage.title
            uuidMakerFile.write(title + '\n')
            uuidMakerFile.close()
        self.downloadPage(directoryPath,self.startPage,0)
        for mainLinkNum in range(self.linksBox.count()):
            pageList = []
            try:
                linkItem = self.linksBox.item(mainLinkNum)
                textPage = linkItem.text()
                page = wikipedia.page(textPage, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                page = wikipedia.page(e.options[0],auto_suggest=False)
            pageList.append(page)
            progressLink.append(textPage)
            newPageLinks = page.links
            for x in newPageLinks:
                try:
                    page = wikipedia.page(x, auto_suggest=False)
                except wikipedia.DisambiguationError as e:
                    self.disambigList.append(x)
                    self.disambig = True
                    page = wikipedia.page("Word-sense_disambiguation",auto_suggest=False) #error throws here, I should compile a list of all disambig errors and then do them at the end when the user can pick which ones they want
                except exceptions.PageError:
                    page = wikipedia.page('Error',auto_suggest=False)
                pageList.append(page)
                self.littleProgress.emit((newPageLinks.index(x)+1,len(newPageLinks),linkItem))
            for d in range(len(pageList)):
                self.downloadPage(directoryPath,pageList[d],uuidMaker)
                uuidMaker += 1
                with open(uuidFile, 'a',encoding="utf-8") as uuidMakerFile:
                    title =  pageList[d].title
                    if ('\r\n' in title):
                        title = title.replace('\r\n', '')
                    uuidMakerFile.write(title + '\n')
                    uuidMakerFile.close()
                self.saveProgress.emit((d+1,len(pageList),linkItem))
            self.progress.emit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = WikipediaLinkGetter()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Exited")


