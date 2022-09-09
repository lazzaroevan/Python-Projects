import os
import shutil
import sys
import requests
import wikipedia
from wikipedia import exceptions
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog,QMainWindow
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

    def browseFiles(self):
        home_dir = str(os.getcwd())
        fname = QFileDialog.getExistingDirectory(self, 'Select Directory', home_dir)
        self.filePathLabel.setText(fname)
        self.filePathLabel.setToolTip(fname)

    def saveDatabase(self):
        numLinks = len(self.links)
        print(numLinks)
        self.progressBar.setRange(0, numLinks)
        self.thread = TaskThread(self.links,self.filePathLabel.text() + '/' +self.searchTerm.text().upper(),self.picturesCheck.isChecked())
        self.thread.moveToThread(self.thread)
        self.thread.started.connect(self.thread.run)
        self.thread.progress.connect(self.progressBarUp)
        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.littleProgress.connect(self.littleProgress)
        self.thread.saveProgress.connect(self.saveFileProgress)

        self.thread.start()

    def littleProgress(self,tuple):
        link = self.listOfLinksBox.findItems(tuple[2],Qt.MatchFlag.MatchExactly)
        for i in link:
            i.setText(i.text() + ':')
            name = i.text().split(':')[0] + ': Sublinks: ' + str(tuple[0]) + '/' + str(tuple[1])
            i.setText(name)

    def progressBarUp(self,num):
        self.progressTracker.setText(str(num) + len(self.links))
        brush = QBrush()
        brush.setColor(QColor.fromRgb(0, 255, 0))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.listOfLinksBox.item(self.progressBar.value()).setBackground(brush)
        self.progressBar.setValue(num + int(self.progressBar.value()))

    def saveFileProgress(self,tuple):
        link = self.listOfLinksBox.findItems(tuple[2],Qt.MatchFlag.MatchExactly)
        for i in link:
            i.setText(link.text() + ':')
            name = i.text().split(':')[0] + ': Saving links: ' + str(tuple[0]) + '/' + str(tuple[1])
            i.setText(name)

    def searchWikipedia(self):
        self.listOfLinksBox.clear()
        searchText = self.searchTerm.text()
        print(searchText)
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
                    page = wikipedia.page(searchText)
                if isinstance(page,wikipedia.WikipediaPage):
                    summary = page.title +': ' +page.summary
                    self.links = page.links
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
        for i in self.links:
            self.listOfLinksBox.addItem(i)
        self.summaryTextBox.setText(summary)

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

class TaskThread(QtCore.QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    littleProgress = pyqtSignal(tuple)
    saveProgress = pyqtSignal(tuple)

    def __init__(self,links,filePath,imageCheck):
        QtCore.QThread.__init__(self,parent=None)
        self.links = links
        self.filePath = filePath
        self.picturesCheck = imageCheck

    def downloadPage(self):
        pass

    def run(self):
        directoryPath = self.filePath
        summaryPath = directoryPath + "/summary"
        imagesPath = directoryPath + "/images"
        fullPagePath = directoryPath + "/fullPage"
        htmlPath = directoryPath + "/HTML"
        secondLinks = []
        progressLink = []
        if not os.path.exists(directoryPath):
            os.mkdir(directoryPath)
        if not os.path.exists(summaryPath):
            os.mkdir(summaryPath)
        if not os.path.exists(htmlPath):
            os.mkdir(htmlPath)
        if not os.path.exists(imagesPath):
            os.mkdir(imagesPath)
        if not os.path.exists(fullPagePath):
            os.mkdir(fullPagePath)
        self.imgTypes = ['bmp', 'jpeg', 'tiff', 'tif', '.gif', 'png', 'jpg']
        uuidMaker = 0
        uuidFile = directoryPath + '/uuidDirectory' + '.txt'
        if (os.path.exists(uuidFile)):
            os.remove(uuidFile)
        for i in range(len(self.links)):
            pageList = []
            try:
                page = wikipedia.page(self.links[i], auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                page = wikipedia.page(e.options[0])
            pageList.append(page)
            progressLink.append(self.links[i])
            newPageLinks = page.links
            for x in newPageLinks:
                try:
                    page = wikipedia.page(x, auto_suggest=False)
                except wikipedia.DisambiguationError as e:
                    page = wikipedia.page(e.options[0])
                except exceptions.PageError:
                    page = wikipedia.page('Error')
                pageList.append(page)
                self.littleProgress.emit((newPageLinks.index(x)+1,len(newPageLinks),self.links[i]))
            for d in range(len(pageList)):
                summary = pageList[d].summary
                fullPage =  pageList[d].content
                htmlDoc =  pageList[d].html()
                forPathUse = str(uuidMaker)
                uuidMaker += 1
                with open(uuidFile, 'a') as uuidMakerFile:
                    title =  pageList[d].title
                    if ('\r\n' in title):
                        title = title.replace('\r\n', '')
                    uuidMakerFile.write(title + '\n')
                    uuidMakerFile.close()
                ## image checkbox check
                if (self.picturesCheck):
                    try:
                        images =  pageList[d].images
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

                tempSummaryPath = summaryPath + '/' + forPathUse + '.txt'
                tempFullPagePath = fullPagePath + '/' + forPathUse + '.txt'
                tempHTMLPath = htmlPath + '/' + forPathUse + '.txt'
                with open(tempSummaryPath, 'w') as f:
                    f.write(ascii(summary))
                    f.close()
                with open(tempHTMLPath, 'w') as f:
                    f.write(ascii(htmlDoc))
                    f.close()
                with open(tempFullPagePath, 'w') as f:
                    f.write(ascii(fullPage))
                    f.close()
                self.saveProgress.emit((d+1,len(pageList),self.links[i]))
            self.progress.emit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = WikipediaLinkGetter()
    myApp.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Exited")


