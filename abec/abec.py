#! /usr/bin/env python3

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
import numbers
import json
import shutil
import numpy as np
import pandas as pd
from deap import benchmarks
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

# datetime variables
cDate = datetime.datetime.now()
year = cDate.year
month = cDate.month
day = cDate.day
hour = cDate.hour
minute = cDate.minute

#nevals = 0



def updateBest(ind, best):
    '''
    Update the global best individual
    '''
    if not isinstance(best["fit"], numbers.Number) or (best["fit"] > ind["fit"]): # If first gen, just copy the ind
        best = ind.copy()

    '''
    Update the ind best
    '''
    if not isinstance(ind["best_fit"], numbers.Number) or (ind["best_fit"] > ind["fit"]): # If first gen, just copy the ind
        ind["best_fit"] = ind["fit"]
        ind["best_pos"] = ind["pos"]

    return ind, best



def evaluate(x, parameters, be = 0):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''
    header_LA = ["run", "gen", "nevals", "popId", "indId", "type", "indPos", "indVel", "indBestPos", "indBestFit", "indFit", "globalBestId", "globalBestPos", "globalBestFit"]
    filename_LA = f"{globalVar.path}/results/log_all_{globalVar.seedInit}.csv"

    x["fit"] = fitFunction.fitnessFunction(x['pos'], parameters)
    globalVar.nevals += 1

    if not be: # If it is a best evaluation does not log

        if parameters["OFFLINE_ERROR"] and isinstance(globalVar.best["fit"], numbers.Number):
            globalVar.eo_sum += globalVar.best["fit"]

        x["ae"] = 1 # Set as already evaluated

        if parameters["LOG_ALL"]:
            log = [{"run": globalVar.run, "gen": globalVar.gen, "nevals": globalVar.nevals, \
                "popId": x["pop_id"], "indId": x["id"], "type": x["type"], "indPos": x["pos"], \
                "indVel": x["vel"], "indBestPos": x["best_pos"], "indBestFit": x["best_fit"], \
                "indFit": x["fit"], \
                "globalBestId": globalVar.best["id"], "globalBestPos": globalVar.best["pos"], \
                "globalBestFit": globalVar.best["fit"]}]
            writeLog(mode=1, filename=filename_LA, header=header_LA, data=log)

        return x

    else:

        return x["fit"]



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



def createPopulation(algo, parameters):
    '''
        This function is to create the populations and individuals
    '''
    pop = []

    for i in range(len(algo.comps_initialization)):
        pop = algo.comps_initialization[i].component(pop, parameters)

    if not pop:
        pop.append(population(parameters))
        globalVar.randomInit = [0]

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

    return pop, best


def randInit(pop, parameters):
    '''
        Random initialization of the individuals
    '''
    for ind in pop.ind:
        ind["pos"] = [float(globalVar.rng.choice(range(parameters['MIN_POS'], parameters['MAX_POS']))) for _ in range(parameters["NDIM"])]
        if ind["type"] == "PSO":
            ind["vel"] = [float(globalVar.rng.choice(range(parameters["PSO_MIN_VEL"], parameters["PSO_MAX_VEL"]))) for _ in range(parameters["NDIM"])]
    return pop



def evaluatePop(pop, best, parameters):
    '''
    Reevaluate each particle attractor and update swarm best
    If ES_CHANGE_COMP is activated, the position of particles is
    changed by ES strategy
    '''
    for ind in pop.ind:
        if ind["ae"] == 0:
            ind = evaluate(ind, parameters)
            '''
            for i, d in enumerate(ind["pos"]):
                ind["pos"][i] = round(d, 4)
            '''
            ind, best = updateBest(ind, best)

    pop.ind = sorted(pop.ind, key = lambda x:x["fit"])
    pop.best = pop.ind[0].copy()

    return pop, best


def finishRun(parameters):
    if parameters["FINISH_RUN_MODE"] == 0:
        if (globalVar.nevals < (parameters["FINISH_RUN_MODE_VALUE"]-parameters["POPSIZE"])+1):
            return 0
        else:
            return 1
    else:
        if globalVar.best["fit"] > parameters["FINISH_RUN_MODE_VALUE"]:
            return 0
        else:
            return 1


'''
Framework
'''
def abec(algo, parameters, seed, layout = 0):
    startTime = time.time()

    globalVar.seedInit = parameters["SEED"]
    header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "ec", "eo", "eo_std"]
    filename = f"{globalVar.path}/results/results.csv"
    header_RUN = ["gen", "nevals", "bestId", "bestPos", "ec", "eo", "env"]
    header_LA = ["run", "gen", "nevals", "popId", "indId", "type", "indPos", "indVel", "indBestPos", "indBestFit", "indFit", "globalBestId", "globalBestPos", "globalBestFit"]
    filename_LA = f"{globalVar.path}/results/log_all_{globalVar.seedInit}.csv"
    header_OPT = [f"opt{i}" for i in range(parameters["NPEAKS_MPB"])]
    filename_OPT = f"{globalVar.path}/results/optima.csv"

    bestRuns = []

    # Headers of the log files
    if(parameters["LOG_ALL"]):
        writeLog(mode=0, filename=filename_LA, header=header_LA)
    writeLog(mode=0, filename=filename, header=header)
    writeLog(mode=0, filename=filename_OPT, header=header_OPT)

    #####################################
    # Main loop of the runs
    #####################################
    print(f"RUN | GEN | NEVALS |                    BEST                   | ERROR")
    for globalVar.run in range(1, parameters["RUNS"]+1):

        if parameters["DEBUG_RUN_2"]:
            print(f"\n==============================================")
            print(f"[START][RUN:{globalVar.run:02}]\n[NEVALS:{globalVar.nevals:06}]")
            print(f"==============================================")

        seed = int(seed + (globalVar.run*2) -2 )
        #seed = int(seed + globalVar.run*2)
        parameters["SEED"] = seed

        globalVar.rng = np.random.default_rng(seed)
        globalVar.nevals = 0
        globalVar.gen = 0
        globalVar.mpb = None
        globalVar.peaks = 0
        globalVar.best = None
        globalVar.eo_sum = 0
        globalVar.flagChangeEnv = 0

        genChangeEnv = 0
        env = 0
        flagEnv = 0
        Eo = 0
        change = 0
        rtPlotNevals = []
        rtPlotError = []
        rtPlotEo = []

        #d = rtPlot.plotUpdate(parameters)
        #d.on_launch(parameters)
        #d()

        # Create the population with POPSIZE individuals
        pops, globalVar.best = createPopulation(algo, parameters)

        #####################################
        # For each pop in pops do the job
        #####################################
        for pop in pops:
            pop = randInit(pop, parameters)

            # Evaluate all the individuals in the pop and update the bests
            pop, globalVar.best = evaluatePop(pop, globalVar.best, parameters)
            for ind in pop.ind:
                ind["ae"] = 0
                # Debug in individual level
                if parameters["DEBUG_IND"]:
                    print(f"[POP {pop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {globalVar.best['id']:04}: {globalVar.best['pos']}\t\tERROR:{globalVar.best['fit']:.04f}]")

        globalVar.gen += 1
        #log = [{"run": globalVar.run, "gen": globalVar.gen, "nevals":globalVar.nevals, "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "bestError": globalVar.best["fit"], "Eo": Eo, "env": env}]
        #writeLog(mode=1, filename=filename, header=header, data=log)
        Eo = globalVar.eo_sum/globalVar.nevals
        log = [{"gen": globalVar.gen, "nevals":globalVar.nevals, "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "ec": globalVar.best["fit"], "eo": Eo, "env": env}]
        filename_RUN = f"{globalVar.path}/results/{parameters['ALGORITHM']}_{globalVar.run:02d}_{parameters['SEED']}.csv"
        writeLog(mode=0, filename=filename_RUN, header=header_RUN)
        writeLog(mode=1, filename=filename_RUN, header=header_RUN, data=log)

        rtPlotNevals.append(globalVar.nevals)
        rtPlotError.append(globalVar.best["fit"])
        rtPlotEo.append(Eo)
        #d.on_running(rtPlotNevals, rtPlotError)
        layout.run(rtPlotNevals, rtPlotError, rtPlotEo)

        #####################################
        # Debug in pop and generation level
        #####################################
        if parameters["DEBUG_POP"]:
            for pop in pops:
                print(f"[POP {pop.id:04}][BEST {pop.best['id']:04}: {pop.best['pos']} ERROR:{globalVar.best['fit']}]")

        if parameters["DEBUG_GEN"]:
            #print(f"[RUN:{globalVar.run:02}][GEN:{globalVar.gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.04f}][Eo: {Eo:.04f}]")
            print(f"[{globalVar.run:02}][{globalVar.gen:04}][{globalVar.nevals:06}][{globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.04f}]")

        ###########################################################################
        # LOOP UNTIL FINISH THE RUN
        ###########################################################################


        while finishRun(parameters) == 0:

            '''
            for pop in pops:
                print(pop.ind[0])
                pop.ind[0]["pos"] = [51.97040, 61.228639]
                evaluate(pop.ind[0], parameters)
                print(pop.ind[0])
                e()
            '''

            ###########################################
            # Apply the Global Diversity Components
            ###########################################

            for i in range(len(algo.comps_global["GDV"])):
                globalVar.randomInit = algo.comps_global["GDV"][i].component(pops, parameters, globalVar.randomInit)

            for id, i in enumerate(globalVar.randomInit, 0):
                if i:
                    pops[id] = randInit(pops[id], parameters)
                    globalVar.randomInit[id] = 0

            ###########################################
            # Apply the Global Exploration Components
            ###########################################

            for i in range(len(algo.comps_global["GER"])):
                pops = algo.comps_global["GER"][i].component(pops, parameters)


            ###########################################
            # Apply the Global Exploitation Components
            ###########################################

            for i in range(len(algo.comps_global["GET"])):
                globalVar.best = algo.comps_global["GET"][i].component(globalVar.best, parameters)


            for pop in pops:

                # Change detection component in the environment
                if(parameters["COMP_REEVALUATION"] == 1):
                    if change == 0:
                        change = changeDetection.detection(pop, parameters)
                    if change:
                        globalVar.best["fit"] = "NaN"
                        pop, globalVar.best = evaluatePop(pop, globalVar.best, parameters)
                        if flagEnv == 0:
                            env += 1
                            genChangeEnv = globalVar.gen
                            flagEnv = 1
                        for ind in pop.ind:
                            ind["ae"] = 0 # Allow new evaluation
                        continue
                elif(parameters["COMP_REEVALUATION"] != 0):
                    errorWarning(0.1, "algoConfig.ini", "COMP_CHANGE_DETECTION", "Component Change Detection should be 0 or 1")

                #####################################
                # Apply the optimizers in the pops
                #####################################

                if i in range(len(algo.opts)):
                    pop = algo.opts[i].optimizer(pop, globalVar.best, parameters)

                ###########################################
                # Apply the Local Exploration Components
                ###########################################

                for i in range(len(algo.comps_local["LER"])):
                    pop = algo.comps_local["LER"][i].component(pop, parameters)

                ###########################################
                # Apply the Local Exploitation Components
                ###########################################


                # Evaluate all the individuals that have no been yet in the pop and update the bests
                pop, globalVar.best = evaluatePop(pop, globalVar.best, parameters)


                for ind in pop.ind:
                    ind["ae"] = 0 # Allow new evaluation
                    # Debug in individual level
                    if parameters["DEBUG_IND"]:
                        print(f"[POP {pop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {globalVar.best['id']:04}: {globalVar.best['pos']}\t\tERROR:{globalVar.best['fit']:.04f}]")


            change = 0
            flagEnv = 0
            if abs(globalVar.gen - genChangeEnv) >= 1:

                change = 0

            globalVar.gen += 1

            #####################################
            # Save the log only with the bests of each generation
            #####################################

            Eo = globalVar.eo_sum/globalVar.nevals
            log = [{"gen": globalVar.gen, "nevals":globalVar.nevals, "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "ec": globalVar.best["fit"], "eo": Eo, "env": env}]
            writeLog(mode=1, filename=filename_RUN, header=header_RUN, data=log)
            rtPlotNevals.append(globalVar.nevals)
            rtPlotError.append(globalVar.best["fit"])
            rtPlotEo.append(Eo)
            #d.on_running(rtPlotNevals, rtPlotError)
            layout.run(rtPlotNevals, rtPlotError, rtPlotEo, globalVar.run)

            #####################################
            # Debug in pop and generation level
            #####################################

            if parameters["DEBUG_POP"]:
                for pop in pops:
                    print(f"[POP {pop.id:04}][BEST {pop.best['id']:04}: {pop.best['pos']} ERROR:{pop.best['fit']}]")

            if parameters["DEBUG_GEN"]:
                print(f"[RUN:{globalVar.run:02}][GEN:{globalVar.gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.04f}][Eo: {Eo:.04f}]")


        #####################################
        # End of the run
        #####################################
        bestRuns.append(globalVar.best)
        eo = offlineError(f"{globalVar.path}/results/{parameters['ALGORITHM']}_{globalVar.run:02d}_{parameters['SEED']}.csv")
        #df = pd.read_csv(f"{globalVar.path}/results/results.csv")
        log = [{"run": globalVar.run, "gen": globalVar.gen, "nevals":globalVar.nevals, "popId": globalVar.best["pop_id"], "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "ec": globalVar.best["fit"], "eo": eo[0], "eo_std": eo[1]}]
        writeLog(mode=1, filename=filename, header=header, data=log)

        if parameters["DEBUG_RUN"]:
            #print(f"[RUN:{globalVar.run:02}][GEN:{globalVar.gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.4f}][Eo:{Eo:.4f}]")
            print(f"{globalVar.run:02}   {globalVar.gen:05}  {globalVar.nevals:06}  {globalVar.best['id']:04}:{globalVar.best['pos']}  {globalVar.best['fit']:.04f}")
        if parameters["DEBUG_RUN_2"]:
            print(f"\n==============================================")
            print(f"[RUN:{globalVar.run:02}]\n[GEN:{globalVar.gen:04}][NEVALS:{globalVar.nevals:06}]")
            print(f"[BEST: IND {globalVar.best['id']:04} from POP {globalVar.best['pop_id']:04}")
            print(f"    -[POS: {globalVar.best['pos']}]")
            print(f"    -[Error: {globalVar.best['fit']}]")
            print(f"==============================================")


        #population.resetId()
        #for pop in pops:
        #    del pop
        globalVar.npops = len(pops)


    # End of the optimization
    print("\n[RESULTS]")
    executionTime = (time.time() - startTime)

    try:
        print("\n[Press continue to calculate the metrics...]")
        layout.set()
        #input()
    except SyntaxError:
        pass


    # Offline error
    df = pd.read_csv(f"{globalVar.path}/results/results.csv")
    eo_mean = df["eo"].mean()

    if parameters["RUNS"] > 1:
        luffy = 0
        bestsPos = []

        eo_std = df["eo_std"].std()

        bests = [d["fit"] for d in bestRuns]
        meanBest = np.mean(bests)
        stdBest = np.std(bests)
        bPos = [d["pos"] for d in bestRuns]
        for i in range(len(bPos[0])):
            for j in range(len(bPos)):
                luffy += bPos[j][i]
            bestsPos.append(luffy/len(bPos))
            luffy = 0

        if parameters["DEBUG_RUN"]:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            print(f"[POS MEAN: {bestsPos} ]")
            print(f"[Ec  MEAN: {meanBest:.4f}({stdBest:.4f})]")
            print(f"[Eo  MEAN: {eo_mean:.4f}({eo_std:.4f})]")


        ecMean_csv = ecMean(f"{globalVar.path}/results", parameters)
        eoMean_csv = eoMean(f"{globalVar.path}/results", parameters)
        ecPlot.ecPlot(ecMean_csv, parameters, multi = 1, pathSave = f"{globalVar.path}/results", name="ecMean")
        eoPlot.eoPlot(eoMean_csv, parameters, multi = 1, pathSave = f"{globalVar.path}/results", name="eoMean")
    else:

        eo_std = df["eo_std"][0]   # If only one run just the number

        if parameters["DEBUG_RUN"]:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            print(f"[POS : {globalVar.best['pos']}]")
            print(f"[Ec  : {globalVar.best['fit']:.4f}]")
            print(f"[Eo  : {eo_mean:.4f}({eo_std:.4f})]")

        ecPlot.ecPlot(f"{globalVar.path}/results/{parameters['ALGORITHM']}_01_{parameters['SEED']}", parameters, pathSave = f"{globalVar.path}/results")
        eoPlot.eoPlot(f"{globalVar.path}/results/{parameters['ALGORITHM']}_01_{parameters['SEED']}", parameters, pathSave = f"{globalVar.path}/results")
        spPlot.spPlot(f"{globalVar.path}/results/log_all_{globalVar.seedInit}", parameters, pathSave = f"{globalVar.path}/results")

    print(f"[RUNTIME: {str(executionTime)} s]")
    print(f"==============================================\n")

    if(parameters["DEBUG_RUN"]):
        files = os.listdir(f"{globalVar.path}/results")
        print(f"\n[FILES GENERATED]\n")
        print(f"-[PATH] {globalVar.path}/results/")
        files = sorted(files)
        for file in files:
            print(f"\t-[FILE] {file}")

    if(parameters["BEBC_ERROR"]):
        if (parameters["DEBUG_RUN"]):
            print("\n[METRICS]")
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {globalVar.path} -d 1")
        else:
            os.system(f"python3 {sys.path[0]}/metrics/bestBeforeChange.py -p {globalVar.path}")




def main():
    seed = minute
    arg_help = "{0} -s <seed> -p <path>".format(sys.argv[0])

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:p:", ["help", "seed=", "path="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-s", "--seed"):
            seed = int(arg)
        elif opt in ("-p", "--path"):
            globalVar.path = arg


    parameters0, algo = algoConfig()
    parameters1 = frameConfig()
    parameters2 = problemConfig()

    parameters = parameters0 | parameters1 | parameters2

    layout = gui.interface(parameters)
    layout.launch(parameters)

    print(f"======================================================")
    print(f"      AbEC -> Ajustable Evolutionary Components        ")
    print(f"        A framework for Optimization Problems         ")
    print(f"======================================================\n")
    try:
        print("[Please check if the configuration files are ok and then press continue...]")
        layout.set()
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

    algo = updateAlgo(algo, parameters)

    if parameters["SEED"] >= 0:
        seed = parameters["SEED"]

    if globalVar.path == ".":
        if not os.path.isdir(f"{parameters['PATH']}"):
            os.mkdir(f"{parameters['PATH']}")
        globalVar.path = f"{parameters['PATH']}/{parameters['ALGORITHM']}"
        globalVar.path = checkDirs(globalVar.path)


    if parameters["DEBUG_RUN"]:
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

    time.sleep(1)
    try:
        print("[Press continue to start...]")
        layout.set()
    except SyntaxError:
        pass

    if parameters["DEBUG_RUN"]:
        print("\n[START]\n")
    abec(algo, parameters, seed, layout)
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
    print("\n[END]\nThx :)")
    layout.set()


if __name__ == "__main__":
    main()


