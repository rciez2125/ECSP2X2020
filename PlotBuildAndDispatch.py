import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

# load fixed data
loadData = pd.read_csv('CSV_Files/HourlyTxScenDemand2018-Notional.csv')
windData = pd.read_csv('CSV_Files/Wind1p5MW.csv')
solarData = pd.read_csv('CSV_Files/Solar1p5MW.csv')

# read json file with output data
def loadScenarioData(fileName):
    with open(fileName) as f:
        data = json.load(f)
    return data

# make a plot with the dispatched assets for every hour 
def plotDispatchCurves(dispatchedAssets, figname, load):
    plt.figure(figsize=(6,4))
    for n in range(len(dispatchedAssets)):
        y = data[dispatchedAssets[n]]
        plt.plot(np.linspace(0,len(y)-1, len(y)), y)
    yl = loadData.demand[0:len(y)]*1000
    if load == 1:
        plt.plot(np.linspace(0, len(y)-1, len(y)), -yl, '-k')
        dispatchedAssets.append('Load')
        plt.legend(dispatchedAssets)
    else:
        plt.legend(dispatchedAssets)
    plt.xlabel('Time [hrs]')
    plt.ylabel('kW')
    plt.savefig(figname, dpi=300)

# plot the installed capacity of different system assets
def plotInstalledSizes(assets, figname):
    plt.figure(figsize=(6,4))
    for n in range(len(assets)):
        y = data[assets[n]]
        plt.bar(n, y)
    plt.xticks(np.linspace(0, n, n+1), assets)
    plt.ylabel('kW')
    plt.savefig(figname, dpi=300)

# plot the energy stored
def plotStorage(dispatchedAssets, figname):
    plt.figure(figsize=(6,4))
    for n in range(len(dispatchedAssets)):
        y = data[dispatchedAssets[n]]
        plt.plot(np.linspace(0, len(y)-1, len(y)), y)
    plt.legend(dispatchedAssets)
    plt.xlabel('Time [hrs]')
    plt.ylabel('kW')
    plt.savefig(figname, dpi=300)

# make a plot of total energy from different sources in different scenarios, along with how much wind/solar end up curtailed
def plotElecByType(scenarios, figname):
    allP = ['png','pbat', 'ppv', 'pw', 'pzn', 'ploss']
    df = pd.DataFrame({'Scenario': scenarios})
    df['Natural Gas'] = np.zeros(len(scenarios))
    df['Battery'] = np.zeros(len(scenarios))
    df['Solar'] = np.zeros(len(scenarios))
    df['Wind'] = np.zeros(len(scenarios))  
    df['Zinc Discharged'] = np.zeros(len(scenarios))
    df['Zinc Production'] = np.zeros(len(scenarios))
    df['Lost Load'] = np.zeros(len(scenarios))
    df['Curtailed Solar'] = np.zeros(len(scenarios)) 
    df['Curtailed Wind'] = np.zeros(len(scenarios))
    xlabels = []

    for m in range(len(scenarios)):
        data = loadScenarioData(scenarios[m])
        df['Wind'].iloc[m] = sum(data['pw'])
        df['Natural Gas'].iloc[m] = sum(data['png'])
        df['Battery'].iloc[m] = sum(data['pbat'])
        df['Solar'].iloc[m] = sum(data['ppv'])

        df['Zinc Discharged'] = sum([num for num in data['pzn'] if num >= 0])
        df['Zinc Production'] = sum([num for num in data['pzn'] if num < 0])

        df['Lost Load'] = sum(data['ploss'])

        df = solarData[0:len(data['ppv'])]
        d1 = (d['System Power Generated | (k)W']/1500) * data['PVSize'] - data['ppv']
        df['Curtailed Solar'].iloc[m] = sum(d1)

        d = windData[0:len(data['pw'])]
        d1 = (d['System Power Generated | (kW)']/1500) * data['WindSize'] - data['pw']
        df['Curtailed Wind'].iloc[m] = sum(d1)

        s = scenarios[m].strip('.json')
        xlabels.append(s)
        del data

    print(df)

    # check to confirm we aren't using the battery or lost load
    print((df['Battery'] == 0).all())
    print((df['Lost Load'] == 0).all())
    # make a figure
    plt.figure(figsize=(7,4))
    fs = 8

    ax1 = plt.subplot(position = [0.1, 0.1, 0.8, 0.5])
    plt.xlim(-0.5, len(scenarios) + 0.5)

    p1 = ax1.bar(df.index, df['Natural Gas'])
    plt.text(len(scenarios) - 0.5, df['Natural Gas'].iloc[-1]/2, 'Natural Gas', fontsize = fs, verticalAlignment = 'center')
    p2 = ax1.bar(df.index, df['Wind'], bottom = df['Natural Gas'])
    plt.text(len(scenarios) - 0.5, df['Natural Gas'].iloc[-1] + df['Wind'].iloc[-1]/2, 'Wind', fontsize = fs, verticalAlignment = 'center')
    p3 = ax1.bar(df.index, df['Solar'], bottom = df['Natural Gas'] + df['Wind'])
    plt.text(len(scenarios) - 0.5, df['Natural Gas'].iloc[-1] + df['Wind'].iloc[-1] + df['Solar'].iloc[-1]/2, 'Solar', fontsize = fs, verticalAlignment = 'center')
    p4 = ax1.bar(df.index, df['Zinc Discharged'], bottom = df['Natural Gas'] + df['Wind'] + df['Solar'])
    plt.text(len(scenarios) - 0.5, df['Natural Gas'].iloc[-1] + df['Wind'].iloc[-1] + df['[Solar'].iloc[-1] + df['Zinc Discharged'].iloc[-1], 'Zinc', fontsize = fs, verticalAlignment = 'center')
    p5 = ax1.bar(df.index, df['Zinc Production'])
    plt.text(len(scenarios) - 0.5, df['Zinc Production'].iloc[-1]/2, 'Zinc Production', fontsize = fs, verticalAlignment = 'center')
    plt.xticks(df,index, labels = xlabels, fontsize = fs)

    plt.plot([-5, 10], [0, 0], '-k')

    ax2 = plt.subplot(position = [0.1, 0.7, 0.8, 0.2])
    plt.xlim(-0.5, len(scenarios) + 0.5)

    p21 = ax2.bar(df.index, df['Curtailed Wind'])
    plt.text(len(scenarios) - 0.5, df['Curtailed Wind'].iloc[-1]/2, 'Curtailed Wind', fontsize = fs, verticalAlignment = 'center')
    p22 = ax2.bar(df.index, df['Curtailed Solar'], bottom = df['Curtailed Wind'])
    plt.xticks(df,index, labels = xlabels, fontsize = fs)

    plt.savefig(figname, dpi=300)

data = loadScenarioData('Baseline20.json')
a = ['pw', 'pbat', 'ppv', 'png', 'pzn', 'ploss']
plotDispatchCurves(a, 'Figures/PowerFlowsBaseline20.png', 1)

# batteries and zinc
b = ['ubatdc', 'ubatc']
plotDispatchCurves(b, 'Figures/BatteriesCharging.png', 0)

b = ['uzndc', 'uznc', 'uznsold', 'xzn']
plotDispatchCurves(b, 'Figures/ZincCharging.png', 0)

print(sum(data['uznsold']))


c = ['xbat', 'xzn']
plotStorage(c, 'Figures/StoredEnergy.png')

c = ['NGGenSize', 'PVSize', 'BatSize', 'WindSize', 'ZnSize', 'FCSize', 'ZnStorageSize']
plotInstalledSizes(c, 'Figures/CapitalAssets.png')

#s = ['LGHW20.json', 'Penetration_Scenarios/Baseline99.json']

#s = ['Penetration_Scenarios/Baseline20.json', 'Penetration_Scenarios/Baseline50.json', 'Penetration_Scenarios/Baseline70.json', 'Penetration_Scenarios/Baseline80.json', 'Penetration_Scenarios/Baseline90.json', 'Penetration_Scenarios/Baseline95.json', 'Penetration_Scenarios/Baseline99.json']
#plotElecByType(s, 'Figures/ElecByType_Baseline.png')

#data = loadScenarioData('Penetration_Scenarios/Baseline99.json')
#a = ['pw', 'pbat', 'ppv', 'png', 'pzn', 'ploss']
#plotDispatchCurves(a, 'Figures/PowerFlowsBaseline99.png', 1)

#s = ['Penetration_Scenarios/LGHW20.json', 'Penetration_Scenarios/LGHW50.json', 'Penetration_Scenarios/LGHW70.json', 'Penetration_Scenarios/LGHW80.json', 'Penetration_Scenarios/LGHW90.json', 'Penetration_Scenarios/LGHW95.json', 'Penetration_Scenarios/LGHW99.json']
#plotElecByType(s, 'Figures/ElecByType_LGHW.png')

#s = ['Penetration_Scenarios/Low20.json', 'Penetration_Scenarios/Low50.json', 'Penetration_Scenarios/Low70.json', 'Penetration_Scenarios/Low80.json', 'Penetration_Scenarios/Low90.json', 'Penetration_Scenarios/Low95.json', 'Penetration_Scenarios/Low99.json']
#plotElecByType(s, 'Figures/ElecByType_Low.png')

#s = ['Penetration_Scenarios/High20.json', 'Penetration_Scenarios/High50.json', 'Penetration_Scenarios/High70.json', 'Penetration_Scenarios/High80.json', 'Penetration_Scenarios/High90.json', 'Penetration_Scenarios/High95.json', 'Penetration_Scenarios/High99.json']
#plotElecByType(s, 'Figures/ElecByType_High.png')
