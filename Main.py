import tkinter 
import os.path
import platform 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import subprocess
import math
import yaml
from tkinter import filedialog

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
dataSheet = client.open("streaming database").sheet1

operatingSystem = platform.system() #Darwin or Windows 

allData = dataSheet.get_all_values()
showDict = {}

for x in allData:
    showDict[x[0]] = x[1:]


#load config
with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

serverConfig = cfg['server']
optionsConfig = cfg['options']

serverPass = serverConfig['password']
serverUser = serverConfig['user']
localIP = serverConfig['local_address']
externalIP = serverConfig['external_address']

def main():

    initWindow() #should probably be last?

def test() :
    print('hello')


 
def initWindow():
    
    window = tkinter.Tk()
    window.title("Test")
    window.geometry("500x300+300+300")
    window.configure(background='gray')

    WINDOW_HEIGHT = 300
    WINDOW_WIDTH = 500

    #label = tkinter.Label(window, text = "reference label", background='gray').place(x=50,y=0)

    def callStream1():
        stream(showIn.get(),episodeIn.get(),True)
    def callStream2():
        stream(showIn.get(),episodeIn.get(),False)
    def callDownload():
        download(showIn.get(),episodeIn.get())

    showIn = tkinter.Entry(window,width=20,font=("Calibri 20"))
    showIn.place(x=115,y=80)
    sLabel = tkinter.Label(window, text = "Show name:", background='gray',font=("Calibri 14")).place(x=115,y=50)

    episodeIn = tkinter.Entry(window,width=3,font=("Calibri 20"))
    episodeIn.place(x=115,y=150)
    eLabel = tkinter.Label(window, text = "Episode:", background='gray',font=("Calibri 14")).place(x=115,y=120)
    
    sB = tkinter.Button(window,text="Stream\nLocal",command=callStream1,background='lightgray',
    height=2,width=10).place(x=(WINDOW_WIDTH/4) + 87,y=235)

    dB = tkinter.Button(window,text="Download",command=callDownload,background='lightgray',
    height=2,width=10).place(x=(WINDOW_WIDTH/4)+220,y=235)

    sEB = tkinter.Button(window,text="Stream\nExternal",command=callStream2,background='lightgray',
    height=2,width=10).place(x=(WINDOW_WIDTH/4) - 50,y=235)

    lastWatched = tkinter.Label(window, text = "\nLast watched: " + showDict['1'][0], background='gray').place(x=(WINDOW_WIDTH/4)-10,y=0)

    def callShowList():
        openShowList(window)

    menubar = tkinter.Menu(window)
    menubar.add_command(label="ShowList", command=callShowList)
    # http://effbot.org/tkinterbook/menu.htm
    
    def callVLCPath():
        VLCPath(window)

    menubar.add_command(label="Options", command=test)

    optionsmenu = tkinter.Menu(menubar, tearoff=0)
    optionsmenu.add_command(label="Set VLC path", command=callVLCPath)
    optionsmenu.add_command(label="placeholder", command=test)
    optionsmenu.add_separator()
    optionsmenu.add_command(label="Exit", command=window.quit)
    menubar.add_cascade(label="Options", menu=optionsmenu)
    

    window.config(menu=menubar)

    if not checkVLC() :
        noVLC = tkinter.Label(window, text = "No VLC found!", background='gray', fg='red').place(x=WINDOW_WIDTH/4 + 95,y=200)

    window.mainloop()


def checkVLC():

    if operatingSystem == "Darwin":
        if os.path.exists(r"/Applications/VLC.app"):
            return True

    if operatingSystem == "Windows":
        if os.path.exists(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
            return True

    return False

#shows need to be concatenated, movies contain everything needed in path
def stream(media, episode, local):
    if local:
        linkBeginning = "sftp://"+ serverUser +":"+ serverPass + "@" + localIP
    else:
        linkBeginning = "sftp://" + serverUser + ":"+ serverPass +"@" + externalIP

    media = sanitizeStr(media)

    showData = getShowInfo(media)
    if showData == -1:
        print("not found")
    else:
        path = showData[0]
        videoType = showData[1]
        extention = showData[2]
        episodeCount = showData[3]
 
        if videoType == "s":
            if int(episode) > int(episodeCount): #seperate so it doesnt do this if its not an 's'
                print("error")
                return

        if checkVLC == False:
            print("error")
            return
        
        if videoType == "m":
            link = linkBeginning + path
            if operatingSystem == "Windows":
                subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",link])
            if operatingSystem == "Darwin":
                subprocess.call(["/usr/bin/open", "-W", "-n", "-a", "/Applications/VLC.app",link])

            dataSheet.update_cell(1,2,media)
            return

        if videoType == "s":
            if int(episode) < 10 and episode[0] != '0':
                episode = "0" + episode
            link = linkBeginning + path + episode + extention
            if operatingSystem == "Windows":
                subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe",link])
            if operatingSystem == "Darwin":
                subprocess.call(["/usr/bin/open", "-W", "-n", "-a", "/Applications/VLC.app",link])
                #subprocess.Popen(["/Applications/VLC.app",link])

            dataSheet.update_cell(1,2,media + " - " + episode)
            return

def sanitizeStr(string):
    #remove extra whitespace
    while string[-1] == ' ':
        string = string[:-1]

    string = string.lower()

    return string


# onvalue="sftp://stream@50.71.198.164" offvalue="sftp://stream@192.168.0.41"

def download(media, episode):
    
    showData = getShowInfo(media)
    if showData == -1:
        print("not found")
    else:
        print(showData[0])

# path, type, extention, episode
def getShowInfo(searchTerm):
    try:
        return showDict[searchTerm]
    except:
        return -1

def openShowList(window):
    class Popup:
        def __init__(self, root, label):
            self.root = root
            self.label = label 
        
        def create(self,c,r):
            tkinter.Button(self.root,text=self.label,font=("Calibri 12"),command=lambda : onClick(self.label),background='lightgray').grid(row=r,column=c)

    showListSorted = []
    #copy the showList
    count = 0
    for i in showList:
        if i != '1' and i != 'search term': #skip the first two
            showListSorted.append(i)
        count += 1
    
    showListSorted = sorted(showListSorted)

    colNum = math.floor(len(showListSorted) / 4)

    def onClick(show):
        showWin = tkinter.Toplevel(window)

        tkinter.Label(showWin,text=show).pack()

        showWin.geometry("200x100+500+300")
        
    newwin = tkinter.Toplevel(window)
    newwin.geometry("+300+300")
    newwin.configure(background='gray')
    count = 0
    c = 0
    for x in showListSorted:
        l = Popup(newwin,x)
        if count > colNum:
            c += 1
            count = 0
        l.create(c,count)
        count += 1
        
def VLCPath(window):
    newWin = tkinter.Toplevel(window)
    newWin.geometry("400x150+500+500")
    newWin.configure(background='gray')
    
    def clickBrowse():
        givenPath = filedialog.askopenfilename(initialdir = "/",title = "Select VLC",filetypes=[("Application", "*.app *.exe")])
        optionsConfig["vlc_path"] = givenPath
        cfg['options'] = optionsConfig
        with open("config.yml", "w") as ymlfile:
            yaml.dump(cfg, ymlfile)


    clickBrowse()

main()