'''
Code to plot graph using data file

Alexandre Mascarenhas

2023/1
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
import getopt

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

colors = ["#afafaf", "#820e57", "orange", "red", "green", "blue", "yellow"]
lineStyles = ["dashdot", "dotted", "dashed", ":", "solid"]
markers = [".", "x", "^"]

def configPlot(parameters):
    THEME = parameters["THEME"]
    if(THEME == 1):
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "cornsilk"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (16, 9)
    elif(THEME == 2):
        plt.style.use("dark_background")
        plt.rcParams["axes.facecolor"] = "#1c1c1c"
        plt.rcParams["savefig.facecolor"] = "#1c1c1c"
        plt.rcParams["figure.figsize"] = (16, 9)
    elif(THEME == 3):
        plt.rcParams["axes.facecolor"] = "white"
        plt.rcParams["figure.figsize"] = (8, 8)

    fig, ax = plt.subplots(1)
    if(parameters["GRID"] == 1):
        ax.grid(True)
        plt.grid(which="major", color="dimgrey", linewidth=0.8)
        plt.grid(which="minor", color="dimgrey", linestyle=":", linewidth=0.5)
    else:
        ax.grid(False)
    return fig, ax



def plot(ax, data, label, fStd=0, color="orange", linestyle="-", marker=".", parameters=False):
    ax.plot(data["nevals"], data["Eo"], color=color, linestyle=linestyle, marker=marker, markersize=0, label=label)
    if(fStd):
        ax.fill_between(data["nevals"], data["Eo"] - data["std"], data["Eo"] + data["std"], color=color, alpha=0.1)
    ax.set_xlabel("Evaluations", fontsize=15)
    ax.set_ylabel("Offline error", fontsize=15)
    if(parameters["YLIM"]):
        ax.set_ylim(bottom=parameters["YLIM"][0], top=parameters["YLIM"][1])
    else:
        ax.set_ylim(bottom=0)
    if(parameters["XLIM"]):
        ax.set_xlim(left=parameters["XLIM"][0], right=parameters["XLIM"][1])
    else:
        ax.set_xlim(0, data["nevals"].iloc[-1])
    #plt.xscale("log")
    return ax




def showPlots(fig, ax, parameters, parameters2, path):
#    path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}/{sys.argv[2]}"
    THEME = parameters["THEME"]
    plt.legend()
    for text in plt.legend().get_texts():
        if(THEME == 1):
            text.set_color("black")
        elif(THEME == 2):
            text.set_color("white")
        text.set_fontsize(14)
    title = parameters["TITLE"]
    if(parameters["TITLE"] == 0):
        if(parameters["THEME"] == 3):
            title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']}"
        else:
            title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']} \n\n \
                    POPSIZE: {parameters2['POPSIZE']}   \
                    NPEAKS: {parameters2['NPEAKS_MPB']}\
                    DIM: {parameters2['NDIM']}\
                    SEVERITY: {parameters2['MOVE_SEVERITY_MPB']} \
                    "
    ax.set_title(title, fontsize=20)
    plt.savefig(f"{path}/{parameters['NAME']}", format="png")
    plt.show()



def mean(data):
    bMean = [0 for i in range( len(data[0]["Eo"]) )]
    bStd = [0 for i in range( len(data[0]["Eo"]) )]
    std = [0 for i in range( len(data) )]
    sum = 0

    for i in range (len(data[0]["Eo"])):
        for j in range(len(data)):
            sum += data[j]["Eo"][i]
            std[j] = data[j]["Eo"][i]
        bMean[i] = sum/len(data)
        bStd[i] = np.std(std)
        sum = 0
        std = [0 for i in range( len(data) )]

    zipped = list(zip(data[0]["nevals"], bMean, bStd))
    bestMean = pd.DataFrame(zipped, columns=["nevals", "Eo", "std"])
    return bestMean



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:", ["help", "path="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-p", "--path"):
            path = arg

    print(f"[PATH]: {path}")

    # reading the parameters from the config file
    with open(f"./config.ini") as f:
        parameters = json.loads(f.read())
    debug = parameters["DEBUG"]

    THEME = parameters["THEME"]
    fig, ax = configPlot(parameters)

    #path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}"
    for j in range(3, len(sys.argv)):

        pathTmp = f"{path}/{sys.argv[j]}"
        print(f"[PATH {j-2}]: {pathTmp}")

        df = pd.read_csv(f"{pathTmp}/data.csv")

        with open(f"{pathTmp}/config.ini") as f:
            parameters2 = json.loads(f.read())

        #print( len(pd.unique(df["run"])) )
        data = [[] for i in range( len(pd.unique(df["run"])) )]
        for i in range(len(pd.unique(df["run"])) ):
            data[i] = df[df["run"] == i+1]
            #data[i] = data[i].drop_duplicates(subset=["gen"], keep="last")[["gen", "nevals", "bestError", "Eo", "env"]]
            data[i].reset_index(inplace=True)
            if(parameters["ALLRUNS"]):
                ax = plot(ax, data=data[i], label=f"Run {i+1}", color=colors[i], parameters=parameters)

        EoMean = mean(data)
        if(parameters["THEME"] == 3):
            ax = plot(ax, data=EoMean, label=f"{parameters2['ALGORITHM']}", color=colors[j-2], linestyle=lineStyles[j-2], marker=markers[j-2], fStd=1, parameters=parameters)
        else:
            ax = plot(ax, data=EoMean, label=f"{parameters2['ALGORITHM']}(M{parameters2['NSWARMS']:02}ESP{parameters2['ES_PARTICLE_PERC']}ESC{parameters2['ES_CHANGE_OP']}LS{parameters2['LOCAL_SEARCH_OP']}X{parameters2['EXCLUSION_OP']}C{parameters2['ANTI_CONVERGENCE_OP']})", color=colors[j-2], linestyle=lineStyles[j-2], fStd=1, parameters=parameters)


    if(parameters2["RANDOM_CHANGES"]):
        changesEnv = parameters2["CHANGES_NEVALS"]
    else:
        changesEnv = parameters2["CHANGES_NEVALS"]
    #changesEnv = data[0].ne(data[0].shift()).filter(like="env").apply(lambda x: x.index[x].tolist())["env"][1:]
    if(parameters["THEME"] != 3):
        for i in changesEnv:
            plt.axvline(int(i), color="black", linestyle="--")
    showPlots(fig, ax, parameters, parameters2, path)


if __name__ == "__main__":
    main()
