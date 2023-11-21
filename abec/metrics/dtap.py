'''
Title: Code to evaluate the Distance to Average Point metric (Ddtap)*

* Hussein A Abbass and Kalyanmoy Deb. Searching under multi-evolutionary pressures. In
International conference on evolutionary multi-criterion optimization, pages 391-404. Springer,
2003.

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["dtap", "NMDF"] # variables used in to calculate the metric
log = ["dtap"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

NMDF = 1

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_DTAP"] == 1:
        return 1
    elif(parameters["MTC_DTAP"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_DTAP", "The Distance to Average Point metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters):
    pd1 = [[] for i in range(parameters["NDIM"])]
    aux = 0
    for subpop in runVars.pop:
        for ind in subpop.ind:
            for d_i, d in enumerate(ind["pos"]):
                pd1[d_i].append(d)
                
    avr_pd1 = [np.average(pd1[d_i]) for d_i in range(parameters["NDIM"])]
    
    for subpop in runVars.pop:
        for ind in subpop.ind:
            for d_i, d in enumerate(ind["pos"]):
                aux += (d - avr_pd1[d_i])**2
    
    popsize = len(runVars.pop) * len(runVars.pop[0].ind)
    aux = np.sqrt(aux) / popsize
        
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["dtap"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric