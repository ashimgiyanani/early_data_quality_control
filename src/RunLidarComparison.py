#%% load modules
from fileinput import filename
import sys
import datetime as dt
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from matplotlib.dates import DateFormatter
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import pandas as pd
import xarray as xr
from mpl_toolkits.mplot3d import Axes3D
import glob

# sys.path.insert(1, r'c:\Users\giyash\ownCloud\Data\TestfeldBHV')
sys.path.append(r"c:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\userModules")
sys.path.append(r"c:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\OneDasExplorer\Python Connector")
from pythonAssist import struct
import matlab2py as m2p

plt.style.use('seaborn-whitegrid')
SMALL_SIZE = 22
MEDIUM_SIZE = 22
BIGGER_SIZE = 22

plt.rc('font', size=SMALL_SIZE,weight = 'bold')          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rc('figure', figsize =  (8, 8))

# Change parameters to select the data
inp = struct()
inp.device = 'GreenPO' #Select between GreenPO, BluePO, BlackTC, could be a list of Lidars

# ideal range and timestamps
inp.R0 = [ 50,  70,  90, 110, 130, 150, 160, 170, 180, 190, 210, 230, 260,
       310, 360, 410, 460, 510, 560, 660]
dt_start =dt.datetime.strptime('2021-01-01_00-00-00', '%Y-%m-%d_%H-%M-%S') # Select start date in the form yyyy-mm-dd_HH-MM-SS
dt_end = dt_start  + dt.timedelta(days=365)# Select end date in the form yyyy-mm-dd_HH-MM-SS
dt_end = dt.datetime.strptime('2021-12-31_00-00-00', '%Y-%m-%d_%H-%M-%S') # Select start date in the form yyyy-mm-dd_HH-MM-SS
inp.dt_start = dt_start.strftime('%Y-%m-%d_%H-%M-%S')
inp.dt_end = dt_end.strftime('%Y-%m-%d_%H-%M-%S')
inp.T0 = pd.date_range(dt_start+dt.timedelta(minutes=10), dt_end, freq= '10T')
i_RaworAverage = 1 #Select if you want to look into raw (0) or average data (1)
getData = 2 #  saving array (1) or loading array (0)  or get and save Data (2)

if (getData == 1) | (getData == 2):
    # Set path
    inp.path1 = r"Z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\04_Nacelle-Lidars-Inflow_CONFIDENTIAL\30_Data\\"
    # same device, but different data folder
    inp.path2 = r"Z:\Projekte\109797-TestfeldBHV\30_Technical_execution_Confidential\TP3\AP2_Aufbau_Infrastruktur\Infrastruktur_Windmessung\02_Equipment\04_Nacelle-Lidars-Inflow_CONFIDENTIAL\30_Data\HourlyData\\"
    # Load all data for all three instruments
    df = {}
    from f_import_nacelle_lidar_data import f_import_nacelle_lidar_data
    # import data
    device='GreenPO'
    usecols = [
        'Date and Time',
        'Distance',
        'HWS hub',
        'HEIGHT high',
        'HEIGHT low',
    ]
    df[0] = f_import_nacelle_lidar_data(inp.path1,device,i_RaworAverage,inp.dt_start,inp.dt_end, usecols=usecols)
    df[1] = f_import_nacelle_lidar_data(inp.path2,device,i_RaworAverage,inp.dt_start,inp.dt_end, usecols=usecols)

    #%% import data from oneDAs for comparison 
    inp.sampleRate = 1/600
    inp.AppendLog = 0
    # must all be of the same sample rate
    inp.paths = [
        '/AIRPORT/AD8_PROTOTYPE/LIDAR_2020/GreenPO_050m_HWS_hub/600 s',
        '/AIRPORT/AD8_PROTOTYPE/ISPIN/WS_free_avg/600 s'
                    ]
    # Provide the names that you want to give to the channel paths
    inp.names = [
            'gpo_v50',
            'ispin_v', 
            ]

    # folder where data will be stored 
    inp.folder = r"../data"
    from FnImportOneDas import FnImportOneDas
    import re
    df[2] = []
    for r in inp.R0:
        paths = [re.sub("_\d+m_","_{0:03d}m_".format((r)),inp.paths[0])]
        names = ['gpo_hws']
        _, df_temp, T3 = FnImportOneDas(dt_start, dt_end, paths, names, inp.sampleRate, inp.folder)
        df[2].append(df_temp.assign(Distance=r))
    df[2] = pd.concat(df[2])
    df[2] = df[2].rename(columns={"t":"Date and Time"})

    del df_temp
    #%% pre-processing data
    df_new = {}
    for i in range(len(df)):
        df_temp = []
        # check if the range gates are matching
        if (df[i].Distance.unique() == inp.R0).all():
            print('Range gates matching')
        else:
            print('check the range gates')
        
        for r in inp.R0:
            cond = (df[i]['Distance'] == r)
            # check if the timestamps are matching
            try:
                (df[i][cond]['Date and Time'] == inp.T0).all()
                df_temp.append(df[i][cond].set_index('Date and Time').resample('10T').asfreq(fill_value=np.nan))
                print('Timestamps matching')
            except (ValueError,TypeError, NameError):
                df_temp.append(df[i][cond].set_index('Date and Time').resample('10T').asfreq(fill_value=np.nan))
                print('Timestamps corrected for gaps, should match now')
        df_new[i] = pd.concat(df_temp)
        del df_temp
# save the pre-processed dataframe and orginal dataframe to a file
elif (getData == 2):
    from pathlib import Path
    filename = r"../data/{0}_{1}_{2}_{3}_{4}.pkl".format(dt.date.today().strftime('%Y%m%d'), Path(__file__).stem, names[0],dt_start.date(), dt_end.date() )
    my_shelf = shelve.open(filename, 'n')
    for key in dir():
        try:
            my_shelf[key] = globals()[key]
        except:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            print('ERROR shelving: {0}'.format(key))			
    my_shelf.close()
else:
    print('check getData value or debug the save-load process')

sys.exit('Manual stop')
#%% correlation
#%% compare against a reference sensor
inp.paths = [
    '/AIRPORT/AD8_PROTOTYPE/ISPIN/WS_free_avg/600 s'
                ]
# Provide the names that you want to give to the channel paths
inp.names = [
        'ispin_v', 
        ]
_, df_temp, T3 = FnImportOneDas(dt_start, dt_end, inp.paths, inp.names, inp.sampleRate, inp.folder)


from FnLinReg_wnddir import FnLinReg_wnddir
from FnWsRange import FnWsRange
for r in inp.R0:
    # assignment
    v1, lab1 = df_new[0].query('Distance==@r')['HWS hub'], 'u_gpo_' + str(r)+ '_Z:'
    v2, lab2 = df_new[1].query('Distance==@r')['HWS hub'], 'u_gpo_' + str(r)+ '_GUI' 
    v3, lab3 = df_new[2].query('Distance==@r')['gpo_hws'], 'u_gpo_' + str(r)+ '_OneDas'
    v4, lab4 = df_temp['ispin_v'], 'u_ispin_OneDas'

    # filtering for non-physical values
    v = [v1, v2, v3, v4]
    lab = [lab1, lab2, lab3, lab4]
    for i in range(len(v)):
        v[i] = FnWsRange(v[i], 0, 40, flag= np.nan, verbose=1)
    
    # Linear regression plots
    R_sq, m, c, fig, ax = FnLinReg_wnddir(v[0].astype('float'), v[1].astype('float'), xstr=lab[0], ystr=lab[1])
    fig.savefig("../results/correlation_{0}.png".format(lab1[0:-1]))
    R_sq, m, c, fig, ax = FnLinReg_wnddir(v[0].astype('float'), v[2].astype('float'), xstr=lab[0], ystr=lab[2])
    fig.savefig(r"../results/correlation_{0}.png".format(lab3))
 
    # timeseries visualization
    import plotly.express as px
    import plotly.graph_objects as go
    fig=go.Figure()
    fig.add_trace(go.Scattergl(name=lab1, mode='markers+lines',x=v[0].index, y=v[0]))
    # fig.add_trace(go.Scatter(name=lab2, mode='markers+lines',x=v[1].index,y=v[1], marker_symbol="star"))
    # fig.add_trace(go.Scatter(name=lab3, mode='markers+lines',x=v[2].index,y=v[2], marker_symbol="x"))
    fig.add_trace(go.Scattergl(name=lab4, mode='markers+lines',x=v[3].index,y=v[3], marker_symbol="x"))
    fig.show()
    fig.write_image(r"../results/timeseries_{0}.png".format(lab1[0:9]))


# timeseries visualization
fig=go.Figure()
fig.add_trace(go.Scatter(name=lab1, mode='markers+lines',x=v[0].index, y=v[0]))
fig.add_trace(go.Scatter(name=lab2, mode='markers+lines',x=v[1].index,y=v[1], marker_symbol="star"))
fig.add_trace(go.Scatter(name=lab3, mode='markers+lines',x=v[2].index,y=df_temp.ispin_v, marker_symbol="x"))
fig.show()

sys.exit('manual stop')
