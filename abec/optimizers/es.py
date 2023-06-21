import globalVar
import abec
import copy

'''
Apply ES on the particle
'''

params = ["RCLOUD"]

def es(ind, popBest, parameters, P=1):
    indTemp = copy.deepcopy(ind)
    rcloud = parameters["ES_RCLOUD"]
    for d in range(parameters["NDIM"]):
        indTemp["pos"][d] = popBest["pos"][d] + P*(globalVar.rng.uniform(-1, 1)*rcloud)
        if indTemp["pos"][d] > parameters["MAX_POS"]:
            indTemp["pos"][d] = parameters["MAX_POS"]
        elif indTemp["pos"][d] < parameters["MIN_POS"]:
            indTemp["pos"][d] = parameters["MIN_POS"]

    indTemp = abec.evaluate(indTemp, parameters)
    if indTemp["fit"] < ind["fit"]:
        indTemp, globalVar.best = abec.updateBest(indTemp, globalVar.best)
        return indTemp
    else:
        ind["ae"] = 1
        return ind

