'''
Title: Code to evaluate the current error metric

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2 
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["ec"] # variables used in to calculate the metric
log = ["ec"] # variables to be written in the log
scope = ["IND"] # scope of the metric {IND, GEN, RUN}

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_EC"] == 1:
        return 1
    elif(parameters["MTC_EC"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_EC", "The Current Error metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters, ind = 0):
    var_metric["ec"] = runVars.best["fit"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, path):
    return var_metric


