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
from deap import benchmarks
# AbEC files
import globalVar
import fitFunction
import optimizers.pso as pso
import optimizers.de as de
import optimizers.ga as ga
import optimizers.es as es
import components.mutation as mutation
import components.changeDetection as changeDetection
import components.exclusion as exclusion
import components.antiConvergence as antiConvergence
import components.localSearch as localSearch
from aux import *


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



def evaluate(x, parameters):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''
    x["fit"] = fitFunction.fitnessFunction(x['pos'], parameters)
    globalVar.nevals += 1
    if parameters["OFFLINE_ERROR"] and isinstance(globalVar.best["fit"], numbers.Number):
        globalVar.eo_sum += globalVar.best["fit"]
    x["ae"] = 1 # Set as already evaluated

    return x



class population():
    '''
        Class of the population
    '''
    newid = itertools.count(1).__next__    # Get a new id for the population

    def __init__(self, parameters, id = 1, fill = 1):
        if(id == 0):    # Temporary population doesnt have an id
            self.id = 0
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



def createPopulation(parameters):
    '''
        This function is to create the populations and individuals
    '''
    pop = []
    if(parameters["COMP_MULTIPOP"] == 1):
        for _ in range (parameters["COMP_MULTIPOP_N"]):
            pop.append(population(parameters))
    elif(parameters["COMP_MULTIPOP"] == 0):
        pop.append(population(parameters))
    else:
        errorWarning(0.1, "algoConfig.ini", "COMP_MULTIPOP", "Component Multipopulation should be 0 or 1")

    best = pop[0].ind[0].copy()
    best["id"] = "NaN"

    return pop, best


def randInit(pop, parameters):
    '''
        Random initialization of the individuals
    '''

    flag = 0
    perc_pop = parameters["GA_POP_PERC"]   \
               +parameters["PSO_POP_PERC"] \
               +parameters["DE_POP_PERC"]  \
               +parameters["ES_POP_PERC"]

    if (abs(perc_pop-1) > 0.001):
        errorWarning(0.0, "algoConfig.ini", "XXX_POP_PERC", "The sum of the percentage of the population to perform the optimizers should be in 1")
        sys.exit()

    if 0 < parameters["GA_POP_PERC"] <= 1:
        if  (parameters["GA_POP_PERC"]*parameters["POPSIZE"]) > 3:
            for ind in pop.ind:
                if ind["id"] <= int(parameters["GA_POP_PERC"]*parameters["POPSIZE"]):
                    ind["type"] = "GA"
                else:
                    flag = ind["id"]-1
                    break
        else:
            errorWarning("0.2.2", "algoConfig.ini", "GA_POP_PERC", "Number of individuals to perform GA should greater than 3")
            sys.exit()
    elif parameters["GA_POP_PERC"] != 0:
        errorWarning("0.2.1", "algoConfig.ini", "GA_POP_PERC", "Percentage of the population to perform GA should be in [0, 1]")
        sys.exit()

    if 0 < parameters["PSO_POP_PERC"] <= 1:
        for i in range(flag, len(pop.ind)):
            if pop.ind[i]["id"] <= int(parameters["PSO_POP_PERC"]*parameters["POPSIZE"]+flag):
                pop.ind[i]["type"] = "PSO"
            else:
                flag = pop.ind[i]["id"]-1
                break
    elif parameters["PSO_POP_PERC"] != 0:
        errorWarning(0.3, "algoConfig.ini", "PSO_POP_PERC", "Percentage of the population to perform PSO should be in [0, 1]")
        sys.exit()

    if 0 < parameters["DE_POP_PERC"] <= 1:
        if  (parameters["DE_POP_PERC"]*parameters["POPSIZE"]) > 3:
            for i in range(flag, len(pop.ind)):
                if pop.ind[i]["id"] <= int(parameters["DE_POP_PERC"]*parameters["POPSIZE"]+flag):
                    pop.ind[i]["type"] = "DE"
                else:
                    flag = pop.ind[i]["id"]-1
                    break
        else:
            errorWarning("0.4.2", "algoConfig.ini", "DE_POP_PERC", "Number of individuals to perform DE should greater than 3")
            sys.exit()
    elif parameters["DE_POP_PERC"] != 0:
        errorWarning("0.4.1", "algoConfig.ini", "DE_POP_PERC", "Percentage of the population to perform DE should be in [0, 1]")
        sys.exit()

    if 0 < parameters["ES_POP_PERC"] <= 1:
        for i in range(flag, len(pop.ind)):
            if pop.ind[i]["id"] <= int(parameters["ES_POP_PERC"]*parameters["POPSIZE"]+flag):
                pop.ind[i]["type"] = "ES"
            else:
                break
    elif parameters["ES_POP_PERC"] != 0:
        errorWarning(0.5, "algoConfig.ini", "ES_POP_PERC", "Percentage of the population to perform ES should be in [0, 1]")
        sys.exit()


    #random.seed(parameters["SEED"])
    for ind in pop.ind:
        ind["pos"] = [float(globalVar.rng.choice(range(parameters['MIN_POS'], parameters['MAX_POS']))) for _ in range(parameters["NDIM"])]
        if ind["type"] == "PSO":
            ind["vel"] = [float(globalVar.rng.choice(range(parameters["PSO_MIN_VEL"], parameters["PSO_MAX_VEL"]))) for _ in range(parameters["NDIM"])]
    return pop


def errorWarning(nError="0.0", file="NONE", parameter="NONE", text="NONE"):
    '''
        Print error function
    '''
    print(f"[ERROR][{nError}]")
    print(f"--[File: '{file}']")
    print(f"--[parameter: '{parameter}']")
    print(f"----[{text}]")
    sys.exit()



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
def abec(parameters, seed):
    startTime = time.time()
    filename = f"{globalVar.path}/{parameters['FILENAME']}"

    bestRuns = []

    # Headers of the log files
    if(parameters["LOG_ALL"]):
        header = ["run", "gen", "nevals", "popId", "indId", "indPos", "indError", "popBestId", "popBestPos", "popBestError", "bestId", "bestPos", "bestError", "Eo", "env"]
    else:
        header = ["run", "gen", "nevals", "bestId", "bestPos", "bestError", "Eo", "env"]
    writeLog(mode=0, filename=filename, header=header)
    headerOPT = [f"opt{i}" for i in range(parameters["NPEAKS_MPB"])]
    writeLog(mode=0, filename=f"{globalVar.path}/optima.csv", header=headerOPT)


    #####################################
    # Main loop of the runs
    #####################################

    for run in range(1, parameters["RUNS"]+1):
        if parameters["DEBUG_RUN_2"]:
            print(f"\n==============================================")
            print(f"[START][RUN:{run:02}]\n[NEVALS:{globalVar.nevals:06}]")
            print(f"==============================================")

        seed = seed*run**5
        parameters["SEED"] = seed

        globalVar.rng = np.random.default_rng(seed)
        globalVar.nevals = 0
        globalVar.mpb = None
        globalVar.best = None
        globalVar.eo_sum = 0
        globalVar.flagChangeEnv = 0

        gen = 1
        genChangeEnv = 0
        env = 0
        flagEnv = 0
        Eo = 0
        change = 0
        randomInit = [0 for _ in range(1, parameters["COMP_MULTIPOP_N"]+2)]

        # Create the population with POPSIZE individuals
        pops, globalVar.best = createPopulation(parameters)

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
                if parameters["LOG_ALL"]:
                    log = [{"run": run, "gen": gen, "nevals":globalVar.nevals, "popId": pop.id, "indId": ind["id"], "indPos": ind["pos"], "indError": ind["fit"], "popBestId": pop.best["id"], "popBestPos": pop.best["pos"], "popBestError": pop.best["fit"], "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "bestError": globalVar.best["fit"], "Eo": Eo, "env": env}]
                    writeLog(mode=1, filename=filename, header=header, data=log)
                if parameters["DEBUG_IND"]:
                    print(f"[POP {pop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {globalVar.best['id']:04}: {globalVar.best['pos']}\t\tERROR:{globalVar.best['fit']:.04f}]")


        if not parameters["LOG_ALL"]:
            log = [{"run": run, "gen": gen, "nevals":globalVar.nevals, "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "bestError": globalVar.best["fit"], "Eo": Eo, "env": env}]
            writeLog(mode=1, filename=filename, header=header, data=log)


        #####################################
        # Debug in pop and generation level
        #####################################
        if parameters["DEBUG_POP"]:
            for pop in pops:
                print(f"[POP {pop.id:04}][BEST {pop.best['id']:04}: {pop.best['pos']} ERROR:{globalVar.best['fit']}]")

        if parameters["DEBUG_GEN"]:
            print(f"[RUN:{run:02}][GEN:{gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.04f}][Eo: {Eo:.04f}]")


        ###########################################################################
        # LOOP UNTIL FINISH THE RUN
        ###########################################################################


        while finishRun(parameters) == 0:


            #####################################
            # Apply the components in Global level
            #####################################

            if antiConvergence.cp_antiConvergence(parameters):
                randomInit = antiConvergence.antiConvergence(pops, parameters, randomInit)

            if exclusion.cp_exclusion(parameters):
                randomInit = exclusion.exclusion(pops, parameters, randomInit)

            for id, i in enumerate(randomInit, 0):
                if i:
                    pops[id] = randInit(pops[id], parameters)
                    randomInit[id] = 0

            if localSearch.cp_localSearch(parameters):
                globalVar.best = localSearch.localSearch(globalVar.best, parameters)


            '''
                The next componentes should be here
            '''


            for pop in pops:

                # Change detection component in the environment
                if(parameters["COMP_CHANGE_DETECT"] == 1):
                    if change == 0:
                        change = changeDetection.detection(pop, parameters)
                    if change:
                        globalVar.best["fit"] = "NaN"
                        pop, globalVar.best = evaluatePop(pop, globalVar.best, parameters)
                        if flagEnv == 0:
                            env += 1
                            genChangeEnv = gen
                            flagEnv = 1
                        for ind in pop.ind:
                            ind["ae"] = 0 # Allow new evaluation
                        continue
                elif(parameters["COMP_CHANGE_DETECT"] != 0):
                    errorWarning(0.1, "algoConfig.ini", "COMP_CHANGE_DETECT", "Component Change Detection should be 0 or 1")

                #####################################
                # Apply the optimizers in the pops
                #####################################

                if parameters["GA_POP_PERC"]:
                    pop = ga.ga(pop, parameters)


                if parameters["DE_POP_PERC"]:
                    pop = de.de(pop, parameters)

                for i in range(len(pop.ind)):
                    if pop.ind[i]["type"] == "PSO":
                        pop.ind[i] = pso.pso(pop.ind[i], pop.best, parameters)
                    elif pop.ind[i]["type"] == "ES":
                        pop.ind[i] = es.es(pop.ind[i], pop.best, parameters)


                #####################################
                # Apply the components in Population level
                #####################################

                if mutation.cp_mutation(parameters, comp=1):
                    pop = mutation.mutation(pop, parameters, comp=1)


                '''
                    The next componentes should be here
                '''


                # Evaluate all the individuals that have no been yet in the pop and update the bests
                pop, globalVar.best = evaluatePop(pop, globalVar.best, parameters)


                for ind in pop.ind:
                    ind["ae"] = 0 # Allow new evaluation
                    # Debug in individual level
                    if parameters["LOG_ALL"]:
                        log = [{"run": run, "gen": gen, "nevals":globalVar.nevals, "popId": pop.id, "indId": ind["id"], "indPos": ind["pos"], "indError": ind["fit"], "popBestId": pop.best["id"], "popBestPos": pop.best["pos"], "popBestError": pop.best["fit"], "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "bestError": globalVar.best["fit"], "Eo": Eo, "env": env}]
                        writeLog(mode=1, filename=filename, header=header, data=log)
                    if parameters["DEBUG_IND"]:
                        print(f"[POP {pop.id:04}][IND {ind['id']:04}: {ind['pos']}\t\tERROR:{ind['fit']:.04f}]\t[BEST {globalVar.best['id']:04}: {globalVar.best['pos']}\t\tERROR:{globalVar.best['fit']:.04f}]")




            change = 0
            flagEnv = 0
            if abs(gen - genChangeEnv) >= 1:

                change = 0

            gen += 1

            #####################################
            # Save the log only with the bests of each generation
            #####################################

            if not parameters["LOG_ALL"]:
                Eo = globalVar.eo_sum/globalVar.nevals
                log = [{"run": run, "gen": gen, "nevals":globalVar.nevals, "bestId": globalVar.best["id"], "bestPos": globalVar.best["pos"], "bestError": globalVar.best["fit"], "Eo": Eo, "env": env}]
                writeLog(mode=1, filename=filename, header=header, data=log)


            #####################################
            # Debug in pop and generation level
            #####################################

            if parameters["DEBUG_POP"]:
                for pop in pops:
                    print(f"[POP {pop.id:04}][BEST {pop.best['id']:04}: {pop.best['pos']} ERROR:{pop.best['fit']}]")

            if parameters["DEBUG_GEN"]:
                print(f"[RUN:{run:02}][GEN:{gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.04f}][Eo: {Eo:.04f}]")


        #####################################
        # End of the run
        #####################################

        bestRuns.append(globalVar.best)

        if parameters["DEBUG_RUN"]:
            print(f"[RUN:{run:02}][GEN:{gen:04}][NEVALS:{globalVar.nevals:06}][POP {globalVar.best['pop_id']:04}][BEST {globalVar.best['id']:04}:{globalVar.best['pos']}][ERROR:{globalVar.best['fit']:.4f}][Eo:{Eo:.4f}]")
        if parameters["DEBUG_RUN_2"]:
            print(f"\n==============================================")
            print(f"[RUN:{run:02}]\n[GEN:{gen:04}][NEVALS:{globalVar.nevals:06}]")
            print(f"[BEST: IND {globalVar.best['id']:04} from POP {globalVar.best['pop_id']:04}")
            print(f"    -[POS: {globalVar.best['pos']}]")
            print(f"    -[Error: {globalVar.best['fit']}]")
            print(f"==============================================")


        population.resetId()


    if parameters["RUNS"] > 1:
        bests = [d["fit"] for d in bestRuns]
        meanBest = np.mean(bests)
        stdBest = np.std(bests)
        if parameters["DEBUG_RUN"]:
            print(f"\n==============================================")
            print(f"[RUNS:{parameters['RUNS']}]")
            print(f"[BEST MEAN: {meanBest:.2f}({stdBest:.2f})]")
            print(f"==============================================\n")

    executionTime = (time.time() - startTime)

    #print(f"File generated: {path}/data.csv")
    if(parameters["DEBUG_RUN"]):
        print(f"\nFile generated: {globalVar.path}/data.csv")
        print(f'Time Exec: {str(executionTime)} s\n')


    # Evaluate the offline error
    if(parameters["OFFLINE_ERROR"]):
        if (parameters["DEBUG_RUN"]):
            print("\n[METRIC]")
            os.system(f"python3 {sys.path[0]}/metrics/offlineError.py -p {globalVar.path} -d 1")
        else:
            os.system(f"python3 {sys.path[0]}/metrics/offlineError.py -p {globalVar.path}")

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

    parameters0 = algoConfig()
    parameters1 = frameConfig()
    parameters2 = problemConfig()
   # Read the parameters from the config file
    if os.path.isfile(f"{globalVar.path}/algoConfig.ini"):
        with open(f"{globalVar.path}/algoConfig.ini") as f:
            p0 = list(json.loads(f.read()).items())
            for i in range(len(p0)):
                #print(p0[i][0])
                parameters0[f"{p0[i][0]}"] = p0[i][1]

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

    if parameters["SEED"] >= 0:
        seed = parameters["SEED"]

    if globalVar.path == ".":
        if not os.path.isdir(f"{parameters['PATH']}"):
            os.mkdir(f"{parameters['PATH']}")
        globalVar.path = f"{parameters['PATH']}/{parameters['ALGORITHM']}"
        globalVar.path = checkDirs(globalVar.path)


    if parameters["DEBUG_RUN"]:
        print(f"======================================================")
        print(f"      AbEC -> Ajustable Evolutionary Components        ")
        print(f"        A framework for Optimization Problems         ")
        print(f"======================================================\n")
        print(f"[ALGORITHM SETUP]")
        print(f"- Name: {parameters['ALGORITHM']}")
        print(f"- Individuals p/ population:\t{parameters['POPSIZE']}")
        print(f"- Optimizers (percentage of each population):")
        if(parameters["GA_POP_PERC"] > 0):
            print(f"-- [GA]:\t{parameters['GA_POP_PERC']*100}%")
            print(f"---- Elitism:\t{parameters['GA_ELI_PERC']*100:.0f}%")
            print(f"---- Crossover:\t{parameters['GA_CROSS_PERC']*100}%")
            print(f"---- Mutation:\t{parameters['GA_MUT_PERC']}")
        if(parameters["PSO_POP_PERC"] > 0):
            print(f"-- [PSO]:\t{parameters['PSO_POP_PERC']*100}%")
            print(f"---- Phi1:\t{parameters['PSO_PHI1']}")
            print(f"---- Phi2:\t{parameters['PSO_PHI2']}")
            print(f"---- W:\t\t{parameters['PSO_W']}")
        if(parameters["DE_POP_PERC"] > 0):
            print(f"-- [DE]:\t{parameters['DE_POP_PERC']*100}%")
            print(f"---- F:\t\t{parameters['DE_F']}")
            print(f"---- CR:\t{parameters['DE_CR']}")
        if(parameters["ES_POP_PERC"] > 0):
            print(f"-- [ES]:\t{parameters['ES_POP_PERC']*100}%")
            print(f"---- Rcloud:\t{parameters['ES_RCLOUD']}")

        print()
        print(f"- Components:")
        if(parameters["COMP_EXCLUSION"]):
            print(f"-- [Exlcusion]:")
            print(f"---- Rexcl:\t{parameters['COMP_EXCLUSION_REXCL']}")
        if(parameters["COMP_ANTI_CONVERGENCE"]):
            print(f"-- [ANTI-CONVERGENCE]:")
            print(f"---- Rconv:\t{parameters['COMP_ANTI_CONVERGENCE_RCONV']}")
        if(parameters["COMP_LOCAL_SEARCH"]):
            print(f"-- [LOCAL_SEARCH]:")
            print(f"---- Etry:\t{parameters['COMP_LOCAL_SEARCH_ETRY']}")
            print(f"---- Rls:\t{parameters['COMP_LOCAL_SEARCH_RLS']}")

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
        input("\n\n[Press enter to start...]")
    except SyntaxError:
        pass

    print("\n[START]\n")
    abec(parameters, seed)
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
    print("\n[END]\nThx :)\n")


if __name__ == "__main__":
    main()


