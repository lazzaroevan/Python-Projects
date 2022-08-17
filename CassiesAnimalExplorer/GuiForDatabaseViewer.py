import os
import tkinter as tk
from PIL import ImageTk, Image,UnidentifiedImageError
import tkinter.font as font
import random

#needs to be here
window = tk.Tk()

#class
class VerticalScrolledFrame(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL,width = 50)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,yscrollcommand=vscrollbar.set,height = (window.winfo_screenheight()-50))
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        # This is what enables scrolling with the mouse:
def importAnimalNames(filepath):
    files = os.walk(filepath)
    animalNames = []
    for i in files:
        animalNames.append(i[2])
    return animalNames[0]
def letterLookup(letter,animalNames,frame,bottomBar,endSearch = 0):
    print(letter)
    startIndex = None
    endIndex = None
    for i in range(len(animalNames)):
        word = str.upper(animalNames[i][0:endSearch])
        if(word==letter):
            startIndex = i
        if(startIndex != None):
            restart(frame,bottomBar,startIndex)
def upOrDownPressedFunc(int,upOrDownPressed,animalButtons,animalNames,increment):
    if((int == -1) and upOrDownPressed[0]>0):
        if(upOrDownPressed[0]-increment>0):
            upOrDownPressed[0] += -increment
        else:
            upOrDownPressed[0]= 0
        print(upOrDownPressed[0])
    elif(int == 1 and (upOrDownPressed[0] < (len(animalNames)-len(animalButtons)))):
        if (upOrDownPressed[0] + increment < (len(animalNames)-len(animalButtons))):
            upOrDownPressed[0] += increment
            print(upOrDownPressed[0])
        else:
            upOrDownPressed[0]= (len(animalNames)-len(animalButtons))
    for i in range(len(animalButtons)):
        animalButtons[i]['text'] = animalNames[i+upOrDownPressed[0]]
def randomAnimal(frame,animalsList,bottomBar,font):
    randomAnimal = random.randint(0,len(animalsList))
    animalName = animalsList[randomAnimal]
    infoShower(frame,animalName,bottomBar,window,font)
def jumpToLetter(animalButtons,animalNames,frame,bottomBar,increment):
    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    fontToUse = font.Font(family='Times New Roman', size=16, weight='bold')
    bottomBar.destroy()
    bottomBar = tk.Frame()
    upOrDownPressedLetters = [0]
    for i in range(len(animalButtons)):
        animalButtons[i]['text'] = letters[i+upOrDownPressedLetters[0]]
        animalButtons[i]['command'] = lambda c=i: letterLookup(animalButtons[c].cget("text"),animalNames,frame,bottomBar)
    downButton = tk.Button(bottomBar, text='DOWN', height=1, border=10, font=fontToUse,
                           command=lambda: upOrDownPressedFunc(1, upOrDownPressedLetters, animalButtons, letters,increment))
    upButton = tk.Button(bottomBar, text='UP', height=1, border=10, font=fontToUse,
                         command=lambda: upOrDownPressedFunc(-1, upOrDownPressedLetters, animalButtons, letters,increment))
    backButton = tk.Button(bottomBar, font=fontToUse, text='BACK', height=1, border=10,
                       command=lambda: restart(frame, bottomBar))
    upButton.pack(side=tk.LEFT)
    backButton.pack(side = tk.LEFT)
    downButton.pack(side=tk.LEFT)
    bottomBar.pack()
def infoShower(frame,title,frameToDestroy,window,font):
    print(title)
    file = open('Summaries/'+title,'r',encoding='utf8')
    string = title + '\n'
    for i in file:
        string += i
    fontToUse = font
    frame.destroy()
    frameToDestroy.destroy()
    newFrame = VerticalScrolledFrame(window)
    newFrame.pack()
    label = tk.Label(newFrame.interior, text=string,font=fontToUse, wraplength=(window.winfo_screenwidth() - 50))
    label.pack(side='top', fill='both', expand='yes')
    bottomBar = tk.Frame(window)
    button = tk.Button(bottomBar, font=fontToUse, text='BACK', height=30, border=10,
                       command=lambda: restart(newFrame, bottomBar))
    button.pack(side='bottom')
    for i in os.walk("Images/"+title):
        for a in i[2]:
            try:
                if('Red_Pencil_Icon.png' not in a):
                    #note, resizing the images takes up alot of time and memory, causes long load times
                    imageToResize = Image.open('Images/'+title+'/'+a)
                    while (imageToResize.size[0] < (window.winfo_screenwidth()/2)-10):
                        imageToResize = imageToResize.resize(
                            (round(imageToResize.size[0] * (1.5)), (round(imageToResize.size[1] * (1.5)))))
                    while(imageToResize.size[0]>(window.winfo_screenwidth()/2)):
                        imageToResize = imageToResize.resize((round(imageToResize.size[0]*(.5)),(round(imageToResize.size[1]*(.5)))))
                    img = ImageTk.PhotoImage(imageToResize)
                    imageLabel = tk.Label(master = newFrame.interior, image=img)
                    imageLabel.img = img
                    imageLabel.pack(side='bottom', fill='both', expand='yes')
            except(UnidentifiedImageError):
                print('imageError')
    bottomBar.pack()
def restart(frame,bottombar,start = 0):
    _list = window.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    window.wm_frame()
    for i in _list:
        i.destroy()
    main(animalNames,start)
def setTextBox(letter,textBox):
    text = textBox['text']
    if(letter == 'BACKSPACE'):
        textBox['text'] = text[0:-1]
    elif(text == ''):
        textBox['text']=letter
    elif(letter != 'BACKSPACE'):
        textBox['text']=text+letter
def keywordSearch(frame,frameToDestroy,window,fontToUse,pixelVirtual):
    frame.destroy()
    frameToDestroy.destroy()
    entryFrame = tk.Frame()
    displayFont = font.Font(family='Times New Roman', size=30, weight='bold')
    entry = tk.Label(entryFrame,font = displayFont,width = window.winfo_screenwidth())
    qList = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P']
    aList = ['A','S','D','F','G','H','J','K','L']
    zList = ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    buttonSize = ((window.winfo_screenwidth()//len(qList)-20),window.winfo_screenheight()//4)
    qLetters = []
    aLetters = []
    zLetters = []
    bottomBar = tk.Frame()
    qFrame = tk.Frame()
    aFrame = tk.Frame()
    zFrame = tk.Frame()
    for i in range(len(qList)):
        newButton = (tk.Button(master=qFrame,font=fontToUse,width = buttonSize[0],height = buttonSize[1],text=qList[i],image=pixelVirtual,compound = tk.CENTER, border=5,
                               bg='lightblue', fg='black',
                               command=lambda c=i: setTextBox(qLetters[c].cget("text"),entry)))
        qLetters.append(newButton)
        qLetters[i].pack(side = tk.LEFT)
    for i in range(len(aList)):
        newButton = (
            tk.Button(master=aFrame, font=fontToUse, border=5, text=aList[i],width = buttonSize[0],height = buttonSize[1],image=pixelVirtual,compound = 'c',
                      bg='lightblue', fg='black',
                      command=lambda c=i: setTextBox(aLetters[c].cget("text"),entry)))
        aLetters.append(newButton)
        aLetters[i].pack(side = tk.LEFT)
    for i in range(len(zList)):
        newButton = (tk.Button(master = zFrame,font=fontToUse, border=5, text=zList[i],width = buttonSize[0],height = buttonSize[1],image=pixelVirtual,compound = 'c',
                               bg='lightblue', fg='black',
                               command=lambda c=i: setTextBox(zLetters[c].cget("text"),entry)))
        zLetters.append(newButton)
        zLetters[i].pack(side = tk.LEFT)
    backSpace = (tk.Button(master=entryFrame, font=fontToUse, border=5, text='BACKSPACE',width = buttonSize[0],height = buttonSize[1],image=pixelVirtual,compound = 'c',
                           bg='lightblue', fg='black',
                           command=lambda c=i: setTextBox('BACKSPACE', entry)))
    enterButton = (tk.Button(master=entryFrame, font=fontToUse, border=5, text='ENTER', width=buttonSize[0],
                           height=buttonSize[1], image=pixelVirtual, compound='c',
                           bg='lightblue', fg='black',
                           command=lambda c=i:letterLookup(entry['text'],animalNames,frame,bottomBar,len(entry['text'])) ))
    backSpace.pack(side = tk.RIGHT)
    enterButton.pack(side = tk.RIGHT)
    entry.pack()
    entryFrame.pack()
    qFrame.pack()
    aFrame.pack()
    zFrame.pack()
def main(animalNames,startingInt = 0):
    animalNames = importAnimalNames('Summaries')
    fontToUse = font.Font(family='Times New Roman', size=16, weight='bold')
    upOrDownPressed = [startingInt]
    animalButtons = []
    frame = tk.Frame()
    pixelVirtual = tk.PhotoImage(width=0, height=0)
    increment = 20 #number of boxes pressing up or down will move
    bottomBar = tk.Frame()
    randomButton = tk.Button(bottomBar, text='RANDOM', border=5, font=fontToUse,height = window.winfo_screenheight()//21,image=pixelVirtual,compound = 'c',
                             command=lambda: randomAnimal(frame, animalNames, bottomBar,fontToUse))
    downButton = tk.Button(bottomBar, text='DOWN', border=5, font=fontToUse,height = window.winfo_screenheight()//21,image=pixelVirtual,compound = 'c',
                           command=lambda: upOrDownPressedFunc(1, upOrDownPressed, animalButtons,animalNames,increment))
    upButton = tk.Button(bottomBar, text='UP', border=5, font=fontToUse,height = window.winfo_screenheight()//21,image=pixelVirtual,compound = 'c',
                         command=lambda: upOrDownPressedFunc(-1, upOrDownPressed, animalButtons,animalNames,increment))
    '''searchByLetter = tk.Button(bottomBar, font=fontToUse, text='LETTER SEARCH', height=1, border=10,
                               command=lambda: jumpToLetter(animalButtons,animalNames, frame,bottomBar,increment))'''
    searchByKeyword = tk.Button(bottomBar, font=fontToUse, text='KEYWORD SEARCH', border=5,height = window.winfo_screenheight()//21,image=pixelVirtual,compound = 'c',
                               command=lambda: keywordSearch(frame,bottomBar,window,fontToUse,pixelVirtual))
    for i in range(increment):
        newButton = (tk.Button(master = frame,font=fontToUse, border='5', text=animalNames[i+startingInt],image=pixelVirtual,height = (window.winfo_screenheight()//30 ) , width=(window.winfo_screenwidth()),compound = 'c',
                               bg='lightblue', fg='black',
                               command=lambda c=i: infoShower(frame, animalButtons[c].cget("text"), bottomBar,window,fontToUse)))
        animalButtons.append(newButton)
        animalButtons[i].pack()
    upButton.pack(side=tk.LEFT)
    randomButton.pack(side=tk.LEFT)
    #searchByLetter.pack(side= tk.LEFT)
    searchByKeyword.pack(side=tk.LEFT)
    downButton.pack(side=tk.RIGHT)
    frame.pack()
    bottomBar.pack()
    window.mainloop()
if __name__ == '__main__':
    # stuff i dont want done every time main loop is run
    window.minsize(window.winfo_screenwidth(), window.winfo_screenheight())
    window.maxsize(window.winfo_screenwidth(), window.winfo_screenheight())
    window.overrideredirect(1)
    window.resizable(0, 0)
    window.title("Animal Encyclopedia")
    animalNames = importAnimalNames('Summaries')
    main(animalNames = animalNames)