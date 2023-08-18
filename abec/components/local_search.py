'''
Apply LS on the best
'''

import sys
import copy
import abec
import numbers
import aux.globalVar as globalVar
from aux.aux import errorWarning

params = ["ETRY", "RLS"]
scope = ["GET"]

def cp(parameters):
    if not (0 < parameters["COMP_LOCAL_SEARCH_ETRY"] < parameters["POPSIZE"]):
        errorWarning("4.4.1", "algoConfig.ini", "COMP_LOCAL_SEARCH_ETRY", "The number of tries of the Local Search should be 0 between [1, POPSIZE[")
        sys.exit()
    if not (0 < parameters["COMP_LOCAL_SEARCH_RLS"] < parameters["MAX_POS"]):
        errorWarning("3.4.2", "algoConfig.ini", "COMP_LOCAL_SEARCH_RLS", "The Local Search radio should be 0 between ]0, MAX_POS[")
        sys.exit()

    return 1


def component(best, parameters):
    bp = copy.deepcopy(best)
    for _ in range(parameters["COMP_LOCAL_SEARCH_ETRY"]):
        for i in range(parameters["NDIM"]):
            bp["pos"][i] = bp["pos"][i] + globalVar.rng.uniform(-1, 1)*parameters["COMP_LOCAL_SEARCH_RLS"]
        bp["fit"] = abec.evaluate(bp, parameters, be = 1)
        if not isinstance(best["fit"], numbers.Number) or bp["fit"] < best["fit"]:
            best = copy.deepcopy(bp)
    return best

