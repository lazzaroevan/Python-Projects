import shutil
import requests
from mediawiki import MediaWiki
from mediawiki import DisambiguationError
import threading
import pickle
import os

#Run this file to gather all the data and save it onto your machine.
# Be cautious though, as there are about 95 gb worth of data gathered by this program
# most of it is images gathered by lines 76-82

wikipedia = MediaWiki()

def getListOfAnimals(title,path,delimiter):
    print('Getting backlinks.......')
    p = wikipedia.page(title)
    checkForReptile = p.backlinks
    print('Received backlinks.......')
    file = open(path,'w',encoding = 'utf8')
    for i in checkForReptile:
        file.write(i)
        file.write(delimiter)
    print('Done writing backlinks to file.......')
    file.close()

def importFile(path,delimiter):
    animalDatabase = []
    file = open(path, 'r',encoding = 'utf8')
    for i in file:
        animalDatabase = i.split(delimiter)
        print(len(animalDatabase))
    file.close()
    return animalDatabase

def preGetDataFunction():
    if (os.path.isdir(os.getcwd() + '\\Images')):
        walk = os.walk(os.getcwd() + '\\Images')
        for i in walk:
            for b in i[1]:
                path = i[0]+ '/' + b
                if(path != ''):
                    walk = os.walk(path)
                    for a in walk:
                        for x in a[2]:
                            os.remove(a[0]+'\\'+x)
                os.rmdir(path)
        os.rmdir(os.getcwd()+'\\Images')
    if (os.path.isdir(os.getcwd() + '\\Summaries')):
        walk = os.walk(os.getcwd() + '\\Summaries')
        for i in walk:
            path = i[0].join(i[2])
            if (path != ''):
                for a in i[2]:
                    os.remove(i[0]+'\\'+a)
        os.rmdir(os.getcwd()+'\\Summaries')
    os.mkdir(os.getcwd() + '\\Images')
    os.mkdir(os.getcwd() + '\\Summaries')

def getData(checkForReptile,breakout,threadIncrement,errors):
    currentSize = 0
    breakVariable = threadIncrement
    for i in checkForReptile[breakout:(breakout+threadIncrement)]:
        try:
            count = 0
            childPage = wikipedia.page(i)
            if(childPage != None):
                tempTitle = childPage.title
                if(os.path.isdir(os.getcwd()+'\\Images\\' + tempTitle)):
                    print('',sep='',end='')
                else:
                    os.mkdir(os.getcwd()+'\\Images\\' + tempTitle)
                file = open('Summaries\\'+ tempTitle,'w',encoding='utf8')
                file.write(childPage.summary)
                file.close()
                for i in childPage.images:
                    filename = i.split("/")[-1]
                    r = requests.get(i, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open(os.getcwd()+'\\Images\\' + tempTitle+ '/' + filename+str(count), 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                    count += 1
        except(DisambiguationError,OSError):
            errors[0] += 1
        if breakVariable == 0:
            break
        else:
            breakVariable -= 1
        currentSize += 1
        if(currentSize%100 == 0):
            print(currentSize,'/',threadIncrement,sep='',end='')
            print(' Errors:',errors[0])

if __name__ == '__main__':
    getListOfAnimals('Animals','animalDatabase.txt','#')
    animalDatabase = importFile('animalDatabase.txt','#')
    print('Loaded the animal database into ram.......')
    arrayOfThreads =[]
    animalDict = {}
    print('Preping work environment.......')
    preGetDataFunction()
    print('Establishing threads.......')
    threadIncrement = len(animalDatabase)//13
    errors = [0]
    for i in range(13):
        thread = threading.Thread(target=getData, args=(animalDatabase,i*threadIncrement,threadIncrement,errors))
        arrayOfThreads.append(thread)
        thread.start()
        print('Thread',i,'has started.......')
    print('All threads created.......')
    for i in arrayOfThreads:
        i.join()
    print('Threads complete.......')
    print('Enjoy!')