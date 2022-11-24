# Script to run File Operations on any sensor and any folder
# What the script should be able to do:
    # - get all the files in a folder, subfolder, subsubfolder, etc.
    # - filter raw files (high frequency data files), average data files and status files
    # - find the gaps in files looking at file names using datetime construct
    # - find the size of files looking at plots
    # - find duplicates based on names
    # - find duplicates based on size
    # - remove duplicates from a folder
    # - get the latest file in the folder


#%% import modules
import pandas as pd
import os, sys, glob
workDir = os.path.dirname(sys.path[0])
sys.path.append(os.path.join(os.path.dirname(workDir), 'userModules'))

from FileOperations import FileOperations
import pythonAssist as pa
import subprocess
import zipfile
ZipFiles = True

# %% Set path
searchStr = '(\d{4}_\d{2}_\d{2}_\d{4})'
dateformat = '%Y_%m_%d_%H%M'

#%% Create a folder for a specific regexp with the same structure as source_dir
CopyFolder = True
if CopyFolder == True:
    import shutil as sh
    source_dir = r"z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\UpgradeData_corrected\server_mirror"
    target_dir = source_dir + "_renamed"
    regStr = '*.dat'
    # if ~os.path.exists(target_dir):
    #     os.mkdir(target_dir)
    fo = FileOperations(source_dir)
    prop = fo.FnGetFileSize(regStr)
    N, Ntotal = 0, len(prop.fullpaths) 
    for f in prop.fullpaths:
        fnew = f.replace('server_mirror', 'server_mirror_renamed')
        if os.path.exists(os.path.dirname(fnew)):
            sh.copy(f, fnew)
        else:
            os.mkdir(os.path.dirname(fnew))
            sh.copy(f, fnew)
        N += 1
        print('[{0}]: Copied file {1}/{2}'.format(pa.now(), N, Ntotal))

#%% Delete a files based on regexp
DeleteFiles = False
if DeleteFiles == True:
    source_dir = r"z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\metmastData"
    regStr = '*.7z'
    fo = FileOperations(source_dir)
    prop = fo.FnGetFileSize(regStr)
    N, Ntotal = 0, len(prop.fullpaths) 
    for f in prop.fullpaths:
        try:
            os.remove(f)
            N += 1
            print('[{0}]: Deleted file {1}/{2}'.format(pa.now(), N, Ntotal))
        except OSError as e:  ## if failed, report it back to the user ##
            print ("Error: %s - %s." % (e.filename, e.strerror))

    path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\zipped\Bowtie1Slow\2022"        
    fo = FileOperations(path)
    regStr = '*T*.zip'
    prop = fo.FnGetFileSize(regStr)
    files_less200b = prop[prop.sizes < 200]
    N, Ntotal = 0, len(files_less200b.fullpaths) 
    for f in files_less200b.fullpaths:
        try:
            os.remove(f)
            N += 1
            print('[{0}]: Deleted file {1}/{2}'.format(pa.now(), N, Ntotal))
        except OSError as e:  ## if failed, report it back to the user ##
            print ("Error: %s - %s." % (e.filename, e.strerror))

#%% get all the files with regStr in a folder
CompareFolders = True
if CompareFolders == True:
    regStr = '*.*'
    searchStr = '(_\d{4}_\d{2}_\d{2}_d{4})'
    dateformat = '_%Y_%m_%d_%H%M'
    path1 = r"z:\\Projekte\\109797-TestfeldBHV\\30_Technical_execution_Confidential\\TP3\\AP2_Aufbau_Infrastruktur\\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\UpgradeData\binary"
    fo1 = FileOperations(path1)
    prop1 = fo1.FnGetFileSize(regStr)
    prop1['DT'] = fo1.FnGetDateTime(prop1.filenames, searchStr, dateformat)

    regStr = '*.*'
    path2 = r"z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\sonicsData_old\binary"
    fo2 = FileOperations(path2)
    prop2 = fo2.FnGetFileSize(regStr)
    prop2['DT'] = fo2.FnGetDateTime(prop2.filenames, searchStr, dateformat)

    # very picky comparison tool
    # prop1.filenames.compare(prop2.filenames)

    # check if one array is a part of another, works well
    import matlab2py as m2p
    prop2['corr_filenames'] = [f[12:] for f in prop2.filenames]
    prop2['exists_in_path1'] = m2p.ismember(prop2.corr_filenames.values, prop1.filenames.values)
    # get a list of files not synced
    files_notsynced = prop2[prop2['exists_in_path1']==0]

    # get a list of files synced and other details, doesn't work always
    # files_synced, files_notsynced, sizes_synced, sizes_notsynced = fo1.FnCheckSynced(prop2.filenames, prop1.filenames, prop1.sizes)

    if CopyFiles == True:
        N, Ntotal = 0, len(files_notsynced.fullpaths) 
        for f in files_notsynced.fullpaths:
            fnew = os.path.join(path1, os.path.basename(f))
            if os.path.exists(os.path.dirname(fnew)):
                sh.copy(f, fnew)
            else:
                os.mkdir(os.path.dirname(fnew))
                sh.copy(f, fnew)
            N += 1
            print('[{0}]: Copied file {1}/{2}'.format(pa.now(), N, Ntotal))



#%% get all the files in a folder
path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Misc\20220406_BackupD_usb\Bremerhaven_data\highre2\zipped_c\Bremerhaven\2021-12-15T131032+00\2021-12-15T131032+00"
fo = FileOperations(path)
sensor = pa.struct()
sensor.files = fo.FnGetFiles()
print(sensor.files) # to get an idea of the contents




# %% get the size of files, filtered by extension or regexp
regStr = '*.dat'
sensor = fo.FnGetFileSize(regStr)
sensor['DT'] = fo.FnGetDateTime(sensor.filenames, searchStr, dateformat)
# sensor.sort_values(by='DT', inplace=True)
print(sensor.columns)
#%% zip files
if ZipFiles == True:
    src_path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Bowtie1\2022\03\16"
    fo = FileOperations(src_path)
    target_folder = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\highre2\2022-03-16T132556+00"
    regStr = '202*[!.(zip|7z|rar)]'  # add /**/ to prefix for including folders
    # regStr = "202*.dat"
    fo.FnFastZipFiles(extn='',outfmt='.zip', target_folder=target_folder, regStr=regStr)

#%%
regStr = '*.7z'
zips_path = r"z:\\Projekte\\109797-TestfeldBHV\\30_Technical_execution_Confidential\\TP3\\AP2_Aufbau_Infrastruktur\\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\sonicsData_old\binary"
fo = FileOperations(zips_path)
zips = fo.FnGetFileSize(regStr)
zips['DT'] = fo.FnGetDateTime(zips.filenames, searchStr, dateformat)
# zips.sort_values(by='DT', inplace=True)
print(zips.columns)

#%%
compression_ratio = [z/h for z,h in zip(zips.sizes, sensor.sizes)]

import plotly.graph_objects as go
fig= go.Figure()
f1 = go.Scattergl(x=sensor.DT, y = compression_ratio, mode='markers', name ='ratio')
fig.add_trace(f1)
fig.update_layout(
    autosize=False,
    width=800,
    height=800,
    xaxis = dict(title="datetime "),
    yaxis = dict(title = "size on drive [bytes]"),
    )
fig.show()


fig= go.Figure()
f1 = go.Scattergl(x=sensor.DT, y = sensor.sizes, mode='markers', name ='h5')
f2 = go.Scattergl(x=zips.DT, y = zips.sizes, mode='markers', name = "7z")
fig.add_trace(f1)
fig.add_trace(f2)
fig.update_layout(
    autosize=False,
    width=800,
    height=800,
    xaxis = dict(title="datetime "),
    yaxis = dict(title = "size on drive [bytes]"),
    )
fig.show()
#%% find gaps in files based on differencing
period = 'H'  
minor_gaps, major_gaps = fo.FnFindFileGaps(searchStr, sensor.filenames, dateformat, period)

#%% File and directory comparison
from filecmp import dircmp
def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s" % (name, dcmp.left,
              dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)

path1 = r"z:\\Projekte\\109797-TestfeldBHV\\30_Technical_execution_Confidential\\TP3\\AP2_Aufbau_Infrastruktur\\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\UpgradeData\ASCII"
path2 = r"z:\\Projekte\\109797-TestfeldBHV\\30_Technical_execution_Confidential\\TP3\\AP2_Aufbau_Infrastruktur\\Infrastruktur_Windmessung\02_Equipment\01_Messmast\Data\UpgradeData\ASCII_temp"
dcmp = dircmp(path1, path2)
print_diff_files(dcmp)

# Finding the files
#%% rename the files
fo.FnRenameFiles(regStr='*.dat', based_on='start')
#%% extract datetime from filenames
import numpy as np
total_time = pd.date_range(min(min(sensor.DT), min(zips.DT)), max(max(sensor.DT), max(zips.DT)), freq='D')
time = pd.DataFrame(index=total_time)

if np.array_equal(np.array(sensor.DT).sort(), np.array(zips.DT).sort()):
    meas = sensor.join(zips, rsuffix='_z').set_index('DT')
    df3 = time.join(meas)
# else:

import plotly.express as px
px.scatter(df3, x=df3.index, y = df3.DT_z)

    
    
    
    


#%% plot
import matplotlib.pyplot as plt
plt.plot(DT, sensor.sizes)
#%% plotly plot with sensor file sizes (visual check to see files with errors)
size_mb = [s/1e6 for s in sensor.sizes]
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=DT, y= size_mb, mode='markers'))
fig.show()
# %%
