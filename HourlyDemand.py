# Gets EIA data for hourly demand for Texas and ERCOT South Central
# creates a notional 2018 year for hourly electrical demand in ERCOT SCEN
import sys, os
print(sys.version, '\n')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import json
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#os.environ["EIA_KEY"]="ae68b0dc13a20c6d81e62fbaab46d992"
os.environ["EIA_KEY"] = "b7377dd90900cf2508b4ea504a6e535b"

years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')

from eiapy import Series
tx = Series('EBA.TEX-ALL.D.H')
tx_south = Series('EBA.ERCO-SCEN.D.H')

print(type(tx_south))

class EIAgov(object):
    def __init__(self, token, series):
        '''
        Purpose:
        Initialise the EIAgov class by requesting:
        - EIA token
        - id code(s) of the series to be downloaded

        Parameters:
        - token: string
        - series: string or list of strings
        '''
        self.token = token
        self.series = series

    '''
    def __repr__(self):
        return str(self.series)
    '''

    def Raw(self, ser):
        # Construct url
        url = 'http://api.eia.gov/series/?api_key=' + self.token + '&series_id=' + ser.upper()

        try:
            # URL request, URL opener, read content
            response = urlopen(url);
            raw_byte = response.read()
            raw_string = str(raw_byte, 'utf-8-sig')
            jso = json.loads(raw_string)
            return jso

        except HTTPError as e:
            print('HTTP error type.')
            print('Error code: ', e.code)

        except URLError as e:
            print('URL type error.')
            print('Reason: ', e.reason)

    def GetData(self):
        # Deal with the date series                       
        date_ = self.Raw(self.series[0])        
        date_series = date_['series'][0]['data']
        endi = len(date_series) # or len(date_['series'][0]['data'])
        date = []
        for i in range (endi):
            date.append(date_series[i][0])

        # Create dataframe
        df = pd.DataFrame(data=date)
        df.columns = ['Date']

        # Deal with data
        lenj = len(self.series)
        for j in range (lenj):
            data_ = self.Raw(self.series[j])
            data_series = data_['series'][0]['data']
            data = []
            endk = len(date_series)         
            for k in range (endk):
                data.append(data_series[k][1])
            df[self.series[j]] = data
        
        return df

if __name__ == '__main__':
    tok = 'b7377dd90900cf2508b4ea504a6e535b'#'e924bc140b111249b616ec1d53a91b6a'
  	
  	# Texas hourly electricity demand
    tx = ['EBA.TEX-ALL.D.H']
    data = EIAgov(tok, tx)
    tx = data.GetData()
    tx = tx.rename(columns = {'EBA.TEX-ALL.D.H':'demand'})

    # Texas hourly electricity demand
    tx_south = ['EBA.ERCO-SCEN.D.H']
    dataTxS = EIAgov(tok, tx_south)
    tx_s = dataTxS.GetData()
    tx_s = tx_s.rename(columns = {'EBA.ERCO-SCEN.D.H':'demand'})

# convert date and time info to datetime object
def cleanUpDateTime(df):
    # creates a function to convert from string to datetime info
    # still need to add info to keep time zone info
    df['DateTime'] = ""
    for n in range(df.shape[0]):
        y = df.Date[n].replace("T", "")
        z = y.replace("Z", "")
        df['DateTime'][n] = datetime.strptime(z, '%Y%m%d%H')
    return(df)

tx = cleanUpDateTime(tx)
tx_s = cleanUpDateTime(tx_s)

# make a figure
def plotTXandTXSouth(demandData, figName):

    plt.figure(figsize=(5,3))

    fig, ax = plt.subplots()

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    plt.plot(demandData.DateTime, demandData.demand)

    ax.set_title('Power Demand')
    plt.ylim(0)
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand (in MW-hrs')

    plt.savefig(figName, dpi=300)

plotTXandTXSouth(tx, 'Figures/HourlyTexasElecDemand.png')
plotTXandTXSouth(tx_s, 'Figures/HourlyTexasSouthElecDemand.png')

# find min and max demands
max_tex = max(tx.demand)
print('Maximum demand, Texas:', max_tex)
min_tex = min(tx.demand)
print('Minimum demand, Texas:', min_tex)
max_tex_south = max(tx_s.demand)
print('Maximum demand, South Central Texas:', max_tex_south)
min_tex_south = min(tx_s.demand)
print('Minimum demand, South Central Texas:', min_tex_south)

# find scale factor between South Central Texas and Texas
ratio = max_tex_south/max_tex
print('Max ERCOT South Central/Max ALL Texas:', ratio)

# set the DateTime to be the index
tx = tx.set_index(['DateTime'])
tx_s = tx_s.set_index(['DateTime'])

# slice 2018 from ALL-Texas demand, save it to csv file
txSlice = tx['2019-01-01 00:00:00' : '2018-01-01 00:00:00']
tx2018 = txSlice.iloc[::-1]
tx2018.to_csv('CSV_Files/HourlyTxDemand2018.csv')

# create a notional 2018 hourly electrical demand for ERCOT SCEN based on ratio of peaks
tx_SCEN = tx2018.copy()
tx_SCEN["demand"]*=ratio
tx_SCEN.to_csv('CSV_Files/HourlyTxScenDemand2018-Notional.csv')
print(tx_SCEN.head())
tx_SCEN = cleanUpDateTime(tx_SCEN)
print(tx_SCEN.head())

plotTXandTXSouth(tx_SCEN, 'Figures/HourlyTxScenDemand2018-Notional.png')


