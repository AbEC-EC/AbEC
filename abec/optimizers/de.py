'''
Title: Code to perform the Differential Evolution (DE) optimizer

Author: Alexandre Mascarenhas
Contact: https://mascarenhasav.github.io

Date: 2023/2
'''
import sys
import copy
import abec
from aux.aux import errorWarning

params = ["F", "CR"]

def cp(parameters):
    if not (0 < parameters["DE_F"] <= 10):
        errorWarning("3.2.1", "algoConfig.ini", "DE_F", "The F parameter should be in the interval ]0, 10]")
        sys.exit()
    if not (0 < parameters["DE_CR"] <= 10):
        errorWarning("3.2.1", "algoConfig.ini", "DF_CR", "The CR parameter should be in the interval ]0, 10]")
        sys.exit()
    return 1


def optimizer(pop, best, runVars, parameters):
    tempPop = copy.deepcopy(pop)
    tempPop.ind = sorted(tempPop.ind, key = lambda x:x["id"]) # Order the individuals by the id number

    dePop = [d for d in tempPop.ind if d["type"]=="DE"] # Select only the DE individuals

    for ind in dePop:
        x = []
        candidates = [c for c in dePop if c["id"] != ind["id"]]
        a, b, c = runVars.rng.choice(candidates, 3, replace=False) # Select the candidate individuals

        for d in range(parameters["NDIM"]):
            x.append(a["pos"][d] + parameters["DE_F"]*(b["pos"][d] - c["pos"][d]))
            if x[d] > parameters["MAX_POS"]:
                x[d] = parameters["MAX_POS"]
            elif x[d] < parameters["MIN_POS"]:
                x[d] = parameters["MIN_POS"]

        for d in range(parameters["NDIM"]):
            if runVars.rng.random() < parameters["DE_CR"]:
                ind["pos"][d] = x[d]

    for ind in dePop:
        ind, runVars = abec.evaluate(ind, runVars, parameters)
        for i in range(len(pop.ind)):
            if ind["id"] == pop.ind[i]["id"]:
                if ind["fit"] < pop.ind[i]["fit"]:
                    pop.ind[i] = ind.copy()
                    ind, runVars.best = abec.updateBest(pop.ind[i], runVars.best)
                else:
                    pop.ind[i]["ae"] = 1    # Assure that this individual will not be evaluated again

    return pop, runVars

