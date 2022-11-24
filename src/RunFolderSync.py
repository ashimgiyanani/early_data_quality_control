# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 16:06:07 2022

@author: giyash
"""

import os
import numpy as np
from fnmatch import fnmatch

pattern = "*average*.csv"
path_Z = r"z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\04_Nacelle-Lidars-Inflow_CONFIDENTIAL\30_Data\BlackTC"
files_Z = []
folders= []
for path, subdirs, files in os.walk(path_Z):
    folders.append(subdirs)
    for name in files:
        if fnmatch(name, pattern):
            files_Z.append(name)
            # print(os.path.join(path, name))
folders = [x for x in folders if x]
            
pattern = "*average*.csv"
path_ftp = r"z:\Projekte\109797-TestfeldBHV\ALT\HourlyData\BlackTC\WITC0100012-(wi2005b00085)_average_data"
files_ftp = []
for path, subdirs, files in os.walk(path_ftp):
    for name in files:
        if fnmatch(name, pattern):
            files_ftp.append(name)
            print(os.path.join(path, name))
            
files_synced, files_notsynced = [],[]           
for filename in file_ftp:
    if filename in files_Z:
        files_synced.append(filename)
    else:
        files_notsynced.append(filename)

patterns = ['pattern1', 'pattern2', ...]
# folders = [os.path.join(main_directory, pattern) for pattern in patterns]

# build folders
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# move files in corresponding folders
for file in files_notsynced:  # files is the list of all yoru file paths
    for pattern, folder in zip(patterns, folders):
    file_name = os.path.basename(file)
    if pattern in file_name:
        os.rename(file, os.path.join(folder, filename))        


