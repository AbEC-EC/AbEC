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

cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

def writeTXT(data, name, path):
    line = f"- {name}= {data[0]:.4f}({data[1]:.4f})\n"
    print(line)
    f = open(f"{path}/results.txt","a")
    f.write(line)
    f.close()

def absoluteRecoveryRate(path, std=1):
    df = pd.read_csv(f"{path}/data.csv")
    optima = pd.read_csv(f"{path}/optima.csv")
    data = [[] for i in range( len(pd.unique(df["run"])) )]
    env = [[[] for _ in range( len(pd.unique(df["env"])) )] for i in range (len(pd.unique(df["run"])) )]
    for i in range(len(pd.unique(df["run"])) ): # Get the number of runs
        data[i] = df[df["run"] == i+1]
        for j in range(len(pd.unique(df["env"]))):
            env[i][j] = data[i][["nevals", "bestError", "env"]][data[i]["env"] == i+1]
            env[i][j].to_csv(f"{path}/Run{i+1}-Env{j}.csv", index = True)
        data[i] = data[i].drop_duplicates(subset=["gen"], keep="last")[["gen", "nevals", "swarmId", "bestError", "env"]]
        data[i].reset_index(inplace=True)
        del data[i]["index"]
        #data[i].to_csv(f"{path}/run{i+1}.csv", index = True)

    NENVS = len(env[0])
    NRUNS = len(data)
    NEVALS = len(env[0][0]['bestError'])
    luffy = [[0 for i in range(NENVS)] for _ in range(NRUNS)]
    zoro = [0 for _ in range(NRUNS)]

    print(env[1][0]['bestError'])
    #p()

    print(f"[NEVALS:{NEVALS}][NRUNS:{NRUNS}][NENVS:{NENVS}]")
    for j in range(NRUNS):
        for i in range(NENVS):
            erro = 0
            for k in range(len(env[j][i]['bestError'])):
               # print(f"[RUN:{j}][ENV:{i}][GEN:{k}]")
               # print(f"[RUN:{j}][ENV:{i}][GEN:{k}]: {abs(env[j][i]['bestError'][k] - env[j][i]['bestError'][0] )} ")
                erro += abs(env[j][i]['bestError'][k] - env[j][i]['bestError'][0])
            erro /= len(env[j][i]['bestError'])*abs(float(optima['opt0'][i][1:10]) - env[j][i]['bestError'][0])
            luffy[j][i] = erro

    for j in range(NRUNS):
        zoro[j] = np.mean(luffy[j])

    arr = [np.mean(zoro), np.std(zoro)]
    if(std):
        return arr
    else:
        return arr[0]


def main():
    # reading the parameters from the config file
    try:
        path = sys.argv[1]
    except IndexError:
        with open("./config.ini") as f:
            parameters = json.loads(f.read())
        debug = parameters["DEBUG"]
        if(debug):
            print("Parameters:")
            print(parameters)
        #path = f"{parameters['PATH']}/{parameters['ALGORITHM']}/{sys.argv[1]}/{sys.argv[2]}"

    ARR = absoluteRecoveryRate(path, 0)
    print(ARR)


if __name__ == "__main__":
    main()
