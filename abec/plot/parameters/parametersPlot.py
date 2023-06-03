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
import getopt

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

colors = ["orange", "#820e57", "#afafaf", "red", "green", "blue", "yellow"]
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



def plot(ax, data, label, fStd=0, color="orange", linestyle="-", markers=".", parameters=False):
    ax.plot(data.iloc[:, 0], data.iloc[:, 1], color=color, linestyle=linestyle, label=label, marker=markers, markersize=10)
    if(fStd):
        ax.fill_between(data.iloc[:, 0], data.iloc[:, 1] - data.iloc[:, 2], data.iloc[:, 1] + data.iloc[:, 2], color=color, alpha=0.1)
    ax.set_xlabel(f"{label}", fontsize=12)
    ax.set_ylabel("Offline error", fontsize=12)
    if(parameters["YLIM"]):
        ax.set_ylim(bottom=parameters["YLIM"][0], top=parameters["YLIM"][1])
    else:
        ax.set_ylim(bottom=0)
    if(parameters["XLIM"]):
        ax.set_xlim(left=parameters["XLIM"][0], right=parameters["XLIM"][1])
    else:
        ax.set_xlim(0, data.iloc[:, 0].iloc[-1])
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
            title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']} \n \
                     POPSIZE: {parameters2['POPSIZE']}   \
                     NPEAKS: {parameters2['NPEAKS_MPB']}\
                     DIM: {parameters2['NDIM']}\
                     SEVERITY: {parameters2['MOVE_SEVERITY_MPB']} \
                     "
    ax.set_title(title, fontsize=16)
    ax.set_xlabel("RLS, REXCL and RCONV", fontsize=12)
    if(parameters["NAME"]==0):
        plt.savefig(f"{path}/{parameters['ALGORITHM']}-{parameters['PARAMETER']}.png", format="png")
    else:
        plt.savefig(f"{path}/{parameters['NAME']}.png", format="png")
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

def parameterOe(path):
    dirValues = list()
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            dirValues.append(float(os.path.join(name)))
    dirValues.sort()
    offlineError = []
    stdOe = []
    for value in dirValues:
        print(value)
        pathTmp = f"{path}/{value}/offlineError.txt"
        file = open(pathTmp, "r")
        data = file.read().split("\t")
        offlineError.append(float(data[0]))
        stdOe.append(float(data[1]))
        file.close()

    return dirValues, offlineError, stdOe

def main():
    path = ""
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


    # reading the parameters from the config file

    with open(f"./config.ini") as f:
        parameters = json.loads(f.read())
    debug = parameters["DEBUG"]
    if(debug):
        print("Parameters:")
        print(parameters)

    THEME = parameters["THEME"]
    fig, ax = configPlot(parameters)
    offlineError = list()
    stdOe = list()

    df = []
    df.append(pd.DataFrame(columns=["rls", "rls_oe", "rls_oe_std"]))
    df.append(pd.DataFrame(columns=["rexcl", "rexcl_oe", "rexcl_oe_std"]))
    df.append(pd.DataFrame(columns=["rconv", "rconv_oe", "rconv_oe_std"]))

    df[0]["rls"], df[0]["rls_oe"], df[0]["rls_oe_std"] = parameterOe(f"{path}/RLS")
    df[1]["rexcl"], df[1]["rexcl_oe"], df[1]["rexcl_oe_std"] = parameterOe(f"{path}/REXCL")
    df[2]["rconv"], df[2]["rconv_oe"], df[2]["rconv_oe_std"] = parameterOe(f"{path}/RCONV")

    PARA = ["RLS", "REXCL"]

    with open(f"{path}/RLS/0.0/config.ini") as f:
        parameters2 = json.loads(f.read())

    #zipped = list(zip(, offlineError, stdOe))
    for i, parameter in enumerate(PARA):
            ax = plot(ax, data=df[i], \
                label=parameter,
                color=colors[i],
                linestyle=lineStyles[i],
                markers=markers[i],
                fStd=1,
                parameters=parameters)

    showPlots(fig, ax, parameters, parameters2, path)


if __name__ == "__main__":
    main()
