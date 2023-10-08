import csv
import os
import numpy as np
import shutil
import pandas as pd
import importlib
import sys
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join

'''
Check if a dir existis and if not, create it
'''
def checkCreateDir(path):
    if(os.path.isdir(path) == False):
        os.mkdir(path)
'''
Check if the dirs already exist, and if not, create them
Returns the path
'''
def checkDirs(path, date):
    # check if the dir exisits, if so, delete and recreate
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{date['year']}-{date['month']:02d}-{date['day']:02d}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    path += f"/{date['hour']:02d}-{date['minute']:02d}"
    if(os.path.isdir(path) == False):
        os.mkdir(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)
    pathTmp = path+"/results"
    if(os.path.isdir(pathTmp) == False):
        os.mkdir(pathTmp)
    return path

def myPrint(string, file, parameters):
    if parameters["TERMINAL_OUTPUT"]:
        print(string)
    file.write(f"{string}\n")

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
def saveOptima(runVars, parameters):
    opt = []
    if(parameters["BENCHMARK"] == "MPB"):
        #print(globalVar.mpb.maximums())
        #opt = [0 for _ in range(parameters["NPEAKS_MPB"])]
        for i in range(len(runVars.mpb.maximums())):
            #print(i)
            opt.append(runVars.mpb.maximums()[i])
    #elif(parameters["BENCHMARK"] == "H1"):
        #opt.append(fitFunction([8.6998, 6.7665])[0])
    with open(f"{runVars.filename_OPT}", "a") as f:
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


def ecMean(path, parameters):
    ec_mean = []
    ec_std = []
    sum = 0
    data = []

    # get the run data files of each run in the dirs
    flist = os.listdir(path)
    flist = sorted(flist)[:parameters["RUNS"]]
    flist = [f"{path}/{d}" for d in flist]
    files = [f"{pdir}/{sorted(os.listdir(pdir))[-1]}" for pdir in flist]
    

    for f in files:
        data.append(pd.read_csv(f))
    std = [0 for i in range(len(data))]

    for row in range(len(data[0].index)):
        for file in range(len(data)):
            sum += data[file]["ec"][row]
            std[file] = data[file]["ec"][row]
        ec_mean.append(sum/len(data))
        ec_std.append(np.std(std))
        sum = 0
        std = [0 for _ in range(len(data))]

    zipped = list(zip(data[0]["nevals"], ec_mean, ec_std))
    bestMean = pd.DataFrame(zipped, columns=["nevals", "ec", "ec_std"])
    bestMean.to_csv(f"{path}/ecMean.csv")

    return f"{path}/ecMean.csv"


def eoMean(path, parameters):
    eo_mean = []
    eo_std = []
    sum = 0
    data = []
    
    # get the run data files of each run in the dirs
    flist = os.listdir(path)
    flist = sorted(flist)[:parameters["RUNS"]]
    flist = [f"{path}/{d}" for d in flist]
    files = [f"{pdir}/{sorted(os.listdir(pdir))[-1]}" for pdir in flist]

    for f in files:
        data.append(pd.read_csv(f))
    std = [0 for i in range(len(data))]

    for row in range(len(data[0].index)):
        for file in range(len(data)):
            sum += data[file]["eo"][row]
            std[file] = data[file]["eo"][row]
        eo_mean.append(sum/len(data))
        eo_std.append(np.std(std))
        sum = 0
        std = [0 for _ in range(len(data))]

    zipped = list(zip(data[0]["nevals"], eo_mean, eo_std))
    bestMean = pd.DataFrame(zipped, columns=["nevals", "eo", "eo_std"])
    bestMean.to_csv(f"{path}/eoMean.csv")

    return f"{path}/eoMean.csv"


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
        "RUNS": 3, \
        "FINISH_RUN_MODE": 0, \
        "FINISH_RUN_MODE_VALUE": 2000, \
        "SEED": 42, \
        "ANALISYS" : 1, \
        "CONFIG_COPY": 1, \
        "OFFLINE_ERROR": 1, \
        "BEBC_ERROR": 0, \
        "PATH": "../experiments", \
        "LOG_ALL": 0, \
        "PARALLELIZATION": 1, \
        "PROCESS": 2, \
        "TERMINAL_OUTPUT": 0, \
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
        "CHANGES_NEVALS": [2000, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 85000, 90000, 95000, 100000, 105000, 110000, 115000, 120000, 125000, 130000, 135000, 140000, 145000, 150000, 155000, 160000, 165000, 170000, 175000, 180000, 185000, 190000, 195000, 200000, 205000, 210000, 215000, 220000, 225000, 230000, 235000, 240000, 245000, 250000, 255000, 260000, 265000, 270000, 275000, 280000, 285000, 290000, 295000, 300000, 305000, 310000, 315000, 320000, 325000, 330000, 335000, 340000, 345000, 350000, 355000, 360000, 365000, 370000, 375000, 380000, 385000, 390000, 395000, 400000, 405000, 410000, 415000, 420000, 425000, 430000, 435000, 440000, 445000, 450000, 455000, 460000, 465000, 470000, 475000, 480000, 485000, 490000, 495000],  \
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