'''
Title: Code to evaluate the Maximum Exploration metric

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *
from sklearn.decomposition import PCA

params = [] # configuration parameters of the metric
vars = ["mex", "NMDF"] # variables used in to calculate the metric
log = ["mex"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_MEX"] == 1:
        return 1
    elif(parameters["MTC_MEX"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_MEX", "The Maximum Exploration metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters):
    popsize = len(runVars.pop) * len(runVars.pop[0].ind)
    minDist = [-1 for _ in range(parameters["POPSIZE"])] # Initialize the min dist as inf
    dim = [[] for _ in range(parameters["NDIM"])]
    pop = []
    
    sumD = 0
    for subpop in runVars.pop:
        for ind in subpop.ind:
            pop.append(ind)
    
    for ind1_i, ind1 in enumerate(pop):
        for ind2 in pop:
            sumD = 0
            if (ind1 == ind2):
                continue
            
            for x1, x2 in zip(ind1["pos"], ind2["pos"]):
                sumD += (x1 - x2)**2    
            d = np.sqrt(sumD) # Euclidean distance
                
            if d < minDist[ind1_i] or minDist[ind1_i] == -1:
                minDist[ind1_i] = d

    aux = sum(minDist)
    
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["mex"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric