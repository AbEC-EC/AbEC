'''
Title: Code to evaluate the Pairwise Distances metric (Dpw)*

* A.L. Barker and W.N. Martin. Dynamics of a distance-based population diversity measure. In
Proceedings of the 2000 Congress on Evolutionary Computation. CEC00 (Cat. No.00TH8512),
volume 2, pages 1002–1009 vol.2, 2000

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["dpw", "NMDF"] # variables used in to calculate the metric
log = ["dpw"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

NMDF = 1

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_DPW"] == 1:
        return 1
    elif(parameters["MTC_DPW"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_DPW", "The Pairwise Distances metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters):
    pop = []
    aux = 0
    aux2 = 0
    
    # If there are more subpopulations, put all the individuals in the same list (pop)
    for subpop in runVars.pop:
        for ind in subpop.ind:
            pop.append(ind)
    popsize = len(pop)

    # Caclulate the difference euclidean distance between the individuals
    # and normalize with the population size
    for ind1_i, ind1 in enumerate(pop):
        for ind2 in pop[:ind1_i-1]:
            for d1, d2 in zip(ind1["pos"], ind2["pos"]):
                aux += (d1-d2)**2
            aux2 += np.sqrt(aux)
            aux = 0
    
    aux = 2*(aux2)/(popsize-1)
    aux = aux / popsize
        
    # Normalize
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["dpw"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric