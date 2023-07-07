import csv
import os
import datetime
import aux.globalVar as globalVar
import importlib
import sys
from os import listdir
from os.path import isfile, join

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

'''
Check if the dirs already exist, and if not, create them
Returns the path
'''
def checkDirs(path):
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{year}-{month}-{day}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{hour}-{minute}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    return path

def errorWarning(nError="0.0", file="NONE", parameter="NONE", text="NONE"):
    '''
        Print error function
    '''
    print(f"[ERROR][{nError}]")
    print(f"--[File: '{file}']")
    print(f"--[parameter: '{parameter}']")
    print(f"----[{text}]")
    sys.exit()



'''
Write the log of the algorithm over the generations on a csv file
'''
def writeLog(mode, filename, header, data=None):
    if(mode==0):
        # Create csv file
        with open(filename, "w") as file:
            csvwriter = csv.DictWriter(file, fieldnames=header)
            csvwriter.writeheader()
    elif(mode==1):
        # Writing in csv file
        with open(filename, mode="a") as file:
            csvwriter = csv.DictWriter(file, fieldnames=header)
            csvwriter.writerows(data)
           # for i in range(len(data)):
           #     csvwriter.writerows(data[i])


'''
Write the position and fitness of the peaks on
the 'optima.csv' file. The number of the peaks will be
NPEAKS_MPB*NCHANGES
'''
def saveOptima(parameters):
    opt = []
    if(parameters["BENCHMARK"] == "MPB"):
        #opt = [0 for _ in range(parameters["NPEAKS_MPB"])]
        for i in range(len(globalVar.mpb.maximums())):
            print(i)
            opt.append(globalVar.mpb.maximums()[i])
    elif(parameters["BENCHMARK"] == "H1"):
        opt.append(fitFunction([8.6998, 6.7665])[0])
    with open(f"{globalVar.path}/optima.csv", "a") as f:
        write = csv.writer(f)
        write.writerow(opt)


'''
Create the class of the algorithm
'''
class algoritmo():

    def __init__(self):
        self.opts = []
        self.comps_global = {"GDV": [], "GER": [], "GET": []}
        self.comps_local = {"LER": [], "LET": []}
        self.comps_initialization = []
        self.components = []
        self.optimizers = []

    def updateOptimizers(self, x):
        self.opts.append(x)

    def removeOptimizers(self, x):
        self.opts.remove(x)

    def updateInitialization(self, x):
        self.comps_initialization.append(x)

    def removeInitialization(self, x):
        self.comps_initialization.remove(x)

    def updateLocal(self, x, scope):
        self.comps_local[scope].append(x)

    def removeComps_local(self, x):
        self.comps_local[x.scope[0]].remove(x)

    def updateGlobal(self, x, scope):
        self.comps_global[scope].append(x)

    def removeComps_global(self, x):
        self.comps_global[x.scope[0]].remove(x)




'''
Update algo with the parameters
'''
def updateAlgo(algo, parameters):
    components = [f for f in listdir("components") if isfile(join("components", f))]
    optimizers = [f for f in listdir("optimizers") if isfile(join("optimizers", f))]
    comp_parameters = []
    opt_parameters = []
    algo.optimizers = [[] for _ in range (len(optimizers))]
    algo.components = [[] for _ in range (len(components))]
    validation = 0
    # Load the optimizers
    id = 0
    for i in range(len(optimizers)):
        optimizers[i] = optimizers[i].split(".")[0].upper()
        arg = f"{optimizers[i]}_POP_PERC"
        opt = importlib.import_module(f"optimizers.{optimizers[i].lower()}")
        if 0 < parameters[arg] <= 1:
            if parameters[arg]*parameters["POPSIZE"] > 3:
                opt.cp(parameters)    # Call the test of the parameters values
                validation += parameters[arg]
                algo.optimizers[id].append(optimizers[i])
                algo.optimizers[id].append(opt)
                id += 1
            else:
                errorWarning("0.2.0", "algoConfig.ini", f"{parameters[arg]}_POP_PERC", "Number of individuals of each optimizer should be greater than 3")
                sys.exit()
        elif(parameters[arg] != 0):
            errorWarning("0.2.1", "algoConfig.ini", f"{parameters[arg]}_POP_PERC", "Percentage of the population to perform optimizer should be in [0, 1]")
            sys.exit()
        else:
            algo.removeOptimizers(opt)


    if (abs(validation-1) > 0.001):
        errorWarning(0.0, "algoConfig.ini", "XXX_POP_PERC", "The sum of the percentage of the population to perform the optimizers should be in 1")
        sys.exit()

    id = 0
    for i in range(len(components)):
        components[i] = components[i].split(".")[0].upper()
        arg = f"COMP_{components[i]}"
        comp = importlib.import_module(f"components.{components[i].lower()}")
        if parameters[arg] == 0:
            if comp.scope[0] == "INI":
                algo.removeInitialization(comp)
            elif comp.scope[0] == "GDV" or comp.scope[0] == "GER" or comp.scope[0] == "GET":
                algo.removeComps_global(comp)
            elif comp.scope[0] == "LER" or comp.scope[0] == "LET":
                algo.removeComps_local(comp)
        elif(parameters[arg] != 1):
            errorWarning("0.2.1", "algoConfig.ini", f"{arg}", "Component selection should be 0 or 1")
            sys.exit()
        else:
            comp.cp(parameters)
            algo.components[id].append(components[i])
            algo.components[id].append(comp)
            id += 1

    algo.optimizers = [x for x in algo.optimizers if x] # Remove the empty lists
    algo.components = [x for x in algo.components if x]

    return algo


'''
Default parametrization for algoConfig.ini
'''
def algoConfig():
    components = [f for f in listdir("components") if isfile(join("components", f))]
    optimizers = [f for f in listdir("optimizers") if isfile(join("optimizers", f))]
    comp_parameters = []
    opt_parameters = []

    algo = algoritmo()

    config = {
        "__COMMENT__": "BASIC CONFIGURATION", \
        "ALGORITHM": "", \
        "POPSIZE": 0, \
        "MIN_POS": 0, \
        "MAX_POS": 0, \
    }

    # Load the optimizers
    for i in range(len(optimizers)):
        optimizers[i] = optimizers[i].split(".")[0]
        opt_parameters.append(importlib.import_module(f"optimizers.{optimizers[i]}"))
        algo.updateOptimizers(opt_parameters[i])
        optimizers[i] = optimizers[i].upper()
        config.update({f"{optimizers[i]}_POP_PERC": 0})
        for j in range(len(opt_parameters[i].params)):
            config.update({f"{optimizers[i]}_{opt_parameters[i].params[j]}": 0})

    # Load the components
    for i in range(len(components)):
        components[i] = components[i].split(".")[0]
        comp_parameters.append(importlib.import_module(f"components.{components[i]}"))
        if comp_parameters[i].scope[0] == "INI":
            algo.updateInitialization(comp_parameters[i])
        elif comp_parameters[i].scope[0] == "GDV":
            algo.updateGlobal(comp_parameters[i], "GDV")
        elif comp_parameters[i].scope[0] == "GER":
            algo.updateGlobal(comp_parameters[i], "GER")
        elif comp_parameters[i].scope[0] == "GET":
            algo.updateGlobal(comp_parameters[i], "GET")
        elif comp_parameters[i].scope[0] == "LER":
            algo.updateLocal(comp_parameters[i], "LER")
        else:
            print("ERRO")

        components[i] = components[i].upper()
        config.update({f"COMP_{components[i]}": 0})
        for j in range(len(comp_parameters[i].params)):
            config.update({f"COMP_{components[i]}_{comp_parameters[i].params[j]}": 0})

    return config, algo

'''
Default parametrization for frameConfig.ini
'''
def frameConfig():
    config = {
        "__COMMENT__": "FRAMEWORK CONFIGURATION", \
        "RUNS": 5, \
        "FINISH_RUN_MODE": 0, \
        "FINISH_RUN_MODE_VALUE": 1000, \
        "SEED": 42, \
        "PLOT" : 0, \
        "CONFIG_COPY": 1, \
        "OFFLINE_ERROR": 0, \
        "BEBC_ERROR": 0, \
        "PATH": "../examples", \
        "FILENAME": "data.csv", \
        "LOG_ALL": 0, \
        "DEBUG_RUN": 1, \
        "DEBUG_RUN_2": 0, \
        "DEBUG_GEN": 0, \
        "DEBUG_POP": 0, \
        "DEBUG_IND": 0 \
    }
    return config


'''
Default parametrization for problemConfig.ini
'''
def problemConfig():
    config = {
        "__COMMENT__": "PROBLEM CONFIGURATION", \
        "BENCHMARK": "H1", \
        "FUNCTION": "NONE" , \
        "NDIM": 2, \
        "CHANGES": 0, \
        "CHANGES_NEVALS": [5000, 10000, 15000], \
        "SCENARIO_MPB": 2, \
        "NPEAKS_MPB": 10, \
        "UNIFORM_HEIGHT_MPB": 0, \
        "MOVE_SEVERITY_MPB": 1, \
        "MIN_HEIGHT_MPB": 30, \
        "MAX_HEIGHT_MPB": 70, \
        "MIN_WIDTH_MPB": 1, \
        "MAX_WIDTH_MPB": 12, \
        "MIN_COORD_MPB": 0, \
        "MAX_COORD_MPB": 100, \
        "LAMBDA_MPB": 0 \
    }
    return config

