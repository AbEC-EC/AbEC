#!/usr/bin/env python3

'''
Base code for AbEC framework

Alexandre Mascarenhas

2023/1
'''
import itertools
import sys
import getopt
import time
import copy
import signal
import platform
import numbers
import json
import numpy as np
import matplotlib.colors as mcolors
# AbEC files
import plot.currentError as ecPlot
import plot.offlineError as eoPlot
import plot.searchSpace as spPlot
import aux.fitFunction as fitFunction
import plot.rtPlot as rtPlot
import gui.gui as gui
from aux.aux import *
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


def myPrint(string, file, parameters):
    if parameters["TERMINAL_OUTPUT"]:
        print(string)
    file.write(f"{string}\n")



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

    def __init__(self, runVars, parameters, id = 1, fill = 1):
        if(id == 0):    # Temporary population doesnt have an id
            self.id = 0
        else:
            if runVars.npops > 1:
                self.id = population.newid() - ((runVars.id()-1)*runVars.npops)
            else:
                self.id = population.newid()

        self.popsize = parameters["POPSIZE"]

        self.change = 0

        self.ind = []
        if fill == 1:
            for i in range(1, parameters["POPSIZE"]+1):
                self.addInd(runVars, parameters, i)

        self.best = self.createInd(runVars, parameters, 0)

    def createInd(self, runVars, parameters, ind_id=-1):
        attr = {"pop_id": self.id, \
                "run": runVars.id(), \
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

    def addInd(self, runVars, parameters, ind_id=-1):
        flag = 0
        ids = [d["id"] for d in self.ind]
        while flag == 0:
            if ind_id in ids:  # If id is already in the population go to next
                ind_id += 1
            else:
                flag = 1
        self.ind.append(self.createInd(runVars, parameters, ind_id))

    def resetId():
        population.newid = itertools.count(1).__next__    # Get a new id for the population


def createPopulation(algo, runVars, parameters):
    '''
        This function is to create the populations and individuals
    '''
    pop = []

    for i in range(len(algo.comps_initialization)):
        pop, runVars = algo.comps_initialization[i].component(pop, runVars, parameters)

    if not pop:
        pop.append(population(runVars, parameters))
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
    def __init__(self, run, seed, parameters):
        self.__id = run
        self.__seed = seed
        self.done = 0
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
        self.npops = 0
        self.Fr = 0
        self.res = 2
        self.flagChangeEnv = 0
        self.tot_pos = (parameters["MAX_POS"]-parameters["MIN_POS"])**parameters["NDIM"] * (10**self.res)
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
        self.changeEV = 0
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
def abec(run, seed, path, layout = 0):
    # get the date by the path
    date = path.split("/")
    date = {"year": date[-2][0:4], "month": date[-2][5:7], "day": date[-2][8:], "hour": date[-1][0:2], "minute": date[-1][3:]}
    
    #####################################
    # initilize the algorithm with the parameters
    #####################################
    parametersFiles = ["algoConfig.ini", "frameConfig.ini", "problemConfig.ini"]
    parameters0, algo = algoConfig()
    parameters = parameters0 | frameConfig() | problemConfig()
    
    for file in parametersFiles:
        with open(f"{path}/{file}") as f:
            p0 = list(json.loads(f.read()).items())
            for i in range(len(p0)):
                parameters[f"{p0[i][0]}"] = p0[i][1]
    
    algo = updateAlgo(algo, parameters) # udpate the algorithm with the parameters

    runVars = runVariables(run, seed, parameters)
    
    
    #####################################
    # initialize and configure the logs
    #####################################
    checkCreateDir(f"{path}/results/{runVars.id():04}") # Check if the run dir exists, if not, create it
    
    header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "ec", "eo", "eo_std", "fr", "fr_std", "execTime"]
    filename = f"{path}/results/results.csv"
    
    
    if parameters["LOG_ALL"]: # log each individual and its positions
        runVars.filename_LA = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_LOGALL.csv"
        writeLog(mode=0, filename=runVars.filename_LA, header=runVars.header_LA)
    if parameters["BENCHMARK"] != "CUSTOM" or parameters["BENCHMARK"] != "custom": # if benchmark sabe the optima points
        runVars.filename_OPT = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_OPTIMA.csv"
        writeLog(mode=0, filename=runVars.filename_OPT, header=runVars.header_OPT)
        
    runVars.filename_RUN = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_RUN.csv"  
    writeLog(mode=0, filename=runVars.filename_RUN, header=runVars.header_RUN)

    readme = open(f"{path}/readme.txt", "a") # open file to write the outputs

    if parameters["DEBUG_RUN_2"]:
        myPrint(f"\n==============================================", readme, parameters)
        myPrint(f"[START][RUN:{runVars.id():02}]\n[NEVALS:{runVars.nevals:06}]", readme, parameters)
        myPrint(f"==============================================", readme, parameters)

    #####################################
    # Start the algorithm
    #####################################
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
                myPrint(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]", readme, parameters)
                
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
        #myPrint(f"[RUN:{runVars.run:02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}][Eo: {Eo:.04f}]")
        myPrint(f"[RUN {runVars.id():02}][GEN {runVars.gen:04}][NE {runVars.nevals:06}][POP {runVars.best['pop_id']:02}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}]", readme, parameters)
        
    if parameters["DEBUG_POP"]:
        for subpop in runVars.pop:
            myPrint(f"[POP {subpop.id:04}][BEST {subpop.best['id']:04}: {subpop.best['pos']} ERROR:{subpop.best['fit']}]", readme, parameters)

    ###########################################################################
    # LOOP UNTIL FINISH THE RUN
    ###########################################################################
    while finishRun(runVars, parameters) == 0:
        ###########################################
        # Apply the Global Diversity Components
        ###########################################
        for i in range(len(algo.comps_global["GDV"])):
            runVars.randomInit, runVars = algo.comps_global["GDV"][i].component(runVars.pop, runVars, parameters, runVars.randomInit)

        #myPrint(runVars.randomInit)
        for id, i in enumerate(runVars.randomInit, 0):
            if i:
                runVars.pop[id], runVars = randInit(runVars.pop[id], runVars, parameters)
                runVars.randomInit[id] = 0

        ###########################################
        # Apply the Global Exploration Components
        ###########################################

        for i in range(len(algo.comps_global["GER"])):
            runVars.pop, runVars = algo.comps_global["GER"][i].component(runVars.pop, runVars, parameters)


        ###########################################
        # Apply the Global Exploitation Components
        ###########################################

        for i in range(len(algo.comps_global["GET"])):
            runVars.best, runVars = algo.comps_global["GET"][i].component(runVars.best, runVars, parameters)


        # Verification if all pop were reeavluated after change
        if parameters["CHANGES"]:
            sumPops = 0
            for subpop in runVars.pop:
                sumPops += subpop.change

            #myPrint(f"sumpops: {sumPops} {runVars.nevals} {len(pop)}")
            if sumPops == len(runVars.pop):
                for subpop in runVars.pop:
                    subpop.change = 0
                runVars.change = 0
                #myPrint("CABOU")

        for subpop_i, subpop in enumerate(runVars.pop):

            # Change detection component in the environment
            if runVars.change:
                #myPrint(f"Change: {runVars.nevals}")
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
                    myPrint(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]", readme, parameters)
                    
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
                myPrint(f"[POP {subpop.id:04}][BEST {subpop.best['id']:04}: {subpop.best['pos']} ERROR:{subpop.best['fit']}]", readme, parameters)

        if parameters["DEBUG_GEN"]:
            myPrint(f"[RUN:{runVars.id():02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}][Eo: {runVars.Eo:.04f}]", readme, parameters)


    #####################################
    # End of the run
    ####################################
    executionTime = (time.time() - runVars.startTime) 
    
    # write the results in the log
    runVars.eo = offlineError(f"{runVars.filename_RUN}")
    log = [{"run": runVars.id(), "gen": runVars.gen, "nevals":runVars.nevals, "popId": runVars.best["pop_id"], "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "ec": runVars.best["fit"], "eo": runVars.eo[0], "eo_std": runVars.eo[1], "execTime": executionTime}]
    writeLog(mode=1, filename=filename, header=header, data=log)

    if parameters["DEBUG_RUN"]:
        #myPrint(f"[RUN:{runVars.run:02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.4f}][Eo:{Eo:.4f}]")
        pos = []
        for p in runVars.best["pos"]:
            pos.append(float(f"{p:.2f}"))
        myPrint(f"{runVars.id():02}   {runVars.gen:05}  {runVars.nevals:06}  {runVars.best['id']:04}:{pos}  {runVars.best['fit']:.04f}", readme, parameters)
    if parameters["DEBUG_RUN_2"]:
        myPrint(f"\n==============================================", readme, parameters)
        myPrint(f"[RUN:{runVars.id():02}]\n[GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}]", readme, parameters)
        myPrint(f"[BEST: IND {runVars.best['id']:04} from POP {runVars.best['pop_id']:04}", readme, parameters)
        myPrint(f"    -[POS: {runVars.best['pos']}]", readme, parameters)
        myPrint(f"    -[Error: {runVars.best['fit']}]", readme, parameters)
        myPrint(f"[RUNTIME: {str(executionTime)} s]", readme, parameters)
        myPrint(f"==============================================", readme, parameters)

    runVars.npops = len(runVars.pop)
    
    readme.close()  # Close file 
    
    if parameters["PARALLELIZATION"]:
        PID = os.getpid()
        os.kill(PID, signal.SIGTERM)
            


if __name__ == '__main__':
    run = 1
    seed = 42
    interface = 0
    
    arg_help = "{0} -r <run> -s <seed> -p <path> -i <interface>".format(sys.argv[0])
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:s:p:i:", ["help", "run=", "seed=", "path=", "interface="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-r", "--run"):
            run = int(arg)
        elif opt in ("-s", "--seed"):
            if seed >= 0:
                seed = int(arg)
        elif opt in ("-p", "--path"):
                path = arg
        elif opt in ("-i", "--interface"):
            interface = int(arg)

    abec(run, seed, path, interface)