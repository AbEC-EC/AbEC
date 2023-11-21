'''
Title: Code to evaluate the True diversity metric (Dtd)*

* Mark Wineberg and Franz Oppacher. The underlying similarity of diversity measures used in
evolutionary computation. In Erick Cantú-Paz and Julian Miller, editors, Genetic and Evo-
lutionary Computation — GECCO 2003, pages 1493-1504, Berlin, Heidelberg, 2003. Springer
Berlin Heidelberg.

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["dtd", "NMDF"] # variables used in to calculate the metric
log = ["dtd"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

NMDF = 1

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_DTD"] == 1:
        return 1
    elif(parameters["MTC_DTD"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_DTD", "The True Diversity metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters):
    pd1 = [[] for i in range(parameters["NDIM"])]
    pd2 = [[] for i in range(parameters["NDIM"])]
    aux = 0
    for subpop in runVars.pop:
        for ind in subpop.ind:
            for d_i, d in enumerate(ind["pos"]):
                pd1[d_i].append(d)
                pd2[d_i].append(d**2)
                
    avr_pd1 = [np.average(pd1[d_i])**2 for d_i in range(parameters["NDIM"])]
    avr_pd2 = [np.average(pd2[d_i]) for d_i in range(parameters["NDIM"])]
    
    for d_i in range(parameters["NDIM"]):
        aux += avr_pd2[d_i] - avr_pd1[d_i]
    
    aux = np.sqrt(aux) / parameters["NDIM"]
    
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["dtd"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric