'''
Apply LS on the best
'''

import aux.fitFunction as fitFunction
import aux.globalVar as globalVar
import copy
from aux import *

params = ["ETRY", "RLS"]
scope = ["GET"]

def evaluate(x, parameters):
    '''
    Fitness function. Returns the error between the fitness of the particle
    and the global optimum
    '''
    fitness = fitFunction.fitnessFunction(x['pos'], parameters)
    globalVar.nevals += 1
    return fitness


def cp(parameters):
    if parameters["COMP_LOCAL_SEARCH"] == 1:
        if 0 < parameters["COMP_LOCAL_SEARCH_ETRY"] < parameters["POPSIZE"]:
            if 0 < parameters["COMP_LOCAL_SEARCH_RLS"] < parameters["MAX_POS"]:
                return 1
            else:
                errorWarning("3.4.2", "algoConfig.ini", "COMP_LOCAL_SEARCH_RLS", "The Local Search radio should be 0 between ]0, MAX_POS[")
                sys.exit()
                return 0
        else:
            errorWarning("3.4.1", "algoConfig.ini", "COMP_LOCAL_SEARCH_ETRY", "The number of tries of the Local Search should be 0 between [1, POPSIZE[")
            sys.exit()
            return 0
    elif(parameters["COMP_LOCAL_SEARCH"] != 0):
        errorWarning("3.4", "algoConfig.ini", "COMP_LOCAL_SEARCH", "The Local Search component should be 0 or 1")
        sys.exit()
        return 0


def component(best, parameters):
    rls  = parameters["COMP_LOCAL_SEARCH_RLS"]
    bp = copy.deepcopy(best)
    for _ in range(parameters["COMP_LOCAL_SEARCH_ETRY"]):
        for i in range(parameters["NDIM"]):
            bp["pos"][i] = bp["pos"][i] + globalVar.rng.uniform(-1, 1)*rls
        bp["fit"] = evaluate(bp, parameters)
        if bp["fit"] < best["fit"]:
            best = copy.deepcopy(bp)
    return best

