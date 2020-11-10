# Two-stage stochastic model, bilevel decision-making
# 1 - Capital Assets to build
# 2 - Dispatch decisions for generation and storage assets
import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory
import json
import random

class SystemBilevelModel:
    def __init__(self, name, scenarioFile, outfileName, minimumRenewableElec):
        self.user = name
        global inputfile, savefile, renMin
        inputfile = scenarioFile
        savefile = outfileName
        renMin = minimumRenewableElec

    def makeSolveAbstractModel(self):
        model = AbstractModel()

        # create empty parameters for capital expenses, fixed and variable O&M, efficiencies, prices
        model.NGCapEx = Param()
        model.PVCapEx = Param()
        model.BatCapEx = Param()
        model.ZnCapEx = Param()
        model.ZnStorCapEx = Param()
        model.FCCapEx = Param()
        model.WindCapEx = Param()
        
        model.NGeff = Param()
        model.Bateff = Param()
        model.Zneff = Param()
        model.PEMeff = Param()
        
        model.NGfom = Param()
        model.PVfom = Param()
        model.Windfom = Param()
        model.ZnProdfom = Param()
        model.ZnStorfom = Param()
        model.ZnLaborfom = Param()
        model.Batfom = Param()
        model.FCfom = Param()
        
        model.elecPriceWholesale = Param()
        model.elecPriceIndustrial = Param()
        model.elecPricePremiumStorage = Param()
        model.refinedZincPremium = Param()

        model.lostLoadCost = Param()

        model.NGvom = Param()
        model.FCvom = Param()
        model.Batvom = Param()

        # create variables for the component sizes, add some preliminary upper and lower bounds (additional constraints added specifically later)
        model.NGGenSize = Var(bounds = (0,None), initialize = 1000) # Var(bounds = (0.0, None))
        model.PVSize = Var(bounds = (0,None), initialize = 100) #Var(bounds = (0.0, None))
        model.BatSize = Var(bounds = (0,None), initialize = 100) #Var(bounds = (0.0, None))
        model.WindSize = Var(bounds = (0,None), initialize = 10)
        model.ZnSize = Var(bounds = (0,None), initialize = 500) # maximum capacity in kg/hr of zinc produced
        model.ZnStorageSize = Var(bounds = (0,None), initialize = 1000) # maximum capacity in kg of zinc 
        model.FCSize = Var(bounds = (0,None), initialize = 20)

        # Specify the length of time simulated (up to 1 year)
        T = 24*7*51
        model.I = RangeSet(1, T)

        # Create the state variables (battery and zinc), add some initial upper and lower bounds (specific constraints defined later)
        model.xbat =    Var(model.I, bounds = (0,None), initialize = 1)
        model.xzn =     Var(model.I, bounds = (0,None), initialize = 1)

        # Create the control variables that affect the state variables over time. Add some initial constraints 
        model.ung =     Var(model.I, initialize = 10) # natural gas output chnage
        model.ubatc =   Var(model.I, bounds = (0, None), initialize = 0) # battery charging
        model.ubatdc =  Var(model.I, bounds = (0, None), initialize = 0) # battery discharging 
        model.uzndc =   Var(model.I, bounds = (0, None), initialize = 0) # zinc discharging
        model.uznc =    Var(model.I, bounds = (0, None),initialize = 0) # zinc charging
        model.uznsold = Var(model.I, bounds = (0, None), initialize = 0) # zinc sales 

        # Create the power flow variables. Similar, but not exactly the same as the control variables. Add specific definitions/constraints later
        model.png =     Var(model.I, bounds = (0, None), initialize = 10000) # power from natural gas
        model.ppv =     Var(model.I, bounds = (0, None), initialize = 1) # power from pv
        model.pw =      Var(model.I, bounds = (0, None), initialize = 1) # power from wind
        model.pbat =    Var(model.I, initialize = 0) # power from the battery
        model.pzn =     Var(model.I, initialize = 0) # power from zinc
        model.ploss =   Var(model.I, bounds = (0,None), initialize = 0) # lost load option, this will be very expensive

        # read csv files
        solarData = pd.read_csv('CSV_Files/Solar1p5MW.csv')
        windData = pd.read_csv('CSV_Files/Wind1p5MW.csv')
        loadData = pd.read_csv('CSV_Files/HourlyTxScenDemand2018-Notional.csv')
        ngPrice = pd.read_csv('CSV_Files/HourlyNatGasPrices2018.csv')

        def initEpv(model, i):
            return float(solarData['System power generated | (kW)'].iloc[i-1]/1500) # scaled to be per kW of installed solar capacity

        def initEw(model, i):
            return float(windData['System power generated | (kW)'].iloc[i-1]/1500) # scaled to be per kW of installed wind capacity

        def initLoad(model, i):
            return float(loadData.demand.iloc[i-1]*1000) # converts from MW to kW

        def calcTotalLoad(T):
            return sum(loadData.demand[0:T-1]*1000) # converts from MW to kW
        L = calcTotalLoad(T)
        print('Total Load:', L)

        print('Zn Electricity', (101000000 * 4.8 * T/8760))

        totalElecRen = (L + (101000000 * 4.8 * T/8760)) * renMin

        def initNGPrice(model, i):
            return float(ngPrice.iloc[i-1,1]/297.395) # converts $/cu ft to $/kWh

        #create a matrix that specifies additional overtime labor costs for zinc production or zinc oxidation for electricity 
        def initZnOT(model, i): 
            n = i%168
            if n<144:
                m = i%24
                if m<9:
                    y = 0
                else:
                    y = 20 * 1.5 # time and a half
            else:
                y = 20 * 1.5
            return y

        # initialize energy constraints for every hour on pv, wind, load, overtime, and natural gas prices
        model.Epv = Param(model.I, initialize = initEpv)
        model.Ew = Param(model.I, initialize = initEw)
        model.Eload = Param(model.I, initialize = initLoad)
        model.ZnOT = Param(model.I, initialize = initZnOT)
        model.NGPrice = Param(model.I, initialize = initNGPrice)

        # define specific constraints

        def renewablePVLimits(model, t):
            return model.ppv[t] <= model.Epv[t] * model.PVSize
        model.renewablePVLimits = Constraint(model.I, rule = renewablePVLimits)

        def renewableWindLimits(model, t):
            return model.pw[t] <= model.Ew[t] * model.WindSize
        model.renewableWindLimits = Constraint(model.I, rule = renewableWindLimits)

        # require a minimum amount of power to come from renewables
        def renewableMinimum(model):
            return(summation(model.ppv) + summation(model.pw)) >= totalElecRen
        model.renewableMinimum = Constraint(rule = renewableMinimum)

        def ngMax(model, t):
            return model.png[t] <= model.NGGenSize
        model.ngMax = Constraint(model.I, rule = ngMax)

        # gas generator power state changing based on control
        def ngTime(model, t):
            if t < T:
                return model.png[t+1] == model.png[t] + model.ung[t]
            else:
                return Constraint.Skip
        model.ngTime = Constraint(model.I, rule = ngTime)

        # gas generator ramp rate limits
        def ngRampLimit(model, t):
            return model.ung[t] <= model.NGGenSize
        def ngThrottleLimit(model, t):
            return model.ung[t] >= -1 * model.NGGenSize
        model.ngRampLimit = Constraint(model.I, rule = ngRampLimit)
        model.ngThrottleLimit = Constraint(model.I, rule = ngThrottleLimit)

        # battery charge state based on charging, discharging
        def batTime(model, t):
            if t > T:
                return model.xbat[t+1] == model.xbat[t] - model.ubatdc[t] + (model.Bateff * model.ubatc)
            else:
                return Constraint.Skip
        model.batTime = Constraint(model.I, rule = batTime)
        
        # specify the battery's minimum charge state
        def batMin(model, t):
            return model.xbat[t] >= 0.2 * model.BatSize
        model.batMin = Constraint(model.I, rule = batMin)

        # specify the battery's max charge state
        def batMax(model, t):
            return model.xbat[t] <= model.BatSize
        model.batMax = Constraint(model.I, rule = batMax)

        # set a starting charge for the battery (20%)
        def batStart(model):
            return model.xbat[1] == 0.2 * model.BatSize
        model.batStart = Constraint(rule = batStart)

        # calculate battery power discharging into the grid, with associated inefficiency
        def batPower(model, t):
            return model.Bateff * model.ubatdc[t] - model.ubatc[t] == model.pbat[t]
        model.batPower = Constraint(model.I, rule = batPower)

        # maximum charge/discharge rate for batteries is limited to C/4
        def chargeMax(model, t):
            return model.ubatc[t] <= 0.25 * model.BatSize
        def dischargeMax(model, t):
            return model.ubatdc[t] <= 0.25 * model.BatSize
        model.chargeMax = Constraint(model.I, rule = chargeMax)
        model.dischargeMax = Constraint(model.I, rule = dischargeMax)

        # set minimum production quota for zinc refinery
        def znProdQuota(model):
            return summation(model.uznsold) - model.uznsold[T] >= (101000000*T/8760)
        model.znProdQuota = Constraint(rule = znProdQuota)

        # set maximum production capacity for zinc refinery
        def znProdMax(model):
            return summation(model.uznsold) <= (200000000*T/8760)
        model.znProdMax = Constraint(rule = znProdMax)

        # zinc stored starts at zero
        def znStart(model):
            return model.xzn[1] == 0
        model.znStart = Constraint(rule = znStart)

        # ensure model does not produce negative value for zinc storage
        def znStorMin(model, t):
            return model.xzn[t] >= 0
        model.znStorMin = Constraint(model.I, rule = znStorMin)

        # buying zinc from an external source (negative sales) is not allowed
        def cantbuy(model, t):
            return model.uznsold[t] >= 0
        model.cantbuy = Constraint(model.I, rule = cantbuy)

        # specify maximum storage capacity for refined zinc
        def znMax(model, t):
            return model.xzn[t] <= model.ZnStorageSize
        model.znMax = Constraint(model.I, rule = znMax)

        # no zinc has been sold initially
        def znSaleStart(model):
            return model.uznsold[1] == 0
        model.znSaleStart = Constraint(rule = znSaleStart)

        # zinc sales can't exceed zinc storage capacity
        def znForSale(model, t):
            return model.uznsold[t] <= model.ZnStorageSize
            if t == 1:
                return model.uznsold[t] == 0
            elif t < T:
                return model.uznsold[t+1] <= model.xzn[t]
            else:
                return model.uznsold[t] == 0
        model.znForSale = Constraint(model.I, rule = znForSale)

        # calculate power the zinc provides (based on fuel cell efficiency)
        def znPower(model, t):
            return model.PEMeff * model.uzndc[t] - model.uznc[t] == model.pzn[t]
        model.znPower = Constraint(model.I, rule = znPower)

        # maximum charge/discharge rate for zinc is limited by production capacity and fuel cell capacity, efficiency
        def ZnChargeMax(model, t):
            return model.uznc[t] <= model.ZnSize
        def ZnDischargeMax(model, t):
            return model.uzndc[t] <= model.FCSize/model.PEMeff
        model.ZnChargeMax = Constraint(model.I, rule = ZnChargeMax)
        model.ZnDischargeMax = Constraint(model.I, rule = ZnDischargeMax)

        # change to zinc stored based on production, "discharge", sale
        def znTime(model, t):
            if t < T:
                return model.xzn[t+1] == model.xzn[t] - model.uzndc[t] + (model.Zneff * model.uznc[t]) -model.uznsold[t]
            else:
                return Constraint.Skip
        model.znTime = Constraint(model.I, rule = znTime)

        # ensure electrical load and supply are matched
        def meetDemand(model, t):
            return model.png[t] + model.png[t] + model.ppv[t] + model.pw[t] + model.pbat[t] + model.pzn[t] + model.ploss[t] == model.Eload[t]
        model.meetDemand = Constraint(model.I, rule = meetDemand)

        # capital and fixed cost computation
        def ComputeFirstStageCost_rule(model):
            expr = model.NGGenSize * (model.NGCapEx + model.NGfom)
            expr += model.PVSize * (model.PVCapEx + model.PVfom)
            expr += model.WindSize * (model.WindCapEx + model.Windfom)
            expr += model.BatSize * (model.BatCapEx + model.Batfom)
            expr += model.ZnSize * (model.ZnCapEx + model.ZnProdfom + model.ZnLaborfom)
            expr += model.ZnStorageSize * (model.ZnStorCapEx + model.ZnStorfom)
            expr += model.FCSize * (model.FCCapEx + model.FCfom)
            return expr
        model.FirstStageCost = Expression(rule = ComputeFirstStageCost_rule)

        # variable operating cost computation
        def ComputeSecondStageCost_rule(model):
            expr = summation(model.uznc) * model.elecPriceIndustrial # electrical cost for producing refined zinc
            expr -= summation(model.uznsold) * model.refinedZincPremium # profits from selling SHG zinc as a commodity
            expr -= summation(model.uzndc) * model.PEMeff * (model.elecPriceWholesale + model.elecPricePremiumStorage) # profits from zinc oxidation/fuel cell operation
            expr += summation(model.ubatc) * (1/model.Bateff) * model.elecPriceWholesale # electrical cost for charging batteries
            #expr += summation(model.ubatdc) * model.Batvom # variable O&M for batteries
            expr -= summation(model.ubatdc) * model.Bateff * (model.elecPriceWholesale + model.elecPricePremiumStorage) # profits from selling battery power
            expr += summation(model.ploss) * model.lostLoadCost # starting price of lost load is high
            for t in model.I:
                expr += model.png[t] * (model.NGPrice[t] + model.NGvom) # natural gas fuel costs
                expr += model.uznc[t] * model.ZnOT[t] # overtime for SHG zinc production
                expr += model.uzndc[t] * model.ZnOT[t] # overtime for zinc oxidation/fuel cell operation
                expr += model.uznsold[t] * model.ZnOT[t] # restrict commodity SHG zinc sales to regular business hours
            return expr     

        model.SecondStageCost = Expression(rule = ComputeSecondStageCost_rule)

        def total_cost_rule(model):
            return (model.FirstStageCost + model.SecondStageCost)
        model.Total_Cost_Objective = Objective(rule = total_cost_rule, sense = minimize)

        # run the model
        instance = model.create_instance(inputfile) # create an initial instance of the model
        #print(instance.ZnCapEx.value, instance.ZnStorCapEx.value, instance.BatCapEx.value, instance.WindCapEx.value, instance.PVCapEx.value, instance.NGCapEx.value)

        # this version of cplex didn't work on Rebecca's computer, I don't think the community version will handle this many variables
        #opt = SolverFactory("cplex", executable = "/Applications/CPLEX_Studio_Community129/cplex/bin/x86-64_osx/cplex")
        
        # copied from previous version
        opt = SolverFactory("cplex", executable = "/Applications/CPLEX_Studio129/cplex/bin/x86-64_osx/cplex")
        # solve locally
        solver_manager = SolverManagerFactory('serial')

        # tee = True displays solver conditions from cplex
        results = solver_manager.solve(instance, opt = opt, tee = True)
        print('solved')

        # display results
        # instance.display()

        results.write(num = 1)

        # save a json file with dictionary data to make plots in a separate file
        outFile = {}
        for v in instance.component_objects(Var, active = True):
            a = []
            for index in v:
                a.append(v[index].value)
            b = {str(v): a}
            outFile.update(b)

        with open(savefile, 'w') as fp:
            json.dump(outFile, fp)
