import platform 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import subprocess
import tkinter
import math
import os
import yaml


'''     
# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("streaming database").sheet1

everything = sheet.get_all_values()
#shows = []
#for i in range(100):
#    shows.append(i)

#for x in everything:
#    print(x)

testDict = {}

for x in everything:
    testDict[x[0]] = x[1:]

while(True):
    inp = input() 
    try:
        print(testDict[inp])
    except:
        print("Nothing found")

'''
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

optionConfig = cfg['options']

print(optionConfig['vlcPath'])


