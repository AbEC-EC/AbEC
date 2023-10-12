'''
Code to evaluate the offline error of data file

Alexandre Mascarenhas

2023/1
'''
import json
import numpy as np
import pandas as pd
import datetime
import sys
import time
import getopt
from aux.aux import *

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

def offlineError(path, std=1):
    df = pd.read_csv(path)

    #luffy = df.drop_duplicates(subset=["run"], keep="last")[["Eo"]]
    eo = [np.mean(df["eo"]), np.std(df["eo"])]

    if(std):
        return eo
    else:
        return eo[0]


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

    '''
    # Read the parameters from the config file
    with open(f"{sys.path[0]}/algoConfig.ini") as f:
        p0 = json.loads(f.read())
    with open(f"{sys.path[0]}/benchConfig.ini") as f:
        p1 = json.loads(f.read())
    with open(f"{sys.path[0]}/frameConfig.ini") as f:
        p2 = json.loads(f.read())

    parameters = p0 | p1 | p2
    '''


    # Evaluate the offline error
    Eo = offlineError(path, std = parameters["STD_Eo"])
    #writeTXT(Eo, "offlineError", path, std = parameters["STD_Eo"])
    if(parameters["DEBUG"] and debug):
        if(parameters["STD_Eo"]):
            print(f"\n[Offline Error]:")
            print(f"- File: {path}")
            print(f"- Value: {Eo[0]:.5f}({Eo[1]:.5f})")
        else:
            print(f"\n[Offline Error]: {Eo:.5f}")

    executionTime = (time.time() - startTime)

    if(parameters["DEBUG"] and debug):
        print(f"File generated: {path}/offlineError.txt")
        print(f'Time Exec: {str(executionTime)} s')


if __name__ == "__main__":
    main()
