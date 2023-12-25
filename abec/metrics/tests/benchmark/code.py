'''
Title: Code of the benchmark presented in 


Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import importlib
import datetime
import csv
import shutil
import time
import json
import os
import analysis

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 15
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes

colors_array = list(matplotlib.colors.cnames.keys())
markers_array = list(matplotlib.markers.MarkerStyle.markers.keys())
plots = [1, 25, 50, 75, 95]
colors_array = ["red", "green", "blue", "orange", "black"]

def loadConfigFiles(pathConfig="."):
    #Read the parameters from the config file
    parametersFiles = ["config.ini"]
    parameters = {}
    for file in parametersFiles:
        if os.path.isfile(f"{pathConfig}/{file}"):
            with open(f"{pathConfig}/{file}") as f:
                p0 = list(json.loads(f.read()).items())
                for i in range(len(p0)):
                    parameters[f"{p0[i][0]}"] = p0[i][1]
        else:
            print(f"{file}", "FILE_NOT_FOUND", f"The {file} file is mandatory!")
    return parameters

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
    return path

def writeLog(mode, filename, header, data=None):
    if(mode==0):
        # Create csv file
        file = open(filename, "w")
        csvwriter = csv.DictWriter(file, fieldnames=header)
        csvwriter.writeheader()
        
    elif(mode==1):
        # Writing in csv file
        file = open(filename, "a")
        csvwriter = csv.DictWriter(file, fieldnames=header)
        csvwriter.writerows(data)
    file.close()

class optimum_point():
    def __init__(self, ndim=2, ld=[0, 100], np=100, nout=0):
        self.positions = (ld[1]- ld[0])*rng.random(size=ndim) + ld[0]
        self.position_min = [ld[0] for d in range(ndim)]
        self.position_max = [ld[1] for d in range(ndim)]
        self.decrease_rate_min = [(self.positions[d] - ld[0])*0.01 for d in range(ndim)]
        self.decrease_rate_max = [(ld[1] - self.positions[d])*0.01 for d in range(ndim)]
        
        self.pop = [[] for _ in range(np)]
        self.outliers = [[] for _ in range(nout)]
        
    def pos(self):
        return self.positions


parameters = loadConfigFiles()

# datetime variables
cDate = datetime.datetime.now()
date = {"year": cDate.year, "month": cDate.month, "day": cDate.day, "hour": cDate.hour, "minute": cDate.minute}
pathOut = checkDirs(path="experiments", date=date)

if parameters["PLOT"]:
    fig, ax = plt.subplots()

startTime = time.time()
for r in range(parameters["NRUNS"]):
    seed = parameters["SEED"]+r
    rng = np.random.default_rng(seed)
    ld = parameters["LD"]
    # create the optima points
    popsize = int(parameters["NP"]/parameters["NPEAKS"])
    optima = [optimum_point(ndim=parameters["NDIM"]
                            , ld=parameters["LD"]
                            , np=popsize
                            , nout=parameters["NOUT"]) 
                            for _ in range(parameters["NPEAKS"])]
    metrics = []
    names = []
    header = ["gen"]
    generations = []
    
    for name in parameters["METRICS_TO_TEST"]:
        names.append(name)
        names.append(f"{name}_NMDF")
        header.append(name)
        header.append(f"{name}_NMDF")
    writeLog(0, f"{pathOut}/results_{date['year']}-{date['month']}-{date['day']}-{date['hour']}-{date['minute']}_seed-{seed}_run-{r+1}.csv", header)
        
    gdms = {name: [] for name in names}

    for metric_name in parameters["METRICS_TO_TEST"]:
        metrics.append(importlib.import_module(f"metrics.{metric_name.lower()}"))
        

    for g in range(1, parameters["NGEN"]):
        # evaluate the boundaries of the space based on the optima points
        for i, optimum in enumerate(optima):
            for d in range(parameters["NDIM"]):
                optimum.position_min[d] += optimum.decrease_rate_min[d]
                optimum.position_max[d] -= optimum.decrease_rate_max[d]                   

            if(parameters["PLOT"] and g in plots):
                plt.xlim(0, 100)
                plt.ylim(0, 100)
                plt.scatter(x=optimum.pos()[0], y=optimum.pos()[1], s=2, color=colors_array[i], marker="X")
                plt.plot((optimum.position_min[0], optimum.position_min[0]), (optimum.position_min[1], optimum.position_max[1]), c=colors_array[i])
                plt.plot((optimum.position_max[0], optimum.position_max[0]), (optimum.position_min[1], optimum.position_max[1]), c=colors_array[i])
                plt.plot((optimum.position_min[0], optimum.position_max[0]), (optimum.position_min[1], optimum.position_min[1]), c=colors_array[i])
                plt.plot((optimum.position_min[0], optimum.position_max[0]), (optimum.position_max[1], optimum.position_max[1]), c=colors_array[i])
                #print(f"Dimension {d}: pos_min = {optimum.position_min[0]}, pos_max = {optimum.position_max[1]}")


        # Set the number of the population based on the outliers     
        if parameters["NOUT"] and g >= parameters["GOUT"][0]:
            NIND = popsize - parameters["NOUT"]
        else:
            NIND = popsize
            
        population = []
        # creation of the individuals
        for optimum in optima:
            for i in range(popsize):
                optimum.pop[i] = [(optimum.position_max[d] - optimum.position_min[d])*rng.random() + optimum.position_min[d] for d in range(parameters["NDIM"])]
                population.append(optimum.pop[i])
            # In specif generations, randomize the outliers
            if parameters["NOUT"] and g in parameters["GOUT"]: 
                for out in range(parameters["NOUT"]):
                    optimum.outliers[out] = [(ld[1]-ld[0])*rng.random() + ld[0] for d in range(parameters["NDIM"])]
                    population.append(optimum.outliers[out])

        # Evaluate the metrics
        for name, metric in zip(parameters["METRICS_TO_TEST"], metrics):
            gdms[name], gdms[f"{name}_NMDF"] = metric.metric(gdms[name], gdms[f"{name}_NMDF"], population, g)
            
        # Plot of the population
        if(parameters["PLOT"] and g in plots):    
            for i, optimum in enumerate(optima):
                for j in range(NIND):
                    ind = optimum.pop[j]
                    plt.scatter(x=ind[0], y=ind[1], s=10, c=colors_array[i], marker=markers_array[i])
                if parameters["NOUT"] and g >= parameters["GOUT"][0]:
                    for ind in optimum.outliers:
                        plt.scatter(x=ind[0], y=ind[1], s=10, c=colors_array[i], marker=markers_array[i])
            plt.show()
            
        generations.append(g)
    
    log = {}
    for g in generations:
        for name in parameters["METRICS_TO_TEST"]:
            log |= {"gen": g, name: gdms[name][g-1], f"{name}_NMDF": gdms[f"{name}_NMDF"][g-1]}
        writeLog(1, f"{pathOut}/results_{date['year']}-{date['month']}-{date['day']}-{date['hour']}-{date['minute']}_seed-{seed}_run-{r+1}.csv", header, data = [log]) 

executionTime = (time.time() - startTime)
avg = analysis.averageRuns(pathOut) # average the runs
analysis.plotRuns(avg, generations, pathOut) # plot the curves
shutil.copy2("config.ini", f"{pathOut}/config.ini") # copy the config file

 

