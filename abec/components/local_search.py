'''
Title: Code to perform the Local Search component

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import copy
import abec
import numbers
from aux.aux import errorWarning

params = ["ETRY", "RLS"]
scope = ["GET"]

def cp(parameters):
    if not (0 < parameters["COMP_LOCAL_SEARCH_ETRY"] < parameters["POPSIZE"]):
        errorWarning("4.4.1", "algoConfig.ini", "COMP_LOCAL_SEARCH_ETRY", "The number of tries of the Local Search should be 0 between [1, POPSIZE[")
        
    if not (0 < parameters["COMP_LOCAL_SEARCH_RLS"] < parameters["MAX_POS"]):
        errorWarning("3.4.2", "algoConfig.ini", "COMP_LOCAL_SEARCH_RLS", "The Local Search radio should be 0 between ]0, MAX_POS[")
    return 1


def component(best, runVars, parameters):
    bp = copy.deepcopy(best)
    for _ in range(parameters["COMP_LOCAL_SEARCH_ETRY"]):
        for i in range(parameters["NDIM"]):
            bp["pos"][i] = bp["pos"][i] + runVars.rng.uniform(-1, 1)*parameters["COMP_LOCAL_SEARCH_RLS"]
        bp["fit"], runVars = abec.evaluate(bp, runVars, parameters, be = 1)
        if not isinstance(best["fit"], numbers.Number) or bp["fit"] < best["fit"]:
            best = copy.deepcopy(bp)
    return best, runVars

