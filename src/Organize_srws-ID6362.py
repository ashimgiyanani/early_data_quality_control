#%% Script to organize the SRWS files
import pandas as pd
sys.path.append(r"../../userModules")
from FileOperations import FileOperations
import os, sys, glob
import pythonAssist as pa
sys.path.append(r"../fun")
import subprocess
import zipfile


#%% Set path
inp = pa.struct()
srws = pa.struct()
# path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\highre2\zipped_c\Bremerhaven\Bowtie1Fast"
# fo = FileOperations(path)

# get a list of files in path
# srws.files = fo.FnGetFiles()

# get file sizes
# srws = fo.FnGetFileSize('*.*')
# srws_zips = fo.FnGetFileSize('*.zip')

#%% arrange the files in a different folder
# src_folder = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\highre2\zipped_c\Bremerhaven\Bowtie1Fast"
# dest_folder = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\zipped\Bowtie1Fast"
# log_file = "CopyFiles.log"
# fo.FnLogging(log_file, src_folder, dest_folder)

# unzip files from dest_folder to unzip folder
# get all the files in unzip folder
uz_path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Rosette"
unzipped_files = glob.glob(''.join([uz_path,'/**/*T*[!.zip]']),recursive=True)

# get all the zip files in the BowTie folder
z_path = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data_zipped\Rosette"
zipped_files = glob.glob(''.join([z_path,'/**/*T*.zip']),recursive=True)


def FnUnzipFiles(fnew_path, zipped_files, path_division):
    path_7zip = r"C:\Program Files\7-Zip\7z.exe"
    for f in sorted(zipped_files):
        if path_division== True:
            d = pd.to_datetime(os.path.splitext(os.path.basename(f))[0])
            tempPath = os.path.join(path2, str(d.year), str(d.month).zfill(2), str(d.day).zfill(2))
            os.makedirs(tempPath, exist_ok= True)
            fnew = os.path.join(tempPath, os.path.basename(f))
        else:
            fnew = os.path.join(fnew_path, os.path.basename(f))

        try:
            if not os.path.exists(os.path.join(fnew, os.path.splitext(os.path.basename(f))[0])):
                subprocess.check_output([path_7zip, "e", f, "-y"])
                print('[{0}]: Extracted {1}'.format(pa.now(), os.path.basename(f)))
            else:
                print('[{0}]: Skipped {1}'.format(pa.now(), os.path.basename(f)))
        except subprocess.CalledProcessError:
            print('[{0}]:  Error based Skipped {1}'.format(pa.now(), os.path.basename(f)))
            continue

#%% Compare two SRWS folders using regex(re.search) and datetime string in the name
inp.compareFolders = True
inp.copyFiles = False
inp.unzipFiles = True
path_7zip = r"C:\Program Files\7-Zip\7z.exe"

if inp.compareFolders == True:
    regStr = '*T*[.(zip|7z)]'
    # regStr = '*'
    searchStr = '(\d{4}-\d{2}-\d{2}T\d{6}+\d{2})'
    dateformat = '%Y-%m-%dT%H%M%S%z'
    path1 = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data_zipped\Bowtie1"
    fo1 = FileOperations(path1)
    prop1 = fo1.FnGetFileSize(regStr)
    deleted_files1 = fo1.delete_files_below_threshold(prop1, threshold=174)
#    prop1['DT'] = fo1.FnGetDateTime(prop1.filenames, searchStr, dateformat)

    regStr = '*T*[!.(zip|7z|txt)]'
    # regStr = '*'
    searchStr = '(\d{4}-\d{2}-\d{2}T\d{6}+\d{2})'
    dateformat = '%Y-%m-%dT%H%M%S%z'
    path2 = r"z:\Projekte\112933-HighRe\20_Durchfuehrung\OE410\SRWS\Data\Bowtie1"
    fo2 = FileOperations(path2)
    prop2 = fo2.FnGetFileSize(regStr)
    deleted_files2 = fo2.delete_files_below_threshold(prop2, threshold=174)
#    prop2['DT'] = fo1.FnGetDateTime(prop2.filenames, searchStr, dateformat)

    import matlab2py as m2p
    prop2['exists_in_path1'] = m2p.ismember(prop2.filenames.values, prop1.filenames.values)
    prop1['exists_in_path2'] = m2p.ismember(prop1.filenames.values, prop2.filenames.values)

    # files not synced between the folders
    files1_not_synced = prop1[prop1['exists_in_path2']==0]
    files2_not_synced = prop2[prop2['exists_in_path1']==0]

    # dropping empty files
    files1_copyto2 = files1_not_synced.drop(files1_not_synced[files1_not_synced.sizes<=174].index)
    files2_copyto1 = files2_not_synced.drop(files2_not_synced[files2_not_synced.sizes<=174].index)

    if inp.copyFiles == True:
        import shutil as sh
        N, Ntotal = 0, len(files2_copyto1.fullpaths) 
        for f in files2_copyto1.fullpaths:
            d = pd.to_datetime(os.path.splitext(os.path.basename(f))[0])
            tempPath = os.path.join(path1, str(d.year), str(d.month).zfill(2), str(d.day).zfill(2))
            os.makedirs(tempPath, exist_ok= True)
            fnew = os.path.join(tempPath, os.path.basename(f))
            # copy files to respective folders
            if os.path.exists(os.path.dirname(fnew)):
                sh.copy(f, fnew)
            else:
                os.mkdir(os.path.dirname(fnew))
                sh.copy(f, fnew)

            if inp.unzipFiles == True:
                # 7zip.exe extract<e> <archive name>
                outfile_name = fnew + '.zip'
                try:
                    # if not os.path.exists(os.path.splitext(fnew)[0]):
                    if not os.path.exists(fnew + '.zip'):
                        os.chdir(os.path.dirname(fnew))
                        # subprocess.check_output([path_7zip, "e", fnew, "-y"])
                        subprocess.check_output([path_7zip, "a", "-tzip", "-m5=lzma", outfile_name, fnew])
                        print('[{0}]: Extracted {1}'.format(pa.now(), os.path.basename(fnew)))
                        os.remove(fnew)
                    else:
                        print('[{0}]: Skipped {1}'.format(pa.now(), os.path.basename(fnew)))
                        os.remove(fnew)
                except subprocess.CalledProcessError:
                    print('[{0}]:  Error based Skipped {1}'.format(pa.now(), os.path.basename(fnew)))
    
            N += 1
            print('[{0}]: Copied file {1}/{2}'.format(pa.now(), N, Ntotal))