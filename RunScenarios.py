# Run the scenarios
import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory
import json
import random

import SystemModel

# run baseline models with different renewable energy minimum requirements
# inputs to SystemBiLevelModel are: name for instance of the class; scenario .dat file; output name of.json file to save data to; minimum % of electricity which must come from renewables
# running 7 scenarios takes ~10 minutes, comment out scenarios if you don't want to rerun them 


# run midpoint cost baseline

#RC 1/14/20 we have different folders, I put the 'baseline20.json' file in 'Cost_Baselines', but I haven't fixed the rest of the code
s = SystemModel.SystemBilevelModel('b1', 'Cost_Baselines/BaselineScenario.dat', 'Cost_Baselines/Baseline20.json', 0.2)
s.makeSolveAbstractModel()
#s = SystemModel.SystemBilevelModel('b2', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline50.json', 0.5)
#s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b3', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline70.json', 0.7)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b4', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline80.json', 0.8)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b5', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline90.json', 0.9)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b6', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline95.json', 0.95)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b7', 'Cost_Baselines/BaselineScenario.dat', 'json_Files/Baseline99.json', 0.99)
# s.makeSolveAbstractModel()


# # run low cost baseline

# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low20.json', 0.20)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low50.json', 0.50)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low70.json', 0.70)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low80.json', 0.80)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low90.json', 0.90)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low95.json', 0.95)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/LowBaselineScenario.dat', 'json_Files/Low99.json', 0.99)
# s.makeSolveAbstractModel()


# # run high cost baseline

# s = SystemModel.SystemBilevelModel('b9', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High20.json', 0.20)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High50.json', 0.50)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High70.json', 0.70)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High80.json', 0.80)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High90.json', 0.90)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High95.json', 0.95)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b8', 'Cost_Baselines/HighBaselineScenario.dat', 'json_Files/High99.json', 0.99)
# s.makeSolveAbstractModel()


# # run high wind cost, low natural gas cost baseline

# s = SystemModel.SystemBilevelModel('b10', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW20.json', 0.20)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b11', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW50.json', 0.50)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b12', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW70.json', 0.70)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b13', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW80.json', 0.80)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b14', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW90.json', 0.90)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b15', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW95.json', 0.95)
# s.makeSolveAbstractModel()
# s = SystemModel.SystemBilevelModel('b16', 'Cost_Baselines/LowGasHighWindBaselineScenario.dat', 'json_Files/LGHW99.json', 0.99)
# s.makeSolveAbstractModel()



