
#%% ToDos for the monthly report

#%% user modules
import pandas as pd
import glob
import os
import numpy as np
import sys
import pickle
from pathlib import Path
from calendar import monthrange

sys.path.append(r"../../userModules")
# sys.path.append(r"../fun") # change to this when sharing the data
sys.path.append(r"../../OneDasExplorer/Python Connector")

import runpy as rp
import matplotlib.pyplot as plt

from csv import writer
import matlab2py as m2p
from pythonAssist import *
from datetime import datetime, timezone, timedelta

from odc_exportData import odc_exportData
from FnImportOneDas import FnImportOneDas
from FnDataAvailability import FnDataAvailability

#%% user definitions
input = struct()
input.tiny = 12
input.Small = 14
input.Medium = 16
input.Large = 18
input.Huge = 22
plt.rc('font', size=input.Small)          # controls default text sizes
plt.rc('axes', titlesize=input.Small)     # fontsize of the axes title
plt.rc('axes', labelsize=input.Medium)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=input.Small)    # fontsize of the tick labels
plt.rc('ytick', labelsize=input.Small)    # fontsize of the tick labels
plt.rc('legend', fontsize=input.Medium)    # legend fontsize
plt.rc('figure', titlesize=input.Huge)  # fontsize of the figure title

#%% import data from OneDAS
# begin = datetime(2021, 9, 6, 0, 0, tzinfo=timezone.utc)
# end   = datetime(2021, 9, 13, 0, 0, tzinfo=timezone.utc)
data = struct()
data.sampleRate = 1/600
input.AppendLog = 0

# must all be of the same sample rate
data.paths = [
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0000_V1/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/P0420_RotorSpdRaw/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/P1000_TotalPwMeas/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0010_V2/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0020_V3/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0030_V4/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0040_V5/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0050_V6/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0060_Precipitation/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0060_Precipitation/600 s_sum',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0230_H1/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0070_D1/600 s_mean_polar',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0100_D4/600 s_mean_polar',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0110_D5/600 s_mean_polar',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0200_B1/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0210_B2/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0220_T1/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0240_T2/600 s_mean',
    '/AIRPORT/AD8_PROTOTYPE/ISPIN/SaDataValid/600 s',
    '/AIRPORT/AD8_PROTOTYPE/ISPIN/WS_free_avg/600 s',
    '/AIRPORT/AD8_PROTOTYPE/ISPIN/DataOK/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/BlackTC_110m_HWS_hub/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/BluePO_110m_HWS_hub/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/GreenPO_110m_HWS_hub/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/BlackTC_110m_HWS_hub_availability/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/BluePO_110m_HWS_hub_availability/600 s',
    '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/GreenPO_110m_HWS_hub_availability/600 s',
    '/AIRPORT/AD8_PROTOTYPE/WIND_CUBE/WC_115m_Wind_Speed/600 s'
                ]
# Provide the names that you want to give to the channel paths
data.names = [
        'v1',
        'omega',
        'Pw',
        'v2',
        'v3',
        'v4',
        'v5',
        'v6',
        'prec',
        'prec_sum',
        'RH',
        'd1',
        'd4',
        'd5',
        'b1',
        'b2',
        'T1',
        'T2',
        's_valid',
        's_V', 
        's_ok',
        'btc_v110',
        'bpo_v110', 
        'gpo_v110', 
        'btc_Av110', 
        'bpo_Av110', 
        'gpo_Av110', 
        'wc_v115'
        ]

# folder where data will be stored 
data.folder = r"../data"
# start and end datetime for data download

data.tstart = datetime.strptime('2022-01-01_00-00-00', '%Y-%m-%d_%H-%M-%S') # Select start date in the form yyyy-mm-dd_HH-MM-SS
# funktioniert
data.tend = data.tstart + timedelta(days=monthrange(data.tstart.year, data.tstart.month)[1]) # Select start date in the form yyyy-mm-dd_HH-MM-SS
data.sensors = ['wt', 'ispin', 'btc', 'bpo', 'gpo', 'metmast', 'sonics', 'windcube']
index = pd.date_range(data.tstart, periods=monthrange(data.tstart.year, data.tstart.month)[1], freq='D')
pkl_file = 'monthly_data_{}.pickle'.format(str(data.tstart)[0:10].replace('-','')) 

try:
    # check whether your path exists
    my_abs_path = Path(data.folder + '/' + pkl_file).resolve(strict=True)
except FileNotFoundError:
    # doesn't exist
    print('File not found: Loading data from OneDAS')
    _, pdData, t = FnImportOneDas(data.tstart, data.tend, data.paths, data.names, data.sampleRate, data.folder)
    # create a pandas dataframe
    with open(data.folder +'/' +pkl_file, 'wb') as f:
        pickle.dump(pdData, f)
        pickle.dump(t,f)
else:
    # exists
    print('File found: Loading data from data folder')
    with open(data.folder + '/' + pkl_file, 'rb') as f:
        pdData = pickle.load(f)
        t = pickle.load(f)
        
# %%
