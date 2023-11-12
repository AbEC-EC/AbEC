'''
Title: Code to evaluate the offline error metric

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2 
'''

import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = []
vars = ["eo", "eo_sum", "eo_std"]
log = ["eo", "eo_std"]
scope = ["IND"]

# check if the params of the metric is set up correctly
def cp(parameters):
    if parameters["MTC_EO"] == 1:
        return 1
    elif(parameters["MTC_EO"] != 0):
        errorWarning("3.2.2", "algoConfig.ini", "MTC_EO", "The Current Error metric should be 0 or 1")
        sys.exit()

# calculate the metric
def metric(var_metric, runVars, parameters, ind = 0):
    var_metric["eo_sum"] += runVars.best["fit"]
    var_metric["eo"] = var_metric["eo_sum"]/runVars.nevals
    return var_metric

# do the final calculations in the end of the run
def finishMetric(var_metric, path):
    df = pd.read_csv(path)
    eo = [np.mean(df["eo"]), np.std(df["eo"])]
    var_metric["eo"] = eo[0]
    var_metric["eo_std"] = eo[1]
    return var_metric
