import csv
import os
import datetime
import globalVar

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
    config = {
        "__COMMENT__": "BASIC CONFIGURATION", \
        "ALGORITHM": "PSO", \
        "POPSIZE": 50, \
        "MIN_POS": -10, \
        "MAX_POS": 10, \
        "__COMMENT__": "OPTIMIZER CONFIGURATION", \
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

