'''
Code to plot graph using data file

Alexandre Mascarenhas
'''
import json
import shutil
import itertools
import operator
import random
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import datetime
import os
import csv
import sys
import time
import getopt


vars = ["bbc"]
params = []
scope = ["GEN"]

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

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute


def writeTXT(data, name, path, std):
    if(std):
        line = f"{data[0]:.5f}\t{data[1]:.5f}"
    else:
        line = f"{data:.5f}"
    f = open(f"{path}/{name}.txt","w")
    f.write(line)
    f.close()


def bestErrorBeforeChange(path, std=1):
    df = pd.read_csv(f"{path}/data.csv")
    data = [[] for i in range( len(pd.unique(df["run"])) )]
    for i in range(len(pd.unique(df["run"])) ): # Get the number of runs
        data[i] = df[df["run"] == i+1]
        data[i] = data[i].drop_duplicates(subset=["env"], keep="last")[["gen", "nevals", "bestError", "env"]]
        data[i].reset_index(inplace=True)
        del data[i]["index"]
        #data[i].to_csv(f"{path}/run{i+1}.csv", index = True)

    NCHANGES = len(data[0]["env"])
    NRUNS = len(data)
    luffy = [0 for _ in range(NRUNS)]

    for j in range(NRUNS):
        luffy[j] = np.sum(data[j]['bestError'])/NCHANGES

    bobc = [np.mean(luffy), np.std(luffy)]
    if(std):
        return bobc
    else:
        return bobc[0]


def main():
    startTime = time.time()
    arg_help = "{0} -p <path>".format(sys.argv[0])
    path = "."
    debug = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:d:", ["help", "path=", "debug="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-d", "--debug"):
            debug = arg

    with open(f"{sys.path[0]}/config.ini") as f:
        parameters = json.loads(f.read())

    # Evaluate the offline error
    Eb = bestErrorBeforeChange(path, std = parameters["STD_Eb"])
    writeTXT(Eb, "bebc", path, std = parameters["STD_Eb"])
    if(parameters["DEBUG"] and debug):
        if(parameters["STD_Eb"]):
            print(f"\n[Best error before change]: {Eb[0]:.5f}({Eb[1]:.5f})")
        else:
            print(f"\n[Best error before change]: {Eb:.5f}")

    executionTime = (time.time() - startTime)
    if(parameters["DEBUG"] and debug):
        print(f"File generated: {path}/bebc.txt")
        print(f'Time Exec: {str(executionTime)} s')



if __name__ == "__main__":
    main()
