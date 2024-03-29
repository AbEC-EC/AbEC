#!/usr/bin/env python3

'''
Base code for AbEC framework

Alexandre Mascarenhas

2023/1
'''
import datetime
import os
import sys
import getopt
import psutil
import time
import ast
import logging
import json
from math import dist
import shutil
import pandas as pd
import numpy as np
from abec import abec
import matplotlib.colors as mcolors
# AbEC files
import plot.currentError as ecPlot
import plot.offlineError as eoPlot
import gui.gui as gui
from aux.aux import *

def getSearchSpace(pop, layout):
    x = []
    y = []
    i = 0
    for subpop in pop:
        x = [d["pos"][0] for d in subpop.ind]
        y = [d["pos"][1] for d in subpop.ind]
        layout.ax_ss.scatter(x, y, c=list(mcolors.CSS4_COLORS)[i], s=0.5, alpha=0.5)
        #layout.ax_ss.scatter(subpop.best["pos"][0], subpop.best["pos"][1], c=list(mcolors.CSS4_COLORS)[i], s=80, alpha=0.8 )
        #print(f"{subpop.best['pos']}, {subpop.best['fit']}")
        i += 1
    return x, y


def initializeInterface(layout):
    layout.window["-OUTPUT-"].update("")
    layout.window["-EXP-"].update(disabled=True)
    layout.window["-ALGO-"].update(disabled=True)
    layout.window["-PRO-"].update(disabled=True)
    layout.window["-COMPS-"].update(visible=False)
    layout.window["butao"].update("Choose the file")
    layout.window["browseFit"].update(disabled=True)
    layout.window["program.sr"].update(False, visible=False)
    layout.window["program.ct"].update(False, visible=False)
    layout.window["program.aad"].update(False, visible=False)
    layout.window["continueBT"].update("Continue")
    layout.window["continueBT"].update(disabled=False)
    layout.window["resetBT"].update(disabled=True)
    #layout.launch()

def analysis(path, parameters, totalTime, readme):
    myPrint("\n[RESULTS]", readme, parameters)

    curError = [0, 0] # current error of the runs
    offError = [0, 0] # offline error of the runs
    meanTime = [0, 0] # executiation time of the runs

    # load the csv with the results
    df = pd.read_csv(f"{path}/results/results.csv")
    df.sort_values(by="ec", inplace=True)

    # calculate the mean of the erros and time
    curError[0] = df["ec"].mean()
    offError[0] = df["eo"].mean()
    meanTime[0] = df["execTime"].mean()

    # get the best run and convert to dict
    best = df.iloc[0].to_dict()
    best["bestPos"] = ast.literal_eval(best["bestPos"]) # convert string to list
    best["bestPos"] = [round(i, 2) for i in best["bestPos"]] # round 2 decimals

    if parameters["RUNS"] > 1:
        # calculate the std of the error and time
        curError[1] = df["ec"].std()
        offError[1] = df["eo_std"].std()
        meanTime[1] = df["execTime"].std()

        ecMean_csv = ecMean(f"{path}/results", parameters)
        eoMean_csv = eoMean(f"{path}/results", parameters)
        ecPlot.ecPlot(ecMean_csv, parameters, multi = 1, pathSave = f"{path}/results", name="ecMean")
        eoPlot.eoPlot(eoMean_csv, parameters, multi = 1, pathSave = f"{path}/results", name="eoMean")
    else:
        offError[1] = df["eo_std"][0]   # If only one run just the number

        # get the run data file of the run
        flist = os.listdir(f"{path}/results")
        pdir = f"{path}/results/{sorted(flist)[0]}"
        runFile = f"{pdir}/{sorted(os.listdir(pdir))[-1]}"

        ecPlot.ecPlot(runFile, parameters, pathSave = f"{path}/results/0001")
        eoPlot.eoPlot(runFile, parameters, pathSave = f"{path}/results/0001")
        #frPlot.frPlot(f"{globalVar.path}/results/{parameters['ALGORITHM']}_01_{parameters['SEED']}", parameters, pathSave = f"{globalVar.path}/results")
        #spPlot.spPlot(f"{globalVar.path}/results/log_all_{globalVar.seedInit}", parameters, pathSave = f"{globalVar.path}/results")


    if parameters["DEBUG_RUN"]:
        #####################################
        # print all the files generated
        #####################################
        files = os.listdir(f"{path}/results")
        myPrint(f"\n[FILES GENERATED]\n", readme, parameters)
        myPrint(f"-[PATH] {path}/results/", readme, parameters)
        files = sorted(files)
        for file in files:
            if os.path.isdir(f"{path}/results/{file}"):
                files2 = os.listdir(f"{path}/results/{file}")
                files2 = sorted(files2)
                for file2 in files2:
                    myPrint(f"\t-[FILE] {file}/{file2}", readme, parameters)
            else:
                myPrint(f"\t-[FILE] {file}", readme, parameters)

        if parameters["RUNS"] > 1:
            myPrint(f"\n==============================================", readme, parameters)
            myPrint(f"[RUNS:{parameters['RUNS']}]", readme, parameters)
            myPrint(f"[BEST POS (RUN {best['run']}) : {best['bestPos']}]", readme, parameters)
            myPrint(f"[BEST FIT (RUN {best['run']}): {best['ec']:.04f}]", readme, parameters)
            myPrint(f"[Ec  MEAN: {curError[0]:.4f}({curError[1]:.4f})]", readme, parameters)
            myPrint(f"[Eo  MEAN: {offError[0]:.4f}({offError[1]:.4f})]", readme, parameters)
        else:
            myPrint(f"\n==============================================", readme, parameters)
            myPrint(f"[RUNS:{parameters['RUNS']}]", readme, parameters)
            myPrint(f"[BEST POS : {best['bestPos']}]", readme, parameters)
            myPrint(f"[EC  : {best['ec']:.4f}]", readme, parameters)
            myPrint(f"[Eo  : {offError[0]:.4f}({offError[1]:.4f})]", readme, parameters)

        myPrint(f"[RUNTIME(s): {float(totalTime):.02f} | {meanTime[0]:.02f}({meanTime[1]:.02f})/run {parameters['PARALLELIZATION']}]", readme, parameters)
        myPrint(f"==============================================", readme, parameters)


    if(parameters["BEBC_ERROR"]):
        if (parameters["DEBUG_RUN"]):
            myPrint("\n[METRICS]", readme, parameters)
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {path} -d 1")
        else:
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {path}")


def checkRuns(path):
    df = pd.read_csv(f"{path}/results/results.csv")
    return df.shape[0]

def printRuns(layout, path):
    fileTmp = open(f"{path}/printTmp.txt", "r")
    content = fileTmp.read()
    print(content[:-2])
    layout.window.refresh()
    fileTmp.close()
    os.remove(f"{path}/printTmp.txt")

def getPids(script_name):
    pids = []
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            pid = proc.pid
        except psutil.NoSuchProcess:
            continue

        if (len(cmdline) >= 2
            and 'python' in cmdline[0]
            and os.path.basename(cmdline[1]) == script_name):
            pids.append(pid)

    return pids

get_time = lambda f: os.stat(f).st_ctime


def loadConfigFiles(parameters, pathConfig):
    #Read the parameters from the config file
    parametersFiles = ["algoConfig.ini", "expConfig.ini", "problemConfig.ini"]
    for file in parametersFiles:
        if os.path.isfile(f"{pathConfig}/{file}"):
            with open(f"{pathConfig}/{file}") as f:
                p0 = list(json.loads(f.read()).items())
                for i in range(len(p0)):
                    parameters[f"{p0[i][0]}"] = p0[i][1]
        else:
            errorWarning(0.1, f"{file}", "FILE_NOT_FOUND", f"The {file} file is mandatory!")
    return parameters


def getRunsFiles(path, luffy, logAllRuns, optimaRuns, nRuns):
    path += "/results"
    if(os.path.isdir(f"{path}")):
        zoro = [name for name in os.listdir(path) if(name != "readme.txt" and name != "results.csv")]
        if(nRuns != len(zoro)):
            for run in zoro:
                content = os.listdir(f"{path}/{run}")
                if(len(content) >= 2):
                    for file in content:
                        if(file[-7:-4] == "RUN"):
                            full = f"{path}/{run}/{file}"
                            if(full not in luffy):
                                luffy.append(full)
                                nRuns = len(zoro)
                        elif(file[-10:-4] == "LOGALL"):
                            full = f"{path}/{run}/{file}"
                            if(full not in logAllRuns):
                                logAllRuns.append(full)
                        elif(file[-10:-4] == "OPTIMA"):
                            full = f"{path}/{run}/{file}"
                            if(full not in optimaRuns):
                                optimaRuns.append(full)


    return luffy, logAllRuns, optimaRuns, nRuns


# plot the current state of the run files
def plotRuns(luffy, layout, nruns):
    if(layout.enablePF):
        for run in luffy:
            nrun = int(run[-15:-11])
            df = pd.read_csv(run)[["nevals", "ec", "eo"]]
            x = df["nevals"].to_list()
            ec = df["ec"].to_list()
            eo = df["eo"].to_list()
            if(x and eo[-1] > 0):
                if(nrun not in nruns):
                    nruns.append(nrun)
                    layout.run(x=x, y1=ec, y2=eo, r=nrun, legendFlag = 1)
                else:
                    layout.run(x=x, y1=ec, y2=eo, r=nrun)
    return nruns

# plot the current state of the run files
def plotRunsSearchSpace(path, layout, lastGen, parameters):
    df = pd.read_csv(path)
    if( (not df.empty) and (df["gen"].iloc[-1]>lastGen) ):
        lastGen = df["gen"].iloc[-1]
        layout.ax_ss.clear()
        layout.ax_ss.set_xlim(int(parameters["MIN_POS"]), int(parameters["MAX_POS"]))
        layout.ax_ss.set_ylim(int(parameters["MIN_POS"]), int(parameters["MAX_POS"]))
        posAll = df[df["gen"] == df["gen"].iloc[-1]-1]
        for subpops in range(1, len(pd.unique(posAll["popId"]))+1):
            x = []
            y = []
            pos = posAll[["indPos", "indFit"]][(posAll["popId"] == subpops)]
            minFit = pos["indFit"].min()
            maxFit = pos["indFit"].max()
            worst = pos["indPos"][pos["indFit"]==maxFit].to_list()[0]
            best = pos["indPos"][pos["indFit"]==minFit].to_list()[0]
            worst = ast.literal_eval(worst)[:2]
            best = ast.literal_eval(best)[:2]
            distance = np.sqrt(((float(best[0])-float(worst[0]))**2) + ((float(best[1])-float(worst[1]))**2))
            medium = [(best[0] + worst[0])/2, (best[1] + worst[1])/2]
            #distance = dist(worst, best)
            if distance < 1:
                distance = 10
            layout.ax_ss.scatter(float(best[0]), float(best[1]), c=list(mcolors.CSS4_COLORS)[subpops*3], s=50, marker="X", linewidth=0, alpha=0.7)
            layout.ax_ss.scatter(float(best[0]), float(best[1]), c=list(mcolors.CSS4_COLORS)[subpops*3], s=(4*distance)**2, linewidth=0, alpha=0.1)
            #layout.ax_ss.scatter(float(worst[0]), float(worst[1]), c=list(mcolors.CSS4_COLORS)[subpops*2], s=50, linewidth=0, alpha=0.7)
            for row in pos["indPos"].tolist():
                    row = ast.literal_eval(row)
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    layout.ax_ss.scatter(x, y, c=list(mcolors.CSS4_COLORS)[subpops*3], s=3, linewidth=0, alpha=0.7)
                    
        layout.fig_agg_ss.draw()
        '''
            if(pos):
                for row in pos:
                    row = ast.literal_eval(row)
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    layout.ax_ss.scatter(x, y1, c=list(mcolors.CSS4_COLORS)[subpops], s=distance, alpha=0.5)
                    layout.fig_agg_ss.draw()

                
                if(nrun not in nruns):
                    nruns.append(nrun)
                    layout.run(x=x, y1=y, type=2, r=subpops, legendFlag = 1)
                    layout.run(x=x, y1=y, type=2, r=nrun, legendFlag = 1)
                else:
                    layout.run(x=x, y1=y, type=2, r=nrun)
        '''
    return lastGen


# plot the current state of the run files
def plotOptimaSearchSpace(optimaRuns, layout, nruns):
    if(layout.enableSS):
        first = 1
        x = []
        y = []
        for run in optimaRuns:
            nrun = int(run[-18:-14])
            opts = pd.read_csv(run)
            if(len(opts) > 0):
                opts = opts.iloc[0].to_list()
                if(opts):
                    for opt in opts:
                        if(type(opt) == str):
                            opt = opt.split(",")
                            x.append(float(opt[1][2:6]))
                            y.append(float(opt[2][1:5]))
                        if(first):
                            layout.ax_ss.scatter(x, y, c="orange", marker="X", s=50, linewidth=0, alpha=0.7)
                            first = 0
                    layout.ax_ss.scatter(x, y, c="red", s=5, alpha=0.7)
                    layout.fig_agg_ss.draw()
    return nruns


def main():

    #####################################
    # log file for debbug
    #####################################
    LOG_FILENAME = "./aux/log/log_last_run.txt"
    if os.path.isfile(LOG_FILENAME):
        os.remove(LOG_FILENAME)
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    logging.debug('This message should go to the log file')

    #####################################
    # start the framework
    #####################################
    while(True):
        try:
            # datetime variables
            cDate = datetime.datetime.now()
            date = {"year": cDate.year, "month": cDate.month, "day": cDate.day, "hour": cDate.hour, "minute": cDate.minute}

            seed = date["minute"]
            pathConfig = "."
            interface = 1
            nruns = 0
            running = 0
            ran = 0

            #####################################
            # get the arguments
            #####################################
            arg_help = "{0} -i <interface> -s <seed> -p <path>".format(sys.argv[0])
            try:
                opts, args = getopt.getopt(sys.argv[1:], "hi:s:p:", ["help", "interface=", "seed=", "path="])
            except:
                print(arg_help)
                sys.exit(2)

            for opt, arg in opts:
                if opt in ("-h", "--help"):
                    print(arg_help)  # print the help message
                    sys.exit(2)
                elif opt in ("-i", "--interface"):
                    interface = int(arg)
                elif opt in ("-s", "--seed"):
                    if seed >= 0:
                        seed = int(arg)
                elif opt in ("-p", "--path"):
                    if arg != "./":
                        pathConfig = arg

            if interface:
                if "layout" not in locals():
                    layout = gui.interface()
                    print("[initializing ... ]")
                    layout.window["continueBT"].update(disabled=True)
                    layout.window.refresh()
                    layout.launch()
                    layout.window["continueBT"].update(disabled=False)
                    layout.window.refresh()

                else:
                    layout.ax_pf = gui.configAxes(layout.ax_pf)
                    layout.ax_ss = gui.configAxes(layout.ax_ss, type = 2)
                    layout.reset = 0

                    initializeInterface(layout)
                    step = 0

            else:
                layout = 0

            if interface:
                print(f"==============================================================================================================")
                print(f"                                   AbEC -> Ajustable Evolutionary Components        ")
                print(f"                                     A framework for Optimization Problems         ")
                print(f"==============================================================================================================")
                print("*                                                                                                            *")
                print("*                                                                                                            *")
                print("*                                            I hope you enjoy!                                               *")
                print("*                                                                                                            *")
                print("*                                                                                                            *")
                print("*                                             Press Continue                                                 *")
                print("*                                                                                                            *")
                print("*                                                                                                            *")
                print("*                        For more informations please visit: https://abec-ec.github.io                       *")

            if interface:
                try:
                    layout.window.refresh()
                    time.sleep(1)
                    layout.set(pathConfig, step = 0)
                    layout.window["-EXP-"].update(disabled=False)
                    layout.window["-ALGO-"].update(disabled=False)
                    layout.window["-PRO-"].update(disabled=False)
                    layout.window["resetBT"].update(disabled=False)
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    print("[Please check if the configuration files are ok and then press continue...]")
                    print("\n[ - Experiment configuration file: Framework parameters (e.g. number of runs, path of the files, number of evaluations, ...)]")
                    print("\n[ - Algorithm configuration file: Functioning of the algorithm itself (e.g. Population size, optimizers, ...)]")
                    print("\n[ - Problem configuration file: e.g. number of dimensions, dynamic or not, ...]")
                    layout.set(pathConfig)
                    if layout.reset:
                        continue
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    print("[Loading configuration files...]")
                    layout.window.refresh()
                except SyntaxError:
                    pass

            #####################################
            # load the parameter files
            #####################################
            parametersFiles = ["algoConfig.ini", "expConfig.ini", "problemConfig.ini"]
            algoParameters, algo = algoConfig()
            parameters = algoParameters | expConfig() | problemConfig()

            parameters = loadConfigFiles(parameters, pathConfig)

            if parameters["SEED"] >= 0:
                seed = parameters["SEED"]

            NCPUS = os.cpu_count()
            if parameters["NPROCESS"] == "MAX":
                parameters["NPROCESS"] = NCPUS
            elif parameters["NPROCESS"] == "AUTO":
                parameters["NPROCESS"] = int((2/3)*NCPUS)

            algo = updateAlgo(algo, parameters) # update the algorithm with the parameters

            #print(f"metrics: {algo.metrics}")

            #####################################
            # create the dir of the experiment
            #####################################
            if pathConfig == ".":
                pathExp = parameters["PATH"]
                checkCreateDir(pathExp)
                pathExp += f"/{parameters['ALGORITHM']}"
                pathExp = checkDirs(pathExp, date)
                # Copy the config.ini file to the experiment dir
                if(parameters["CONFIG_COPY"]):
                    for file in parametersFiles:
                        shutil.copyfile(f"{pathConfig}/{file}", f"{pathExp}/{file}")
            else:
                pathExp = pathConfig
                if(os.path.isdir(pathExp+"/results") == False):
                    os.mkdir(pathExp+"/results")
                else:
                    shutil.rmtree(pathExp+"/results")
                    os.mkdir(pathExp+"/results")

            readme = open(f"{pathExp}/results/readme.txt", "w") # open file to write the outputs
            headerReadme(readme, interface)

            saveTheDate = open(f"{pathExp}/savethedate.txt", "w")
            saveTheDate.write(f"{date['year']}/{date['month']:02}/{date['day']:02}/{date['hour']:02}/{date['minute']:02}")
            saveTheDate.close()

            if interface:
                layout.window["-EXP-"].update(disabled=True)
                layout.window["-ALGO-"].update(disabled=True)
                layout.window["-PRO-"].update(disabled=True)
                #layout.ax_pf.set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])
                layout.ax_pf[0].set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])

            bench = parameters["BENCHMARK"].upper()

            if bench == "CUSTOM":
                if interface:
                    try:
                        time.sleep(1)
                        print("[Loaded]\n")
                        layout.window.refresh()
                        time.sleep(0.3)
                        layout.window["-OUTPUT-"].update("")
                        layout.window.refresh()
                        layout.window["-EXP-"].update(disabled=True)
                        layout.window["-ALGO-"].update(disabled=True)
                        layout.window["-PRO-"].update(disabled=True)
                        layout.window["continueBT"].update(disabled=True)
                        layout.window["browseFit"].update(disabled=False)
                        print("[Input the fitness function file and press continue...]")
                        print("\n[ - The function should be defined in a python script, which will evaluate the solutions of the algorithm]")
                        layout.set(pathExp, step =4)
                        if layout.reset:
                            continue
                        layout.window["-OUTPUT-"].update("")
                        layout.window.refresh()
                        print("[Loading Fitness Function file...]")
                        layout.window["browseFit"].update(disabled=True)
                        layout.window.refresh()
                    except SyntaxError:
                        pass
                else:
                    #if(pathConfig != "."): # only copy if the path is not the abec folder
                    os.system(f"cp {pathConfig}/{parameters['FUNCTION']} {os.path.abspath(os.getcwd())}/function.py")

            if interface and False:
                try:
                    time.sleep(1)
                    print("[Loaded]\n")
                    layout.window.refresh()
                    time.sleep(0.3)
                    components = []
                    for i in range(len(algo.components)):
                        components.append(algo.components[i][0])
                    layout.window["program.sr"].update(visible=True)
                    layout.window["program.ct"].update(visible=True)
                    layout.window["program.aad"].update(visible=True)
                    layout.window["-COMPS-"].update(value="", values=components, visible=True)
                    layout.window.refresh()
                    print("[Select a program and press continue...]")
                    print("\n[ - Simple Run: A simple test of how the algorithm performs on the problem]")
                    print("\n[ - Component Evaluation: How a specific component performs. It will be done a bench of test with the component with and without other components and a personalized evaluation will be done on it]")
                    print("\n[ - Auto Algorithm Design: It will be find a good algorithm configuration which solves good for the specified problem]")
                    layout.window["-COMPS-"].update(value="", values=components, visible=False)
                    layout.window.refresh()
                    layout.set(step=3)
                    if layout.reset:
                        continue
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    print("[Preparing to run...]")
                    layout.window.refresh()
                    time.sleep(0.5)
                    print("[Ready]")
                    layout.window.refresh()
                    time.sleep(0.5)
                except SyntaxError:
                    pass


            if parameters["DEBUG_RUN"]:
                if interface:
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()

                myPrint(f"\n[ALGORITHM SETUP]", readme, parameters)
                myPrint(f"- Name: {parameters['ALGORITHM']}", readme, parameters)
                myPrint(f"- Individuals p/ population:\t{parameters['POPSIZE']}", readme, parameters)

                myPrint(f"- [OPTIMIZERS]:", readme, parameters)
                for opt in algo.optimizers:
                    myPrint(f"-- [{opt[0]}]", readme, parameters)
                    value = parameters[f"{opt[0]}_POP_PERC"]
                    myPrint(f"---- % of POP: {value*100}%", readme, parameters)
                    for i in opt[1].params:
                        value = parameters[f"{opt[0]}_{i}"]
                        myPrint(f"---- {i}: {value}", readme, parameters)

                myPrint(f"- [COMPONENTS]:", readme, parameters)
                for comp in algo.components:
                    myPrint(f"-- [{comp[0]}]", readme, parameters)
                    myPrint(f"---- SCOPE: {comp[1].scope[0]}", readme, parameters)
                    for i in comp[1].params:
                        value = parameters[f"COMP_{comp[0]}_{i}"]
                        myPrint(f"---- {i}: {value}", readme, parameters)

                myPrint(f"\n[FRAMEWORK SETUP]", readme, parameters)
                myPrint(f"- RUNS:\t\t {parameters['RUNS']}", readme, parameters)
                if parameters["FINISH_RUN_MODE"] == 0:
                    myPrint(f"- NEVALS p/ RUN: {parameters['FINISH_RUN_MODE_VALUE']}", readme, parameters)
                else:
                    myPrint(f"- Target error: {parameters['FINISH_RUN_MODE_VALUE']}", readme, parameters)
                myPrint(f"- SEED:\t\t {parameters['SEED']}", readme, parameters)

                myPrint(f"\n[PROBLEM SETUP]", readme, parameters)
                if parameters["BENCHMARK"] == "NONE":
                    myPrint(f"- Name: Fitness Function", readme, parameters)
                else:
                    myPrint(f"- Name: {parameters['BENCHMARK']}", readme, parameters)
                myPrint(f"- NDIM: {parameters['NDIM']}", readme, parameters)


            if interface:
                try:
                    layout.window.refresh()
                    print("\n[Check if the setup is correct, if so, press continue to start...]")
                    layout.set(pathExp)
                    if layout.reset:
                        continue
                    #layout.window["continueBT"].update("Cancel")
                    layout.window["continueBT"].update(disabled=True)
                    layout.window["resetBT"].update(disabled=True)
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                except SyntaxError:
                    pass

            # Create a list with the runs, seeds and if it is done or not
            # to allow the parallelization
            runs = [{"id": run+1, "seed": int(parameters["SEED"] + run), "done":0} for run in range(parameters["RUNS"])]

            header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "execTime"]
            keys = list(algo.mts)
            for i in range(len(algo.mts)):
                for j in algo.mts[keys[i]]:
                    for var in j.log:
                        header.append(var)
            #print(header)


            filename = f"{pathExp}/results/results.csv"
            writeLog(mode=0, filename=filename, header=header)

            if parameters["DEBUG_RUN"]:
                myPrint("\n[RUNNING]\n", readme, parameters)
                myPrint(f"RUN | GEN | NEVALS |                    BEST                   | ERROR", readme, parameters)
                if layout:
                    layout.window.refresh()

            readme.close()   # Close file for the runs

            numberRuns = 0
            luffy = [] # list with the paths of the runs files
            logAllRuns = []
            optimaRuns = []
            runsDone = []
            lastGenSS = 0
            runsDoneOP = []
            #####################################
            # Main loop of the runs
            #####################################
            startTime = time.time()
            if parameters["PARALLELIZATION"]:
                prev_time = get_time(f"{pathExp}/results/results.csv")
                for run in runs:
                    while True:
                        if interface:
                            if(layout.enablePF):
                                luffy, logAllRuns, optimaRuns, numberRuns = getRunsFiles(pathExp, luffy, logAllRuns, optimaRuns, numberRuns)
                                if(parameters["LOG_ALL"] and layout.enableSS and logAllRuns):
                                    lastGenSS = plotRunsSearchSpace(logAllRuns[0], layout, lastGenSS, parameters)
                                    if(parameters["BENCHMARK"] != "CUSTOM"):
                                        runsDoneOP = plotOptimaSearchSpace(optimaRuns, layout, runsDoneOP)
                                runsDone = plotRuns(luffy, layout, runsDone)
                        if running < parameters["NPROCESS"]:
                            break
                        t = get_time(f"{pathExp}/results/results.csv")
                        if t != prev_time: # if the file changed, see how many runs have finished
                            ran = checkRuns(pathExp)
                            running = nruns - ran
                            prev_time = t
                        if interface and os.path.isfile(f"{pathExp}/printTmp.txt"):
                            printRuns(layout, pathExp)



                    os.system(f"./abec.py -r {run['id']} -s {run['seed']} -p {pathExp} -i {interface} &")
                    #os.system(f"taskset -c {i},{i+1} ./abec.py -r {run['id']} -s {run['seed']} -p {pathExp} -i {interface} &")

                    nruns += 1
                    running = nruns - ran

                # wait for the runs fininsh if parallelization on
                prev_time = get_time(f"{pathExp}/results/results.csv")
                while True:
                    if interface:
                        if(layout.enablePF):
                            luffy, logAllRuns, optimaRuns, numberRuns = getRunsFiles(pathExp, luffy, logAllRuns, optimaRuns, numberRuns)
                            if(parameters["LOG_ALL"] and layout.enableSS and logAllRuns):
                                lastGenSS = plotRunsSearchSpace(logAllRuns[0], layout, lastGenSS, parameters)
                                if(parameters["BENCHMARK"] != "CUSTOM"):
                                    runsDoneOP = plotOptimaSearchSpace(optimaRuns, layout, runsDoneOP)
                            runsDone = plotRuns(luffy, layout, runsDone)
                    t = get_time(f"{pathExp}/results/results.csv")
                    if t != prev_time: # if the file changed, see how many runs have finished
                        ran = checkRuns(pathExp)
                        if checkRuns(pathExp) >= parameters["RUNS"]:
                            break
                        prev_time = t

                    if interface and os.path.isfile(f"{pathExp}/printTmp.txt"):
                        printRuns(layout, pathExp)


                if interface and os.path.isfile(f"{pathExp}/printTmp.txt"):
                    printRuns(layout, pathExp)
                    if(layout.enablePF):
                        luffy, logAllRuns, optimaRuns, numberRuns = getRunsFiles(pathExp, luffy, logAllRuns, optimaRuns, numberRuns)
                        if(parameters["LOG_ALL"] and layout.enableSS and logAllRuns):
                            lastGenSS = plotRunsSearchSpace(logAllRuns[0], layout, lastGenSS, parameters)
                            if(parameters["BENCHMARK"] != "CUSTOM"):
                                        runsDoneOP = plotOptimaSearchSpace(optimaRuns, layout, runsDoneOP)
                        runsDone = plotRuns(luffy, layout, runsDone)

            else:
                for run in runs:
                    abec(run['id'], run['seed'], pathExp, interface)
                    if interface:
                        layout.window.refresh()

            executionTime = (time.time() - startTime)
            #####################################
            # analisys of the results
            #####################################
            readme = open(f"{pathExp}/results/readme.txt", "a") # open file to write the outputs
            if parameters["ANALISYS"]:
                analysis(pathExp, parameters, executionTime, readme)

            #####################################
            # end of the experiment
            #####################################
            myPrint(f"[DATE: {date['month']:02}/{date['day']:02}/{date['year']} at {date['hour']:02}:{date['minute']:02}]", readme, parameters)
            myPrint("[END] Thx :)", readme, parameters)

            if(os.path.isfile(f"{pathExp}/savethedate.txt")):
                os.remove(f"{pathExp}/savethedate.txt")
            if(os.path.isfile(f"{pathExp}/printTmp.txt")):
                os.remove(f"{pathExp}/printTmp.txt")
            readme.write("\n\nAbEC developed by Alexandre Mascarenhas\n")
            readme.write("For more informations please go to https://abec-ec.github.io\n")
            readme.write("Eh nois")
            readme.close()
            if interface:
                layout.window["continueBT"].update(disabled=True)
                layout.window["resetBT"].update(disabled=False)
                layout.set(pathExp)
                if layout.reset:
                    continue
            else:
                break

        except Exception as e:
            while(True):
                x = 1
            logging.exception('Got exception on main handler')
            raise


if __name__ == "__main__":
    main()


