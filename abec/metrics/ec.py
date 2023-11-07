'''
Title: Code to evaluate the current error metric

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2 
'''
import numpy as np
import pandas as pd

vars = ["ec"] # variables used in to calculate the metric
log = ["ec"] # variables to be written in the log
scope = ["IND"] # scope of the metric {IND, GEN, RUN}
params = [] # configuration parameters of the metric

# check if the params of the metric is set up correctly
def cp(parameters):
    # code ...
    return 1

# calculate the metric
def metric(var_metric, runVars, parameters, ind = 0):
    var_metric["ec"] = runVars.best["fit"]
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, path):
    return var_metric
