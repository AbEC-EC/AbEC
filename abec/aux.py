import csv
import os
import datetime
import globalVar
import importlib
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
    opt = [0]
    if(parameters["BENCHMARK"] == "MPB"):
        opt = [0 for _ in range(parameters["NPEAKS_MPB"])]
        for i in range(parameters["NPEAKS_MPB"]):
            opt[i] = globalVar.mpb.maximums()[i]
    elif(parameters["BENCHMARK"] == "H1"):
        opt[0] = fitFunction([8.6998, 6.7665])[0]
    with open(f"{globalVar.path}/optima.csv", "a") as f:
        write = csv.writer(f)
        write.writerow(opt)



'''
Default parametrization for algoConfig.ini
'''
def algoConfig():
    components = [f for f in listdir("components") if isfile(join("components", f))]
    optimizers = [f for f in listdir("optimizers") if isfile(join("optimizers", f))]
    comp_parameters = []
    opt_parameters = []

    config = {
        "__COMMENT__": "BASIC CONFIGURATION", \
        "ALGORITHM": "", \
        "POPSIZE": 0, \
        "MIN_POS": 0, \
        "MAX_POS": 0, \
    }
    print(config)
    print(optimizers)
    print(components)

    # Load the optimizers
    for i in range(len(optimizers)):
        optimizers[i] = optimizers[i].split(".")[0]
        opt_parameters.append(importlib.import_module(f"optimizers.{optimizers[i]}"))
        optimizers[i] = optimizers[i].upper()
        print(optimizers[i])
        config.update({f"{optimizers[i]}_POP_PERC": 0})
        for j in range(len(opt_parameters[i].params)):
            #print(opt_parameters[i].params[j])
            config.update({f"{optimizers[i]}_{opt_parameters[i].params[j]}": 0})
        #print()

    # Load the components
    for i in range(len(components)):
        components[i] = components[i].split(".")[0]
        comp_parameters.append(importlib.import_module(f"components.{components[i]}"))
        components[i] = components[i].upper()
        print(components[i])
        config.update({f"COMP_{components[i]}": 0})
        for j in range(len(comp_parameters[i].params)):
            #print(comp_parameters[i].params[j])
            config.update({f"COMP_{components[i]}_{comp_parameters[i].params[j]}": 0})
        #print()

    #print(config)
    #e()

    '''
        "GA_POP_PERC": 0, \
        "GA_ELI_PERC": 0.2, \
        "GA_CROSS_PERC": 1, \
        "GA_MUT_PERC": 0.1, \
        "GA_MUT_STD": 1, \
        "GA_ENCODER": 0, \
        "GA_INDSIZE": 16, \
        "PSO_POP_PERC": 1, \
        "PSO_PHI1": 2.05, \
        "PSO_PHI2": 2.05, \
        "PSO_W": 0.729, \
        "PSO_MIN_VEL": -10, \
        "PSO_MAX_VEL": 10, \
        "DE_POP_PERC": 0, \
        "DE_F": 0.5, \
        "DE_CR": 0.7, \
        "ES_POP_PERC": 0, \
        "ES_RCLOUD": 0.2, \
        "__COMMENT__": "COMPONENTS CONFIGURATION", \
    }
        f"COMP_{components[0]}": 0, \
        "COMP_CHANGE_DETECT": 0, \
        "COMP_CHANGE_DETECT_MODE": 0, \
        "COMP_MULTIPOP": 0, \
        "COMP_MULTIPOP_N": 10, \
        "COMP_MUT": 0, \
        "COMP_MUT_PERC": 0.05, \
        "COMP_MUT_ELI": 0.5, \
        "COMP_MUT_STD": 0.1, \
        "COMP_EXCLUSION": 0, \
        "COMP_EXCLUSION_REXCL": 22.9, \
        "COMP_ANTI_CONVERGENCE": 0, \
        "COMP_ANTI_CONVERGENCE_RCONV": 39.7, \
        "COMP_LOCAL_SEARCH": 0, \
        "COMP_LOCAL_SEARCH_ETRY": 20, \
        "COMP_LOCAL_SEARCH_RLS": 1 \
    }
    '''
    return config

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

