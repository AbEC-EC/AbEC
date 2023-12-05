'''
Title: Code to evaluate the Variance Average Chromosomes metric (Dvac)*

* Francisco Herrera, E Herrera-Viedma, Manuel Lozano, and Jose Luis Verdegay. Fuzzy tools to
improve genetic algorithms. In Second European Congress on Intelligent Techniques and Soft
Computing, volume 3, pages 1532–1539, 1994

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["dvac", "NMDF"] # variables used in to calculate the metric
log = ["dvac"] # variable to be recorded on the log file
scope = ["GEN"] # scope of the metric, GEN

NMDF = 1

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_DVAC"] == 1:
        return 1
    elif(parameters["MTC_DVAC"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_DVAC", "The Variance Average Chromosomes metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters):
    pd1 = []
    pop = []
    aux = 0
    
    # If there are more subpopulations, put all the individuals in the same list (pop)
    for subpop in runVars.pop:
        for ind in subpop.ind:
            pop.append(ind)
    popsize = len(pop)
    
    # Append the value of the dimensions in a list
    for ind in pop:
        for d in ind["pos"]:
            pd1.append(d)
                
    # Average the values of all dimensions
    avr_pd1 = np.average(pd1)
    pd1 = []
    
    # For each individual, sum the difference between the average of its dimensions values
    # and the average of all dimensions. Normalize with the population size
    for ind in pop:
        for d in ind["pos"]:
            pd1.append(d)
        aux += (np.average(pd1) - avr_pd1)**2
            
    aux = aux / popsize
        
    # Normalize
    if(runVars.gen == 1 or aux > var_metric["NMDF"]):
        var_metric["NMDF"] = aux
    var_metric["dvac"] = aux / var_metric["NMDF"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, file):
    return var_metric