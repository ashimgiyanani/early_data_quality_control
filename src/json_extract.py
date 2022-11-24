def FnLuftdaten_uba(tstart, tend, station, component, url, plotFig=1):

    import requests
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from datetime import timedelta
    
    # Find every instance of `name` in a Python dictionary.
    if url == None:
        url = "https://www.umweltbundesamt.de/api/air_data/v2/measures/json"
    else:
        url = url

    parameters= {
        "date_from": tstart.date(),
        "time_from": tstart.time().hour+1,
        "date_to": tend.date() - timedelta(hours=1),
        "time_to": tend.time().hour+1,
        "station": station,
        "component": component,
    }
    params = parameters
    r = requests.get(url, params= parameters)
    jdata = r.json()
    t, value = [], []
    for k, v in jdata.items():
        if k =='data':
            for k1, v1 in v.items():
                if k1 == '620':
                    for k2, v2 in v1.items():
                        t.append(k2)
                        print(k2)
                        value.append(v2[2])
                    
    df = pd.DataFrame(np.transpose([t,value]), columns=['time','PM10'], index = t)
    df = df.sort_values(by='time')
    
    if plotFig==1:
        # import matplotlib.dates as mdates
        # date_fmt = mdates.DateFormatter('%d/%m')
        # fig, ax = plt.subplots()
        plt.plot(df.PM10, 'k.', label='pm10')
        # plt.axis([df.time[0], df.time[-1], 0, 50])
        plt.legend(loc=1)
        plt.xlabel('Time [hh:mm:ss]')
        plt.ylabel('particulate matter [µg/m³]')
        # plt.xticks(rotation=30)
        # ax.xaxis.set_major_formatter(date_fmt)
        plt.show()

    return df

# Example:
import datetime as dt
from datetime import datetime, timedelta

# input tstart and tend in datetime format
tstart = datetime.strptime('2022-01-17_00-00-00', '%Y-%m-%d_%H-%M-%S')
tend = datetime.strptime('2022-01-24_00-00-00', '%Y-%m-%d_%H-%M-%S')
# url for measurements at UBA (default = given)
url = "https://www.umweltbundesamt.de/api/air_data/v2/measures/json"
station = 620
component = 1
df = FnLuftdaten_uba(tstart, tend, station, component, url= None, plotFig=0)

