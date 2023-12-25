'''
Title: Code of the benchmark presented in 


Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import importlib
import datetime
import csv
import shutil
import json
import os
from os import listdir
from os.path import isfile, join

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 15
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes

colors_array = list(matplotlib.colors.cnames.keys())
markers_array = list(matplotlib.markers.MarkerStyle.markers.keys())
colors_array = ["red", "green", "blue", "orange", "black"]

def loadConfigFiles(pathConfig="."):
    #Read the parameters from the config file
    parametersFiles = ["config.ini"]
    parameters = {}
    for file in parametersFiles:
        if os.path.isfile(f"{pathConfig}/{file}"):
            with open(f"{pathConfig}/{file}") as f:
                p0 = list(json.loads(f.read()).items())
                for i in range(len(p0)):
                    parameters[f"{p0[i][0]}"] = p0[i][1]
        else:
            print(f"{file}", "FILE_NOT_FOUND", f"The {file} file is mandatory!")
    return parameters

parameters = loadConfigFiles()

metrics = {metric: [] for metric in parameters["METRICS_TO_TEST"]}
def averageRuns(path):
    avg = {}
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        df = pd.read_csv(f"{path}/{file}")
        for metric in parameters["METRICS_TO_TEST"]:
            metrics[metric].append(df[metric].values)
    
    for metric in parameters["METRICS_TO_TEST"]:
        avg[metric] = np.mean(metrics[metric], axis=0)
        avg[f"{metric}_std"] = np.std(metrics[metric], axis=0)

    with open(f"{path}/results_average.csv", 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(avg.keys())
        csv_writer.writerows(zip(*avg.values()))

    return avg    
        
def plotRuns(metrics, generations, path):
    fig, ax = plt.subplots()
    for i, metric in enumerate(parameters["METRICS_TO_TEST"]):
        plt.plot(generations, metrics[metric], label=f"{metric}", marker=markers_array[i])
        ax.fill_between(generations, metrics[metric] - metrics[f"{metric}_std"], metrics[metric] + metrics[f"{metric}_std"], alpha=0.1)

    plt.xlim(0, parameters["NGEN"])
    #plt.ylim(0, 1)
    plt.xlabel("Generations")
    plt.ylabel("Metric value")
    plt.grid(1)
    plt.legend(loc='best')
    plt.savefig(f"{path}/metrics_comparison_graph.png")
    plt.show()
