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
import numbers
import json
import numpy as np
# AbEC files
import aux.fitFunction as fitFunction
from aux.aux import *






def myPrint(string, file, parameters):
    if parameters["TERMINAL_OUTPUT"]:
        print(string)
    file.write(f"{string}\n")
    
def myPrint2(string, path):
    file = open(f"{path}/printTmp.txt", "a")
    file.write(f"{string}\n")
    file.close()
    
def finishMetrics(runVars, parameters):
    log = {}
    '''
    for i in range(len(runVars.algo.mts["RUN"])):
        metricName = runVars.algo.mts["RUN"][i].vars[0]
        runVars.metrics[metricName.upper()] = runVars.algo.mts["RUN"][i].metric(runVars.metrics[metricName.upper()], runVars, parameters)
        for var in runVars.algo.mts["RUN"][i].log:   
            log[var] = runVars.metrics[metricName.upper()][var]
    '''
    
    for s in ["RUN", "GEN", "IND"]:
        for i in range(len(runVars.algo.mts[s])):
            metricName = runVars.algo.mts[s][i].vars[0]
            runVars.metrics[metricName.upper()] = runVars.algo.mts[s][i].finishMetric(runVars.metrics[metricName.upper()], f"{runVars.filename_RUN}")
            for var in runVars.algo.mts[s][i].log:   
                log[var] = runVars.metrics[metricName.upper()][var]
            
    return runVars.metrics, log
            
def updateBest(ind, popBest, best):
    '''
    Update the global best individual
    '''
    #print(f"ind type: {type(ind)} {ind['pop_id']} {ind['id']} {ind['fit']} {globalVar.nevals}")
    #print(f"best type: {type(best)} {best['fit']}")
    #if not isinstance(best["fit"], numbers.Number) or (ind["fit"] < best["fit"]): # If first gen, just copy the ind
    if ind["fit"] < best["fit"]: # If first gen, just copy the ind
        best = ind.copy()
        
    '''
    Update the pop best
    '''
    if ind["fit"] < popBest["fit"]: # If first gen, just copy the ind
        popBest = ind.copy()

    '''
    Update the ind best
    '''
    if ind["fit"] < ind["best_fit"]: # If first gen, just copy the ind
        ind["best_fit"] = ind["fit"]
        ind["best_pos"] = ind["pos"]

    return ind, popBest, best


def evaluate(x, popBest, runVars, parameters, be = 0):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''

    # If a dynamic problem, there will be changes in the env
    

    if not parameters["CHANGES"] or runVars.changeEV:
        x["fit"], runVars = fitFunction.fitnessFunction(x['pos'], runVars, parameters)
        runVars.nevals += 1
        if not be:
            x, popBest, runVars.best = updateBest(x, popBest, runVars.best)
    else:
        if not be:
            return x, popBest, runVars
        else:
            return x["fit"], popBest, runVars

    if not be: # If it is a best evaluation does not log
        x["ae"] = 1 # Set the individual as already evaluated
        
        ###########################################
        # Apply the individual level metrics
        ###########################################        
        if (isinstance(runVars.best["fit"], numbers.Number)):
            for i in range(len(runVars.algo.mts["IND"])):
                metricName = runVars.algo.mts["IND"][i].vars[0]
                runVars.metrics[metricName.upper()] = runVars.algo.mts["IND"][i].metric(runVars.metrics[metricName.upper()], runVars, parameters, x)
                
        if parameters["LOG_ALL"]:
            log = [{"run": runVars.id(), "gen": runVars.gen, "nevals": runVars.nevals, \
                "popId": x["pop_id"], "indId": x["id"], "type": x["type"], "indPos": x["pos"], \
                "indVel": x["vel"], "indBestPos": x["best_pos"], "indBestFit": x["best_fit"], \
                "indFit": x["fit"], \
                "popBestId": popBest["id"], "popBestPos": popBest["pos"], "popBestFit": popBest["fit"], \
                "globalBestId": runVars.best["id"], "globalBestPos": runVars.best["pos"], \
                "globalBestFit": runVars.best["fit"]}]
            writeLog(mode=1, filename=runVars.filename_LA, header=runVars.header_LA, data=log)

        return x, popBest, runVars

    else:
        return x["fit"], popBest, runVars



class population():
    '''
        Class of the population
    '''
    # Get a new id for the population
    newid = itertools.count(1).__next__

    def __init__(self, runVars, parameters, popsize, id = 1, fill = 1):
        if(id == 0):    # Temporary population doesnt have an id
            self.id = 0
        else:
            if runVars.npops > 1:
                self.id = population.newid() - ((runVars.id()-1)*runVars.npops)
            else:
                self.id = population.newid()

        self.popsize = popsize

        self.change = 0
        self.ae = 0

        self.ind = []
        if fill == 1:
            for i in range(1, popsize+1):
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
                "best_fit": 100000000, \
                "fit": 1000000000, \
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


def createPopulation(runVars, parameters):
    '''
        This function is to create the populations and individuals
    '''
    pop = []

    for i in range(len(runVars.algo.comps_initialization)):
        pop, runVars = runVars.algo.comps_initialization[i].component(pop, runVars, parameters)

    if not pop:
        pop.append(population(runVars, parameters, parameters["POPSIZE"]))
        runVars.randomInit = [0]

    #best = pop[0].ind[0].copy()
    #best["id"] = "NaN"

    for subpop in pop:
        flag = 0
        for opt in runVars.algo.optimizers:
            for i in range(flag, len(subpop.ind)):
                if subpop.ind[i]["id"] <= int(parameters[f"{opt[0]}_POP_PERC"]*len(subpop.ind)+flag):
                    subpop.ind[i]["type"] = opt[0]
                else:
                    flag = subpop.ind[i]["id"]-1
                    break

    return pop, runVars


def randInit(pop, runVars, parameters):
    '''
        Random initialization of the individuals
    '''
    #print(f"REINIT {subpop.id}")
    for ind_i, ind in enumerate(pop.ind):
        pop.ind[ind_i]["pos"] = [float(runVars.rng.choice(range(int(parameters['MIN_POS']), int(parameters['MAX_POS'])))) for _ in range(parameters["NDIM"])]
        pop.ind[ind_i]["best_pos"] = pop.ind[ind_i]["pos"]
        pop.ind[ind_i]["best_fit"] = 100000000
        if pop.ind[ind_i]["type"] == "PSO":
            pop.ind[ind_i]["vel"] = [float(runVars.rng.choice(range(int(parameters["PSO_MIN_VEL"]), int(parameters["PSO_MAX_VEL"])))) for _ in range(parameters["NDIM"])]
    pop.best = pop.ind[0].copy()
    pop.best["fit"] = 100000000
    return pop, runVars



def evaluatePop(pop, runVars, parameters):
    for ind_i, ind in enumerate(pop.ind):
        if ind["ae"] == 0:
            pop.ind[ind_i], pop.best, runVars = evaluate(ind, pop.best, runVars, parameters)
            '''
            for i, d in enumerate(ind["pos"]):
                ind["pos"][i] = round(d, 4)
            '''
            # ind, best = updateBest(ind, best)

    pop.ind = sorted(pop.ind, key = lambda x:x["fit"])
    # pop.best = pop.ind[0].copy()

    return pop, runVars


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



class runVariables():
    def __init__(self, run, seed, algo, parameters):
        self.__id = run
        self.__seed = seed
        self.done = 0
        self.rng = np.random.default_rng(self.__seed)
        self.algo = algo
        self.gen = 0
        self.nevals = 0
        self.pop = []
        self.best = None
        self.sspace = []
        self.randomInit = [0]
        self.mpb = None
        self.peaks = 0
        self.npops = 0
        self.res = 2
        self.flagChangeEnv = 0
        self.tot_pos = (parameters["MAX_POS"]-parameters["MIN_POS"])**parameters["NDIM"] * (10**self.res)
        self.startTime = 0
        self.bestRuns = []
        self.header_RUN = ["gen", "nevals", "bestId", "bestPos", "env"]  
        self.filename_RUN = ""
        self.header_LA = ["run", "gen", "nevals", "popId", "indId", "type", "indPos", "indVel", "indBestPos", "indBestFit", "indFit", "popBestId", "popBestPos", "popBestFit", "globalBestId", "globalBestPos", "globalBestFit"]
        self.filename_LA = ""
        self.header_OPT = [f"opt{i}" for i in range(1, parameters["NPEAKS_MPB"]+1)]
        self.filename_OPT = ""
        self.genChangeEnv = 0
        self.env = 0
        self.flagEnv = 0
        self.change = 0
        self.changeEV = 1
        self.metrics = {}
        # add the metrics to the variable and header
        for i in range(len(algo.metrics)):
            self.metrics[f"{algo.metrics[i][0]}"] = {}
            for var in algo.metrics[i][1].vars:
                self.metrics[f"{algo.metrics[i][0]}"][f"{var}"] = 0
            if (algo.metrics[i][1].scope[0] == "GEN" or algo.metrics[i][1].scope[0] == "IND"):
                self.header_RUN.append(f"{algo.metrics[i][0].lower()}")
            
    
    def id(self):
        return self.__id
    
    def seed(self):
        return self.__seed


'''
Framework
'''
def abec(run, seed, path, interface):
    # get the date by the path
    tmpdate = open(f"{path}/savethedate.txt", "r")
    date = tmpdate.read()
    tmpdate.close()
    date = date.split("/")
    date = {"year": date[0], "month": date[1], "day": date[2], "hour": date[3], "minute": date[4]}
    
    #####################################
    # initilize the algorithm with the parameters
    #####################################
    parametersFiles = ["algoConfig.ini", "expConfig.ini", "problemConfig.ini"]
    parameters0, algo = algoConfig()
    parameters = parameters0 | expConfig() | problemConfig()
    
    for file in parametersFiles:
        with open(f"{path}/{file}") as f:
            p0 = list(json.loads(f.read()).items())
            for i in range(len(p0)):
                parameters[f"{p0[i][0]}"] = p0[i][1]
    
    algo = updateAlgo(algo, parameters) # udpate the algorithm with the parameters

    runVars = runVariables(run, seed, algo, parameters)    

    #####################################
    # initialize and configure the logs
    #####################################
    checkCreateDir(f"{path}/results/{runVars.id():04}") # Check if the run dir exists, if not, create it
    
    header = ["run", "gen", "nevals", "popId", "bestId", "bestPos", "execTime"]
    keys = list(algo.mts)
    for i in range(len(algo.mts)):
        for j in algo.mts[keys[i]]:
            for var in j.log:
                header.append(var)
    
    filename = f"{path}/results/results.csv"
    if (not os.path.isfile(f"{path}/results/results.csv")):
        # Headers of the log files
        writeLog(mode=0, filename=filename, header=header)
    
    
    if parameters["LOG_ALL"]: # log each individual and its positions
        runVars.filename_LA = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_LOGALL.csv"
        writeLog(mode=0, filename=runVars.filename_LA, header=runVars.header_LA)
    if parameters["BENCHMARK"] != "CUSTOM" or parameters["BENCHMARK"] != "custom": # if benchmark sabe the optima points
        runVars.filename_OPT = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_OPTIMA.csv"
        writeLog(mode=0, filename=runVars.filename_OPT, header=runVars.header_OPT)
        
    runVars.filename_RUN = f"{path}/results/{runVars.id():04}/{parameters['ALGORITHM']}_{date['year']}{date['month']:02}{date['day']:02}_{date['hour']:02}{date['minute']:02}_{runVars.id():04}_{runVars.seed()}_RUN.csv"  
    writeLog(mode=0, filename=runVars.filename_RUN, header=runVars.header_RUN)

    readme = open(f"{path}/results/readme.txt", "a") # open file to write the outputs

    if parameters["DEBUG_RUN_2"]:
        myPrint(f"\n==============================================", readme, parameters)
        myPrint(f"[START][RUN:{runVars.id():02}]\n[NEVALS:{runVars.nevals:06}]", readme, parameters)
        myPrint(f"==============================================", readme, parameters)

    #####################################
    # Start the algorithm
    #####################################
    runVars.startTime = time.time()
    # Create the population with POPSIZE individuals
    runVars.pop, runVars = createPopulation(runVars, parameters)
    runVars.best = copy.deepcopy(runVars.pop[0].ind[0])
    runVars.best["fit"] = 10000000
    runVars.gen += 1  # First generation
    
    #####################################
    # For each subpop in pop do the job
    #####################################
    for subpop_i, subpop in enumerate(runVars.pop):
        
        subpop, runVars = randInit(subpop, runVars, parameters)

        # Evaluate all the individuals in the pop and update the bests
        subpop, runVars = evaluatePop(subpop, runVars, parameters)
        for ind_i, ind in enumerate(subpop.ind):
            ind["ae"] = 0
            # Debug in individual level
            if parameters["DEBUG_IND"]:
                myPrint(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]", readme, parameters)
                
            subpop.ind[ind_i] = copy.deepcopy(subpop.ind[ind_i]) # Apply the changes to the ind
            
        runVars.pop[subpop_i] = copy.deepcopy(runVars.pop[subpop_i]) # Apply the changes to the subpop

    
    if (isinstance(runVars.best["fit"], numbers.Number)):
        for i in range(len(runVars.algo.mts["IND"])):
            metricName = runVars.algo.mts["IND"][i].vars[0]
            runVars.metrics[metricName.upper()] = runVars.algo.mts["IND"][i].metric(runVars.metrics[metricName.upper()], runVars, parameters)

    ###########################################
    # Apply the generation level metrics
    ###########################################
    for i in range(len(runVars.algo.mts["GEN"])):
            metricName = runVars.algo.mts["GEN"][i].vars[0]
            runVars.metrics[metricName.upper()] = runVars.algo.mts["GEN"][i].metric(runVars.metrics[metricName.upper()], runVars, parameters)

    #####################################
    # Save the log only with the bests of each generation
    #####################################
    log = {}
    for s in ["GEN", "IND"]:
        for i in range(len(runVars.algo.mts[s])):
            metricName = runVars.algo.mts[s][i].vars[0]
            log[metricName] = runVars.metrics[metricName.upper()][metricName]
    log |= {"gen": runVars.gen, "nevals":runVars.nevals, "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "env": runVars.env}
    writeLog(mode=1, filename=runVars.filename_RUN, header=runVars.header_RUN, data=[log])


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
        runVars.gen += 1
        ###########################################
        # Apply the Global Diversity Components
        ###########################################
        for i in range(len(runVars.algo.comps_global["GDV"])):
            runVars.randomInit = runVars.algo.comps_global["GDV"][i].component(runVars.pop, runVars.randomInit, runVars, parameters)

        #myPrint(runVars.randomInit)
        for id in range(len(runVars.randomInit)):
            if runVars.randomInit[id]:
                #print(id)
                runVars.pop[id-1], runVars = randInit(runVars.pop[id-1], runVars, parameters)
                runVars.randomInit[id] = 0
                # Evaluate all the individuals in the pop and update the bests
                runVars.pop[id-1], runVars = evaluatePop(runVars.pop[id-1], runVars, parameters)
                runVars.pop[id-1].ae = 1

                

        ###########################################
        # Apply the Global Exploration Components
        ###########################################

        for i in range(len(runVars.algo.comps_global["GER"])):
            runVars.pop = runVars.algo.comps_global["GER"][i].component(runVars.pop, runVars, parameters)


        ###########################################
        # Apply the Global Exploitation Components
        ###########################################

        for i in range(len(runVars.algo.comps_global["GET"])):
            runVars.best, runVars = runVars.algo.comps_global["GET"][i].component(runVars.best, runVars, parameters)


        # Verification if all pop were reeavluated after change
        if parameters["CHANGES"]:
            sumPops = 0
            for subpop in runVars.pop:
                sumPops += subpop.change
                
            if sumPops == len(runVars.pop):
                for subpop in runVars.pop:
                    subpop.change = 0
                runVars.change = 0

        for subpop_i, subpop in enumerate(runVars.pop):
            if runVars.pop[subpop_i].ae == 1:
                continue
            # Change detection component in the environment
            if runVars.change:
                runVars.best["fit"] = 10000000
                runVars.changeEV = 1 # enable the evaluation again
                if subpop.change == 0:
                    subpop, runVars = evaluatePop(subpop, runVars, parameters)
                    subpop.change = 1
                    if runVars.flagEnv == 0:
                        runVars.env += 1
                        runVars.genChangeEnv = runVars.gen
                        runVars.flagEnv = 1
                    for ind_i, ind in enumerate(subpop.ind):
                        ind["ae"] = 0 # Allow new evaluation
                        subpop.ind[ind_i] = copy.deepcopy(subpop.ind[ind_i])
                    continue

            #####################################
            # Apply the optimizers in the pop
            #####################################
            for i in range(len(runVars.algo.opts)):    
                subpop, runVars = runVars.algo.opts[i].optimizer(subpop, runVars.best, runVars, parameters)

            ###########################################
            # Apply the Local Exploration Components
            ###########################################

            for i in range(len(runVars.algo.comps_local["LER"])):
                subpop, runVars = runVars.algo.comps_local["LER"][i].component(runVars.pop, runVars, parameters)

            ###########################################
            # Apply the Local Exploitation Components
            ###########################################


            # Evaluate all the individuals that have no been yet in the subpop and update the bests
            subpop, runVars = evaluatePop(subpop, runVars, parameters)
                
            for ind_i, ind in enumerate(subpop.ind):
                ind["ae"] = 0 # Allow new evaluation
                # Debug in individual level
                if parameters["DEBUG_IND"]:
                    myPrint(f"[POP {subpop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {runVars.best['id']:04}: {runVars.best['pos']}\t\tERROR:{runVars.best['fit']:.04f}]", readme, parameters)
                    
                subpop.ind[ind_i] = copy.deepcopy(subpop.ind[ind_i])
                    
            runVars.pop[subpop_i] = copy.deepcopy(runVars.pop[subpop_i])
            
        for subpop_i, subpop in enumerate(runVars.pop):
            runVars.pop[subpop_i].ae = 0
            for ind_i in range(len(subpop.ind)):
                subpop.ind[ind_i]["ae"] = 0


        runVars.flagEnv = 0
        
        ###########################################
        # Apply the generation level metrics
        ###########################################
        for i in range(len(runVars.algo.mts["GEN"])):
            metricName = runVars.algo.mts["GEN"][i].vars[0]
            runVars.metrics[metricName.upper()] = runVars.algo.mts["GEN"][i].metric(runVars.metrics[metricName.upper()], runVars, parameters)
            
        #####################################
        # Save the log only with the bests of each generation
        #####################################
        log = {}
        for s in ["GEN", "IND"]:
            for i in range(len(runVars.algo.mts[s])):
                metricName = runVars.algo.mts[s][i].vars[0]
                log[metricName] = runVars.metrics[metricName.upper()][metricName]
        log |= {"gen": runVars.gen, "nevals":runVars.nevals, "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "env": runVars.env}
        writeLog(mode=1, filename=runVars.filename_RUN, header=runVars.header_RUN, data=[log])
        

        #####################################
        # Debug in subpop and generation level
        #####################################

        if parameters["DEBUG_POP"]:
            for subpop in runVars.pop:
                myPrint(f"[POP {subpop.id:04}][BEST {subpop.best['id']:04}: {subpop.best['pos']} ERROR:{subpop.best['fit']}]", readme, parameters)

        if parameters["DEBUG_GEN"]:
            myPrint(f"[RUN:{runVars.id():02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.04f}]]", readme, parameters)


    #####################################
    # End of the run
    ####################################
    executionTime = (time.time() - runVars.startTime) 
    
    ###########################################
    # Apply the run level metrics and write in the log
    ###########################################
    log = {}
    runVars.metrics, log = finishMetrics(runVars, parameters)
            
    log |= {"run": runVars.id(), "gen": runVars.gen, "nevals":runVars.nevals, "popId": runVars.best["pop_id"], "bestId": runVars.best["id"], "bestPos": runVars.best["pos"], "execTime": executionTime}
    writeLog(mode=1, filename=filename, header=header, data=[log])

    if parameters["DEBUG_RUN"]:
        #myPrint(f"[RUN:{runVars.run:02}][GEN:{runVars.gen:04}][NEVALS:{runVars.nevals:06}][POP {runVars.best['pop_id']:04}][BEST {runVars.best['id']:04}:{runVars.best['pos']}][ERROR:{runVars.best['fit']:.4f}][Eo:{Eo:.4f}]")
        pos = []
        for p in runVars.best["pos"]:
            pos.append(float(f"{p:.2f}"))
        myPrint(f"{runVars.id():02}   {runVars.gen:05}  {runVars.nevals:06}  {runVars.best['id']:04}:{pos}  {runVars.best['fit']:.04f}", readme, parameters)
        myPrint2(f"{runVars.id():02}   {runVars.gen:05}  {runVars.nevals:06}  {runVars.best['id']:04}:{pos}  {runVars.best['fit']:.04f}", path)
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
    
    # if parameters["PARALLELIZATION"]:
    #     PID = os.getpid()
    #     os.kill(PID, signal.SIGTERM)
            


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