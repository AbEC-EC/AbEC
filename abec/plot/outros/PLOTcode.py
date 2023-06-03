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
from deap import base
from deap import benchmarks
from deap import creator
from deap import tools
from deap.benchmarks import movingpeaks
from deap import creator
from deap import tools

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

colors = ["r", "b", "#afafaf", "#820e57", "orange", "yellow"]

def configPlot(parameters):
    THEME = parameters["THEME"]
    plt.rcParams["figure.figsize"] = (16, 9)
    if(THEME == 1):
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "cornsilk"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
    elif(THEME == 2):
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
    elif(THEME == 3):
        plt.rcParams["axes.facecolor"] = "white"

    fig, ax = plt.subplots(1)
    if(parameters["GRID"] == 1):
        ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
    else:
        ax.grid(False)
    return fig, ax



def plot(ax, data, label, fStd=0, color="orange", parameters=False):
    ax.plot(data["nevals"], data["bestError"], color=color, label=label)
    if(fStd):
        ax.fill_between(data["nevals"], data["bestError"] - data["std"], data["bestError"] + data["std"], color="dark"+color, alpha=0.3)
    ax.set_xlabel("N Evaluations", fontsize=15)
    ax.set_ylabel("Error", fontsize=15)
    if(parameters["YLIM"]):
        ax.set_ylim(bottom=parameters["YLIM"][0], top=parameters["YLIM"][1])
    else:
        ax.set_ylim(bottom=0, top=0.1)
    ax.set_xlim(1, data["nevals"].iloc[-1])
    #plt.xscale("log")
    return ax




def showPlots(fig, ax, parameters, parameters2):
    path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}/{sys.argv[2]}"
    THEME = parameters["THEME"]
    plt.legend()
    for text in plt.legend().get_texts():
        if(THEME == 1):
            text.set_color("black")
        elif(THEME == 2):
            text.set_color("white")
        text.set_fontsize(18)
    title = parameters["TITLE"]
    if(parameters["TITLE"] == 0):
        title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']} \n\n \
                POPSIZE: {parameters2['POPSIZE']}   \
                M{parameters2['NSWARMS']}\
                ES{parameters2['ES_PARTICLE_OP']}\
                EX{parameters2['EXCLUSION_OP']}\
                AC{parameters2['ANTI_CONVERGENCE_OP']}\
                "
    ax.set_title(title, fontsize=20)
    plt.savefig(f"{path}/{parameters['NAME']}", format="png")
    plt.show()



def mean(data):
    bMean = [0 for i in range( len(data[0]["bestError"]) )]
    bStd = [0 for i in range( len(data[0]["bestError"]) )]
    std = [0 for i in range( len(data) )]
    sum = 0

    for i in range (len(data[0]["bestError"])):
        for j in range(len(data)):
            sum += data[j]["bestError"][i]
            std[j] = data[j]["bestError"][i]
        bMean[i] = sum/len(data)
        bStd[i] = np.std(std)
        sum = 0
        std = [0 for i in range( len(data) )]

    zipped = list(zip(data[0]["nevals"], bMean, bStd))
    bestMean = pd.DataFrame(zipped, columns=["nevals", "bestError", "std"])
    return bestMean



def main():
    # reading the parameters from the config file
    with open("./config.ini") as f:
        parameters = json.loads(f.read())
    debug = parameters["DEBUG"]
    if(debug):
        print("Parameters:")
        print(parameters)

    path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}/{sys.argv[2]}"
    df = pd.read_csv(f"{path}/data.csv")

    with open(f"{path}/config.ini") as f:
        parameters2 = json.loads(f.read())

    THEME = parameters["THEME"]

    fig, ax = configPlot(parameters)

    print( len(pd.unique(df["run"])) )
    data = [[] for i in range( len(pd.unique(df["run"])) )]
    for i in range(len(pd.unique(df["run"])) ):
        data[i] = df[df["run"] == i+1]
        data[i] = data[i].drop_duplicates(subset=["gen"], keep="last")[["gen", "nevals", "bestError", "env"]]
        data[i].reset_index(inplace=True)
        if(parameters["ALLRUNS"]):
            ax = plot(ax, data=data[i], label=f"Run {i+1}", color=colors[i], parameters=parameters)

    bestMean = mean(data)
    ax = plot(ax, data=bestMean, label="Mean", color="green", fStd=1, parameters=parameters)


    if(parameters2["RANDOM_CHANGES"]):
        changesEnv = parameters2["CHANGES_NEVALS"]
    else:
        changesEnv = parameters2["CHANGES_NEVALS"]
    #changesEnv = data[0].ne(data[0].shift()).filter(like="env").apply(lambda x: x.index[x].tolist())["env"][1:]
    for i in changesEnv:
        plt.axvline(int(i), color="black", linestyle="--")
    showPlots(fig, ax, parameters, parameters2)


if __name__ == "__main__":
    main()
