# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 14:43:53 2022

@author: giyash
"""

def listdir_r(sftp, remotedir):
    
    from stat import S_ISDIR, S_ISREG
    from collections import deque

    dirs_to_explore = deque([remotedir])
    list_of_files = deque([])

    while len(dirs_to_explore) > 0:
        current_dir = dirs_to_explore.popleft()

        for entry in sftp.listdir_attr(current_dir):
            current_fileordir = current_dir + "/" + entry.filename

            if S_ISDIR(entry.st_mode):
                dirs_to_explore.append(current_fileordir)
            elif S_ISREG(entry.st_mode):
                list_of_files.append(current_fileordir)

    return list(list_of_files)

import os
import pysftp

sftp_url = "ftp.fraunhofer.de" # change this for a different ftp address
user = "testfeld01" # change username here
pswd = "s1fOEXaaeT1C8D" # change password here
# indicate no hostkeys to avoid the error related to ssh hostkeys or provide a ssh hostkey
cnopts = pysftp.CnOpts() 
cnopts.hostkeys = None # not recommended due to lack of secured connection

## connect to the sftp server
sftp =  pysftp.Connection(host=sftp_url,username=user, password=pswd,cnopts=cnopts)
print('Connection succesfully established')
remotedir = ""

lf = listdir_r(sftp,remotedir)