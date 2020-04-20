import platform 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import subprocess
import tkinter
import math
import os
import yaml


with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

optionConfig = cfg['options']

print(optionConfig['vlc_path'])


