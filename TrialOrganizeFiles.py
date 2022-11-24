# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 23:44:24 2022

@author: giyash
"""

# def FnOrganizeFiles(path, Str, period):
from datetime import datetime
from pathlib import Path
import os

def FnGetFiles(path):
    # path = r"Z:\Projekte\109797-TestfeldBHV\Data"

    import os
    import itertools

    files = []
    for root, subdirs, f in os.walk(path):
        files.append(f)
    files = list(itertools.chain(*files))
    return files

filepath = Path(r"z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\04_Nacelle-Lidars-Inflow_CONFIDENTIAL\30_Data\Backup_2021\DailyData_GreenPO\WIPO0100301-(wi020100301)_average_data")
#  https://automatetheboringstuff.com/chapter9/
files = FnGetFiles(filepath)

# Is the path a file?
print(filepath.is_file())                  # Returns false

# Is the path a directory?
print(filepath.is_dir())                   # Returns true

# What is the parent of the file?
print(filepath.parent)                     # Returns /Users/nikpi/Desktop

# What is the base of the filename?
print(filepath.stem)                       # Returns Files

# What are the extensions of the file?
print(filepath.suffix)                     # Returns "" (since it's not a file)

for files in filepath.iterdir():
    if file.is_file() and file.suffix != "*.csv"
for folder in our_files.iterdir():
    directory = folder.parent
    folder_name = file.stem
    # Convert date to datetime and convert to string of desired format
    folder_date = datetime.strptime(old_name, "%Y-%m-%d")
    
    for file in folder.iterdir():
        # Set up key variables for the parent path and the file extensions
        extension = file.suffix
        year, month, day = old_name.split('-')

    
