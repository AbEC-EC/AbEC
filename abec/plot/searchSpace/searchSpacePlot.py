
'''
Code to plot search space graph using data file

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
import getopt
import matplotlib.pyplot as plt
import datetime
import os
import csv
import sys

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

#colors = ["r", "b", "#afafaf", "#820e57", "orange", "yellow"]
colors = ["r", "b", "#afafaf", "#820e57", "orange", "yellow","r", "b", "#afafaf", "#820e57", "orange", "yellow","r", "b", "#afafaf", "#820e57", "orange", "yellow"]
colorS = ["orange", "red", "g", "b"]
colors2 = ["r", "gray"]

def configPlot(parameters):
    THEME = parameters["THEME"]
    #plt.rcParams["figure.figsize"] = (20, 8)
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


def plot(ax, data, label=None, fStd=0, color="orange", s=1, marker="o", alpha=1, conn=False):
    #print(data)
    x = [item[0] for item in data]
    y = [item[1] for item in data]
    if(conn):
        ax.plot(x,y, color=color, label=label, marker=marker, markersize=s, alpha=alpha)
    else:
        ax.scatter(x,y, color=color, label=label, s=s, marker=marker, alpha=alpha)
    if(fStd):
        ax.fill_between(data["gen"], data["bestError"] - data["std"], data["bestError"] + data["std"], color="dark"+color, alpha=0.1)
    ax.set_xlabel("X", fontsize=15)
    ax.set_ylabel("Y", fontsize=15)
    #ax.set_ylim(bottom=0)
    ax.set_ylim(0, 100)
    #print(len(data["gen"]))
    ax.set_xlim(0, 100)
    return ax


def showPlots(fig, ax, path, parameters):
    THEME = parameters["THEME"]
    plt.legend()
    for text in plt.legend().get_texts():
        if(THEME == 1):
            text.set_color("black")
        elif(THEME == 2):
            text.set_color("white")
        text.set_fontsize(12)
    title = parameters["TITLE"]
    if(parameters["TITLE"] == 0):
        title = f"{parameters['ALGORITHM']} on {parameters['BENCHMARK']}"
    ax.set_title(title, fontsize=20)
    plt.savefig(f"{path}/scatter.png", format="png")
    plt.show()


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
        #pathTmp = f"{path}"
        print(f"[PATH {j-2}]: {pathTmp}")

        df = pd.read_csv(f"{pathTmp}/data.csv")

     # Read the parameters from the config file
        with open(f"{pathTmp}/algoConfig.ini") as f:
            p0 = json.loads(f.read())
        with open(f"{pathTmp}/frameConfig.ini") as f:
            p1 = json.loads(f.read())
        with open(f"{pathTmp}/problemConfig.ini") as f:
            p2 = json.loads(f.read())

        parameters2 = p0 | p1 | p2

        #path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}/{sys.argv[2]}"
        df = pd.read_csv(f"{pathTmp}/data.csv")
        gop = pd.read_csv(f"{pathTmp}/optima.csv")

        #print( len(pd.unique(df["run"])) )
        data = [[] for i in range( len(pd.unique(df["run"])) )]
        best = [[] for i in range( len(pd.unique(df["run"])) )]
        ind = [[] for i in range( len(pd.unique(df["run"])) )]
        if(parameters2["COMP_MULTIPOPULATION"]):
            subpops = [[] for i in range( len(pd.unique(df["popId"])) )]
            bsubpop = [[] for i in range( len(pd.unique(df["popId"])) )]

        for i in range(len(pd.unique(df["run"])) ):
            data[i] = df[df["run"] == i+1]
            #print(data[i])
            if parameters2["COMP_MULTIPOPULATION"]:
                for j in range(len(pd.unique(data[i]["popId"])) ): # Get the number of runs
                    subpops[j] = data[i][data[i]["popId"] == j+1]
                    bsubpop[j] = subpops[j].drop_duplicates(subset=["gen"], keep="last")[["popBestPos"]]
                    #bsubpop[j] = bsubpop[j].iloc[-1]
                    #print(bsubpop[j]["popBestPos"])
                    bsubpop[j].reset_index(inplace=True)
                    #print(bsubpop[j]["popBestPos"].iloc[-1])
                    bsubpop[j] = bsubpop[j]["popBestPos"].values.tolist()[-2:-1]
                    print(bsubpop[j])
                    #e()
                    temp = [json.loads(item)[0:2] for item in bsubpop[j]]
                    ax = plot(ax, data=temp, color=colors[j], s=4000, alpha=0.5)
            else:
                best[i] = data[i].drop_duplicates(subset=["gen"], keep="last")[["bestPos"]]
                best[i].reset_index(inplace=True)
                best[i] = best[i]["bestPos"].values.tolist()
                #part[i] = data[i]["indPos"].values.tolist()
                #temp = [json.loads(item)[0:2] for item in part[i]]
                #ax = plot(ax, data=temp, label=f"Run {i+1}", color=colors[i], s=5, alpha=0.3)
                temp = [json.loads(item)[0:2] for item in best[i]]
                ax = plot(ax, data=temp, color=colors[i], s=5, marker="X", conn=True)


        for k in range(gop.shape[1]):
            temp = gop[f"opt{k}"].values.tolist()
            for j in range(len(temp)):
                temp[j] = list(temp[j].split(", "))
                for i in range(len(temp[j])):
                    temp[j][i] =  temp[j][i].replace("[", "")
                    temp[j][i] =  temp[j][i].replace("(", "")
                    temp[j][i] =  temp[j][i].replace(")", "")
                    temp[j][i] =  temp[j][i].replace("]", "")
                    temp[j][i] =  float(temp[j][i])

            #print(temp)
            x = [[x[1], x[2]] for x in temp]
            if(k == 0):
                ax = plot(ax, data=x, label=f"GOP", color="green", s=10, marker="*", conn=True)
            else:
                ax = plot(ax, data=x, color="green", s=5, marker="s", conn=True, alpha=0.5)


        showPlots(fig, ax, pathTmp, parameters)


if __name__ == "__main__":
    main()
