'''
Title: Code to evaluate the X metric

Author: xxx
Contact: xxx

Date: xxx
'''
import numpy as np
import pandas as pd


vars = ["VAR1"] # variables used in to calculate the metric
scope = ["IND"] # scope of the metric {IND, GEN, RUN}
params = [] # configuration parameters of the metric

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
