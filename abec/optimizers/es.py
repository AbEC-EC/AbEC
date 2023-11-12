'''
Title: Code to perform the Evolutionary Strategy (ES) optimizer

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import abec
import copy
from aux.aux import errorWarning

params = ["RCLOUD"]
P = 1

def cp(parameters):
    if parameters["ES_RCLOUD"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "ES_RCLOUD", "The RCLOUD should be greater than 0")

def optimizer(pop, best, runVars, parameters):
    for i in range(len(pop.ind)):
        indTemp = copy.deepcopy(pop.ind[i])
        rcloud = parameters["ES_RCLOUD"]
        for d in range(parameters["NDIM"]):
            indTemp["pos"][d] = pop.best["pos"][d] + P*(runVars.rng.uniform(-1, 1)*rcloud)
            if indTemp["pos"][d] > parameters["MAX_POS"]:
                indTemp["pos"][d] = parameters["MAX_POS"]
            elif indTemp["pos"][d] < parameters["MIN_POS"]:
                indTemp["pos"][d] = parameters["MIN_POS"]

        indTemp, runVars = abec.evaluate(indTemp, runVars, parameters)
        if indTemp["fit"] < pop.ind[i]["fit"]:
            indTemp, runVars.best = abec.updateBest(indTemp, runVars.best)
            pop.ind[i] = indTemp
        else:
            pop.ind[i]["ae"] = 1


    return pop, runVars

