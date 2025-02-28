# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:59:37 2022

@author: giyash
"""

# List the contents of a directory to get the filenames.
# Extract the date from the filenames (assuming a regular expression pattern match of \d{8} is good enough to extract the date).
# Sort or otherwise group the files by the extracted date.
# Iterate over those groups to do something.

import os, pathlib, itertools
import re
from collections import defaultdict
from datetime import datetime, tzinfo
import pandas as pd
import sys
sys.path.append(r'C:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\DataQualityControl\src')
sys.path.append(r'C:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\userModules')
from FileOperations import FileOperations
import shutil
from shutil import make_archive
import pythonAssist as pa


def FnLogging(log_file, src_folder, dest_folder):
    import logging
    
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info('Started')
    copy_files(src_folder, dest_folder)
    logging.info('Finished')    

def copy_files(src_folder, dest_folder):
    import logging
    import csv
    
    logging.info('Copying files')
    # load the File Operations class
    fo = FileOperations(src_folder)
    
    # get the files in the given path
    files = fo.FnGetFiles()
    
    # get the file sizes, paths and names
    regStr = '*T*.zip'
    sizes, paths, fullnames, names, ext = fo.FnGetFileSize(regStr)
    
    # get the dates of the files in datetime format
    dates = pd.to_datetime(names)
    
    # change to the directory where folders need to be created
    os.chdir(dest_folder)
    
    # copy zip files from source folder to destination folder, if the file not exists
    N_empty, N_exists = 0, 0
    files_copied, files_notcopied = [], []
    for i in range(len(fullnames)):
        d = pd.to_datetime(names[i])
        tempPath = os.path.join(dest_folder, str(d.year), str(d.month).zfill(2), str(d.day).zfill(2))
        os.makedirs(tempPath, exist_ok= True)
        try:
            dest_file = os.path.join(tempPath, fullnames[i])
            if not os.path.isfile(dest_file):
                shutil.copy2(paths[i], tempPath)
                print("[{0}]: Completed {3}/{4} -- File {1} copied to {2}".format(pa.now(), fullnames[i], tempPath[-18:], i, len(fullnames)))
                N_empty += 1
                files_copied.append(paths[i])
                with open('CopiedFiles.txt', 'a') as file:
                    w = csv.writer(file)
                    w.writerow(paths[i])

        except OSError:
            print("[{0}]: File {1} exists or has some error".format(pa.now(), fullnames[i]))
            console=logging.StreamHandler()
            console.setLevel(logging.ERROR)
            logger = logging.getLogger('CopyFiles.log').addHandler(console)
            # logger.debug("[{0}]: File {1} exists or has some error {2}".format(pa.now(), fullnames[i], shutil.Error))
            logger.info('info message')
            logger.warn('warn message')
            logger.error('error message')
            logger.critical('critical message')

            N_exists += 1
            files_notcopied.append(paths[i])
            with open('NotCopiedFiles.txt', 'a') as file:
                w = csv.writer(file)
                w.writerow(str(paths[i])+'\n')

if __name__ == '__main__':
    src_folder = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Lissajous"
    dest_folder = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Lissajous"
    log_file = "CopyFiles.log"

    FnLogging(log_file, src_folder, dest_folder)
    
    
        
