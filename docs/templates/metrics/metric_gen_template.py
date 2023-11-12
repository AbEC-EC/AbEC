'''
Title: Code to evaluate the X metric

Author: xxx
Contact: xxx

Date: xxx
'''
import numpy as np
import pandas as pd
import sys
from aux.aux import *

params = [] # configuration parameters of the metric
vars = ["metricX", "var1"] # variables used in to calculate the metric
log = [] # variable to be recorded on the log file
scope = ["IND"] # scope of the metric {IND, GEN, RUN}

# check if the params of the metric is set up correctly
def cp(parameters):
    # code ...
    return 1

# calculate the metric
def metric(ind, pop, var_metric, parameters):
    # code ...
    return var_metric

# do the final calculations in the end of the run
def finishMetric(file):
    # code ...
    return file
