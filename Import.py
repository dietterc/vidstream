import gspread
from oauth2client.service_account import ServiceAccountCredentials
import paramiko
from scp import SCPClient
import os
import sys
import yaml

import re #for the fancy sort

#load config
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

serverConfig = cfg['server']

serverPass = serverConfig['password']

#get user input
inp = input("Ready: (type directory searchterm(spaces as dashes) external/internal)\n")
 
#INPUT FORMAT: type directory searchterm(spaces as dashes) external/internal
#example: s show star-wars i

#if type is m, directory is just the file to be added

# type a for add

while inp[-1] == ' ':
    inp = inp[:-1]

params = inp.split(" ")

if len(params) != 4:
    sys.exit("ERROR: Expected 4 parameters, recieved " + str(len(params)))

videoType = params[0]

if videoType != "s" and videoType != 'm' and videoType != 'a':
    sys.exit("ERROR: " + params[0] + " is not a valid type")

if params[3] != "i" and videoType != 'e':
    sys.exit("ERROR: " + params[3] + " is not a valid param")

localDir = params[1] + '/'
searchTerm = params[2].replace("-"," ")


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

if params[3] == 'i':
    ssh = createSSHClient("192.168.0.41", "22", "stream", serverPass)
if params[3] == 'e':
    ssh = createSSHClient("50.71.198.164", "22", "stream", serverPass)

scp = SCPClient(ssh.get_transport())

if videoType == 'm':
    print("Starting " + localDir)
    scp.put(localDir, "streaming/movies/")
    print("..done")
    filePath = str(ssh.exec_command(r"readlink -f streaming/movies/" + localDir)[1].read()).replace("b","").replace("'","").replace(r"\n", "")
    #print(filePath)

if videoType == 's':
    try:
        ssh.exec_command(r"mkdir streaming/shows/" + params[2])
    except:
        ssh.exec_command(r"mkdir streaming/shows/" + params[2])
    
    newEpisodes = []
    for x in os.listdir(localDir):
        newEpisodes.append(x)

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [ atoi(c) for c in re.split(r'(\d+)', text) ]

    newEpisodes.sort(key=natural_keys)

    for x in newEpisodes:
        print("Starting " + x)
        scp.put(localDir + x, "streaming/shows/" + params[2])
        print("..done")
        extension = "." + x.split(".")[-1]

    output = str(ssh.exec_command(r"ls streaming/shows/" + params[2])[1].read()).replace("'","")
    outList = output.split(r"\n")
    outList = outList[:-1]
    outList[0] = outList[0][1:]

    outListSorted = []
    for x in outList:
        outListSorted.append(x)

    outListSorted.sort(key=natural_keys)

    index = 1
    for x in outListSorted:
        zero = ""
        if index < 10:
            zero = "0" 
        fixedX = x.replace("[","\[").replace(" ","\ ").replace("]","\]")
        ssh.exec_command(r"mv streaming/shows/" + params[2] + "/" + fixedX + r" streaming/shows/" + params[2] + "/" + zero + str(index) + extension)
        index += 1
    filePath = "/home/stream/streaming/shows/" + params[2]

ssh.close()

print("Adding to spreadsheet...")

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("streaming database").sheet1

showList = sheet.col_values(1)
freeRow = len(showList) + 1

sheet.update_cell(freeRow, 1, searchTerm)
sheet.update_cell(freeRow, 2, filePath)

if videoType == 'm':
    sheet.update_cell(freeRow, 3, 'm')
    sheet.update_cell(freeRow, 2, filePath)

if videoType == 's':
    sheet.update_cell(freeRow, 2, filePath + '/')
    sheet.update_cell(freeRow, 3, 's')
    sheet.update_cell(freeRow, 4, extension)
    sheet.update_cell(freeRow, 5, len(outList))

print("Done!")