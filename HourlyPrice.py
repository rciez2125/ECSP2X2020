# Loads EIA data on monthly natural gas and electricity prices
# upsamples gas prices for use in hourly dispatch model
import sys, os
print(sys.version,sys.path)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import json
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


os.environ["EIA_KEY"]="ae68b0dc13a20c6d81e62fbaab46d992"

years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')

from eiapy import Series
ng_tx = Series('NG.N3045TX3.M')
print(type(ng_tx))

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
    tok = 'e924bc140b111249b616ec1d53a91b6a'
        
    # Natural Gas - Daily prices
    # http://www.eia.gov/beta/api/qb.cfm?category=462457&sdid=NG.RNGC1.D
    # natural gas, monthly, Texas, all sectors average price, in $/1,000 cu ft
    ng_tx = ['NG.N3045TX3.M']
    ng_tx_data = EIAgov(tok, ng_tx)
    ng_tx = ng_tx_data.GetData()
    ng_tx = ng_tx.rename(columns={'NG.N3045TX3.M':'price'})

    # electricity price, monthly, Texas, all sectors average retail price, in cents/kWh
    elec_tx = ['ELEC.PRICE.TX-ALL.M']
    elec_tx_data = EIAgov(tok, elec_tx)
    elec_tx = elec_tx_data.GetData()
    elec_tx = elec_tx.rename(columns={'ELEC.PRICE.TX-ALL.M':'price'})

    # convert date and time info to datetime object
    def cleanUpDateTime(df):
        # creates a function to convert from string to datetime info
        # still need to add info to keep time zone info
        df['DateTime']=""
        for n in range(df.shape[0]):
            y = df.Date[n].replace("T","")
            z = y.replace("Z","")
            df['DateTime'][n] = datetime.strptime(z, '%Y%m')
        return(df)

    ng_tx = cleanUpDateTime(ng_tx)
    elec_tx = cleanUpDateTime(elec_tx)

    # set the datetime info to be the index
    ng_tx = ng_tx.set_index(['DateTime'])
    elec_tx = elec_tx.set_index(['DateTime'])

    # save csv files of monthly natural gas and electricity prices
    ng_tx.to_csv('CSV_Files/MonthlyNatGasPrices.csv')
    elec_tx.to_csv('CSV_Files/MonthlyElectricityPrices.csv')

    print('convertedIndex', ng_tx.head(5))
    # make a figure
    def plotGasAndElecPrices(priceData, figName):

        plt.figure(figsize=(5,3))
        # add a matplotlib converter to get rid of this error

        fig, ax = plt.subplots()
        # rotate and align the tick labels so they look better
        fig.autofmt_xdate()

        plt.plot(priceData.index, priceData.price)

        # use a more precise date string for the x axis locations in the toolbar
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m')

        # add x and y axis labels  
        plt.ylim(0)
        plt.ylabel('Price [$/thousand cu ft]')
        plt.xlabel('Month')

        plt.savefig(figName, dpi=300)

    plotGasAndElecPrices(ng_tx, 'Figures/MonthlyTexasGasPrices.png')
    plotGasAndElecPrices(elec_tx, 'Figures/MonthlyTexasElecPrices.png')

    def plotSubset(priceData, figName, startDate, endDate):
        subset = priceData.loc[endDate:startDate] # note the reverse chronological order end:start
        print(subset)
        plotGasAndElecPrices(subset, figName)

    plotSubset(ng_tx, 'Figures/MonthlyTexas2018GasPrices.png', '2018-01-01','2018-12-01')

    print('convertedIndex', elec_tx.head(5))
    # make electricity figure
    def plotGasAndElecPrices(priceData, figName):

        plt.figure(figsize=(5,3))
        # add a matplotlib to get rid of this error

        fig, ax = plt.subplots()
        # rotate and align the tick labels so they look better

        fig.autofmt_xdate()

        plt.plot(priceData.index, priceData.price)

        # use a more precise date sring for the x axis locations in the toolbar
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m')
        
        # add x and y labels
        plt.ylim(0)
        plt.ylabel('Price [cents/kWh]')
        plt.xlabel('Month')

        plt.savefig(figName, dpi = 300)

    def plotSubset(priceData, figName, startDate, endDate):
        subset = priceData.loc[endDate:startDate] # note the reverse chronological order end:start
        print(subset)
        plotGasAndElecPrices(subset, figName)

    plotSubset(elec_tx, 'Figures/MonthlyTexas2018ElecPrices.png','2018-01-01','2018-12-01')

# upsamples monthly gas prices to hourly for use in the hourly dispatch model
costs = pd.read_csv("CSV_Files/MonthlyNatGasPrices.csv", parse_dates=["DateTime"],date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"), index_col="DateTime")
costsSlice = costs['2019-01-01' : '2018-01-01']
upsampled = costsSlice.price.resample('H').ffill()
upsampled.to_csv('CSV_Files/HourlyNatGasPrices2018.csv')
    