'''
Title: Code to evaluate the Moment of Inertia metric (Dmi)*

* De Jong K.A. Morrison, R.W. Measurement of population diversity. In Artificial Evolution.
EA 2001. Lecture Notes in Computer Science, vol 2310. Springer, Berlin, Heidelberg, volume
2310, pages 1128–1134, 2002.

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["dmi", "NMDF"] # variables used in to calculate the metric
log = ["dmi"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

NMDF = 1

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_DMI"] == 1:
        return 1
    elif(parameters["MTC_DMI"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_DMI", "The Moment of Inertia metric should be 0 or 1")
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
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["dmi"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric