#!/usr/bin/env python3

'''
Base code for AbEC framework

Alexandre Mascarenhas

2023/1
'''
import itertools
import random
import datetime
import csv
import sys
import getopt
import time
import copy
import numbers
import logging
import json
import shutil
import numpy as np
import pandas as pd
from abec import abec
from deap import benchmarks
from tqdm import tqdm
import matplotlib.colors as mcolors
# AbEC files
import plot.currentError as ecPlot
import plot.offlineError as eoPlot
import plot.searchSpace as spPlot
import aux.globalVar as globalVar
import aux.fitFunction as fitFunction
import plot.rtPlot as rtPlot
import gui.gui as gui
from aux.aux import *
import optimizers.pso as pso
import optimizers.de as de
import optimizers.ga as ga
import optimizers.es as es
from metrics.offlineError import offlineError
from metrics.fillingRate import fillingRate

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
    layout.window["browseFit"].update(disabled=True)
    layout.window["program.sr"].update(False, visible=False)
    layout.window["program.ct"].update(False, visible=False)
    layout.window["program.aad"].update(False, visible=False)
    layout.window["continueBT"].update(disabled=False)
    layout.window["resetBT"].update(disabled=True)

def analysis(path, parameters, totalTime):
    # End of the optimization
    #print(len(runVars.sspace))
    #print(runVars.tot_pos)
    print("\n[RESULTS]")

    '''
    if layout:
        layout.window.refresh()
        try:
            print("\n[Press continue to calculate the metrics...]")
            layout.set()
        except SyntaxError:
            pass
    '''

    # Offline error
    df = pd.read_csv(f"{path}/results/results.csv")
    eo_mean = df["eo"].mean()
    meanTime = df["execTime"].mean()
    meanTimeStd = df["execTime"].std()
    #fr_mean = df["fr"].mean()
    #fr_std = df["fr"].std()

    if parameters["RUNS"] > 1:
        luffy = 0
        bestsPos = []

        eo_std = df["eo_std"].std()

        '''
        bests = [d["fit"] for d in globalVar.bestRuns]
        meanBest = np.mean(bests)
        stdBest = np.std(bests)
        bPos = [d["pos"] for d in globalVar.bestRuns]
        for i in range(len(bPos[0])):
            for j in range(len(bPos)):
                luffy += bPos[j][i]
            bestsPos.append(luffy/len(bPos))
            luffy = 0
        '''

        ecMean_csv = ecMean(f"{path}/results", parameters)
        eoMean_csv = eoMean(f"{path}/results", parameters)
        ecPlot.ecPlot(ecMean_csv, parameters, multi = 1, pathSave = f"{path}/results", name="ecMean")
        eoPlot.eoPlot(eoMean_csv, parameters, multi = 1, pathSave = f"{path}/results", name="eoMean")
    else:

        eo_std = df["eo_std"][0]   # If only one run just the number

        # get the run data file of the run
        flist = os.listdir(f"{path}/results")
        pdir = f"{path}/results/{sorted(flist)[0]}"
        runFile = f"{pdir}/{sorted(os.listdir(pdir))[-1]}"

        ecPlot.ecPlot(runFile, parameters, pathSave = f"{path}/results/0001")
        eoPlot.eoPlot(runFile, parameters, pathSave = f"{path}/results/0001")
        #frPlot.frPlot(f"{globalVar.path}/results/{parameters['ALGORITHM']}_01_{parameters['SEED']}", parameters, pathSave = f"{globalVar.path}/results")
        #spPlot.spPlot(f"{globalVar.path}/results/log_all_{globalVar.seedInit}", parameters, pathSave = f"{globalVar.path}/results")


    if parameters["DEBUG_RUN"]:
        files = os.listdir(f"{path}/results")
        print(f"\n[FILES GENERATED]\n")
        print(f"-[PATH] {path}/results/")
        files = sorted(files)
        for file in files:
            print(f"\t-[FILE] {file}")

        if parameters["RUNS"] > 1:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            # print(f"[BEST RUN POS : {globalVar.best['pos']}]")
            # print(f"[BEST RUN FIT : {globalVar.best['fit']}]")
            print(f"[POS MEAN: {bestsPos} ]")
            # print(f"[Ec  MEAN: {meanBest:.4f}({stdBest:.4f})]")
            #print(f"[Fr  MEAN: {fr_mean:.4f}({fr_std:.4f})]")
            print(f"[Eo  MEAN: {eo_mean:.4f}({eo_std:.4f})]")
        else:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            # print(f"[POS : {globalVar.best['pos']}]")
            # print(f"[Ec  : {globalVar.best['fit']:.4f}]")
            #print(f"[Fr  : {globalVar.Fr:.4f} %]")
            print(f"[Eo  : {eo_mean:.4f}({eo_std:.4f})]")

        print(f"[RUNTIME(s): {float(totalTime):.02f} | {meanTime:.02f}({meanTimeStd:.02f})/run]")
        print(f"==============================================")


    if(parameters["BEBC_ERROR"]):
        if (parameters["DEBUG_RUN"]):
            print("\n[METRICS]")
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {path} -d 1")
        else:
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {path}")


def checkRuns(path):
    df = pd.read_csv(f"{path}/results/results.csv")
    return df.shape[0]


def main():

    #####################################
    # log file for debbug
    #####################################
    #LOG_FILENAME = "./aux/log/log_last_run.txt"
    #logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    #logging.debug('This message should go to the log file')

    #####################################
    # start the framework
    #####################################
    while(True):
        try:
            # datetime variables
            cDate = datetime.datetime.now()
            globalVar.year = cDate.year
            globalVar.month = cDate.month
            globalVar.day = cDate.day
            globalVar.hour = cDate.hour
            globalVar.minute = cDate.minute
            globalVar.cleanGlobalVars()

            seed = globalVar.minute
            pathConfig = "."
            interface = 1



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

            print(f"\n\nAbEC running parameters:")
            print(f"Graphical Interface: {interface}\nPath: {pathConfig}\nSeed: {seed}\n")

            #####################################
            # load the parameter files
            #####################################
            parametersFiles = ["algoConfig.ini", "frameConfig.ini", "problemConfig.ini"]
            algoParameters, algo = algoConfig()
            parameters = algoParameters | frameConfig() | problemConfig()

            #Read the parameters from the config file
            for file in parametersFiles:
                if os.path.isfile(f"{pathConfig}/{file}"):
                    with open(f"{pathConfig}/{file}") as f:
                        p0 = list(json.loads(f.read()).items())
                        for i in range(len(p0)):
                            parameters[f"{p0[i][0]}"] = p0[i][1]

                else:
                    errorWarning(0.1, f"{file}", "FILE_NOT_FOUND", f"The {file} file is mandatory!")


            if parameters["SEED"] >= 0:
                seed = parameters["SEED"]

            #####################################
            # create the dis of the experiment
            #####################################
            if pathConfig == ".":
                pathExp = parameters["PATH"]
                checkCreateDir(pathExp)
            else:
                pathExp = pathConfig


            pathExp += f"/{parameters['ALGORITHM']}"
            pathExp = checkDirs(pathExp)

            # Copy the config.ini file to the experiment dir
            if(parameters["CONFIG_COPY"]):
                for file in parametersFiles:
                    shutil.copyfile(f"{pathConfig}/{file}", f"{pathExp}/{file}")

            if interface:
                if "layout" not in locals():
                    layout = gui.interface(parameters)
                    layout.launch(parameters)
                else:
                    layout.ax_pf = gui.configAxes(layout.ax_pf)
                    layout.ax_ss = gui.configAxes(layout.ax_ss, type = 2)
                    layout.reset = 0
                    initializeInterface(layout)
                    step = 0

            print(f"====================================================================================================")
            print(f"                               AbEC -> Ajustable Evolutionary Components        ")
            print(f"                                 A framework for Optimization Problems         ")
            print(f"====================================================================================================")
            print("*                                                                                                  *")
            print("*                                                                                                  *")
            print("*                                          I hope you enjoy!                                       *")
            print("*                                                                                                  *")
            print("*                                                                                                  *")
            if interface:
                try:
                    layout.window.refresh()
                    time.sleep(1)
                    layout.set(step = 0)
                    layout.window["-EXP-"].update(disabled=False)
                    layout.window["-ALGO-"].update(disabled=False)
                    layout.window["-PRO-"].update(disabled=False)
                    layout.window["resetBT"].update(disabled=False)
                    print("[Please check if the configuration files are ok and then press continue...]")
                    print("\n[ - Experiment configuration file: Framework parameters (e.g. number of runs, path of the files, number of evaluations, ...)]")
                    print("\n[ - Algorithm configuration file: Functioning of the algorithm itself (e.g. Population size, optimizers, ...)]")
                    print("\n[ - Problem configuration file: e.g. number of dimensions, dynamic or not, ...]")
                    layout.set()
                    if layout.reset:
                        continue
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    print("[Loading configuration files...]")
                    layout.window.refresh()
                except SyntaxError:
                    pass


            if interface:
                layout.window["-EXP-"].update(disabled=True)
                layout.window["-ALGO-"].update(disabled=True)
                layout.window["-PRO-"].update(disabled=True)
                #layout.ax_pf.set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])
                layout.ax_pf[0].set_xlim(0, parameters["FINISH_RUN_MODE_VALUE"])

            bench = parameters["BENCHMARK"].upper()

            if interface and bench == "CUSTOM":
                try:
                    time.sleep(1)
                    print("[Loaded]\n")
                    layout.window.refresh()
                    time.sleep(0.3)
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    layout.window["browseFit"].update(disabled=False)
                    print("[Input the fitness function file and press continue...]")
                    print("\n[ - The function should be defined in a python script, which will evaluate the solutions of the algorithm]")
                    layout.set()
                    if layout.reset:
                        continue
                    layout.window["-OUTPUT-"].update("")
                    layout.window.refresh()
                    print("[Loading Fitness Function file...]")
                    layout.window["browseFit"].update(disabled=True)
                    layout.window.refresh()
                except SyntaxError:
                    pass


            if interface:
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
                print(f"[ALGORITHM SETUP]")
                print(f"- Name: {parameters['ALGORITHM']}")
                print(f"- Individuals p/ population:\t{parameters['POPSIZE']}")

                print(f"- [OPTIMIZERS]:")
                for opt in algo.optimizers:
                    print(f"-- [{opt[0]}]")
                    value = parameters[f"{opt[0]}_POP_PERC"]
                    print(f"---- % of POP: {value*100}%")
                    for i in opt[1].params:
                        value = parameters[f"{opt[0]}_{i}"]
                        print(f"---- {i}: {value}")

                print()
                print(f"- [COMPONENTS]:")
                for comp in algo.components:
                    print(f"-- [{comp[0]}]")
                    print(f"---- SCOPE: {comp[1].scope[0]}")
                    for i in comp[1].params:
                        value = parameters[f"COMP_{comp[0]}_{i}"]
                        print(f"---- {i}: {value}")

                print()
                print(f"[FRAMEWORK SETUP]")
                print(f"- RUNS:\t\t {parameters['RUNS']}")
                if parameters["FINISH_RUN_MODE"] == 0:
                    print(f"- NEVALS p/ RUN: {parameters['FINISH_RUN_MODE_VALUE']}")
                else:
                    print(f"- Target error: {parameters['FINISH_RUN_MODE_VALUE']}")
                print(f"- SEED:\t\t {parameters['SEED']}")

                print()
                print(f"[PROBLEM SETUP]")
                if parameters["BENCHMARK"] == "NONE":
                    print(f"- Name: Fitness Function")
                else:
                    print(f"- Name: {parameters['BENCHMARK']}")
                print(f"- NDIM: {parameters['NDIM']}")

            if interface:
                try:
                    layout.window.refresh()
                    print("\n[Press continue to start...]")
                    layout.set()
                    if layout.reset:
                        continue
                    layout.window["resetBT"].update(disabled=True)
                    layout.window.refresh()
                except SyntaxError:
                    pass

            # Create a list with the runs, seeds and if it is done or not
            # to allow the parallelization
            runs = [{"id": run+1, "seed": int(parameters["SEED"] + run), "done":0} for run in range(parameters["RUNS"])]

            header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "ec", "eo", "eo_std", "fr", "fr_std", "execTime"]
            filename = f"{pathExp}/results/results.csv"

            # Headers of the log files
            writeLog(mode=0, filename=filename, header=header)

            #####################################
            # Main loop of the runs
            #####################################
            if parameters["DEBUG_RUN"]:
                print("\n[RUNNING]\n")
                print(f"RUN | GEN | NEVALS |                    BEST                   | ERROR")

            startTime = time.time()
            if parameters["PARALLELIZATION"]:
                for run in runs:
                    os.system(f"./abec.py -r {run['id']} -s {run['seed']} -p {pathExp} -i {interface} &")
            else:
                for run in runs:
                    if interface:
                        abec(algo, parameters, run, layout)
                    else:
                        abec(algo, parameters, run)

            progressBar = 0
            if progressBar:
                #progress_bar = tqdm(total=total_gen, desc=f"Run {runVars.id():02d}... ")
                progress_bar = tqdm(total=len(runs))
                progress_bar.update()
            rdOld = 0

            #####################################
            # wait for the runs fininsh
            #####################################
            while True:
                runsDone = checkRuns(pathExp)
                if not interface and progressBar:
                    if runsDone != rdOld:
                        progress_bar.update(1)
                        rdOld = runsDone

                if runsDone >= len(runs):
                    break
                else:
                    time.sleep(0.2)

            executionTime = (time.time() - startTime)

            if progressBar:
                progress_bar.close()

            #####################################
            # analisys of the results
            #####################################
            analysis(pathExp, parameters, executionTime)

            #####################################
            # end of the experiment
            #####################################
            print("[END]\nThx :)")
            if interface:
                layout.window["continueBT"].update(disabled=True)
                layout.window["resetBT"].update(disabled=False)
                layout.set()
                if layout.reset:
                    continue
            else:
                break

        except Exception as e:
            logging.exception('Got exception on main handler')
            raise


if __name__ == "__main__":
    main()


