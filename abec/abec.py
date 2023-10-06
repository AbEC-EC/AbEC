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


def updateBest(ind, best):
    '''
    Update the global best individual
    '''
    #print(f"ind type: {type(ind)} {ind['pop_id']} {ind['id']} {ind['fit']} {globalVar.nevals}")
    #print(f"best type: {type(best)} {best['fit']}")
    if not isinstance(best["fit"], numbers.Number) or (best["fit"] > ind["fit"]): # If first gen, just copy the ind
        best = ind.copy()

    '''
    Update the ind best
    '''
    if not isinstance(ind["best_fit"], numbers.Number) or (ind["best_fit"] > ind["fit"]): # If first gen, just copy the ind
        ind["best_fit"] = ind["fit"]
        ind["best_pos"] = ind["pos"]

    return ind, best



def evaluate(x, runVars, parameters, be = 0):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''
    
    position = []
    for i in x["pos"]:
        pos = round(i, runVars.res)
        position.append(pos)
    if position not in runVars.sspace:
        runVars.sspace.append(position)
    runVars.Fr = (len(runVars.sspace)/runVars.tot_pos)*100
    #print(globalVar.sspace)
    #print(globalVar.Fr)

    # If a dynamic problem, there will be changes in the env

    if not parameters["CHANGES"] or runVars.changeEV:
        x["fit"], runVars = fitFunction.fitnessFunction(x['pos'], runVars, parameters)
        runVars.nevals += 1
    else:
        if x["fit"] == "NaN":
            print(f"{x}")
        if not be:
            return x, runVars
        else:
            return x["fit"], runVars

    if not be: # If it is a best evaluation does not log

        if parameters["OFFLINE_ERROR"] and isinstance(runVars.best["fit"], numbers.Number):
            runVars.eo_sum += runVars.best["fit"]

        x["ae"] = 1 # Set as already evaluated

        if parameters["LOG_ALL"]:
            log = [{"run": runVars.id(), "gen": runVars.gen, "nevals": runVars.nevals, \
                "popId": x["pop_id"], "indId": x["id"], "type": x["type"], "indPos": x["pos"], \
                "indVel": x["vel"], "indBestPos": x["best_pos"], "indBestFit": x["best_fit"], \
                "indFit": x["fit"], \
                "globalBestId": runVars.best["id"], "globalBestPos": runVars.best["pos"], \
                "globalBestFit": runVars.best["fit"]}]
            writeLog(mode=1, filename=runVars.filename_LA, header=runVars.header_LA, data=log)

        return x, runVars

    else:

        return x["fit"], runVars



class population():
    '''
        Class of the population
    '''
    # Get a new id for the population
    newid = itertools.count(1).__next__

    def __init__(self, parameters, id = 1, fill = 1):
        if(id == 0):    # Temporary population doesnt have an id
            self.id = 0
        else:
            if globalVar.npops > 1:
                self.id = population.newid() - ((globalVar.run-1)*globalVar.npops)
            else:
                self.id = population.newid()

        self.popsize = parameters["POPSIZE"]

        self.change = 0

        self.ind = []
        if fill == 1:
            for i in range(1, parameters["POPSIZE"]+1):
                self.addInd(parameters, i)

        self.best = self.createInd(parameters, 0)

    def createInd(self, parameters, ind_id=-1):
        attr = {"pop_id": self.id, \
                "id": ind_id, \
                "type": "NaN", \
                "pos": [0 for _ in range(parameters["NDIM"])], \
                "vel": [0 for _ in range(parameters["NDIM"])], \
                "best_pos": [0 for _ in range(parameters["NDIM"])], \
                "best_fit": "NaN", \
                "fit": "NaN", \
                "ae": 0 \
                }
        return attr

    def addInd(self, parameters, ind_id=-1):
        flag = 0
        ids = [d["id"] for d in self.ind]
        while flag == 0:
            if ind_id in ids:  # If id is already in the population go to next
                ind_id += 1
            else:
                flag = 1
        self.ind.append(self.createInd(parameters, ind_id))

    def resetId():
        population.newid = itertools.count(1).__next__    # Get a new id for the population


def createPopulation(algo, runVars, parameters):
    '''
        This function is to create the populations and individuals
    '''
    pop = []

    for i in range(len(algo.comps_initialization)):
        pop = algo.comps_initialization[i].component(pop, parameters)

    if not pop:
        pop.append(population(parameters))
        runVars.randomInit = [0]

    best = pop[0].ind[0].copy()
    best["id"] = "NaN"

    for subpop in pop:
        flag = 0
        for opt in algo.optimizers:
            for i in range(flag, len(subpop.ind)):
                if subpop.ind[i]["id"] <= int(parameters[f"{opt[0]}_POP_PERC"]*parameters["POPSIZE"]+flag):
                    subpop.ind[i]["type"] = opt[0]
                else:
                    flag = subpop.ind[i]["id"]-1
                    break

    return pop, best, runVars


def randInit(pop, runVars, parameters):
    '''
        Random initialization of the individuals
    '''
    #print(f"REINIT {subpop.id}")
    for ind in pop.ind:
        ind["pos"] = [float(runVars.rng.choice(range(parameters['MIN_POS'], parameters['MAX_POS']))) for _ in range(parameters["NDIM"])]
        if ind["type"] == "PSO":
            ind["vel"] = [float(runVars.rng.choice(range(parameters["PSO_MIN_VEL"], parameters["PSO_MAX_VEL"]))) for _ in range(parameters["NDIM"])]
    pop.best = pop.ind[0].copy()
    return pop, runVars



def evaluatePop(pop, best, runVars, parameters):
    '''
    Reevaluate each particle attractor and update swarm best
    If ES_CHANGE_COMP is activated, the position of particles is
    changed by ES strategy
    '''
    for ind in pop.ind:
        if ind["ae"] == 0:
            ind, runVars = evaluate(ind, runVars, parameters)
            '''
            for i, d in enumerate(ind["pos"]):
                ind["pos"][i] = round(d, 4)
            '''
            ind, best = updateBest(ind, best)

    pop.ind = sorted(pop.ind, key = lambda x:x["fit"])
    pop.best = pop.ind[0].copy()

    return pop, best, runVars


def finishRun(runVars, parameters):
    if parameters["FINISH_RUN_MODE"] == 0:
        if (runVars.nevals < (parameters["FINISH_RUN_MODE_VALUE"]-parameters["POPSIZE"])+1):
            return 0
        else:
            return 1
    else:
        if runVars.best["fit"] > parameters["FINISH_RUN_MODE_VALUE"]:
            return 0
        else:
            return 1


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

class runVariables():
    def __init__(self, run, parameters):
        self.__id = run["id"]
        self.__seed = run["seed"]
        self.done = run["done"]
        self.rng = np.random.default_rng(self.__seed)
        self.gen = 0
        self.nevals = 0
        self.pop = []
        self.best = None
        self.sspace = []
        self.randomInit = [0]
        self.mpb = None
        self.peaks = 0
        self.eo_sum = 0
        self.Fr = 0
        self.res = 2
        self.flagChangeEnv = 0
        self.tot_pos = (parameters["MAX_POS"]-parameters["MIN_POS"])**parameters["NDIM"] * (10**globalVar.res)
        self.startTime = 0
        self.bestRuns = []
        self.header_RUN = ["gen", "nevals", "bestId", "bestPos", "ec", "eo", "fr", "env"]  
        self.filename_RUN = ""
        self.header_LA = ["run", "gen", "nevals", "popId", "indId", "type", "indPos", "indVel", "indBestPos", "indBestFit", "indFit", "globalBestId", "globalBestPos", "globalBestFit"]
        self.filename_LA = ""
        self.header_OPT = [f"opt{i}" for i in range(parameters["NPEAKS_MPB"])]
        self.filename_OPT = ""
        self.genChangeEnv = 0
        self.env = 0
        self.flagEnv = 0
        self.Eo = 0
        self.Fr = 0
        self.change = 0
        self.rtPlotNevals = []
        self.rtPlotError = []
        self.rtPlotEo = []
        self.rtPlotFr = []
    
    def id(self):
        return self.__id
    
    def seed(self):
        return self.__seed
    

'''
Framework
'''
def abec(algo, parameters, run, layout = 0):

    runVars = runVariables(run, parameters)
        #Initialize the logs
    checkCreateDir(f"{globalVar.path}/results/{runVars.id():04}") # Check if the run dir exists, if not, create it
    runVars.filename_LA = f"{globalVar.path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{globalVar.year}{globalVar.month:02}{globalVar.day:02}_{globalVar.hour:02}{globalVar.minute:02}_{runVars.id():04}_{runVars.seed()}_LOGALL.csv"
    runVars.filename_OPT = f"{globalVar.path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{globalVar.year}{globalVar.month:02}{globalVar.day:02}_{globalVar.hour:02}{globalVar.minute:02}_{runVars.id():04}_{runVars.seed()}_OPTIMA.csv"
    runVars.filename_RUN = f"{globalVar.path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{globalVar.year}{globalVar.month:02}{globalVar.day:02}_{globalVar.hour:02}{globalVar.minute:02}_{runVars.id():04}_{runVars.seed()}_RUN.csv"
    if(parameters["LOG_ALL"]):
        writeLog(mode=0, filename=runVars.filename_LA, header=runVars.header_LA)
    writeLog(mode=0, filename=runVars.filename_OPT, header=runVars.header_OPT)
    writeLog(mode=0, filename=runVars.filename_RUN, header=runVars.header_RUN)

    
    if parameters["DEBUG_RUN_2"]:
        print(f"\n==============================================")
        print(f"[START][RUN:{runVars.id():02}]\n[NEVALS:{runVars.nevals:06}]")
        print(f"==============================================")

    runVars.startTime = time.time()
    # Create the population with POPSIZE individuals
    runVars.pop, runVars.best, runVars = createPopulation(algo, runVars, parameters)

    #####################################
    # For each subpop in pop do the job
    #####################################
    for subpop_i, subpop in enumerate(runVars.pop):
        
        subpop, runVars = randInit(subpop, runVars, parameters)

        # Evaluate all the individuals in the pop and update the bests
        subpop, runVars.best, runVars = evaluatePop(subpop, runVars.best, runVars, parameters)
        for ind_i, ind in enumerate(subpop.ind):
            ind["ae"] = 0
            # Debug in individual level
            if parameters["DEBUG_IND"]:
                print(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]")
                
            subpop.ind[ind_i] = copy.deepcopy(subpop.ind[ind_i]) # Apply the changes to the ind
            
        runVars.pop[subpop_i] = copy.deepcopy(runVars.pop[subpop_i]) # Apply the changes to the subpop

    runVars.gen += 1  # First generation
    runVars.Eo = runVars.eo_sum/runVars.nevals  # Offline error
    
    log = [{"gen": runVars.gen, "nevals":runVars.nevals, "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "ec": runVars.best["fit"], "eo": runVars.Eo, "fr": runVars.Fr, "env": runVars.env}]
    writeLog(mode=1, filename=runVars.filename_RUN, header=runVars.header_RUN, data=log)

    # Graphic interface
    if layout:
        #Lists for real time graphs
        runVars.rtPlotNevals.append(runVars.nevals)
        runVars.rtPlotError.append(runVars.best["fit"])
        runVars.rtPlotEo.append(runVars.Eo)
        runVars.rtPlotFr.append(runVars.Fr)

        layout.window.refresh()
        if layout.enablePF:
            layout.run(runVars.rtPlotNevals, runVars.rtPlotError, runVars.rtPlotEo)
        if layout.enableSS:
            xSS, ySS = getSearchSpace(subpop, layout)
            layout.run(x = xSS, y1 = ySS, type = 2)

    #####################################
    # Debug in pop and generation level
    #####################################
    
    if parameters["DEBUG_GEN"]:
        #print(f"[RUN:{runVars.run:02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}][Eo: {Eo:.04f}]")
        print(f"[RUN {runVars.id():02}][GEN {runVars.gen:04}][NE {runVars.nevals:06}][POP {runVars.best['pop_id']:02}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}]")
        
    if parameters["DEBUG_POP"]:
        for subpop in runVars.pop:
            print(f"[POP {subpop.id:04}][BEST {subpop.best['id']:04}: {subpop.best['pos']} ERROR:{subpop.best['fit']}]")
 
    ###########################################################################
    # LOOP UNTIL FINISH THE RUN
    ###########################################################################

    if not layout:
        total_gen = int(parameters["FINISH_RUN_MODE_VALUE"]/(parameters["POPSIZE"]*len(runVars.pop)))
        progress_bar = tqdm(total=total_gen, desc=f"Run {runVars.id():02d}... ")
        progress_bar.update(1)
    while finishRun(runVars, parameters) == 0:
        if not layout:
            progress_bar.update(1)
        '''
        for subpop in pop:
            print(subpop.ind[0])
            subpop.ind[0]["pos"] = [51.97040, 61.228639]
            evaluate(subpop.ind[0], parameters)
            print(subpop.ind[0])
            e()
        '''

        ###########################################
        # Apply the Global Diversity Components
        ###########################################
        for i in range(len(algo.comps_global["GDV"])):
            runVars.randomInit = algo.comps_global["GDV"][i].component(runVars.pop, parameters, runVars.randomInit)

        #print(runVars.randomInit)
        for id, i in enumerate(runVars.randomInit, 0):
            if i:
                runVars.pop[id], runVars = randInit(runVars.pop[id], runVars, parameters)
                runVars.randomInit[id] = 0

        ###########################################
        # Apply the Global Exploration Components
        ###########################################

        for i in range(len(algo.comps_global["GER"])):
            runVars.pop = algo.comps_global["GER"][i].component(runVars.pop, parameters)


        ###########################################
        # Apply the Global Exploitation Components
        ###########################################

        for i in range(len(algo.comps_global["GET"])):
            runVars.best = algo.comps_global["GET"][i].component(runVars.best, parameters)


        # Verification if all pop were reeavluated after change
        if parameters["CHANGES"]:
            sumPops = 0
            for subpop in runVars.pop:
                sumPops += subpop.change

            #print(f"sumpops: {sumPops} {runVars.nevals} {len(pop)}")
            if sumPops == len(runVars.pop):
                for subpop in runVars.pop:
                    subpop.change = 0
                runVars.change = 0
                #print("CABOU")

        for subpop_i, subpop in enumerate(runVars.pop):

            # Change detection component in the environment
            if runVars.change:
                #print(f"Change: {runVars.nevals}")
                runVars.best["fit"] = "NaN"
                runVars.changeEV = 1
                if subpop.change == 0:
                    runVars.pop, runVars.best = evaluatePop(runVars.pop, runVars.best, parameters)
                    subpop.change = 1
                    if flagEnv == 0:
                        env += 1
                        genChangeEnv = runVars.gen
                        flagEnv = 1
                    for ind_i, ind in enumerate(subpop.ind):
                        ind["ae"] = 0 # Allow new evaluation
                        subpop.ind[ind_i] = copy.deepcopy(subpop[ind_i])
                    continue

            #####################################
            # Apply the optimizers in the pop
            #####################################

            if i in range(len(algo.opts)):
                subpop, runVars = algo.opts[i].optimizer(subpop, runVars.best, runVars, parameters)

            ###########################################
            # Apply the Local Exploration Components
            ###########################################

            for i in range(len(algo.comps_local["LER"])):
                subpop = algo.comps_local["LER"][i].component(runVars.pop, parameters)

            ###########################################
            # Apply the Local Exploitation Components
            ###########################################


            # Evaluate all the individuals that have no been yet in the subpop and update the bests
            subpop, runVars.best, runVars = evaluatePop(subpop, runVars.best, runVars, parameters)

            if layout:
                layout.ax_ss.scatter(subpop.best['pos'][0], subpop.best['pos'][1], c="white", s=0.5)
                
            for ind_i, ind in enumerate(subpop.ind):
                ind["ae"] = 0 # Allow new evaluation
                # Debug in individual level
                if parameters["DEBUG_IND"]:
                    print(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]")
                    
                subpop.ind[ind_i] = copy.deepcopy(subpop.ind[ind_i])
                    
            runVars.pop[subpop_i] = copy.deepcopy(runVars.pop[subpop_i])


        runVars.change = 0  # The generation is over so reset the change flag
        runVars.flagEnv = 0
        runVars.gen += 1
        #if abs(runVars.gen - runVars.genChangeEnv) >= 1:
            #runVars.change = 0

        #####################################
        # Save the log only with the bests of each generation
        #####################################

        runVars.Eo = runVars.eo_sum/runVars.nevals  # Calculate the offline error
        log = [{"gen": runVars.gen, "nevals":runVars.nevals, "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "ec": runVars.best["fit"], "eo": runVars.Eo, "fr": runVars.Fr, "env": runVars.env}]
        writeLog(mode=1, filename=runVars.filename_RUN, header=runVars.header_RUN, data=log)


        # Graphic interface
        if layout:
            #Lists for real time graphs
            runVars.rtPlotNevals.append(runVars.nevals)
            runVars.rtPlotError.append(runVars.best["fit"])
            runVars.rtPlotEo.append(runVars.Eo)
            runVars.rtPlotFr.append(runVars.Fr)

            layout.window.refresh()
            if layout.enablePF:
                layout.run(runVars.rtPlotNevals, runVars.rtPlotError, runVars.rtPlotEo, r = runVars.id())
            if layout.enableSS:
                xSS, ySS = getSearchSpace(runVars.pop, layout)
                layout.ax_ss.scatter(runVars.best["pos"][0], runVars.best["pos"][1], c="red", s=50 )
                layout.run(x = xSS, y1 = ySS, type = 2)

        #####################################
        # Debug in subpop and generation level
        #####################################

        if parameters["DEBUG_POP"]:
            for subpop in runVars.pop:
                print(f"[POP {subpop.id:04}][BEST {subpop.best['id']:04}: {subpop.best['pos']} ERROR:{subpop.best['fit']}]")

        if parameters["DEBUG_GEN"]:
            print(f"[RUN:{runVars.id():02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}][Eo: {runVars.Eo:.04f}]")


    #####################################
    # End of the run
    #####################################
    executionTime = (time.time() - runVars.startTime)
    progress_bar.close()
    globalVar.bestRuns.append(runVars.best)
    if runVars.id() == 1 or runVars.best["fit"] < globalVar.best["fit"]:
        globalVar.best = copy.deepcopy(runVars.best)
    runVars.eo = offlineError(f"{runVars.filename_RUN}")
    #fr = fillingRate(f"{runVars.path}/results/{parameters['ALGORITHM']}_{runVars.run:02d}_{parameters['SEED']}.csv")
    #df = pd.read_csv(f"{runVars.path}/results/results.csv")
    #log = [{"run": runVars.run, "gen": runVars.gen, "nevals":runVars.nevals, "popId": runVars.best["pop_id"], "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "ec": runVars.best["fit"], "eo": eo[0], "eo_std": eo[1], "fr":fr[0], "fr_std":fr[1]}]
    log = [{"run": runVars.id(), "gen": runVars.gen, "nevals":runVars.nevals, "popId": runVars.best["pop_id"], "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "ec": runVars.best["fit"], "eo": runVars.eo[0], "eo_std": runVars.eo[1], "execTime": executionTime}]
    writeLog(mode=1, filename=globalVar.filename, header=globalVar.header, data=log)

    if parameters["DEBUG_RUN"]:
        #print(f"[RUN:{runVars.run:02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.4f}][Eo:{Eo:.4f}]")
        pos = []
        for p in runVars.best["pos"]:
            pos.append(float(f"{p:.2f}"))
        print(f"{runVars.id():02}   {runVars.gen:05}  {runVars.nevals:06}  {runVars.best['id']:04}:{pos}  {runVars.best['fit']:.04f}")
    if parameters["DEBUG_RUN_2"]:
        print(f"\n==============================================")
        print(f"[RUN:{runVars.id():02}]\n[GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}]")
        print(f"[BEST: IND {runVars.best['id']:04} from POP {runVars.best['pop_id']:04}")
        print(f"    -[POS: {runVars.best['pos']}]")
        print(f"    -[Error: {runVars.best['fit']}]")
        print(f"[RUNTIME: {str(executionTime)} s]")
        print(f"==============================================")


    runVars.npops = len(runVars.pop)




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

def analysis(parameters):
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
    df = pd.read_csv(f"{globalVar.path}/results/results.csv")
    eo_mean = df["eo"].mean()
    totalTime = df["execTime"].sum()
    #fr_mean = df["fr"].mean()
    #fr_std = df["fr"].std()

    if parameters["RUNS"] > 1:
        luffy = 0
        bestsPos = []

        eo_std = df["eo_std"].std()

        bests = [d["fit"] for d in globalVar.bestRuns]
        meanBest = np.mean(bests)
        stdBest = np.std(bests)
        bPos = [d["pos"] for d in globalVar.bestRuns]
        for i in range(len(bPos[0])):
            for j in range(len(bPos)):
                luffy += bPos[j][i]
            bestsPos.append(luffy/len(bPos))
            luffy = 0

        ecMean_csv = ecMean(f"{globalVar.path}/results", parameters)
        eoMean_csv = eoMean(f"{globalVar.path}/results", parameters)
        ecPlot.ecPlot(ecMean_csv, parameters, multi = 1, pathSave = f"{globalVar.path}/results", name="ecMean")
        eoPlot.eoPlot(eoMean_csv, parameters, multi = 1, pathSave = f"{globalVar.path}/results", name="eoMean")
    else:

        eo_std = df["eo_std"][0]   # If only one run just the number
        # get the run data file of the run
        flist = os.listdir(f"{globalVar.path}/results")
        pdir = f"{globalVar.path}/results/{sorted(flist)[0]}"
        runFile = f"{pdir}/{sorted(os.listdir(pdir))[-1]}"
        ecPlot.ecPlot(runFile, parameters, pathSave = f"{globalVar.path}/results/0001")
        eoPlot.eoPlot(runFile, parameters, pathSave = f"{globalVar.path}/results/0001")
        #frPlot.frPlot(f"{globalVar.path}/results/{parameters['ALGORITHM']}_01_{parameters['SEED']}", parameters, pathSave = f"{globalVar.path}/results")
        #spPlot.spPlot(f"{globalVar.path}/results/log_all_{globalVar.seedInit}", parameters, pathSave = f"{globalVar.path}/results")


    if parameters["DEBUG_RUN"]:
        files = os.listdir(f"{globalVar.path}/results")
        print(f"\n[FILES GENERATED]\n")
        print(f"-[PATH] {globalVar.path}/results/")
        files = sorted(files)
        for file in files:
            print(f"\t-[FILE] {file}")

        if parameters["RUNS"] > 1:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            print(f"[BEST RUN POS : {globalVar.best['pos']}]")
            print(f"[BEST RUN FIT : {globalVar.best['fit']}]")
            print(f"[POS MEAN: {bestsPos} ]")
            print(f"[Ec  MEAN: {meanBest:.4f}({stdBest:.4f})]")
            #print(f"[Fr  MEAN: {fr_mean:.4f}({fr_std:.4f})]")
            print(f"[Eo  MEAN: {eo_mean:.4f}({eo_std:.4f})]")
        else:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            print(f"[POS : {globalVar.best['pos']}]")
            print(f"[Ec  : {globalVar.best['fit']:.4f}]")
            #print(f"[Fr  : {globalVar.Fr:.4f} %]")
            print(f"[Eo  : {eo_mean:.4f}({eo_std:.4f})]")

        print(f"[RUNTIME: {str(totalTime)} s]")
        print(f"==============================================")


    if(parameters["BEBC_ERROR"]):
        if (parameters["DEBUG_RUN"]):
            print("\n[METRICS]")
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {globalVar.path} -d 1")
        else:
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {globalVar.path}")


def main():
    LOG_FILENAME = "./aux/log/log_last_run.txt"
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    logging.debug('This message should go to the log file')
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
            interface = 1
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
                        globalVar.path = arg

            print(f"\n\nAbEC running parameters:")
            print(f"Graphical Interface: {interface}\nPath: {globalVar.path}\nSeed: {seed}\n")

            parameters0, algo = algoConfig()
            parameters1 = frameConfig()
            parameters2 = problemConfig()

            parameters = parameters0 | parameters1 | parameters2

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


           # Read the parameters from the config file
            if os.path.isfile(f"{globalVar.path}/algoConfig.ini"):
                with open(f"{globalVar.path}/algoConfig.ini") as f:
                    p0 = list(json.loads(f.read()).items())
                    for i in range(len(p0)):
                        #print(p0[i][0])
                        parameters0[f"{p0[i][0]}"] = p0[i][1]
            else:
                errorWarning(0.1, "algoConfig.ini", "FILE_NOT_FIND", "The algoConfig.ini file is mandatory!")

            if os.path.isfile(f"{globalVar.path}/frameConfig.ini"):
                with open(f"{globalVar.path}/frameConfig.ini") as f:
                    p1 = list(json.loads(f.read()).items())
                    for i in range(len(p1)):
                        #print(p1[i][0])
                        parameters1[f"{p1[i][0]}"] = p1[i][1]

            if os.path.isfile(f"{globalVar.path}/problemConfig.ini"):
                with open(f"{globalVar.path}/problemConfig.ini") as f:
                    p2 = list(json.loads(f.read()).items())
                    for i in range(len(p2)):
                        #print(p2[i][0])
                        parameters2[f"{p2[i][0]}"] = p2[i][1]

            parameters = parameters0 | parameters1 | parameters2

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


            algo = updateAlgo(algo, parameters)

            '''
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
            '''

            if parameters["SEED"] >= 0:
                seed = parameters["SEED"]

            if globalVar.path == ".":
                if not os.path.isdir(f"{parameters['PATH']}"):
                    os.mkdir(f"{parameters['PATH']}")
                globalVar.path = f"{parameters['PATH']}/{parameters['ALGORITHM']}"
            globalVar.path = checkDirs(globalVar.path)


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
            globalVar.runs = [{"id": run+1, "seed": int(parameters["SEED"] + run), "done":0} for run in range(parameters["RUNS"])]
            globalVar.seedInit = parameters["SEED"]
            print(globalVar.runs)
                               
            globalVar.header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "ec", "eo", "eo_std", "fr", "fr_std", "execTime"]
            globalVar.filename = f"{globalVar.path}/results/results.csv"

            # Headers of the log files
            writeLog(mode=0, filename=globalVar.filename, header=globalVar.header)

            #####################################
            # Main loop of the runs
            #####################################
            if parameters["DEBUG_RUN"]:
                print("\n[RUNNING]\n")
                print(f"RUN | GEN | NEVALS |                    BEST                   | ERROR")
            for run in globalVar.runs:
                if interface:
                    abec(algo, parameters, run, layout)
                else:
                    abec(algo, parameters, run)

            # Analysis of the results            
            analysis(parameters)
            
            # Copy the config.ini file to the experiment dir
            if(parameters["CONFIG_COPY"]):
                f = open(f"{globalVar.path}/algoConfig.ini","w")
                f.write(json.dumps(parameters0))
                f.close()
                f = open(f"{globalVar.path}/frameConfig.ini","w")
                f.write(json.dumps(parameters1))
                f.close()
                f = open(f"{globalVar.path}/problemConfig.ini","w")
                f.write(json.dumps(parameters2))
                f.close()
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


