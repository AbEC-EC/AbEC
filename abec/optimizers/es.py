import aux.globalVar as globalVar
import abec
import copy
from aux.aux import errorWarning

'''
Apply ES on the particle
'''

params = ["RCLOUD"]
P = 1

def cp(parameters):
    if parameters["ES_RCLOUD"] <= 0:
        errorWarning("3.2.1", "algoConfig.ini", "ES_RCLOUD", "The RCLOUD should be greater than 0")
        sys.exit()


def optimizer(pop, best, parameters):
    for i in range(len(pop.ind)):
        indTemp = copy.deepcopy(pop.ind[i])
        rcloud = parameters["ES_RCLOUD"]
        for d in range(parameters["NDIM"]):
            indTemp["pos"][d] = pop.best["pos"][d] + P*(globalVar.rng.uniform(-1, 1)*rcloud)
            if indTemp["pos"][d] > parameters["MAX_POS"]:
                indTemp["pos"][d] = parameters["MAX_POS"]
            elif indTemp["pos"][d] < parameters["MIN_POS"]:
                indTemp["pos"][d] = parameters["MIN_POS"]

        indTemp = abec.evaluate(indTemp, parameters)
        if indTemp["fit"] < pop.ind[i]["fit"]:
            indTemp, globalVar.best = abec.updateBest(indTemp, globalVar.best)
            pop.ind[i] = indTemp
        else:
            pop.ind[i]["ae"] = 1


    return pop

