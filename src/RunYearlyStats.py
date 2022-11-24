# Script to derive yearly stats from data

#%% user modules
import pandas as pd
import glob
import os
import numpy as np
import sys
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
import dill

#%% user definitions
input = struct()
output = struct()
#%%
data = struct()
data.sampleRate = 1/600
input.AppendLog = 0
input.dump = True

if input.dump==True:
        # must all be of the same sample rate
        data.paths = [
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0000_V1/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0010_V2/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0050_V6/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0070_D1/600 s_mean_polar',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/M0110_D5/600 s_mean_polar',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/P2250_r_YawTwNacellePosDegrees/600 s_mean_polar',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/P0420_RotorSpdRaw/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/P1000_TotalPwMeas/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/GENERAL_DAQ/C0010_Availability/600 s_mean',
        '/AIRPORT/AD8_PROTOTYPE/ISPIN/SaDataValid/600 s',
        '/AIRPORT/AD8_PROTOTYPE/ISPIN/WS_free_avg/600 s',
        '/AIRPORT/AD8_PROTOTYPE/ISPIN/DataOK/600 s',
        '/AIRPORT/AD8_PROTOTYPE/ISPIN/True_Heading_Avg/600 s'
                        ]
        # Provide the names that you want to give to the channel paths
        data.names = [
                'v1',
                'v2',
                'v6',
                'd1',
                'd5',
                'wt_yaw',
                'omega',
                'Pw',
                'wt_Av',
                's_valid',
                's_V', 
                's_ok',
                's_twd',
                ]

        # folder where data will be stored 
        data.folder = r"../data"
        # start and end datetime for data download
        data.tstart = datetime.strptime('2022-05-18_00-00-00', '%Y-%m-%d_%H-%M-%S') # Select start date in the form yyyy-mm-dd_HH-MM-SS
        # funktioniert
        data.tend = data.tstart + timedelta(days=365) # Select start date in the form yyyy-mm-dd_HH-MM-SS
        data.tend = datetime.strptime('2022-05-22_00-00-00', '%Y-%m-%d_%H-%M-%S')
        _, pdData, t = FnImportOneDas(data.tstart, data.tend, data.paths, data.names, data.sampleRate, data.folder)

        output.pkl_path = r"c:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\DataQualityControl\data\{0}_data_stats_{1}_{2}".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d'))
        dill.dump_session(output.pkl_path)
        dill.dump_session(output.pkl_path)
else:
        output.pkl_path = r"c:\Users\giyash\OneDrive - Fraunhofer\Python\Scripts\DataQualityControl\data\{0}_data_stats_{1}_{2}".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d'))
        dill.load_session(output.pkl_path)

#%% Filter data
from FnWsRange import FnWsRange
x = FnWsRange(pdData.s_V,1, 20, flag=np.nan, verbose=True)
# Weibull
# bars = 1
from FnWeibull import FnWeibull
nbins = 21
x_range = (0,20)
k, A, bin_center, bins, vals, fig, ax = FnWeibull(x.dropna(),nbins, x_range)
fig.savefig(r"../results/{0}_weibull_ispin_{1}_{2}.png".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d')), bbox_inches='tight') 


##Neat solution to a weibull fit
from scipy import stats
import matplotlib.pyplot as plt
# #The a and loc are fixed in the fit since it is standard to assume they are known
a_out, Kappa_out, loc_out, Lambda_out = stats.exponweib.fit(pdData.s_V.dropna())

# #Plot
bins = range(32)
fig = plt.figure() 
ax = fig.add_subplot(1, 1, 1)
ax.plot(bins, stats.exponweib.pdf(bins, a=a_out,c=Kappa_out,loc=loc_out,scale = Lambda_out))
ax.hist(pdData.s_V.dropna(), bins = bins , density=True, alpha=0.5)
ax.annotate("Shape: $k = %.2f$ \n Scale: $\lambda = %.2f$"%(Kappa_out,Lambda_out), xy=(0.7, 0.85), xycoords=ax.transAxes)
ax.xlabel('Wind speed bins [m/s]')
ax.ylabel('density fraction [-]')
plt.show()

#%% windrose
if windrose == True:
    from FnWindRose import FnWindRose, FnWindRose_mainsectors
    title, plotFig= False, True
    uu, dd, fig, ax = FnWindRose(pdData.s_twd[pdData.s_V.between(1,35)], pdData.s_V[pdData.s_V.between(1,35)] , title, plotFig)
    median_dd, mean_dd, std_dd = FnWindRose_mainsectors(dd)
    fig.savefig(r"../results/{0}_windrose_iSpin_{1}_{2}.png".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d')), bbox_inches='tight') 


#%% 
condlist = [pdData.omega.between(0.1, 50), pdData.Pw.isna(), ~pdData.Pw.apply(np.isfinite), pdData.Pw.isnull()]
choicelist = [1, 0, 0, 0]
pdData['Avail'] = np.select(condlist, choicelist, 0)
daily_Av = pdData.groupby(pdData.index.date).sum().Avail/144
import plotly.express as px
fig = px.bar(daily_Av, x=pd.to_datetime(daily_Av.index), y="Avail", color='Avail', orientation='v',
        #      hover_data=[daily_Av.index],
             height=600,
             width=1200,
             color_continuous_scale=['firebrick', '#2ca02c'],
        #      title='Data Availabiltiy Plot',
             template='plotly_white',
            )

# fig.update_layout(yaxis=daily_Av.index, xaxis=dict(title='', showgrid=False, gridcolor='grey',
#                   tickvals=[],
#                             )
#                  )
fig.show()
fig.write_html(r"../results/{0}_timeline_ispin_{1}_{2}.html".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d'))) 
# %%

daily_pdData = pdData.groupby(pdData.index.date).mean()
daily_pdData.v1.between(0.5,40)
# New plot with sensors
fig,ax = plt.subplots(4,1, figsize =  (10, 18),sharex=True)
ax[0].plot(daily_pdData.index[daily_pdData.v1.between(0.5,40)] , daily_pdData.v1[daily_pdData.v1.between(0.5,40)] ,'b.',label = 'v1@115m')
# ax[0].set_xlabel('date')
ax[0].set_ylabel("wind speed [m/s]")
date_form = DateFormatter("%d/%m/%y")
ax[0].xaxis.set_major_formatter(date_form)
ax[0].set_xlim([ datetime.strptime(str(data.tstart), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(data.tend), '%Y-%m-%d %H:%M:%S')])
ax[0].set_ylim([-2,25])
ax[0].legend(loc=1)
ax[0].grid(axis = 'x', color='0.95')

ax[1].plot(daily_pdData.index[daily_pdData.v2.between(0.5,40)] , daily_pdData.v2[daily_pdData.v2.between(0.5,40)],'g.',label = 'v2@115m')
# ax[0].set_xlabel('date')
ax[1].set_ylabel("wind speed [m/s]")
date_form = DateFormatter("%d/%m/%y")
ax[1].xaxis.set_major_formatter(date_form)
ax[1].set_xlim([ datetime.strptime(str(data.tstart), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(data.tend), '%Y-%m-%d %H:%M:%S')])
ax[1].set_ylim([-2,25])
ax[1].legend(loc=1)
ax[1].grid(axis = 'x', color='0.95')

ax[2].plot(daily_pdData.index[daily_pdData.v6.between(0.5,40)] , daily_pdData.v6[daily_pdData.v6.between(0.5,40)],'r.',label = 'v6@115m')
# ax[0].set_xlabel('date')
ax[2].set_ylabel("wind speed [m/s]")
date_form = DateFormatter("%d/%m/%y")
ax[2].xaxis.set_major_formatter(date_form)
ax[2].set_xlim([ datetime.strptime(str(data.tstart), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(data.tend), '%Y-%m-%d %H:%M:%S')])
ax[2].set_ylim([-2,25])
ax[2].legend(loc=1)
ax[2].grid(axis = 'x', color='0.95')

ax[3].plot(daily_pdData.index[daily_pdData.s_V.between(0.5,40)] , daily_pdData.s_V[daily_pdData.s_V.between(0.5,40)] ,'k.',label = 'ispin V@115m')
ax[3].set_xlabel('date')
ax[3].set_ylabel("iSpin wind speed [m/s]")
date_form = DateFormatter("%d/%m/%y")
ax[3].xaxis.set_major_formatter(date_form)
ax[3].set_xlim([ datetime.strptime(str(data.tstart), '%Y-%m-%d %H:%M:%S'), datetime.strptime(str(data.tend), '%Y-%m-%d %H:%M:%S')])
ax[3].set_ylim([-2,25])
ax[3].legend(loc=1)
ax[3].grid(axis = 'x', color='0.95')
plt.xticks(rotation=30)

fig.savefig(r"../results/{0}_timeseries_{1}_{2}.png".format(now().replace('.', '')[0:8], data.tstart.date().strftime('%Y%m%d'), data.tend.date().strftime('%Y%m%d')), bbox_inches='tight')

# %%
pdData.Pw.plot()
# %%
plt.plot(pdData.index, pdData.Pw, 'k.')
plt.xticks(rotation=30)
plt.xlabel('Date')
plt.ylabel('Power [kW]')

plt.plot(pdData.v1[pdData.Pw.between(100,8500)], pdData.Pw[pdData.Pw.between(100,8500)],'k.')
plt.xlabel('windspeed [m/s]')
plt.ylabel('Power [kW]')

# %%
